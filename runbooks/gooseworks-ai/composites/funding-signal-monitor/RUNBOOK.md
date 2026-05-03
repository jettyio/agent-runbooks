---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/funding-signal-monitor/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/funding-signal-monitor
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Funding Signal Monitor
  imported_at: '2026-05-03T02:53:58Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: funding-signal-monitor
    confidence: high
secrets:
  APIFY_API_TOKEN:
    required: false
    description: Optional Apify API token for Twitter and Reddit scraper sources.
---

# Funding Signal Monitor — Agent Runbook

## Objective

Detect recently funded startups that may be ready for outreach after a Seed, Series A, Series B, or Series C raise. This runbook aggregates public funding signals from web search, Hacker News, Twitter, Reddit, and manual verification sources, then deduplicates and scores companies by fit, recency, source confidence, and outreach angle. The final output is a ranked report of qualified companies with enough provenance for a human reviewer to validate before any outreach is launched.

Source description: Monitor web sources for Series A-C funding announcements. Aggregates signals from TechCrunch, Crunchbase (via web search), Twitter, Hacker News, and LinkedIn. Filters by stage, amount, and industry. Returns qualified recently-funded companies ready for outreach.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|------|-------------|
| `/app/results/funding_signal_report.md` | Ranked markdown report of qualified funding signals and outreach angles |
| `/app/results/funding_signal_companies.json` | Structured company records, scores, source URLs, and qualification notes |
| `/app/results/search_provenance.json` | Query log, source list, timestamps, and deduplication evidence |
| `/app/results/summary.md` | Executive summary of run parameters, totals, strongest signals, and caveats |
| `/app/results/validation_report.json` | Programmatic validation results for required files and data quality checks |

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `results_dir` | No | `/app/results` | Output directory for all required files |
| `target_stages` | Yes | `Series A, Series B, Series C` | Comma-separated funding stages to include |
| `target_industries` | No | `all` | Optional industry filter such as SaaS, AI, fintech, or healthtech |
| `min_amount` | No | `none` | Optional minimum funding amount filter, for example `$5M` |
| `lookback_days` | No | `7` | Number of days back to search |
| `output_path` | No | `/app/results/funding_signal_report.md` | Markdown report output path |
| `max_results` | No | `15` | Maximum ranked companies to include in the executive report |

## Dependencies

| Dependency | Required | Purpose |
|------------|----------|---------|
| Python 3.12+ | Yes | Runs validation and optional source helper scripts |
| `requests` | Yes | Calls public APIs such as Hacker News Algolia and fetches verification pages |
| Web search capability | Yes | Finds TechCrunch, Crunchbase, VentureBeat, company blog, and press release announcements |
| Hacker News Algolia API | No | Supplements web search with HN funding discussions |
| `APIFY_API_TOKEN` | No | Enables optional Twitter and Reddit scraper searches |

## Step 1: Environment Setup

Create the results directory, install lightweight dependencies, and capture the resolved inputs.

```bash
mkdir -p /app/results
python -m pip install requests
python - <<'PY'
import json, os, datetime
params = {
  "target_stages": os.getenv("TARGET_STAGES", "Series A, Series B, Series C"),
  "target_industries": os.getenv("TARGET_INDUSTRIES", "all"),
  "min_amount": os.getenv("MIN_AMOUNT", "none"),
  "lookback_days": int(os.getenv("LOOKBACK_DAYS", "7")),
  "results_dir": "/app/results",
  "created_at": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
}
open("/app/results/search_provenance.json", "w").write(json.dumps({"parameters": params, "queries": [], "sources": []}, indent=2))
PY
```

## Step 2: Configure Search Strategy

Build 4-6 search queries per requested stage and industry. Include direct announcement phrases such as `raised Series A`, `announces Series B funding`, `startup funding round`, and `excited to announce raised`, plus industry-specific variants when `target_industries` is not `all`.

Record every query, source type, timestamp, and result count in `/app/results/search_provenance.json`.

## Step 3: Multi-Source Search

Run searches across available sources in parallel where the execution environment permits it:

| Source | Query Pattern | Required Fields |
|--------|---------------|-----------------|
| Web search | Funding phrases and industry filters | Company, amount, stage, date, lead investors, source URL |
| Hacker News | `raised funding Series` and stage variants | Company, title, points, comments, date, URL |
| Twitter | `excited to announce` plus funding terms | Company, post URL, date, quoted amount or stage |
| Reddit | Startup and SaaS communities with funding terms | Company, subreddit, post URL, engagement |
| LinkedIn or company blog | Manual verification for top candidates | Announcement URL and company-authored source |

If `APIFY_API_TOKEN` is unavailable, skip Twitter and Reddit with an explicit note in the provenance file instead of failing the run.

## Step 4: Consolidate and Deduplicate

Normalize company names, announcement dates, stages, and amounts. Merge records that refer to the same company and keep every source URL in a `sources` array.

For each candidate, evaluate stage, amount, industry, cloud likelihood, team-size estimate, and recency. A company appearing in more than one source should receive higher confidence than a single-source result.

## Step 5: Score and Rank Companies

Apply this scoring rubric:

| Signal | Score |
|--------|-------|
| Appears in multiple independent sources | +3 |
| Stage exactly matches `target_stages` | +2 |
| Industry matches `target_industries` | +2 |
| High cloud likelihood such as SaaS, AI, fintech, or developer tools | +1 |
| Announcement is within the last 3 days | +1 |
| Stage outside target range | -1 |
| Non-tech industry unless explicitly targeted | -2 |

Sort by score descending. Break ties by recency, then number of independent sources.

## Step 6: Generate Outputs

Write `/app/results/funding_signal_companies.json` with structured records:

```json
[
  {
    "rank": 1,
    "company": "ExampleCo",
    "amount": "$12M",
    "stage": "Series A",
    "announcement_date": "2026-05-01",
    "investors": ["Example Ventures"],
    "industry": "AI infrastructure",
    "sources": ["web", "hn"],
    "source_urls": ["https://example.com/announcement"],
    "cloud_likelihood": "High",
    "score": 9,
    "outreach_angle": "Scale fast with fresh capital"
  }
]
```

Write `/app/results/funding_signal_report.md` with a ranked table containing rank, company, amount, stage, date, investors, industry, sources, cloud likelihood, and outreach angle.

## Step 7: Human Review Guardrails

Do not launch outreach from this runbook. Present the ranked list and require explicit user confirmation before chaining to contact discovery or cold-email workflows. Mark any result without a primary announcement URL as `needs_manual_verification`.

## Step 8: Iterate on Errors (max 3 rounds)

If validation fails or the report contains fewer qualified companies than expected, perform targeted retries for max 3 rounds:

| Issue | Fix |
|-------|-----|
| No results found | Broaden stages, extend lookback to 14 or 30 days, or remove the industry filter |
| Too many weak results | Add an industry filter, raise `min_amount`, or focus on Series B+ |
| Optional scraper failed | Continue with web search and Hacker News, noting the skipped source |
| Duplicate companies remain | Tighten normalized company-name matching and compare announcement URLs |
| Missing primary source | Search company blog, press release, investor blog, or SEC/newswire source |

## Final Checklist

Run this verification script before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/funding_signal_report.md" \
  "$RESULTS_DIR/funding_signal_companies.json" \
  "$RESULTS_DIR/search_provenance.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
python - <<'PY'
import json, pathlib, sys
companies = json.loads(pathlib.Path("/app/results/funding_signal_companies.json").read_text())
if not isinstance(companies, list):
    sys.exit("FAIL: company output is not a list")
required = {"rank", "company", "stage", "sources", "score", "outreach_angle"}
missing = [c.get("company", "<unknown>") for c in companies if not required.issubset(c)]
if missing:
    sys.exit(f"FAIL: missing required company fields for {missing}")
print("PASS: company records include required fields")
PY
```

## Tips

- Run weekly for best coverage because funding announcements have a short news cycle.
- Web search is the primary source; Hacker News, Twitter, and Reddit are supplementary confidence signals.
- Multi-source appearances are the strongest signals and should rank above single-source mentions.
- Combine reviewed results with contact discovery only after a human selects companies to pursue.
