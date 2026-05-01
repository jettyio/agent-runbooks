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
    source_collection: "playbooks"
    skill_name: "competitor-monitoring-system"
    confidence: "high"
secrets: {}
---

# Competitor Monitoring System — Agent Runbook

## Objective

Set up and run ongoing competitive intelligence monitoring for a client. This runbook tracks competitor content, ads, reviews, social presence, and product moves across multiple channels and cadences. It establishes a competitor watchlist, runs an initial baseline, configures recurring monitoring cycles, and produces structured intelligence reports. The goal is to surface actionable competitive insights — messaging shifts, new campaigns, review trends, and strategic announcements — on a weekly, bi-weekly, and monthly cadence so the client can respond proactively.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/competitor-watchlist.md` | Structured watchlist documenting each competitor with URL, products, social profiles, content channels, and review pages |
| `/app/results/competitor-baseline.md` | Initial competitive baseline output from full competitor-intel scraper run |
| `/app/results/monitoring-plan.md` | Configured monitoring cadence table with assigned skills, frequencies, and what to look for |
| `/app/results/intelligence-report.md` | Latest intelligence report in standard format (key changes, recommended actions, detailed findings) |
| `/app/results/summary.md` | Executive summary with run metadata, key findings, and any issues |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

If you finish your analysis but have not written all files, go back and write them before stopping.

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Client name | *(required)* | Client name used to scope output paths (e.g. `acme-corp`) |
| Competitor list | *(required)* | List of 3–7 competitor company names and URLs |
| Monitoring cadence | `weekly/biweekly/monthly` | Frequency mix per channel as defined in cadence table |
| Cycle type | `weekly` | Which cycle type to run: `weekly`, `biweekly`, `monthly`, or `quarterly` |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `competitor-intel` | Skill (composite) | Yes | Chains reddit + twitter + linkedin + blog + review scrapers for each competitor |
| `meta-ad-scraper` | Skill (capability) | Yes | Scrapes current Meta ad creatives for a given competitor |
| `google-ad-scraper` | Skill (capability) | Yes | Scrapes current Google ad creatives for a given competitor |
| `review-scraper` | Skill (capability) | Yes | Pulls latest G2/Capterra/Trustpilot reviews |
| `blog-scraper` | Skill (capability) | Yes | Fetches new blog/content posts from competitor domains |
| `linkedin-profile-post-scraper` | Skill (capability) | Yes | Scrapes LinkedIn posts from founder/exec profiles |
| `twitter-scraper` | Skill (capability) | Yes | Scrapes recent tweets from competitor accounts |
| `reddit-scraper` | Skill (capability) | Yes | Pulls competitor mentions and discussions from Reddit |
| `hacker-news-scraper` | Skill (capability) | Yes | Pulls competitor mentions from Hacker News |
| Client context file | File | Yes | Background document with client positioning and competitive landscape |

---

## Step 1: Environment Setup

Verify required inputs are available and create the output directory structure.

```bash
echo "=== ENVIRONMENT SETUP ==="

# Verify client name is set
if [ -z "${CLIENT_NAME}" ]; then
  echo "ERROR: CLIENT_NAME is not set. Export it before running."
  exit 1
fi

# Create output dirs
mkdir -p /app/results
mkdir -p "clients/${CLIENT_NAME}/intelligence/competitor-reports"

echo "Client: ${CLIENT_NAME}"
echo "Results dir: /app/results"
echo "PASS: environment ready"
```

---

## Step 2: Define Competitor Watchlist

Create a competitor tracking file for each competitor to monitor. Document all channels and profiles needed by downstream scrapers.

For each competitor, record:

- Company name and primary URL
- Key products or features
- Founder/exec LinkedIn profile URLs (for social monitoring)
- Known content channels (blog URL, YouTube channel, podcast feed)
- Review profiles (G2, Capterra, Trustpilot URLs)
- Ad library pages (Meta Ad Library URL, Google Ads Transparency Center)

Write the watchlist to `/app/results/competitor-watchlist.md` using this format:

```markdown
# Competitor Watchlist — [CLIENT_NAME]

## [Competitor Name]
- **URL**: https://...
- **Products**: [list key products]
- **LinkedIn (exec)**: https://linkedin.com/in/...
- **Blog**: https://...blog
- **G2**: https://g2.com/products/...
- **Meta Ads**: https://facebook.com/ads/library/?...
- **Google Ads**: https://adstransparency.google.com/...
```

**Human Checkpoint**: Review the completed watchlist before proceeding to baseline. Verify all URLs resolve and profiles are correct.

---

## Step 3: Run Initial Competitive Baseline

Run the full `competitor-intel` composite skill for each competitor in the watchlist to establish a baseline for comparison in future monitoring cycles.

For each competitor:

1. Run `competitor-intel` (chains reddit + twitter + linkedin + blog + review scrapers)
2. Run `meta-ad-scraper` — capture current Meta ad creatives
3. Run `google-ad-scraper` — capture current Google ad creatives
4. Run `review-scraper` — pull latest G2/Capterra/Trustpilot reviews

Aggregate results and write to `/app/results/competitor-baseline.md`:

```markdown
# Competitor Baseline — [CLIENT_NAME] — [DATE]

## [Competitor Name]
### Social / Content Snapshot
[Summary of recent posts, key themes, engagement patterns]

### Ad Creative Snapshot
[Summary of current ad campaigns and messaging]

### Review Snapshot
[Rating, volume, top themes in recent reviews]
```

---

## Step 4: Configure Monitoring Cadence

Write the monitoring plan to `/app/results/monitoring-plan.md` based on the cadence table below. Adjust frequencies based on competitive intensity.

| What to Monitor | Frequency | Skill | What to Look For |
|----------------|-----------|-------|-----------------|
| Blog/content output | Weekly | `blog-scraper` | New posts, topic shifts, SEO attacks on client keywords |
| Social media posts | Weekly | `linkedin-profile-post-scraper` + `twitter-scraper` | Messaging changes, product announcements, engagement patterns |
| Reddit/HN mentions | Weekly | `reddit-scraper` + `hacker-news-scraper` | User sentiment, complaints, praise, feature requests |
| Ad creative changes | Bi-weekly | `meta-ad-scraper` + `google-ad-scraper` | New campaigns, messaging shifts, spend signals |
| Review sentiment | Monthly | `review-scraper` | New reviews, rating trends, common complaint themes |
| Full re-baseline | Quarterly | `competitor-intel` (all scrapers) | Major positioning or product shifts since last baseline |

---

## Step 5: Run Monitoring Cycle (max 3 rounds per cycle)

Execute the scrapers appropriate for the current `CYCLE_TYPE`. Compare new data against the baseline or most recent prior cycle report.

```bash
CYCLE_TYPE="${CYCLE_TYPE:-weekly}"
echo "Running ${CYCLE_TYPE} monitoring cycle for ${CLIENT_NAME}"
```

For a **weekly** cycle, run:
- `blog-scraper` for each competitor
- `linkedin-profile-post-scraper` for each exec profile
- `twitter-scraper` for each competitor
- `reddit-scraper` for each competitor name
- `hacker-news-scraper` for each competitor name

For a **bi-weekly** cycle, additionally run:
- `meta-ad-scraper` for each competitor
- `google-ad-scraper` for each competitor

For a **monthly** cycle, additionally run:
- `review-scraper` for each competitor (G2, Capterra, Trustpilot)

For a **quarterly** cycle, re-run the full `competitor-intel` composite and update the baseline file.

Flag significant changes:
- New product features or pricing changes
- New content targeting client's keywords
- Negative review trends (potential customer-poaching opportunity)
- New ad campaigns or messaging pivots
- Founder/exec public statements about strategy

If a scraper fails or returns no data, retry once. After 1 retry still failing, record the failure in the report and continue with remaining scrapers. Do not block the entire cycle on a single scraper failure.

---

## Step 6: Produce Intelligence Report

After each cycle, synthesize findings into a structured intelligence report. Write to `/app/results/intelligence-report.md`.

```markdown
# Competitor Intelligence — [CLIENT_NAME] — Week of [DATE]

## Key Changes
- [Competitor A] published N new blog posts targeting "[keyword]"
- [Competitor B] launched new Meta ad campaign focused on [theme]
- [Competitor C] received N negative G2 reviews about [issue]

## Recommended Actions
- Publish response content for [Competitor A]'s keyword attack
- Create comparison page addressing [Competitor B]'s new messaging
- Target [Competitor C]'s unhappy customers with migration content

## Detailed Findings

### [Competitor A]
[Content / social / ad / review findings]

### [Competitor B]
[Content / social / ad / review findings]

### [Competitor C]
[Content / social / ad / review findings]
```

**Human Checkpoint**: Review recommended actions before executing any content or campaign responses.

---

## Step 7: Validate Outputs

Verify all required output files are present and non-empty before finishing.

```bash
echo "=== OUTPUT VALIDATION ==="
PASS=0
FAIL=0
for f in \
  /app/results/competitor-watchlist.md \
  /app/results/competitor-baseline.md \
  /app/results/monitoring-plan.md \
  /app/results/intelligence-report.md \
  /app/results/summary.md \
  /app/results/validation_report.json; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
    FAIL=$((FAIL+1))
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
    PASS=$((PASS+1))
  fi
done
echo "Results: $PASS passed, $FAIL failed"
if [ "$FAIL" -gt 0 ]; then
  echo "ERROR: Missing output files — do not mark run as complete"
  exit 1
fi
echo "PASS: all outputs present"
```

---

## Common Fixes

| Issue | Fix |
|-------|-----|
| Scraper returns no data for a competitor | Verify the competitor URL and social handles in the watchlist are current; retry once before skipping |
| Baseline file missing after Step 3 | Re-run `competitor-intel` for any missing competitors; do not proceed to monitoring cycles without a full baseline |
| Intelligence report has no key changes | Compare against the most recent prior report, not the baseline; if this is the first cycle, note it as "initial cycle — baseline established" |
| Ad scraper fails with auth or rate-limit error | Note the failure in the report and continue; retry on the next bi-weekly cycle |
| Review scraper returns stale data | Confirm the review page URLs in the watchlist are the direct product review pages, not the vendor homepage |

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/competitor-watchlist.md" \
  "$RESULTS_DIR/competitor-baseline.md" \
  "$RESULTS_DIR/monitoring-plan.md" \
  "$RESULTS_DIR/intelligence-report.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

### Checklist

- [ ] `competitor-watchlist.md` exists with all competitors documented
- [ ] `competitor-baseline.md` exists with initial scraper output
- [ ] `monitoring-plan.md` exists with cadence table
- [ ] `intelligence-report.md` exists with key changes and recommended actions
- [ ] `summary.md` exists and summarizes the run
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] All Human Checkpoints reviewed (watchlist review, recommended-actions review)

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Run the full baseline before any monitoring cycle.** Comparisons are only meaningful with a good baseline. Do not skip Step 3.
- **Keep the watchlist current.** Add new competitors as they emerge and retire companies that shut down or are acquired.
- **Brief reports are more actionable than exhaustive ones.** Focus the intelligence report on changes since the last cycle — not a full re-description of each competitor.
- **Scraper failures are not blockers.** If a single scraper returns no data, note it in the report and continue. A partial report is more useful than no report.
- **Quarterly re-baseline is critical.** Competitors shift positioning, launch new products, and change ad strategies. The quarterly re-run catches structural changes that weekly diffs might miss.
- **Human checkpoints are non-negotiable.** The watchlist and recommended actions must be reviewed by a human before acting on them.
