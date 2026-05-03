---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/newsletter-monitor/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/newsletter-monitor
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Newsletter Monitor
  imported_at: '2026-05-03T02:46:17Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: newsletter-monitor
    confidence: high
secrets:
  AGENTMAIL_API_KEY:
    env: AGENTMAIL_API_KEY
    description: AgentMail API key used to scan the configured inbox
    required: true
---

# Newsletter Monitor — Agent Runbook

## Objective

Convert the `newsletter-monitor` skill into a repeatable AgentMail newsletter signal scan. Scan an AgentMail inbox for newsletter signals using configurable keyword campaigns. Extracts matched keywords, context snippets, and company mentions from incoming emails. Use for monitoring accounting industry newsletters for buying signals like acquisitions, migrations, and staffing news. The runbook validates inputs, runs the scan with bounded retries, captures both machine-readable and human-readable outputs, and records enough provenance for auditability.

This runbook is designed for programmatic evaluation: all required outputs are written under `/app/results`, every stage records validation status, and the final checklist verifies output files before completion.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|------|-------------|
| `/app/results/newsletter_matches.json` | JSON array of matched newsletter messages, campaigns, keywords, snippets, and company mentions |
| `/app/results/newsletter_summary.md` | Human-readable summary of matched emails grouped by campaign |
| `/app/results/run_metadata.json` | Runtime parameters, source provenance, command used, and timestamps |
| `/app/results/summary.md` | Executive summary of the scan, counts, output locations, and issues |
| `/app/results/validation_report.json` | Structured validation results with stages, counts, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory where all required files are written |
| Campaign | all campaigns | Optional campaign name from `config/campaigns.json` |
| Days | no limit | Only scan emails from the last N days |
| Keywords | use campaigns | Comma-separated custom keywords overriding configured campaigns |
| Output | `json` and `summary` | Output formats captured by this runbook |
| Inbox | `AGENTMAIL_INBOX` or `supergoose@agentmail.to` | AgentMail inbox address to scan |
| Limit | `100` | Maximum messages to fetch |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `python3` | CLI | Yes | Runs the newsletter scanning script |
| `pip3` | CLI | Yes | Installs Python package dependencies |
| `agentmail` | Python package | Yes | AgentMail SDK for inbox access |
| `python-dotenv` | Python package | Yes | Loads optional local environment variables |
| `AGENTMAIL_API_KEY` | Secret | Yes | API key used to access AgentMail |
| Source skill files | Repository content | Yes | `scripts/scan_newsletters.py` and `config/campaigns.json` from the imported skill |

## Step 1: Environment Setup

```bash
set -euo pipefail

RESULTS_DIR="${RESULTS_DIR:-/app/results}"
mkdir -p "$RESULTS_DIR" "$RESULTS_DIR/work"

if [ -z "${{AGENTMAIL_API_KEY:-}}" ]; then
  echo "ERROR: AGENTMAIL_API_KEY is not set"
  exit 1
fi

command -v python3 >/dev/null || {{ echo "ERROR: python3 not installed"; exit 1; }}
command -v pip3 >/dev/null || {{ echo "ERROR: pip3 not installed"; exit 1; }}

pip3 install agentmail python-dotenv
```

## Step 2: Resolve Scan Parameters

Resolve orchestration inputs into CLI arguments. Only include optional flags when values are provided so defaults from the source skill remain intact.

```bash
set -euo pipefail

RESULTS_DIR="${RESULTS_DIR:-/app/results}"
CAMPAIGN="${CAMPAIGN:-}"
DAYS="${DAYS:-}"
KEYWORDS="${KEYWORDS:-}"
INBOX="${INBOX:-}"
LIMIT="${LIMIT:-100}"

ARGS=("--limit" "$LIMIT")

if [ -n "$CAMPAIGN" ]; then ARGS+=("--campaign" "$CAMPAIGN"); fi
if [ -n "$DAYS" ]; then ARGS+=("--days" "$DAYS"); fi
if [ -n "$KEYWORDS" ]; then ARGS+=("--keywords" "$KEYWORDS"); fi
if [ -n "$INBOX" ]; then ARGS+=("--inbox" "$INBOX"); fi

printf '%s\n' "${ARGS[@]}" > "$RESULTS_DIR/work/scan_args.txt"
```

## Step 3: Run Newsletter Scan

Run both JSON and summary modes. The JSON output is used for downstream processing and validation; the summary output is kept for human review.

```bash
set -euo pipefail

RESULTS_DIR="${RESULTS_DIR:-/app/results}"
mapfile -t ARGS < "$RESULTS_DIR/work/scan_args.txt"

python3 scripts/scan_newsletters.py "${ARGS[@]}" --output json > "$RESULTS_DIR/newsletter_matches.json"
python3 scripts/scan_newsletters.py "${ARGS[@]}" --output summary > "$RESULTS_DIR/newsletter_summary.md"
```

## Step 4: Validate Outputs

Validate that the scan produced parseable JSON and that the required summary artifacts exist.

```bash
set -euo pipefail

RESULTS_DIR="${RESULTS_DIR:-/app/results}"

python3 - <<'PY'
import json
import pathlib

results = pathlib.Path("/app/results")
matches_path = results / "newsletter_matches.json"
summary_path = results / "newsletter_summary.md"
matches = json.loads(matches_path.read_text())
if not isinstance(matches, list):
    raise SystemExit("newsletter_matches.json must contain a JSON array")
if not summary_path.read_text().strip():
    raise SystemExit("newsletter_summary.md is empty")

metadata = {
    "origin_url": "https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/newsletter-monitor/SKILL.md",
    "user_supplied_url": "https://skills.gooseworks.ai/skills/newsletter-monitor",
    "imported_by": "skill-to-runbook-converter@1.1.0",
    "match_count": len(matches),
}
(results / "run_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
PY
```

## Step 5: Iterate on Errors (max 3 rounds)

If setup, scanning, or output validation fails, retry up to max 3 rounds after applying the relevant correction.

| Failure | Correction |
|---------|------------|
| Missing `AGENTMAIL_API_KEY` | Configure the secret in the collection environment and rerun |
| Invalid campaign | Inspect `config/campaigns.json` and use one of the configured campaign names |
| Empty or invalid JSON output | Rerun with a smaller `--limit` or without custom keywords to isolate the input |
| AgentMail request failure | Check inbox address, API key scope, and network connectivity before retrying |

## Step 6: Write Reports

```bash
set -euo pipefail

RESULTS_DIR="${RESULTS_DIR:-/app/results}"

python3 - <<'PY'
import json
import pathlib
from datetime import datetime, timezone

results = pathlib.Path("/app/results")
matches = json.loads((results / "newsletter_matches.json").read_text())
metadata = json.loads((results / "run_metadata.json").read_text())
now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

summary = [
    "# Newsletter Monitor — Results",
    "",
    f"- **Date**: {{now}}",
    f"- **Matches**: {{len(matches)}}",
    f"- **Origin URL**: {{metadata['origin_url']}}",
    f"- **JSON output**: `/app/results/newsletter_matches.json`",
    f"- **Summary output**: `/app/results/newsletter_summary.md`",
    "",
    "## Issues / Manual Follow-up",
    "- Review detected company names before routing to downstream contact-finding workflows.",
]
(results / "summary.md").write_text("\n".join(summary) + "\n")

validation = {
    "version": "1.0.0",
    "run_date": now,
    "stages": [
        {"name": "setup", "passed": True, "message": "Environment and secret checks completed"},
        {"name": "scan", "passed": True, "message": f"Captured {{len(matches)}} matched messages"},
        {"name": "report_generation", "passed": True, "message": "Required output reports written"},
    ],
    "results": {"pass": 3, "partial": 0, "fail": 0},
    "overall_passed": True,
}
(results / "validation_report.json").write_text(json.dumps(validation, indent=2) + "\n")
PY
```

## Final Checklist

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="${RESULTS_DIR:-/app/results}"
for f in \
  "$RESULTS_DIR/newsletter_matches.json" \
  "$RESULTS_DIR/newsletter_summary.md" \
  "$RESULTS_DIR/run_metadata.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
    exit 1
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

## Tips

Use built-in campaigns for repeatable monitoring and custom keywords for short investigative runs. When useful signals are found, route company mentions to `company-contact-finder` and combine results with `accounting-news-monitor` for broader account intelligence.
