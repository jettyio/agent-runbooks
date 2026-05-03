---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/playbooks/event-prospecting-pipeline/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/event-prospecting-pipeline
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Event Prospecting Pipeline
  imported_at: '2026-05-03T02:45:38Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: event-prospecting-pipeline
    confidence: high
secrets: null
---

# Event Prospecting Pipeline - Agent Runbook

## Objective

Execute an end-to-end event prospecting workflow: discover event attendees or speakers, research and enrich their companies, qualify them against the requested ICP, deduplicate contacts, and prepare an approved outreach path. The runbook is based on the upstream skill description: Find attendees at conferences/events, research their companies, qualify against ICP, and launch outreach Human review gates are required before contact finding and before any outreach is launched.

## REQUIRED OUTPUT FILES (MANDATORY)

All files must be written under `/app/results` and must be non-empty before the run is complete.

| File | Description |
|---|---|
| `/app/results/raw_attendees.csv` | Raw attendee or speaker list gathered from the event source |
| `/app/results/enriched_leads.csv` | Researched people and companies with role, company, signal, and enrichment notes |
| `/app/results/qualified_leads.csv` | Deduplicated, ICP-qualified contacts with score and rationale |
| `/app/results/outreach_plan.md` | Optional outreach copy and launch plan, only when outreach is approved |
| `/app/results/summary.md` | Executive summary of sources, counts, qualification decisions, and review status |
| `/app/results/validation_report.json` | Structured validation report with stages, results, and `overall_passed` |

## Parameters

| Parameter | Default | Required | Description |
|---|---:|---:|---|
| `results_dir` | `/app/results` | No | Directory for generated artifacts |
| `event_query_or_url` | none | Yes | Luma URL, conference website, event name, topic, or location |
| `icp_criteria` | none | Yes | Ideal customer profile used to qualify enriched leads |
| `launch_outreach` | `false` | No | Whether to prepare or launch outreach after human approval |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---:|---|
| Web search | Capability | Yes | Research events, attendees, companies, roles, and recent signals |
| `luma-event-attendees` | Skill | Conditional | Use for Luma URLs or topic/location event search |
| `conference-speaker-scraper` | Skill | Conditional | Use for conference websites and speaker pages |
| `lead-qualification` | Skill | Yes | Score and filter enriched leads against ICP |
| `company-contact-finder` | Skill | Conditional | Find decision-makers and emails for qualified companies |
| `contact-cache` | Skill | Yes | Deduplicate against prior outreach and known contacts |
| Google Sheets or CSV export | Capability | Yes | Export raw, enriched, and qualified lead tables |
| `cold-email-outreach` or AgentMail API | Skill/API | Optional | Prepare or launch approved outreach |

## Step 1: Environment Setup

1. Create `/app/results` if it does not exist.
2. Confirm `event_query_or_url` and `icp_criteria` are present.
3. Initialize empty CSV files with stable headers so partial runs remain inspectable.
4. If a required input is missing, write `validation_report.json` with `overall_passed=false` and stop.

```bash
mkdir -p /app/results
printf 'name,title,company,profile_url,bio,source,event\n' > /app/results/raw_attendees.csv
printf 'name,title,company,profile_url,email,company_stage,company_size,recent_signal,enrichment_notes\n' > /app/results/enriched_leads.csv
printf 'name,title,company,linkedin_url,email,signal,score,qualification_reason,dedup_status\n' > /app/results/qualified_leads.csv
```

## Step 2: Find Attendees or Speakers

Use the event source to build the raw person list.

- For a Luma event URL or topic/location search, run `luma-event-attendees`.
- For a conference website, run `conference-speaker-scraper`.
- For a broad topic/location request, search for relevant events first, then collect attendees or speakers from the strongest matching sources.

Write every discovered person to `/app/results/raw_attendees.csv` with name, bio, profile links, company, and event source. Preserve source URLs for auditability.

## Step 3: Research and Enrich

For each person and company, collect company funding stage, size, product, recent news, current role, and seniority. Skip deep enrichment only when the operator explicitly requested a raw attendee list.

Write enriched records to `/app/results/enriched_leads.csv`. Include a concise evidence note for each signal so the qualifier can make a defensible scoring decision.

## Step 4: Qualify Against ICP

Run `lead-qualification` against the enriched list and the provided `icp_criteria`. Score each lead and preserve the qualification rationale.

Human checkpoint: after this step, pause for review of the qualified lead list before finding decision-maker contacts.

## Step 5: Find Decision-Maker Contacts

For each qualified company, run `company-contact-finder` to identify the most relevant decision-makers and email addresses. Prefer the contact most aligned with the ICP and buying committee.

Do not find contacts for companies that failed ICP qualification unless the operator explicitly overrides the filter.

## Step 6: Deduplicate

Run `contact-cache` against all candidate contacts. Remove or mark contacts that have already been used in prior outreach or are known duplicates across strategies.

Write the final deduplicated leads to `/app/results/qualified_leads.csv`.

## Step 7: Output Results

Export qualified, deduplicated leads with these columns: `Name`, `Title`, `Company`, `LinkedIn URL`, `Email`, `Signal`, `Score`, `Qualification Reason`, and `Dedup Status`.

Also write `/app/results/summary.md` with event source, raw lead count, enriched count, qualified count, deduplicated count, and any limitations.

## Step 8: Launch Outreach (Optional)

Only proceed when `launch_outreach=true` and a human has approved the final list and copy. Prepare outreach through `cold-email-outreach`, the selected outreach tool, or direct email via AgentMail API.

Write `/app/results/outreach_plan.md` with approved messaging, selected tool, launch status, and contacts included. If outreach is not approved, write the file with `Outreach not launched` and the reason.

## Step 9: Iterate on Errors (max 3 rounds)

If validation fails, perform up to max 3 rounds of targeted fixes:

1. Read `/app/results/validation_report.json`.
2. Fix only the failed stage, such as missing input, empty CSV, malformed summary, or missing outreach decision.
3. Re-run the affected step.
4. Re-run final validation.

### Common Fixes

| Issue | Fix |
|---|---|
| Missing input | Ask for the missing event source or ICP criteria and stop until supplied |
| Empty attendee list | Switch between Luma, conference scraping, and web search discovery |
| Weak enrichment | Add company website, funding, employee count, and recent signal evidence |
| Duplicate contacts | Re-run `contact-cache` and mark duplicate rows with the cache reason |
| Outreach unclear | Write `Outreach not launched` unless human approval is explicit |

## Final Checklist

Run this verification script before finishing.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/raw_attendees.csv" \
  "$RESULTS_DIR/enriched_leads.csv" \
  "$RESULTS_DIR/qualified_leads.csv" \
  "$RESULTS_DIR/outreach_plan.md" \
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
report = pathlib.Path("/app/results/validation_report.json")
data = json.loads(report.read_text())
if not data.get("overall_passed"):
    sys.exit("FAIL: validation_report.json overall_passed is false")
print("PASS: validation_report.json overall_passed is true")
PY
```

## Tips

- Use the upstream event source as evidence and keep source URLs in every table.
- Preserve the two human checkpoints: after qualification and before outreach.
- When the user asks for only a raw attendee list, skip enrichment and write that scope decision into `summary.md`.
