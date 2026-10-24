"""The toolset the agent runs on — the replacement for ``cardinal.py``.

Ten tools. Two properties are fixed by the assignment and everything else is a
judgement call:

  · **names, argument schemas and read-only flags do not change**, because they
    are the interface the tests and the approval layer depend on;
  · **descriptions do change, and they are not decoration.** A description is
    the only thing the model knows about a tool. "Run one shell command" and
    "Run one shell command. No here-documents; write multi-line Python as
    python3 -c '...'" produce measurably different behaviour from the same
    model, which is why the descriptions here say what *not* to do.

The lazy index (``_ensure_indexes``) is the other load-bearing detail: creating
a session must not read the corpus. Building the email index at construction
time would make every test pay for it and would make a two-tool session pay for
tools it does not have.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from . import bm25, pipelines
from .corpus import load_docs, load_emails
from .tokens import count_tokens, count_message_tokens
from .types import ToolSpec

#: what the model sees of one terminal result, in tokens
TERMINAL_TOKENS = 800


def _clip(text: str, tokens: int) -> str:
    if count_tokens(text) <= tokens:
        return text
    return text[: tokens * 4].rstrip() + f"\n… [cut at {tokens} tokens]"


class ToolContext:
    """Lazily built indexes plus the settings the tools close over."""

    def __init__(self, config, terminal=None):
        self.config = config
        self.terminal = terminal
        self._emails: Optional[list[dict]] = None
        self._email_index = None
        self._docs: Optional[list[dict]] = None
        self._doc_index = None
        self.memory = None

    # -- indexes ----------------------------------------------------------
    @property
    def emails(self) -> list[dict]:
        if self._emails is None:
            self._emails = load_emails()
        return self._emails

    @property
    def email_index(self):
        if self._email_index is None:
            self._email_index = pipelines.build_email_index(self.emails)
        return self._email_index

    @property
    def docs(self) -> list[dict]:
        if self._docs is None:
            self._docs = load_docs()
        return self._docs

    @property
    def doc_index(self):
        if self._doc_index is None:
            self._doc_index = pipelines.build_doc_index(self.docs)
        return self._doc_index

    # -- the observation policy for the terminal --------------------------
    def observation(self, raw: str) -> str:
        """What the model sees when a command printed more than fits.

        Head and tail, with a note in the middle. The alternative — write the
        full output to a file and tell the model the path — is better for
        follow-up questions but only works if the model then spends a turn
        reading that file, and this sandbox forbids redirection anyway. The
        choice is the memo's question 5.
        """
        if count_tokens(raw) <= TERMINAL_TOKENS:
            return raw
        head = raw[: int(TERMINAL_TOKENS * 4 * 0.6)]
        tail = raw[-int(TERMINAL_TOKENS * 4 * 0.3):]
        dropped = len(raw) - len(head) - len(tail)
        return f"{head}\n… [{dropped} characters omitted; narrow the command to see them] …\n{tail}"


def _fmt_emails(hits: list[dict]) -> str:
    if not hits:
        return "No email matched that query."
    lines = []
    for e in hits:
        body = " ".join(e.get("body", "").split())[:200]
        lines.append(f"[{e['id']}] {e['date'][:10]} | {e.get('subject') or '(no subject)'} | {body}")
    return "\n".join(lines)


def build_toolset(ctx: ToolContext, ask_user=None) -> list[ToolSpec]:
    """The ten tools, wired to ``ctx``. Descriptions are the prompt."""

    # -- retrieval over email --------------------------------------------
    def search_emails(query: str, k: int = 5) -> str:
        hits = pipelines.make_search(ctx.emails, ctx.email_index)(query, k)
        return _fmt_emails(hits)

    def read_email(email_id: str) -> str:
        from .corpus import get_email

        email = get_email(email_id)
        if email is None:
            raise LookupError(f"no email with id {email_id!r}")
        body = _clip(email.get("body", ""), 1200)
        return (
            f"[{email['id']}] {email['date']}\n"
            f"From: {email['from']}\nTo: {', '.join(email['to'])}\n"
            f"Subject: {email.get('subject') or '(no subject)'}\n\n{body}"
        )

    def email_qa(question: str) -> str:
        search = pipelines.make_search(ctx.emails, ctx.email_index)
        out = pipelines.run_email_qa(question, search, ctx.config.aux_lm or _no_lm)
        if out["answer"] is None:
            return "No answer found in the archive."
        support = ", ".join(out["support"]) or "none"
        return f"{out['answer']}\n\nSupporting emails: {support}"

    def daily_digest(date: str) -> str:
        from .corpus import emails_on

        day = emails_on(date)
        if not day:
            return f"No email on {date}."
        return pipelines.run_daily_digest(day, ctx.config.aux_lm or _no_lm)

    # -- retrieval over documents ----------------------------------------
    def search_docs(query: str, k: int = 5) -> str:
        results = pipelines.search_docs(ctx.docs, ctx.doc_index, query, k)
        if not results:
            return "No document matched that query."
        lines = []
        for r in results:
            total = len(pipelines.doc_lines(next(d for d in ctx.docs if d["doc_id"] == r["doc_id"])))
            lines.append(f"{r['doc_id']} — {r['title']} ({total} lines)\n  {r['snippet']}")
        return "\n".join(lines)

    def read_doc(doc_id: str, start_line: int = 1) -> str:
        w = pipelines.read_doc(ctx.docs, doc_id, start_line)
        more = "" if w["end_line"] >= w["total_lines"] else (
            f"\n\n[lines {w['start_line']}-{w['end_line']} of {w['total_lines']}; "
            f"call read_doc again with start_line={w['end_line'] + 1} for more]"
        )
        return f"{w['doc_id']} lines {w['start_line']}-{w['end_line']} of {w['total_lines']}\n{w['text']}{more}"

    # -- the terminal -----------------------------------------------------
    def run_terminal(cmd: str) -> str:
        if ctx.terminal is None:
            raise RuntimeError("no terminal is configured for this session")
        result = ctx.terminal.run(cmd, workspace=ctx.config.workspace,
                                  timeout=ctx.config.terminal_timeout)
        if result.rejected:
            raise RuntimeError(f"the command was refused: {result.reason}")
        if result.timed_out:
            raise RuntimeError(f"the command timed out after {ctx.config.terminal_timeout}s")

        shown_out = ctx.observation(result.stdout)
        shown_err = ctx.observation(result.stderr)
        body = f"exit code {result.exit_code}\nstdout:\n{shown_out}"
        if shown_err.strip():
            body += f"\nstderr:\n{shown_err}"
        if not result.ok:
            raise RuntimeError(body)
        return body

    # -- memory -----------------------------------------------------------
    def remember(fact: str) -> str:
        if ctx.memory is None:
            raise RuntimeError("this session has no memory directory")
        f = ctx.memory.remember(fact)
        return f"Remembered ({f.id})."

    def recall(query: str) -> str:
        if ctx.memory is None:
            raise RuntimeError("this session has no memory directory")
        facts = ctx.memory.recall(query)
        if not facts:
            return "Nothing in memory matches that. The store is empty or has nothing on this topic."
        return "\n".join(f"- {f.line()} ({f.id})" for f in facts)

    tools = [
        ToolSpec(
            "search_emails",
            "Search the 2001 email archive with BM25. Returns up to k matching emails as "
            "[id] date | subject | first 200 characters. Use read_email with an id to see one in full.",
            {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "minLength": 1, "description": "search terms"},
                    "k": {"type": "integer", "minimum": 1, "maximum": 20},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
            search_emails, read_only=True,
        ),
        ToolSpec(
            "read_email",
            "Read one email in full by its id (for example em-0003).",
            {
                "type": "object",
                "properties": {"email_id": {"type": "string", "minLength": 1}},
                "required": ["email_id"],
                "additionalProperties": False,
            },
            read_email, read_only=True,
        ),
        ToolSpec(
            "email_qa",
            "Answer a question that needs one or two hops across the email archive. "
            "Returns the answer and the ids of the emails it rests on.",
            {
                "type": "object",
                "properties": {"question": {"type": "string", "minLength": 3}},
                "required": ["question"],
                "additionalProperties": False,
            },
            email_qa, read_only=True,
        ),
        ToolSpec(
            "daily_digest",
            "Summarise one day of the email archive. Date is YYYY-MM-DD.",
            {
                "type": "object",
                "properties": {"date": {"type": "string", "minLength": 10, "maxLength": 10}},
                "required": ["date"],
                "additionalProperties": False,
            },
            daily_digest, read_only=True,
        ),
        ToolSpec(
            "search_docs",
            "Search the company documents. Returns doc_id, title and a short snippet. "
            "This is a pointer, not the document: call read_doc to read it.",
            {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "minLength": 1},
                    "k": {"type": "integer", "minimum": 1, "maximum": 10},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
            search_docs, read_only=True,
        ),
        ToolSpec(
            "read_doc",
            "Read a line window of one document. Returns at most ~1500 tokens and tells you "
            "the total line count; call again with the next start_line to continue.",
            {
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "minLength": 1},
                    "start_line": {"type": "integer", "minimum": 1},
                },
                "required": ["doc_id"],
                "additionalProperties": False,
            },
            read_doc, read_only=True,
        ),
        ToolSpec(
            "run_terminal",
            "Run one shell command in a workspace that holds the email archive and documents. "
            "Arguments must be plain shell: no here-documents, no command substitution, no "
            "redirection. Write multi-line Python as python3 -c '...'. Returns the exit code, "
            "stdout and stderr. Large output is truncated in the middle.",
            {
                "type": "object",
                "properties": {"cmd": {"type": "string", "minLength": 1}},
                "required": ["cmd"],
                "additionalProperties": False,
            },
            run_terminal, read_only=False,
        ),
        ToolSpec(
            "remember",
            "Store one durable fact about the user in persistent memory, for later sessions. "
            "Store what the user told you, not what you guessed.",
            {
                "type": "object",
                "properties": {"fact": {"type": "string", "minLength": 3}},
                "required": ["fact"],
                "additionalProperties": False,
            },
            remember, read_only=True,
        ),
        ToolSpec(
            "recall",
            "Search persistent memory from earlier sessions.",
            {
                "type": "object",
                "properties": {"query": {"type": "string", "minLength": 1}},
                "required": ["query"],
                "additionalProperties": False,
            },
            recall, read_only=True,
        ),
        ToolSpec(
            "ask_user",
            "Ask the user one clarifying question when the request cannot be answered without "
            "a detail only they know. Do not use it to confirm something you can look up.",
            {
                "type": "object",
                "properties": {"question": {"type": "string", "minLength": 3}},
                "required": ["question"],
                "additionalProperties": False,
            },
            ask_user or (lambda question: "No user is available to answer."),
            read_only=True,
        ),
    ]
    return tools


def _no_lm(messages, **kw):  # pragma: no cover - only reached without a model
    raise RuntimeError("this tool needed a model but the session has none")
