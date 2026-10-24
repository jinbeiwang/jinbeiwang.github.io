"""Shared fixtures: two small tools and a helper to read a transcript."""

from __future__ import annotations

import pytest

from agentlab.types import ToolSpec


def echo_spec() -> ToolSpec:
    return ToolSpec(
        name="echo",
        description="Echo the text back.",
        parameters={
            "type": "object",
            "properties": {"text": {"type": "string", "minLength": 1}},
            "required": ["text"],
            "additionalProperties": False,
        },
        fn=lambda text: text,
        read_only=True,
    )


def big_spec(size: int = 2000) -> ToolSpec:
    return ToolSpec(
        name="big",
        description="Return a large blob, to exercise compaction.",
        parameters={
            "type": "object",
            "properties": {"n": {"type": "integer", "minimum": 1}},
            "required": [],
            "additionalProperties": False,
        },
        fn=lambda n=1: "x" * size,
        read_only=True,
    )


def write_spec() -> ToolSpec:
    """A side-effecting tool: it is the one approval has to gate."""
    calls: list[str] = []

    def run(path: str) -> str:
        calls.append(path)
        return f"wrote {path}"

    spec = ToolSpec(
        name="write_file",
        description="Write a file. This one has side effects.",
        parameters={
            "type": "object",
            "properties": {"path": {"type": "string", "minLength": 1}},
            "required": ["path"],
            "additionalProperties": False,
        },
        fn=run,
        read_only=False,
    )
    spec.calls = calls  # type: ignore[attr-defined]
    return spec


@pytest.fixture()
def tools():
    return [echo_spec(), big_spec(), write_spec()]


def events(transcript: list[dict], kind: str) -> list[dict]:
    return [e for e in transcript if e["type"] == kind]
