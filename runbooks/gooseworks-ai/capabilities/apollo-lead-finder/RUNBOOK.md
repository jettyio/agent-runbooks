---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/apollo-lead-finder/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/apollo-lead-finder
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Apollo Lead Finder
  imported_at: '2026-05-03T02:53:43Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: apollo-lead-finder
    confidence: high
secrets:
  APOLLO_API_KEY:
    env: APOLLO_API_KEY
    description: Apollo API key used for People Search, enrichment, list, and contact
      APIs.
    required: true
---

# Apollo Lead Finder — Agent Runbook

## Objective

Run a two-phase Apollo.io prospecting workflow that first uses free People Search to discover ICP-matching leads, then selectively enriches approved contacts to reveal email, phone, LinkedIn URL, and full contact details. The runbook must preserve the source skill's approval gates: no paid enrichment without explicit user confirmation, and no export until the enriched results have been reviewed. It creates Apollo lists when requested, deduplicates against existing contacts by LinkedIn URL, and writes auditable outputs for every run.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/search_manifest.json` | Search configuration, Apollo person IDs, result counts, sample preview, and title distribution from the free search phase |
| `/app/results/enrichment_manifest.json` | Enrichment request batches, approval metadata, credit estimate, and enrichment result summary |
| `/app/results/leads.csv` | Final approved lead export; write an empty CSV with headers if export is not approved |
| `/app/results/apollo_list.json` | Apollo list creation result or a skipped record when list creation is disabled |
| `/app/results/summary.md` | Executive summary of filters, counts, approvals, costs, list/export status, and follow-up recommendations |
| `/app/results/validation_report.json` | Structured validation results with stages, messages, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| Results directory | `/app/results` | Output directory for all required files |
| Apollo API key | `APOLLO_API_KEY` env var | Secret used as the `x-api-key` header on Apollo API requests |
| Client name | user supplied | Human-readable client or campaign name |
| Search config name | user supplied | Stable slug/name for the search configuration |
| ICP segment | user supplied | Segment label used in manifests and summaries |
| Apollo filters | user supplied | Apollo People Search filters such as titles, seniority, locations, employee ranges, and keyword tags |
| Enrichment filters | optional | Local filters such as excluded title substrings applied before paid enrichment |
| Apollo list name prefix | optional | Prefix for any created Apollo list |
| Create Apollo list | `true` | Whether to create a list and add approved contacts |
| Mode | `standard` | One of `test`, `standard`, or `full` |
| Max pages | mode-dependent | Search pagination cap; max 1 for test, 50 for standard, 500 for full |
| Existing contacts CSV | optional | CSV used for LinkedIn URL deduplication before export |

## Dependencies

| Dependency | Required | Purpose |
|---|---|---|
| Python 3.12 | Yes | Run request, CSV, JSON, and validation helpers |
| `requests` | Yes | Call Apollo APIs with retry handling |
| `APOLLO_API_KEY` | Yes | Authenticate Apollo requests |
| Network access to `api.apollo.io` | Yes | People Search, Bulk People Match, list, and contact APIs |
| CSV reader/writer | Yes | Load existing contacts and write final exports |

## Step 1: Environment Setup

1. Create `/app/results` and initialize empty output placeholders for every required file.
2. Verify `APOLLO_API_KEY` is set. If it is missing, stop immediately and write `validation_report.json` with `overall_passed=false`.
3. Normalize the selected mode:

| Mode | Max search pages | Max search results | Max enrichments |
|---|---:|---:|---:|
| `test` | 1 | 100 | 10 |
| `standard` | 50 | 5,000 | 500 |
| `full` | 500 | 50,000 | 2,500 |

## Step 2: Intake and Config

Ask the operator for the ICP and campaign settings before any API call:

1. Target job titles, such as `VP of Sales`, `Head of Growth`, or `Director of Sales`.
2. Seniority levels: `owner`, `founder`, `c_suite`, `partner`, `vp`, `director`, `manager`, `senior`, or `entry`.
3. Company employee ranges in Apollo format, such as `51,200`, `201,500`, `501,1000`, or `1001,5000`.
4. Geographic regions for people or organizations.
5. Industry or keyword tags, such as `SaaS`, `Software`, or `FinTech`.
6. Titles to exclude, such as `intern` or `assistant`.
7. Whether to create an Apollo list.
8. Desired result volume: `test`, `standard`, or `full`.

Map the answers into an Apollo-compatible JSON config and save it into `/app/results/search_manifest.json` before the search starts.

## Step 3: Free People Search

1. Build the Apollo People Search payload from the config using `person_titles`, `person_seniority`, `person_locations`, `organization_num_employees_ranges`, `q_organization_keyword_tags`, `person_not_titles`, `q_organization_name`, and `organization_locations` when supplied.
2. Call `POST https://api.apollo.io/api/v1/mixed_people/api_search` for page 1 with `per_page=100`.
3. Record `total_entries`, the first page preview, and the effective filters in `/app/results/search_manifest.json`.
4. Paginate up to the mode cap, applying local title exclusion filters as results arrive.
5. Store Apollo person IDs for the enrichment phase. The search phase is free and must not reveal emails, phone numbers, LinkedIn URLs, or full names.

## Step 4: Search Review Gate

Present total matches, a sample of preview leads, title distribution, and the planned enrichment count. Ask for explicit approval before continuing. If approval is denied, write final summary and validation files, write an empty `leads.csv` with headers, and skip paid enrichment.

## Step 5: Paid Enrichment

1. Load the approved Apollo person IDs from `/app/results/search_manifest.json`.
2. Load the optional existing contacts CSV and build a LinkedIn URL set for deduplication. If no existing contacts file is provided, record that deduplication was skipped.
3. Display the exact enrichment count and credit estimate. Require explicit approval again before calling Bulk People Match.
4. Call `POST https://api.apollo.io/api/v1/people/bulk_match` in batches of 10 person IDs.
5. Handle `429` responses by respecting the `Retry-After` header and retrying bounded batches.
6. Save raw batch status, successful matches, failures, and credit estimates to `/app/results/enrichment_manifest.json`.

## Step 6: Deduplicate and Review

Filter enriched leads whose LinkedIn URLs already exist in the supplied contacts file. Present net-new count, email coverage, representative enriched leads, and company coverage. Ask for explicit approval before writing contacts, creating list membership, or exporting the final CSV.

## Step 7: Apollo List and Contact Export

Only after approval:

1. Create a list with `POST https://api.apollo.io/api/v1/labels` when list creation is enabled.
2. Add approved contacts with `POST https://api.apollo.io/api/v1/contacts`, attaching the list ID when available.
3. Write `/app/results/leads.csv` with stable headers for name, title, company, email, phone, LinkedIn URL, location, company domain, and Apollo IDs.
4. Write `/app/results/apollo_list.json` with the created list result or a skipped record.

## Step 8: Review and Refine

Summarize total matching profiles, new leads found after deduplication, Apollo list details, enriched count, email coverage, and the top approved leads. Recommend specific filter adjustments when the search is too broad, too narrow, low quality, or has low email coverage.

## Step 9: Iterate on Errors (max 3 rounds)

If any API call, validation check, or output write fails, inspect the failing stage, apply the smallest targeted fix, and retry that stage for max 3 rounds. Stop before paid API calls if the failure affects approval state, cost estimation, or filter correctness.

### Common Fixes

| Issue | Fix |
|---|---|
| Missing `APOLLO_API_KEY` | Ask the operator to configure the secret and stop without making API calls |
| Search returns too many irrelevant leads | Add seniority, employee range, geography, keyword tags, or excluded titles |
| Search returns too few leads | Broaden titles, remove location filters, or expand employee ranges |
| Low email coverage | Enrich a larger approved sample or adjust the ICP to more discoverable roles |
| Apollo rate limit | Respect `Retry-After`, reduce batch pressure, and resume from the last saved batch |
| Existing contacts CSV lacks LinkedIn URLs | Record deduplication as partial and proceed only after user approval |

## Step 10: Write Reports

Write `/app/results/summary.md` with the final filters, counts, approvals, estimated credits, actual enrichment count, list/export state, and any follow-up recommendations. Write `/app/results/validation_report.json` with all setup, search, approval, enrichment, export, and reporting stages.

## Final Checklist

Run this verification script before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/search_manifest.json" \
  "$RESULTS_DIR/enrichment_manifest.json" \
  "$RESULTS_DIR/leads.csv" \
  "$RESULTS_DIR/apollo_list.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

Confirm these items:

- `summary.md` states whether paid enrichment and export were approved.
- `validation_report.json` includes every stage and an `overall_passed` boolean.
- `search_manifest.json` contains total matches, sample preview, filters, and Apollo person IDs.
- `enrichment_manifest.json` contains credit estimate, batch status, and enrichment outcome.
- `leads.csv` exists, even when export was not approved.
- `apollo_list.json` records the created list or the reason list creation was skipped.

## Tips

Always run free search first, then require explicit approval before any credit-consuming enrichment. Treat Apollo list creation and CSV export as separate approval-gated steps so the operator can review quality before contacts are written anywhere.
