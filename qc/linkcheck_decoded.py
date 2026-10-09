"""Second link-check pass for percent-encoded URLs (https%3A%2F%2F...). Resumable.

Decodes each URL once and checks the result with the same logic as qc.linkcheck.
Input: out/link_results_clean.csv (rows with result == invalid). Output: out/link_results_decoded.csv.

Usage: python -m qc.linkcheck_decoded [--sample N] [--seed 7] [--concurrency 20] [--per-host 2] [--timeout 10]
  --sample N picks N URLs spread round-robin across hosts (so one big host does not dominate).
"""
import argparse
import asyncio
import csv
import os
import random
from collections import Counter, defaultdict
from urllib.parse import unquote, urlparse

import httpx

from qc.linkcheck import UA, check

SRC = "out/link_results_clean.csv"
OUT = "out/link_results_decoded.csv"


def load(sample: int | None, seed: int) -> tuple[list[tuple[str, str, str]], Counter]:
    with open(SRC, encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["result"] == "invalid"]
    items, undecodable = [], Counter()
    for r in rows:
        dec = unquote(r["url"].strip())
        if urlparse(dec).scheme in ("http", "https") and urlparse(dec).netloc:
            items.append((r["url"], dec, r["record_id"]))
        else:
            undecodable["still_invalid_after_decode"] += 1
    if sample and sample < len(items):
        rng = random.Random(seed)
        by_host = defaultdict(list)
        for it in items:
            by_host[urlparse(it[1]).netloc].append(it)
        for v in by_host.values():
            rng.shuffle(v)
        hosts = list(by_host); rng.shuffle(hosts)
        picked = []
        while len(picked) < sample and any(by_host.values()):
            for h in hosts:
                if by_host[h] and len(picked) < sample:
                    picked.append(by_host[h].pop())
        items = picked
    return items, undecodable


async def run(todo, concurrency, per_host, timeout):
    host_sem = defaultdict(lambda: asyncio.Semaphore(per_host))
    global_sem = asyncio.Semaphore(concurrency)
    new_file = not os.path.exists(OUT)
    done = 0
    async with httpx.AsyncClient(headers={"User-Agent": UA}, follow_redirects=True,
                                 limits=httpx.Limits(max_connections=concurrency * 2)) as client:
        with open(OUT, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new_file:
                w.writerow(["encoded_url", "decoded_url", "record_id", "result", "status", "final_url"])

            async def one(enc, dec, rid):
                nonlocal done
                res = await check(client, dec, host_sem, global_sem, timeout)
                w.writerow([enc, dec, rid, *res])
                done += 1
                if done % 250 == 0:
                    f.flush(); print(f"  {done}/{len(todo)}", flush=True)

            await asyncio.gather(*(one(*t) for t in todo))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--concurrency", type=int, default=20)
    ap.add_argument("--per-host", type=int, default=2)
    ap.add_argument("--timeout", type=float, default=10)
    args = ap.parse_args()

    items, undecodable = load(args.sample, args.seed)
    done = set()
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8", newline="") as f:
            done = {row["encoded_url"] for row in csv.DictReader(f)}
    todo = [t for t in items if t[0] not in done]
    print(f"{len(items)} decodable URLs selected, {len(done)} already checked, {len(todo)} to check; "
          f"{dict(undecodable)}")
    asyncio.run(run(todo, args.concurrency, args.per_host, args.timeout))

    with open(OUT, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    print(dict(Counter(r["result"] for r in rows)))
    hosts = Counter(urlparse(r["decoded_url"]).netloc for r in rows)
    print("hosts:", hosts.most_common(6))


if __name__ == "__main__":
    main()
