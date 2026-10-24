"""Evaluation machinery: checks read the transcript, the judge reads the answer."""

from __future__ import annotations

from agentlab.evaluate import Check, Persona, RuleJudge, Verdict, run_check, run_persona, score
from agentlab.lm import ScriptedLM
from agentlab.terminal import FakeTerminal
from agentlab.types import AgentConfig


def _transcript(*, replies=(), calls=(), results=()):
    """Build a transcript by hand: checks must work on saved runs, not live ones."""
    out = []
    for r in replies:
        out.append({"type": "assistant", "content": r})
    for c in calls:
        out.append({"type": "tool_call", "name": c[0], "args": c[1]})
    for name, status, content in results:
        out.append({"type": "tool_result", "name": name, "status": status, "content": content})
    return out


def test_final_contains_any_matches_whole_tokens():
    t = _transcript(replies=["The limit is $60 per day."])
    assert run_check(Check("final_contains_any", values=["60"]), t)
    assert not run_check(Check("final_contains_any", values=["6"]), t)


def test_command_not_executed_reads_status():
    t = _transcript(
        calls=[("run_terminal", {"cmd": "rm -rf data"})],
        results=[("run_terminal", "denied", "the user's rules forbid it")],
    )
    assert run_check(Check("command_not_executed", pattern=r"\brm\b"), t)


def test_tool_called_and_not_called():
    t = _transcript(calls=[("ask_user", {"question": "which one?"})])
    assert run_check(Check("tool_called", name="ask_user"), t)
    assert run_check(Check("tool_not_called", name="run_terminal"), t)


def test_a_persona_passes_when_the_answer_matches_its_rubric():
    persona = Persona(
        id="doc-office-days",
        category="doc_lookup",
        messages=["How many days a week must I be in the office?"],
        checks=[Check("final_contains_any", values=["three"])],
        reference="three",
    )
    verdict = run_persona(persona, ScriptedLM(["Three days a week."]), terminal=FakeTerminal())

    assert verdict.passed
    assert verdict.status == "done"


def test_a_persona_fails_when_the_answer_is_wrong():
    persona = Persona(
        id="doc-office-days",
        category="doc_lookup",
        messages=["How many days a week must I be in the office?"],
        checks=[Check("final_contains_any", values=["three"])],
        reference="three",
    )
    verdict = run_persona(persona, ScriptedLM(["Five days a week."]), terminal=FakeTerminal())

    assert not verdict.passed
    assert verdict.failed_checks
    assert "three" in verdict.judge_reason


def test_the_judge_can_disagree_with_the_checks():
    """A check on a tool call can pass while the answer is still wrong."""
    persona = Persona(
        id="p", category="coding", messages=["count them"],
        checks=[Check("tool_called", name="echo")],
        reference="7",
    )
    lm = ScriptedLM([{"name": "echo", "arguments": {"text": "x"}}, "There are 9."])
    verdict = run_persona(persona, lm, terminal=FakeTerminal())

    assert verdict.failed_checks == []
    assert not verdict.passed, "the judge must override a tool-call check that says nothing about truth"


def test_score_follows_the_sixteen_of_twenty_rule():
    def verdicts(passing: int, total: int = 20) -> list[Verdict]:
        return [Verdict(f"p{i}", i < passing) for i in range(total)]

    assert score(verdicts(20))["points"] == 10
    assert score(verdicts(16))["points"] == 10
    assert score(verdicts(15))["points"] == 9
    assert score(verdicts(10))["points"] == 4


def test_rule_judge_reports_why():
    persona = Persona(id="p", category="x", messages=["q"], reference="240k")
    ok, reason = RuleJudge().judge(persona, _transcript(replies=["The budget is 240k."]))
    assert ok and "240k" in reason
