"""The model boundary: one primitive, plus everything the harness needs
around it — a disk cache, a cost ledger, a spending cap, and stand-ins that
let the whole system run with no API key.

The interface is deliberately poor: ``lm(messages) -> str``. No tool calling,
no JSON mode, no streaming. Everything above this line — how tools are
described, how calls are parsed, how results are fed back — has to be built,
and that is the point of the assignment.

Three implementations share the signature:

  ``LM``          cached, metered, budgeted wrapper around a provider
  ``ScriptedLM``  replays a fixed list of replies; the deterministic tests' model
  ``mock_provider`` a crude rule-based stand-in so that ``python -m agentlab``
                 works offline. It is NOT a language model: its scores measure
                 plumbing, never model quality. Every page that reports a number
                 from it says so.
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from .tokens import count_tokens

Messages = list[dict]
Provider = Callable[[Messages, int], str]


class BudgetExceeded(RuntimeError):
    """The spending cap was reached; no paid call was made."""


class OutputTruncated(RuntimeError):
    """The model hit max_tokens. ``.text`` is what it managed to write."""

    def __init__(self, text: str = ""):
        super().__init__("model output was truncated at max_tokens")
        self.text = text


class ScriptExhausted(RuntimeError):
    """The agent asked for more model calls than the script contains."""


# --------------------------------------------------------------------------
# the cache key
# --------------------------------------------------------------------------

def cache_key(model: str, messages: Messages, max_tokens: int, salt: str) -> str:
    """A key over everything that can change a reply.

    Note what is *not* in here: the tag, the temperature (this API has none),
    and the wall clock. Two calls with the same model, the same messages and
    the same cap must return the same text, or the cache is lying.
    """
    blob = json.dumps(
        {"model": model, "max_tokens": max_tokens, "salt": salt, "messages": messages},
        ensure_ascii=False,
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


@dataclass
class LedgerEntry:
    model: str
    tag: str
    prompt_tokens: int
    completion_tokens: int
    usd: float
    cached: bool = False


class LM:
    """A cached, metered, budgeted model.

    Prices are illustrative (per million tokens) and only exist so the ledger
    can show a number; the point of the budget check is to stop a runaway loop,
    not to predict an invoice.
    """

    PRICES = {  # model: (usd per 1M input, usd per 1M output)
        "mock/agent": (0.0, 0.0),
        "mock/judge": (0.0, 0.0),
        "openai/gpt-class": (2.5, 10.0),
        "openai/mini-class": (0.15, 0.60),
    }

    def __init__(
        self,
        model: str = "mock/agent",
        *,
        provider: Optional[Provider] = None,
        cache_dir: Optional[Path] = None,
        budget_usd: Optional[float] = None,
        max_tokens: int = 1200,
        tag: str = "untagged",
        salt: str = "",
    ):
        self.model = model
        self.provider = provider or get_provider(model)
        self.cache_dir = Path(cache_dir or os.environ.get("AGENTLAB_CACHE", ".lm_cache"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.budget_usd = budget_usd if budget_usd is not None else _env_float("AGENTLAB_BUDGET_USD")
        self.max_tokens = max_tokens
        self.tag = tag
        self.salt = salt
        self._lock = threading.Lock()
        self.spent_usd = 0.0

    # -- the call ---------------------------------------------------------
    def __call__(self, messages: Messages, *, tag: Optional[str] = None,
                 max_tokens: Optional[int] = None) -> str:
        cap = max_tokens if max_tokens is not None else self.max_tokens
        use_tag = tag or self.tag
        key = cache_key(self.model, messages, cap, self.salt)
        path = self.cache_dir / f"{key}.txt"

        if path.exists():
            text = path.read_text(encoding="utf-8")
            self._append_ledger(LedgerEntry(self.model, use_tag, count_tokens(_join(messages)),
                                            count_tokens(text), 0.0, cached=True))
            return text

        # budget is checked *before* the paid call, so hitting the cap costs nothing
        if self.budget_usd is not None and self.spent_usd >= self.budget_usd:
            raise BudgetExceeded(
                f"spent ${self.spent_usd:.4f} of a ${self.budget_usd:.2f} cap; cached replies still work"
            )

        text = self.provider(messages, cap)

        usd = self._price(_join(messages), text)
        path.write_text(text, encoding="utf-8")
        self._append_ledger(LedgerEntry(self.model, use_tag, count_tokens(_join(messages)),
                                        count_tokens(text), usd, cached=False))
        with self._lock:
            self.spent_usd += usd
        return text

    # -- accounting -------------------------------------------------------
    def _price(self, prompt: str, completion: str) -> float:
        pin, pout = self.PRICES.get(self.model, (0.0, 0.0))
        return (count_tokens(prompt) * pin + count_tokens(completion) * pout) / 1_000_000

    def _append_ledger(self, e: LedgerEntry) -> None:
        with self._lock:
            with (self.cache_dir / "ledger.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(e.__dict__, ensure_ascii=False) + "\n")

    def totals(self) -> dict:
        """Spend and call counts by model and by tag, from the ledger."""
        out: dict = {"by_model": {}, "by_tag": {}, "calls": 0, "cached": 0}
        ledger = self.cache_dir / "ledger.jsonl"
        if not ledger.exists():
            return out
        for line in ledger.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            out["calls"] += 1
            out["cached"] += 1 if e["cached"] else 0
            for bucket, key in ((out["by_model"], e["model"]), (out["by_tag"], e["tag"])):
                b = bucket.setdefault(key, {"usd": 0.0, "calls": 0, "tokens": 0})
                b["usd"] += e["usd"]
                b["calls"] += 1
                b["tokens"] += e["prompt_tokens"] + e["completion_tokens"]
        return out


def _join(messages: Messages) -> str:
    return "\n".join(str(m.get("content", "")) for m in messages)


def _env_float(name: str) -> Optional[float]:
    v = os.environ.get(name)
    try:
        return float(v) if v else None
    except ValueError:
        return None


# --------------------------------------------------------------------------
# providers
# --------------------------------------------------------------------------

def mock_provider(model: str = "mock/agent") -> Provider:
    """A deterministic stand-in so the package runs with no key.

    It does not reason. It pattern-matches the machine-readable markers the
    pipelines put in their prompts (``TASK=priority`` and friends) and applies
    a crude heuristic. Its purpose is to exercise the *harness* offline; any
    score it produces is a property of this function, not of a model.
    """
    from . import mock as mock_mod  # local import: keeps this module importable alone

    def call(messages: Messages, max_tokens: int) -> str:
        return mock_mod.respond(messages)

    return call


def openai_compatible_provider(model: str, base_url: Optional[str] = None,
                               api_key: Optional[str] = None) -> Provider:
    """A real provider over the OpenAI-compatible /chat/completions shape.

    Not exercised by the test suite (it needs a key and a network). It is here
    so that switching from the stand-in to a real model is a one-line change,
    and so the boundary the assignment draws is visible: this function is the
    *only* place in the package that knows what an API looks like.
    """
    import urllib.request

    url = (base_url or os.environ.get("AGENTLAB_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
    key = api_key or os.environ.get("AGENTLAB_API_KEY", "")

    def call(messages: Messages, max_tokens: int) -> str:
        body = json.dumps({"model": model, "messages": messages, "max_tokens": max_tokens}).encode()
        req = urllib.request.Request(
            f"{url}/chat/completions", data=body,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        )
        with urllib.request.urlopen(req, timeout=120) as r:
            payload = json.loads(r.read())
        choice = payload["choices"][0]
        if choice.get("finish_reason") == "length":
            raise OutputTruncated(choice["message"].get("content", ""))
        return choice["message"]["content"]

    return call


def get_provider(model: str) -> Provider:
    if model.startswith("mock/"):
        return mock_provider(model)
    return openai_compatible_provider(model)


# --------------------------------------------------------------------------
# the scripted model
# --------------------------------------------------------------------------

class ScriptedLM:
    """Replays a fixed list of replies, one per call.

    A scripted entry is either a string (the reply as-is) or a dict
    ``{"name": ..., "arguments": {...}}``, which is turned into text with the
    protocol formatter — so a deterministic test can script a tool call without
    knowing which format the implementation chose.

    The last entry may be ``{"repeat": "..."}`` to answer every remaining call
    with the same text, which is how "the model never stops asking" is tested.
    """

    def __init__(self, replies: list, *, formatter=None):
        self._replies = list(replies)
        self._i = 0
        self._formatter = formatter
        self.calls: list[Messages] = []

    def __call__(self, messages: Messages, **kwargs) -> str:
        self.calls.append([dict(m) for m in messages])
        if self._i >= len(self._replies):
            raise ScriptExhausted(
                f"the agent made model call #{self._i + 1}; the script has {len(self._replies)} replies"
            )
        item = self._replies[self._i]
        self._i += 1

        if isinstance(item, dict) and "repeat" in item:
            self._i -= 1  # stay on this entry
            return item["repeat"]
        if isinstance(item, dict):
            from .protocol import format_tool_call
            from .types import ToolCall
            fmt = self._formatter or format_tool_call
            return fmt(item.get("text", ""), ToolCall(item["name"], item.get("arguments", {})))
        return str(item)

    @property
    def remaining(self) -> int:
        return max(0, len(self._replies) - self._i)


# --------------------------------------------------------------------------
# a reply function as a model
# --------------------------------------------------------------------------

class FnLM:
    """A model whose reply is computed from the messages.

    ``ScriptedLM`` is order-dependent, which is wrong whenever the harness makes
    calls concurrently — the daily digest classifies a day's email in a thread
    pool, and which thread gets reply #3 is not defined. ``FnLM`` reads the
    prompt instead, so the label lands on the email it belongs to no matter
    which order the threads run in.
    """

    def __init__(self, fn, *, record: bool = False):
        self._fn = fn
        self.calls: list[Messages] = []
        self._record = record

    def __call__(self, messages: Messages, **kwargs) -> str:
        if self._record:
            self.calls.append([dict(m) for m in messages])
        return self._fn(messages)


# --------------------------------------------------------------------------
# a second model for auxiliary calls
# --------------------------------------------------------------------------

class AuxLM:
    """Wraps a model so auxiliary calls never consume an agent turn.

    ``AgentConfig.aux_lm`` exists for one reason: summaries, and the model
    calls inside Part 1 tools, must not eat the agent's own turn budget. The
    tests pass a separate scripted model here precisely so a compaction
    summary cannot silently swallow the reply the test expects next.
    """

    def __init__(self, lm):
        self._lm = lm
        self.calls = 0

    def __call__(self, messages: Messages, **kw) -> str:
        self.calls += 1
        tag = kw.pop("tag", "aux")
        return self._lm(messages, tag=tag, **kw)
