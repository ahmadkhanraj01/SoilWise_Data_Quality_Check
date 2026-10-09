# docs

| File | Contents |
|---|---|
| `NEXT_STEPS.md` | Deferred work: decoded link-check pass, accuracy scoring, open decisions, harvester tickets |
| `TEAM_QUESTIONS.md` | Four decisions needed from the team (scope, labeled sample, trusted sources, where results go) |
| `HARVESTER_TICKETS.md` | Draft tickets for the harvester owners with counts and evidence |
| `FINDINGS.md` | Data profile of `validate.records`, scoring runs, source-aware scoring, relevance and link-check results |

## Quality dimensions (one file each: what it is, how it is checked, data flow, what remains, suggestions)

| File | Dimension | Weight |
|---|---|---|
| `COMPLETENESS.md` | Are the fields present and substantive? | 0.25 |
| `CONSISTENCY.md` | Do the fields agree with each other and the corpus? | 0.20 |
| `CREDIBILITY.md` | Is the record trustworthy: source, attribution, license, link? | 0.20 |
| `RELEVANCE.md` | Is it about soil / land / agriculture (NLP: embeddings + keywords)? | 0.25 |
| `ACCURACY.md` | Are the values correct (spatial WKT; link liveness planned)? | 0.10, penalty-only |

Project overview and diagrams: [`../README.md`](../README.md).
