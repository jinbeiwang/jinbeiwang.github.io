"""The four pipelines: output contracts, the digest's three constraints,
the hop budget, and the document window."""

from __future__ import annotations

import pytest

from agentlab import pipelines
from agentlab.corpus import get_email, load_docs, load_emails
from agentlab.lm import FnLM, ScriptedLM
from agentlab.tokens import count_tokens


# --------------------------------------------------------------------------
# priority
# --------------------------------------------------------------------------

def test_priority_reads_the_label_and_reason():
    lm = ScriptedLM(["CATEGORY: urgent\nREASON: The audit response is due today."])
    out = pipelines.run_priority(get_email("em-0018"), lm)

    assert out["category"] == "urgent"
    assert out["reason"] == "The audit response is due today."


def test_priority_without_a_label_is_unknown_not_a_guess():
    lm = ScriptedLM(["This one looks fairly important, I think."])
    out = pipelines.run_priority(get_email("em-0018"), lm)

    assert out["category"] == "unknown"
    assert out["reason"]


def test_priority_rejects_an_invented_label():
    lm = ScriptedLM(["CATEGORY: critical\nREASON: sounds bad"])
    assert pipelines.run_priority(get_email("em-0018"), lm)["category"] == "unknown"


def test_priority_survives_an_empty_reply():
    lm = ScriptedLM([""])
    out = pipelines.run_priority(get_email("em-0018"), lm)
    assert out["category"] == "unknown" and out["reason"]


# --------------------------------------------------------------------------
# digest
# --------------------------------------------------------------------------

def test_digest_drops_ignore_and_names_every_urgent_item():
    from agentlab.corpus import emails_on

    day = emails_on("2001-06-06")

    def fn(messages):
        prompt = messages[-1]["content"]
        if "TASK=priority" in prompt:
            if "conference pass" in prompt or "Benefits enrollment" in prompt:
                return "CATEGORY: ignore\nREASON: mass mailing"
            if "Larchfield" in prompt or "Invoice 8841" in prompt:
                return "CATEGORY: urgent\nREASON: due today or Friday"
            return "CATEGORY: normal\nREASON: no deadline"
        if "TASK=digest" in prompt:
            items = [line[2:] for line in prompt.splitlines() if line.startswith("- [")]
            return "Morning. " + " | ".join(items)
        return "ok"

    text = pipelines.run_daily_digest(day, FnLM(fn))

    assert "Larchfield" in text, "an urgent item must be named"
    assert "conference pass" not in text.lower(), "the ignore pile must not appear"
    assert len(text.split()) <= 300


def test_digest_one_item_per_thread():
    from agentlab.corpus import emails_on

    day = emails_on("2001-06-04")
    prompts: list[str] = []

    def fn(messages):
        prompt = messages[-1]["content"]
        prompts.append(prompt)
        if "TASK=priority" in prompt:
            return "CATEGORY: normal\nREASON: none"
        items = [l for l in prompt.splitlines() if l.startswith("- [")]
        return f"{len(items)} items"

    out = pipelines.run_daily_digest(day, FnLM(fn))

    final_prompt = [p for p in prompts if "TASK=digest" in p][0]
    assert "Thistledown budget approved at 240k" in final_prompt
    assert "Re: Thistledown budget approved at 240k" not in final_prompt
    assert out == "6 items" or out.strip().endswith("items")


def test_empty_day_needs_no_model_call():
    def fn(messages):
        raise AssertionError("an empty day must not call the model")

    assert pipelines.run_daily_digest([], FnLM(fn)).strip()


# --------------------------------------------------------------------------
# multi-hop QA
# --------------------------------------------------------------------------

def _search():
    emails = load_emails()
    index = pipelines.build_email_index(emails)
    return pipelines.make_search(emails, index)


def test_qa_answers_in_two_hops_and_cites_support():
    """The second hop searches for the *person*, which the question never names.

    One search for the question's own words finds the email that says who
    chairs the review; a second search on that name finds the email that says
    which team they belong to. Neither email answers the question alone.
    """
    lm = ScriptedLM(["SEARCH: basin review", "SEARCH: Dana Whitfield", "ANSWER: Engineering"])
    out = pipelines.run_email_qa(
        "Which team does the person who chairs the weekly Basin review work in?",
        _search(), lm,
    )

    assert out["answer"] == "Engineering"
    assert out["support"], "a correct answer must cite at least one retrieved email"
    assert out["searches"] == 3, "two searches, then the answer"


def test_qa_stops_at_the_hop_budget():
    """Even with an endless supply of plausible queries, the fourth never runs."""
    def always(query: str, k: int = 4):
        return [get_email("em-0003")]

    lm = ScriptedLM([f"SEARCH: query{i}" for i in range(8)])
    out = pipelines.run_email_qa("anything", always, lm)

    assert out["searches"] == pipelines.HOP_BUDGET
    assert out["answer"] is None


def test_qa_reports_no_answer_rather_than_guessing():
    lm = ScriptedLM(["ANSWER: NONE"])
    out = pipelines.run_email_qa("What is the CFO's shoe size?", _search(), lm)

    assert out["answer"] is None
    assert out["support"] == []


def test_qa_support_only_names_retrieved_emails():
    lm = ScriptedLM(["SEARCH: Thistledown budget", "ANSWER: 240k"])
    out = pipelines.run_email_qa("What is the Thistledown budget?", _search(), lm)

    retrieved = {"em-0003", "em-0004", "em-0009", "em-0015"}
    assert set(out["support"]) <= retrieved


# --------------------------------------------------------------------------
# documents
# --------------------------------------------------------------------------

def test_read_doc_respects_the_token_window():
    docs = load_docs()
    window = pipelines.read_doc(docs, "employee-handbook", 1)

    assert window["start_line"] == 1
    assert window["end_line"] <= window["total_lines"]
    assert count_tokens(window["text"]) <= pipelines.WINDOW_TOKENS


def test_read_doc_errors_are_typed():
    docs = load_docs()
    with pytest.raises(LookupError):
        pipelines.read_doc(docs, "no-such-doc")
    with pytest.raises(ValueError):
        pipelines.read_doc(docs, "employee-handbook", 999)


def test_search_doc_snippets_respect_the_budget():
    docs = load_docs()
    index = pipelines.build_doc_index(docs)
    results = pipelines.search_docs(docs, index, "meals reimbursement", 5)

    assert results
    for r in results:
        assert count_tokens(r["snippet"]) <= pipelines.SNIPPET_TOKENS
        assert r["doc_id"] and r["title"]


def test_search_docs_finds_both_expense_policies():
    """The superseded document must be findable: hiding it would be worse."""
    docs = load_docs()
    index = pipelines.build_doc_index(docs)
    ids = {r["doc_id"] for r in pipelines.search_docs(docs, index, "meals reimbursement", 5)}

    assert "expense-policy-2026" in ids
    assert "expense-policy-2025" in ids
