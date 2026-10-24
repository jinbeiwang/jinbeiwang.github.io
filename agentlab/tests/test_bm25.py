"""BM25: one hand-computed case, then the properties that make it an index."""

from __future__ import annotations

import math
import time

from agentlab import bm25
from agentlab.corpus import load_emails
from agentlab.pipelines import build_email_index


def test_hand_computed_scores():
    """Three documents, one query term, arithmetic done on paper.

    N=3, avgdl=(2+3+1)/3=2. Term "a" is in 2 documents, so
    IDF = ln((3-2+0.5)/(2+0.5)+1) = ln(1.6).

    d0 ("a b")   : tf=1, dl=2 -> tf*(k1+1) = 2.5 ; denom = 1 + 1.5*(0.25+0.75*1) = 2.5
    d1 ("a a b"): tf=2, dl=3 -> tf*(k1+1) = 5.0 ; denom = 2 + 1.5*(0.25+0.75*1.5) = 4.0625
    """
    index = bm25.build(["a b", "a a b", "c"])
    got = bm25.scores(index, "a")
    idf = math.log(1.6)

    assert set(got) == {0, 1}
    assert math.isclose(got[0], idf * 2.5 / 2.5, rel_tol=1e-12)
    assert math.isclose(got[1], idf * 2 * 2.5 / 4.0625, rel_tol=1e-12)
    assert got[1] > got[0], "more occurrences must score higher on equal-length documents"


def test_no_shared_term_returns_nothing():
    index = bm25.build(["alpha beta", "gamma delta"])
    assert bm25.search(index, "epsilon", 10) == []


def test_repeated_query_term_counts_once():
    index = bm25.build(["alpha beta", "gamma"])
    once = bm25.scores(index, "alpha")
    thrice = bm25.scores(index, "alpha alpha alpha")
    assert once == thrice


def test_ties_broken_by_lower_doc_id():
    index = bm25.build(["same", "same", "sane"])
    hits = bm25.search(index, "same", 2)
    assert [h[0] for h in hits] == [0, 1]
    assert math.isclose(hits[0][1], hits[1][1])


def test_k_larger_than_candidates():
    index = bm25.build(["a", "b"])
    assert len(bm25.search(index, "a", 50)) == 1


def test_index_builds_fast_enough():
    emails = load_emails()
    started = time.perf_counter()
    index = build_email_index(emails)
    elapsed = time.perf_counter() - started
    assert index.n_docs == len(emails)
    assert elapsed < 1.0, f"25 documents should index in well under a second, took {elapsed:.3f}s"


def test_query_is_sublinear():
    """A rare term must not require touching every document."""
    docs = [f"filler words number {i} here" for i in range(5000)]
    docs.append("unique needle token")
    index = bm25.build(docs)

    started = time.perf_counter()
    for _ in range(200):
        bm25.search(index, "needle", 10)
    per_query = (time.perf_counter() - started) / 200
    assert per_query < 0.002, f"a rare-term query took {per_query * 1000:.2f} ms"
