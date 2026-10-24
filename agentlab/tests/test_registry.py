"""The registry: validate separately from execute, contain every failure."""

from __future__ import annotations

from agentlab.registry import ToolRegistry, validate_args
from agentlab.types import ToolSpec
from conftest import echo_spec, write_spec


def test_schemas_expose_exactly_three_keys():
    reg = ToolRegistry([echo_spec()])
    (schema,) = reg.schemas()
    assert set(schema) == {"name", "description", "parameters"}
    assert "fn" not in schema and "read_only" not in schema


def test_registration_order_is_preserved():
    reg = ToolRegistry([echo_spec(), write_spec()])
    assert [s["name"] for s in reg.schemas()] == ["echo", "write_file"]


def test_unknown_tool():
    reg = ToolRegistry([echo_spec()])
    result = reg.execute("nope", {})
    assert result.status == "unknown_tool"
    assert "echo" in result.content  # the error names what does exist


def test_missing_required_argument_is_not_executed():
    reg = ToolRegistry([echo_spec()])
    result = reg.execute("echo", {})
    assert result.status == "invalid_args"
    assert "required" in result.content


def test_wrong_type_is_rejected():
    reg = ToolRegistry([echo_spec()])
    assert reg.execute("echo", {"text": 42}).status == "invalid_args"


def test_schema_violation_is_not_executed():
    reg = ToolRegistry([echo_spec()])
    assert reg.validate("echo", {}) is not None      # validate alone is enough
    assert reg.validate("echo", {"text": "ok"}) is None


def test_tool_exception_is_contained():
    def boom() -> str:
        raise ValueError("the tool broke")

    spec = ToolSpec("boom", "raise", {"type": "object", "properties": {}}, boom, read_only=True)
    result = ToolRegistry([spec]).execute("boom", {})

    assert result.status == "tool_error"
    assert "the tool broke" in result.content


def test_success_is_str_of_the_return_value():
    spec = ToolSpec("num", "returns a number", {"type": "object", "properties": {}},
                    lambda: 7, read_only=True)
    result = ToolRegistry([spec]).execute("num", {})
    assert result.status == "ok" and result.content == "7"


def test_additional_properties_rejected_when_forbidden():
    problems = validate_args(
        {"type": "object", "properties": {"a": {"type": "string"}}, "additionalProperties": False},
        {"a": "x", "b": "y"},
    )
    assert problems and "not a known argument" in problems[0]


def test_boolean_is_not_an_integer():
    problems = validate_args({"type": "object", "properties": {"n": {"type": "integer"}}}, {"n": True})
    assert problems
