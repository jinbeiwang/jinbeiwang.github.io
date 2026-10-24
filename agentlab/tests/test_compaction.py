"""Compaction: the budget holds for every call of a long session."""

from __future__ import annotations

from agentlab.agent import Session
from agentlab.lm import FnLM, ScriptedLM
from agentlab.protocol import format_tool_call
from agentlab.terminal import FakeTerminal
from agentlab.tokens import count_message_tokens
from agentlab.types import AgentConfig, ToolCall

from conftest import big_spec, echo_spec

BUDGET = 4000


def test_budget_holds_over_sixty_calls():
    """59 large tool results then a final answer, at a 4,000-token budget.

    The last tool result must never be shortened: the contract is that it
    appears verbatim in the call that immediately follows it.
    """
    repeated = format_tool_call("", ToolCall("big", {"n": 1}))
    replies = [repeated] * 59 + ["Done."]
    lm = ScriptedLM(replies)

    # compaction's summary calls must not eat a scripted reply
    aux = FnLM(lambda messages: "Earlier: the agent read several large outputs.")
    session = Session(
        lm, tools=[echo_spec(), big_spec(2000)],
        config=AgentConfig(context_budget=BUDGET, max_turns=80, aux_lm=aux),
        terminal=FakeTerminal(),
    )

    result = session.send("read a lot of data")

    assert result.status == "done"
    assert len(lm.calls) == 60
    worst = max(count_message_tokens(messages) for messages in lm.calls)
    assert worst <= BUDGET, f"largest call was {worst} tokens, budget is {BUDGET}"


def test_recent_tool_result_is_never_shortened():
    repeated = format_tool_call("", ToolCall("big", {"n": 1}))
    replies = [repeated] * 12 + ["Done."]
    lm = ScriptedLM(replies)
    aux = FnLM(lambda messages: "summary")
    session = Session(
        lm, tools=[big_spec(3000)],
        config=AgentConfig(context_budget=BUDGET, max_turns=20, aux_lm=aux),
        terminal=FakeTerminal(),
    )
    session.send("go")

    # for every call after a tool result, the newest result is present in full
    for messages in lm.calls[1:]:
        last = messages[-1]["content"]
        if last.startswith("TOOL RESULT"):
            assert "x" * 3000 in last, "the newest tool result was compacted away"


def test_short_session_is_untouched():
    lm = ScriptedLM(["hello", "again"])
    aux = FnLM(lambda messages: "unused")
    session = Session(lm, tools=[echo_spec()],
                      config=AgentConfig(context_budget=BUDGET, aux_lm=aux),
                      terminal=FakeTerminal())
    session.send("one")
    session.send("two")

    assert len(aux.calls) == 0, "no summary should be paid for when nothing needs compacting"


def test_current_user_message_survives_compaction():
    repeated = format_tool_call("", ToolCall("big", {"n": 1}))
    lm = ScriptedLM([repeated] * 10 + ["ok"])
    aux = FnLM(lambda messages: "summary")
    session = Session(lm, tools=[big_spec(3000)],
                      config=AgentConfig(context_budget=BUDGET, max_turns=20, aux_lm=aux),
                      terminal=FakeTerminal())

    session.send("the opening constraint: never touch production")

    for messages in lm.calls:
        joined = "\n".join(str(m["content"]) for m in messages)
        assert "never touch production" in joined
