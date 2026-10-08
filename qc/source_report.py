"""Per-source field gap report (read-only). Writes out/source_gaps.md.

Usage: python -m qc.source_report
"""
from collections import defaultdict

from qc import config as C
from qc.fetch import fetch_records

CHECKS = {
    "abstract<200": lambda r: len((r.abstract or "").strip()) < C.MIN_ABSTRACT_CHARS,
    "no license": lambda r: not r.license,
    "no url": lambda r: not r.url,
    "no person/org": lambda r: not r.n_persons and not r.n_orgs,
    "no keywords": lambda r: not r.n_subjects,
    "no dates": lambda r: not (r.publication_date or r.resource_creation_date or r.resource_updated_date),
    "no distribution": lambda r: not r.n_distributions,
}
SYSTEMIC = 0.80   # share of a source's records missing a field to call the gap systemic


def main() -> None:
    by_source = defaultdict(list)
    for r in fetch_records():
        by_source[r.source].append(r)

    names = list(CHECKS)
    lines = ["# Per-source gaps (% of records missing)\n",
             "| source | n | " + " | ".join(names) + " |", "|---|---|" + "---|" * len(names)]
    systemic = {}
    for src, recs in sorted(by_source.items(), key=lambda x: -len(x[1])):
        pct = {k: sum(f(r) for r in recs) / len(recs) for k, f in CHECKS.items()}
        systemic[src] = [k for k, v in pct.items() if v >= SYSTEMIC]
        lines.append(f"| {src} | {len(recs)} | " + " | ".join(
            f"**{v:.0%}**" if v >= SYSTEMIC else f"{v:.0%}" for v in pct.values()) + " |")
    lines += ["", f"## Systemic gaps (>= {SYSTEMIC:.0%} of a source's records)", ""]
    for src, gaps in systemic.items():
        if gaps:
            lines.append(f"- **{src}**: {', '.join(gaps)}")
    open("out/source_gaps.md", "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
