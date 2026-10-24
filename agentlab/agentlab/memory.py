"""Persistent memory: a JSON-lines store with the metadata that makes it
safe to keep.

The course asks for two tools, ``remember`` and ``recall``, and one policy
decision: what a new session starts with. This implementation goes one step
further, following the self-study plan's Week 10 rather than the handout,
because the extra fields are what turn a scratchpad into something you would
ship:

  · ``source`` — "user" (stated), "tool" (derived from a tool result), or
    "inferred". Only the first two are asserted as fact when they are recalled;
    an inferred fact is labelled as a guess.
  · ``sensitive`` — facts marked sensitive are never loaded into the system
    prompt, only returned by an explicit ``recall``.
  · ``id`` — so a user can delete one.

What a new session starts with: the newest few *non-sensitive* user-stated
facts, plus a one-line hint that a store exists and how to search it. That is
the middle ground between "load everything" (safe, but it eats the context
budget) and "load nothing" (cheap, but the model never knows there is anything
to recall).
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

from .tokenizer import tokenize

PROMPT_FACTS = 5
STOP = {"the", "a", "an", "is", "was", "of", "to", "and", "i", "my", "me", "in", "for"}


@dataclass
class Fact:
    text: str
    source: str = "user"          # user | tool | inferred
    confidence: str = "stated"    # stated | derived | guess
    sensitive: bool = False
    created: float = field(default_factory=time.time)
    id: str = field(default_factory=lambda: "f-" + uuid.uuid4().hex[:8])

    def line(self) -> str:
        tag = "" if self.source == "user" else f" [{self.confidence}]"
        return f"{self.text}{tag}"


class MemoryStore:
    """One directory per memory. Two sessions share a memory by sharing a dir."""

    def __init__(self, directory: Path | str):
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path = self.dir / "facts.jsonl"

    # -- write ------------------------------------------------------------
    def remember(self, text: str, *, source: str = "user", confidence: str = "stated",
                 sensitive: bool = False) -> Fact:
        fact = Fact(text=text.strip(), source=source, confidence=confidence, sensitive=sensitive)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(fact), ensure_ascii=False) + "\n")
        return fact

    def forget(self, fact_id: str) -> bool:
        facts = self.all()
        kept = [f for f in facts if f.id != fact_id]
        if len(kept) == len(facts):
            return False
        self._rewrite(kept)
        return True

    def _rewrite(self, facts: list[Fact]) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            for fact in facts:
                f.write(json.dumps(asdict(fact), ensure_ascii=False) + "\n")

    # -- read -------------------------------------------------------------
    def all(self) -> list[Fact]:
        if not self.path.exists():
            return []
        out = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    out.append(Fact(**json.loads(line)))
                except (json.JSONDecodeError, TypeError):
                    continue
        return out

    def recall(self, query: str, k: int = 5) -> list[Fact]:
        """Rank facts by term overlap. No model, no embeddings, on purpose."""
        terms = set(tokenize(query)) - STOP
        if not terms:
            return self.all()[-k:]
        scored = []
        for fact in self.all():
            hits = len(terms & set(tokenize(fact.text)))
            if hits:
                scored.append((hits, fact.created, fact))
        scored.sort(key=lambda t: (-t[0], -t[1]))
        return [f for _h, _c, f in scored[:k]]

    def prompt_block(self) -> str:
        """What a new session loads before the first message."""
        facts = [f for f in self.all() if not f.sensitive and f.source == "user"]
        if not facts:
            return ""
        recent = facts[-PROMPT_FACTS:]
        lines = ["What you remember about this user from earlier sessions:"]
        lines += [f"- {f.text}" for f in recent]
        if len(facts) > len(recent):
            lines.append(f"- ({len(facts) - len(recent)} older facts are in the store; use recall to search them)")
        return "\n".join(lines)
