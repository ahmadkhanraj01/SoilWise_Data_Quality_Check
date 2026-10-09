"""Retry URLs that timed out, with a longer timeout, to separate slow servers from dead ones.

Inputs: out/link_results_clean.csv and out/link_results_decoded.csv (rows with result == timeout).
Output: out/link_results_retry.csv. At most --max-per-host URLs per host are retried, because a slow host would
otherwise take hours (30 s each, 2 at a time); the per-host verdict is what matters, not every URL.

Usage: python -m qc.linkcheck_retry [--timeout 30] [--max-per-host 25] [--concurrency 20] [--per-host 2]
"""
import argparse
import asyncio
import csv
import os
import random
from collections import Counter, defaultdict
from urllib.parse import urlparse

import httpx

from qc.linkcheck import UA, check

OUT = "out/link_results_retry.csv"


def load(max_per_host: int, seed: int):
    items = []
    for path, url_col in (("out/link_results_clean.csv", "url"), ("out/link_results_decoded.csv", "decoded_url")):
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r["result"] == "timeout":
                    items.append((r[url_col], r["record_id"], path.split("/")[-1]))
    by_host = defaultdict(list)
    for it in items:
        by_host[urlparse(it[0]).netloc].append(it)
    rng = random.Random(seed)
    picked = []
    for h, v in by_host.items():
        rng.shuffle(v)
        picked += v[:max_per_host]
    return items, picked, by_host


async def run(todo, concurrency, per_host, timeout):
    host_sem = defaultdict(lambda: asyncio.Semaphore(per_host))
    global_sem = asyncio.Semaphore(concurrency)
    new_file = not os.path.exists(OUT)
    async with httpx.AsyncClient(headers={"User-Agent": UA}, follow_redirects=True,
                                 limits=httpx.Limits(max_connections=concurrency * 2)) as client:
        with open(OUT, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new_file:
                w.writerow(["url", "record_id", "source_file", "result", "status", "final_url"])

            async def one(url, rid, src):
                res = await check(client, url, host_sem, global_sem, timeout)
                w.writerow([url, rid, src, *res]); f.flush()

            await asyncio.gather(*(one(*t) for t in todo))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=float, default=30)
    ap.add_argument("--max-per-host", type=int, default=25)
    ap.add_argument("--concurrency", type=int, default=20)
    ap.add_argument("--per-host", type=int, default=2)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    items, picked, by_host = load(args.max_per_host, args.seed)
    done = set()
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8", newline="") as f:
            done = {r["url"] for r in csv.DictReader(f)}
    todo = [t for t in picked if t[0] not in done]
    print(f"{len(items)} timeouts on {len(by_host)} hosts; retrying {len(todo)} "
          f"(max {args.max_per_host} per host, {args.timeout:.0f}s timeout)")
    print("hosts with most timeouts:", Counter({h: len(v) for h, v in by_host.items()}).most_common(6))
    asyncio.run(run(todo, args.concurrency, args.per_host, args.timeout))

    with open(OUT, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    print(dict(Counter(r["result"] for r in rows)))


if __name__ == "__main__":
    main()
