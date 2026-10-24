"""The tokenizer BM25 must use.

Lowercase, split on anything that is not alphanumeric. That is it.

Why this and not a stemmer or a subword tokenizer: scores have to be
comparable across implementations, and a stemmer changes which documents
match, not just how they rank. Keeping the tokenizer trivial means a
hand-computed five-document example is a real test rather than a
compatibility test.

The consequence is that "emails" and "email" are different terms here. That
is a known recall cost, and it is the retriever design question the memo asks
about.
"""

from __future__ import annotations

import re

_SPLIT = re.compile(r"[^a-z0-9]+")


def tokenize(text: str) -> list[str]:
    """Split ``text`` into lowercase alphanumeric tokens."""
    return [t for t in _SPLIT.split(text.lower()) if t]
