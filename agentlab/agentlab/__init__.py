"""agentlab — a from-scratch agent harness, built as the reference
implementation for the CS329Z guide on jinbeiwang.github.io.

The point of this package is that every layer is visible: a model call is a
list of messages in and a string out, tool calls are text we parse, the loop
is a while statement. Nothing here is delegated to a framework.

Modules:
    types        the dataclasses that cross every boundary
    tokens       the token counter (4 characters per token, like the course)
    tokenizer    the tokenizer BM25 must use
    lm           LM (cache + ledger + budget), ScriptedLM, MockProvider
    corpus       the fixture corpus: 6 documents, 42 emails, gold labels
    bm25         inverted-index BM25, built from scratch
    pipelines    Part 1: priority, digest, multi-hop QA, doc retrieval
    registry     tool specs, schema validation, execution
    protocol     the text tool-call format and its parser
    terminal     a sandboxed terminal (allowlist, timeout, workspace)
    memory       the persistent memory store
    agent        the session: loop, compaction, approval, steering, guardrails
    evaluate     personas, programmatic checks, the judge
    cli          `python -m agentlab ...`
"""

__version__ = "0.1.0"
