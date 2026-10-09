# docs

Documentation for the SoilWise Data Quality Check. Start with [`../README.md`](../README.md)
for the project overview, or pick a file below.

## Quality dimensions (the five TOR checks)

One file per dimension, written for technical and non-technical readers alike: what it is in
plain words, how the code checks it (with the exact rules), a data flow diagram, what the data
showed, what is still missing, and suggestions.

| File | Dimension | Weight | In one sentence |
|---|---|---|---|
| [`COMPLETENESS.md`](COMPLETENESS.md) | Completeness | 0.25 | Is everything that should be in the record actually there? |
| [`CONSISTENCY.md`](CONSISTENCY.md) | Consistency | 0.20 | Does the record contradict itself or the rest of the collection? |
| [`CREDIBILITY.md`](CREDIBILITY.md) | Credibility | 0.20 | Can a user trust it: source, author, license, working link? |
| [`RELEVANCE.md`](RELEVANCE.md) | Relevance | 0.25 | Is it actually about soil / land / agriculture (NLP)? |
| [`ACCURACY.md`](ACCURACY.md) | Accuracy | 0.10, penalty-only | Are the values correct: valid map shapes, working links? |

## Results and analysis

| File | Contents |
|---|---|
| [`FINDINGS.md`](FINDINGS.md) | Data profile of `validate.records`, scoring runs 1-4, source-aware scoring, relevance and link-check results |

## Planning and decisions

| File | Contents |
|---|---|
| [`NEXT_STEPS.md`](NEXT_STEPS.md) | Deferred work: decoded link-check pass, accuracy scoring, open decisions, harvester tickets |
| [`TEAM_QUESTIONS.md`](TEAM_QUESTIONS.md) | Four decisions needed from the team (scope, labeled sample, trusted sources, where results go) |
| [`HARVESTER_TICKETS.md`](HARVESTER_TICKETS.md) | Draft tickets for the harvester owners with counts and evidence |

Numbers in the dimension files come from `out/qc_results.csv` (run4, 25,129 records) and are listed in
[`FINDINGS.md`](FINDINGS.md); where a file cites run3, the dimension did not change in run4.

Project overview and diagrams: [`../README.md`](../README.md).
Code-level docs: [`../qc/README.md`](../qc/README.md) and
[`../qc/checks/README.md`](../qc/checks/README.md).
