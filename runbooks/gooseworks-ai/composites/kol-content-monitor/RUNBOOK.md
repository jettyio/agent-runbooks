---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/kol-content-monitor/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/kol-content-monitor
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: KOL Content Monitor
  imported_at: '2026-05-03T02:46:04Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: kol-content-monitor
    confidence: high
secrets:
  APIFY_API_TOKEN:
    env: APIFY_API_TOKEN
    description: Apify API token used by upstream LinkedIn scraping workflows.
    required: false
---

# KOL Content Monitor - Agent Runbook

## Objective

Track what key opinion leaders in a target market are posting on LinkedIn and Twitter/X, then identify trending narratives, high-engagement posts, early signals, and content actions. This runbook converts the upstream `kol-content-monitor` skill into a Jetty-friendly workflow that gathers KOL inputs, runs the upstream scrapers, clusters topics, and produces a content-monitor report. It is designed for marketing teams, founders, and operators who want to join relevant conversations while the topics are still active.

Source description: Track what key opinion leaders (KOLs) in your space are posting on LinkedIn and Twitter/X. Surfaces trending narratives, high-engagement topics, and early signals of emerging conversations before they peak. Chains linkedin-profile-post-scraper and twitter-mention-tracker. Use when a marketing team wants to ride trends rather than create them from scratch, or when a founder wants to know which topics are resonating with their audience.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/kol-monitor-report.md` | Final KOL content monitor report with tracked KOLs, trending topics, top posts, emerging topics, and recommended content actions. |
| `/app/results/kol-monitor-data.json` | Normalized source data, including fetched LinkedIn posts, Twitter/X posts, filters applied, clusters, and signal classifications. |
| `/app/results/content-calendar.md` | Optional trigger-based content calendar derived from "Ride the Wave" opportunities. If skipped, include a short note explaining why. |
| `/app/results/summary.md` | Executive summary of the run, key trends, data coverage, and any limitations. |
| `/app/results/validation_report.json` | Structured validation report for setup, inputs, scraping, clustering, report generation, and final file checks. |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `results_dir` | `/app/results` | Output directory where all required files must be written. |
| `config_path` | `kol-monitor.json` | JSON file containing KOL names, LinkedIn URLs, Twitter/X handles, keywords, thresholds, and output settings. |
| `days_back` | `7` | Number of days of posts to inspect for a weekly monitor. Use `30` for a first run. |
| `min_reactions` | `20` | Minimum LinkedIn reaction count to include. Twitter/X likes use half this threshold. |
| `output_path` | `/app/results/kol-monitor-report.md` | Destination markdown report path. |
| `include_calendar` | `true` | Whether to write `/app/results/content-calendar.md`. |

## Dependencies

| Dependency | Type | Required | Notes |
|---|---|---|---|
| `python3` | CLI | Yes | Runs local scripts and validation helpers. |
| `linkedin-profile-post-scraper` | Upstream skill | Yes | Scrapes recent LinkedIn posts for tracked KOL profiles. |
| `twitter-mention-tracker` | Upstream skill | Recommended | Scrapes recent Twitter/X posts for tracked handles. |
| `kol-discovery` | Upstream skill | Optional | Use when the operator does not already have a KOL list. |
| `APIFY_API_TOKEN` | Secret | Conditional | Required when LinkedIn scraping uses Apify-backed collectors. |
| Network access | External service | Yes | Required for LinkedIn, Twitter/X, and any scraper APIs. |

## Step 1: Environment Setup

Create the output directory, load the monitor config, and verify the tools and credentials needed for the selected sources.

```bash
mkdir -p /app/results
test -f "${CONFIG_PATH:-kol-monitor.json}" || {
  echo "ERROR: missing KOL monitor config"
  exit 1
}
command -v python3 >/dev/null || {
  echo "ERROR: python3 is required"
  exit 1
}
```

Validate the config before scraping. It must include at least one KOL with a LinkedIn URL or Twitter/X handle, `days_back`, `min_reactions`, and an output path. If LinkedIn profiles are present and the upstream scraper requires Apify, verify `APIFY_API_TOKEN` is set without printing the secret.

## Step 2: Intake and Config Normalization

Read `config_path` and normalize each KOL entry into a consistent schema:

```json
{
  "name": "Lenny Rachitsky",
  "linkedin": "https://www.linkedin.com/in/lennyrachitsky/",
  "twitter": "@lennysan"
}
```

If no KOL list is provided, pause and run `kol-discovery` first, then resume this runbook with the discovered names and profile URLs. Apply defaults of `7` days for weekly monitoring, `30` days for first-run analysis, `20` LinkedIn reactions, and `10` Twitter/X likes unless the user supplied different values.

## Step 3: Scrape LinkedIn Posts

Run `linkedin-profile-post-scraper` for all configured LinkedIn profiles:

```bash
python3 skills/linkedin-profile-post-scraper/scripts/scrape_linkedin_posts.py \
  --profiles "<url1>,<url2>,<url3>" \
  --days "<days_back>" \
  --max-posts 20 \
  --output json
```

Filter out posts below `min_reactions`. Keep author, date, text, URL, reaction count, comment count, and any available repost/share count in `/app/results/kol-monitor-data.json`.

## Step 4: Scrape Twitter/X Posts

For each configured handle, run `twitter-mention-tracker` over the same date window:

```bash
python3 skills/twitter-mention-tracker/scripts/search_twitter.py \
  --query "from:<handle>" \
  --since "<YYYY-MM-DD>" \
  --until "<YYYY-MM-DD>" \
  --max-tweets 20 \
  --output json
```

Filter tweets below `min_reactions / 2` likes. If a handle is missing or the scraper fails for one KOL, record the failure in `validation_report.json` and continue with the remaining sources.

## Step 5: Topic Clustering

Group all retained posts by topic or theme:

1. Extract a one-to-three-word topic label for each post.
2. Merge semantically similar labels.
3. Count how many KOLs discussed each topic and how many posts belong to it.
4. Rank clusters by total engagement across LinkedIn reactions and Twitter/X likes.

Classify signals using these rules:

| Signal | Rule |
|---|---|
| `CONVERGENCE` | Three or more KOLs discussed the same topic in the selected period. |
| `SPIKE` | Topic volume is at least twice the comparable previous period when historical data is available. |
| `UNDERDOG` | One KOL covered a topic that no other tracked KOL covered. |
| `CONTROVERSY` | Comment-to-reaction ratio is unusually high or replies indicate active debate. |

## Step 6: Generate the Monitor Report

Write `/app/results/kol-monitor-report.md` with:

```markdown
# KOL Content Monitor - Week of [DATE]

## Tracked KOLs
[N] KOLs | [N] LinkedIn posts | [N] tweets | Period: [date range]

## Trending Topics This Week

### 1. [Topic Name] - CONVERGENCE SIGNAL
- **KOLs discussing:** [Name 1], [Name 2], [Name 3]
- **Total posts:** [N] | **Total engagement:** [N] reactions/likes
- **Trend direction:** New this week / Growing / Stable

**Best posts on this topic:**
> "[Post excerpt]"
- [Author], [Date] | [N] reactions

**Content opportunity:** [How to contribute to this conversation]
```

Also include high-engagement posts, emerging topics to watch, and recommended content actions for this week and next week.

## Step 7: Build Trigger-Based Content Calendar

When `include_calendar=true`, write `/app/results/content-calendar.md` with one entry for each strong "Ride the Wave" opportunity:

```markdown
## [Topic]
- **Best post format:** LinkedIn insight post / tweet thread / blog
- **Suggested hook:** [hook]
- **Supporting points:** [three bullets from product, market, or founder experience]
- **Ideal publish date:** [within three days of peak]
```

If there are no actionable opportunities, write the file with a short explanation rather than leaving it empty.

## Step 8: Iterate on Errors (max 3 rounds)

If scraping, clustering, or report validation fails, perform at most 3 rounds of targeted fixes:

1. Read the failed stage from `/app/results/validation_report.json`.
2. Fix only the failed input, scraper invocation, parser mapping, or report section.
3. Re-run the failed step and downstream report generation.
4. Stop after 3 rounds and preserve a clear failure message if the issue remains.

Partial social-source failures are acceptable when at least one platform produced usable data; the summary must name missing platforms or profiles.

## Step 9: Scheduling

For a weekly Friday afternoon monitor, schedule the equivalent command after validating the config:

```bash
0 14 * * 5 python3 run_skill.py kol-content-monitor --client <client-name>
```

The Friday cadence catches the week's peaks and leaves time to draft over the weekend.

## Final Checklist

Run this verification script before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="${RESULTS_DIR:-/app/results}"
for f in \
  "$RESULTS_DIR/kol-monitor-report.md" \
  "$RESULTS_DIR/kol-monitor-data.json" \
  "$RESULTS_DIR/content-calendar.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

Checklist:

- `kol-monitor-report.md` includes tracked KOLs, trending topics, top posts, emerging topics, and recommended content actions.
- `kol-monitor-data.json` records normalized source data and applied filters.
- `content-calendar.md` exists, even when no calendar entries were produced.
- `summary.md` names source coverage, strongest signals, and limitations.
- `validation_report.json` includes each stage, pass/fail results, and `overall_passed`.

## Common Fixes

| Issue | Fix |
|---|---|
| Missing KOL profiles | Run `kol-discovery` or ask the operator for LinkedIn URLs and Twitter/X handles. |
| LinkedIn scraper authentication failure | Verify `APIFY_API_TOKEN` is set and that the upstream scraper can reach Apify. |
| Twitter/X scraper returns no results | Check handle formatting, date range, and whether the account posted during the selected period. |
| Topic clusters are too broad | Re-label broad themes into one-to-three-word topics and merge only genuinely similar posts. |
| Report has no actionable topics | Lower thresholds for a first run or expand `days_back` to 30 days. |

## Tips

- Use `kol-discovery` first when the user does not already have a high-quality list of KOLs.
- Treat multi-KOL convergence as a stronger signal than a single viral post.
- Preserve source URLs in the report so content teams can review the original context before publishing a response.
