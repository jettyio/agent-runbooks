# anthropics/pdf — demo payload

A **self-contained launch payload** for the `anthropics/pdf` runbook: the runbook
itself, three worked examples (real input PDF + real Jetty outputs), thumbnails, and a
`manifest.json` describing it so the public runbook directory can render a
"try-this / here's-what-you-get" page (per the detail-view mockup).

```
pdf/
  RUNBOOK.md                              # the runbook (v1.2.1)
  manifest.json                           # directory metadata: cta, example_outputs[], inputs[], secrets[], meta
  README.md                               # this file
  examples/
    pubmed-tables-to-json/                # EXAMPLE 1 — extract
      input.pdf                           #   shared input: a 20-page PLOS Medicine article (CC BY 4.0)
      input.json  trajectory.json  thumbnail.png
      expected/  extracted_tables.json (primary) · .xlsx · extracted_text.txt · summary.md · validation_report.json
    watermark-confidential/               # EXAMPLE 2 — modify
      input.json  trajectory.json  thumbnail.png
      expected/  output.pdf (primary) · summary.md · validation_report.json
    create-summary-pdf/                   # EXAMPLE 3 — author
      input.json  trajectory.json  thumbnail.png
      expected/  output.pdf (primary) · summary.md · validation_report.json
```

## The gallery: one PDF, three capabilities (extract → modify → author)

All three examples run against the same CC BY 4.0 source PDF — *Evaluation of the
sugar-sweetened beverage tax in Oakland* (White et al., **PLOS Medicine 20(4): e1004212,
2023**, [doi:10.1371/journal.pmed.1004212](https://doi.org/10.1371/journal.pmed.1004212)).

| # | Capability | Operation | Output | Trajectory | Eval |
|---|-----------|-----------|--------|-----------|------|
| 1 | **Extract** | `extract-tables` | `extracted_tables.json` — every table as strict JSON | `6c756bcf` | 7/7 ✓ |
| 2 | **Modify** | `watermark` | `output.pdf` — every page stamped CONFIDENTIAL | `0e7dcb7b` | 4/4 ✓ |
| 3 | **Author** | `create` | `output.pdf` — a new one-page Document Summary | `7f700569` | 5/5 ✓ |

The hero (example 1) turns a messy two-column research PDF into clean structured data.
The cleanest table (page 9) reads verbatim from `expected/extracted_tables.json`:

```json
{
  "source_page": 9,
  "headers": ["No. UPCs", "Adjusted Difference-in-Differences Model", "col_2"],
  "rows": [
    { "No. UPCs": "3,451", "Adjusted Difference-in-Differences Model": "−452.20 (−656.67 to −247.73)", "col_2": "<0.001" }
  ]
}
```

## What changed (vs the imported v1.0.x), all driven by real runs

- **v1.1.0 — strictly-valid JSON + primary file.** The original run emitted literal
  `NaN` (invalid JSON); v1.1.0 maps blanks/`NaN` → `null` with `allow_nan=False`, lowers
  the text tolerance to recover word spacing (`"Numberofstores"` → `"Number of stores"`),
  prunes blank rows/cols, and declares operation-aware `primary_outputs` (surfaces
  `extracted_tables.json` / `output.pdf` / `extracted_text.txt` as `primary_files`).
- **v1.2.0 — operation routing.** The original runbook's blanket "MANDATORY outputs"
  block forced text+table extraction on *every* run, so the `operation` parameter was
  silently ignored (a `watermark` request still produced table files). v1.2.0 makes the
  required outputs **operation-conditional** and states the requested operation
  imperatively (`{{operation}}`), so the agent runs only the chosen operation and emits
  only its deliverables. Verified: the watermark/create runs produce *only* `output.pdf`.
- **v1.2.1 — visible watermark.** Bumped the watermark to a bold diagonal red overlay so
  it's legible at any zoom (the v1.2.0 watermark was applied but near-invisible).

## Reproduce (example 1)

```bash
# from repo root, with JETTY_API_TOKEN_JON_RUNBOOKS in .env
TOKEN="$(grep '^JETTY_API_TOKEN_JON_RUNBOOKS=' .env | cut -d= -f2-)"
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  --form-string 'init_params={"vars":{"operation":"extract every table into JSON"}}' \
  -F "files=@runbooks/anthropics/pdf/examples/pubmed-tables-to-json/input.pdf" \
  "https://flows-api.jetty.io/api/v1/run/jon-runbooks/pdf-amber-hawk"
```

> Use `--form-string` (not `-F`) for `init_params` — curl's `-F` treats `;` in the value
> as a parameter separator and truncates the JSON.

## Known follow-ups

- The **directory site doesn't ingest this yet** — `runbooks-directory` reads only
  `RUNBOOK.md`; rendering the `example_outputs` gallery + `inputs`/`secrets` from
  `manifest.json` needs an ingest + detail-page change.
- For the directory's **Operation input** to drive real runs end-to-end, the chosen
  operation must reach the agent (it's injected into the runbook body here); confirm the
  run plumbing forwards it for forked users.
- More demo ideas (gov-form extract, scanned OCR, merge, figure extraction) are listed in
  `manifest.json` → `demo_ideas`.
