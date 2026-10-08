# Questions for the team

Context: an automated quality check now scores all 25,129 records in `validate.records` on completeness,
consistency, credibility, relevance and (partly) accuracy. Four decisions only the team can make are blocking
further improvement. Results so far: `docs/FINDINGS.md`.

## 1. Scope: is food and livestock content in the Knowledge Hub?
Records on livestock, poultry, animal breeding and food traceability (mostly from eufarmbook) are flagged as
off-topic for soil/land/agriculture: 169 records, 12% of eufarmbook.
- **Yes, in scope:** we add livestock and food terms to the topic profile and those records pass.
- **No, out of scope:** the flags are correct and the records should be reviewed or removed.

## 2. Labeled sample for calibration
Relevance cut-offs and the publish/review/reject thresholds are my guesses. To tune them we need about
50 records labeled by someone who knows the domain: relevant / not relevant (and ideally good / poor metadata).
I can export a stratified sample (mix of sources, resource types and score bands) as a spreadsheet for this.
Who can do the labeling, and how long would it take?

## 3. Trusted sources
Credibility currently treats all 14 sources equally (trust 0.7). The sources are impact4soil, openaire,
data.europa.eu, cordis, eufarmbook, inspire, bonares, fao, ejpsoil, eea, prepsoil, isric, islandr, ngr.
Please give a trust level (high / medium / low) per source, or tell me who decides.

## 4. Where should results go?
Options: (a) CSV only, as now; (b) write the decision to `approval_status` (currently 25,125 pending, 3 approved,
1 disapproved); (c) a separate `qc` schema with score and reason tables, leaving `approval_status` untouched.
My recommendation is (c) first, so nothing changes the live status until the thresholds are calibrated.
Does the pipeline have write access to this database, and who reviews the "review" list?

## Also for the harvester owners
See `docs/HARVESTER_TICKETS.md`.
