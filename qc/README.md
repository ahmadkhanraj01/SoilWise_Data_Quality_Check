# qc package

The code that reads records, runs the checks, scores them and writes results.
Project overview and full diagrams: [`../README.md`](../README.md). Individual checks: [`checks/README.md`](checks/README.md).

## Module flow

```mermaid
flowchart LR
    DB[(PostgreSQL<br/>read-only)] --> fetch[fetch.py]
    fetch --> runner[runner.py]
    runner --> gaps[gaps.py<br/>source waivers]
    gaps --> checks[checks/*]
    runner --> checks
    checks --> scoring[scoring.py]
    scoring --> csv[/out/qc_results.csv/]
    db2[db.py] -.used by.-> fetch
    cfg[config.py] -.settings.-> checks
    cfg -.settings.-> scoring
    cfg -.settings.-> gaps
```

## Files

| File | Role |
|---|---|
| `db.py` | Connection from `DB_*` env vars (loaded from `.env` at runtime), read-only |
| `config.py` | Weights, thresholds, source trust, waiver settings, relevance cut-offs |
| `models.py` | `Record` and `CheckResult` dataclasses |
| `fetch.py` | Loads records plus counts of persons, organizations, subjects, distributions, and source |
| `gaps.py` | Detects fields systematically missing per source (waivers) |
| `topics.py` | Soil/land/agri topic seeds and keywords for relevance |
| `checks/` | One module per dimension |
| `scoring.py` | Weighted score to publish / review / reject |
| `runner.py` | Runs everything, writes `out/qc_results.csv` |
| `linkcheck.py` | URL and DOI liveness checker (separate, resumable job) |
| `export_labeling.py` | Builds the blind labeling workbook for domain experts |
| `linkcheck_decoded.py` | Second link-check pass: decodes percent-encoded URLs once, then checks them (`--sample N` spreads across hosts) |
| `linkcheck_retry.py` | Retries timed-out URLs with a longer limit (max 25 per host) to separate slow from dead hosts |
| `source_report.py` | Per-source gap report (`out/source_gaps.md`) |
| `discover.py`, `profile.py` | Schema discovery and data profiling reports |

Each check returns a `CheckResult`: a `score` in 0..1, `flags` (minor issues that lower the score) and
`major` (serious issues that block automatic publish).

## Scoring (`scoring.py`)

```mermaid
flowchart TD
    S[Dimension scores<br/>completeness, consistency,<br/>credibility, relevance] --> W[Weighted average<br/>weights from config.WEIGHTS,<br/>renormalised over available dimensions]
    ACC[Accuracy score<br/>spatial + link checks] --> PEN[Penalty only<br/>overall -= 0.10 x 1 - accuracy]
    W --> PEN
    PEN --> A{overall}
    A -->|under 0.40| R[reject]
    A -->|0.40 to 0.75| V[review]
    A -->|0.75 or more| M{any major flag?}
    M -->|no| P[publish]
    M -->|yes| V
```

Accuracy is penalty-only (`ACCURACY_PENALTY_ONLY`): it subtracts `0.10 * (1 - score)` and never adds. A result with
`applies=False` (e.g. relevance for thin-text records) keeps its flags but is left out of the average.

Weights: completeness 0.25, consistency 0.20, credibility 0.20, relevance 0.25 (the four averaged dimensions), plus
accuracy 0.10 as a penalty. Accuracy covers the spatial check and link liveness (`linkscore.py`, definitive ok/broken answers only).

## Source-aware scoring (`gaps.py`)
A field missing in at least `SYSTEMIC_THRESHOLD` (80%) of a source's records is a harvester-level gap. For
sources with at least `MIN_SOURCE_SIZE` (50) records it is waived: not penalised per record in completeness,
and dropped from the credibility score. Waivable: license, url, person_org, keywords, dates. Abstract length
and the consistency checks are never waived. The gaps stay visible in `out/source_gaps.md`
(`python -m qc.source_report`) and should be fixed in the harvesters.

## Tuning
Edit `config.py`: weights, thresholds, `SOURCE_TRUST`, length limits, `SIM_LOW` / `SIM_HIGH`,
`OFFTOPIC_MAX`, `WEAK_TOPIC_MAX`. Thresholds are untuned guesses until labeled records exist.

## Adding a check
Create `checks/<name>.py` with `check(record) -> CheckResult`, add the weight to `config.WEIGHTS`, and call it in
`runner.py`. (`relevance.py` is batch-based: `score_all(records)`.)

## Output (`out/qc_results.csv`)
See [`../out/README.md`](../out/README.md).
