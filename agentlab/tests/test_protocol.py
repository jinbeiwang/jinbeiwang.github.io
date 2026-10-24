"""The tool-call protocol: round-trip, truncation, nesting, one-call limit."""

from __future__ import annotations

from agentlab.protocol import format_tool_call, parse_response, render_tools
from agentlab.types import ToolCall


def test_round_trip_preserves_json_types():
    call = ToolCall("search", {"n": 3, "flag": True, "name": "x", "items": [1, 2]})
    parsed = parse_response(format_tool_call("Looking it up.", call))

    assert parsed.error is None
    assert parsed.tool_call == call
    assert parsed.text == "Looking it up."
    assert isinstance(parsed.tool_call.args["n"], int)
    assert isinstance(parsed.tool_call.args["flag"], bool)


def test_truncation_at_any_character_is_safe():
    """Cut the reply everywhere; never raise, never invent a call."""
    call = ToolCall("t", {"a": "x" * 20})
    text = format_tool_call("", call)

    for i in range(len(text) + 1):
        parsed = parse_response(text[:i])
        if parsed.tool_call is not None:
            assert parsed.tool_call == call, f"prefix {i} produced a different call"


def test_cut_inside_arguments_sets_error():
    text = format_tool_call("", ToolCall("t", {"a": "x" * 40}))
    cut = text[: text.find('"a"') + 10]  # inside the string value
    parsed = parse_response(cut)

    assert parsed.tool_call is None
    assert parsed.error and "cut off" in parsed.error.lower()


def test_argument_may_contain_the_protocol():
    inner = format_tool_call("", ToolCall("inner", {"k": 1}))
    call = ToolCall("outer", {"cmd": inner})

    parsed = parse_response(format_tool_call("", call))
    assert parsed.error is None
    assert parsed.tool_call.name == "outer"
    assert parsed.tool_call.args["cmd"] == inner


def test_two_calls_are_an_error():
    block = format_tool_call("", ToolCall("a", {}))
    parsed = parse_response(block + "\n\nand also\n\n" + block)

    assert parsed.tool_call is None
    assert parsed.error and "more than one" in parsed.error.lower()


def test_plain_prose_has_no_call():
    parsed = parse_response("The office requirement is three days.")
    assert parsed.tool_call is None and parsed.error is None
    assert parsed.text == "The office requirement is three days."


def test_render_tools_names_every_tool_and_the_format():
    schemas = [
        {"name": "alpha", "description": "do alpha", "parameters": {"type": "object"}},
        {"name": "beta", "description": "do beta", "parameters": {"type": "object"}},
    ]
    text = render_tools(schemas)
    assert "alpha" in text and "beta" in text
    assert "```tool" in text
