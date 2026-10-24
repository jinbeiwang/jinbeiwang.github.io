"""The types that cross a boundary.

Two kinds live here, and the distinction matters when you read the code:

  · ``TypedDict`` (Email, SearchResult, DocWindow) is a plain dict with named
    keys. Read ``email["subject"]``, not ``email.subject``. They are dicts on
    purpose: they go straight into JSON fixtures and back.
  · ``dataclass`` (ToolSpec, ToolCall, ToolResult, ...) is an object with
    attributes, because these are built and passed around in code.

This mirrors ``cs329z_hw1/types.py`` from the course starter so that the
reference implementation and the handout describe the same shapes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal, Optional, TypedDict

Message = dict  # {"role": "system" | "user" | "assistant", "content": str}
LMCallable = Callable[[list[Message]], str]


class Email(TypedDict):
    id: str
    thread_id: str
    reply_to: Optional[str]
    to: list[str]
    date: str  # ISO 8601, UTC
    subject: str
    body: str
    # "from" cannot be declared as a field name (Python keyword); the dict
    # still carries it.


Status = Literal["ok", "unknown_tool", "invalid_args", "tool_error", "denied"]


@dataclass
class ToolSpec:
    """Everything the registry stores about one tool."""

    name: str
    description: str
    parameters: dict  # JSON Schema object
    fn: Callable[..., Any]
    read_only: bool = False


@dataclass
class ToolCall:
    name: str
    args: dict = field(default_factory=dict)


@dataclass
class ToolResult:
    status: Status
    content: str


@dataclass
class ParsedResponse:
    """What parse_response extracts from one model reply."""

    text: str
    tool_call: Optional[ToolCall] = None
    error: Optional[str] = None


# Why a call to the agent stopped.
#   done / max_turns / token_budget / malformed — the course's four reasons
#   stuck — the same call repeated past AgentConfig.repeat_limit
#
# "stuck" is an addition. The course's budgets bound how *much* work a send may
# do; none of them notices a loop that keeps doing the same thing within budget.
StopReason = Literal["done", "max_turns", "token_budget", "malformed", "stuck"]


@dataclass
class AgentResult:
    text: str
    status: StopReason
    transcript: list[dict]


@dataclass
class Approval:
    approved: bool
    reason: str = ""


@dataclass
class AgentConfig:
    max_turns: int = 20
    token_budget: int = 400_000
    context_budget: int = 16_000
    memory_dir: Optional[Path] = None
    mode: Literal["confirm", "auto"] = "auto"
    user: Any = None
    deny_rules: tuple[str, ...] = ()
    aux_lm: Any = None
    workspace: Optional[Path] = None
    terminal_timeout: float = 10.0
    # Stop a send that repeats one identical tool call this many times. 0 is off.
    repeat_limit: int = 0


class SearchResult(TypedDict):
    doc_id: str
    title: str
    snippet: str


class DocWindow(TypedDict):
    doc_id: str
    start_line: int
    end_line: int
    total_lines: int
    text: str
