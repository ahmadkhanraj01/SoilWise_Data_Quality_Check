from dataclasses import dataclass, field


@dataclass
class Record:
    id: str
    identifier: str
    title: str
    abstract: str | None
    resource_type: str | None
    license: str | None
    language: str | None
    url: str | None
    publication_date: object
    resource_creation_date: object
    resource_updated_date: object
    temporal_start: object
    temporal_end: object
    spatial: str | None
    approval_status: str
    source: str | None
    n_persons: int
    n_orgs: int
    n_subjects: int
    n_distributions: int


@dataclass
class CheckResult:
    dimension: str
    score: float                      # 0..1
    flags: list[str] = field(default_factory=list)   # minor issues
    major: list[str] = field(default_factory=list)   # force review/reject
    applies: bool = True                              # False: flags are kept but the score is not used
