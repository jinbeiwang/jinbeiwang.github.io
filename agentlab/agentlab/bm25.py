"""BM25 over an inverted index, built from scratch.

The score of a document for a query is the sum, over the query's distinct
terms, of

    IDF(t) * f(t,d) * (k1 + 1) / (f(t,d) + k1 * (1 - b + b * |d| / avgdl))

with

    IDF(t) = ln((N - n_t + 0.5) / (n_t + 0.5) + 1)

and k1 = 1.5, b = 0.75. The ``+1`` inside the logarithm is what Lucene does;
the original Robertson paper omits it, and then a term appearing in more than
half the corpus gets a *negative* weight and actively pushes documents down.
Using the Lucene variant keeps every weight non-negative.

Two properties are load-bearing and are what the tests check:

  · **Build is one pass.** Tokenise each document once, accumulate postings.
  · **Search touches only the query's postings.** The whole point of the
    inverted index is that a rare query costs a handful of dictionary lookups,
    not a scan of the corpus. A 2 ms budget for a term in 3 of 200,000
    documents fails any implementation that iterates over documents.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .tokenizer import tokenize

K1 = 1.5
B = 0.75


@dataclass
class Index:
    """An inverted index plus the statistics BM25 needs at query time."""

    postings: dict[str, dict[int, int]] = field(default_factory=dict)  # term -> {doc: tf}
    lengths: list[int] = field(default_factory=list)
    idf: dict[str, float] = field(default_factory=dict)

    @property
    def n_docs(self) -> int:
        return len(self.lengths)

    @property
    def avgdl(self) -> float:
        return (sum(self.lengths) / len(self.lengths)) if self.lengths else 0.0

    def documents_containing(self, term: str) -> int:
        return len(self.postings.get(term, ()))


def build(docs: list[str]) -> Index:
    """Index a corpus in a single pass. A document's id is its list index."""
    index = Index()
    postings = index.postings
    lengths = index.lengths

    for doc_id, text in enumerate(docs):
        tokens = tokenize(text)
        lengths.append(len(tokens))
        for tok in tokens:
            row = postings.get(tok)
            if row is None:
                postings[tok] = {doc_id: 1}
            else:
                row[doc_id] = row.get(doc_id, 0) + 1

    n = len(lengths)
    for term, row in postings.items():
        nt = len(row)
        index.idf[term] = math.log((n - nt + 0.5) / (nt + 0.5) + 1.0)
    return index


def scores(index: Index, query: str) -> dict[int, float]:
    """Score every document that shares at least one term with the query."""
    terms = set(tokenize(query))  # distinct: a repeated term is counted once
    if not terms or not index.lengths:
        return {}

    avgdl = index.avgdl or 1.0
    out: dict[int, float] = {}
    for term in terms:
        row = index.postings.get(term)
        if not row:
            continue
        idf = index.idf[term]
        for doc_id, tf in row.items():
            dl = index.lengths[doc_id]
            denom = tf + K1 * (1.0 - B + B * dl / avgdl)
            out[doc_id] = out.get(doc_id, 0.0) + idf * tf * (K1 + 1.0) / denom
    return out


def search(index: Index, query: str, k: int = 10) -> list[tuple[int, float]]:
    """Top-k (doc_id, score), best first, ties broken by lower doc_id."""
    ranked = sorted(scores(index, query).items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked[:k]
