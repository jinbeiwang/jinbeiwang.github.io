"""The tool-call protocol: a fenced JSON block, and a parser that survives
truncation.

Why this format and not XML tags or a bespoke syntax: the model already writes
JSON well, and a strict JSON object gives exact argument *types* for free
(``3`` stays a number, ``true`` stays a boolean). The cost is verbosity, and
the parser has to be careful — which is the interesting part.

Three rules the parser must satisfy, all tested:

  1. **At most one call per reply.** Two fenced blocks is an error, not a
     "run both".
  2. **Truncation is not corruption.** If the reply is cut at any character,
     the result is either no call or exactly the original call. A cut *inside*
     the arguments sets ``error`` — the harness must not execute a half-parsed
     call.
  3. **A string argument may contain the protocol.** If an argument value
     itself holds a complete fenced call, the parser must not find it. That is
     what the brace-depth scanner buys over a regular expression: it tracks
     string state and escapes, so text inside a JSON string is never counted
     as structure.

The scan is deliberately done by hand rather than with ``json.JSONDecoder``'s
``raw_decode``: ``raw_decode`` needs a *complete* document and cannot tell you
"this was cut inside the arguments" from "there was nothing here".
"""

from __future__ import annotations

import json
from typing import Optional

from .types import ParsedResponse, ToolCall

OPEN = "```tool"
CLOSE = "```"


def render_tools(schemas: list[dict]) -> str:
    """The text that tells the model which tools exist and how to call one.

    This is the whole "tool calling feature": a string in the system prompt.
    Everything the model knows about the tools it knows from here, so the
    descriptions and the schema are the API documentation.
    """
    lines = [
        "You can call one tool at a time. To call a tool, reply with a fenced",
        "block tagged `tool` containing a single JSON object with exactly two",
        "keys: `name` (a string) and `arguments` (an object matching that",
        "tool's schema). Write nothing after the closing fence.",
        "",
        "Example:",
        OPEN,
        '{"name": "search_emails", "arguments": {"query": "larchfield audit", "k": 5}}',
        CLOSE,
        "",
        "Tools:",
    ]
    for s in schemas:
        lines.append("")
        lines.append(f"- {s['name']}: {s['description']}")
        lines.append(f"  arguments: {json.dumps(s['parameters'], ensure_ascii=False, sort_keys=True)}")
    return "\n".join(lines)


def format_tool_call(text: str, call: ToolCall) -> str:
    """Write a reply containing prose plus one call, in this protocol."""
    body = json.dumps({"name": call.name, "arguments": call.args}, ensure_ascii=False, indent=2)
    head = text.strip()
    block = f"{OPEN}\n{body}\n{CLOSE}"
    return f"{head}\n\n{block}" if head else block


def _balanced_object(text: str, start: int) -> Optional[int]:
    """Index just past the first balanced {...} at or after ``start``.

    Returns None when the object never closes — which is exactly what a
    truncated reply looks like. Braces inside strings do not count.
    """
    i = start
    n = len(text)
    while i < n and text[i] != "{":
        # prose between the fence and the object is tolerated, but a closing
        # fence before any object means "no call here"
        if text.startswith(CLOSE, i):
            return None
        i += 1
    if i >= n:
        return None

    depth = 0
    in_string = False
    escaped = False
    while i < n:
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
        i += 1
    return None


def parse_response(text: str) -> ParsedResponse:
    """Split one model reply into its prose and at most one tool call."""
    if not text:
        return ParsedResponse(text="", error=None)

    idx = text.find(OPEN)
    if idx < 0:
        return ParsedResponse(text=text.strip(), error=None)

    body_start = idx + len(OPEN)
    obj_end = _balanced_object(text, body_start)
    if obj_end is None:
        return ParsedResponse(
            text=text[:idx].strip(),
            error=(
                "Your tool call was cut off before its JSON object closed. "
                "Reply again with one complete, smaller call."
            ),
        )

    raw = text[body_start:obj_end]
    raw = raw[raw.find("{"):]

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return ParsedResponse(
            text=text[:idx].strip(),
            error=f"Your tool call was not valid JSON ({exc.msg}). Reply again with one valid call.",
        )

    if not isinstance(payload, dict) or not isinstance(payload.get("name"), str):
        return ParsedResponse(
            text=text[:idx].strip(),
            error='A tool call must be a JSON object with a string "name".',
        )

    args = payload.get("arguments", {})
    if args is None:
        args = {}
    if not isinstance(args, dict):
        return ParsedResponse(
            text=text[:idx].strip(),
            error='"arguments" must be a JSON object.',
        )

    # swallow a trailing closing fence, so it does not leak into the prose
    tail_start = obj_end
    rest = text[obj_end:]
    stripped = rest.lstrip()
    if stripped.startswith(CLOSE):
        tail_start = obj_end + (len(rest) - len(stripped)) + len(CLOSE)

    # a second call anywhere after this one is an error, not a batch
    if OPEN in text[tail_start:]:
        return ParsedResponse(
            text=text[:idx].strip(),
            error="You wrote more than one tool call. Send one call per reply.",
        )

    prose = (text[:idx] + text[tail_start:]).strip()
    return ParsedResponse(text=prose, tool_call=ToolCall(name=payload["name"], args=args), error=None)
