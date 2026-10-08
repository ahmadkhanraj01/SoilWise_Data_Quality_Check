# Findings (profiling, scoring runs, relevance, link check)

Data: `validate.records`, 25,129 rows, profiled 2026-10-08. Related tables: persons, organizations,
projects, subjects (joined through `record_*` tables), `distributions` (46,702 links), `sources` (14).
The `records_backup_*` tables are copies of `records` and are ignored.

## Profile
- `approval_status`: 25,125 pending, 3 approved, 1 disapproved.
- Never missing: title, abstract, resource_type, language.
- Mostly missing: license 77.5%, spatial 80.7%, resource_creation_date 88.9%, temporal 89-91%,
  thumbnail 91.4%. Also missing: publication_date 58.1%, url 7.9%.
- Abstracts: 986 under 50 chars, 4,885 between 50 and 199.
- Dates: 42 publications in the future, 78 created after published, 2 temporal end before start.
- Duplicates: 205 title groups, 122 URL groups, no duplicate identifiers.
- Titles: 82 under 10 chars, 38 over 250 chars, 205 all caps.
- Language: 88% English; abstract-language mismatches found in 880 records.
- Relations: 43% have a person, 43% an organization, 39% a subject.
- Resource types: Journal Article 10,965; Dataset 7,184; Other 1,508; Project 1,251; Document 1,232; Report 1,218.

## First run (equal source trust, untuned thresholds)
publish 12,907 / review 12,221 / reject 1.
Only 985 review cases carry a major flag; the rest fall in the 0.50-0.75 score band.

Review rate by source: impact4soil 92%, prepsoil 91%, islandr 97%, data.europa.eu 45%,
ejpsoil 37%, fao 35%, openaire 23%, eufarmbook 1%, bonares 4%.
impact4soil alone accounts for about 8,600 review cases, which points to a systematic gap in that
harvest (missing authors, keywords, license), not record-level problems.

## Source-aware scoring (second run)
Fields missing in 80%+ of a source's records are no longer penalised per record (see `qc/README.md`).
publish 22,697 / review 2,431 / reject 1 (was 12,907 / 12,221 / 1).
Remaining review cases are mostly records that are unusual for their source: short abstracts,
language mismatches, duplicates and gaps in sources that are otherwise complete.
The systemic gaps themselves still need harvester fixes; see `out/source_gaps.md`.

## Relevance check (third run)
Multilingual MiniLM embeddings (title, first 1,200 chars of abstract, keyword labels) compared with 20 soil/land/agri
topic seeds, combined 70/30 with keyword hits (`qc/checks/relevance.py`, seeds in `qc/topics.py`).
Flags: `possibly_off_topic` (major: score under 0.25 and no keyword hit) and `weak_topic_match` (score under 0.45).

Result of the corrected run (weights: completeness 0.25, consistency 0.20, credibility 0.20, relevance 0.25):
publish 20,471 / review 4,641 / reject 17. Totals: 1,830 off-topic, 3,043 weak matches.

| Source | Records | Off-topic | % | Weak | In review | % |
|---|---|---|---|---|---|---|
| impact4soil | 9,337 | 177 | 2% | 691 | 343 | 4% |
| openaire | 6,353 | 1,211 | 19% | 989 | 2,241 | 35% |
| data.europa.eu | 1,728 | 36 | 2% | 516 | 456 | 26% |
| cordis | 1,407 | 107 | 8% | 169 | 419 | 30% |
| eufarmbook | 1,353 | 169 | 12% | 261 | 205 | 15% |
| inspire | 1,313 | 28 | 2% | 89 | 156 | 12% |
| bonares | 1,300 | 45 | 3% | 114 | 145 | 11% |
| fao | 1,014 | 38 | 4% | 142 | 340 | 34% |
| ejpsoil | 674 | 11 | 2% | 30 | 205 | 30% |
| eea | 275 | 2 | 1% | 11 | 30 | 11% |
| prepsoil | 264 | 5 | 2% | 22 | 91 | 34% |
| islandr | 98 | 1 | 1% | 9 | 9 | 9% |
| ngr | 12 | 0 | 0% | 0 | 1 | 8% |
| isric | 1 | 0 | 0% | 0 | 0 | 0% |

- openaire dominates the off-topic flags (1,211 of 1,830). Spot checks show genuinely unrelated papers (optical
  metasurfaces, inductors, gut microbiome, polymer membranes).
- A keyword bug was found and fixed: French soil maps ("Carte pédologique ...") were flagged because the
  keyword list lacked accented forms. This took data.europa.eu from 9% to 2% off-topic.
- eufarmbook's flagged records are livestock, poultry, cheese traceability and animal breeding: agriculture, but
  not soil. Whether this is in scope is an open question (see `NEXT_STEPS.md`).
- The 0.25 / 0.45 cut-offs and the similarity range (0.15 to 0.50) were set from a few samples, not labeled data.

## Link and DOI check (first pass)
`qc/linkcheck.py` checked 56,721 unique URLs from `records.url` and `distributions.access_url`. DOIs are verified through
the doi.org handle API (publisher sites such as Wiley and Taylor & Francis return 403 to bots, which made 199 of 300
DOIs look restricted in a first version). Other URLs: HEAD request with a streamed-GET fallback, 20 in parallel,
max 2 per host, 10 second timeout.

| Result | URLs |
|---|---|
| invalid (percent-encoded, not yet tested) | 33,844 |
| ok | 21,196 |
| timeout | 868 |
| client_error | 584 |
| broken (404/410 or unregistered DOI) | 78 |
| restricted (401/403/405/429) | 78 |
| connect_error | 49 |
| dns_error | 14 |
| server_error / other error | 5 |

- **Defect:** 33,844 `distributions.access_url` values (about 72% of links checked) are stored fully
  percent-encoded (`https%3A%2F%2F...`) and cannot be opened as links. A decoded second pass is deferred
  (see `NEXT_STEPS.md`).
- Of the 22,872 URLs that could be tested, 92.7% are ok.
- Failures cluster on a few hosts: maps.bonares.de 822, ec.europa.eu 547 (plus 29 on www.ec.europa.eu),
  hdl.handle.net 48. DOIs are healthy (14 failures). Many failures are timeouts, which may only mean slow servers;
  retrying with a longer limit would separate slow from dead.
- 5 result rows were malformed and dropped. The raw file had been reformatted with padded columns by an editor;
  use `out/link_results_clean.csv`.
- Link results are not yet part of the score.

## Limits
- Accuracy is not scored yet: link results exist but are not in the score, and no numeric or range checks exist.
- Credibility uses offline signals only, and source trust is flat at 0.7, so it says little about source quality.
- Relevance cut-offs and publish/review thresholds are untuned. There is no labeled data; the 3 approved and 1
  disapproved records are too few to calibrate.
