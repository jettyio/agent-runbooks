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
  imported_at: "2026-05-01T03:20:31Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "gooseworks-ai"
    skill_name: "signal-detection-pipeline"
    confidence: "high"
secrets: {}
---

# Signal Detection Pipeline — Agent Runbook

## Objective

Detect buying signals from multiple sources, qualify leads, and generate outreach context. This runbook orchestrates multiple independent signal-detection sub-skills (job postings, funding events, conference attendance, Reddit discussions, and LinkedIn content) to surface companies that are actively in-market. Signals are combined, deduplicated, and scored to produce a prioritized list of qualified leads with outreach angles ready for downstream enrichment and campaign setup.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/qualified_leads.csv` | Deduplicated, scored lead list: Company, Signal Sources, Signal Strength, Context, Outreach Angle |
| `/app/results/job_posting_signals.json` | Raw output from the job-posting-intent skill |
| `/app/results/funding_signals.json` | Raw output from the funding-signal-monitor skill |
| `/app/results/conference_signals.json` | Raw output from the luma-event-attendees skill |
| `/app/results/reddit_signals.json` | Raw output from the reddit-scraper skill |
| `/app/results/linkedin_signals.json` | Raw output from linkedin-post-research + linkedin-commenter-extractor |
| `/app/results/summary.md` | Executive summary: sources run, lead counts, top opportunities, issues |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

## Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| `target_keywords` | *(required)* | Keywords describing the problem/solution space (e.g. "sales automation", "data observability") |
| `icp_criteria` | *(required)* | Ideal Customer Profile criteria (industry, company size, geography, tech stack) |
| `signal_sources` | `all` | Comma-separated list of sources to run: `job_posting`, `funding`, `conference`, `reddit`, `linkedin`. Default: `all` |
| `funding_stage_filter` | `seed,series-a,series-b` | Funding stages to include in funding signals |
| `event_urls` | *(optional)* | Specific Luma event URLs for conference signals |
| `subreddits` | *(optional)* | Specific subreddits to search for Reddit signals |
| `linkedin_time_frame` | `30d` | Lookback window for LinkedIn post research |
| `max_leads_per_source` | `50` | Maximum raw leads to retrieve per signal source |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `requests` | Python package | Yes | HTTP calls to signal-source APIs |
| `pyyaml` | Python package | Yes | Parse YAML skill frontmatter |
| `pandas` | Python package | Yes | Deduplicate and score lead lists |
| `job-posting-intent` skill | Sub-skill | Yes | Detect companies hiring in the problem area |
| `funding-signal-monitor` skill | Sub-skill | Yes | Detect recently funded companies |
| `luma-event-attendees` skill | Sub-skill | Conditional | Detect conference attendance signals |
| `reddit-scraper` skill | Sub-skill | Conditional | Detect pain-signal posts on Reddit |
| `linkedin-post-research` skill | Sub-skill | Conditional | Detect LinkedIn content signals |
| `linkedin-commenter-extractor` skill | Sub-skill | Conditional | Extract commenters from LinkedIn posts |
| `lead-qualification` skill | Sub-skill | Yes | Score and qualify leads from combined signals |
| `contact-cache` skill | Sub-skill | Yes | Deduplicate against previously contacted companies |

## Step 1: Environment Setup

```bash
pip install requests pyyaml pandas
mkdir -p /app/results

# Validate required inputs
if [ -z "$TARGET_KEYWORDS" ]; then
  echo "ERROR: TARGET_KEYWORDS is not set"; exit 1
fi
if [ -z "$ICP_CRITERIA" ]; then
  echo "ERROR: ICP_CRITERIA is not set"; exit 1
fi
echo "Environment ready — Keywords: $TARGET_KEYWORDS | ICP: $ICP_CRITERIA"
```

## Step 2: Run Signal Sources in Parallel

Run the sources relevant to the client's ICP. Each is independent — run in parallel.

Run the sources relevant to the client's ICP. Each is independent — invoke in parallel where possible.

### 2a: Job Posting Signals (Strongest)

**Skill:** `job-posting-intent`

Companies hiring for roles in the problem area = budget allocated and pain acknowledged.

- Input: `target_keywords`, `icp_criteria`
- Output: → `/app/results/job_posting_signals.json`

```python
import subprocess, json, pathlib
result = subprocess.run(
    ["python3", "-m", "skills.job_posting_intent",
     "--keywords", "$TARGET_KEYWORDS",
     "--icp",      "$ICP_CRITERIA",
     "--max",      "50",
     "--output",   "/app/results/job_posting_signals.json"],
    capture_output=True, text=True
)
print(result.stdout or result.stderr)
```

### 2b: Funding Signals

**Skill:** `funding-signal-monitor`

Recently funded companies = budget available, growth mandate.

- Input: `icp_criteria`, `funding_stage_filter`
- Output: → `/app/results/funding_signals.json`

```bash
python3 -m skills.funding_signal_monitor \
  --icp "$ICP_CRITERIA" \
  --stages "$FUNDING_STAGE_FILTER" \
  --output /app/results/funding_signals.json
```

### 2c: Conference Attendance Signals

**Skill:** `luma-event-attendees`

People attending events in the problem space = actively engaged.

- Input: event URLs or topic search
- Output: → `/app/results/conference_signals.json`

```bash
python3 -m skills.luma_event_attendees \
  --keywords "$TARGET_KEYWORDS" \
  --event-urls "$EVENT_URLS" \
  --output /app/results/conference_signals.json
```

### 2d: Reddit Pain Signals

**Skill:** `reddit-scraper`

People complaining about or discussing the problem = experiencing the pain.

- Input: `target_keywords`, optional `subreddits`
- Output: → `/app/results/reddit_signals.json`

```bash
python3 -m skills.reddit_scraper \
  --keywords "$TARGET_KEYWORDS" \
  --subreddits "$SUBREDDITS" \
  --output /app/results/reddit_signals.json
```

### 2e: LinkedIn Content Signals

**Skills:** `linkedin-post-research` + `linkedin-commenter-extractor`

People posting about or engaging with the problem = thought leaders or practitioners.

- Input: `target_keywords`, `linkedin_time_frame`
- Output: → `/app/results/linkedin_signals.json`

```bash
python3 -m skills.linkedin_post_research \
  --keywords "$TARGET_KEYWORDS" \
  --time-frame "$LINKEDIN_TIME_FRAME" \
  --extract-commenters true \
  --output /app/results/linkedin_signals.json
```

## Step 3: Combine and Deduplicate Signals

After all sources complete, merge and deduplicate:

```python
import pandas as pd, json, pathlib

signal_files = {
    "job_posting":  "/app/results/job_posting_signals.json",
    "funding":      "/app/results/funding_signals.json",
    "conference":   "/app/results/conference_signals.json",
    "reddit":       "/app/results/reddit_signals.json",
    "linkedin":     "/app/results/linkedin_signals.json",
}

all_leads = []
for source_name, path in signal_files.items():
    p = pathlib.Path(path)
    if p.exists() and p.stat().st_size > 0:
        data = json.loads(p.read_text())
        for lead in data.get("leads", []):
            lead["_source"] = source_name
            all_leads.append(lead)

df = pd.DataFrame(all_leads)
# Deduplicate by company name (normalize to lowercase)
df["_company_key"] = df.get("company", df.get("name", pd.Series())).str.lower().str.strip()
grouped = df.groupby("_company_key").agg(
    company=("company", "first"),
    signal_sources=("_source", lambda x: ", ".join(sorted(set(x)))),
    signal_count=("_source", "count"),
    context=("context", lambda x: " | ".join(x.dropna().astype(str)[:2])),
).reset_index(drop=True)

# Score: job_posting+funding=3, linkedin+reddit=2, conference=1
WEIGHTS = {"job_posting": 3, "funding": 3, "linkedin": 2, "reddit": 2, "conference": 1}
def score(row):
    return sum(WEIGHTS.get(s.strip(), 1) for s in row["signal_sources"].split(","))
grouped["signal_strength"] = grouped.apply(score, axis=1)
grouped = grouped.sort_values("signal_strength", ascending=False)
grouped["outreach_angle"] = ""  # to be filled by lead-qualification skill
grouped.to_csv("/app/results/qualified_leads.csv", index=False)
print(f"Deduplicated leads: {len(grouped)}")
```

## Step 4: Score and Qualify Leads

Apply `lead-qualification` skill to the deduplicated list:

```bash
python3 -m skills.lead_qualification \
  --input /app/results/qualified_leads.csv \
  --icp "$ICP_CRITERIA" \
  --output /app/results/qualified_leads.csv
```

Signal scoring tiers:
- **Highest intent**: Job posting + funding signal → priority outreach
- **Validated pain**: LinkedIn post + Reddit complaint → value-led outreach
- **Awareness only**: Single conference attendance → nurture sequence

## Step 5: Human Checkpoint — Review Before Proceeding

**STOP HERE** — review the consolidated lead list before initiating outreach.

```bash
echo "=== TOP LEADS ===" && head -20 /app/results/qualified_leads.csv
```

Verify:
- [ ] Lead companies are plausible fits for the ICP
- [ ] Signal context accurately reflects the source (no hallucinated entries)
- [ ] Outreach angles are specific and non-generic
- [ ] No contacts from the contact-cache (already reached)

If review passes, continue to Step 6. If issues found, adjust `icp_criteria` or `target_keywords` and re-run from Step 2.

## Step 6: Iterate on Errors (max 3 rounds)

If any signal source returned zero leads or an error:

1. Read the specific failure from its output JSON (`"error"` key)
2. Apply fix from the table below
3. Re-run only the failing source
4. Merge new results back via Step 3

Repeat up to **max 3 rounds** per source.

| Issue | Fix |
|-------|-----|
| Job posting API rate-limited | Add `--delay 5` flag; retry after 5 minutes |
| No Reddit posts found | Broaden `target_keywords`; add related subreddits |
| LinkedIn returns 0 posts | Extend `linkedin_time_frame` to `90d` |
| Funding source empty | Try adjacent funding stages (`pre-seed`, `series-c`) |
| Conference events not found | Provide explicit `event_urls` parameter |

After 3 rounds with persistent failure for a source, mark it as `skipped` in `summary.md` and continue with available signals.

## Step 7: Check Contact Cache

Deduplicate final leads against previously contacted companies:

```bash
python3 -m skills.contact_cache \
  --check /app/results/qualified_leads.csv \
  --remove-already-contacted true \
  --output /app/results/qualified_leads.csv
```

## Step 8: Write Executive Summary

```python
import pandas as pd, pathlib
df = pd.read_csv("/app/results/qualified_leads.csv")
summary = f"""# Signal Detection Pipeline — Results

## Overview
- **Date**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- **Target keywords**: $TARGET_KEYWORDS
- **ICP criteria**: $ICP_CRITERIA
- **Total leads found**: {len(df)}
- **Multi-signal leads**: {(df["signal_count"] > 1).sum()} (highest priority)

## Signal Source Results

| Source | Leads Found |
|--------|------------|
| Job Posting | {len(pd.read_json("/app/results/job_posting_signals.json").get("leads", []))} |
| Funding | {len(pd.read_json("/app/results/funding_signals.json").get("leads", []))} |
| Conference | {len(pd.read_json("/app/results/conference_signals.json").get("leads", []))} |
| Reddit | {len(pd.read_json("/app/results/reddit_signals.json").get("leads", []))} |
| LinkedIn | {len(pd.read_json("/app/results/linkedin_signals.json").get("leads", []))} |

## Top 5 Leads by Signal Strength

{df.head(5)[["company","signal_sources","signal_strength","outreach_angle"]].to_markdown(index=False)}

## Issues / Manual Follow-up
- Review leads with `signal_count == 1` — lower confidence, may need manual validation
- Outreach angles marked empty require human review before campaign launch
"""
pathlib.Path("/app/results/summary.md").write_text(summary)
print("summary.md written")
```

## Step 9: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/qualified_leads.csv" \
  "$RESULTS_DIR/job_posting_signals.json" \
  "$RESULTS_DIR/funding_signals.json" \
  "$RESULTS_DIR/conference_signals.json" \
  "$RESULTS_DIR/reddit_signals.json" \
  "$RESULTS_DIR/linkedin_signals.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
LEAD_COUNT=$(wc -l < "$RESULTS_DIR/qualified_leads.csv")
if [ "$LEAD_COUNT" -gt 1 ]; then
  echo "PASS: qualified_leads.csv has $((LEAD_COUNT-1)) leads"
else
  echo "FAIL: qualified_leads.csv has no leads — check signal sources"
fi
```

### Checklist

- [ ] `qualified_leads.csv` exists and contains at least 1 lead row
- [ ] All signal source JSON files exist (may be empty if source was skipped)
- [ ] `summary.md` reports lead counts and top opportunities
- [ ] `validation_report.json` exists with `overall_passed` field
- [ ] Human checkpoint (Step 5) was completed before proceeding to outreach
- [ ] Contact cache deduplication was applied (Step 7)
- [ ] No individual source failed more than 3 times without being marked `skipped`

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Run signal sources in parallel** when your execution environment supports it — each source is fully independent and the combined runtime drops from ~15 min to ~4 min.
- **Job posting signals are the highest-quality signal**: a company hiring a role that requires solving your client's problem almost always has budget allocated and explicit pain acknowledged.
- **Multi-signal leads are gold**: a company that appears in job postings AND received recent funding AND has a LinkedIn post discussing the problem has no weak spots in the signal chain — prioritize these above all others.
- **Reddit signals require caution**: authors may be individual contributors, not decision-makers. Always enrich with `company-contact-finder` before outreach.
- **Slugify company names consistently** before deduplication — "Acme Corp.", "ACME Corp", and "acme" are the same company. Use `str.lower().strip().replace(".", "")` at minimum.
- **Contact cache integration prevents burnout**: always run Step 7 before exporting to any outreach campaign. Re-contacting a company that already declined is a hard negative signal.
