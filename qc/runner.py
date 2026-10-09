"""Score all records and write a CSV. Does NOT modify the database.

Usage: python -m qc.runner [--limit N] [--out out/qc_results.csv]
"""
import argparse
import csv
import os
import pickle
import re
from collections import Counter

from qc.gaps import waived_by_source
from qc.checks import accuracy, completeness, consistency, credibility, relevance
from qc.fetch import fetch_records
from qc.scoring import decide


def norm_title(t: str) -> str:
    return re.sub(r"\W+", " ", (t or "").lower()).strip()


def load_records(args):
    """--cached reuses out/records_cache.pkl (the DB fetch is slow); otherwise fetch and refresh the cache."""
    path = "out/records_cache.pkl"
    if args.cached and not args.limit and os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    records = fetch_records(args.limit)
    if not args.limit:
        with open(path, "wb") as f:
            pickle.dump(records, f)
    return records


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--cached", action="store_true", help="reuse the cached DB fetch (out/records_cache.pkl)")
    ap.add_argument("--no-relevance", action="store_true", help="skip the (slow) embedding check")
    ap.add_argument("--out", default="out/qc_results.csv")
    args = ap.parse_args()

    records = load_records(args)
    titles = Counter(norm_title(r.title) for r in records)
    urls = Counter(r.url for r in records if r.url)
    waived = waived_by_source(records)
    for src, w in sorted(waived.items(), key=lambda x: x[0] or ""):
        if w:
            print(f"  waived for {src}: {', '.join(sorted(w))}")
    print(f"Scoring {len(records)} records")

    rel = {} if args.no_relevance else relevance.score_all(records)
    rows, summary = [], Counter()
    for r in records:
        res = [
            completeness.check(r, waived[r.source]),
            consistency.check(r, titles[norm_title(r.title)] > 1, bool(r.url) and urls[r.url] > 1),
            credibility.check(r, waived[r.source]),
        ]
        if r.id in rel:
            res.append(rel[r.id])
        acc = accuracy.check(r)
        if acc:
            res.append(acc)
        overall, decision = decide(res)
        summary[decision] += 1
        row = {"id": r.id, "identifier": r.identifier, "title": r.title[:120], "source": r.source,
               "resource_type": r.resource_type, "current_status": r.approval_status,
               "overall": round(overall, 3), "decision": decision}
        for x in res:
            row[x.dimension] = round(x.score, 3) if x.applies else ""
        if r.id in rel:
            row["rel_sim"] = round(rel[r.id].sim, 3); row["kw_hits"] = rel[r.id].hits
        row["waived"] = ";".join(sorted(waived[r.source]))
        row["flags"] = ";".join(f for x in res for f in x.flags + x.major)
        row["major"] = ";".join(f for x in res for f in x.major)
        rows.append(row)

    fields = ["id", "identifier", "title", "source", "resource_type", "current_status", "overall", "decision",
              "completeness", "consistency", "credibility", "relevance", "accuracy",
              "rel_sim", "kw_hits", "waived", "flags", "major"]
    tmp = args.out + ".tmp"          # write to a temp file so a crash never destroys the previous results
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, restval="", extrasaction="raise")
        w.writeheader(); w.writerows(rows)
    os.replace(tmp, args.out)

    print(dict(summary))
    flag_counts = Counter(fl for r in rows for fl in r["flags"].split(";") if fl)
    for k, v in flag_counts.most_common():
        print(f"  {k}: {v}")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
