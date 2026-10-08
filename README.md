# SoilWise Data Quality Check

Quality assurance for Knowledge Hub records (TOR p. 25): validate **relevance, credibility,
completeness, accuracy and consistency** with automated checks, plus manual review where needed.

Data source: PostgreSQL `msp-kh-dev`, schema `validate` (main table `records`, ~25k harvested
metadata records from 14 sources).

## Status

| Dimension | State |
|---|---|
| Completeness | Done (rule-based, source-aware) |
| Consistency | Done (dates, titles, duplicates, language) |
| Credibility | Partial (offline signals only; source trust is flat) |
| Relevance | Done (multilingual embeddings + keywords); cut-offs untuned |
| Accuracy | In progress: link/DOI checker built (`qc.linkcheck`), not yet in the score |

The runner writes a CSV only. It never modifies the database.

## How it works

Diagrams are Mermaid and render on GitHub / GitLab / most Markdown viewers.

### 1. End-to-end data flow

```mermaid
flowchart LR
    DB[(PostgreSQL<br/>msp-kh-dev<br/>schema: validate)]
    subgraph READ["Read-only access"]
        F[fetch.py<br/>records + counts of persons,<br/>orgs, subjects, distributions + source]
        S[relevance.fetch_subject_text<br/>keyword labels per record]
        U[linkcheck.load_urls<br/>records.url + distributions.access_url]
    end
    DB --> F
    DB --> S
    DB --> U

    F --> G[gaps.py<br/>find fields missing in 80%+<br/>of a source's records]
    G -->|waived fields per source| C
    F --> C[Per-record checks<br/>completeness / consistency / credibility]
    F --> R[relevance.py<br/>embeddings + keywords]
    S --> R
    U --> L[linkcheck.py<br/>URL + DOI liveness]

    C --> SC[scoring.py<br/>weighted score + decision]
    R --> SC
    L -. planned: accuracy .-> SC

    SC --> CSV[/out/qc_results.csv/]
    G --> SG[/out/source_gaps.md/]
    L --> LR[/out/link_results.csv/]
    CSV --> REV[Reviewer<br/>works the 'review' list]
```

Solid arrows exist today. The dotted arrow (link results feeding the score) is the next step.
Nothing is written back to the database.

### 2. What happens to one record

```mermaid
flowchart TD
    A[Record from DB] --> WV[Waived fields for the record's source<br/>from gaps.py, applied inside<br/>completeness and credibility]

    subgraph CHECKS["Dimension scores (each 0 to 1)"]
        C1[Completeness<br/>abstract length, url, author/org,<br/>keywords, dates, license]
        C2[Consistency<br/>date logic, title length/case,<br/>duplicate title or url,<br/>abstract language vs language field]
        C3[Credibility<br/>source trust, attribution,<br/>license, url or distribution]
        C4[Relevance<br/>similarity to soil/land/agri topics<br/>+ keyword hits in title,<br/>abstract and keywords]
    end

    A --> C1
    A --> C2
    A --> C3
    A --> C4
    WV -.-> C1
    WV -.-> C3

    C1 --> W[Weighted average<br/>0.25 / 0.20 / 0.20 / 0.25<br/>renormalised]
    C2 --> W
    C3 --> W
    C4 --> W

    C1 -. major flag .-> M
    C4 -. possibly_off_topic .-> M[Major flag present?]

    W --> D{Overall score}
    D -->|below 0.40| REJ[reject]
    D -->|0.75 or more| M
    D -->|0.40 to 0.75| REVW[review]
    M -->|no major flag| PUB[publish]
    M -->|major flag| REVW
```

### 3. Relevance check

```mermaid
flowchart LR
    T[Title + first 1200 chars of abstract<br/>+ keyword labels] --> E[Multilingual MiniLM<br/>embedding]
    SEEDS[20 soil / land / agri<br/>topic seeds in topics.py] --> E2[Seed embeddings]
    E --> SIM[Cosine similarity<br/>mean of 3 best-matching seeds]
    E2 --> SIM
    T --> KW[Keyword hits<br/>soil, bodem, boden, suolo, pédolog ...]
    SIM -->|70%| SCORE[Relevance score 0 to 1]
    KW -->|30%| SCORE
    SCORE --> OUT{Result}
    OUT -->|below 0.25 and no keywords| OFF[major flag:<br/>possibly_off_topic]
    OUT -->|below 0.45| WEAK[flag: weak_topic_match]
    OUT -->|otherwise| OK[relevant]
```

Embeddings are cached in `out/emb_cache.npz`, so changing cut-offs or keywords re-runs in minutes.

### 4. Link / DOI checker

```mermaid
flowchart TD
    URLS[Unique URLs from records.url<br/>and distributions.access_url] --> K{Valid http/https URL?}
    K -->|no, e.g. percent-encoded| INV[invalid<br/>second pass decodes and rechecks]
    K -->|yes| H{Host is doi.org?}
    H -->|yes| API[doi.org handle API<br/>does not touch publisher sites]
    H -->|no| HEAD[HEAD request<br/>20 parallel, max 2 per host]
    HEAD -->|403 / 405 / 501| GET[streamed GET<br/>body never downloaded]
    API --> RES
    HEAD --> RES
    GET --> RES
    RES{{Result}} --> OK[ok]
    RES --> BR[broken: 404 / 410 / unregistered DOI]
    RES --> RS[restricted: 401 / 403 / 405 / 429<br/>reachable, not proof of dead link]
    RES --> ER[timeout / dns / connect / server error]
    OK --> CSV[(out/link_results.csv<br/>resumable)]
    BR --> CSV
    RS --> CSV
    ER --> CSV
    INV --> CSV
```

### 5. Source-aware scoring

A field missing in 80%+ of a source's records (and the source has 50+ records) is a harvester-level
gap, not a record-level defect. It is reported once in `out/source_gaps.md` and **not** penalised per
record, so reviewers see records that are unusual for their source.

```mermaid
flowchart LR
    ALL[All records of a source] --> RATE[Missing rate per field<br/>license, url, person_org,<br/>keywords, dates]
    RATE --> T{80% or more missing<br/>and source has 50+ records?}
    T -->|yes| WV[Waived for that source<br/>shown in source_gaps.md,<br/>fix in the harvester]
    T -->|no| PEN[Penalised per record]
```

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install torch --index-url https://download.pytorch.org/whl/cpu   # CPU build, much smaller
cp envExample.txt .env      # then fill in DB_USER and DB_PASSWORD
```

`.env` holds credentials and is git-ignored. `envExample.txt` is the template.

## Usage

```bash
python -m qc.discover --samples 2   # schema_report.md: tables, columns, row counts, samples
python -m qc.profile                # profile_report.md: null rates, value distributions, duplicates
python -m qc.source_report          # out/source_gaps.md: fields systematically missing per source
python -m qc.runner                 # out/qc_results.csv: scores and decisions (~16 min first run, cached after)
python -m qc.runner --no-relevance  # skip the embedding step (~6 min)
python -m qc.runner --limit 500     # quick test run
python -m qc.linkcheck              # out/link_results.csv: URL/DOI liveness (long, resumable)
```

All database access is read-only. The link checker contacts third-party sites, politely
(low concurrency, max 2 parallel requests per host, no body downloads).

## Layout

```
qc/
  config.py        weights, thresholds, source trust, language map, relevance cut-offs
  db.py            connection from DB_* env vars (read-only)
  models.py        Record, CheckResult
  fetch.py         loads records plus relation counts
  gaps.py          source-level gap detection (waivers)
  topics.py        soil/land/agri topic seeds and keywords
  checks/          completeness.py, consistency.py, credibility.py, relevance.py
  scoring.py       weighted score -> publish / review / reject
  runner.py        runs everything, writes CSV
  linkcheck.py     URL and DOI liveness, resumable
  source_report.py per-source gap report
  discover.py      schema discovery
  profile.py       data profiling
```

See `qc/README.md` for the checks and scoring, and `docs/FINDINGS.md` for the data profile
and results.

## Known data issues found so far

- Most `distributions.access_url` values (about 34k) are fully percent-encoded
  (`https%3A%2F%2F...`) and cannot be opened as links: a harvester/ingest defect.
- License is missing in 82-100% of records in 12 of 14 sources.
- impact4soil, prepsoil and islandr lack authors, keywords and dates systematically.

## Planned next

Full detail in [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md).

1. Second link-check pass on decoded URLs, then add link results to the score as the accuracy dimension.
2. Calibrate relevance cut-offs and thresholds on ~50 labeled records.
3. Decide whether food/livestock content is in scope (affects eufarmbook).
4. Persist results (`approval_status` or a separate `qc` schema) and a reviewer queue.
