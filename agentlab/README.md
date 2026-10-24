# agentlab

A from-scratch agent harness. Reference implementation for the guide at
<https://jinbeiwang.github.io/agent.html>.

The premise: a model call is a list of messages in and a string out, and
everything people call "agent framework" is built on top of that one
primitive. So this package builds it on top, in the open, with no dependencies.

```bash
python -m pytest                 # 87 deterministic tests, no API key, ~1.3 s
python -m agentlab bench         # score the harness against the fixture gold
python -m agentlab show priority em-0018
python -m agentlab show bm25 "thistledown budget"
python -m agentlab show qa "What is the Thistledown budget?"
python -m agentlab show docs "meals reimbursement"
```

## What is here

| module | what it does |
|---|---|
| `lm.py` | `LM` (disk cache + cost ledger + spending cap), `ScriptedLM`, `FnLM`, a mock provider |
| `bm25.py` | inverted-index BM25, k1=1.5, b=0.75, Lucene's IDF |
| `pipelines.py` | priority, daily digest, multi-hop QA, document search/read |
| `registry.py` | tool specs, JSON-Schema validation, contained execution |
| `protocol.py` | the fenced-JSON tool-call format and a truncation-safe parser |
| `agent.py` | the loop, budgets, compaction, approval, steering, guardrails |
| `memory.py` | a JSONL store with source / confidence / sensitivity / id |
| `terminal.py` | allowlist, timeout, scrubbed environment, `jail()` reporting |
| `evaluate.py` | programmatic checks over a transcript, and a judge stand-in |

## The honest part

`mock.py` is **not** a language model. It pattern-matches the `TASK=` marker a
pipeline puts in its prompt and applies a crude heuristic. Every number it
produces measures this harness, not model quality: `bench` reports 20/25 on
priority and 3/6 on QA, and those are properties of `mock.py`.

To run against a real model, set `AGENTLAB_API_KEY` and `AGENTLAB_BASE_URL` and
pass `--model openai/gpt-class`. The provider is one function in `lm.py`; that
is deliberately the only place in the package that knows what an API is.
