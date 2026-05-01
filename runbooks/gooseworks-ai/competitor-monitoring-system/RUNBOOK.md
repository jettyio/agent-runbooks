---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://github.com/gooseworks-ai/gooseworks-skills/blob/main/skills/playbooks/competitor-monitoring-system/SKILL.md"
  source_host: "github.com"
  source_title: "Competitor Monitoring System"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "gooseworks-ai"
    skill_name: "competitor-monitoring-system"
    confidence: "high"
secrets: {}
---

# Competitor Monitoring System — Agent Runbook

## Objective

Set up and run ongoing competitive intelligence monitoring for a client. The runbook tracks competitor content, ads, reviews, social presence, and product moves across multiple channels on a recurring cadence. It produces regular intelligence reports that surface key competitor changes and recommend strategic actions. The agent coordinates multiple scraper skills and synthesizes findings into structured reports stored in a client-specific directory.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to the configured results directory.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `clients/<client-name>/intelligence/competitor-watchlist.md` | Structured competitor watchlist with URLs, profiles, and channels |
| `clients/<client-name>/intelligence/competitor-baseline.md` | Initial competitive baseline from full intel run |
| `clients/<client-name>/intelligence/competitor-reports/<date>.md` | Per-cycle intelligence report |
| `summary.md` | Executive summary of the monitoring run |
| `validation_report.json` | Structured validation results with stages and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for validation and summary files |
| `client_name` | *(required)* | Client name slug used in file paths |
| `competitor_list` | *(required)* | List of 3–7 competitors to monitor (names + URLs) |
| `client_context` | *(required)* | Client competitive positioning context |
| `monitoring_cycle` | `weekly` | Cycle type: `weekly`, `biweekly`, or `monthly` |
| `output_dir` | `clients/<client-name>/intelligence` | Root directory for intelligence output |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `competitor-intel` composite | Skill | Yes | Chains reddit + twitter + linkedin + blog + review scrapers |
| `meta-ad-scraper` | Skill | Yes | Scrapes current Meta ads for each competitor |
| `google-ad-scraper` | Skill | Yes | Scrapes current Google ads for each competitor |
| `review-scraper` | Skill | Yes | Pulls latest G2/Capterra/Trustpilot reviews |
| `blog-scraper` | Skill | Yes | Fetches new blog posts and content |
| `linkedin-profile-post-scraper` | Skill | Yes | Scrapes LinkedIn posts from exec profiles |
| `twitter-scraper` | Skill | Yes | Scrapes competitor Twitter/X activity |
| `reddit-scraper` | Skill | Yes | Monitors Reddit mentions and discussions |
| `hacker-news-scraper` | Skill | Yes | Monitors Hacker News mentions |

## Step 1: Environment Setup

Verify all inputs and initialize the output directory structure.

```bash
# Verify required inputs
if [ -z "$CLIENT_NAME" ]; then
  echo "ERROR: CLIENT_NAME is not set"
  exit 1
fi

if [ -z "$COMPETITOR_LIST" ]; then
  echo "ERROR: COMPETITOR_LIST is not set"
  exit 1
fi

# Create output directories
mkdir -p "clients/${CLIENT_NAME}/intelligence/competitor-reports"
mkdir -p /app/results

echo "Environment ready. Client: ${CLIENT_NAME}"
echo "Output root: clients/${CLIENT_NAME}/intelligence/"
```

## Step 2: Define Competitor Watchlist

Create the competitor tracking file at `clients/<client-name>/intelligence/competitor-watchlist.md`.

For each competitor, document all of the following fields:

```markdown
# Competitor Watchlist — <Client Name>

## <Competitor Name>
- **URL**: https://...
- **Key products/features**: ...
- **Founder/exec LinkedIn profiles**: https://linkedin.com/in/...
- **Blog URL**: https://...
- **YouTube channel**: https://...
- **Podcast**: ...
- **G2 profile**: https://g2.com/products/...
- **Capterra profile**: https://capterra.com/...
- **Meta Ad Library**: https://facebook.com/ads/library/?search_term=...
- **Google Ads Transparency**: https://adstransparency.google.com/...
```

**Output**: `clients/<client-name>/intelligence/competitor-watchlist.md`

After completing the watchlist, pause for human review before proceeding.

**Human checkpoint**: Review competitor watchlist and monitoring plan before baseline run.

## Step 3: Run Initial Competitive Baseline

Run the full `competitor-intel` composite skill for each competitor to establish a baseline. This chains reddit, twitter, linkedin, blog, and review scrapers into a single pass.

Additionally run:
- **`meta-ad-scraper`** — Scrape current Meta ads for each competitor
- **`google-ad-scraper`** — Scrape current Google ads for each competitor
- **`review-scraper`** — Pull latest G2/Capterra/Trustpilot reviews

Combine all findings into:

**Output**: `clients/<client-name>/intelligence/competitor-baseline.md`

Structure the baseline as:

```markdown
# Competitor Baseline — <Client Name> — <Date>

## <Competitor Name>
### Content & Blog
...
### Social (LinkedIn / Twitter)
...
### Community (Reddit / HN)
...
### Ads (Meta / Google)
...
### Reviews (G2 / Capterra / Trustpilot)
...
```

## Step 4: Configure Monitoring Cadence

The following table defines what to monitor, at what frequency, and what signals to watch for:

| What to Monitor | Frequency | Skill | What to Look For |
|----------------|-----------|-------|-----------------|
| Blog/content output | Weekly | `blog-scraper` | New posts, topic shifts, SEO attacks |
| Social media posts | Weekly | `linkedin-profile-post-scraper` + `twitter-scraper` | Messaging changes, product announcements, engagement patterns |
| Reddit/HN mentions | Weekly | `reddit-scraper` + `hacker-news-scraper` | User sentiment, complaints, praise, feature requests |
| Ad creative changes | Bi-weekly | `meta-ad-scraper` + `google-ad-scraper` | New campaigns, messaging shifts, spend changes |
| Review sentiment | Monthly | `review-scraper` | New reviews, rating trends, common complaints |

Confirm the cadence with the client before beginning recurring runs.

## Step 5: Run Monitoring Cycle (max 7 competitors per cycle)

Each monitoring cycle:

1. Determine which cycle type is running (`weekly`, `biweekly`, `monthly`) and select the relevant scrapers from Step 4.
2. Run all relevant scrapers for **each** competitor in the watchlist.
3. Compare new data against the baseline or the previous cycle's report.
4. Flag significant changes, including:
   - New product features or pricing changes
   - New content targeting the client's keywords
   - Negative review trends (poaching opportunity)
   - New ad campaigns (messaging intelligence)
   - Founder/exec public statements about strategy

## Step 6: Iterate on Errors (max 3 rounds)

If any scraper fails or returns empty results:

1. Check the specific scraper's error output.
2. Retry the failed scraper once with updated parameters (e.g., adjusted date ranges, alternative profile URLs).
3. If still failing, mark the data source as `UNAVAILABLE` in the report and note it in the summary.
4. After 3 rounds of retries, proceed with available data and flag the gap in `validation_report.json`.

## Step 7: Produce Intelligence Report

After each cycle, produce a brief intelligence summary:

```markdown
# Competitor Intelligence — [Client] — Week of [Date]

## Key Changes
- [Competitor A] published 3 new blog posts targeting "[keyword]"
- [Competitor B] launched new Meta ad campaign focused on [theme]
- [Competitor C] received 5 negative G2 reviews about [issue]

## Recommended Actions
- Publish response content for [Competitor A]'s keyword attack
- Create comparison page addressing [Competitor B]'s new messaging
- Target [Competitor C]'s unhappy customers with migration content

## Detailed Findings
[Per-competitor breakdown]
```

**Output**: `clients/<client-name>/intelligence/competitor-reports/<date>.md`

**Human checkpoint**: Review recommended actions before executing any content or campaign responses.

## Step 8: Write Summary and Validation

Write `summary.md` to `/app/results/summary.md`:

```markdown
# Competitor Monitoring Run — Summary

## Run Details
- **Date**: <run date>
- **Client**: <client_name>
- **Cycle type**: <weekly|biweekly|monthly>
- **Competitors monitored**: <count>
- **Scrapers run**: <list>

## Output Files
- Watchlist: clients/<client-name>/intelligence/competitor-watchlist.md
- Baseline: clients/<client-name>/intelligence/competitor-baseline.md
- Report: clients/<client-name>/intelligence/competitor-reports/<date>.md

## Issues / Gaps
- <Any scrapers that failed or returned no data>

## Next Run
- **Weekly cycle**: <next Monday's date>
- **Bi-weekly cycle**: <next bi-weekly date>
- **Monthly cycle**: <next month's date>
```

Write `validation_report.json` to `/app/results/validation_report.json` using the structure defined in Step 10.

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
CLIENT="${CLIENT_NAME:-unknown}"
for f in \
  "clients/${CLIENT}/intelligence/competitor-watchlist.md" \
  "clients/${CLIENT}/intelligence/competitor-baseline.md" \
  "/app/results/summary.md" \
  "/app/results/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== DONE ==="
```

### Checklist

- [ ] Competitor watchlist created and reviewed by human
- [ ] Baseline run completed for all competitors
- [ ] Monitoring cadence configured
- [ ] All relevant scrapers executed for current cycle type
- [ ] Intelligence report written with Key Changes and Recommended Actions
- [ ] `summary.md` written to `/app/results/`
- [ ] `validation_report.json` written to `/app/results/`
- [ ] Human checkpoint completed before executing recommendations

## Tips

- **Scraper depth vs. speed.** Weekly runs can use shallow scrapes (last 7 days). Monthly runs should go deeper (last 30–90 days) for review and ad data.
- **Watchlist maintenance.** Review and update the watchlist quarterly — competitors pivot, shut down, or launch new channels.
- **Baseline drift.** After a quarterly re-baseline, treat the new baseline as the reference — don't compare against a year-old snapshot.
- **LinkedIn scraping limits.** LinkedIn rate-limits aggressively. If `linkedin-profile-post-scraper` fails, retry after 30 minutes with a reduced request frequency.
- **Attribution low-confidence isn't a blocker.** For any scraper source that's behind auth or a paywall, note in the report that data is partial.
- **Keep reports concise.** The "Key Changes" section should have 3–5 bullets maximum. Detailed findings belong in the per-competitor breakdown, not the summary.
