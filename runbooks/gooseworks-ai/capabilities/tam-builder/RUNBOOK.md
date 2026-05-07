---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/tam-builder/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/tam-builder
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: TAM Builder
  imported_at: '2026-05-03T16:40:21Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: tam-builder
    confidence: high
secrets:
  APOLLO_API_KEY:
    env: APOLLO_API_KEY
    description: Apollo API key for company and people search
    required: true
---

# TAM Builder — Agent Runbook

## Objective

Build and maintain a scored Total Addressable Market using Apollo Company Search. The runbook supports build, refresh, and status modes, scores ICP fit from a JSON configuration, assigns Tier 1/2/3 labels, and builds a persona watchlist for Tier 1-2 accounts using Apollo People Search. It enforces an approval gate before any full export so sample quality, tier distribution, and expected cost are reviewed before broad data collection.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/summary.md` | Executive summary of the TAM run, selected mode, counts, approval state, and output locations |
| `/app/results/validation_report.json` | Structured validation report for setup, config, approval, Apollo calls, scoring, exports, and final checks |
| `/app/results/tam-companies-{date}.csv` | All discovered or refreshed companies with ICP score, tier, status, and scoring factors |
| `/app/results/tam-personas-{date}.csv` | Persona watchlist for Tier 1-2 companies when watchlist generation is enabled |
| `/app/results/tam-status.json` | Read-only status payload for status mode or the final run state for build/refresh mode |

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `results_dir` | `/app/results` | Directory where all required output files are written |
| `config_path` | required | Path to the client or segment JSON config containing company filters, scoring weights, watchlist settings, mode, and caps |
| `mode` | `standard` | One of `test`, `standard`, or `full`; applies page and company caps from the source skill |
| `operation` | `build` | One of `build`, `refresh`, or `status` |
| `require_approval` | `true` | Require explicit user approval before full build or refresh export |
| `max_pages` | config value | Upper bound for Apollo pagination; capped by selected mode |
| `APOLLO_API_KEY` | secret | Apollo API key supplied from the environment; never write it to results |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---:|---|
| `python` | CLI | Yes | Runs validation, scoring, CSV export, and report generation scripts |
| `requests` | Python package | Yes | Calls Apollo Company Search and People Search APIs |
| `APOLLO_API_KEY` | Secret | Yes | Authenticates Apollo API calls using the `x-api-key` header |
| Apollo Company Search | External API | Yes | Discovers matching companies from `POST /api/v1/mixed_companies/search` |
| Apollo People Search | External API | Conditional | Builds the Tier 1-2 persona watchlist from `POST /api/v1/mixed_people/search` |

## Step 1: Environment Setup

1. Create `results_dir` and initialize `summary.md` and `validation_report.json` placeholders.
2. Verify `APOLLO_API_KEY` exists in the environment.
3. Install or verify Python dependencies: `requests` and any local CSV/JSON helpers used by the implementation.
4. Load `config_path` as JSON and validate required top-level keys: `client_name`, `tam_config_name`, `company_filters`, `scoring`, `watchlist`, `mode`, and `max_pages`.
5. Fail fast if the selected `operation` is not `build`, `refresh`, or `status`.

## Step 2: Validate TAM Configuration

Check that scoring weights cover `employee_count_fit`, `industry_fit`, `funding_stage_fit`, `geo_fit`, and `keyword_match`, and that they sum to a sensible total before normalization. Validate that tier thresholds are ordered so Tier 1 is stricter than Tier 2. Enforce mode caps: test mode allows max 1 page and 100 companies, standard mode allows max 50 pages and 5,000 companies, and full mode allows max 200 pages and 20,000 companies.

## Step 3: Status Mode

If `operation=status`, do not call Apollo or mutate any stored data. Read existing TAM output files or local state, summarize active companies, deprecated companies, tier distribution, watchlist size, and most recent refresh timestamp, then write `/app/results/tam-status.json`, `/app/results/summary.md`, and `/app/results/validation_report.json`.

## Step 4: Preview and Sample

Run a preview request against Apollo Company Search using the configured filters, `per_page=100`, and `page=1`. Score the sample companies in memory only, then present total count, estimated page count, mode cap, estimated People Search calls, tier distribution, and representative Tier 1/2 examples. Do not write final CSV exports in this step.

## Step 5: Approval Gate

Before full build or refresh, require explicit user approval after the sample review. The approval must be captured as a clear yes/approve/proceed response in the orchestration transcript or an equivalent machine-readable approval field. If approval is missing, stop after writing summary and validation artifacts that state no export was performed.

## Step 6: Build Mode Pipeline

After approval, page through Apollo Company Search within the selected cap. For each company returned in the `accounts` array, normalize company fields, compute ICP score using the pure scoring function, assign Tier 1 for scores at or above `tier_1_min_score`, Tier 2 for scores at or above `tier_2_min_score`, and Tier 3 otherwise. Export all discovered companies to `/app/results/tam-companies-{date}.csv`.

## Step 7: Refresh Mode Pipeline

For refresh mode, page through the current Apollo search, upsert returned companies, re-score every active match, and detect tier changes. Mark a first missing company with `metadata.refresh_miss_count = 1`, deprecate companies missing from two consecutive refreshes, immediately deprecate companies whose employee count drops to 0, and always exempt companies with `tam_status = converted`. Export the refreshed company table to `/app/results/tam-companies-{date}.csv`.

## Step 8: Persona Watchlist Sync

When `watchlist.enabled` is true, call Apollo People Search for Tier 1-2 companies only, respecting `personas_per_company`, `person_filters`, and `tiers_to_watch`. Pull personas for new Tier 1-2 companies and companies promoted from Tier 3 to Tier 2, disqualify personas at deprecated companies, and stop refreshing personas for companies demoted out of watched tiers. Write `/app/results/tam-personas-{date}.csv`.

## Step 9: Iterate on Errors (max 3 rounds)

If an Apollo request, config validation, scoring assertion, CSV write, or watchlist sync fails, inspect the failed validation stage, apply the smallest targeted fix, and retry that stage. Run at most 3 rounds before stopping with `overall_passed=false` in `/app/results/validation_report.json`.

## Common Fixes

| Issue | Fix |
|---|---|
| Missing `APOLLO_API_KEY` | Stop and request the secret from the runtime environment; do not write a placeholder key |
| Apollo response contains no `accounts` | Confirm Company Search endpoint, request body filters, and pagination fields |
| Scoring weights are incomplete | Add all five scoring dimensions or normalize missing dimensions to zero with an explicit warning |
| Full export attempted before approval | Stop the run and rewrite validation to show approval was required and missing |
| Persona output is empty | Confirm Tier 1-2 companies exist and `watchlist.enabled` is true before treating this as an error |

## Final Checklist

Run this verification script before completing the run:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

if ls "$RESULTS_DIR"/tam-companies-*.csv >/dev/null 2>&1 || [ -s "$RESULTS_DIR/tam-status.json" ]; then
  echo "PASS: TAM output or status output exists"
else
  echo "FAIL: no TAM company export or status output found"
fi
```

The run is complete only when required output files exist, validation includes every stage result, and any skipped export is explained by status mode or a missing approval gate.

## Tips

Start with the sample and approval gate even when the filters look obvious. Apollo searches can return broad matches, and the sample tier distribution is the cheapest way to catch filter or scoring mistakes before writing a full TAM export.

## Source Skill Content

The operational details above were derived from the upstream skill sections: Prerequisites, Config Format, Approval Gate, Build Mode, Refresh Mode, ICP Scoring, Deprecation Rules, Watchlist Persona Sync, Mode Caps, Apollo API Reference, and Output.
