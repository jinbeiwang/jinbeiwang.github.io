"""Token counting.

The course counts four characters per token and says so in the handout, which
is a deliberate simplification: it is stable across models, needs no
tokenizer, and is within about 20% of a real BPE tokenizer on English prose.
Every budget in the assignment — 16,000 for a call, 400,000 for a send —
is expressed in these units.

Do not "improve" this to a real tokenizer unless you also change every
threshold: the numbers only mean something relative to the counter.
"""

from __future__ import annotations

CHARS_PER_TOKEN = 4


def count_tokens(text: str) -> int:
    """Tokens in a string, at four characters per token."""
    if not text:
        return 0
    return (len(text) + CHARS_PER_TOKEN - 1) // CHARS_PER_TOKEN


def count_message_tokens(messages: list[dict]) -> int:
    """Tokens in a whole message list, the way a provider would bill it.

    Each message costs its content plus a small per-message overhead for the
    role and the delimiters. The overhead matters: a conversation with
    hundreds of tiny tool results is not free just because the text is short.
    """
    total = 0
    for m in messages:
        total += count_tokens(str(m.get("content", "")))
        total += 4  # role + framing, the usual per-message overhead
    return total
