---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/signal-scanner/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/signal-scanner
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Signal Scanner
  imported_at: '2026-05-03T02:59:30Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: signal-scanner
    confidence: high
secrets:
  SUPABASE_URL:
    env: SUPABASE_URL
    required: true
  SUPABASE_SERVICE_ROLE_KEY:
    env: SUPABASE_SERVICE_ROLE_KEY
    required: true
  APIFY_TOKEN:
    env: APIFY_TOKEN
    required: false
  ANTHROPIC_API_KEY:
    env: ANTHROPIC_API_KEY
    required: false
---

# Signal Scanner — Agent Runbook

## Objective

Detect buying signals across TAM companies and watchlist personas, then prepare reviewed signal records for downstream activation. The runbook enforces a dry-run-first workflow so signal counts, affected records, Apify spend, and proposed lead-status changes are inspected before any database write. After explicit approval, it runs the scanner with the selected config and records a concise summary plus validation evidence.

This import was resolved from the directory mirror `https://skills.gooseworks.ai/skills/signal-scanner` to the pinned upstream source `https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/signal-scanner/SKILL.md`.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/summary.md` | Executive summary of scan scope, dry-run findings, approval state, and final action |
| `/app/results/validation_report.json` | Structured validation results with stages, messages, and `overall_passed` |
| `/app/results/signal_scan_dry_run.json` | Machine-readable dry-run signal findings and proposed database changes |
| `/app/results/signal_scan_stdout.txt` | Captured scanner console output |
| `/app/results/approval_record.json` | Record of explicit approval before any non-dry-run execution, or skipped status |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| Results directory | `/app/results` | Output directory where all required files are written |
| Config path | `skills/capabilities/signal-scanner/configs/example.json` | JSON config selecting client, signal thresholds, and scan scope |
| Test mode | `true` | Limit execution to 5 companies and 3 people while validating setup |
| Dry run | `true` | Detect signals without database writes; must be true for the first pass |
| Max runs | `50` | Optional Apify run limit override |
| Approval required | `true` | Non-dry-run execution requires explicit user approval after reviewing dry-run output |

## Dependencies

| Dependency | Required | Purpose |
|---|---|---|
| `python` | Yes | Execute the signal scanner script |
| `SUPABASE_URL` | Yes | Connect to the Supabase project |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Read and write TAM, people, signal, and enrichment records |
| `APIFY_TOKEN` | Optional | Enable job, profile, and LinkedIn content scans |
| `ANTHROPIC_API_KEY` | Optional | Enable LLM-assisted LinkedIn content analysis |
| TAM data from `tam-builder` | Yes | Provides companies and watchlist personas to scan |

## Step 1: Environment Setup

1. Create `/app/results` and verify the configured scanner file exists.
2. Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are present.
3. If Apify-backed signals are enabled in the config, verify `APIFY_TOKEN` is present.
4. If LLM content analysis is enabled, verify `ANTHROPIC_API_KEY` is present.
5. Write a setup stage into `/app/results/validation_report.json`.

```bash
mkdir -p /app/results
test -n "$SUPABASE_URL"
test -n "$SUPABASE_SERVICE_ROLE_KEY"
test -f "$CONFIG_PATH"
```

## Step 2: Inspect Config and Scope

Read the config JSON and confirm `client_name`, `signals.*`, and `scan_scope` match the requested run. Summarize enabled signal types, estimated Apify usage, and whether the scan is limited by tier, status, or lead status.

## Step 3: Run Dry-Run Scan

Run the scanner with `--dry-run` first. Use `--test` for initial validation unless the operator explicitly requested full scope.

```bash
python skills/capabilities/signal-scanner/scripts/signal_scanner.py \
  --config "$CONFIG_PATH" \
  --dry-run \
  --test | tee /app/results/signal_scan_stdout.txt
```

Parse or summarize the dry-run output into `/app/results/signal_scan_dry_run.json`, including signal count, signal types, affected companies and people, proposed lead-status updates, and estimated paid enrichment usage.

## Step 4: Present Findings and Require Approval

Present dry-run results to the user before any write. Do not run the scanner without `--dry-run` until the user explicitly approves the exact config and scope. Write `/app/results/approval_record.json` with the approval status, timestamp, and requested scope.

## Step 5: Execute Approved Scan

Only after approval, run the scanner without `--dry-run`. Never pass `--yes` on a first run; reserve it for pre-approved scheduled scans where the user has already validated signal detection logic.

```bash
python skills/capabilities/signal-scanner/scripts/signal_scanner.py \
  --config "$CONFIG_PATH" | tee -a /app/results/signal_scan_stdout.txt
```

## Step 6: Validate Database Effects

Confirm inserted `signals`, `enrichment_log` entries, company signal snapshots, and person `lead_status` changes match the approved dry-run expectations. Flag discrepancies in `summary.md` and set `overall_passed=false` when writes exceed the approved scope.

## Step 7: Iterate on Errors (max 3 rounds)

If setup, dry-run parsing, scanner execution, or database validation fails, apply a targeted fix and repeat the affected step for max 3 rounds. Stop before write execution if failures involve credentials, ambiguous config scope, unexpected paid enrichment volume, or missing approval.

### Common Fixes

| Issue | Fix |
|---|---|
| Missing Supabase credentials | Stop and request `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` |
| Apify signals enabled without token | Disable Apify-backed signals or provide `APIFY_TOKEN` |
| Dry-run output is not machine-readable | Preserve stdout and manually summarize required fields into `signal_scan_dry_run.json` |
| Proposed write scope is larger than expected | Narrow `scan_scope` or run with `--test` |
| User has not approved writes | Do not run without `--dry-run`; write skipped status to `approval_record.json` |

## Final Checklist

Run the following verification before finishing.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/signal_scan_dry_run.json" \
  "$RESULTS_DIR/signal_scan_stdout.txt" \
  "$RESULTS_DIR/approval_record.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

The final validation report must include `overall_passed`, all stage results, and any skipped non-dry-run execution reason.

## Tips

- Always run `--dry-run` first and show the signal count, strongest signals, and affected records before requesting approval.
- Treat `lead_status` and signal snapshot updates as consequential writes because they drive future outreach timing and future diff detection.
- Keep Apify-backed signals disabled for a free first pass when the user is validating config or data coverage.

## Source Skill Notes

### Signal Types

| Priority | Signal | Level | Source | Cost |
|----------|--------|-------|--------|------|
| P0 | Headcount growth (>10% in 90d) | Company | Data diffs | Free |
| P0 | Tech stack changes | Company | Data diffs | Free |
| P0 | Funding round | Company | Data diffs | Free |
| P0 | Job posting for relevant roles | Company | Apify linkedin-job-search | ~$0.001/job |
| P1 | Leadership job change | Person | Apify linkedin-profile-scraper | ~$3/1k |
| P1 | LinkedIn content analysis | Person | Apify linkedin-profile-posts + LLM | ~$2/1k + LLM |
| P1 | LinkedIn profile updates | Person | Apify linkedin-profile-scraper | ~$3/1k |
| P2 | New C-suite hire | Company | Derived from person scans | Free |

### Database Write Policy

**CRITICAL: Never write signals or update lead statuses without explicit user approval.**

The signal scanner writes to multiple tables: `signals` (insert), `enrichment_log` (insert), `companies` (patch snapshots), and `people` (patch lead_status). These writes affect downstream outreach decisions — bad signals lead to bad outreach timing.

**Required flow:**
1. **Always run `--dry-run` first** to detect signals without writing to the database
2. Present the dry-run results to the user: signal count, types, top signals, affected companies/people
3. **Get explicit user approval** before running without `--dry-run`
4. Only then run the actual scan that writes to the database

**Why this matters:**
- Signals drive outreach timing — incorrect signals trigger premature outreach
- `lead_status` changes from `monitoring` to `signal_detected` are hard to undo across many records
- Snapshot updates affect future signal diffs — bad snapshots cascade into future scans
- Enrichment log entries track Apify credit spend

**The agent must NEVER pass `--yes` on a first run.** The `--yes` flag is only for pre-approved scheduled scans where the user has already validated the signal detection logic.

### Usage

```bash
# Dry run first (ALWAYS DO THIS) — detect signals without writing to DB
python skills/capabilities/signal-scanner/scripts/signal_scanner.py \
  --config skills/capabilities/signal-scanner/configs/my-client.json --dry-run

# Full scan (only after user reviews dry-run results and approves)
python skills/capabilities/signal-scanner/scripts/signal_scanner.py \
  --config skills/capabilities/signal-scanner/configs/my-client.json

# Test mode (5 companies max)
python skills/capabilities/signal-scanner/scripts/signal_scanner.py \
  --config configs/example.json --test --dry-run

# Free signals only (skip Apify)
# Set all Apify signals to enabled: false in config
```

### Flags

| Flag | Effect |
|------|--------|
| `--config PATH` | Path to config JSON (required) |
| `--test` | Limit to 5 companies, 3 people |
| `--yes` | Auto-confirm Apify cost prompts. **Only use for pre-approved scheduled scans.** |
| `--dry-run` | Detect signals but don't write to DB. **Always run this first.** |
| `--max-runs N` | Override Apify run limit (default 50) |

### Output



### Activation Score

```
activation_score = strength * recency_multiplier * account_fit

Recency:   <24h = 1.5, 1-3d = 1.2, 3-7d = 1.0, 1-2w = 0.8, 2-4w = 0.5
Account:   Tier 1 = 1.3, Tier 2 = 1.0, Tier 3 = 0.7
```

### Connects To

- **Upstream:** `tam-builder` (provides companies + people)
- **Downstream:** `cold-email-outreach` (acts on signals)
