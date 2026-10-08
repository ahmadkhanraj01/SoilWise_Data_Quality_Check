"""Accuracy: plausibility checks on structured values (no network).

Currently validates the `spatial` WKT polygon. Returns None when the record has nothing checkable,
so the dimension is skipped for it and the remaining weights are renormalised.
Link/DOI liveness (qc/linkcheck.py) is not part of this check yet.
"""
import re

from qc.models import CheckResult, Record

NUM = re.compile(r"-?\d+(?:\.\d+)?")


def _points(wkt: str) -> list[tuple[float, float]]:
    nums = [float(n) for n in NUM.findall(wkt)]
    return list(zip(nums[0::2], nums[1::2]))


def check(r: Record) -> CheckResult | None:
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
