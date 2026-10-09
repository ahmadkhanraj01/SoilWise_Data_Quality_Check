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

## Accuracy check and run3 (current results)
`qc/checks/accuracy.py` validates the `spatial` WKT polygon: parseable, coordinates in range, ring closed, non-zero
extent. It applies only to the 4,857 records that have a spatial value (19%); other records are scored without it.
Weights (renormalised per record): completeness 0.25, consistency 0.20, credibility 0.20, relevance 0.25, accuracy 0.10.

**Decisions (run3):** publish 20,597 (82%) / review 4,515 (18%) / reject 17.
Previous run (relevance, no accuracy): 20,471 / 4,641 / 17.

| Source | Records | Publish | Review | Reject |
|---|---|---|---|---|
| impact4soil | 9,281 | 8,938 | 343 | 0 |
| openaire | 6,359 | 4,103 | 2,239 | 17 |
| data.europa.eu | 2,150 | 1,668 | 482 | 0 |
| cordis | 1,411 | 992 | 419 | 0 |
| eufarmbook | 1,362 | 1,155 | 207 | 0 |
| bonares | 1,303 | 1,201 | 102 | 0 |
| fao | 1,014 | 700 | 314 | 0 |
| inspire | 999 | 914 | 85 | 0 |
| ejpsoil | 618 | 412 | 206 | 0 |
| eea | 276 | 257 | 19 | 0 |
| prepsoil | 245 | 154 | 91 | 0 |
| islandr | 98 | 91 | 7 | 0 |
| ngr | 12 | 11 | 1 | 0 |
| isric | 1 | 1 | 0 | 0 |

Mean scores: completeness 0.903, consistency 0.986, credibility 0.768, relevance 0.685, accuracy 0.991
(4,857 records), overall 0.834. Relevance is the weakest dimension.

Most common flags: no license 6,282; no keywords 5,205; abstract_short 4,885; weak_topic_match 3,043;
no author or organization 2,458; no dates 2,056; possibly_off_topic 1,830; abstract_very_short 986; no url 978.
Records in review with a major flag: 1,814 possibly off-topic and 973 with a near-empty abstract; the rest are
borderline scores.

**Accuracy findings**
- 4,705 of 4,857 spatial records score 1.0 (mean 0.991). No out-of-range coordinates, unparseable geometry or
  unclosed rings were found.
- 152 records have a zero-extent polygon (`degenerate_extent`: a point or line, not an area): 149 from bonares and
  3 from data.europa.eu. A small data defect to raise with bonares.
- The accuracy check changed 132 decisions (129 review to publish, 3 publish to review); the largest score change
  was 0.097. Most of these moves are an artifact: a perfect accuracy score lifts borderline averages just over
  0.75, which is the cost of scoring one dimension for only 19% of records. Making accuracy a penalty-only
  component is an option.

**Rejected records:** all 17 are openaire project deliverables with generic titles ("METK Case Study", "WP3 Report",
"Video", "Final event", "Social media accounts"), scores 0.26 to 0.40. They may be valid project outputs with poor
metadata, so a human should look before rejecting.

**Notes**
- Source counts in this table differ from the earlier tables (e.g. impact4soil 9,281 vs 9,337; inspire 999 vs
  1,313). The faster records query assigns each record to one source (first alphabetically); the earlier query
  picked one arbitrarily for records in several sources. The total is unchanged at 25,129.
- The previous run is saved as `out/qc_results_pre_accuracy.csv`. The runner now writes results to a temp file and
  swaps it in, so a crash cannot destroy previous output.

## Link check: decoded sample (percent-encoded URLs)
All 33,844 percent-encoded URLs decode once into valid http(s) URLs (816 hosts; 16,367 are `doi.org`). A sample of 3,000,
spread round-robin across all 816 hosts (`qc/linkcheck_decoded.py`, `out/link_results_decoded.csv`), gave:
ok 1,939 / timeout 315 / broken 217 / client_error 166 / server_error 101 / restricted 111 / connect_error 72 /
dns_error 57 / error 22. That is 64.6% ok, but the sample is host-balanced, not representative of the URL population.
Weighting each result by its host's share of the 33,844 gives a rough estimate: **about 82% ok, 7% broken,
6% timeout, 3% client error**. Treat it as indicative only (hosts with few URLs carry large uncertainty).
- **Decoding fixes the defect:** the links work once decoded, so the harvester ticket is a pure encoding bug.
- **One dead host:** `geoportale.lamma.rete.toscana.it` accounts for 1,718 URLs (5% of the encoded set) and all 14
  sampled URLs were broken. 17 hosts failed completely in the sample (~1,837 URLs in total); others are
  `wms.mapama.gob.es`, `rkh.apps.fao.org`, `dados.gov.pt`, `www.lgl-bw.de`, `www.hlnug.de`.
- The full 34k-URL decoded pass was not run; the sample answers the question. Re-run after the harvester fix.

## Link check: timeout retry (30 s)
`qc/linkcheck_retry.py` retried the 1,183 URLs that timed out in the two passes (101 hosts), at most 25 per host, with a
30 second limit (`out/link_results_retry.csv`). Of 372 retried: 319 still time out, 30 ok, 17 connect errors, 2 broken,
1 server error, 1 client error, 2 other errors.
- **Mostly dead or unresponsive, not slow:** 85 of 101 hosts recovered nothing (1,147 of the 1,183 timeouts). Only
  15 hosts recovered (28 timeouts), e.g. registry.gdi-de.org, eufarmbook.eu; hdl.handle.net was mixed (2 of 8 ok).
- **maps.bonares.de** accounts for 836 of the 1,183 timeouts and all 25 retried URLs timed out again.
  Other fully unresponsive hosts: webgis.regione.sardegna.it, webgis2.regione.sardegna.it, geoservices.wallonie.be,
  www.avepa.it, gaia.arpa.veneto.it.
- **Caveat:** these checks ran from one machine and network. A host that blocks or firewalls this IP looks the same as
  a dead host. Confirm the biggest ones (bonares first) from another network or with the data owners before calling
  them dead.

## Run4: penalty-only accuracy and thin-text relevance (current results)
Two scoring fixes after run3:
- **Thin text:** records with under 50 characters of abstract and no keywords (586 records, mostly openaire 326 and
  fao 177) can't be judged by an embedding ("Video", "Website"). Relevance is now marked unknown for them
  (`relevance_unknown_thin_text`) and left out of the average instead of being flagged off-topic. Off-topic flags
  fell from 1,830 to 1,568.
- **Accuracy is penalty-only:** it can lower a score but a pass adds nothing. This reverses run3's artifact: all
  171 publish-to-review moves versus run3 are records with a spatial value that lost the lift of a perfect score.

**Decisions (run4):** publish 20,426 / review 4,698 / reject 5 (run3: 20,597 / 4,515 / 17). Versus the pre-accuracy
run only 57 decisions differ (the accuracy penalty on 152 degenerate polygons, and thin-text records).
Of the 586 thin-text records, 585 go to review. Twelve of the 17 run3 rejects moved to review.
The 5 remaining rejects (openaire: "WP3 Report", "Social media accounts", "Articles and presentations", "Video",
"Promotional Package M06") are rejected on weak completeness and credibility alone, with no positive evidence of
bad content. Option: reject only when off-topic or duplicate, otherwise review.

**Run5 (link results in accuracy):** publish 20,380 / review 4,744 / reject 5. Accuracy now also uses link evidence
(`qc/linkscore.py`): share of definitive answers (ok vs broken) per record; timeouts, restricted and invalid URLs are
unknown. 24,159 records (96%) have an accuracy score (mean 0.991); 201 carry `broken_link`, and 46 moved from
publish to review versus run4.

## Limits
- Accuracy covers spatial plausibility (19% of records) plus link liveness where the check has a definitive answer.
  The 33,844 percent-encoded URLs count as unknown except the 3,000-URL decoded sample.
- Credibility uses offline signals only, and source trust is flat at 0.7, so it says little about source quality.
- Relevance cut-offs and publish/review thresholds are untuned. There is no labeled data; the 3 approved and 1
  disapproved records are too few to calibrate.
