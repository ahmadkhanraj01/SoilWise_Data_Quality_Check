"""Source-level gap detection: fields missing in most of a source's records are waived per record."""
from collections import defaultdict

from qc import config as C

# gap name -> predicate (True = field missing)
GAPS = {
    "license": lambda r: not r.license,
    "url": lambda r: not r.url,
    "person_org": lambda r: not r.n_persons and not r.n_orgs,
    "keywords": lambda r: not r.n_subjects,
    "dates": lambda r: not (r.publication_date or r.resource_creation_date or r.resource_updated_date),
}


def source_gap_rates(records) -> dict[str, dict[str, float]]:
    by_source = defaultdict(list)
    for r in records:
        by_source[r.source].append(r)
    return {src: {g: sum(f(r) for r in recs) / len(recs) for g, f in GAPS.items()}
            for src, recs in by_source.items()}


def waived_by_source(records) -> dict[str, set[str]]:
    """Gaps treated as systemic (rate >= threshold, source large enough) -> not penalised per record."""
    counts = defaultdict(int)
    for r in records:
        counts[r.source] += 1
    return {src: {g for g, v in rates.items() if v >= C.SYSTEMIC_THRESHOLD}
            if counts[src] >= C.MIN_SOURCE_SIZE else set()
            for src, rates in source_gap_rates(records).items()}
