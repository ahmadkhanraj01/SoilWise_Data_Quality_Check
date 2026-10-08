"""Check that record URLs and distribution links resolve. Resumable; writes out/link_results.csv.

Polite by design: low global concurrency, max 2 parallel requests per host, HEAD first
(falls back to a streamed GET that never downloads the body), no retries beyond one fallback.

Usage: python -m qc.linkcheck [--limit N] [--concurrency 20] [--per-host 2] [--timeout 10]
"""
import argparse
import asyncio
import csv
import os
from collections import defaultdict
from urllib.parse import quote, unquote, urlparse

import httpx

from qc.db import connect, get_schema

OUT = "out/link_results.csv"
UA = "SoilWise-QualityCheck/0.1 (link validation; contact: project maintainers)"


def load_urls(limit: int | None) -> list[tuple[str, str]]:
    """(url, record_id) for records.url and distributions.access_url, first record per URL."""
    s = get_schema()
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SET statement_timeout = '300s'")
        cur.execute(f"""SELECT url, id::text FROM {s}.records WHERE url IS NOT NULL
                        UNION ALL
                        SELECT access_url, record_id::text FROM {s}.distributions WHERE access_url IS NOT NULL""")
        seen, out = set(), []
        for url, rid in cur.fetchall():
            url = url.strip()
            if url not in seen:
                seen.add(url); out.append((url, rid))
    return out[:limit] if limit else out


def classify(status: int) -> str:
    if 200 <= status < 400:
        return "ok"
    if status in (404, 410):
        return "broken"
    if status in (401, 403, 405, 429):
        return "restricted"      # reachable but refused; not evidence the link is dead
    return "server_error" if status >= 500 else "client_error"


async def check_doi(client, parsed, host_sem, global_sem, timeout):
    """Verify a DOI is registered via the doi.org handle API, without hitting publisher sites
    (which commonly bot-block and would show up as false 'restricted')."""
    doi = parsed.path.lstrip("/")
    if parsed.query:
        doi += "?" + parsed.query
    async with global_sem, host_sem["doi.org"]:
        try:
            r = await client.get("https://doi.org/api/handles/" + quote(unquote(doi), safe="/"),
                                 timeout=timeout)
            if r.status_code == 404:
                return "broken", 404, ""
            if r.status_code == 200:
                code = r.json().get("responseCode")
                return ("ok" if code == 1 else "broken"), 200, f"handle_responseCode={code}"
            return classify(r.status_code), r.status_code, ""
        except httpx.TimeoutException:
            return "timeout", 0, ""
        except (httpx.HTTPError, ValueError) as e:
            return "error", 0, type(e).__name__


async def check(client, url, host_sem, global_sem, timeout):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return "invalid", 0, ""
    if parsed.netloc in ("doi.org", "dx.doi.org", "www.doi.org"):
        return await check_doi(client, parsed, host_sem, global_sem, timeout)
    async with global_sem, host_sem[parsed.netloc]:
        try:
            r = await client.head(url, timeout=timeout)
            if r.status_code in (403, 405, 501):          # some servers reject HEAD
                async with client.stream("GET", url, timeout=timeout) as g:
                    r = g
                    return classify(g.status_code), g.status_code, str(g.url)
            return classify(r.status_code), r.status_code, str(r.url)
        except httpx.TimeoutException:
            return "timeout", 0, ""
        except httpx.ConnectError as e:
            return ("dns_error" if "Name or service" in str(e) or "getaddrinfo" in str(e) else "connect_error"), 0, ""
        except httpx.HTTPError as e:
            return "error", 0, type(e).__name__


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
                w.writerow(["url", "record_id", "result", "status", "final_url"])

            async def one(url, rid):
                nonlocal done
                res = await check(client, url, host_sem, global_sem, timeout)
                w.writerow([url, rid, *res])
                done += 1
                if done % 500 == 0:
                    f.flush(); print(f"  {done}/{len(todo)}", flush=True)

            await asyncio.gather(*(one(u, r) for u, r in todo))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--concurrency", type=int, default=20)
    ap.add_argument("--per-host", type=int, default=2)
    ap.add_argument("--timeout", type=float, default=10)
    args = ap.parse_args()

    urls = load_urls(args.limit)
    done = set()
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8", newline="") as f:
            done = {row["url"] for row in csv.DictReader(f)}
    todo = [(u, r) for u, r in urls if u not in done]
    print(f"{len(urls)} unique URLs, {len(done)} already checked, {len(todo)} to check")
    asyncio.run(run(todo, args.concurrency, args.per_host, args.timeout))

    from collections import Counter
    with open(OUT, encoding="utf-8", newline="") as f:
        print(dict(Counter(row.get("result") for row in csv.DictReader(f))))


if __name__ == "__main__":
    main()
