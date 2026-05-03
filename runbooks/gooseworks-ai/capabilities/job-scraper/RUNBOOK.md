---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/job-scraper/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/job-scraper
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Job Scraper
  imported_at: '2026-05-03T02:54:12Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: job-scraper
    confidence: high
secrets:
  APIFY_API_TOKEN:
    env: APIFY_API_TOKEN
    description: Apify API token used to run the LinkedIn and Indeed scraping actors.
    required: true
---

# Job Scraper — Agent Runbook

## Objective

Search LinkedIn and Indeed job postings through Apify and return structured job market data. Search for job postings across LinkedIn and Indeed. Use when users want to find open roles, monitor hiring signals, identify companies hiring for specific positions, or research competitor hiring activity. Returns job title, company, location, salary, description, seniority level, and direct apply URLs. No login or cookies required. The runbook chooses the right source from the user's intent, runs bounded collection, normalizes the actor output, and writes auditable result files under `/app/results`.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/jobs.json` | Normalized job postings with title, company, location, salary, description, seniority, source, and apply URL |
| `/app/results/search_plan.json` | Resolved source selection, query parameters, actor choices, and limits |
| `/app/results/summary.md` | Executive summary of the search, key hiring signals, and notable gaps |
| `/app/results/validation_report.json` | Programmatic validation results with stage outcomes and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `results_dir` | `/app/results` | Directory where all output files are written |
| `query` | required | Role, company, keyword, or hiring-signal request to search |
| `location` | optional | City, region, country, or remote filter |
| `source` | `auto` | `auto`, `linkedin`, `indeed`, or `both` |
| `max_results` | `50` | Maximum normalized jobs to return |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| `APIFY_API_TOKEN` | secret | yes | Token for Apify actors |
| `requests` | Python package | yes | Calls Apify APIs and downloads datasets |
| `pyyaml` | Python package | yes | Writes structured run metadata |
| `jq` | CLI | optional | Useful for local inspection of JSON outputs |

## Step 1: Environment Setup

1. Verify `/app/results` exists and create it if needed.
2. Verify `APIFY_API_TOKEN` is present in the environment.
3. Install Python dependencies if they are missing:

```bash
pip install requests pyyaml
mkdir -p /app/results
test -n "$APIFY_API_TOKEN"
```

If setup fails, write `/app/results/validation_report.json` with `overall_passed=false`, include the failing stage, and stop.

## Step 2: Interpret the Search Request

Map the user's request into a concrete job-search plan:

| Signal | Source choice |
|---|---|
| B2B, SaaS, enterprise, seniority, job function, or industry research | LinkedIn |
| broad coverage, salary, company details, ratings, contacts, or street address | Indeed |
| unclear or explicitly cross-platform | both |

Do not ask which source to use unless the request is genuinely ambiguous. Write the resolved plan to `/app/results/search_plan.json`.

## Step 3: Run Apify Actors

Use `automation-lab/linkedin-jobs-scraper` for LinkedIn and `borderline/indeed-scraper` for Indeed. Start only the actors selected in `search_plan.json`, pass the query and location filters, and cap each actor so the combined normalized output respects `max_results`.

Poll Apify until each actor run succeeds, fails, or times out. Keep polling bounded to max 12 rounds with a fixed delay between rounds, and record actor run IDs in the validation report.

## Step 4: Normalize Job Records

Transform all source records into this schema:

```json
{
  "title": "string",
  "company": "string",
  "location": "string",
  "salary": "string or null",
  "description": "string or null",
  "seniority_level": "string or null",
  "source": "linkedin or indeed",
  "apply_url": "string",
  "posted_at": "string or null"
}
```

Deduplicate by canonical apply URL when available, otherwise by normalized title, company, and location. Write the final array to `/app/results/jobs.json`.

## Step 5: Analyze Hiring Signals

Summarize the strongest patterns in `/app/results/summary.md`: companies hiring most actively, recurring role families, locations, salary ranges when available, and caveats about platform coverage or actor failures.

## Step 6: Validate Outputs

Programmatically verify:

| Check | Requirement |
|---|---|
| `jobs.json` | exists, parses as JSON, and contains a list |
| `search_plan.json` | exists and records query, source, and max results |
| `summary.md` | exists and is non-empty |
| `validation_report.json` | includes stages, results, and `overall_passed` |

## Step 7: Iterate on Errors (max 3 rounds)

If validation fails, inspect the first failing stage, apply the targeted fix, and rerun only the affected step. Stop after max 3 rounds and leave `overall_passed=false` if the same failure remains.

## Common Fixes

| Issue | Fix |
|---|---|
| Missing `APIFY_API_TOKEN` | Stop and report the missing secret; do not attempt scraping |
| Actor returns no records | Broaden the query or run both sources if the user allowed auto selection |
| Dataset fields differ from expected names | Preserve raw fields in memory and update the normalization mapping |
| Duplicate-heavy results | Deduplicate by apply URL first, then title/company/location |

## Final Checklist

Run this verification script before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/jobs.json" \
  "$RESULTS_DIR/search_plan.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
python - <<'PY'
import json, pathlib, sys
base = pathlib.Path('/app/results')
json.loads((base / 'jobs.json').read_text())
report = json.loads((base / 'validation_report.json').read_text())
assert 'stages' in report and 'overall_passed' in report
PY
```

## Tips

Prefer automatic source selection from the user's intent. LinkedIn is usually better for B2B hiring-signal research, while Indeed is usually better for broad market coverage and richer company or salary fields.
