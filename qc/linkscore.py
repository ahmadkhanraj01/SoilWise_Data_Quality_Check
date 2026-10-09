"""Per-record link evidence from the link-check CSVs (no network, no DB).

Only definitive answers count: `ok` (works) and `broken` (404/410/unregistered DOI). Timeouts, DNS/connect
errors, restricted (401/403/429) and invalid URLs are *unknown*, because one machine cannot tell a dead host
from one that blocks it. Sources, in order of precedence: decoded sample > main run.
"""
import csv
import os
from collections import defaultdict

MAIN = "out/link_results_clean.csv"
DECODED = "out/link_results_decoded.csv"


def _rows(path):
    if not os.path.exists(path):
        return
    with open(path, newline="", encoding="utf-8") as f:
        yield from csv.DictReader(f)


def load() -> dict[str, tuple[int, int]]:
    """record_id -> (ok_count, broken_count). Results were stored against the first record using each URL,
    so records sharing a URL with an earlier record are not covered."""
    per = defaultdict(lambda: [0, 0])
    decoded_ids = set()
    for row in _rows(DECODED):
        rid, res = (row.get("record_id") or "").strip(), (row.get("result") or "").strip()
        if res in ("ok", "broken"):
            per[rid][0 if res == "ok" else 1] += 1
            decoded_ids.add(rid)
    for row in _rows(MAIN):
        rid, res = (row.get("record_id") or "").strip(), (row.get("result") or "").strip()
        if rid in decoded_ids:
            continue
        if res in ("ok", "broken"):
            per[rid][0 if res == "ok" else 1] += 1
    return {k: (v[0], v[1]) for k, v in per.items()}
