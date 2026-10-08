from qc import config as C
from qc.models import CheckResult, Record

PLACEHOLDERS = {"tbd", "n/a", "na", "none", "null", "lorem ipsum", "-", "untitled", "no abstract"}


def check(r: Record, waived: frozenset | set = frozenset()) -> CheckResult:
    score, flags, major = 1.0, [], []
    abstract = (r.abstract or "").strip()
    n = len(abstract)

    if abstract.lower() in PLACEHOLDERS or n == 0:
        major.append("abstract_missing_or_placeholder"); score -= 0.5
    elif n < C.SHORT_ABSTRACT_CHARS:
        major.append("abstract_very_short"); score -= 0.35
    elif n < C.MIN_ABSTRACT_CHARS:
        flags.append("abstract_short"); score -= 0.15

    if not r.url and "url" not in waived:
        flags.append("no_url"); score -= 0.1
    if not r.n_persons and not r.n_orgs and "person_org" not in waived:
        flags.append("no_author_or_org"); score -= 0.15
    if not r.n_subjects and "keywords" not in waived:
        flags.append("no_keywords"); score -= 0.1
    if not r.license and "license" not in waived:
        flags.append("no_license"); score -= 0.05
    if not (r.publication_date or r.resource_creation_date or r.resource_updated_date) and "dates" not in waived:
        flags.append("no_dates"); score -= 0.1
    return CheckResult("completeness", max(score, 0.0), flags, major)
