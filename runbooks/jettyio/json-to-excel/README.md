# jettyio/json-to-excel — demo payload

A launch payload for the `jettyio/json-to-excel` runbook: the runbook, a `manifest.json`,
and three worked examples — each a real production run that fills an Excel template from a
JSON of values **without ever clobbering a label or a formula**.

```
json-to-excel/
  RUNBOOK.md                        # the runbook (v1.0.0)
  manifest.json                     # directory metadata: cta, example_outputs[], inputs[], secrets[], meta
  README.md                         # this file
  examples/
    budget-fy2026/                  # finance — match_label + header-keyed values
      template.xlsx  data.json  input.json  trajectory.json  thumbnail.png
      expected/  filled_workbook.xlsx (primary) · placement_report.json · summary.md · validation_report.json
    price-list-order/               # procurement — table_range + rows
      template.xlsx  data.json  input.json  trajectory.json  thumbnail.png  expected/ …
    project-status/                 # project mgmt — match_label + dropdown + percent + text
      template.xlsx  data.json  input.json  trajectory.json  thumbnail.png  expected/ …
```

## What it is

A **domain-agnostic Excel template filler**, generalized from the internal
`governgpt` due-diligence-questionnaire runbook into a reusable engine. Given an empty
`.xlsx` whose cells already carry the document's structure (section labels, column
headers, row labels) plus placeholder cells, and a JSON describing the values, it writes
each value into its correct cell — preserving every structural label, merged cell, and
formula, coercing values by the destination cell's `number_format`, and handling overflow.

The proprietary due-diligence specifics (GovernGPT editor markers, the Aksia/Swiss
examples, the questionnaire framing) were stripped; the reusable engine was kept: label
preservation, placeholder/label classification, Jaccard label/header matching,
`number_format`-aware coercion, overflow `alert`/`insert`, and the label-preservation +
dimension audit gates.

## The gallery: three analogs, three targeting modes

| # | Example | Domain | Targeting mode | Exercises | Trajectory |
|---|---------|--------|----------------|-----------|-----------|
| 1 | **Department budget** | Finance / FP&A | `match_label` + header-keyed values | label/section/formula preservation, money cells | `4fa49a03` |
| 2 | **Purchase order** | Procurement | `table_range` + rows | table fill under a header, `C*D`/`SUM()` formula preservation | `48359a63` |
| 3 | **Weekly status report** | Project mgmt | `match_label` + values | data-validation **dropdown**, **percent** number_format, free text | `bc354d46` |

Each `expected/filled_workbook.xlsx` is the headline deliverable; thumbnails are rendered
from the filled workbook. Inputs are **synthetic samples** (safe to ship) chosen to
exercise the engine — they are deliberately *not* the GovernGPT due-diligence example.

## Why these inputs are good tests

- **Budget** — section labels (`Personnel`, `Operations`), row labels (`Salaries`), and
  `FY Total = SUM()` formulas must survive; only the `TBD` quarter cells are writable.
  Verified: dimensions unchanged, **0 labels/formulas clobbered**, all 36 figures placed.
- **Purchase order** — the `Line Total = C*D` and `Subtotal = SUM()` formulas must not be
  overwritten when the product rows are written into the line-item range.
- **Status report** — the RAG column is a real `DataValidation` dropdown (`please select`),
  `% Complete` is a percent-formatted cell (`X%`), and `Update` is a `[Leave blank]` text
  cell — three different placeholder/coercion paths in one fill.

## Reproduce (example 1)

```bash
TOKEN="$(grep '^JETTY_API_TOKEN_JON_RUNBOOKS=' .env | cut -d= -f2-)"
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  --form-string 'init_params={"vars":{"output_basename":"budget-fy2026","overflow_strategy":"alert"}}' \
  -F "files=@runbooks/jettyio/json-to-excel/examples/budget-fy2026/template.xlsx" \
  -F "files=@runbooks/jettyio/json-to-excel/examples/budget-fy2026/data.json" \
  "https://flows-api.jetty.io/api/v1/run/jon-runbooks/json-to-excel"
```
