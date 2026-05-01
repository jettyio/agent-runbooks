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
  imported_at: "2026-05-01T10:21:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "gooseworks-ai"
    source_collection: "playbooks"
    skill_name: "event-prospecting-pipeline"
    confidence: "high"
---

# Event Prospecting Pipeline — Agent Runbook

## Objective

This runbook implements an end-to-end event prospecting pipeline: discover attendees and speakers at conferences or events, enrich and research each person's company and role, qualify leads against defined Ideal Customer Profile (ICP) criteria, deduplicate against existing contact history, export a structured lead list, and optionally launch a personalized outreach campaign. It orchestrates multiple specialized skills — from event scrapers and lead qualification to contact finders and outreach tools — into a single repeatable workflow. The pipeline is parameterized by an event URL or topic and an ICP criteria definition, and produces a qualified lead list and optional outreach campaign as outputs.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/qualified_lead_list.csv` | Final qualified, deduplicated lead list with columns: Name, Title, Company, LinkedIn URL, Email, Signal, Score |
| `/app/results/outreach_campaign.md` | Outreach campaign details and email copy (if outreach was launched; otherwise note it was skipped) |
| `/app/results/pipeline_log.md` | Step-by-step log of what was done, how many leads were processed at each stage, and any decisions made |
| `/app/results/summary.md` | Executive summary with run metadata, lead counts at each stage, and any issues encountered |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

If you finish your analysis but have not written all files, go back and write them before stopping.

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| `event_url_or_topic` | *(required)* | Luma event URL, conference website URL, or topic/location string (e.g. "AI events in SF") |
| `icp_criteria` | *(required)* | ICP definition: target industries, company sizes, roles/titles, funding stages, geographies, etc. |
| `launch_outreach` | `false` | If `true`, launch a personalized outreach campaign after lead qualification |
| `outreach_method` | `smartlead` | Outreach tool to use: `smartlead` (via setup-outreach-campaign) or `agentmail` |
| `max_leads` | `100` | Maximum number of leads to process through the enrichment and qualification steps |
| `deduplicate_against_cache` | `true` | Whether to check the contact cache and skip previously contacted leads |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `luma-event-attendees` | Skill (Apify) | Conditional | Scrapes Luma event attendee lists; required when `event_url_or_topic` is a Luma URL or topic search |
| `conference-speaker-scraper` | Skill | Conditional | Scrapes conference website speaker lists; required when `event_url_or_topic` is a conference website |
| `lead-qualification` | Skill | Yes | Filters and scores enriched leads against ICP criteria |
| `company-contact-finder` | Skill | Yes | Finds decision-maker email addresses for qualified companies |
| `contact-cache` | Skill | Yes | Deduplication against existing outreach history |
| `setup-outreach-campaign` | Skill | Conditional | Sets up Smartlead outreach campaign; required when `launch_outreach=true` and `outreach_method=smartlead` |
| `agentmail` | Skill | Conditional | Sends direct personalized emails; required when `launch_outreach=true` and `outreach_method=agentmail` |
| Web search / browser | Capability | Yes | Used in Step 3 (Research & Enrich) to look up company and person details |
| Google Sheets / CSV export | Capability | Yes | Used in Step 7 to export the final lead list |

## Step 1: Environment Setup

Verify all required parameters are provided and skills are accessible before running the pipeline.

```bash
# Confirm required parameters are set
if [ -z "$event_url_or_topic" ]; then
  echo "ERROR: event_url_or_topic is required. Provide a Luma URL, conference URL, or topic string."
  exit 1
fi

if [ -z "$icp_criteria" ]; then
  echo "ERROR: icp_criteria is required. Define target industries, roles, company sizes, etc."
  exit 1
fi

# Create output directory
mkdir -p /app/results

echo "Event / topic: $event_url_or_topic"
echo "ICP criteria: $icp_criteria"
echo "Launch outreach: ${launch_outreach:-false}"
echo "Max leads: ${max_leads:-100}"
echo "Environment ready."
```

Decide which attendee-finder skill to invoke:
- If `event_url_or_topic` contains `lu.ma` or is a Luma URL → use `luma-event-attendees`
- If `event_url_or_topic` is a conference/event website URL → use `conference-speaker-scraper`
- If `event_url_or_topic` is a free-text topic or location → use `luma-event-attendees` in Apify search mode to find matching events first

Log this decision to `/app/results/pipeline_log.md`.

## Step 2: Find Attendees / Speakers

**Skills:** `luma-event-attendees` OR `conference-speaker-scraper`

Invoke the appropriate skill determined in Step 1:

```
luma-event-attendees:
  input: event_url_or_topic
  mode: attendees | search   # attendees if URL, search if topic/location
  max_results: {max_leads}

conference-speaker-scraper:
  input: event_url_or_topic   # conference website URL
  max_results: {max_leads}
```

**Expected output:** Person list with:
- Name
- Bio / description
- LinkedIn URL
- Twitter / X URL
- Company name
- Event / conference name

Persist raw attendee list to `/app/results/pipeline_log.md` (append). Note the count of persons found.

If fewer than 5 persons are found, pause and ask the user whether to continue with a smaller list or adjust the input parameters.

## Step 3: Research & Enrich

**Capability:** Web search + browser

For each person in the list (up to `max_leads`), research:
- **Company**: funding stage, size, product category, recent news
- **Person**: current role, seniority level, time in role
- **Signals**: recent job postings, press releases, LinkedIn activity, fundraising rounds

Use web search for each person/company pair. Cache results to avoid re-fetching.

Skip enrichment if the user explicitly requested a raw attendee list only. In that case, proceed directly to Step 6 (Output Results) and note the skip in `pipeline_log.md`.

Append enrichment summary (counts, notable signals found) to `/app/results/pipeline_log.md`.

## Step 4: Qualify Against ICP

**Skill:** `lead-qualification`

Filter the enriched person list against `icp_criteria`. For each person:
1. Evaluate against each ICP dimension (industry, company size, role, funding stage, geography)
2. Assign a qualification score (0–100)
3. Flag as `qualified` (score ≥ threshold, default 60) or `not_qualified`

```
lead-qualification:
  leads: [enriched person list]
  icp_criteria: {icp_criteria}
  score_threshold: 60
```

Log to `pipeline_log.md`:
- Total leads evaluated
- Total qualified
- Total not qualified
- Score distribution summary

**Human checkpoint:** After this step, present the qualified lead list to the user for review before proceeding to contact finding. Ask for explicit approval to continue.

## Step 5: Find Decision-Maker Contacts

**Skill:** `company-contact-finder`

For each qualified company, find the specific decision-makers with verified email addresses:

```
company-contact-finder:
  companies: [list of qualified company names]
  target_roles: [roles/titles from icp_criteria]
  verify_emails: true
```

Match found contacts back to the qualified person list. Prefer direct contact for the already-known person; use decision-maker contacts as fallback.

Log counts: companies searched, contacts found, emails verified.

## Step 6: Deduplicate

**Skill:** `contact-cache`

If `deduplicate_against_cache=true`, check all found leads against the contact cache:

```
contact-cache:
  action: check
  contacts: [qualified leads with emails]
  return: new_only  # filter out previously contacted
```

Log:
- Total leads before dedup
- Leads removed (already in cache)
- Net new leads to proceed with

If `deduplicate_against_cache=false`, skip this step and note it in `pipeline_log.md`.

## Step 7: Output Results

**Capability:** Google Sheets or CSV export

Export the final qualified, deduplicated lead list to `/app/results/qualified_lead_list.csv` with columns:

| Name | Title | Company | LinkedIn URL | Email | Signal | Score |
|------|-------|---------|--------------|-------|--------|-------|

Also write a human-readable summary table to `/app/results/pipeline_log.md`.

**Human checkpoint:** Present the final lead list and any draft email copy to the user for review and approval before launching outreach.

## Step 8: Launch Outreach (Optional)

**Skill:** `setup-outreach-campaign` OR `agentmail`

Only execute this step if `launch_outreach=true` AND the user approved the final list in Step 7.

```bash
if [ "${launch_outreach:-false}" = "true" ]; then
  if [ "${outreach_method:-smartlead}" = "agentmail" ]; then
    # Direct personalized email via AgentMail
    echo "Launching AgentMail outreach for $(wc -l < /app/results/qualified_lead_list.csv) leads"
    # invoke agentmail skill
  else
    # Smartlead campaign setup
    echo "Setting up Smartlead campaign for $(wc -l < /app/results/qualified_lead_list.csv) leads"
    # invoke setup-outreach-campaign skill
  fi
fi
```

Write outreach details (campaign name, lead count, email copy used, campaign ID / confirmation) to `/app/results/outreach_campaign.md`.

If `launch_outreach=false`, write a note to `/app/results/outreach_campaign.md` indicating outreach was not launched and the lead list is ready for manual use.

## Step 9: Iterate on Errors (max 3 rounds)

If any step fails (skill invocation error, no leads found, contact finder returns 0 results):

1. Read the specific error from `pipeline_log.md`
2. Apply the targeted fix from the table below
3. Re-run the affected step
4. Repeat up to 3 times total

### Common Fixes

| Issue | Fix |
|-------|-----|
| `luma-event-attendees` returns empty list | Switch to `conference-speaker-scraper` or refine the topic search string |
| `conference-speaker-scraper` fails | Try fetching the conference agenda page directly and parsing speaker names manually |
| `lead-qualification` qualifies 0 leads | Relax ICP score threshold from 60 to 40 and re-run; flag in summary |
| `company-contact-finder` returns no emails | Broaden target roles in ICP criteria; try Apollo or Hunter fallback if available |
| `contact-cache` skill unavailable | Skip dedup step and note in pipeline_log.md; proceed with full list |
| Outreach launch fails | Save campaign details to outreach_campaign.md for manual setup; do not retry automatically |

After 3 rounds on any step, if still failing, document the failure in `pipeline_log.md` and `summary.md`, skip that step, and continue to the next.

## Final Checklist

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/qualified_lead_list.csv" \
  "$RESULTS_DIR/outreach_campaign.md" \
  "$RESULTS_DIR/pipeline_log.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

LEAD_COUNT=$(tail -n +2 "$RESULTS_DIR/qualified_lead_list.csv" 2>/dev/null | wc -l)
echo "INFO: Qualified lead count: $LEAD_COUNT"

echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] `qualified_lead_list.csv` exists and has at least 1 data row
- [ ] `outreach_campaign.md` exists (either campaign details or explicit note that outreach was skipped)
- [ ] `pipeline_log.md` documents all steps, counts, and decisions
- [ ] `summary.md` includes lead counts at each stage and any issues
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Human checkpoints after Step 4 (qualify) and Step 7 (output review) were both completed with user approval before proceeding
- [ ] Verification script printed PASS for every output file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Luma vs. Conference scraper.** Luma events tend to return richer attendee metadata (names, bios, LinkedIn URLs). Conference speaker scrapers require more post-processing to enrich. Choose based on the event type, not just the URL format.
- **ICP relaxation is a tool, not a crutch.** If you relax the score threshold in Step 9, flag it prominently in `summary.md` so the reviewer knows the list is broader than the original ICP intended.
- **Human checkpoints are mandatory.** Do not skip the approval gates after Step 4 and Step 7. Outreach sent to unreviewed lists is hard to undo and can damage sender reputation.
- **Contact cache is append-only.** After a successful run, add the new contacts to the cache so future pipeline runs don't re-contact the same people. Use the `contact-cache` skill in `append` mode after outreach is confirmed.
- **Deduplication before enrichment saves API calls.** If you have access to the contact cache before Step 3, run a lightweight dedup first to avoid enriching leads you'll discard in Step 6.
- **For Luma-only lead gen** with built-in Google Sheets + Slack alerting, consider using the `get-qualified-leads-from-luma` composite skill instead — it's optimized for that specific use case.
