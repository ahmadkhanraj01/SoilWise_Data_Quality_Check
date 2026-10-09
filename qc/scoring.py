from qc import config as C
from qc.models import CheckResult


def decide(results: list[CheckResult]) -> tuple[float, str]:
    acc = next((x for x in results if x.dimension == "accuracy" and x.applies), None)
    scored = [x for x in results if x.applies and not (C.ACCURACY_PENALTY_ONLY and x.dimension == "accuracy")]
    w = {x.dimension: C.WEIGHTS[x.dimension] for x in scored}
    total = sum(w.values())
    overall = sum(x.score * w[x.dimension] for x in scored) / total
    if acc and C.ACCURACY_PENALTY_ONLY:
        # accuracy can only lower the score: a passing check must not lift borderline records
        overall -= C.WEIGHTS["accuracy"] * (1 - acc.score)
    major = any(x.major for x in results)
    if overall < C.REJECT_MAX:
        return overall, "reject"
    if overall >= C.PUBLISH_MIN and not major:
        return overall, "publish"
    return overall, "review"
