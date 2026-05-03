---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/kol-engager-icp/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/kol-engager-icp
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: KOL Engager ICP
  imported_at: '2026-05-03T02:53:54Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: kol-engager-icp
    confidence: high
secrets:
  APIFY_API_TOKEN:
    env: APIFY_API_TOKEN
    required: true
---

# KOL Engager ICP — Agent Runbook

## Objective

Find ICP-fit leads from key opinion leader audiences on LinkedIn by selecting one relevant, high-engagement post per KOL, scraping reactors and commenters, filtering by role and ICP signals, enriching the strongest profiles, and exporting classified leads. This runbook keeps costs bounded by using one selected post per KOL and explicit hard caps for KOL count and enrichment volume. Use it when an operator needs to turn a list of KOL LinkedIn profiles into a reviewed CSV of Likely ICP, Possible ICP, Unknown, and Tech Vendor contacts.

Source summary: Find ICP-fit leads from KOL audiences on LinkedIn. Given a list of KOLs, scrapes their most relevant high-engagement post from the last 30 days, extracts engagers (reactors + commenters), pre-filters by position, enriches top profiles, and ICP-classifies. Cost-controlled: 1 post per KOL. Use when someone wants to "find leads from KOL audiences" or "scrape engagers from influencer posts" or after running kol-discovery.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/summary.md` | Executive summary of the run, configuration used, lead counts, and follow-up recommendations |
| `/app/results/validation_report.json` | Structured validation results for setup, probe, pipeline execution, outputs, and review |
| `/app/results/kol_engager_config.json` | Resolved client configuration used by the pipeline |
| `/app/results/kol_engagers.csv` | Exported lead list from the pipeline |
| `/app/results/pipeline_log.md` | Notes from probe, selected posts, cost confirmation, and refinement decisions |

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| Results directory | `/app/results` | Directory where all required output files must be written |
| Client name | required | Slug used for configuration and output naming |
| Product or service description | required | What the user sells; used to classify ICP fit |
| Topic keywords | required | 3-5 terms used to select relevant KOL posts |
| Target industries or verticals | required | Industries that qualify as ICP |
| Target job titles | required | Roles that should pass the pre-filter |
| Excluded titles | optional | Roles to reject before enrichment |
| Competitors and vendor terms | optional | Terms used to identify tech vendors or non-buyers |
| Geographic focus | optional | Country or region filter applied after enrichment |
| KOL LinkedIn URLs | required | KOL profile URLs from discovery output or manual input |
| Mode | `standard` | One of `test`, `standard`, or `full`; controls hard caps |

## Dependencies

| Dependency | Required | Purpose |
|---|---|---|
| Python 3 | Yes | Runs the KOL engager pipeline script |
| `APIFY_API_TOKEN` | Yes | Authenticates Apify actors |
| `harvestapi/linkedin-profile-posts` | Yes | Scrapes recent posts from each KOL profile |
| `harvestapi/linkedin-company-posts` | Yes | Scrapes reactions and comments from selected posts |
| `harvestapi/linkedin-profile-scraper` | Yes | Enriches selected LinkedIn profiles |
| Source repository scripts | Yes | Provides `skills/kol-engager-icp/scripts/kol_engager_icp.py` |

## Step 1: Environment Setup

Verify the required secret and create the output directories before collecting inputs.

```bash
test -n "$APIFY_API_TOKEN" || { echo "ERROR: APIFY_API_TOKEN is not set"; exit 1; }
mkdir -p /app/results
mkdir -p skills/kol-engager-icp/configs
mkdir -p skills/kol-engager-icp/output
```

Initialize `/app/results/validation_report.json` with a `setup` stage. Mark it failed and stop if the Apify token or pipeline script is unavailable.

## Step 2: Intake

Ask for the ICP criteria and KOL input:

1. Product or service description.
2. Topic keywords for post relevance filtering.
3. Target industries or verticals.
4. Target job titles or roles.
5. Titles to exclude.
6. Competitors and tech vendor terms to filter out.
7. Geographic focus.
8. KOL LinkedIn profile URLs.

Write the resolved configuration to `/app/results/kol_engager_config.json` and copy it to `skills/kol-engager-icp/configs/{client-name}.json`.

```json
{
  "client_name": "example",
  "topic_keywords": ["freight automation", "dispatch operations"],
  "topic_patterns": ["freight.*automat", "dispatch.*oper"],
  "icp_keywords": ["freight", "logistics", "3pl"],
  "target_titles": ["vp operations", "head of logistics", "coo"],
  "exclude_titles": ["software engineer", "data scientist"],
  "tech_vendor_keywords": ["competitor-name", "saas founder"],
  "country_filter": "United States",
  "kol_urls": ["https://www.linkedin.com/in/kol-1/"],
  "days_back": 30,
  "max_posts_per_kol": 20,
  "max_kols": 10,
  "max_enrichment_profiles": 200,
  "mode": "standard"
}
```

## Step 3: Probe Engager Scraping

Run a probe before spending enrichment budget.

```bash
python3 skills/kol-engager-icp/scripts/kol_engager_icp.py \
  --config skills/kol-engager-icp/configs/{client-name}.json \
  --probe
```

Append the selected sample post, sample engager count, and any actor errors to `/app/results/pipeline_log.md`.

## Step 4: Run the Pipeline

Run the pipeline in the selected mode. Start with test mode unless the user has confirmed cost and volume.

```bash
python3 skills/kol-engager-icp/scripts/kol_engager_icp.py \
  --config skills/kol-engager-icp/configs/{client-name}.json \
  --test
```

For a confirmed standard or full run, remove `--test` and add `--yes` after recording the user's confirmation in `/app/results/pipeline_log.md`.

## Step 5: Review Results

Present and record:

| Review item | Required notes |
|---|---|
| Per-KOL breakdown | Which KOL post generated the most qualified leads |
| Pre-filter stats | How many engagers passed position filtering |
| ICP breakdown | Counts by Likely ICP, Possible ICP, Unknown, and Tech Vendor |
| Top 15 leads | Name, role, company, KOL source, engagement type, and useful comment text |

Copy the final CSV to `/app/results/kol_engagers.csv`.

## Step 6: Refine on Quality or Cost (max 3 rounds)

If the result quality is poor or the cost is too high, iterate up to max 3 rounds:

| Symptom | Adjustment |
|---|---|
| Too many tech vendors | Add terms to `tech_vendor_keywords` |
| Missing ICP leads | Broaden `icp_keywords` or `target_titles` |
| Low-engagement posts selected | Make `topic_keywords` less restrictive |
| Too expensive | Lower `max_enrichment_profiles` or switch to test mode |

After each round, append the change and resulting counts to `/app/results/pipeline_log.md`.

## Step 7: Final Checklist

Run the final output verification and update `/app/results/validation_report.json`.

```bash
echo "FINAL OUTPUT VERIFICATION"
for f in \
  /app/results/summary.md \
  /app/results/validation_report.json \
  /app/results/kol_engager_config.json \
  /app/results/kol_engagers.csv \
  /app/results/pipeline_log.md; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f"
  fi
done
```

The run is complete only when every mandatory file exists, the CSV contains the expected columns, and `validation_report.json` has `overall_passed: true` or clearly explains the failed stage.

## Common Fixes

| Issue | Fix |
|---|---|
| Probe returns no engagers | Confirm the first KOL has posts in the last 30 days and broaden `topic_keywords` |
| Enrichment volume is too high | Lower `max_enrichment_profiles` before standard or full mode |
| Country filter removes most leads | Verify enriched profile locations and adjust geographic focus |
| CSV is missing comment text | Confirm comment scraping is enabled and record reactions separately from comments |

## Tips

- Keep the one-post-per-KOL rule unless the user explicitly accepts higher cost.
- Commenters are usually higher intent than reactors; prioritize them in review.
- Treat tech vendors and competitor employees as exclusions even when their titles otherwise match.
