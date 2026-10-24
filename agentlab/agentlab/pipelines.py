"""Part 1: the four pipelines.

Each one takes the model as an argument and makes every model call through it.
None of them imports a provider; none of them knows what an API is. That is
what makes them testable with a ``ScriptedLM`` and reusable as tools in Part 2.

The progression is deliberate:

    priority      one call, one parse, one output contract
    digest        many calls, but *our* code owns the control flow
    bm25          no model at all
    email_qa      the model decides when to stop ── the first agent-shaped thing

``email_qa`` is where a fixed pipeline ends. The model chooses the next query
and when it has enough, but the *budget* — at most three searches — stays in
our code, because a loop that trusts the model to stop is a loop that does not
stop.
"""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional

from . import bm25
from .corpus import doc_lines, email_text
from .tokens import count_tokens
from .types import DocWindow, Email, LMCallable, SearchResult

CATEGORIES = ("urgent", "normal", "ignore")

RUBRIC = """\
Judge the email from the point of view of the person it is addressed to, at the
time it was sent. A working day is Monday to Friday.

urgent  The email asks the recipient to do something, or reports a live problem
        the recipient is responsible for, and the action is needed the same day,
        the next working day, or by a stated deadline at most two working days away.
normal  Mail written for this recipient or a small working group, with no
        deadline in the next two working days: status updates, questions,
        documents for review, scheduling, personal notes.
ignore  Mail the recipient can leave unread: advertising, newsletters,
        announcements to large lists, automated notifications that ask nothing.

The wording does not decide the label. A mass mailing that says "act now" is
ignore. An email with URGENT in the subject that asks nothing of the recipient
is not urgent.
"""


# --------------------------------------------------------------------------
# problem 1: one call
# --------------------------------------------------------------------------

def run_priority(email: Email, lm: LMCallable) -> dict:
    """Classify one email as urgent / normal / ignore, with a one-line reason.

    The output contract is the interesting part: the model returns prose, so
    the pipeline has to survive a reply with no label at all. That case is
    ``unknown`` — not a guess, and not an exception.
    """
    prompt = "\n".join([
        "TASK=priority",
        "Classify one email for its recipient.",
        "",
        "RUBRIC:",
        RUBRIC,
        "Answer with exactly two lines:",
        "CATEGORY: urgent | normal | ignore",
        "REASON: one sentence",
        "",
        f"SUBJECT: {email.get('subject', '')}",
        f"FROM: {email.get('from', '')}",
        f"TO: {', '.join(email.get('to', []))}",
        f"DATE: {email.get('date', '')}",
        f"BODY: {email.get('body', '')}",
    ])

    reply = lm([{"role": "user", "content": prompt}])

    category = "unknown"
    m = re.search(r"CATEGORY\s*:\s*([A-Za-z]+)", reply)
    if m:
        word = m.group(1).lower()
        if word in CATEGORIES:
            category = word

    reason = ""
    m = re.search(r"REASON\s*:\s*(.+)", reply, re.S)
    if m:
        reason = m.group(1).strip().splitlines()[0].strip()

    if not reason:
        reason = "The model gave no reason." if category != "unknown" else "The model stated no category."

    return {"category": category, "reason": reason}


# --------------------------------------------------------------------------
# problem 2: many calls, our control flow
# --------------------------------------------------------------------------

def _classify_all(emails: list[Email], lm: LMCallable) -> list[tuple[Email, str]]:
    """Classify concurrently. The calls are independent, so this is I/O bound."""
    if not emails:
        return []
    workers = min(8, len(emails))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        labels = list(pool.map(lambda e: run_priority(e, lm), emails))
    return [(e, lab["category"]) for e, lab in zip(emails, labels)]


def run_daily_digest(emails: list[Email], lm: LMCallable, *, max_words: int = 300) -> str:
    """A morning summary of one day's mail.

    Three constraints decide the design, and all three are checked by tests:

      · at most ``max_words`` words — enforced in the prompt, because cutting
        the model's text afterwards loses content and reads badly;
      · every urgent item named — so each urgent email contributes its subject,
        which is where the company, project or site name lives;
      · nothing from the ignore pile — so the filter happens before the final
        call, not inside it.
    """
    if not emails:
        return "No email arrived that day."

    labelled = _classify_all(emails, lm)

    # one item per thread: keep the first email of a thread, which is the one
    # that states the request rather than replying to it
    seen_threads: set[str] = set()
    items: list[tuple[str, str, str]] = []  # (label, subject-ish, detail)
    for email, label in labelled:
        if label == "ignore":
            continue
        thread = email.get("thread_id") or email["id"]
        if thread in seen_threads:
            continue
        seen_threads.add(thread)
        subject = email.get("subject") or "(no subject)"
        detail = email.get("body", "").strip().split(". ")[0][:120]
        items.append((label, subject, detail))

    # urgent first, stable within a group
    items.sort(key=lambda it: 0 if it[0] == "urgent" else 1)

    lines = [f"- [{label}] {subject} | {detail}" for label, subject, detail in items]
    prompt = "\n".join([
        "TASK=digest",
        f"Write a morning summary of this day's email in at most {max_words} words.",
        "Name every urgent item by the company, project or site it mentions.",
        "Do not mention anything that was filtered out as ignore.",
        "",
        "ITEMS:",
        *lines,
    ])
    text = lm([{"role": "user", "content": prompt}]).strip()
    return text


# --------------------------------------------------------------------------
# problem 3: retrieval with no model
# --------------------------------------------------------------------------

def build_email_index(emails: list[Email]) -> bm25.Index:
    return bm25.build([email_text(e) for e in emails])


def make_search(emails: list[Email], index: bm25.Index) -> Callable[[str, int], list[Email]]:
    """The ``search(query, k)`` callable ``run_email_qa`` is handed."""

    def search(query: str, k: int = 5) -> list[Email]:
        hits = bm25.search(index, query, k)
        return [dict(emails[doc_id]) for doc_id, _score in hits]

    return search


# --------------------------------------------------------------------------
# problem 4: multi-hop QA
# --------------------------------------------------------------------------

HOP_BUDGET = 3


def run_email_qa(question: str, search: Callable[[str, int], list[Email]],
                 lm: LMCallable, *, k: int = 4) -> dict:
    """Answer a question, searching at most ``HOP_BUDGET`` times.

    The loop belongs to our code. The model may ask for another search or give
    an answer; whatever it says, the fourth search does not happen. That budget
    is the difference between a pipeline and a runaway.
    """
    searched: dict[str, Email] = {}
    queries: list[str] = []
    query = question
    answer: Optional[str] = None

    for _hop in range(HOP_BUDGET):
        hits = search(query, k)
        queries.append(query)
        for e in hits:
            searched[e["id"]] = e
        if not hits:
            break

        context = "\n".join(
            f"[{e['id']}] {e.get('subject', '')}: {e.get('body', '')}" for e in hits
        )
        prompt = "\n".join([
            "TASK=qa",
            "Answer the question from the retrieved emails, or ask for one more search.",
            "Reply with exactly one of:",
            "ANSWER: <short answer>",
            "SEARCH: <query>",
            "If the emails do not contain the answer, reply ANSWER: NONE",
            "",
            f"QUESTION: {question}",
            "CONTEXT:",
            context,
        ])
        reply = lm([{"role": "user", "content": prompt}])

        m = re.search(r"ANSWER\s*:\s*(.+)", reply, re.I)
        if m:
            candidate = m.group(1).strip().splitlines()[0].strip()
            if candidate.upper() not in ("NONE", "N/A", "UNKNOWN", ""):
                answer = candidate
            break

        m = re.search(r"SEARCH\s*:\s*(.+)", reply, re.I)
        if not m:
            break
        next_query = m.group(1).strip().splitlines()[0].strip()
        if not next_query or next_query in queries:
            break
        query = next_query

    if answer is None:
        return {"answer": None, "support": [], "searches": len(queries)}
    return {"answer": answer, "support": _support(answer, searched, question), "searches": len(queries)}


def _support(answer: str, searched: dict[str, Email], question: str) -> list[str]:
    """The retrieved emails the answer rests on.

    A short answer ("240k") shares few tokens with the email that states it, so
    support is ranked on the answer's content words with the question removed,
    falling back to the question when the answer is a bare name.
    """
    from .tokenizer import tokenize

    q = set(tokenize(question))
    a = set(tokenize(answer)) - q - {"the", "a", "an", "is", "was", "of"}
    probe = a or set(tokenize(answer))

    scored = []
    for eid, email in searched.items():
        terms = set(tokenize(email_text(email)))
        overlap = len(probe & terms)
        if overlap:
            scored.append((overlap, eid))
    scored.sort(key=lambda kv: (-kv[0], kv[1]))
    return [eid for _n, eid in scored[:2]]


# --------------------------------------------------------------------------
# document retrieval, sized for an agent rather than for our code
# --------------------------------------------------------------------------

SNIPPET_TOKENS = 150
WINDOW_TOKENS = 1500


def build_doc_index(docs: list[dict]) -> bm25.Index:
    """Index the documents. Whole documents here — see chapter 3 on chunking.

    With six short documents, chunking buys nothing and costs boundary
    problems. At handbook scale (thousands of words) it starts to matter, which
    is exactly the trade-off the memo asks about.
    """
    return bm25.build([f"{d['title']}\n{d['text']}" for d in docs])


def search_docs(docs: list[dict], index: bm25.Index, query: str, k: int = 5) -> list[SearchResult]:
    """Pointers plus short evidence — never whole documents.

    A tool result goes into the model's context as-is, so a search that returns
    entire documents fills the context window in two calls. What comes back
    here is what a good search interface returns: which document, what it is
    called, and the one line that made it match.
    """
    from .tokenizer import tokenize

    out: list[SearchResult] = []
    for doc_id, _score in bm25.search(index, query, k):
        doc = docs[doc_id]
        out.append({
            "doc_id": doc["doc_id"],
            "title": doc["title"],
            "snippet": _snippet(doc, query),
        })
    return out


def _snippet(doc: dict, query: str) -> str:
    """The best-matching line, cut to the token budget."""
    from .tokenizer import tokenize

    terms = set(tokenize(query))
    best, best_hits = "", 0
    for line in doc_lines(doc):
        hits = len(terms & set(tokenize(line)))
        if hits > best_hits:
            best, best_hits = line, hits
    if not best:
        best = doc_lines(doc)[0]

    if count_tokens(best) <= SNIPPET_TOKENS:
        return best
    return best[: SNIPPET_TOKENS * 4].rstrip() + " …"


def read_doc(docs: list[dict], doc_id: str, start_line: int = 1) -> DocWindow:
    """A window of one document, bounded by lines *and* by tokens.

    One paragraph per line means lines are long, so a line bound alone does not
    bound the context. ``total_lines`` in the result is how the model knows
    whether to ask for the next window.
    """
    doc = next((d for d in docs if d["doc_id"] == doc_id), None)
    if doc is None:
        raise LookupError(f"no document with doc_id {doc_id!r}")

    lines = doc_lines(doc)
    total = len(lines)
    if start_line < 1 or start_line > total:
        raise ValueError(f"start_line {start_line} is outside {doc_id} (1..{total})")

    taken: list[str] = []
    tokens = 0
    i = start_line - 1
    while i < total:
        t = count_tokens(lines[i])
        if taken and tokens + t > WINDOW_TOKENS:
            break
        taken.append(lines[i])
        tokens += t
        i += 1

    return {
        "doc_id": doc_id,
        "start_line": start_line,
        "end_line": start_line + len(taken) - 1,
        "total_lines": total,
        "text": "\n".join(taken),
    }
