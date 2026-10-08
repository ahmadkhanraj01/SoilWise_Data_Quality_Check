from datetime import datetime, timezone

from langdetect import DetectorFactory, LangDetectException, detect

from qc import config as C
from qc.models import CheckResult, Record

DetectorFactory.seed = 0


def check(r: Record, dup_title: bool = False, dup_url: bool = False) -> CheckResult:
    score, flags, major = 1.0, [], []
    now = datetime.now(timezone.utc)

    if r.publication_date and r.publication_date > now:
        flags.append("publication_in_future"); score -= 0.25
    if r.resource_creation_date and r.publication_date and r.resource_creation_date > r.publication_date:
        flags.append("created_after_published"); score -= 0.1
    if r.resource_creation_date and r.resource_updated_date and r.resource_updated_date < r.resource_creation_date:
        flags.append("updated_before_created"); score -= 0.1
    if r.temporal_start and r.temporal_end and r.temporal_end < r.temporal_start:
        flags.append("temporal_end_before_start"); score -= 0.15

    t = (r.title or "").strip()
    if len(t) < C.MIN_TITLE_CHARS:
        flags.append("title_too_short"); score -= 0.2
    elif len(t) > C.MAX_TITLE_CHARS:
        flags.append("title_too_long"); score -= 0.1
    elif t == t.upper():
        flags.append("title_all_caps"); score -= 0.05

    if dup_title:
        flags.append("duplicate_title"); score -= 0.15
    if dup_url:
        flags.append("duplicate_url"); score -= 0.15

    text = (r.abstract or "").strip()
    expected = C.LANG_CODES.get(r.language or "")
    if expected and len(text) >= 100:
        try:
            if detect(text) != expected:
                flags.append("language_mismatch"); score -= 0.2
        except LangDetectException:
            pass
    return CheckResult("consistency", max(score, 0.0), flags, major)
