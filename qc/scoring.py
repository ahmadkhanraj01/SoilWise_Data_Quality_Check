from qc import config as C
from qc.models import CheckResult


def decide(results: list[CheckResult]) -> tuple[float, str]:
    w = {x.dimension: C.WEIGHTS[x.dimension] for x in results}
    total = sum(w.values())
    overall = sum(x.score * w[x.dimension] for x in results) / total
    major = any(x.major for x in results)
    if overall < C.REJECT_MAX:
        return overall, "reject"
    if overall >= C.PUBLISH_MIN and not major:
        return overall, "publish"
    return overall, "review"
