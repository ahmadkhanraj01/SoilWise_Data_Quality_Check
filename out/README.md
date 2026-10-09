# out

Generated results. Safe to delete and regenerate; nothing here is read back by the database.
(`out/` is git-ignored except this README.)

| File | Produced by | Contents |
|---|---|---|
| `qc_results.csv` | `python -m qc.runner` | One row per record (see columns below) |
| `qc_results_baseline.csv` | manual copy | Run before source-aware scoring, for comparison |
| `source_gaps.md` | `python -m qc.source_report` | Per-source % of records missing each field, with systemic gaps |
| `link_results.csv` | `python -m qc.linkcheck` | `url, record_id, result, status, final_url`; resumable |
| `link_results_v1.csv` | superseded | First link-check test, before the DOI handle-API change |
| `labeling_sample.xlsx` | `python -m qc.export_labeling` | Blind 60-record sample for domain-expert labeling (sheets: Instructions, Label, Key) |
| `qc_results_run3.csv` | manual copy | Run3 results (accuracy as a weighted dimension), before run4 |
| `records_cache.pkl` | `qc.runner` | Cached DB fetch for `--cached` reruns |
| `qc_results_pre_accuracy.csv` | manual copy | Run before the accuracy check, for comparison |
| `link_results_decoded.csv` | `python -m qc.linkcheck_decoded` | `encoded_url, decoded_url, record_id, result, status, final_url`; the 3,000-URL decoded sample |
| `link_results_retry.csv` | `python -m qc.linkcheck_retry` | Timeouts retried at 30 s, max 25 per host: `url, record_id, source_file, result, status, final_url` |
| `link_results_clean.csv` | cleaned copy | First-pass link results with trimmed cells; use this one |
| `emb_cache.npz` | relevance check | Cached embeddings, keyed by text hash |
| `run*.log`, `linkcheck.log` | background runs | Progress logs |

## qc_results.csv columns

| Column | Meaning |
|---|---|
| `id`, `identifier`, `title`, `source`, `resource_type` | Record identity (title truncated to 120 chars) |
| `current_status` | `approval_status` currently in the database |
| `overall` | Weighted score 0..1 |
| `decision` | `publish`, `review` or `reject` |
| `completeness`, `consistency`, `credibility`, `relevance` | Dimension scores 0..1 |
| `accuracy` | Spatial plausibility score; empty for records with no spatial value |
| `rel_sim`, `kw_hits` | Raw embedding similarity and keyword hit count |
| `waived` | Fields not penalised because they are systemic gaps for the record's source |
| `flags` | All flags raised (minor and major) |
| `major` | Major flags only; any of these prevents automatic publish |

## link_results.csv `result` values
`ok`, `broken` (404/410 or unregistered DOI), `restricted` (401/403/405/429: reachable, not proof of a dead
link), `client_error`, `server_error`, `timeout`, `dns_error`, `connect_error`, `error`,
`invalid` (not a usable http/https URL, e.g. percent-encoded).
