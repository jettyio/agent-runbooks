---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://github.com/gooseworks-ai/gooseworks-skills/blob/main/skills/playbooks/event-prospecting-pipeline/SKILL.md"
  source_host: "github.com"
  source_title: "Event Prospecting Pipeline"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "gooseworks-ai"
    skill_name: "event-prospecting-pipeline"
    confidence: "high"
secrets: {}
---

# Event Prospecting Pipeline — Agent Runbook

## Objective

This runbook implements an end-to-end event prospecting pipeline: discover attendees or speakers at conferences and events, enrich their profiles with company research, qualify them against an Ideal Customer Profile (ICP), deduplicate against existing contact caches, export a structured lead list, and optionally launch personalized outreach campaigns. It orchestrates multiple specialized skills (luma-event-attendees, conference-speaker-scraper, lead-qualification, company-contact-finder, contact-cache, setup-outreach-campaign, agentmail) into a coherent workflow that takes an event URL or topic and ICP criteria as inputs and produces a qualified lead list with optional outreach.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/qualified_leads.csv` | Final qualified, deduplicated lead list with columns: Name, Title, Company, LinkedIn URL, Email, Signal, Score |
| `/app/results/raw_attendees.json` | Raw attendee/speaker list as fetched from the event source |
| `/app/results/enriched_leads.json` | Enriched lead data with company funding stage, size, product, role, seniority, recent news |
| `/app/results/qualified_leads.json` | Scored and filtered leads after ICP qualification |
| `/app/results/outreach_status.json` | Outreach campaign setup result, or `{"skipped": true}` if outreach not requested |
| `/app/results/summary.md` | Executive summary with run metadata, lead counts, and any issues |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

If you finish your analysis but have not written all files, go back and write them before stopping.

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| `event-url-or-topic` | *(required)* | URL of a Luma event, conference website, or a topic/location to search (e.g. "AI events in SF") |
| `icp-criteria` | *(required)* | Ideal Customer Profile criteria for lead qualification (e.g. funding stage, company size, role seniority) |
| `launch-outreach` | `false` | If `true`, set up personalized outreach after lead review approval |
| `outreach-method` | `smartlead` | `smartlead` (via setup-outreach-campaign) or `agentmail` (via AgentMail direct) |
| `export-format` | `csv` | `csv` or `sheets` — format for the final lead list export |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `luma-event-attendees` | Skill | Conditional | Fetches attendee list from a Luma event URL or finds events by topic; required when input is a Luma URL or topic search |
| `conference-speaker-scraper` | Skill | Conditional | Scrapes speaker list from a conference website; required when input is a conference site URL |
| `lead-qualification` | Skill | Yes | Scores and filters enriched leads against ICP criteria |
| `company-contact-finder` | Skill | Yes | Finds decision-maker email addresses for qualified companies |
| `contact-cache` | Skill | Yes | Deduplicates leads against existing contacted persons to prevent repeat outreach |
| `setup-outreach-campaign` | Skill | Conditional | Sets up a Smartlead campaign for approved leads; required when `launch-outreach=true` and `outreach-method=smartlead` |
| `agentmail` | Skill | Conditional | Sends direct personalized emails via AgentMail; required when `launch-outreach=true` and `outreach-method=agentmail` |
| Web search | Capability | Yes | Used in Step 2 for company and person enrichment |
| Google Sheets / CSV export | Capability | Conditional | Used in Step 6 to export the final lead list |

---

## Step 1: Environment Setup

```bash
echo "=== EVENT PROSPECTING PIPELINE: Environment Setup ==="
mkdir -p /app/results

# Validate required inputs
if [ -z "$EVENT_URL_OR_TOPIC" ]; then
  echo "ERROR: event-url-or-topic is required"
  exit 1
fi
if [ -z "$ICP_CRITERIA" ]; then
  echo "ERROR: icp-criteria is required"
  exit 1
fi

# Determine event source type
if echo "$EVENT_URL_OR_TOPIC" | grep -q "lu.ma"; then
  EVENT_SOURCE="luma"
elif echo "$EVENT_URL_OR_TOPIC" | grep -qE "^https?://"; then
  EVENT_SOURCE="conference"
else
  EVENT_SOURCE="topic-search"
fi
echo "Event source type: $EVENT_SOURCE"
echo "ICP criteria: $ICP_CRITERIA"
```

Verify all required inputs are available. If `event-url-or-topic` is empty, fail fast and write a `validation_report.json` with `stages[0].passed=false`.

---

## Step 2: Find Attendees / Speakers

**Choose the appropriate skill based on input type:**

- **Luma event URL or topic** → invoke `luma-event-attendees`
  - For a direct Luma URL: pass the URL to fetch attendees
  - For a topic/location (e.g. "AI events in SF"): use Apify search mode to discover events first, then fetch attendees
- **Conference website URL** → invoke `conference-speaker-scraper`
  - Scrape the conference speaker or attendee page
  - Extract names, bios, LinkedIn/Twitter URLs, company affiliations

**Expected output:** Person list with fields: name, bio, linkedin_url, twitter_url, company, title.

Save raw results to `/app/results/raw_attendees.json`.

```python
import json, pathlib

# Example structure — actual data comes from the invoked skill
raw_attendees = [
    {
        "name": "<person name>",
        "bio": "<bio text>",
        "linkedin_url": "<url or null>",
        "twitter_url": "<url or null>",
        "company": "<company name>",
        "title": "<job title>"
    }
]
pathlib.Path('/app/results/raw_attendees.json').write_text(json.dumps(raw_attendees, indent=2))
```

---

## Step 3: Research & Enrich

**Capability:** Web search

For each person and company in the raw attendee list, gather enrichment signals via web search:

- **Company signals:** funding stage, headcount/size, product category, recent news
- **Person signals:** current role, seniority level, recent posts or activity, job changes

Skip enrichment if the user only requested a raw attendee list (set enriched = raw in that case).

Save enriched data to `/app/results/enriched_leads.json` with additional fields: `funding_stage`, `company_size`, `product`, `seniority`, `recent_news`.

**Human Checkpoint after Step 3:** If enrichment surfaces unexpected data or a very large list (>200 leads), pause and present a sample to the user before proceeding.

---

## Step 4: Qualify Against ICP

**Skill:** `lead-qualification`

Filter the enriched lead list against the provided `icp-criteria`. Assign each lead:
- A numeric `score` (0–100)
- A boolean `qualified` flag
- A `disqualification_reason` if not qualified

ICP criteria examples:
- Funding stage: Seed through Series B
- Company size: 10–500 employees
- Role seniority: VP or above, or Founder/C-suite
- Product fit signals

Save qualified leads to `/app/results/qualified_leads.json`.

**Human Checkpoint after Step 4:** Present the qualified lead list to the user for review before finding contact details. User must approve before proceeding to Step 5.

---

## Step 5: Find Decision-Maker Contacts

**Skill:** `company-contact-finder`

For each company in the qualified lead list, find specific decision-makers with verified email addresses. This step runs only on qualified companies to minimize API usage.

Output fields added: `email`, `verified`, `contact_source`.

Update `/app/results/qualified_leads.json` with contact information.

---

## Step 6: Deduplicate via Contact Cache

**Skill:** `contact-cache`

Check all qualified leads with contact info against the contact cache to identify:
- Previously contacted persons (skip)
- Persons already in an active outreach sequence (skip)
- New contacts (keep)

After deduplication, update the qualified list to mark removed entries as `deduplicated: true`.

---

## Step 7: Iterate on Errors (max 3 rounds)

If any step (Steps 2–6) fails or returns empty results:

1. Identify the specific failure from the step logs
2. Apply the targeted fix:
   - Empty attendee list → try alternate skill (luma-event-attendees ↔ conference-speaker-scraper) or broaden search
   - Enrichment API failure → retry with exponential backoff (max 3 retries per person)
   - Qualification returns 0 leads → loosen ICP criteria or ask user to adjust
   - Contact finder returns no emails → fall back to LinkedIn URL as contact method
   - Deduplication cache unavailable → skip dedup and flag in output
3. Re-run the affected step
4. Repeat up to 3 times total

After 3 rounds, if still blocked, write the failure into `summary.md` and continue with partial results.

---

## Step 8: Export Results

**Capability:** Google Sheets or CSV export

Export the final qualified, deduplicated lead list to `/app/results/qualified_leads.csv` with columns:

| Name | Title | Company | LinkedIn URL | Email | Signal | Score |
|------|-------|---------|--------------|-------|--------|-------|

Also write `/app/results/outreach_status.json`:
- If `launch-outreach=false`: `{"skipped": true, "reason": "launch-outreach not requested"}`
- If `launch-outreach=true`: proceed to Step 9

**Human Checkpoint after Step 8:** Present the final lead list and proposed email copy (if outreach=true) to the user for sign-off before launching.

---

## Step 9: Launch Outreach (optional)

**Skip this step if `launch-outreach=false`.**

Based on `outreach-method`:

**Smartlead (via `setup-outreach-campaign`):**
```bash
# Set up a Smartlead campaign with the approved lead list and email copy
# Campaign name: event-prospecting-<event-slug>-<YYYY-MM-DD>
```

**AgentMail (via `agentmail`):**
```bash
# Send personalized direct emails via AgentMail
# One email per approved lead
```

Update `/app/results/outreach_status.json` with campaign ID, lead count enrolled, and launch timestamp.

---

## Step 10: Write Executive Summary

Write `/app/results/summary.md`:

```markdown
# Event Prospecting Pipeline — Results

## Overview
- **Date**: <run date>
- **Event**: <event-url-or-topic>
- **ICP Criteria**: <icp-criteria>
- **Launch Outreach**: <true|false>

## Lead Funnel
| Stage | Count |
|-------|-------|
| Raw attendees/speakers | N |
| After enrichment | N |
| After ICP qualification | N |
| After deduplication | N |
| Final leads exported | N |

## Outreach
- Status: <launched|skipped>
- Method: <smartlead|agentmail|N/A>
- Campaign ID: <id or N/A>

## Issues / Manual Follow-up
- <Any empty-result stages>
- <Any leads missing email — only LinkedIn URL available>
- <Any deduplication cache failures>

## Output Files
- `/app/results/qualified_leads.csv` — final lead list
- `/app/results/qualified_leads.json` — detailed lead data
- `/app/results/outreach_status.json` — outreach result
```

---

## Step 11: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/raw_attendees.json" \
  "$RESULTS_DIR/enriched_leads.json" \
  "$RESULTS_DIR/qualified_leads.json" \
  "$RESULTS_DIR/qualified_leads.csv" \
  "$RESULTS_DIR/outreach_status.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# Validate lead counts
LEAD_COUNT=$(python3 -c "import json; data=json.load(open('$RESULTS_DIR/qualified_leads.json')); print(len([l for l in data if l.get('qualified')]))" 2>/dev/null || echo "0")
echo "Qualified leads: $LEAD_COUNT"

# Validate outreach status
OUTREACH=$(python3 -c "import json; d=json.load(open('$RESULTS_DIR/outreach_status.json')); print('skipped' if d.get('skipped') else 'launched')" 2>/dev/null || echo "unknown")
echo "Outreach status: $OUTREACH"
```

### Checklist

- [ ] `raw_attendees.json` exists and is non-empty
- [ ] `enriched_leads.json` exists with enrichment signals
- [ ] `qualified_leads.json` has scored and filtered leads
- [ ] `qualified_leads.csv` has all 7 required columns
- [ ] `outreach_status.json` reflects actual outreach outcome
- [ ] `summary.md` exists with lead funnel counts
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Human checkpoints were honored (Steps 4, 8)
- [ ] Verification script printed PASS for every file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Luma vs. conference scraper:** When in doubt about event type, try `luma-event-attendees` first — it handles both direct Luma URLs and topic-based search. Fall back to `conference-speaker-scraper` for non-Luma conference websites.
- **ICP criteria format:** Pass ICP criteria as a structured object (JSON) when possible — `lead-qualification` performs best with explicit field comparisons rather than free-text descriptions.
- **Dedup is non-negotiable:** Never skip the `contact-cache` step — sending duplicate outreach damages sender reputation and burns relationships. If the cache is unavailable, pause and flag to the user.
- **Human checkpoints are mandatory:** Do not auto-proceed past Steps 4 and 8 without explicit user approval. Present a sample of the data and wait for a "proceed" signal.
- **For Luma-only qualified lead gen** with built-in Google Sheets + Slack alerting, use `skills/composites/get-qualified-leads-from-luma/SKILL.md` instead. This runbook covers the full pipeline including outreach.
- **Contact cache connects to:** `skills/capabilities/setup-outreach-campaign/SKILL.md` and `skills/capabilities/contact-cache/SKILL.md` — ensure these are provisioned in your agent environment before running.
