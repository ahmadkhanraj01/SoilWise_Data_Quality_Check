# checks

One module per quality dimension. Each returns a `CheckResult` (`score` 0..1, `flags`, `major`).
Source-aware: completeness and credibility accept a `waived` set (see `../gaps.py`).

| Module | Dimension | Signature |
|---|---|---|
| `completeness.py` | Completeness | `check(record, waived)` |
| `consistency.py` | Consistency | `check(record, dup_title, dup_url)` |
| `credibility.py` | Credibility (offline signals) | `check(record, waived)` |
| `relevance.py` | Relevance | `score_all(records)` (batch, embeddings) |
| `accuracy.py` | Accuracy (spatial WKT plausibility; returns None when no spatial value) | `check(record)` |
| link liveness | not in the score yet; see `../linkcheck.py` | |

## completeness

```mermaid
flowchart TD
    R[record] --> A{abstract}
    A -->|missing or placeholder| M1[major -0.50]
    A -->|under 50 chars| M2[major -0.35]
    A -->|under 200 chars| F1[flag -0.15]
    R --> O[other gaps, each skipped if waived<br/>no author/org -0.15, no url -0.10,<br/>no keywords -0.10, no dates -0.10, no license -0.05]
    M1 --> S[score = 1.0 minus penalties, floor 0]
    M2 --> S
    F1 --> S
    O --> S
```

## consistency

| Condition | Penalty |
|---|---|
| Publication date in the future | 0.25 |
| Title under 10 chars | 0.20 |
| Abstract language differs from `language` field (`langdetect`, abstract of 100+ chars) | 0.20 |
| Temporal end before start | 0.15 |
| Duplicate normalized title / duplicate URL | 0.15 each |
| Created after published; updated before created | 0.10 each |
| Title over 250 chars | 0.10 |
| Title all caps | 0.05 |

Duplicates are detected across the whole run, so they only work when scoring all records.

## credibility

```mermaid
flowchart LR
    ST[source trust x 0.5<br/>default 0.7 for every source] --> E[earned points]
    AT[author or org +0.20] --> E
    LI[license +0.15] --> E
    UR[url or distribution +0.15] --> E
    E --> SC[score = earned / possible]
    WV[waived components<br/>removed from both] -.-> SC
```

DOI and URL liveness are not part of this score yet.

## relevance

```mermaid
flowchart LR
    T[title + abstract start + keyword labels] --> EM[multilingual MiniLM embedding]
    SE[20 topic seeds, topics.py] --> SM[mean of 3 best seed similarities]
    EM --> SM
    T --> KW[keyword hits]
    SM -->|70%| SC[score]
    KW -->|30%| SC
    SC -->|under 0.25 and no keyword| MJ[major: possibly_off_topic]
    SC -->|under 0.45| WK[flag: weak_topic_match]
```

Embeddings are cached in `out/emb_cache.npz`. Mapping from similarity to 0..1 uses `SIM_LOW` / `SIM_HIGH` in `config.py`.
