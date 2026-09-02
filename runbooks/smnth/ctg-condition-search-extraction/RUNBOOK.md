---
version: "1.3.0"
evaluation: programmatic
agent: opencode                       # Agent runtime: claude-code | opencode | codex | gemini-cli
model: openai/gpt-5.6-terra            # Model for the agent — OpenRouter catalog id
model_provider: openrouter             # opencode routes through OpenRouter
snapshot: prism-playwright            # Browser needed to read exact rendered text off each study page
primary_outputs:
  - "studies.csv"
secrets:                              # None — ClinicalTrials.gov API v2 and study pages are public, no auth
---

# ClinicalTrials.gov Condition Search Extraction — Agent Runbook

## Objective

Search ClinicalTrials.gov for studies matching the condition `{{condition}}` that were first posted between `{{posted_from}}` and `{{posted_to}}`. For each matching study, open its own ClinicalTrials.gov study page (`https://clinicaltrials.gov/study/{NCT_NUMBER}`) and extract exactly what is displayed there — no paraphrasing, no reformatting, no inferred values — for seven fields: Study Title, NCT Number, Study URL, Study Status, Enrollment size, Study Type, and Start Date. Produce a single spreadsheet with one row per study, using "Not found" for any field genuinely absent from the page. The output is consumed directly by the user as a CSV they will open in a spreadsheet tool.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `{{results_dir}}`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `{{results_dir}}/studies.csv` | One row per matching study, columns exactly: `Study Title, NCT Number, Study URL, Study Status, Enrollment size, Study Type, Start Date` |
| `{{results_dir}}/summary.md` | Executive summary with run metadata, results breakdown, and recommendations |
| `{{results_dir}}/validation_report.json` | Structured validation results with stages, results, and overall_passed |
| `{{results_dir}}/extraction_audit.json` | Full provenance trail — candidate list, sanity-check drops, page-404 exclusions, and per-row extraction detail (see Step 6) |

If you finish your analysis but have not written all files, go back and write them before stopping.

---

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|------------------|---------|-------------|
| Results directory | `{{results_dir}}` | `/app/results` (Jetty) / `./results` (local) | Output directory for all results |
| Condition | `{{condition}}` | `Multiple myeloma` | Exact condition text to search for on ClinicalTrials.gov. Use verbatim — do not substitute synonyms. |
| Posted from | `{{posted_from}}` | `2026-06-25` | Earliest "First Posted" date to include (inclusive), format YYYY-MM-DD |
| Posted to | `{{posted_to}}` | `2026-08-25` | Latest "First Posted" date to include (inclusive), format YYYY-MM-DD |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| ClinicalTrials.gov API v2 (`https://clinicaltrials.gov/api/v2/studies`) | External API | Yes | Public, no auth required. Used only to build the candidate list of NCT numbers — never as the source of the displayed field values. |
| ClinicalTrials.gov study pages (`https://clinicaltrials.gov/study/{NCT}`) | External web page (JS-rendered) | Yes | The authoritative source for every extracted field. Requires a real browser (Playwright/Chromium) since the page is a client-rendered SPA. |
| pandas | Python package | Yes | CSV construction |

---

## Step 1: Environment Setup

```bash
pip install pandas playwright
python -m playwright install chromium

mkdir -p {{results_dir}}
```

No secrets are required — both the API and the study pages are public.

---

## Step 2: Build the Candidate List

Use the ClinicalTrials.gov API v2 to narrow down which studies to visit. This step only produces a list of NCT numbers — it is NOT the source of any extracted field value.

### API Call

```bash
curl -s "https://clinicaltrials.gov/api/v2/studies" \
  --data-urlencode "query.cond={{condition}}" \
  --data-urlencode "filter.advanced=AREA[StudyFirstPostDate]RANGE[$(date -d {{posted_from}} +%m/%d/%Y 2>/dev/null || echo {{posted_from}}),$(date -d {{posted_to}} +%m/%d/%Y 2>/dev/null || echo {{posted_to}})]" \
  --data-urlencode "fields=NCTId,BriefTitle,Condition" \
  --data-urlencode "pageSize=200"
```

Handle pagination via the `nextPageToken` field in the response — keep requesting with `pageToken=<token>` until it is absent, so no matching study is missed.

### Record

For each returned study, record `{ "nct": ..., "conditions": [...] }` into a running `candidates` list — this becomes the `candidates` array in `extraction_audit.json` (Step 6).

### Sanity check

Drop any candidate whose `conditions` list does not plausibly reference `{{condition}}` (case-insensitive substring or clear synonym match, e.g. "Multiple Myeloma", "MM"). This guards against overly broad API matches. For each dropped candidate, record `{ "nct": ..., "reason": ..., "conditions": [...] }` into a running `dropped` list — this becomes the `dropped` array in `extraction_audit.json`.

---

## Step 3: Extract Exact Field Values From Each Study Page

For every candidate NCT number remaining after Step 2, open `https://clinicaltrials.gov/study/{NCT}` in a real browser (Playwright/Chromium) and wait for the page content to fully render (the page is a client-rendered app — a raw HTTP GET will not contain the visible text).

For each study, read the **visible rendered text** for these fields exactly as displayed — same casing, same punctuation, same qualifiers (e.g. "(Estimated)" / "(Actual)" if the page shows them), no reformatting:

| Output column | Where to find it on the page |
|---|---|
| Study Title | The main page heading (official/brief title as shown at the top of the study page) |
| NCT Number | The NCT identifier shown near the title |
| Study URL | Construct as `https://clinicaltrials.gov/study/{NCT}` (this is deterministic, not scraped) |
| Study Status | The status badge/label near the top of the page (e.g. "Recruiting", "Not yet recruiting", "Active, not recruiting", "Completed") |
| Enrollment size | The "Enrollment" value, typically in the Study Design or Participation section — copy the number and any qualifier text exactly as shown |
| Study Type | The "Study Type" value in the Study Design section (e.g. "Interventional", "Observational") |
| Start Date | The "Start Date" value, typically in the Status or Study Record Dates section — copy exactly as shown, including precision (month-only vs full date) and any "(Estimated)"/"(Actual)" qualifier |

If a field is genuinely not present anywhere on the page, use the literal string `Not found` for that cell — never guess, infer, or backfill from the Step 2 API data.

### Record

For each study, store a row: `[Study Title, NCT Number, Study URL, Study Status, Enrollment size, Study Type, Start Date]`. Alongside it, record the extraction detail that will populate `extraction_audit.json`'s `rows` array: the same seven fields plus `_page_loaded` (bool), `_condition_present` (bool — did the study's own page actually reference `{{condition}}`), `_attempts` (int), `_error` (string, empty if none), `_evaluation` (`PASS`/`PARTIAL`/`FAIL` per Step 4), and `_evaluation_reason` (string, empty if PASS with no caveats).

Add a small polite delay between page loads (e.g. 1-2 seconds) to avoid hammering the site.

---

## Step 4: Evaluate Outputs

For each row, assign an evaluation status:

| Status | Criteria |
|--------|----------|
| `PASS` | Page loaded successfully; NCT Number, Study Title, Study URL, and Study Status were all found verbatim on the page; any remaining fields are either found verbatim or genuinely absent (correctly marked "Not found") |
| `PARTIAL` | Page loaded, but one or more of Enrollment size / Study Type / Start Date could not be located and were marked "Not found" even though the section plausibly exists (worth a retry) |
| `FAIL` | Page failed to load after retries, or the study does not actually reference `{{condition}}` on its own page (should have been dropped in Step 2's sanity check) |

---

## Step 5: Iterate on Errors (max 3 rounds)

If any rows received `FAIL` or `PARTIAL` status:

1. Read the specific error (timeout, selector not found, navigation failure, condition mismatch)
2. Apply the targeted fix from the Common Fixes table below
3. Re-run the failed study through Step 3
4. Re-evaluate with Step 4 criteria
5. Repeat up to 3 times total

After 3 rounds, keep the best result obtained. For any field still unresolved, use "Not found" — do not leave a cell blank or invent a value. Flag remaining failures in the summary.

### Common Fixes

| Issue | Fix |
|-------|-----|
| Page times out / doesn't finish rendering | Increase wait timeout, wait for a specific content selector (e.g. the title heading) rather than a fixed sleep, retry navigation once |
| A field's section isn't present for this study type (e.g. no Enrollment shown for a withdrawn study) | Confirm by re-reading the full rendered page text; if truly absent, this is not a failure — record "Not found" and mark PASS |
| Study page 404s (NCT retired/merged) | Drop the row, log it in the summary as excluded, do not fabricate a row. Record `{ "nct": ..., "reason": "404 / retired" }` into a running `excluded` list — this becomes the `excluded` array in `extraction_audit.json` |
| Rate limiting / temporary network error | Back off 5 seconds and retry the page load, up to 3 attempts |

---

## Step 6: Write Extraction Audit Trail

Write `{{results_dir}}/extraction_audit.json` — the full provenance trail assembled while working through Steps 2-5. This exists so a reader can verify no value was fabricated or backfilled from the API, and see exactly why any candidate was dropped or excluded:

```json
{
  "candidates": [
    { "nct": "NCT00000000", "conditions": ["..."] }
  ],
  "dropped": [
    { "nct": "NCT00000000", "reason": "Condition list did not plausibly reference {{condition}}", "conditions": ["..."] }
  ],
  "excluded": [
    { "nct": "NCT00000000", "reason": "404 / retired" }
  ],
  "rows": [
    {
      "Study Title": "...", "NCT Number": "...", "Study URL": "...", "Study Status": "...",
      "Enrollment size": "...", "Study Type": "...", "Start Date": "...",
      "_page_loaded": true, "_condition_present": true, "_attempts": 1,
      "_error": "", "_evaluation": "PASS", "_evaluation_reason": ""
    }
  ]
}
```

`rows` must have exactly one entry per row in `studies.csv`, in the same order, and every NCT number that appears in `candidates` must be traceable to either a `dropped`, `excluded`, or `rows` entry — no candidate should silently disappear.

---

## Step 7: Write Executive Summary

Write `{{results_dir}}/summary.md` with the following structure:

```markdown
# ClinicalTrials.gov Condition Search Extraction — Results

## Overview
- **Date**: {run date}
- **Condition searched**: {{condition}}
- **First Posted date range**: {{posted_from}} to {{posted_to}}
- **Candidate studies found (API)**: {count}
- **Studies dropped by sanity check**: {count, with reasons}
- **Studies written to spreadsheet**: {count}

## Results Summary

| Status | Count | % |
|--------|-------|---|
| PASS | ... | ... |
| PARTIAL | ... | ... |
| FAIL | ... | ... |

## Sample Outputs

### Successes
{2-3 representative rows}

### Failures / Not found fields
{List any study where a field is "Not found", and any study excluded entirely, with reasons}

## Recommendations
- {What to fix or investigate}

## Limitations
- Only the study's own ClinicalTrials.gov page was used as a source — no other registries, no cached/API-derived substitutions for displayed fields.
```

---

## Step 8: Write Validation Report

Write `{{results_dir}}/validation_report.json`:

```json
{
  "version": "1.0.0",
  "run_date": "2026-01-01T00:00:00Z",
  "parameters": {
    "condition": "{{condition}}",
    "posted_from": "{{posted_from}}",
    "posted_to": "{{posted_to}}"
  },
  "stages": [
    { "name": "setup", "passed": true, "message": "Environment ready" },
    { "name": "candidate_search", "passed": true, "message": "Found N candidates via API" },
    { "name": "page_extraction", "passed": true, "message": "Extracted N studies from their pages" },
    { "name": "evaluation", "passed": true, "message": "All rows evaluated" },
    { "name": "report_generation", "passed": true, "message": "All output files written" }
  ],
  "results": {
    "pass": 0,
    "partial": 0,
    "fail": 0
  },
  "overall_passed": true,
  "output_files": [
    "{{results_dir}}/studies.csv",
    "{{results_dir}}/summary.md",
    "{{results_dir}}/validation_report.json",
    "{{results_dir}}/extraction_audit.json"
  ]
}
```

---

## Step 9: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="{{results_dir}}"
for f in "$RESULTS_DIR/studies.csv" "$RESULTS_DIR/summary.md" "$RESULTS_DIR/validation_report.json" "$RESULTS_DIR/extraction_audit.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

python3 -c "
import csv, json
with open('$RESULTS_DIR/studies.csv') as f:
    reader = csv.reader(f)
    header = next(reader)
    expected = ['Study Title','NCT Number','Study URL','Study Status','Enrollment size','Study Type','Start Date']
    assert header == expected, f'Header mismatch: {header}'
    rows = list(reader)
    ncts = [r[1] for r in rows]
    assert len(ncts) == len(set(ncts)), 'Duplicate NCT numbers found'
    print(f'PASS: {len(rows)} rows, header matches exactly, no duplicate NCT numbers')

audit = json.load(open('$RESULTS_DIR/extraction_audit.json'))
assert len(audit['rows']) == len(rows), f\"audit rows ({len(audit['rows'])}) != csv rows ({len(rows)})\"
print(f\"PASS: extraction_audit.json has {len(audit['rows'])} row entries matching the CSV, {len(audit['dropped'])} dropped, {len(audit['excluded'])} excluded\")
"
```

### Checklist

- [ ] `studies.csv` exists, has the exact 7-column header, one row per unique NCT number
- [ ] Every field was copied verbatim from the study's own ClinicalTrials.gov page, or is "Not found"
- [ ] `summary.md` exists and follows the template from Step 7
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] `extraction_audit.json` exists with `candidates`, `dropped`, `excluded`, and `rows`, and every candidate NCT is accounted for in exactly one of `dropped`/`excluded`/`rows`
- [ ] Verification script printed PASS for all files

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- The ClinicalTrials.gov API v2 is convenient for building the candidate NCT list and handling pagination, but the user explicitly wants values "as exactly listed on the study's web page" — always read the final displayed field text from the rendered `/study/{NCT}` page itself, not the raw API JSON, since API enum codes (e.g. `NOT_YET_RECRUITING`) and API date structs are not formatted the way the page displays them.
- "First Posted" is the date filter criterion, per the user's "posted to clinicaltrials.gov" phrasing — it is not one of the output columns.
- Be conservative with "Not found": only use it when the field's section genuinely isn't present on the page, not when a selector merely needs a longer wait.
- `extraction_audit.json` is what lets a reader verify no value was silently fabricated or pulled from the API instead of the page — keep its `rows` entries populated as you go through Step 3 rather than reconstructing them from memory afterward, so `_error`/`_attempts` reflect what actually happened.
