---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/linkedin-job-scraper/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/linkedin-job-scraper
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: LinkedIn Scraper
  imported_at: '2026-05-03T02:53:45Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: linkedin-job-scraper
    confidence: high
secrets: {}
---

# LinkedIn Scraper - Agent Runbook

## Objective
This runbook finds LinkedIn job postings using the JobSpy Python library and a local `tools/jobspy_scraper.py` wrapper. It turns a requested role, location, company filter, recency window, and output target into a reproducible CSV export with posting metadata and direct URLs. The workflow includes environment setup, parameter selection, scraper execution, result interpretation, bounded retry handling, and final output validation.

## REQUIRED OUTPUT FILES (MANDATORY)

You MUST write all of the following files to `/app/results`. The task is not complete until every file exists and is non-empty.

| File | Description |
|---|---|
| `/app/results/linkedin_jobs.csv` | CSV export from JobSpy containing LinkedIn job postings and metadata. |
| `/app/results/summary.md` | Human-readable summary of search parameters, result count, top matches, output path, and issues. |
| `/app/results/validation_report.json` | Structured validation report with stages, pass/fail results, and final status. |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| Results directory | `/app/results` | Directory where required output files are written. |
| Search term | required | Job title, role, company hiring keyword, or search phrase for LinkedIn postings. |
| Location | none | City, state, country, or `Remote`. Recommended unless using only remote filters. |
| Results wanted | `25` | Maximum number of jobs to fetch. |
| Recency | none | Optional `hours_old` filter for recent postings, such as the last 48 or 72 hours. |
| Company IDs | none | Optional comma-separated LinkedIn company IDs. |
| Full descriptions | `false` | Fetch full job descriptions when detailed content is needed; this is slower. |
| Job type | any | One of `fulltime`, `parttime`, `contract`, or `internship`. |
| Remote only | `false` | Restrict results to remote jobs. |
| Output CSV | `/app/results/linkedin_jobs.csv` | Path for the scraper CSV output. |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| Python 3.10+ | Runtime | Yes | Required by `python-jobspy` and the scraper wrapper. |
| `python-jobspy` | Python package | Yes | Job scraping library used to query LinkedIn postings. |
| `tools/jobspy_scraper.py` | Local script | Yes | Thin wrapper around JobSpy that accepts CLI parameters and writes a CSV. |
| Network access | External | Yes | Required to retrieve current LinkedIn job results. |
| `csv`-readable output path | Filesystem | Yes | Results must be saved under `/app/results`. |

## Step 1: Environment Setup

Install the runtime dependency and create the output directory.

```bash
mkdir -p /app/results
python3.12 -m pip install -U python-jobspy --break-system-packages
```

Verify the scraper wrapper is available. If it is missing, copy it from the source skill assets before running.

```bash
test -s tools/jobspy_scraper.py || cp skills/linkedin-job-scraper/scripts/jobspy_scraper.py tools/jobspy_scraper.py
test -s tools/jobspy_scraper.py
```

## Step 2: Resolve Search Inputs

Identify the search term, location, result count, recency, company IDs, description requirement, job type, and remote-only flag from the user request. If a request is underspecified, choose pragmatic defaults and record them in `/app/results/summary.md`.

Use these defaults unless the user supplied different values:

| Input | Default |
|---|---|
| Search term | Ask for a role or infer from the request if obvious. |
| Location | Omit unless the user provided one or asked for remote jobs. |
| Results | `25` |
| Output | `/app/results/linkedin_jobs.csv` |

## Step 3: Construct the Scraper Command

Build the command with only the filters that apply. Always write the CSV to `/app/results/linkedin_jobs.csv` unless the user requested a different file under `/app/results`.

```bash
python tools/jobspy_scraper.py \
  --search "<term>" \
  --location "<location>" \
  --results <N> \
  --output /app/results/linkedin_jobs.csv
```

Optional flags:

```bash
--hours-old <N>
--fetch-descriptions
--company-ids <id1,id2>
--job-type fulltime|parttime|contract|internship
--remote
```

Do not combine `--hours-old` and `--easy-apply`; LinkedIn does not allow that combination.

## Step 4: Run the Scraper

Execute the command and capture the terminal output for the summary. Example:

```bash
python tools/jobspy_scraper.py \
  --search "software engineer" \
  --location "San Francisco, CA" \
  --results 25 \
  --output /app/results/linkedin_jobs.csv
```

The script prints progress and a result summary. Keep the raw CSV unchanged so downstream users can inspect or import it.

## Step 5: Interpret Results

Read the CSV and summarize the outcome in `/app/results/summary.md`:

- Search parameters used
- Total jobs found
- Brief table with Title, Company, Location, Salary, Posted, and URL when available
- Output file path
- Any errors, rate-limit warnings, or assumptions

If the CSV has zero rows, suggest broadening the search term, removing a location filter, increasing `--results`, or waiting before retrying if rate limited.

## Step 6: Iterate on Errors (max 3 rounds)

If installation, scraper execution, or result validation fails, iterate up to max 3 rounds. After each fix, rerun the failed step and update `/app/results/validation_report.json`.

| Issue | Fix |
|---|---|
| `ModuleNotFoundError: jobspy` | Run `python3.12 -m pip install -U python-jobspy --break-system-packages`. |
| `tools/jobspy_scraper.py` missing | Copy it from `skills/linkedin-job-scraper/scripts/jobspy_scraper.py` into `tools/`. |
| 0 results returned | Broaden the search term, remove location, increase results, or remove restrictive filters. |
| Rate limited or blocked | Wait a few minutes and avoid repeated large scrapes. |
| `hours_old and easy_apply cannot both be set` | Remove one of the conflicting flags. |
| CSV missing required columns | Re-run the scraper and verify the wrapper writes JobSpy output without post-processing changes. |

After 3 unsuccessful rounds, stop and write the failure details to `summary.md` and `validation_report.json`.

## Step 7: Write Validation Report

Write `/app/results/validation_report.json` with this shape:

```json
{
  "version": "1.0.0",
  "run_date": "<ISO-8601 UTC>",
  "parameters": {
    "search": "<term>",
    "location": "<location or null>",
    "results": <N>,
    "output": "/app/results/linkedin_jobs.csv"
  },
  "stages": [
    {"name": "setup", "passed": true, "message": "Dependencies installed and scraper found"},
    {"name": "scrape", "passed": true, "message": "CSV written"},
    {"name": "summary", "passed": true, "message": "summary.md written"},
    {"name": "final_output_verification", "passed": true, "message": "All required files are non-empty"}
  ],
  "overall_passed": true
}
```

Set `overall_passed` to `false` if any required file is missing, empty, or if the scraper could not complete after the bounded retry loop.

## Final Checklist

Run this verification script before finishing.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/linkedin_jobs.csv" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

python3.12 - <<'PY'
import csv, json, pathlib
base = pathlib.Path('/app/results')
required = ['linkedin_jobs.csv', 'summary.md', 'validation_report.json']
missing = [name for name in required if not (base / name).is_file() or (base / name).stat().st_size == 0]
if missing:
    raise SystemExit(f"missing required outputs: {missing}")
report = json.loads((base / 'validation_report.json').read_text())
if not isinstance(report.get('stages'), list) or 'overall_passed' not in report:
    raise SystemExit('validation_report.json missing stages or overall_passed')
with (base / 'linkedin_jobs.csv').open(newline='') as fh:
    reader = csv.reader(fh)
    header = next(reader, [])
if not header:
    raise SystemExit('linkedin_jobs.csv has no header')
print('PASS: structured validation completed')
PY
```

Checklist:

- [ ] `linkedin_jobs.csv` exists and contains a header row.
- [ ] `summary.md` reports parameters, result count, top matches, and issues.
- [ ] `validation_report.json` has `stages` and `overall_passed`.
- [ ] The final verification script prints PASS for every required file.

## Tips

Prefer narrower searches for high-signal results and broader searches when LinkedIn returns zero rows. Use `--fetch-descriptions` only when the user needs full job descriptions, because it is slower and more likely to trigger rate limits. Save all generated outputs under `/app/results` so the run is auditable and repeatable.
