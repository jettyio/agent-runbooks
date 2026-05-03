---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/competitor-content-tracker/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/competitor-content-tracker
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Competitor Content Tracker
  imported_at: '2026-05-03T02:53:54Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: competitor-content-tracker
    confidence: high
secrets:
  APIFY_API_TOKEN:
    required: false
    description: Optional BYO Apify API token; Gooseworks proxy may be used by default
      when available.
---

# Competitor Content Tracker — Agent Runbook

## Objective
Monitor competitor content across blogs, LinkedIn, and Twitter/X on a recurring basis. Surfaces new posts, trending topics, and content gaps you can own. Chains blog-feed-monitor, linkedin-profile-post-scraper, and twitter-mention-tracker. Use when you want a weekly digest of what competitors are publishing and which topics are generating engagement. The runbook collects recent competitor publishing activity from blogs, LinkedIn, and Twitter/X, then synthesizes a weekly digest with engagement signals, recurring themes, and content gaps. It preserves the source skill workflow while adding deterministic setup, output, and validation steps for Jetty programmatic evaluation.

## REQUIRED OUTPUT FILES (MANDATORY)

All files MUST be written under `/app/results` and must be non-empty.

| File | Description |
|---|---|
| `/app/results/summary.md` | Executive summary of tracked competitors, date range, top themes, content gaps, and recommended actions |
| `/app/results/competitor-content-digest.md` | Structured markdown digest with per-competitor blog, LinkedIn, and Twitter/X findings |
| `/app/results/raw_findings.json` | Normalized raw findings collected from blog, LinkedIn, and Twitter/X sources |
| `/app/results/config.json` | Resolved run configuration used for the tracker |
| `/app/results/validation_report.json` | Programmatic validation report for setup, collection, synthesis, and output verification |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `results_dir` | `/app/results` | Directory where all required output files are written |
| `client_name` | required | Client or workspace name used to label the digest |
| `competitors` | required | Competitor company names to track |
| `blog_urls` | required | Competitor blog or feed URLs |
| `linkedin_profiles` | optional | LinkedIn profile URLs for founders, executives, or company voices |
| `twitter_handles` | optional | Twitter/X handles to inspect |
| `days_back` | `7` | Lookback window; use `30` for a first run |
| `keywords` | optional | Priority terms used to rank relevant posts |
| `output_mode` | `highlights` | `highlights` for top findings or `full` for a complete digest |

## Dependencies

| Dependency | Required | Purpose |
|---|---|---|
| Python 3 | Yes | Run collection scripts and validation checks |
| `blog-feed-monitor` | Yes | Collect recent posts from competitor blogs or RSS feeds |
| `linkedin-profile-post-scraper` | Optional | Collect LinkedIn profile posts when profile URLs are provided |
| `twitter-mention-tracker` | Optional | Collect Twitter/X posts when handles are provided |
| Apify access | Optional | LinkedIn and Twitter/X scraping may use Apify; set `APIFY_API_TOKEN` when not using a managed proxy |

## Step 1: Environment Setup

Create the output directory, validate required inputs, and persist the resolved configuration.

```bash
mkdir -p /app/results
python3 - <<'PY'
import json, pathlib, sys
config = {
  "client_name": "<client_name>",
  "competitors": ["<competitor_name>"],
  "blog_urls": ["<competitor_blog_url>"],
  "linkedin_profiles": [],
  "twitter_handles": [],
  "days_back": 7,
  "keywords": [],
  "output_mode": "highlights"
}
if not config["competitors"] or not config["blog_urls"]:
    raise SystemExit("competitors and blog_urls are required")
pathlib.Path("/app/results/config.json").write_text(json.dumps(config, indent=2))
PY
```

## Step 2: Scrape Blog Content

Run `blog-feed-monitor` for each competitor blog URL. Collect post title, publish date, URL, excerpt, and any keyword matches.

```bash
python3 skills/capabilities/blog-feed-monitor/scripts/scrape_blogs.py \
  --urls "<competitor_blog_url>" \
  --days "<days_back>" \
  --keywords "<keywords>" \
  --output summary
```

## Step 3: Scrape LinkedIn Posts

When LinkedIn profiles are provided, run `linkedin-profile-post-scraper` and collect post preview, date, reactions, comments, and URL. Skip this step with a clear note in `raw_findings.json` when no profiles are configured.

```bash
python3 skills/capabilities/linkedin-profile-post-scraper/scripts/scrape_linkedin_posts.py \
  --profiles "<linkedin_url_1>,<linkedin_url_2>" \
  --days "<days_back>" \
  --max-posts 20 \
  --output summary
```

## Step 4: Scrape Twitter/X

When Twitter/X handles are provided, run `twitter-mention-tracker` for each handle. Collect tweet text, date, likes, reposts, and URL.

```bash
python3 skills/capabilities/twitter-mention-tracker/scripts/search_twitter.py \
  --query "from:<handle>" \
  --since "<YYYY-MM-DD>" \
  --until "<YYYY-MM-DD>" \
  --max-tweets 20 \
  --output summary
```

## Step 5: Analyze and Synthesize

Normalize the channel outputs into `/app/results/raw_findings.json`. For each competitor, identify new blog posts, top LinkedIn post, top tweet, recurring themes, and content format patterns. Across competitors, identify shared trending topics, coverage gaps, topics the client owns, and engagement benchmarks.

Write `/app/results/competitor-content-digest.md` using this structure:

```markdown
# Competitor Content Digest — Week of <DATE>

## Summary
- <N> new blog posts tracked across <N> competitors
- Top trending topic: <topic>
- Biggest content gap: <topic>

## <Competitor Name>

### Blog
- <Post Title> — <Date> — <URL>

### LinkedIn
- <Top post summary and engagement>

### Twitter/X
- <Top tweet summary and engagement>

## Content Gap Analysis

| Topic | Competitors covering | You covering |
|---|---|---|
| <topic> | <competitors> | <yes/no> |

## Recommended Actions
1. <specific content opportunity>
2. <response or alternative take to publish>
```

## Step 6: Evaluate Outputs

Validate that every required file exists, that the digest contains a summary, competitor sections, content gap analysis, and recommended actions, and that `raw_findings.json` is valid JSON.

```bash
python3 - <<'PY'
import json, pathlib
results = pathlib.Path('/app/results')
checks = []
for name in ['summary.md', 'competitor-content-digest.md', 'raw_findings.json', 'config.json']:
    p = results / name
    checks.append({'name': name, 'passed': p.exists() and p.stat().st_size > 0})
json.loads((results / 'raw_findings.json').read_text())
digest = (results / 'competitor-content-digest.md').read_text()
for section in ['## Summary', '## Content Gap Analysis', '## Recommended Actions']:
    checks.append({'name': section, 'passed': section in digest})
report = {
  'version': '1.0.0',
  'stages': checks,
  'overall_passed': all(c['passed'] for c in checks)
}
(results / 'validation_report.json').write_text(json.dumps(report, indent=2))
if not report['overall_passed']:
    raise SystemExit('validation failed')
PY
```

## Step 7: Iterate on Errors (max 3 rounds)

If validation fails, inspect `/app/results/validation_report.json`, fix the missing or malformed output, and rerun Step 6. Stop after max 3 rounds and report unresolved failures in `/app/results/summary.md`.

### Common Fixes

| Issue | Fix |
|---|---|
| Missing competitor section | Re-run synthesis using every configured competitor name |
| Empty social channel | Mark the channel as skipped or unavailable, then continue with blog findings |
| Invalid JSON | Re-emit with `json.dumps(..., indent=2)` |
| No recommended actions | Add 1-3 concrete content opportunities derived from observed gaps |

## Step 8: Scheduling

For recurring use, run weekly. Mondays at 8am local time are recommended.

```bash
0 8 * * 1 python3 run_skill.py competitor-content-tracker --client <client-name>
```

## Step 9: Final Checklist

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/competitor-content-digest.md" \
  "$RESULTS_DIR/raw_findings.json" \
  "$RESULTS_DIR/config.json" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

## Final Checklist

- [ ] `summary.md` includes run date, tracked competitors, top themes, and issues
- [ ] `competitor-content-digest.md` includes summary, per-competitor findings, content gap analysis, and recommended actions
- [ ] `raw_findings.json` is valid JSON and records skipped channels explicitly
- [ ] `validation_report.json` exists and `overall_passed` reflects the checks
- [ ] FINAL OUTPUT VERIFICATION prints PASS for every required output file

## Tips

Use a 30-day lookback on the first run to establish baseline themes, then switch to the default 7-day weekly cadence. Treat LinkedIn and Twitter/X as optional enrichment channels when API or scraping access is unavailable.
