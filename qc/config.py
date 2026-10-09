"""Tunable settings for the quality checks."""

WEIGHTS = {"completeness": 0.25, "consistency": 0.20, "credibility": 0.20, "relevance": 0.25, "accuracy": 0.10}
# weights are renormalised over the dimensions available for a record (accuracy only applies to records with a spatial value)

# Accuracy covers only ~19% of records (those with a spatial value). As a normal weighted dimension a
# perfect score would lift borderline records over the publish line, so it only subtracts when it finds problems.
ACCURACY_PENALTY_ONLY = True

PUBLISH_MIN = 0.75
REJECT_MAX = 0.40

MIN_ABSTRACT_CHARS = 200
SHORT_ABSTRACT_CHARS = 50
MIN_TITLE_CHARS = 10
MAX_TITLE_CHARS = 250

# source -> trust 0..1 (all equal by default; edit when the team defines trusted sources)
DEFAULT_SOURCE_TRUST = 0.7
SOURCE_TRUST: dict[str, float] = {}

# language names in the DB -> langdetect codes
LANG_CODES = {
    "English": "en", "Italian": "it", "German": "de", "French": "fr", "Dutch": "nl",
    "Spanish": "es", "Portuguese": "pt", "Hungarian": "hu", "Romanian": "ro",
    "Swedish": "sv", "Danish": "da", "Latvian": "lv", "Czech": "cs", "Finnish": "fi",
    "Polish": "pl",
}

# Source-aware scoring: a field missing in >= SYSTEMIC_THRESHOLD of a source's records is
# reported at source level (out/source_gaps.md) and not penalised per record.
# Sources with fewer than MIN_SOURCE_SIZE records are never waived (too small to judge).
SYSTEMIC_THRESHOLD = 0.80
MIN_SOURCE_SIZE = 50

# Relevance (embedding similarity to qc/topics.py seeds). SIM_LOW/HIGH map the mean top-3 cosine
# similarity to 0..1; set from the observed distribution (see docs/FINDINGS.md).
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
SIM_LOW = 0.15
SIM_HIGH = 0.50
OFFTOPIC_MAX = 0.25
WEAK_TOPIC_MAX = 0.45
