# Harvester tickets (drafts)

Evidence: `out/source_gaps.md`, `docs/FINDINGS.md`. Counts are from the `validate` schema on 2026-10-08.

## T1. Percent-encoded `distributions.access_url` (high)
- **Problem:** about 33,844 of 56,721 checked links (mostly `distributions.access_url`) are stored fully
  percent-encoded, e.g. `https%3A%2F%2Fmaps.bonares.de%2F...`. They have no scheme as stored and cannot be opened.
  Looks like a URL encoded twice during harvest or ingest.
- **Seen in:** at least bonares, fao, dov.vlaanderen.be endpoints (not yet broken down per source).
- **Ask:** find where the value is encoded; fix the harvester; repair existing rows with a single decode.
- **Verified by sample:** the 33,844 URLs all decode (single `unquote`) into valid http(s) URLs, and about 82% of them
  work once decoded (rough estimate from a 3,000-URL sample). Nearly half (16,367) are `doi.org` DOIs.
- **Check after fix:** the number of `access_url` values not starting with `http` should be 0.

## T2. License missing almost everywhere (high)
- **Problem:** license is empty in 77.5% of all records. Per source, 82-100% missing in 12 of 14 sources
  (impact4soil 96%, data.europa.eu 99%, eufarmbook, inspire, bonares, fao, eea, ngr, isric, islandr 100%,
  prepsoil 95%, ejpsoil 82%). Only openaire (32%) and cordis (45%) mostly carry it.
- **Ask:** check whether the source metadata provides a license/rights field that the harvester drops, and
  extend the mapping. If a source does not provide one, record that so it is not counted as a defect.

## T3. impact4soil: authors, keywords, dates (medium)
- **Problem:** in 9,337 records, missing person/organization 92%, keywords 95%, all dates 92%.
- **Ask:** check the source mapping for creators, subjects and publication dates.

## T4. prepsoil and islandr: authors and dates (medium)
- prepsoil (264 records): person/org 91%, dates 93% missing. islandr (98 records): person/org 99%, dates 94% missing.

## T5. Other source-specific gaps (medium/low)
| Source | Missing | Rate |
|---|---|---|
| eufarmbook | keywords, dates | 100% |
| data.europa.eu | dates | 98% |
| fao | url | 100% |
| ngr | url, keywords | 83%, 100% |
| inspire | url | 43% |
| bonares | keywords | 77% |

## T6. Link reliability (low)
Update: a 30 s retry showed 85 of 101 timing-out hosts stay unresponsive, so these are mostly dead or blocked
services, not slow ones. maps.bonares.de accounts for 836 of 1,183 timeouts; confirm with the data owner.

Of 22,872 testable URLs, 868 timed out and 584 returned client errors, concentrated on maps.bonares.de (822
failures) and ec.europa.eu (547). Needs a retry with a longer timeout before treating these as dead.

## T6b. Dead host: geoportale.lamma.rete.toscana.it (medium)
1,718 distribution URLs point to this host and every sampled URL (14 of 14) is broken. Ask whether the service moved
or was retired, and update or remove the links.

## T7. Data hygiene (low)
- 42 records have a publication date in the future; 78 have creation after publication; 2 have temporal end before start.
- 205 groups of records share a title; 122 groups share a URL.
- 986 abstracts are under 50 characters.
