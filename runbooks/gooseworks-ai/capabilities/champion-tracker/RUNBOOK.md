---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/champion-tracker/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/champion-tracker
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Champion Tracker
  imported_at: '2026-05-03T02:54:10Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: champion-tracker
    confidence: high
secrets:
  APIFY_API_TOKEN:
    env: APIFY_API_TOKEN
    description: Apify API token used by champion_tracker.py for LinkedIn profile
      enrichment.
    required: true
---

# Champion Tracker — Agent Runbook

## Objective

Track product champions for job changes and qualify their new companies against ICP. Takes a CSV of known champions (with LinkedIn URLs), creates a baseline snapshot via Apify enrichment, then detects when champions move to new companies. Scores new companies on a 0-4 ICP fit scale. Outputs a downloadable CSV of movers with qualification verdicts. This runbook turns the source skill into a repeatable Jetty workflow that prepares inputs, runs the tracker in a bounded way, validates the produced CSV, and writes auditable summaries. It supports both first-run baseline creation and recurring checks for job changes, then records ICP scoring outputs for follow-up.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/champion_changes.csv` | CSV of detected champion job changes and ICP qualification fields. |
| `/app/results/champion_tracking_report.json` | Structured run metadata, mode, row counts, validation details, and output paths. |
| `/app/results/summary.md` | Executive summary of the tracking run, findings, and follow-up notes. |
| `/app/results/validation_report.json` | Programmatic validation report with stages and overall pass/fail status. |

## Parameters

| Parameter | Default | Required | Description |
|---|---:|---:|---|
| `results_dir` | `/app/results` | No | Directory where all required output files are written. |
| `mode` | `check` | No | `init` creates or refreshes the baseline; `check` detects job changes against the baseline. |
| `champions_csv` | `champions.csv` | Yes for `init` | CSV with `name` and `linkedin_url`; optional `original_company`, `original_title`, `email`, `source`, and `notes`. |
| `output_csv` | `/app/results/champion_changes.csv` | No | Destination for detected mover records. |
| `dry_run` | `false` | No | When true, estimate cost and validate inputs without mutating baseline snapshots or writing final change results. |

## Dependencies

| Dependency | Required | Purpose |
|---|---:|---|
| `python3` | Yes | Runs the champion tracker CLI and validation helpers. |
| `APIFY_API_TOKEN` | Yes | Enables LinkedIn profile enrichment through Apify. |
| `champion_tracker.py` | Yes | Source skill script that initializes baselines, checks movers, and emits CSV output. |
| `review-site-scraper` skill | Optional | Helps discover initial champions from review sites. |
| `linkedin-post-research` skill | Optional | Helps discover product champions from LinkedIn posts. |
| Fiber or ContactOut | Optional | Resolves names and companies to LinkedIn profile URLs during discovery. |

## Step 1: Environment Setup

1. Create `results_dir` and confirm it is writable.
2. Verify `APIFY_API_TOKEN` is present in the environment.
3. Locate `champion_tracker.py`; prefer the source skill path `skills/champion-tracker/scripts/champion_tracker.py`.
4. Validate that `python3` can start the script without import errors.

```bash
mkdir -p /app/results
test -n "$APIFY_API_TOKEN" || { echo "ERROR: APIFY_API_TOKEN is not set"; exit 1; }
python3 skills/champion-tracker/scripts/champion_tracker.py --help >/tmp/champion-tracker-help.txt
```

## Step 2: Prepare Champion Inputs

For a first run, build `champions.csv` from known customer champions, review-site authors, LinkedIn product advocates, or CRM exports. The CSV must include `name` and `linkedin_url`; include `original_company`, `original_title`, `email`, `source`, and `notes` when available so downstream outreach has context.

## Step 3: Initialize Baseline

Run this step when no baseline exists or when intentionally refreshing the baseline. First run a dry-run cost estimate, then create the baseline only after the estimate is acceptable.

```bash
python3 skills/champion-tracker/scripts/champion_tracker.py init -i champions.csv --dry-run
python3 skills/champion-tracker/scripts/champion_tracker.py init -i champions.csv
```

## Step 4: Check for Job Changes

For recurring runs, detect movers against the latest baseline and write the normalized CSV to the required output path.

```bash
python3 skills/champion-tracker/scripts/champion_tracker.py check --dry-run
python3 skills/champion-tracker/scripts/champion_tracker.py check -o /app/results/champion_changes.csv
```

## Step 5: Validate Output CSV

Confirm that the mover CSV exists, has the required columns, and can be parsed. Treat an empty CSV with headers as a valid no-movers result.

```python
import csv, json, pathlib
path = pathlib.Path("/app/results/champion_changes.csv")
required = {
    "champion_name", "linkedin_url", "previous_company", "previous_title",
    "new_company", "new_title", "change_detected_date", "position_start_date",
    "days_since_change", "icp_score", "icp_verdict", "icp_notes", "email", "notes"
}
with path.open(newline="") as fh:
    reader = csv.DictReader(fh)
    missing = sorted(required - set(reader.fieldnames or []))
    rows = list(reader)
if missing:
    raise SystemExit(f"missing columns: {missing}")
pathlib.Path("/app/results/champion_tracking_report.json").write_text(json.dumps({
    "output_csv": str(path),
    "row_count": len(rows),
    "required_columns_present": True,
}, indent=2) + "\n")
```

## Step 6: Review ICP Qualification

Inspect every mover with `icp_verdict` of `Strong Fit`, `Good Fit`, or `Possible Fit`. Prioritize recent role changes, senior titles, and companies with clear B2B sales, growth, or revenue motions.

## Step 7: Write Reports

Write `/app/results/summary.md` with the mode, baseline/check status, mover count, highest-priority accounts, and any enrichment or scoring issues. Write `/app/results/validation_report.json` with stage-by-stage pass/fail results for setup, input validation, tracker execution, CSV validation, and report generation.

## Step 8: Iterate on Errors (max 3 rounds)

If setup, tracker execution, or CSV validation fails, apply one targeted fix and rerun the failed step. Stop after max 3 rounds and write the failure into both `summary.md` and `validation_report.json` rather than continuing with incomplete outputs.

## Common Fixes

| Issue | Fix |
|---|---|
| `APIFY_API_TOKEN` missing | Add the secret to the runtime environment and rerun Step 1. |
| `champions.csv` missing required columns | Add `name` and `linkedin_url`, then rerun the dry-run init command. |
| Apify cost estimate is unexpectedly high | Reduce the champion list or inspect duplicate LinkedIn URLs before running without `--dry-run`. |
| Output CSV missing headers | Rerun `check -o /app/results/champion_changes.csv` and inspect script errors. |

## Final Checklist

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/champion_changes.csv" \
  "$RESULTS_DIR/champion_tracking_report.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
python3 - <<'PY'
import csv, json, pathlib
csv_path = pathlib.Path("/app/results/champion_changes.csv")
with csv_path.open(newline="") as fh:
    reader = csv.DictReader(fh)
    assert "champion_name" in (reader.fieldnames or [])
json.loads(pathlib.Path("/app/results/validation_report.json").read_text())
print("PASS: CSV headers and validation JSON parse")
PY
```

## Tips

- Use `--dry-run` before any baseline initialization or recurring check to review cost.
- Keep the champion CSV focused on verified product advocates; noisy inputs create noisy mover signals.
- Treat ICP scoring as triage, then verify account fit before outreach.

## Source Skill Notes

### Source: Champion Tracker

Detect when product champions change jobs and qualify their new companies against ICP.

### Source: Script Usage

### Source: Output CSV Columns

| Column | Description |
|--------|-------------|
| champion_name | Full name |
| linkedin_url | LinkedIn profile URL |
| previous_company | Company at baseline |
| previous_title | Title at baseline |
| new_company | Current company (changed) |
| new_title | Current title |
| change_detected_date | Date this check was run |
| position_start_date | When they started the new role |
| days_since_change | Days since new position started |
| icp_score | 0-4 ICP qualification score |
| icp_verdict | Strong Fit / Good Fit / Possible Fit / Weak Fit |
| icp_notes | Scoring breakdown |
| email | Email if available |
| notes | Original notes from champion CSV |

### Source: ICP Scoring (0-4)

| Signal | Points | What it checks |
|--------|--------|----------------|
| B2B signal | 1.0 | Title contains sales/SDR/revenue/growth keywords |
| Outbound motion | 1.0 | Sales leadership title (VP Sales, Head of Growth, etc.) |
| Company size | 1.0 / 0.5 | SMB/mid-market = 1.0; unknown = 0.5 benefit-of-doubt |
| Seniority | 1.0 | VP, Director, Head of, C-level, Founder |

**Verdicts**: Strong Fit (>=3) / Good Fit (>=2) / Possible Fit (>=1.5) / Weak Fit (<1.5)

### Source: Cost

- ~$3 per 1,000 LinkedIn profiles enriched
- 50-80 champions ≈ $0.15-0.25 per run
- `--dry-run` always shows cost before any API calls

### Source: File Structure

```
skills/champion-tracker/
  SKILL.md                    # This file
  scripts/
    champion_tracker.py       # Main CLI script
  input/
    champions_template.csv    # Template for manual additions
  snapshots/                  # Created at runtime
    baseline.json             # Latest full snapshot
    archive/                  # Timestamped copies
  output/                     # Created at runtime
    changes-YYYY-MM-DD.csv    # Generated output
```

### Source: Dependencies

- Reuses `LinkedInEnricher` from `skills/lead-qualification/scripts/enrich_leads.py`
- Falls back to inline implementation if import fails
- Requires: `requests` (Python package), `APIFY_API_TOKEN` (env var)
