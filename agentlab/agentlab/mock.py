"""A deterministic stand-in for a language model.

This module exists so the package runs — ``python -m agentlab show priority``,
the whole agent loop, the evaluation — with no API key and no network. It is
**not** a model. It looks for the machine-readable marker each pipeline puts at
the top of its prompt (``TASK=priority`` and friends) and applies a crude
heuristic.

The consequences, stated plainly because they are easy to misread:

  · A score produced through this module measures the *harness* (does the
    pipeline call the model, parse the reply, handle the empty case), never the
    quality of an LLM.
  · Its heuristics are deliberately cruder than the corpus's gold labels, so
    the accuracy it reports is not 100%. A stand-in that always agreed with the
    gold labels would make every test vacuous.
  · Switching to a real model is one line — see ``lm.openai_compatible_provider``.
"""

from __future__ import annotations

import re

from .tokenizer import tokenize


def respond(messages: list[dict]) -> str:
    """Produce a reply for the first recognised task marker in the prompt."""
    prompt = "\n".join(str(m.get("content", "")) for m in messages)

    if "TASK=priority" in prompt:
        return _priority(prompt)
    if "TASK=digest" in prompt:
        return _digest(prompt)
    if "TASK=next_query" in prompt:
        return _next_query(prompt)
    if "TASK=qa" in prompt:
        return _qa(prompt)
    if "TASK=summarise" in prompt:
        return _summarise(prompt)
    return "OK."


# --------------------------------------------------------------------------

def _section(prompt: str, name: str) -> str:
    """Text after a ``NAME:`` line, up to the next ALL-CAPS marker line."""
    m = re.search(rf"^{name}:\s*(.*?)(?=\n[A-Z][A-Z_ ]*:|\Z)", prompt, re.S | re.M)
    return m.group(1).strip() if m else ""


def _priority(prompt: str) -> str:
    subject = _section(prompt, "SUBJECT")
    body = _section(prompt, "BODY")
    blob = f"{subject} {body}".lower()

    mass_mail = any(k in blob for k in ("unsubscribe", "act now", "no action", "automated notice",
                                        "newsletter", "congratulations"))
    deadline = any(k in blob for k in ("today", "tomorrow", "end of day", "due friday",
                                       "by tomorrow", "required today", "two working days"))
    live_problem = any(k in blob for k in ("offline", "overdue", "outage", "waiting on your call"))

    if mass_mail:
        return "CATEGORY: ignore\nREASON: This is a mass mailing or automated notice that asks nothing of the recipient."
    if deadline or live_problem:
        return "CATEGORY: urgent\nREASON: It asks the recipient to act within a day or two, or reports a live problem they own."
    return "CATEGORY: normal\nREASON: It is mail written for this recipient with no deadline in the next two working days."


def _digest(prompt: str) -> str:
    items = re.findall(r"^- \[(urgent|normal)\] (.+?)(?: \| (.*))?$", _section(prompt, "ITEMS"), re.M)
    if not items:
        return "Nothing of note today."

    urgent = [f"{subj} ({detail})" if detail else subj for label, subj, detail in items if label == "urgent"]
    normal = [f"{subj}" for label, subj, _ in items if label == "normal"]

    parts = []
    if urgent:
        parts.append("Handle these first: " + "; ".join(urgent) + ".")
    if normal:
        parts.append("The rest of the day: " + "; ".join(normal[:6]) + ("." if len(normal) <= 6 else ", and others."))
    return " ".join(parts)[:1500]


def _qa(prompt: str) -> str:
    question = _section(prompt, "QUESTION")
    context = _section(prompt, "CONTEXT")
    if not context:
        return "ANSWER: NONE"

    q_terms = set(tokenize(question))
    best_line, best_score = "", -1.0
    for line in context.splitlines():
        line = line.strip()
        if not line:
            continue
        terms = set(tokenize(line))
        if not terms:
            continue
        overlap = len(q_terms & terms) / (len(q_terms) or 1)
        if overlap > best_score:
            best_line, best_score = line, overlap

    if best_score <= 0 or not best_line:
        return "ANSWER: NONE"

    answer = _extract(best_line)
    return f"ANSWER: {answer}" if answer else "ANSWER: NONE"


def _extract(line: str) -> str:
    """Pull the most answer-like fragment out of a retrieved line."""
    body = line.split("]", 1)[-1]
    body = body.split(":", 1)[-1] if ":" in body else body
    for sep in (". ", "; "):
        if sep in body:
            body = body.split(sep)[0]
    return body.strip()[:200]


def _next_query(prompt: str) -> str:
    question = _section(prompt, "QUESTION").lower()
    stop = {"the", "a", "an", "who", "what", "which", "does", "did", "is", "are", "was",
            "were", "of", "in", "on", "for", "to", "and", "that", "their", "its", "how",
            "many", "much", "when", "where", "why", "team", "person"}
    words = [w for w in tokenize(question) if w not in stop]
    return f"SEARCH: {' '.join(words[:4])}" if words else "SEARCH: " + question[:40]


def _summarise(prompt: str) -> str:
    text = _section(prompt, "TRANSCRIPT") or prompt
    flat = " ".join(text.split())
    return "Earlier in this session: " + flat[:600]
