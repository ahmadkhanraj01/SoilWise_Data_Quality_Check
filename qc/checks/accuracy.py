"""Accuracy: plausibility checks on structured values (no network).

Validates the `spatial` WKT polygon and, when link evidence exists (qc/linkscore.py), link liveness:
share of definitively answered links that work (timeouts/restricted are unknown and ignored). The score is
the lower of the two. Returns None when the record has nothing checkable, so the dimension is skipped for it
and the remaining weights are renormalised.
"""
import re

from qc.models import CheckResult, Record

NUM = re.compile(r"-?\d+(?:\.\d+)?")


def _points(wkt: str) -> list[tuple[float, float]]:
    nums = [float(n) for n in NUM.findall(wkt)]
    return list(zip(nums[0::2], nums[1::2]))


def check(r: Record, links: tuple[int, int] | None = None) -> CheckResult | None:
    """links = (ok, broken) counts of definitive link results, or None when there is no link evidence."""
    spatial = _spatial(r)
    link = _link(links)
    if spatial is None and link is None:
        return None
    parts = [x for x in (spatial, link) if x]
    score = min(x.score for x in parts)
    return CheckResult("accuracy", score, [f for x in parts for f in x.flags], [f for x in parts for f in x.major])


def _link(links) -> CheckResult | None:
    if not links or sum(links) == 0:
        return None
    ok, broken = links
    return CheckResult("accuracy", ok / (ok + broken), ["broken_link"] if broken else [], [])


def _spatial(r: Record) -> CheckResult | None:
    if not r.spatial or not r.spatial.strip():
        return None
    score, flags, major = 1.0, [], []
    wkt = r.spatial.strip().upper()
    pts = _points(wkt)

    if not wkt.startswith(("POLYGON", "MULTIPOLYGON")) or len(pts) < 4:
        major.append("spatial_unparseable"); score -= 0.6
    else:
        if any(abs(x) > 180 for x, _ in pts) or any(abs(y) > 90 for _, y in pts):
            major.append("coordinates_out_of_range"); score -= 0.6
        if len(NUM.findall(wkt)) % 2:
            flags.append("odd_coordinate_count"); score -= 0.2
        if wkt.startswith("POLYGON") and pts[0] != pts[-1]:
            flags.append("polygon_not_closed"); score -= 0.2
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        if max(xs) - min(xs) == 0 or max(ys) - min(ys) == 0:
            flags.append("degenerate_extent"); score -= 0.3
    return CheckResult("accuracy", max(score, 0.0), flags, major)
