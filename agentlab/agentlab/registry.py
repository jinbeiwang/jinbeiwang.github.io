"""The tool registry: validate, then execute — two separate steps.

The separation is the whole idea. The interactive layer has to ask the user
"may I run this?" *before* running it, and it must never ask about a call that
was going to fail validation anyway (an unknown tool, a missing argument, a
type error). If validation only happened inside ``execute``, the approval
prompt would be the first place a malformed call surfaced, and the user would
be asked to approve nonsense.

``validate`` therefore returns a ``ToolResult`` or ``None``: a result means
"this call cannot run, here is why" and execution must not proceed. It never
calls the tool and never raises.

The schema subset implemented here is small on purpose — type, required,
properties, enum, numeric and string bounds, array items, and
``additionalProperties: false``. That is enough for the assignments, and it is
about 80 lines instead of a dependency. Real code should use ``jsonschema``.
"""

from __future__ import annotations

from typing import Any, Optional

from .types import ToolResult, ToolSpec


# --------------------------------------------------------------------------
# a small JSON Schema checker
# --------------------------------------------------------------------------

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "integer": int,
    "number": (int, float),
}


def _type_ok(value: Any, wanted: str) -> bool:
    if wanted == "integer":
        # bool is a subclass of int in Python; a boolean is not an integer here
        return isinstance(value, int) and not isinstance(value, bool)
    if wanted == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    py = _TYPES.get(wanted)
    if py is None:
        return True
    return isinstance(value, py)


def validate_args(schema: dict, args: Any, path: str = "arguments") -> list[str]:
    """Every problem with ``args`` against ``schema``, as readable sentences."""
    problems: list[str] = []

    if not isinstance(args, dict):
        return [f"{path} must be an object, got {type(args).__name__}"]

    for key in schema.get("required", []):
        if key not in args:
            problems.append(f"{path}.{key} is required")

    props = schema.get("properties", {})
    for key, value in args.items():
        sub = props.get(key)
        if sub is None:
            if schema.get("additionalProperties") is False:
                problems.append(f"{path}.{key} is not a known argument")
            continue
        problems.extend(validate_value(sub, value, f"{path}.{key}"))

    return problems


def validate_value(schema: dict, value: Any, path: str) -> list[str]:
    problems: list[str] = []

    wanted = schema.get("type")
    if wanted and not _type_ok(value, wanted):
        return [f"{path} must be a {wanted}, got {type(value).__name__}"]

    if "enum" in schema and value not in schema["enum"]:
        allowed = ", ".join(repr(v) for v in schema["enum"])
        problems.append(f"{path} must be one of {allowed}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            problems.append(f"{path} must be >= {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            problems.append(f"{path} must be <= {schema['maximum']}")

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            problems.append(f"{path} must be at least {schema['minLength']} characters")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            problems.append(f"{path} must be at most {schema['maxLength']} characters")

    if isinstance(value, list) and isinstance(schema.get("items"), dict):
        for i, item in enumerate(value):
            problems.extend(validate_value(schema["items"], item, f"{path}[{i}]"))

    if isinstance(value, dict) and schema.get("properties"):
        problems.extend(validate_args(schema, value, path))

    return problems


# --------------------------------------------------------------------------
# the registry
# --------------------------------------------------------------------------

class ToolRegistry:
    """Holds the tools; validates and runs calls; never raises."""

    def __init__(self, tools: list[ToolSpec]):
        self._order: list[str] = []
        self._tools: dict[str, ToolSpec] = {}
        for t in tools:
            self.add(t)

    def add(self, tool: ToolSpec) -> None:
        if tool.name not in self._tools:
            self._order.append(tool.name)
        self._tools[tool.name] = tool

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def get(self, name: str) -> Optional[ToolSpec]:
        return self._tools.get(name)

    def schemas(self) -> list[dict]:
        """Exactly what the model is shown: name, description, parameters."""
        return [
            {
                "name": n,
                "description": self._tools[n].description,
                "parameters": self._tools[n].parameters,
            }
            for n in self._order
        ]

    def read_only(self, name: str) -> bool:
        tool = self._tools.get(name)
        return bool(tool and tool.read_only)

    def validate(self, name: str, args: dict) -> Optional[ToolResult]:
        """Return a failure result, or None when the call may run."""
        tool = self._tools.get(name)
        if tool is None:
            known = ", ".join(self._order) or "(none)"
            return ToolResult("unknown_tool", f"There is no tool called {name!r}. Available: {known}.")

        problems = validate_args(tool.parameters, args)
        if problems:
            return ToolResult(
                "invalid_args",
                f"The arguments for {name} did not match its schema: " + "; ".join(problems),
            )
        return None

    def execute(self, name: str, args: dict) -> ToolResult:
        failure = self.validate(name, args)
        if failure is not None:
            return failure

        tool = self._tools[name]
        try:
            value = tool.fn(**args)
        except Exception as exc:  # contained on purpose: a tool must not kill the loop
            return ToolResult("tool_error", f"{type(exc).__name__}: {exc}")
        return ToolResult("ok", "" if value is None else str(value))
