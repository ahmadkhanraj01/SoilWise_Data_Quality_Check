from qc import config as C
from qc.models import CheckResult, Record


def check(r: Record, waived: frozenset | set = frozenset()) -> CheckResult:
    """Offline signals only; DOI/URL liveness checks come later.

    Components that are systemic gaps for the source are dropped from both earned and possible
    points, so the score is not lowered by a harvester-level gap.
    """
    flags = []
    earned = 0.5 * C.SOURCE_TRUST.get(r.source or "", C.DEFAULT_SOURCE_TRUST)
    possible = 0.5

    if "person_org" not in waived:
        possible += 0.2
        if r.n_persons or r.n_orgs:
            earned += 0.2
        else:
            flags.append("no_attribution")
    if "license" not in waived:
        possible += 0.15
        if r.license:
            earned += 0.15
        else:
            flags.append("no_license")
    if "url" not in waived:
        possible += 0.15
        if r.n_distributions or r.url:
            earned += 0.15
    return CheckResult("credibility", min(earned / possible, 1.0), flags)
