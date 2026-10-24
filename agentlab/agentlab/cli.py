"""``python -m agentlab ...`` — look at what the pipelines actually produce.

Reading a score tells you a number. Reading the output tells you why. These
commands exist so that the second thing is one line away, and so the memo's
questions ("run a few queries of your own — what did the ranking get wrong?")
have something to run.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import bm25, pipelines
from .corpus import PRIORITY_GOLD, QA_GOLD, emails_on, get_email, load_docs, load_emails
from .lm import LM


def _lm(args) -> LM:
    return LM(args.model, cache_dir=Path(args.cache), budget_usd=args.budget)


def cmd_priority(args) -> None:
    email = get_email(args.email_id)
    if email is None:
        sys.exit(f"no email {args.email_id!r}")
    lm = _lm(args)
    out = pipelines.run_priority(email, lm)
    gold = PRIORITY_GOLD.get(args.email_id, "?")
    print(f"{args.email_id}  {email['date'][:10]}  {email.get('subject') or '(no subject)'}")
    print(f"  label   {out['category']}   (gold: {gold})")
    print(f"  reason  {out['reason']}")


def cmd_digest(args) -> None:
    day = emails_on(args.date)
    if args.limit:
        day = day[: args.limit]
    lm = _lm(args)
    text = pipelines.run_daily_digest(day, lm)
    print(f"{args.date}: {len(day)} emails, {len(text.split())} words\n")
    print(text)
    if args.labels:
        print()
        for e in day:
            label = pipelines.run_priority(e, lm)["category"]
            print(f"  [{label:6}] {e['id']}  {e.get('subject') or '(no subject)'}")


def cmd_bm25(args) -> None:
    emails = load_emails()
    index = pipelines.build_email_index(emails)
    hits = bm25.search(index, args.query, args.k)
    if not hits:
        print("no match")
        return
    for doc_id, score in hits:
        e = emails[doc_id]
        print(f"{score:8.3f}  {e['id']}  {e.get('subject') or '(no subject)'}")


def cmd_qa(args) -> None:
    emails = load_emails()
    index = pipelines.build_email_index(emails)
    search = pipelines.make_search(emails, index)
    out = pipelines.run_email_qa(args.question, search, _lm(args))
    print(f"answer   {out['answer']}")
    print(f"support  {', '.join(out['support']) or '—'}")
    print(f"searches {out['searches']}")


def cmd_docs(args) -> None:
    docs = load_docs()
    index = pipelines.build_doc_index(docs)
    for r in pipelines.search_docs(docs, index, args.query, args.k):
        print(f"{r['doc_id']} — {r['title']}\n  {r['snippet']}")


def cmd_memory(args) -> None:
    from .memory import MemoryStore

    store = MemoryStore(args.dir)
    facts = store.all()
    if not facts:
        print(f"{args.dir}: empty")
        return
    for f in facts:
        print(f"- {f.line()}  ({f.id}, {f.source})")


def cmd_bench(args) -> None:
    """The fixture benchmark: what this harness scores with the stand-in model.

    Every number printed here is a property of ``mock.py``, not of a language
    model. It is printed so that a reader can see the harness working end to
    end, and so that a difference between two runs is attributable to code
    rather than to a model's mood.
    """
    lm = _lm(args)

    print("priority (25 emails, gold labels from the corpus)")
    ok = 0
    unknown = 0
    for e in load_emails():
        out = pipelines.run_priority(e, lm)
        gold = PRIORITY_GOLD[e["id"]]
        ok += out["category"] == gold
        unknown += out["category"] == "unknown"
    total = len(PRIORITY_GOLD)
    print(f"  agree {ok}/{total} = {ok / total:.0%}   unknown {unknown}")

    print("\nemail QA (6 questions, exact substring match on accepted answers)")
    emails = load_emails()
    index = pipelines.build_email_index(emails)
    search = pipelines.make_search(emails, index)
    hits = 0
    for q in QA_GOLD:
        out = pipelines.run_email_qa(q["question"], search, lm)
        answer = (out["answer"] or "").lower()
        good = any(a.lower() in answer for a in q["answers"])
        hits += good
        print(f"  {'ok ' if good else 'ERR'} [{q['hops']}hop] {q['question'][:58]:58} → {out['answer']}")
    print(f"  correct {hits}/{len(QA_GOLD)}")

    totals = lm.totals()
    print(f"\ncalls {totals['calls']} (cached {totals['cached']})  spend ${sum(v['usd'] for v in totals['by_model'].values()):.4f}")


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="agentlab", description="the reference harness")
    p.add_argument("--model", default="mock/agent")
    p.add_argument("--cache", default=".lm_cache")
    p.add_argument("--budget", type=float, default=None)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("show", help="run one pipeline and print the result")
    show = s.add_subparsers(dest="what", required=True)

    sp = show.add_parser("priority")
    sp.add_argument("email_id")
    sp.set_defaults(fn=cmd_priority)

    sd = show.add_parser("digest")
    sd.add_argument("date")
    sd.add_argument("--limit", type=int, default=0)
    sd.add_argument("--labels", action="store_true")
    sd.set_defaults(fn=cmd_digest)

    sb = show.add_parser("bm25")
    sb.add_argument("query")
    sb.add_argument("-k", type=int, default=5)
    sb.set_defaults(fn=cmd_bm25)

    sq = show.add_parser("qa")
    sq.add_argument("question")
    sq.set_defaults(fn=cmd_qa)

    sc = show.add_parser("docs")
    sc.add_argument("query")
    sc.add_argument("-k", type=int, default=5)
    sc.set_defaults(fn=cmd_docs)

    sm = show.add_parser("memory")
    sm.add_argument("dir")
    sm.set_defaults(fn=cmd_memory)

    b = sub.add_parser("bench", help="score the harness against the fixture gold")
    b.set_defaults(fn=cmd_bench)

    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
