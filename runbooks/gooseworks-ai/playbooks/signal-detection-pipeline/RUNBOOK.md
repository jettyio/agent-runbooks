---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://github.com/gooseworks-ai/gooseworks-skills/blob/main/skills/playbooks/signal-detection-pipeline/SKILL.md"
  source_host: "github.com"
  source_title: "Signal Detection Pipeline"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "gooseworks-ai"
    source_collection: "playbooks"
    skill_name: "signal-detection-pipeline"
    confidence: "high"
secrets: {}
---

# Signal Detection Pipeline — Agent Runbook

## Objective

Monitor multiple signal sources to find companies actively in-market for a client's solution. This runbook detects buying signals from multiple channels—job postings, funding events, conference attendance, Reddit pain signals, and LinkedIn content—qualifies the resulting leads against an Ideal Customer Profile (ICP), and generates structured outreach context. It combines signals for higher-confidence lead identification by deduplicating companies across sources and scoring them by signal strength and recency.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/qualified_leads.json` | Deduplicated, scored, and enriched leads from all signal sources |
| `/app/results/signal_report.md` | Summary of signals detected per source with counts and highlights |
| `/app/results/outreach_context.json` | Per-lead outreach angles and context for campaign use |
| `/app/results/summary.md` | Executive summary with run metadata, signal counts, and top leads |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| `target_keywords` | *(required)* | Keywords to search for job postings, Reddit posts, LinkedIn content |
| `icp_criteria` | *(required)* | Ideal Customer Profile criteria for lead qualification |
| `industry` | *(optional)* | Target industry for funding signal monitoring |
| `event_urls` | *(optional)* | Event URLs or topic search for conference attendance signals |
| `subreddits` | *(optional)* | Relevant subreddits to scrape for pain signals |
| `time_frame` | `30d` | Time frame for LinkedIn content signals |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `job-posting-intent` | Gooseworks skill | Conditional | Finds companies hiring for roles in the problem area |
| `funding-signal-monitor` | Gooseworks skill | Conditional | Monitors recently funded companies |
| `luma-event-attendees` | Gooseworks skill | Conditional | Extracts conference attendees from Luma events |
| `reddit-scraper` | Gooseworks skill | Conditional | Scrapes Reddit for pain-signal posts |
| `linkedin-post-research` | Gooseworks skill | Conditional | Finds LinkedIn posts related to target keywords |
| `linkedin-commenter-extractor` | Gooseworks skill | Conditional | Extracts commenters from LinkedIn posts |
| `lead-qualification` | Gooseworks skill | Yes | Qualifies leads against ICP criteria |
| `contact-cache` | Gooseworks skill | Yes | Caches and deduplicates contact lookups |
| `company-contact-finder` | Gooseworks skill | Conditional | Enriches qualified leads with contact details |
| `setup-outreach-campaign` | Gooseworks skill | Conditional | Downstream campaign setup (connects_to) |
| `requests` | Python package | Yes | HTTP calls to signal source APIs |
| `pyyaml` | Python package | Yes | Parse structured outputs |

## Step 1: Environment Setup

```bash
pip install requests pyyaml

mkdir -p /app/results

# Verify required parameters are provided
if [ -z "$TARGET_KEYWORDS" ]; then
  echo "ERROR: TARGET_KEYWORDS is not set"
  exit 1
fi
if [ -z "$ICP_CRITERIA" ]; then
  echo "ERROR: ICP_CRITERIA is not set"
  exit 1
fi

echo "Environment ready."
```

Set the following environment variables before proceeding:

```bash
export TARGET_KEYWORDS="your keywords here"
export ICP_CRITERIA="your ICP definition here"
export INDUSTRY="optional industry filter"
export EVENT_URLS="optional event URLs"
export SUBREDDITS="optional subreddit names"
export TIME_FRAME="30d"
```

## Step 2: Run Signal Sources in Parallel

Run all applicable signal sources independently. Each source is optional; run the ones relevant to the client's ICP. For best results, run in parallel.

### Step 2a: Job Posting Signals (Strongest)

Companies hiring for roles in the problem area have budget allocated and pain acknowledged.

```python
# Use the job-posting-intent skill
# Input: TARGET_KEYWORDS, ICP_CRITERIA
# Output: Qualified companies with outreach angles

import json, pathlib

# Invoke the job-posting-intent skill
# result = invoke_skill("job-posting-intent", keywords=TARGET_KEYWORDS, icp=ICP_CRITERIA)
# For each result, record: company, signal_source="job_posting", signal_strength=3, context

job_posting_results = []  # populate from skill invocation
pathlib.Path("/app/results/work/job_posting_signals.json").write_text(json.dumps(job_posting_results))
print(f"Job posting signals: {len(job_posting_results)} companies")
```

### Step 2b: Funding Signals

Recently funded companies have budget available and a growth mandate.

```python
# Use the funding-signal-monitor skill
# Input: INDUSTRY, funding_stage_filter
# Output: Funded companies with timing context

funding_results = []  # populate from skill invocation
pathlib.Path("/app/results/work/funding_signals.json").write_text(json.dumps(funding_results))
print(f"Funding signals: {len(funding_results)} companies")
```

### Step 2c: Conference Attendance Signals

People attending events in the problem space are actively engaged.

```python
# Use the luma-event-attendees skill
# Input: EVENT_URLS
# Output: Person/company list

event_results = []  # populate from skill invocation
pathlib.Path("/app/results/work/event_signals.json").write_text(json.dumps(event_results))
print(f"Event attendance signals: {len(event_results)} contacts")
```

### Step 2d: Reddit Pain Signals

People complaining about or discussing the problem are experiencing it firsthand.

```python
# Use the reddit-scraper skill
# Input: TARGET_KEYWORDS, SUBREDDITS
# Output: Posts with authors and context

reddit_results = []  # populate from skill invocation
pathlib.Path("/app/results/work/reddit_signals.json").write_text(json.dumps(reddit_results))
print(f"Reddit signals: {len(reddit_results)} posts")
```

### Step 2e: LinkedIn Content Signals

People posting about or engaging with the problem are thought leaders or practitioners.

```python
# Use linkedin-post-research + linkedin-commenter-extractor skills
# Input: TARGET_KEYWORDS, TIME_FRAME
# Output: Posters and commenters with engagement data

linkedin_results = []  # populate from skill invocation
pathlib.Path("/app/results/work/linkedin_signals.json").write_text(json.dumps(linkedin_results))
print(f"LinkedIn signals: {len(linkedin_results)} contacts")
```

## Step 3: Combine and Deduplicate Signals

After all signal sources have run, merge and score the results.

```python
import json, pathlib, os

# Load all signal results
work_dir = pathlib.Path("/app/results/work")
all_signals = []
signal_files = {
    "job_posting": "job_posting_signals.json",
    "funding": "funding_signals.json",
    "event": "event_signals.json",
    "reddit": "reddit_signals.json",
    "linkedin": "linkedin_signals.json"
}

for source, fname in signal_files.items():
    fpath = work_dir / fname
    if fpath.exists():
        data = json.loads(fpath.read_text())
        for item in data:
            item["signal_source"] = source
        all_signals.extend(data)

# Signal strength scores by source
SIGNAL_WEIGHTS = {
    "job_posting": 3,
    "funding": 3,
    "linkedin": 2,
    "reddit": 2,
    "event": 1
}

# Deduplicate by company name; accumulate signal sources
companies = {}
for signal in all_signals:
    company_key = signal.get("company", signal.get("company_name", "unknown")).lower().strip()
    if company_key not in companies:
        companies[company_key] = {
            "company": signal.get("company", signal.get("company_name", "unknown")),
            "signal_sources": [],
            "signal_strength": 0,
            "context": [],
            "outreach_angle": signal.get("outreach_angle", "")
        }
    source = signal["signal_source"]
    if source not in companies[company_key]["signal_sources"]:
        companies[company_key]["signal_sources"].append(source)
        companies[company_key]["signal_strength"] += SIGNAL_WEIGHTS.get(source, 1)
    if signal.get("context"):
        companies[company_key]["context"].append(f"[{source}] {signal['context']}")

# Sort by signal strength descending
leads = sorted(companies.values(), key=lambda x: x["signal_strength"], reverse=True)

pathlib.Path("/app/results/work/combined_signals.json").write_text(json.dumps(leads, indent=2))
print(f"Combined {len(leads)} unique companies from {len(all_signals)} signals")
```

**Human Checkpoint:** Review the consolidated list before enrichment and outreach.

## Step 4: Qualify Leads Against ICP

```python
import json, pathlib

leads = json.loads(pathlib.Path("/app/results/work/combined_signals.json").read_text())

# Use the lead-qualification skill against ICP_CRITERIA
# qualified = [l for l in leads if invoke_skill("lead-qualification", lead=l, icp=ICP_CRITERIA)]

# Enrich top qualified leads with company details
qualified_leads = leads  # replace with filtered list from lead-qualification skill

# Write qualified leads output
pathlib.Path("/app/results/qualified_leads.json").write_text(json.dumps(qualified_leads, indent=2))
print(f"Qualified leads: {len(qualified_leads)}")
```

## Step 5: Generate Outreach Context

```python
import json, pathlib

qualified_leads = json.loads(pathlib.Path("/app/results/qualified_leads.json").read_text())

outreach_context = []
for lead in qualified_leads:
    sources = lead.get("signal_sources", [])
    # Derive outreach angle based on signal combination
    if "job_posting" in sources and "funding" in sources:
        angle = "High-intent: actively hiring AND recently funded — budget and pain both confirmed"
    elif "job_posting" in sources:
        angle = "Hiring for relevant roles — pain acknowledged, budget allocated"
    elif "funding" in sources:
        angle = "Recently funded — growth mandate and budget available"
    elif "linkedin" in sources and "reddit" in sources:
        angle = "Validated pain: discussing the problem both on LinkedIn and Reddit"
    elif "linkedin" in sources:
        angle = "Thought leader or practitioner actively discussing the problem space"
    elif "reddit" in sources:
        angle = "Experiencing pain: active discussion on Reddit"
    elif "event" in sources:
        angle = "Awareness signal: attended relevant conference"
    else:
        angle = lead.get("outreach_angle", "General interest signal")

    outreach_context.append({
        "company": lead["company"],
        "signal_strength": lead["signal_strength"],
        "signal_sources": sources,
        "outreach_angle": angle,
        "context_notes": lead.get("context", [])
    })

pathlib.Path("/app/results/outreach_context.json").write_text(json.dumps(outreach_context, indent=2))
print(f"Outreach context generated for {len(outreach_context)} leads")
```

## Step 6: Iterate on Errors (max 3 rounds)

If any signal source fails or returns no results:

1. Check the error message from the failed skill invocation
2. Apply targeted fix from the table below
3. Re-run only the failed source
4. Re-merge results in Step 3

Repeat up to 3 times per source before marking it as unavailable.

### Common Fixes

| Issue | Fix |
|-------|-----|
| Job posting skill returns empty | Broaden `target_keywords`; check API rate limits |
| Reddit scraper blocked | Use different user agent; check subreddit accessibility |
| LinkedIn skill fails | Verify LinkedIn session credentials; reduce time_frame |
| Funding monitor empty | Widen `industry` filter; extend lookback window |
| Event URL invalid | Verify Luma event URLs are public and accessible |
| Lead qualification fails | Simplify `icp_criteria`; check qualification skill configuration |

## Step 7: Write Signal Report

```python
import json, pathlib
from datetime import datetime

qualified_leads = json.loads(pathlib.Path("/app/results/qualified_leads.json").read_text())

# Count by source
source_counts = {}
for lead in qualified_leads:
    for src in lead.get("signal_sources", []):
        source_counts[src] = source_counts.get(src, 0) + 1

top_leads = sorted(qualified_leads, key=lambda x: x.get("signal_strength", 0), reverse=True)[:10]

report = f"""# Signal Detection Pipeline — Report

**Run date**: {datetime.utcnow().strftime('%Y-%m-%d')}
**Total qualified leads**: {len(qualified_leads)}

## Signal Source Summary

| Source | Leads Found |
|--------|------------|
"""
for src, count in sorted(source_counts.items(), key=lambda x: -x[1]):
    report += f"| {src} | {count} |\n"

report += f"""
## Top 10 Leads by Signal Strength

| Company | Signal Strength | Signal Sources |
|---------|----------------|----------------|
"""
for lead in top_leads:
    report += f"| {lead['company']} | {lead.get('signal_strength', 0)} | {', '.join(lead.get('signal_sources', []))} |\n"

pathlib.Path("/app/results/signal_report.md").write_text(report)
print("Signal report written")
```

## Step 8: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/qualified_leads.json" \
  "$RESULTS_DIR/signal_report.md" \
  "$RESULTS_DIR/outreach_context.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# Verify lead quality
LEAD_COUNT=$(python3 -c "import json; data=json.load(open('$RESULTS_DIR/qualified_leads.json')); print(len(data))")
echo "INFO: Total qualified leads: $LEAD_COUNT"

if [ "$LEAD_COUNT" -eq 0 ]; then
  echo "WARN: No qualified leads found — check signal source configuration"
else
  echo "PASS: Qualified leads found"
fi
```

### Checklist

- [ ] `qualified_leads.json` exists with deduplicated, scored leads
- [ ] `signal_report.md` exists with per-source counts and top 10 leads
- [ ] `outreach_context.json` exists with per-lead outreach angles
- [ ] `summary.md` exists with run metadata and highlights
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] At least one signal source returned results
- [ ] All leads in `qualified_leads.json` have `signal_strength > 0`
- [ ] Human checkpoint completed: reviewed combined signals list before outreach

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Run signal sources in parallel** for best throughput — each source is independent.
- **Multi-signal companies are your strongest leads.** A company appearing in both job postings and funding data has confirmed budget and acknowledged pain.
- **Start with job posting signals.** They are the strongest buying signal because they indicate both budget allocation and specific role/pain acknowledgment.
- **Score conservatively.** A single conference attendance is awareness only — don't treat it as high intent without corroborating signals.
- **Cache contact lookups.** Use the `contact-cache` skill to avoid redundant enrichment calls for companies that appear in multiple signal passes.
- **Human review before outreach.** Always review the consolidated lead list before connecting to the outreach campaign — false positives waste sales effort.
- **Connects downstream to** `company-contact-finder` for enrichment and `setup-outreach-campaign` for campaign creation.
