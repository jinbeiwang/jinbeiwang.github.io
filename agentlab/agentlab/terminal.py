"""A terminal the model may use, with the limits written down.

``run_terminal`` is the only tool in the set with side effects, so it is the
one that needs a story about what it stops. Three layers, in the order they
apply:

  1. **A syntactically checked allowlist.** The command is split on pipes and
     separators; every program in it must be on the allowlist. Command
     substitution and here-documents are rejected outright, because both are
     ways to run something the allowlist never saw.
  2. **A timeout and a scrubbed environment.** The command does not inherit
     ``AGENTLAB_API_KEY``; a command that leaks the key is a command that can
     spend money.
  3. **An operating-system jail** — ``sandbox-exec`` on macOS, ``bwrap`` on
     Linux when installed. **On Windows there is none.** This is not a detail
     to skip: on Windows the allowlist, the timeout and the scrub are the only
     limits, and a ``python3`` command can read any file the account can.

``jail()`` reports which of the three situations you are in, because a limit
you believe in but do not have is worse than a limit you know is missing.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

ALLOWED = {
    "python3", "python", "grep", "egrep", "fgrep", "wc", "sort", "uniq", "head",
    "tail", "cut", "tr", "sed", "awk", "cat", "ls", "find", "echo", "printf",
    "basename", "dirname", "nl", "comm", "join", "paste", "xargs", "date",
}

#: written down so the refusal message can be specific rather than "no"
NEEDS_SHELL = {"bash", "sh", "zsh", "cmd", "powershell", "pwsh"}
FETCHERS = {"curl", "wget", "nc", "ssh", "scp", "ftp"}
DESTRUCTIVE = {"rm", "rmdir", "mv", "dd", "mkfs", "shred", "chmod", "chown"}


@dataclass
class TerminalResult:
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    timed_out: bool = False
    rejected: bool = False
    reason: str = ""

    @property
    def ok(self) -> bool:
        return not (self.rejected or self.timed_out) and self.exit_code == 0


def jail() -> str:
    """Which OS-level sandbox is active: 'sandbox-exec', 'bwrap', or 'none'."""
    if sys.platform == "darwin" and shutil.which("sandbox-exec"):
        return "sandbox-exec"
    if sys.platform.startswith("linux") and shutil.which("bwrap"):
        return "bwrap"
    return "none"


def check_command(cmd: str) -> Optional[str]:
    """Return a refusal reason, or None when the command may run."""
    if not cmd or not cmd.strip():
        return "the command was empty"

    if "<<" in cmd:
        return "here-documents (<<) are not allowed; write multi-line Python as python3 -c '...'"
    if "$(" in cmd or "`" in cmd:
        return "command substitution is not allowed"
    if ">" in cmd or "<" in cmd:
        return "redirection is not allowed; print what you need instead of writing files"

    # split into the programs that would actually run
    for segment in re.split(r"\||;|&&|\|\|", cmd):
        segment = segment.strip()
        if not segment:
            continue
        program = segment.split()[0]
        name = Path(program).name
        if name in NEEDS_SHELL:
            return f"{name} is not allowed: it would run arbitrary commands"
        if name in FETCHERS:
            return f"{name} is not allowed: network access is outside the sandbox"
        if name in DESTRUCTIVE:
            return f"{name} is not allowed: it changes files outside the workspace"
        if name not in ALLOWED:
            return f"{name} is not on the allowlist"
    return None


class FakeTerminal:
    """A terminal that returns scripted results. Deterministic tests use this.

    The alternative — running real commands in a test — makes the test depend
    on the machine's shell, which is exactly the dependency the sandbox's
    docstring warns about. The allowlist itself is still tested for real, by
    calling ``check_command`` directly.
    """

    def __init__(self, script: Optional[dict[str, TerminalResult]] = None, default: Optional[TerminalResult] = None):
        self.script = script or {}
        self.default = default or TerminalResult(stdout="", exit_code=0)
        self.commands: list[str] = []

    def run(self, cmd: str, *, workspace=None, timeout: float = 10.0) -> TerminalResult:
        self.commands.append(cmd)
        refusal = check_command(cmd)
        if refusal:
            return TerminalResult(rejected=True, reason=refusal, exit_code=126)
        for pattern, result in self.script.items():
            if re.search(pattern, cmd):
                return result
        return self.default


class LocalTerminal:
    """Really runs the command, after the checks. No OS jail on Windows."""

    def run(self, cmd: str, *, workspace=None, timeout: float = 10.0) -> TerminalResult:
        refusal = check_command(cmd)
        if refusal:
            return TerminalResult(rejected=True, reason=refusal, exit_code=126)

        cwd = Path(workspace) if workspace else Path.cwd()
        env = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": str(cwd),
            "LANG": "C.UTF-8",
        }
        try:
            proc = subprocess.run(
                cmd, shell=True, cwd=cwd, env=env, timeout=timeout,
                capture_output=True, text=True, errors="replace",
            )
            return TerminalResult(
                stdout=proc.stdout.replace("\r\n", "\n"),
                stderr=proc.stderr.replace("\r\n", "\n"),
                exit_code=proc.returncode,
            )
        except subprocess.TimeoutExpired as exc:
            return TerminalResult(
                stdout=(exc.stdout or "").replace("\r\n", "\n") if isinstance(exc.stdout, str) else "",
                stderr=(exc.stderr or "").replace("\r\n", "\n") if isinstance(exc.stderr, str) else "",
                exit_code=124, timed_out=True, reason=f"the command exceeded {timeout}s",
            )
