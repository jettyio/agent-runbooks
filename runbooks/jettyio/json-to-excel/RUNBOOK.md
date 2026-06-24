---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
model_provider: anthropic
snapshot: python312-uv-office
# The headline deliverable — the filled workbook.
primary_outputs:
  - filled_workbook.xlsx
secrets: {}
---

# JSON → Excel — Template Filler Runbook

> **EXECUTE THIS RUNBOOK NOW.** Work through the steps in order with tools, writing
> every deliverable to `{{results_dir}}`. This is a task to perform, not a document to
> summarize. Your first action is a tool call (Step 1). The inputs are already provided
> below — never pause to ask the user for them.

## Inputs (already provided)

- **Template workbook:** the first `*.xlsx` uploaded into `/app/assets/` (an EMPTY
  template with labels, headers, and placeholder cells).
- **Fill data:** the first `*.json` uploaded into `/app/assets/` (the values to insert).
- **Notes (optional):** the first `*.md` uploaded into `/app/assets/`, if any.
- **Output basename:** {{output_basename}} · **Overflow strategy:** {{overflow_strategy}}

## Objective

Given (a) an **empty** Excel template (`.xlsx`) whose cells already carry the document's
structure — section labels, column headers, row labels — and placeholder cells for the
data, and (b) a **JSON** file describing the values to insert, produce a **filled** copy
of the template that writes every value into its correct cell **without ever overwriting
a structural label or a formula**. The filler must:

1. **Preserve every structural label and formula** already in the template. Only
   *placeholder* cells (empty, `TBD`, `XX%`, `[Leave blank]`, dropdown prompts, checkbox
   lists) are writable. Labels are sacred.
2. **Match each fill to its destination** by one of three targeting modes (see Input
   Contract): explicit `cell`, a `match_label` (find the row/label and write to the
   adjacent placeholder, or to the column whose header matches each value key), or a
   `table_range` + `rows` (write a table's data rows under the existing header).
3. **Coerce values by the destination cell's `number_format`**, not by their surface
   form (a percent cell gets a float; a text cell keeps the string).
4. Preserve structure, styling, formulas, and merged cells.
5. **Detect and handle overflow** — more data rows than placeholder rows — via the
   configured strategy (`alert` / `insert` / `both`).
6. Tolerate missing/blank values; record everything dropped or skipped for auditability.

This is the domain-agnostic engine behind any "fill an Excel template from structured
data" task — budgets, price lists, status reports, scorecards, intake forms, etc.

---

## Parameter precedence (read first)

**Explicit run parameters win over hints in the notes file.** If the user passes
`overflow_strategy=alert`, use alert mode even if the notes say "insert new rows". The
notes file is consulted only for: which fills are intentionally blank, dropdown/validation
caveats, sheets to delete, and anything that does NOT correspond to a parameter already
set. Surface any tension in `summary.md` under "Recommendations" — never silently
override a parameter.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following to `{{results_dir}}`. The task is NOT complete
until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `{{results_dir}}/filled_workbook.xlsx` | The filled workbook — same sheets and dimensions as the template (plus inserted rows when `overflow_strategy=insert`), original styling/formulas preserved, values populated. |
| `{{results_dir}}/overflow_report.json` | Per-fill record of overflow events (answer larger than its range), the strategy used, and where alerts/inserted rows live. May be `[]`. |
| `{{results_dir}}/skipped_fills.json` | Fills with empty/missing values or whose destination was a label (intentionally not written), keyed for traceability. May be `[]`. |
| `{{results_dir}}/placement_report.json` | One record per fill: target, status, cells written, labels preserved, match score. |
| `{{results_dir}}/summary.md` | Executive summary: counts placed/skipped/overflowed, sheets touched, parameter values, issues. |
| `{{results_dir}}/validation_report.json` | Stage-by-stage validation with `overall_passed`. See Step 8. |

If you finish your analysis but have not written all files, go back and write them first.

---

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|------------------|---------|-------------|
| Results directory | `{{results_dir}}` | `/app/results` | Output directory for all results |
| Template workbook | *(uploaded)* | first `*.xlsx` in `/app/assets/` | The empty `.xlsx` template |
| Fill data | *(uploaded)* | first `*.json` in `/app/assets/` | The JSON of values to insert |
| Notes | *(uploaded, optional)* | first `*.md` in `/app/assets/` | User notes — intentional blanks, dropdown caveats, sheets to drop |
| Output basename | `{{output_basename}}` | `workbook` | Names the filled file (`FILLED_<basename>.xlsx`) |
| Overflow strategy | `{{overflow_strategy}}` | `alert` | `alert` (truncate + flag), `insert` (add rows/cols), or `both` |
| Max overflow inserts | `{{max_overflow_inserts}}` | `50` | Cap on inserted rows/cols per table before falling back to `alert` |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `openpyxl` | Python package | Yes | Read/write `.xlsx` preserving styles, merged cells, comments, formulas |
| `beautifulsoup4` | Python package | Optional | Parse `value_html` when a fill carries rich text/HTML |
| `lxml` | Python package | Optional | Faster HTML parser backend for BeautifulSoup |

---

## Input Data Contract

The fill data JSON is an object with a `fills` array. Each fill targets a destination in
one of three ways and carries a value:

```json
{
  "fills": [
    { "sheet": "Budget", "match_label": "Salaries", "values": { "Q1": 120000, "Q2": 120000, "Q3": 126000, "Q4": 126000 } },
    { "sheet": "Budget", "cell": "E4", "value": "Acme Corp" },
    { "sheet": "Budget", "match_label": "Executive Summary", "value": "Long free-text answer…" },
    { "sheet": "Inventory", "table_range": ["B10", "E14"], "header": ["Item","Qty","Unit Price","Total"],
      "rows": [["Widget", 3, "$10.00", "$30.00"], ["Gadget", 5, "$8.50", "$42.50"]] }
  ]
}
```

Targeting modes (a fill uses exactly one):

- **`cell`** — write `value` directly into that single cell (after placeholder/label check).
- **`match_label`** + **`values`** (object keyed by column header) — find the row whose
  column-0 (or any) label best matches `match_label`; for each `values` key, find the
  column whose header matches the key, and write into the placeholder cell at
  (matched-row, matched-column).
- **`match_label`** + **`value`** (single string) — find the label cell, then write
  `value` into the first placeholder cell to its right (extend-right, up to +8 columns).
- **`table_range`** + **`rows`** (+ optional **`header`**) — write the table's data rows
  into the range, preserving any existing header row and aligning columns by header match.

Optional per-fill keys: `value_html` (rich text — strip wrapper tags, keep inner text),
`number_format` (force a format), `note` (provenance, never written into a cell).
A fill with empty/`null`/whitespace value is intentionally blank → record in
`skipped_fills.json`, write nothing.

---

## Step 1: Environment Setup

```bash
python -m pip install --quiet openpyxl beautifulsoup4 lxml
mkdir -p "{{results_dir}}"

# Resolve inputs from /app/assets (uploaded files land there)
TEMPLATE="$(ls /app/assets/*.xlsx 2>/dev/null | head -1)"
DATA="$(ls /app/assets/*.json 2>/dev/null | head -1)"
NOTES="$(ls /app/assets/*.md 2>/dev/null | head -1)"
echo "template=$TEMPLATE"; echo "data=$DATA"; echo "notes=${NOTES:-<none>}"
[ -s "$TEMPLATE" ] || { echo "ERROR: no template .xlsx in /app/assets"; exit 1; }
[ -s "$DATA" ]     || { echo "ERROR: no data .json in /app/assets"; exit 1; }
```

---

## Step 2: Read & Apply Notes (if present)

If a notes `.md` exists, read it **before** touching the workbook and extract structured
rules: intentional blanks, dropdown/validation caveats (write only an accepted option,
drop free text), sheets to delete from the final export, and any per-cell quirks. Persist
the extracted rules to `{{results_dir}}/notes_applied.json` so the trajectory shows what
you actually applied. Remember: notes never override an explicit run parameter.

---

## Step 3: Load & Classify — build the placement plan

1. `wb = openpyxl.load_workbook(TEMPLATE)` — keep formulas (`data_only=False`).
2. Load the fill data JSON.
3. For every cell in each touched sheet, classify it (store a `cell_class` map):
   - **`formula`** — `value` is a string starting with `=`. **Never overwrite.**
   - **`empty`** — `None` or whitespace-only.
   - **`placeholder`** — writable. A cell is a placeholder if it matches ANY of:
     - Regex `^[\s\[\]xX%$,.\-]*$` (e.g. `XX%`, `X%`, `[XX]`, `--`)
     - Case-insensitive equals one of: `tbd`, `n/a`, `please select`, `please choose`,
       `select an option`, `select...`, `choose one`, `please specify`, `[leave blank]`
     - Has an attached `DataValidation` (dropdown) — a constrained input slot
     - A multi-line cell whose non-empty lines all start with a checkbox glyph
       (`☐ ☑ ☒` or `[ ]` / `[x]`)
   - **`label`** — any other non-empty cell. **Never overwrite.**
4. For each fill, resolve its destination per the Input Contract targeting mode and record
   a plan entry (target cells, matched header columns, match score). Validate the `sheet`
   exists (case-insensitive fallback); if missing, skip that fill (don't crash).
5. Write the plan to `{{results_dir}}/placement_plan.json` (including the `cell_class` of
   each target) for debugging.

**Label/header matching** uses Jaccard similarity: tokenize on whitespace+punctuation,
lowercase, drop `%`/`[]` and tokens of length ≤ 1, then `len(a&b)/len(a|b)`. Accept a
match at ≥ 0.5 for labels, ≥ 0.3 for table-header alignment.

---

## Step 4: Fill the Workbook

Process fills sorted by `(sheet, top_row, top_col)`. For each:

### 4a. Skip path
If the fill's value is empty/`null`/whitespace, or its resolved destination is classified
`label`/`formula`, append to `skipped_fills.json` (with the reason and the existing label
text) and continue. **Never overwrite a `label` or `formula` cell** — that is a hard FAIL.

### 4b. `cell` target
Re-check the cell's class. If `placeholder`/`empty`, normalize (Step 4d) and write
(`cell.value = ...`; assign `.value` only, never the whole Cell, to preserve styling).

### 4c. `match_label` + `values` (row-label + header-keyed)
1. Find the **header row**: the first row containing any of the `values` keys as a label;
   record `{key: column}` for each matched key.
2. Find the **destination row**: the row whose column-0 label has the highest Jaccard
   similarity to `match_label` (≥ 0.5).
3. For each `(key, value)`: the destination cell is `(dest_row, header_col[key])`. If it's
   `placeholder`/`empty`, normalize and write; if `label`/`formula`, skip + record.

### 4c.1 `match_label` + `value` (label → adjacent placeholder)
Find the label cell, then scan rightward from the next column (up to +8 columns) for the
first `placeholder`/`empty` cell and write there. Record `wrote_at`. If none is writable,
append to `skipped_fills.json` (`reason: "no_writable_cell_adjacent_to_label"`).

### 4c.2 `table_range` + `rows`
Parse the range. If its first row contains labels, treat them as the header and align the
incoming `header`/columns to the existing labels by Jaccard (≥ 0.3); write only data rows
under the header. If column 0 of the range carries row labels, anchor each incoming row to
the destination row whose col-0 label matches best (don't write sequentially). Per cell:
re-check class; `label`/`formula` → skip, else normalize + write. If the table has more
data rows than placeholder rows → overflow (Step 5).

### 4d. Value normalization (FORMAT-AWARE — apply to every write)
Read the destination cell's `number_format` and coerce only when it calls for it:
- **Percent** (`number_format` contains `%`): `"34%"` → float `0.34`. If the format is
  `General`/`@` (text), keep the string `"34%"`.
- **Number** (`number_format` matches `0`/`#`, not `@`): strip `$ € ,` and write
  `float`/`int`. If `@` (text), keep the string.
- **Date** (`y`/`m`/`d` mask): parse `YYYY-MM-DD` or `M/D/YYYY` to `datetime`; else keep.
- **Empty/`None`**: if the rendered value is empty/`"None"`/whitespace → SKIP the write.
  (`str(None)` → `"None"` must never land in a cell.)
- **Checkbox single-select**: if the destination is a multi-line checkbox placeholder and
  the value names one checked option, write just that option's text.
- Otherwise write the rendered string, and set `wrap_text=True` for multi-line content.

The template's `number_format` is the source of truth for type coercion, not the value's
surface form.

### 4e. Always
Record per fill in `placement_report.json`: `{target, status, cells_written,
labels_preserved, match_score, overflowed, strategy_applied}`.

---

## Step 5: Overflow Handling

### 5a. `alert` (default) — truncate + flag, NEVER insert
Under `alert`, **never** call `insert_rows`/`insert_cols`; dimensions must equal the
template's. Truncate the value to fit, attach an `openpyxl.comments.Comment` to the first
destination cell (`OVERFLOW: 12 rows / 5 available, 7 truncated. See overflow_report.json`),
set a loud fill (`PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")`,
preserving any existing non-default fill), and append the full untruncated content to
`overflow_report.json`.

### 5b. `insert`
If `data_rows > dest_rows` and `delta ≤ {{max_overflow_inserts}}`: `ws.insert_rows(bottom+1,
amount=delta)`, copy styling from the last original row onto inserted rows, then write.
Maintain a `row_shift_map: {sheet: {orig_row: shift}}` and apply it to every subsequent
fill's coords. Above the cap, fall back to `alert`. Column inserts are riskier (they break
absolute-column formulas) — default to `alert` for column overflow unless notes request it.

### 5c. `both`
Do `insert`, plus a brief comment on the first cell noting "N rows inserted to fit".

Every overflow event is appended to `overflow_report.json` regardless of strategy.

---

## Step 6: Save & Self-Verify

1. `wb.save("{{results_dir}}/filled_workbook.xlsx")`
2. Reopen the saved file — `openpyxl.load_workbook(...)` must not raise.
3. Spot-check 5 placed fills: read back the destination and confirm a non-empty value.
4. Spot-check overflow events: confirm the comment/fill/inserted rows are present.

---

## Step 7: Evaluate Outputs

Assign each fill a status:

| Status | Criteria |
|--------|----------|
| `PASS` | Non-empty value, destination resolved, all `label`/`formula` cells in/around the destination preserved, value written, and (if it overflowed) the configured strategy applied + logged. |
| `PARTIAL` | Placed with caveats: label/header match `< 0.5`/`0.3` (fell back), overflow truncated under `alert`, `insert` hit the cap, or dropdown coercion dropped explanatory text. |
| `FAIL` | Non-empty value but could not place — sheet missing, range parse error, openpyxl write exception, **or a `label`/`formula` cell was overwritten** (hard FAIL — never silently roll forward). |
| *(not counted)* | `skipped_fills.json` entries — not failures. |

Aggregate into `validation_report.json` under `results`, including `labels_preserved_total`.

---

## Step 8: Iterate on Errors (max 3 rounds)

For any `FAIL`: read the captured error, apply the matching Common Fix, retry just that
fill, re-evaluate. Repeat at most 3 times; after that keep `FAIL` and surface it in
`summary.md`.

### Common Fixes

| Issue | Fix |
|-------|-----|
| Existing label/header overwritten | The destination's `cell_class` had `label`/`formula` cells that were ignored. Restore the template's value for that cell and re-resolve the target. **Hard FAIL until fixed.** |
| Formula clobbered (e.g. wrote a number over `=SUM(...)`) | Never write into a cell whose value starts with `=`. Classify it `formula` and skip. |
| Workbook grew under `alert` | You called `insert_rows` while `overflow_strategy=alert`. Re-read Step 5a — truncate-and-flag only. |
| Overrode a parameter because the notes mentioned it | Re-read "Parameter precedence". The run parameter is non-negotiable. |
| `"20%"` became `0.2` but the template keeps `"20%"` | The cell's `number_format` is `General`/`@` (text) — write the string as-is (Step 4d). |
| Literal `"None"` written into a cell | The rendered value was `str(None)`; skip the write when empty/`None`/whitespace. |
| `KeyError` on sheet name | Case-insensitive then `strip().lower()` then fuzzy-substring lookup; log the resolved name. |
| `IllegalCharacterError` on write | Strip control/zero-width chars, replace tabs with spaces, trim to 32,767 chars (Excel's per-cell limit). |
| `MergedCell` write rejection | Write to the merged range's top-left anchor; re-resolve anchors after any `insert_rows`. |
| Insert broke a downstream fill's coords | Apply the `row_shift_map` to that fill's coords before retrying; else fall back to `alert`. |
| Value JSON has no `fills` array | Accept a bare array too, or `{data:[...]}`; coerce to a `fills` list. Log the coercion. |

---

## Step 9: Write Executive Summary

Write `{{results_dir}}/summary.md`:

```markdown
# JSON → Excel — {{output_basename}} — Results

## Overview
- **Date**: <ISO timestamp>
- **Template**: <filename>  ·  **Data**: <filename>  ·  **Overflow strategy**: {{overflow_strategy}}
- **Sheets touched**: <list>
- **Fills**: <N>  |  **Placed**: <N>  |  **Skipped**: <N>  |  **Failed**: <N>

## Results Summary
| Status | Count | % |
|--------|-------|---|
| PASS | … | … |
| PARTIAL | … | … |
| FAIL | … | … |
| SKIPPED | … | … |

## Overflow Events
- **Total**: <N>  ·  resolved by insert / alert: <N> / <N>  ·  top offenders: <list>

## Notes Applied
<rules extracted from the notes file and whether they fired>

## Recommendations / Limitations
<e.g. raise max_overflow_inserts; sheet X uses dropdowns; param-vs-notes tensions>
```

---

## Step 10: Write Validation Report

Write `{{results_dir}}/validation_report.json`:

```json
{
  "version": "1.0.0",
  "run_date": "<ISO timestamp>",
  "parameters": { "output_basename": "{{output_basename}}", "overflow_strategy": "{{overflow_strategy}}", "max_overflow_inserts": {{max_overflow_inserts}} },
  "stages": [
    { "name": "setup", "passed": true, "message": "Inputs resolved, deps installed" },
    { "name": "plan", "passed": true, "message": "Built N placement plans" },
    { "name": "placement", "passed": true, "message": "Placed P, skipped S, failed F" },
    { "name": "overflow_handling", "passed": true, "message": "O overflow events handled" },
    { "name": "label_preservation", "passed": true, "message": "All label/formula cells preserved" },
    { "name": "save", "passed": true, "message": "Workbook saved and reopened cleanly" },
    { "name": "report_generation", "passed": true, "message": "All output files written" }
  ],
  "results": { "pass": 0, "partial": 0, "fail": 0, "skipped": 0, "overflow_events": 0, "labels_preserved_total": 0 },
  "overall_passed": true,
  "output_files": [
    "{{results_dir}}/filled_workbook.xlsx",
    "{{results_dir}}/overflow_report.json",
    "{{results_dir}}/skipped_fills.json",
    "{{results_dir}}/placement_report.json",
    "{{results_dir}}/summary.md",
    "{{results_dir}}/validation_report.json"
  ]
}
```

`overall_passed` is `true` iff every stage passed **and** `results.fail == 0`.

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="{{results_dir}}"
FILLED="$RESULTS_DIR/filled_workbook.xlsx"
for f in "$FILLED" \
         "$RESULTS_DIR/overflow_report.json" \
         "$RESULTS_DIR/skipped_fills.json" \
         "$RESULTS_DIR/placement_report.json" \
         "$RESULTS_DIR/summary.md" \
         "$RESULTS_DIR/validation_report.json"; do
  [ -s "$f" ] && echo "PASS: $f ($(wc -c < "$f") bytes)" || echo "FAIL: $f is missing or empty"
done
python - <<PY
from openpyxl import load_workbook
import glob, sys
tmpl = sorted(glob.glob("/app/assets/*.xlsx"))[0]
filled = "$FILLED"
e = load_workbook(tmpl); f = load_workbook(filled)
print(f"PASS: filled reopened, sheets={f.sheetnames}")
# Dimension audit (alert strategy must not grow the sheet)
if "{{overflow_strategy}}" == "alert":
    for s in e.sheetnames:
        if s in f.sheetnames and (f[s].max_row > e[s].max_row or f[s].max_column > e[s].max_column):
            print(f"FAIL: sheet {s} grew under alert strategy"); sys.exit(1)
    print("PASS: dimension audit (no growth under alert)")
PY
echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] `filled_workbook.xlsx` exists and reopens cleanly with `openpyxl`
- [ ] `overflow_report.json`, `skipped_fills.json`, `placement_report.json` exist (may be `[]`)
- [ ] `summary.md` follows the Step 9 template; `validation_report.json` has `stages`/`results`/`overall_passed`
- [ ] **Label-preservation audit**: for ≥ 5 sampled fills, the destination's surrounding label/header cells in the FILLED workbook still equal the template's values exactly. Any divergence is a FAIL.
- [ ] **Formula audit**: every cell that was a formula in the template is still a formula in the output (none clobbered with a literal).
- [ ] **Dimension audit**: under `overflow_strategy=alert`, every sheet's `max_row`/`max_column` equals the template's. Growth = a stray insert = FAIL.
- [ ] Sheet names unchanged (none renamed/dropped/added unintentionally)

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **The template's existing cells are the source of truth for layout.** Snapshot and
  classify every destination cell first; labels and formulas are sacred, placeholders and
  empties are the only writable surfaces.
- **Coerce by `number_format`, not by surface form.** `'0.0%'` → float; `'@'` text → keep
  the string. Blanket-normalizing destroys values the template intentionally keeps verbatim.
- **Row-label anchoring beats sequential writes.** When a range's rows have labels in
  column 0, match each incoming row to the destination row whose label is most similar —
  sequential writing misaligns the moment the template has spacer or out-of-order rows.
- **Never write over a formula.** A cell whose value starts with `=` is computed structure;
  writing a literal silently breaks the workbook's math.
- **`alert` means zero inserts.** If `max_row`/`max_column` grew, you violated the strategy.
- **`openpyxl.insert_rows` shifts everything below.** Keep a `row_shift_map`, process fills
  top-down, and re-resolve merged-cell anchors after any insert (Excel drops comments on
  non-anchor merged cells).
- **Merged cells reject non-anchor writes** — always write to the top-left anchor.
- **Jaccard similarity is enough** — tokenize, lowercase, drop `%`/`[]`, `len(a&b)/len(a|b)`.
  Thresholds 0.5 (labels) / 0.3 (table headers) are good defaults.
- **Excel's per-cell limit is 32,767 chars** — truncate with a trailing marker, don't crash.
