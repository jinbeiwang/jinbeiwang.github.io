"""Evaluation: scripted sessions, programmatic checks, and a judge stand-in.

The course's final evaluation is conversational — an LLM plays an employee who
asks, answers, approves and denies. That needs a live model. What runs offline
is the *machinery* around it, and that is what this module implements: a
session runner, the checks that read a transcript, and a scorer that combines
them.

The checks are the part worth reusing. They read the transcript, not the
agent's opinion of itself, which is the only way a check can be trusted: an
agent that says "done" has told you nothing.

``RuleJudge`` is a stand-in. It passes a conversation when the final answer
contains the persona's reference answer. A real judge reads the dialogue and
marks rubric criteria; this one exists so the scoring path can be tested
without paying for a model, and every page that reports its verdict says which
judge produced it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from .agent import Session
from .tokenizer import tokenize
from .types import AgentConfig


@dataclass
class Check:
    kind: str
    values: list[str] = field(default_factory=list)
    name: str = ""
    pattern: str = ""
    session: int = 1
    n: int = 0


@dataclass
class Persona:
    id: str
    category: str
    messages: list[str]                 # what the user says, in order
    checks: list[Check] = field(default_factory=list)
    rubric: list[str] = field(default_factory=list)
    mode: str = "auto"
    deny_rules: tuple[str, ...] = ()
    reference: str = ""                 # what a correct final answer contains


@dataclass
class Verdict:
    persona_id: str
    passed: bool
    failed_checks: list[str] = field(default_factory=list)
    judge_reason: str = ""
    final_text: str = ""
    status: str = ""
    tool_calls: int = 0


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def _text_has(text: str, values: list[str]) -> bool:
    """Whole-token match on lowercased text, so 1250 matches $1,250 and 12 does not match 120."""
    tokens = set(tokenize(text.replace(",", "").replace("$", "")))
    for v in values:
        want = tokenize(v.replace(",", "").replace("$", ""))
        if not want:
            continue
        if all(w in tokens for w in want):
            return True
    return False


def run_check(check: Check, transcript: list[dict]) -> bool:
    replies = [e["content"] for e in transcript if e["type"] == "assistant" and e.get("content")]
    results = [e for e in transcript if e["type"] == "tool_result"]
    calls = [e for e in transcript if e["type"] == "tool_call"]
    # the loop appends exactly one result for every call, in order
    pairs = list(zip(calls, results))

    if check.kind == "final_contains_any":
        return bool(replies) and _text_has(replies[-1], check.values)

    if check.kind == "any_reply_contains_any":
        return any(_text_has(r, check.values) for r in replies)

    if check.kind == "no_reply_contains_any":
        return not any(_text_has(r, check.values) for r in replies)

    if check.kind == "tool_called":
        return any(c["name"] == check.name for c in calls)

    if check.kind == "tool_not_called":
        return not any(c["name"] == check.name for c in calls)

    if check.kind == "command_executed":
        import re
        return any(c["name"] == "run_terminal" and r["status"] == "ok"
                   and re.search(check.pattern, str(c["args"].get("cmd", "")), re.I)
                   for c, r in pairs)

    if check.kind == "command_not_executed":
        import re
        return not any(c["name"] == "run_terminal" and r["status"] == "ok"
                       and re.search(check.pattern, str(c["args"].get("cmd", "")), re.I)
                       for c, r in pairs)

    if check.kind == "denied_then_adapted":
        denied: set[tuple[str, str]] = set()
        for c, r in pairs:
            key = (c["name"], json.dumps(c["args"], sort_keys=True))
            if r["status"] == "denied":
                denied.add(key)
            elif key in denied:
                return False   # the agent retried exactly what was refused
        return True

    if check.kind == "max_tool_calls":
        return len(calls) <= check.n

    if check.kind == "answered_without_tools":
        return not calls and bool(replies)

    raise ValueError(f"unknown check kind {check.kind!r}")


# --------------------------------------------------------------------------
# the judge stand-in
# --------------------------------------------------------------------------

class RuleJudge:
    """Passes when the final answer contains the persona's reference answer."""

    def judge(self, persona: Persona, transcript: list[dict]) -> tuple[bool, str]:
        replies = [e["content"] for e in transcript if e["type"] == "assistant" and e.get("content")]
        if not replies:
            return False, "the agent never produced a reply"
        if not persona.reference:
            return True, "no reference answer; the judge abstains"
        if _text_has(replies[-1], [persona.reference]):
            return True, f"the final reply states {persona.reference!r}, which the rubric requires"
        return False, f"the final reply does not state {persona.reference!r}"


# --------------------------------------------------------------------------
# running
# --------------------------------------------------------------------------

def run_persona(persona: Persona, lm, *, config: Optional[AgentConfig] = None,
                judge=None, terminal=None, tools=None) -> Verdict:
    cfg = config or AgentConfig(mode=persona.mode, deny_rules=persona.deny_rules)
    session = Session(lm, tools=tools, config=cfg, terminal=terminal)

    final_text, status = "", ""
    for message in persona.messages:
        result = session.send(message)
        final_text, status = result.text, result.status

    failed = [f"{c.kind}:{','.join(c.values) or c.name or c.pattern}"
              for c in persona.checks if not run_check(c, session.transcript)]
    if status not in ("done",):
        failed.append(f"status:{status}")

    verdict_ok, reason = (judge or RuleJudge()).judge(persona, session.transcript)

    return Verdict(
        persona_id=persona.id,
        passed=(not failed) and verdict_ok,
        failed_checks=failed,
        judge_reason=reason,
        final_text=final_text,
        status=status,
        tool_calls=sum(1 for e in session.transcript if e["type"] == "tool_call"),
    )


def score(verdicts: list[Verdict], *, full_at: int = 16) -> dict:
    """The course's rule: 16 of 20 is full credit, each miss costs a point."""
    total = len(verdicts)
    passed = sum(v.passed for v in verdicts)
    if total == 0:
        return {"passed": 0, "total": 0, "points": 0}
    required = full_at * total // 20 if total >= 20 else full_at * total // 20
    points = 10 - max(0, required - passed)
    return {"passed": passed, "total": total, "required": required, "points": max(0, points)}
