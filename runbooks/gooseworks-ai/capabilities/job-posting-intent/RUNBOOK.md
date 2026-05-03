---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/job-posting-intent/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/job-posting-intent
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Job Posting Intent Detection
  imported_at: '2026-05-03T02:53:59Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: job-posting-intent
    confidence: high
secrets:
  APIFY_API_TOKEN:
    env: APIFY_API_TOKEN
    description: Apify API token used by the source job-posting intent scripts
    required: true
  RUBE_API_KEY:
    env: RUBE_API_KEY
    description: Rube/Composio credential used for Google Sheets export when enabled
    required: false
---

# Job Posting Intent Detection — Agent Runbook

## Objective
Detect buying intent from job postings. When a company posts a job in your problem area, they've allocated budget and are actively thinking about the problem. This skill finds those companies, qualifies them, extracts personalization context, and outputs everything to a Google Sheet. Does NOT do outreach — just delivers qualified leads with reasoning. The runbook guides an agent through configuring the required APIs, estimating search cost, running the job-posting intent search, and exporting qualified lead intelligence. It preserves the upstream workflow while adding Jetty-required outputs, bounded validation, and structured provenance.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/job_posting_intent_results.json` | Structured leads and qualification signals produced by the search |
| `/app/results/google_sheet_url.txt` | Google Sheet URL when sheet export is enabled, or an explanatory skip note |
| `/app/results/raw_jobs.json` | Raw job posting payloads when raw output is requested |
| `/app/results/summary.md` | Executive summary of query, cost estimate, result counts, and follow-up notes |
| `/app/results/validation_report.json` | Programmatic validation report for setup, execution, outputs, and final verification |

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `results_dir` | `/app/results` | Output directory for all required artifacts |
| `target_titles` | `[]` | Job titles or title fragments to search for |
| `problem_area` | required | Problem, capability, or market area that the hiring signal should map to |
| `location` | optional | Geographic filter passed through to the search provider |
| `max_results` | `100` | Maximum job postings to inspect before qualification |
| `max_cost` | `25` | Maximum expected Apify spend in USD before execution proceeds |
| `sheet_name` | generated | Google Sheet name used when export is enabled |
| `export_google_sheet` | `true` | Whether to create a Google Sheet through Rube/Composio |
| `save_raw_json` | `true` | Whether to retain raw posting payloads for traceability |

## Dependencies

| Dependency | Required | Purpose |
|---|---|---|
| `python` and `pip` | Yes | Run the upstream scripts and validation snippets |
| `requests` | Yes | Fetch and process job posting data |
| `apify-client` | Yes | Query job posting/search actors |
| `APIFY_API_TOKEN` | Yes | Authenticate to Apify |
| `RUBE_API_KEY` or Composio/Rube auth | No | Create Google Sheets when export is enabled |
| Google Sheets access | No | Destination for exported qualified leads |

## Step 1: Environment Setup

Create the output directory, install runtime dependencies, and verify required secrets before running any paid search.

```bash
mkdir -p /app/results
python -m pip install --quiet requests apify-client pandas pydantic

if [ -z "${APIFY_API_TOKEN:-}" ]; then
  echo "ERROR: APIFY_API_TOKEN is required" >&2
  exit 1
fi
```

Source setup notes:

```markdown

```

## Step 2: Define the Search Intent

Convert the operator's ICP into explicit title, problem-area, and location filters. Treat job postings as budget signals: the hiring company has allocated headcount, acknowledged the problem, and is actively trying to solve it.

```json
{
  "problem_area": "<problem your product solves>",
  "target_titles": ["<role title 1>", "<role title 2>"],
  "location": "<optional geography>",
  "max_results": 100,
  "export_google_sheet": true
}
```

Upstream rationale:

```markdown
When a company posts a job, they've:
- Allocated budget (headcount is expensive)
- Acknowledged the problem exists
- Started actively solving it

If your product helps solve that problem faster, cheaper, or better than a hire alone, the timing is perfect.
```

## Step 3: Estimate Cost

Estimate Apify spend before execution and stop if the estimate exceeds `max_cost`. Write the estimate into the validation report so reviewers can audit paid API usage.

```bash
python scripts/job_posting_intent.py estimate-cost \
  --titles "$TARGET_TITLES" \
  --problem-area "$PROBLEM_AREA" \
  --max-results "${MAX_RESULTS:-100}"
```

## Step 4: Run the Search

Run the search only after setup and cost validation pass. Save both qualified results and raw payloads when requested.

```bash
python scripts/job_posting_intent.py search \
  --titles "$TARGET_TITLES" \
  --problem-area "$PROBLEM_AREA" \
  --location "${LOCATION:-}" \
  --max-results "${MAX_RESULTS:-100}" \
  --output /app/results/job_posting_intent_results.json \
  --raw-output /app/results/raw_jobs.json
```

Usage patterns from the source skill:

```markdown

```

## Step 5: Qualify and Export Leads

For each candidate company, record signal strength, reasoning, likely decision makers, outreach angles, and personalization context. If Google Sheets export is enabled, create or update the sheet and write its URL to `/app/results/google_sheet_url.txt`; otherwise write `Google Sheets export skipped` to that file.

Expected sheet columns are inherited from the source skill:

```markdown
| Column | Description |
|--------|-------------|
| Signal | HIGH / MEDIUM / LOW based on # postings + seniority |
| Company | Company name |
| Employees | Employee count |
| Industry | Company industry |
| Website | Company website |
| LinkedIn | Company LinkedIn URL |
| # Postings | Number of relevant job postings found |
| Job Titles | The actual job titles posted |
| Job URL | Link to the primary job posting |
| Location | Job location(s) |
| Decision Maker | Suggested title of person to contact |
| Outreach Angle | Accelerate / Replace / Multiply the hire |
| Tech Stack | Technologies mentioned in job descriptions |
| Growth Signals | Growth indicators (first hire, scaling, series stage) |
| Pain Points | Pain indicators (automate, optimize, manual processes) |
| Description | Company description snippet |
```

## Step 6: Validate Outputs

Validate that every mandatory artifact exists, that JSON outputs parse, and that lead records include company, job title, source URL, qualification reasoning, and signal strength.

```bash
python - <<'PY'
import json
from pathlib import Path

required = [
    Path("/app/results/job_posting_intent_results.json"),
    Path("/app/results/google_sheet_url.txt"),
    Path("/app/results/summary.md"),
    Path("/app/results/validation_report.json"),
]
missing = [str(path) for path in required if not path.exists() or path.stat().st_size == 0]
if missing:
    raise SystemExit("Missing required outputs: " + ", ".join(missing))

results = json.loads(Path("/app/results/job_posting_intent_results.json").read_text())
if not isinstance(results, list):
    raise SystemExit("job_posting_intent_results.json must contain a JSON array")
for index, row in enumerate(results):
    for key in ["company", "job_title", "source_url", "reasoning", "signal_strength"]:
        if key not in row:
            raise SystemExit(f"Result {index} missing {key}")
print("Output validation passed")
PY
```

## Step 7: Iterate on Errors (max 3 rounds)

If setup, execution, export, or validation fails, inspect the specific failure, apply one targeted fix, and rerun validation. Stop after max 3 rounds and write the unresolved issue to `/app/results/summary.md` and `/app/results/validation_report.json`.

### Common Fixes

| Issue | Fix |
|---|---|
| No jobs found | Broaden titles, remove location filters, or search adjacent titles |
| Too many irrelevant results | Add required keywords and stricter title filters |
| Google Sheet creation failed | Verify Rube/Composio auth, then rerun export from saved JSON |
| High cost estimate | Lower `max_results` or split the query into narrower batches |

Source troubleshooting notes:

```markdown

```

## Step 8: Write Summary

Write `/app/results/summary.md` with the query parameters, cost estimate, number of postings inspected, number of qualified leads, Google Sheet URL or skip reason, and any manual follow-up needed.

## Final Checklist

Run this verification script before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/job_posting_intent_results.json" \
  "$RESULTS_DIR/google_sheet_url.txt" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

python - <<'PY'
import json
from pathlib import Path
report = json.loads(Path("/app/results/validation_report.json").read_text())
if not report.get("overall_passed"):
    raise SystemExit("FAIL: validation_report.json overall_passed is false")
print("PASS: validation_report.json overall_passed is true")
PY
```

- [ ] Required output files exist and are non-empty
- [ ] Cost estimate was recorded before paid execution
- [ ] Qualified leads include reasoning and signal strength
- [ ] Google Sheet URL or skip note is present
- [ ] Validation report includes stage-level results and `overall_passed`

## Tips

- [Apify LinkedIn Job Search Actor](https://apify.com/harvestapi/linkedin-job-search)
- [Apify API Token](https://console.apify.com/account/integrations)
- [Apify Billing Dashboard](https://console.apify.com/billing)

## Source Options Reference

```markdown
```
Required:
  --titles              Comma-separated job titles to search

Optional:
  --locations           Comma-separated locations (default: no filter)
  --max-per-title       Max jobs per title per location (default: 25)
  --posted-limit        Recency: 1h, 24h, week, month (default: week)
  --output, -o          Also save raw JSON to this file path
  --json                Print JSON output to console
  --estimate-only       Show cost estimate without running
  --no-sheet            Skip Google Sheet creation
  --sheet-name          Custom Google Sheet title (default: "Job Posting Intent Signals - {date}")
  --relevance-keywords  Comma-separated keywords to filter truly relevant postings
```
```
