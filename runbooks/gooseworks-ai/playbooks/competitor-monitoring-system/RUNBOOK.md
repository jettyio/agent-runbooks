---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/playbooks/competitor-monitoring-system/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/competitor-monitoring-system
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Competitor Monitoring System
  imported_at: '2026-05-03T02:45:11Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: competitor-monitoring-system
    confidence: high
secrets: {}
---

# Competitor Monitoring System — Agent Runbook

## Objective

Set up and run ongoing competitive intelligence monitoring for a client. Tracks competitor content, ads, reviews, social, and product moves. This runbook turns that playbook into a repeatable Jetty workflow for defining a competitor watchlist, collecting an initial baseline, running recurring monitoring cycles, and producing action-oriented intelligence reports. It expects a client name, competitor list, and client context, then writes the watchlist, baseline, report, summary, and validation artifacts under `/app/results`.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/competitor-watchlist.md` | Competitor watchlist with company URLs, products, executive profiles, content channels, review profiles, and ad library links. |
| `/app/results/competitor-baseline.md` | Initial competitive baseline summarizing content, ads, reviews, social signals, and product moves. |
| `/app/results/competitor-report.md` | Current-cycle intelligence report with key changes, recommended actions, and detailed findings. |
| `/app/results/summary.md` | Executive summary of the monitoring run, inputs used, output paths, and unresolved issues. |
| `/app/results/validation_report.json` | Structured validation report with stages, results, and `overall_passed`. |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `results_dir` | `/app/results` | Directory where all required output files are written. |
| `client_name` | required | Client or brand being protected and monitored. |
| `competitors` | required | List of 3-7 competitors to track. |
| `client_context` | required | Client positioning, priority products, target keywords, and known differentiators. |
| `monitoring_cadence` | `weekly` | Cadence for the current cycle: weekly, bi-weekly, monthly, or quarterly. |
| `reporting_period` | current week | Date range represented by the intelligence report. |

## Dependencies

| Dependency | Required | Purpose |
|---|---|---|
| Web search or browsing capability | Yes | Discover competitor content, ad libraries, public posts, reviews, and product updates. |
| `competitor-intel` skill | Recommended | Composite competitor baseline across social, content, review, and discussion sources. |
| `google-ad-scraper` skill | Recommended | Collect current Google ad creative and messaging. |
| `review-site-scraper` skill | Recommended | Pull G2, Capterra, Trustpilot, or similar review data. |
| `blog-feed-monitor` skill | Recommended | Track new competitor blog and content output. |
| `linkedin-profile-post-scraper` and `twitter-mention-tracker` skills | Recommended | Monitor executive and company social messaging. |
| `reddit-post-finder` and `hacker-news-scraper` skills | Optional | Track community discussion, complaints, and praise. |

## Step 1: Environment Setup

1. Create `results_dir` if it does not exist.
2. Confirm `client_name`, `competitors`, and `client_context` are present.
3. Normalize competitor names and URLs into a consistent list.
4. Create a working folder for any intermediate notes under `/app/results/work`.

## Step 2: Define Competitor Watchlist

Write `/app/results/competitor-watchlist.md`. For each competitor, include company name, URL, key products or features, founder and executive LinkedIn profiles, known content channels, review profiles, and Meta or Google ad library pages.

## Step 3: Initial Competitive Baseline

For each competitor, collect a baseline using available competitor-intelligence, ad, review, social, and content tools. Compare findings against the client context and write `/app/results/competitor-baseline.md` with current positioning, messaging, campaign themes, review sentiment, and notable product moves.

## Step 4: Configure Monitoring Cadence

Use this cadence matrix for the current run:

| What to Monitor | Frequency | Tooling | What to Look For |
|---|---|---|---|
| Blog and content output | Weekly | `blog-feed-monitor` | New posts, topic shifts, SEO attacks. |
| Social media posts | Weekly | `linkedin-profile-post-scraper`, `twitter-mention-tracker` | Messaging changes, product announcements, engagement patterns. |
| Reddit and Hacker News mentions | Weekly | `reddit-post-finder`, `hacker-news-scraper` | User sentiment, complaints, praise, feature requests. |
| Ad creative changes | Bi-weekly | `google-ad-scraper`, Meta Ad Library web research | New campaigns, messaging shifts, spend changes. |
| Review sentiment | Monthly | `review-site-scraper` | New reviews, rating trends, common complaints. |

## Step 5: Run Monitoring Cycle

Run the relevant monitors for `monitoring_cadence`. Compare new data against the baseline or previous cycle, then flag significant changes: new product features, pricing changes, new content targeting client keywords, negative review trends, new ad campaigns, and founder or executive public statements about strategy.

## Step 6: Produce Intelligence Report

Write `/app/results/competitor-report.md` with these sections:

```markdown
# Competitor Intelligence — <client_name> — <reporting_period>

## Key Changes
- <Competitor and evidence-backed change>

## Recommended Actions
- <Action tied to the observed change>

## Detailed Findings
<Per-competitor breakdown>
```

## Step 7: Human Checkpoints

After setup, ask for review of the competitor watchlist and monitoring plan. After each report, ask for review of recommended actions before execution. Mark any unreviewed recommendation as pending in `/app/results/summary.md`.

## Step 8: Iterate on Errors (max 3 rounds)

If validation fails, inspect `/app/results/validation_report.json`, correct only the missing or malformed artifact, and re-run validation. Repeat for max 3 rounds, then stop and report any remaining failure in `/app/results/summary.md`.

## Common Fixes

| Issue | Fix |
|---|---|
| Missing watchlist fields | Add URLs, products, executive profiles, content channels, review profiles, and ad library links for every competitor. |
| Baseline lacks evidence | Add source references or dated observations for each claim. |
| Report has recommendations without findings | Tie each recommendation to a specific observed competitor change. |
| Required output missing | Create the file under `/app/results` and include a short explanation if data was unavailable. |

## Final Checklist

Run this verification before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/competitor-watchlist.md" \
  "$RESULTS_DIR/competitor-baseline.md" \
  "$RESULTS_DIR/competitor-report.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

## Tips

Keep competitor monitoring evidence-based and dated. Separate observed changes from recommended responses so reviewers can approve actions before execution.
