# ClinicalTrials.gov condition search extraction (Jetty runbook)

**Search ClinicalTrials.gov for a condition and a posting window, then read seven fields
off each study's own page — verbatim.** The API is used only to build the candidate NCT
list; every value in the spreadsheet comes from the rendered study page (Playwright/Chromium),
exactly as displayed, with `Not found` for anything genuinely absent. A full provenance
trail (`extraction_audit.json`) shows why any candidate was dropped or excluded, so no value
can be silently fabricated or backfilled.

## Flow

1. **Candidates** — ClinicalTrials.gov API v2, paginated, filtered on *First Posted*;
   sanity-check that each candidate's condition list plausibly references the condition.
2. **Extract** — open `https://clinicaltrials.gov/study/{NCT}` in a real browser and copy
   Study Title, NCT Number, Study URL, Study Status, Enrollment size, Study Type, Start Date.
3. **Evaluate** — PASS / PARTIAL / FAIL per row; up to 3 retry rounds.
4. **Audit + report** — `extraction_audit.json`, `summary.md`, `validation_report.json`.

## Deliverables (`{{results_dir}}/`)

| File | What |
|------|------|
| `studies.csv` | One row per study, 7 columns, values verbatim from the page |
| `extraction_audit.json` | `candidates`, `dropped`, `excluded`, and per-row extraction detail |
| `summary.md` | Counts, exclusions, sample rows, recommendations |
| `validation_report.json` | Stage results, per-status counts, `overall_passed` |

## Parameters

`condition` (verbatim, no synonyms) · `posted_from` · `posted_to` (YYYY-MM-DD, inclusive).

## Examples

See `examples/` — real runs on Jetty with inputs, `expected/` outputs, `trajectory.json`,
and a thumbnail. Study pages are a client-rendered SPA; this runbook needs the
`prism-playwright` snapshot, not a plain HTTP fetch.
