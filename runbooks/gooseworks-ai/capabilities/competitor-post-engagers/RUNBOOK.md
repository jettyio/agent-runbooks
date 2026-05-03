---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/competitor-post-engagers/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/competitor-post-engagers
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Competitor Post Engagers
  imported_at: '2026-05-03T02:53:53Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: competitor-post-engagers
    confidence: high
secrets: {}
---

# Competitor Post Engagers — Agent Runbook

## Objective

Find leads by scraping engagers from a competitor's top LinkedIn posts. Given one or more company page URLs, scrapes recent posts, ranks by engagement, selects the top N, extracts all reactors and commenters, ICP-classifies, and exports CSV. Use when someone wants to "find leads engaging with competitor content" or "scrape people who interact with [company]'s LinkedIn posts". The workflow collects competitor LinkedIn activity, ranks recent posts by engagement, extracts reactors and commenters, classifies them against ICP criteria, and exports a reviewable lead list with validation metadata.
This runbook was requested from a directory mirror at `https://skills.gooseworks.ai/skills/competitor-post-engagers` and imported from the resolved upstream source `https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/competitor-post-engagers/SKILL.md`.


## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/competitor_post_engagers.csv` | CSV of extracted and ICP-classified LinkedIn engagers |
| `/app/results/summary.md` | Executive summary of companies processed, top posts selected, counts, and issues |
| `/app/results/validation_report.json` | Structured validation stages and pass/fail status |

## Parameters

| Parameter | Environment / Path | Description |
|---|---|---|
| Results directory | `/app/results` | Where mandatory outputs are written |
| Target company LinkedIn URLs | `TARGET_COMPANY_LINKEDIN_URLS` | One or more competitor LinkedIn company page URLs |
| Top posts per company | `TOP_POSTS_PER_COMPANY` | Number of high-engagement recent posts to process |
| ICP criteria | `ICP_CRITERIA` | Fit rules used to classify people and companies |
| Output CSV path | `/app/results/competitor_post_engagers.csv` | Exported lead list |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| LinkedIn access or approved scraping provider | External service | Yes | Used to retrieve company posts, reactions, and comments within applicable terms |
| CSV writer | Runtime capability | Yes | Used to write the final lead export |
| ICP criteria supplied by operator | Input | Yes | Used to score and label extracted profiles |
| `/app/results` | Filesystem | Yes | Stores mandatory outputs |

## Step 1: Environment Setup

Verify all required inputs are present before starting. Create the results directory, confirm any browser automation or scraping credentials required by the operator are available, and initialize a structured validation report.

```bash
mkdir -p /app/results
test -n "${TARGET_COMPANY_LINKEDIN_URLS:-}" || echo "TARGET_COMPANY_LINKEDIN_URLS should contain one or more LinkedIn company page URLs"
```

## Step 2: Intake

Ask the user these questions:

## Step 3: Run the Pipeline

```bash
python3 skills/competitor-post-engagers/scripts/competitor_post_engagers.py \
  --config competitor-post-engagers-config.json \
  [--test] [--yes] [--skip-company-enrich] [--top-n 3] [--max-runs 30]
```

**Flags:**
- `--config` (required) — path to config JSON
- `--test` — small limits (20 posts, 50 profiles, 1 top post)
- `--yes` — skip cost confirmation prompts
- `--skip-company-enrich` — skip Apollo company enrichment step (saves credits)
- `--top-n` — override top_n_posts from config
- `--max-runs` — override Apify run limit

## Step 4: Pipeline Steps

**Step 1: Scrape company posts + engagers** — For each company URL, one Apify call using `harvestapi/linkedin-company-posts` with `scrapeReactions: true, scrapeComments: true`. Returns posts, reactions, and comments in a single dataset.

**Step 2: Rank & select top posts** — Filter posts by time window (`days_back`), rank by total engagement (reactions + comments), select top N per company. Then extract engagers (reactors + commenters) only from those selected posts. Deduplication by name. Score engagers by position:
- `+3` Commenter (higher intent)
- `+2` Position matches ICP keywords
- `-5` Position matches exclude keywords

**Step 3: Company enrichment (Apollo)** — Extract unique company names from engagers, call `apollo.enrich_organization(name=...)` for each. Returns industry, employee count, description, and location. ~1 Apollo credit per unique company. Merge data back to all engagers from that company. Skip with `--skip-company-enrich` or `"enrich_companies": false`.

**Step 4: ICP classify & export** — Classify as Likely ICP / Possible ICP / Unknown / Tech Vendor. Uses both headline keyword matching AND company industry data (from Step 3) — if the engager's company industry matches `industry_keywords`, they're classified as "Likely ICP" regardless of role. Export CSV.

## Step 5: Review & Refine

Present results:
- **Post selection** — which posts were chosen and why (engagement counts, preview)
- **Per-company breakdown** — how many leads from each competitor
- **ICP breakdown** — counts by tier
- **Top 15 leads** — name, role, company, engagement type

Common adjustments:
- **Too many irrelevant leads** — tighten `icp_keywords` or add `exclude_keywords`
- **Missing ICP leads** — broaden `icp_keywords`
- **Wrong posts selected** — increase `top_n_posts` or adjust `days_back`
- **Too expensive** — use `--test` mode or lower `max_reactions`/`max_comments`

## Step 6: Output

CSV exported to `{output_dir}/{name}-engagers-{date}.csv`:

| Column | Description |
|--------|-------------|
| Name | Full name |
| LinkedIn URL | Profile link |
| Role | Parsed from headline |
| Company | Parsed from headline |
| Company Industry | From Apollo enrichment |
| Company Size | Estimated employee count from Apollo |
| Company Description | Short company description from Apollo |
| Company Location | City, State, Country from Apollo |
| Source Page | Which competitor's page |
| Post URL | Link to the specific post |
| Post Preview | First 120 chars of post content |
| Engagement Type | Comment or Reaction |
| Comment Text | Their comment (personalization gold) |
| ICP Tier | Likely ICP / Possible ICP / Unknown / Tech Vendor |
| Pre-Filter Score | Priority score from pre-filter |

## Step 7: Iterate on Errors (max 3 rounds)

If extraction, classification, or output validation fails, inspect the failed stage, apply the smallest targeted correction, and rerun only the affected stage. Stop after max 3 rounds and record unresolved issues in `summary.md` and `validation_report.json`.

## Final Checklist

Final step 8: run the final output verification before ending the task.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in "$RESULTS_DIR/summary.md" "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

## Common Fixes

| Issue | Fix |
|---|---|
| No posts found for a company | Confirm the LinkedIn URL is a company page and widen the recent-post window |
| Engager extraction returns too few people | Check scraping-provider limits, authentication, and whether the post has public reactions/comments |
| ICP labels are inconsistent | Restate the ICP criteria and rerun classification for the affected rows only |
| CSV validation fails | Normalize headers, remove duplicate profile URLs, and rerun final validation |

## Tips

Scrape all recent posts for each company in one collection pass, rank locally, and only then extract engagers from the top posts to control cost while preserving lead quality.
