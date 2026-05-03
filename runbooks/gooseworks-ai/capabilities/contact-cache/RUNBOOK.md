---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/contact-cache/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/contact-cache
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: contact-cache
  imported_at: '2026-05-03T02:53:59Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: contact-cache
    confidence: high
secrets: null
---

# contact-cache — Agent Runbook

## Objective
Use the Contact Cache skill to maintain a CSV-backed database of identified and contacted people across outreach strategies. The workflow prevents duplicate outreach by checking LinkedIn URLs and email addresses before adding or updating records. It also supports status tracking, strategy-level exports, and summary statistics for recurring lead-generation work.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/contact_cache_summary.json` | Machine-readable summary of requested cache operations, including counts and any duplicate matches. |
| `/app/results/contact_cache_export.csv` | CSV export of the cache after operations complete, when export is requested or available. |
| `/app/results/summary.md` | Human-readable execution summary, including cache path, operations performed, and follow-up notes. |
| `/app/results/validation_report.json` | Structured validation results for setup, operation execution, and output verification. |

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| Results directory | `/app/results` | Directory where all required output files must be written. |
| Cache script | `skills/contact-cache/scripts/cache.py` | Path to the Contact Cache CLI script in the source skill checkout. |
| Cache data file | `skills/contact-cache/data/contacts.csv` | CSV file where contacts are stored; created automatically by the cache script on first use. |
| Operation | `stats` | Operation to run: `check`, `add`, `update`, `export`, or `stats`. |
| LinkedIn URLs | empty | Comma-separated LinkedIn profile URLs used for duplicate checks, adds, or updates. |
| Emails | empty | Comma-separated email addresses used for duplicate checks, adds, or updates. |
| Strategy | empty | Strategy label to attach to added contacts or use for filtered exports. |
| Export format | `csv` | Export format, either `csv` or `json`. |

## Dependencies

| Dependency | Required | Purpose |
|---|---|---|
| `python3` | Yes | Runs the Contact Cache CLI script. |
| Source skill checkout | Yes | Provides `skills/contact-cache/scripts/cache.py` and the CSV data directory. |
| Writable `/app/results` | Yes | Stores required Jetty output artifacts. |

## Step 1: Environment Setup

```bash
mkdir -p /app/results
python3 --version
if [ ! -f skills/contact-cache/scripts/cache.py ]; then
  echo "ERROR: skills/contact-cache/scripts/cache.py not found"
  exit 1
fi
```

Verify that the source skill checkout is available from the current working directory and that `/app/results` is writable before running cache operations.

## Step 2: Inspect Inputs

Normalize any supplied LinkedIn URLs, email lists, status values, and strategy names. If no explicit operation is supplied, run `stats` first so the output files still describe the current cache state.

Valid statuses from the source skill:

`new`, `qualified`, `contacted`, `replied`, `meeting_booked`, `converted`, `not_interested`

## Step 3: Run the Contact Cache Operation

Use the source CLI exactly as intended by the skill. Common commands are:

```bash

Capture stdout and stderr for the summary and validation report. If an operation fails, stop before writing success results and include the failed command and exit code in `validation_report.json`.

## Step 4: Export Current Cache State

After any successful mutation, export the cache so downstream systems can inspect the final state.

```bash
python3 skills/contact-cache/scripts/cache.py export --format csv > /app/results/contact_cache_export.csv
python3 skills/contact-cache/scripts/cache.py stats
```

If the cache is empty or the export command is unavailable, create `/app/results/contact_cache_export.csv` with only headers and record the reason in `summary.md`.

## Step 5: Write Structured Results

Write `/app/results/contact_cache_summary.json` with operation metadata, duplicate counts, added or updated contact IDs when available, export path, and the cache data path. The cache stores contacts in:

Contacts are stored in `skills/contact-cache/data/contacts.csv`. The file is auto-created on first use.

Dedup is by LinkedIn URL (preferred) or email. Both are normalized and hashed (SHA256, first 16 chars) to produce a stable `contact_id`.

## Step 6: Iterate on Errors (max 3 rounds)

If setup, execution, export, or validation fails, apply one targeted fix and retry, for max 3 rounds. Common fixes are creating the missing data directory, correcting a status to one of the valid values, quoting comma-separated URL or email arguments, or switching the export format to `csv`.

## Step 7: Final Checklist

## Final Checklist

Run this verification script before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in   "$RESULTS_DIR/contact_cache_summary.json"   "$RESULTS_DIR/contact_cache_export.csv"   "$RESULTS_DIR/summary.md"   "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

The run is complete only when the script prints `PASS` for every required output file and `validation_report.json` has `overall_passed: true`.

## Common Fixes

| Issue | Fix |
|---|---|
| Cache script missing | Run from the repository root that contains `skills/contact-cache/scripts/cache.py`. |
| Invalid status | Use one of the valid statuses listed in Step 2. |
| Duplicate contact detected | Treat the existing contact as the source of truth and use `update` instead of `add`. |
| Export file missing | Re-run `export --format csv` and redirect stdout to `/app/results/contact_cache_export.csv`. |

## Tips

Prefer LinkedIn URL as the deduplication key when both LinkedIn URL and email are available. Use the `strategy` field consistently so recurring campaigns can export and audit their own contact history.
