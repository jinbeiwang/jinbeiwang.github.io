"""The loop: termination, budgets, malformed recovery, transcript discipline."""

from __future__ import annotations

from agentlab.agent import Session
from agentlab.lm import FnLM, OutputTruncated, ScriptedLM
from agentlab.protocol import format_tool_call
from agentlab.terminal import FakeTerminal
from agentlab.types import AgentConfig, ToolCall

from conftest import big_spec, echo_spec, events, write_spec


def session_with(replies, tools=None, **cfg):
    lm = ScriptedLM(replies)
    cfg.setdefault("aux_lm", FnLM(lambda messages: "summary"))
    return Session(lm, tools=tools or [echo_spec()], config=AgentConfig(**cfg),
                   terminal=FakeTerminal()), lm


def test_plain_answer_is_done():
    session, lm = session_with(["Three days a week."])
    result = session.send("How many days?")

    assert result.status == "done"
    assert result.text == "Three days a week."
    assert len(lm.calls) == 1


def test_tool_result_appears_verbatim_in_the_next_call():
    call = ToolCall("echo", {"text": "the needle"})
    session, lm = session_with([{"name": call.name, "arguments": call.args}, "done"])

    result = session.send("echo please")

    assert [e["type"] for e in result.transcript] == [
        "user", "assistant", "tool_call", "tool_result", "assistant"
    ]
    assert events(result.transcript, "tool_result")[0]["content"] == "the needle"
    # the second model call must contain the result exactly
    assert "the needle" in lm.calls[1][-1]["content"]


def test_unparseable_reply_recovers():
    """Balanced but invalid JSON is a format error the model can fix."""
    session, lm = session_with(["```tool\n{not: valid json}\n```", "Recovered."])
    result = session.send("hello")

    assert result.status == "done"
    assert result.text == "Recovered."
    errors = events(result.transcript, "error")
    assert len(errors) == 1
    assert "not valid JSON" in errors[0]["content"]


def test_three_malformed_replies_stop_the_send():
    session, lm = session_with(["```tool\n{", "```tool\n{", "```tool\n{"])
    result = session.send("hello")

    assert result.status == "malformed"
    assert result.text  # never empty
    assert len(events(result.transcript, "error")) == 3


def test_unknown_tool_counts_as_malformed():
    session, _ = session_with([{"name": "nope", "arguments": {}}, "fine"])
    result = session.send("try a bad tool")

    assert result.status == "done"
    result_event = events(result.transcript, "tool_result")[0]
    assert result_event["status"] == "unknown_tool"
    assert "nope" in result_event["content"]


def test_max_turns():
    repeated = format_tool_call("", ToolCall("echo", {"text": "a"}))
    lm = ScriptedLM([{"repeat": repeated}])
    session = Session(lm, tools=[echo_spec()], config=AgentConfig(max_turns=2, aux_lm=lm),
                      terminal=FakeTerminal())

    result = session.send("loop forever")

    assert result.status == "max_turns"
    assert len(lm.calls) == 2
    assert result.text


def test_token_budget_checked_before_the_call():
    session, lm = session_with(
        [{"name": "echo", "arguments": {"text": "a"}}, "second"],
        max_turns=10, token_budget=1,
    )
    result = session.send("hello")

    assert result.status == "token_budget"
    assert len(lm.calls) == 1, "the budget was crossed by call 1, so call 2 must not happen"


def test_answer_that_crosses_the_budget_is_still_done():
    session, _ = session_with(["short answer"], token_budget=1)
    result = session.send("hello")
    assert result.status == "done", "a final answer on the crossing call still counts"


def test_truncated_output_is_reported_and_retried():
    replies = [0]

    def flaky(messages):
        replies[0] += 1
        if replies[0] <= 2:
            raise OutputTruncated("half a sen")
        return "Whole answer."

    session = Session(FnLM(flaky), tools=[echo_spec()], config=AgentConfig(), terminal=FakeTerminal())
    result = session.send("hello")

    assert result.status == "done"
    assert result.text == "Whole answer."
    assert len(events(result.transcript, "error")) == 2


def test_transcript_is_returned_as_a_copy():
    session, _ = session_with(["a"])
    result = session.send("hello")
    result.transcript.append({"type": "user", "content": "tampered"})

    assert all(e.get("content") != "tampered" for e in session.transcript)


def test_session_creation_does_not_touch_the_corpus():
    """Building a session must not build an index: that would be paid for by
    every test and by every two-tool session."""
    lm = ScriptedLM(["x"])
    session = Session(lm, tools=None, config=AgentConfig(), terminal=FakeTerminal())
    assert session.ctx._emails is None
    assert session.ctx._email_index is None
