---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/company-contact-finder/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/company-contact-finder
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: company-contact-finder
  imported_at: '2026-05-03T02:53:41Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: company-contact-finder
    confidence: high
secrets: null
---

# company-contact-finder — Agent Runbook

## Objective

Find decision-makers at a specific company using Apollo, Crustdata, Fiber, and PDL people search via Gooseworks MCP. Given a company name and target titles, returns a list of contacts with name, title, LinkedIn URL, and location. This runbook converts that skill into a Jetty-compatible contact discovery workflow with explicit inputs, bounded fallback behavior, and required output files. The agent should return decision-maker contacts for one target company while tracking provider provenance and validation status.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|------|-------------|
| `/app/results/contacts.json` | Normalized contact records with provider provenance and match reasons |
| `/app/results/summary.md` | Executive summary of search strategy, contacts found, gaps, and manual follow-up |
| `/app/results/validation_report.json` | Structured validation results for setup, searches, deduplication, and output verification |

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `/app/results` | No | `/app/results` | Directory where required output files are written |
| `company_name` | Yes | -- | The company to search (e.g., "EisnerAmper") |
| `company_linkedin_url` | No | -- | Company LinkedIn URL for disambiguation |
| `target_titles` | Yes | -- | List of titles to find (e.g., ["Partner", "Controller", "VP Finance"]) |
| `num_results` | No | 10 | How many contacts to return |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| Gooseworks MCP | MCP tools | Yes | Provides Apollo, Crustdata, Fiber, and PDL people-search capabilities |
| `apollo_person_search` | MCP tool | Yes | Primary low-cost people-search provider |
| `crustdata_people_search` | MCP tool | No | Fallback people-search provider |
| `fiber_search_people` | MCP tool | No | Fallback people-search provider |
| `pdl_person_search` | MCP tool | No | Final fallback provider for hard-to-find contacts |
| JSON writer | Agent capability | Yes | Writes normalized `contacts.json` and validation output |

## Step 1: Environment Setup

Verify the operator provided the required inputs and that Gooseworks MCP people-search tools are available in the active agent environment.

```bash
mkdir -p /app/results
test -n "${company_name:-}" || echo "company_name must be supplied by the orchestrator"
test -n "${target_titles:-}" || echo "target_titles must be supplied by the orchestrator"
```

Record the resolved company name, optional company LinkedIn URL, target titles, and requested result count before making search calls.
## Step 2: Iterate on Errors (max 3 rounds)

If the search result set is empty or low confidence, perform at most 3 rounds of targeted recovery:

1. Tighten company disambiguation with the company LinkedIn URL or verified domain.
2. Broaden target titles with equivalent seniority terms.
3. Move to the next fallback provider in the order defined above.

Stop iterating once enough contacts are collected or the 3-round limit is reached. Record each attempted provider and why it was accepted or rejected.
## Step 3: Write Results

Write normalized contacts to `/app/results/contacts.json` and a concise executive summary to `/app/results/summary.md`.

Each contact record should include `name`, `title`, `company`, `linkedin_url`, `location`, `email` when available, `source_provider`, and a short `match_reason` explaining why the contact fits the requested titles.
## Final Checklist

Run this verification script before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in "$RESULTS_DIR/contacts.json" "$RESULTS_DIR/summary.md" "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

Confirm that the contacts are deduplicated, title matches are explained, and fallback attempts are reflected in the validation report.

## Common Fixes

| Issue | Fix |
|-------|-----|
| Company name returns unrelated contacts | Add `company_linkedin_url` or a verified company domain before retrying |
| Too few senior contacts | Add adjacent titles with the same seniority, such as Managing Director, Head of, VP, or C-level |
| Duplicate people across providers | Deduplicate by LinkedIn URL first, then by normalized name plus company |
| Provider result lacks LinkedIn URL | Keep the record only if title, company, and location are strong enough to justify the match |

## Tips

Start with Apollo because it is the cheapest provider, then fall back only when the result count or match quality is insufficient. Keep provider names on every contact so reviewers can audit where each lead came from.
