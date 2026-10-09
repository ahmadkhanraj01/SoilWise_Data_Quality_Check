# Next steps (deferred)

Status as of 2026-10-08. Nothing here is in progress.

## 0. Ready to send / waiting on people
- `out/labeling_sample.xlsx`: 60 blind records for a domain expert (relevant? publishable?). When labels return,
  write the calibration script: compare labels with decisions, report precision/recall, propose cut-offs.
- `docs/TEAM_QUESTIONS.md` to the team and `docs/HARVESTER_TICKETS.md` to the harvester owners.
- Done in run4: accuracy is penalty-only; thin-text records get relevance "unknown" (see FINDINGS.md). Open: the
  5 remaining openaire rejects are rejected on thin metadata alone; consider rejecting only when off-topic or duplicate.
- Draft the `qc` schema SQL and a dry-run loader (nothing written to the database).

## 1. Link check: decoded second pass (sample done)

**Done 2026-10-09:** a 3,000-URL host-spread sample was run (`python -m qc.linkcheck_decoded --sample 3000`). Decoding
fixes the defect; about 82% of decoded links work (rough estimate), and one host, geoportale.lamma.rete.toscana.it,
is dead for 1,718 URLs. See `docs/FINDINGS.md`. The full pass (below) is optional: run it only after the harvester
fix lands, or if per-record link scores are needed.

**Original plan (for the full run):**

**Why:** 33,844 of 56,721 URLs (all from `distributions.access_url`) are fully percent-encoded
(`https%3A%2F%2F...`), so the first pass marked them `invalid` without testing them. We do not yet know
whether they work once decoded.

**Plan**
1. Decode each `invalid` URL once (`urllib.parse.unquote`) and keep only those that become valid http/https URLs.
2. Run a **sample first**: about 3,000 URLs spread across hosts (not the first 3,000, which would all be bonares).
   Roughly 10 minutes. This tells us if decoding fixes them and which hosts fail.
3. Decide on the **full run** (about 34k URLs, an estimated 1 to 1.5 hours because of the 2-per-host limit).
   Run it overnight if needed. The checker is resumable.
4. Record results in a separate file (for example `out/link_results_decoded.csv`) with an `encoded_url`
   marker, so the harvester defect stays visible even where the decoded link works.

**Code changes needed in `qc/linkcheck.py`:** a `--decoded` mode (or a pre-step) that unquotes URLs, plus a
`--sample N --spread-by-host` option. When reading the output file, trim cells and open with `newline=""`.

**Inputs already available:** `out/link_results_clean.csv` (first pass, cleaned). Use this one, not
`out/link_results.csv`, which an editor padded with spaces.

## 2. First-pass link results to review (retry done)

**Done 2026-10-09:** the timeouts were retried at 30 s. 85 of 101 hosts stayed unresponsive (1,147 of 1,183 timeouts),
including maps.bonares.de (836). Next: confirm bonares and the Sardinian/Walloon servers from another network or with
the owners, since a blocked IP looks the same as a dead host. See `docs/FINDINGS.md`.

**Original notes:**

Of 22,872 checkable URLs: 21,196 ok (92.7%), 868 timeout, 584 client error, 78 broken, 78 restricted,
49 connect error, 14 DNS error.
- Failures cluster on `maps.bonares.de` (822), `ec.europa.eu` (547), `hdl.handle.net` (48).
- Check what the errors really are on those hosts before calling links dead. Retry the timeouts with a longer limit
  (try `--timeout 30`) to separate slow servers from dead ones.
- DOIs are healthy (14 failures).

## 3. Add link results to the score (accuracy dimension) — DONE in run5
Implemented in `qc/linkscore.py` and `qc/checks/accuracy.py`; the text below is the original plan. Still open: full decoded pass after the harvester fix, and making `broken_link` a major flag.
Treat an unconfirmed timeout as unknown, not failed, until the dead-host question above is settled.
Map per-record link results to a 0..1 accuracy score (share of a record's links that are ok; treat `restricted`
and `timeout` as unknown, not failed). Add weight 0.10 to `config.WEIGHTS` and renormalise. Also include the
percent-encoded defect as a flag.

## 4. Decisions needed from the team
- Is food and livestock content in scope for the Knowledge Hub? (affects eufarmbook, 12% flagged off-topic)
- Who can label about 50 records as relevant or not, to tune the relevance cut-offs and publish/review thresholds?
- Which sources are trusted? `SOURCE_TRUST` in `config.py` is flat at 0.7.
- Where do results go: `approval_status`, a separate `qc` schema, or CSV only?

## 5. Harvester tickets (from the data, not code)
- Percent-encoded `distributions.access_url` (about 34k rows).
- License missing in 82-100% of records in 12 of 14 sources.
- impact4soil, prepsoil, islandr: authors, keywords and dates missing systematically.
- eufarmbook: keywords and dates. data.europa.eu: dates. fao: URL. ngr: URL and keywords.
Evidence: `out/source_gaps.md`.

## 6. Docs to update when work resumes
- `qc/README.md` and root `README.md`: mark accuracy done once step 3 is finished.
- `docs/FINDINGS.md`: add the decoded-pass results.

## 7. Later
Reviewer queue and decision storage, an alert if a normally complete source suddenly gains a systemic gap,
and a scheduled rerun.
