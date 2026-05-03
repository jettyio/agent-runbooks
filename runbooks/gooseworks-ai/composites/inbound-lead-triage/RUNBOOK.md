---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/inbound-lead-triage/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/inbound-lead-triage
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Inbound Lead Triage
  imported_at: '2026-05-03T02:58:47Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: inbound-lead-triage
    confidence: high
secrets: null
---

# Inbound Lead Triage — Agent Runbook

## Objective

Triage inbound leads for a requested period by collecting configured lead sources, normalizing records, ranking urgency, checking ICP fit, enriching context, and producing a prioritized action queue. The runbook converts the source skill's tool-agnostic workflow into a Jetty programmatic runbook with explicit output files and validation. It should work with API-backed sources, CSV exports, MCP tools, or manually pasted leads.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary of lead volume, source coverage, top-priority accounts, and follow-up recommendations |
| `/app/results/validation_report.json` | Structured validation report for setup, collection, classification, enrichment, output generation, and final checks |
| `/app/results/inbound_lead_triage.md` | Human-readable prioritized action queue grouped by urgency tier |
| `/app/results/inbound_lead_triage.csv` | Flat export of all normalized leads with triage fields and recommended actions |
| `/app/results/dedup_report.json` | Counts by source, duplicate merges, and any records excluded from triage |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `results_dir` | `/app/results` | Output directory for all required artifacts |
| `time_period` | `last 24 hours` | Period to inspect for inbound leads |
| `lead_sources` | `configured sources` | CRM, form tool, product database, event platform, chatbot, CSV, or pasted leads |
| `qualification_prompt_path` | `null` | Optional existing ICP qualification prompt to apply in fast mode |
| `response_preferences` | `configured defaults` | SLA and tone guidance for response drafts |

## Dependencies

| Dependency | Required | Purpose |
|------------|----------|---------|
| Lead source access | Yes | Read demo requests, trial signups, content downloads, webinar registrations, chatbot conversations, CSVs, or pasted leads |
| Company context | Recommended | Identify ICP fit, market segment, customer status, competitor status, and recent activity |
| Person context | Recommended | Understand title, seniority, buying role, and recent engagement |
| Email drafting capability | Recommended | Draft concise follow-up responses using the configured response preferences |
| Calendar access | Optional | Include available time slots for Tier 1 response drafts |

## Step 1: Environment Setup

1. Create `/app/results` if it does not exist.
2. Confirm that the requested `time_period` is explicit enough to query each lead source.
3. Load `config/inbound-triage.json` when present. If it is missing and the user did not provide raw leads, ask for source configuration before collecting leads.
4. Confirm each configured source can be read. If a source is unavailable, record it in `validation_report.json` and continue with available sources only when the user approves.

```bash
mkdir -p /app/results
```

## Step 2: Configuration (Once Per Client)

On first run, ask the user to configure their lead sources and preferences. Save to the current working directory or wherever the user prefers (e.g., `config/inbound-triage.json`).

```json
{
  "lead_sources": {
    "demo_requests": {
      "source_tool": "HubSpot | Salesforce | Typeform | CSV | other",
      "access_method": "API | CSV export | MCP tool | manual paste",
      "fields_available": ["name", "email", "company", "title", "message"]
    },
    "free_trial_signups": {
      "source_tool": "product database | Stripe | CSV | other",
      "access_method": "API | CSV export | manual paste",
      "fields_available": ["name", "email", "company", "signup_date", "plan"]
    },
    "content_downloads": {
      "source_tool": "HubSpot | Marketo | CSV | other",
      "access_method": "API | CSV export | manual paste",
      "fields_available": ["name", "email", "company", "content_title", "download_date"]
    },
    "webinar_registrations": {
      "source_tool": "Zoom | Luma | CSV | other",
      "access_method": "API | CSV export | manual paste",
      "fields_available": ["name", "email", "company", "webinar_title", "attended"]
    },
    "chatbot_conversations": {
      "source_tool": "Intercom | Drift | Crisp | CSV | other",
      "access_method": "API | CSV export | manual paste",
      "fields_available": ["name", "email", "company", "conversation_summary", "intent"]
    }
  },
  "urgency_overrides": {},
  "response_preferences": {
    "demo_request_sla": "< 1 hour",
    "trial_signup_sla": "< 4 hours",
    "default_sla": "< 24 hours"
  },
  "qualification_prompt_path": "path/to/existing/qualification-prompt.md or null"
}
```

**On subsequent runs:** Load config silently, skip setup.

**If user provides a raw CSV or pastes leads inline:** Skip source config — just classify what's given.

---

## Step 3: Collect Leads



## Step 4: Classify & Rank by Urgency



## Step 5: Qualify Against ICP



## Step 6: Enrich with Context



## Step 7: Route & Recommend Response



## Step 8: Write Required Outputs

Write `/app/results/inbound_lead_triage.md` with a prioritized action queue grouped by urgency tier. Include lead name, company, source signal, ICP fit, urgency reason, recommended owner, next action, and a response draft where appropriate.

Write `/app/results/inbound_lead_triage.csv` with one row per normalized lead and these columns at minimum: `name`, `email`, `company`, `title`, `source_type`, `source_detail`, `timestamp`, `urgency_tier`, `urgency_reason`, `icp_fit`, `fit_reasoning`, `recommended_action`, `response_draft`, `company_context`, `person_context`, and `engagement_context`.

Write `/app/results/dedup_report.json`, `/app/results/summary.md`, and `/app/results/validation_report.json`.

## Step 9: Iterate on Errors (max 3 rounds)

If output generation or validation fails, perform a targeted correction and retry for max 3 rounds. Do not broaden the task beyond the failed stage.

| Issue | Common Fix |
|-------|------------|
| Source authentication failed | Ask for an export or pasted leads, then mark the unavailable source in the report |
| Required lead fields missing | Preserve raw fields and leave derived fields empty with an explanatory note |
| Duplicate merge is ambiguous | Keep the newest record primary and list merged sources in `dedup_report.json` |
| Enrichment tool unavailable | Use available CRM/source context and mark enrichment as partial |
| Response draft is unsafe or unsupported | Provide a recommended action without a draft and explain why |

## Final Checklist

This is the final Step 10 checkpoint for the runbook.

Run the final verification after all outputs are written.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/inbound_lead_triage.md" \
  "$RESULTS_DIR/inbound_lead_triage.csv" \
  "$RESULTS_DIR/dedup_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

- Confirm `summary.md` names the time period, sources checked, source failures, lead counts, and highest-priority follow-up.
- Confirm `validation_report.json` includes stages, results, and `overall_passed`.
- Confirm Tier 1 leads have an explicit next action and owner.
- Confirm poor-fit, competitor, existing-customer, and spam records are separated from the sales action queue.

## Tips

Keep the workflow tool-agnostic: use the best available source access method, preserve raw lead fields, and mark partial enrichment honestly instead of inventing missing context.

## Provenance

- Origin URL: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/inbound-lead-triage/SKILL.md
- User-supplied URL: https://skills.gooseworks.ai/skills/inbound-lead-triage
- Imported from directory mirror: true
- Source host: raw.githubusercontent.com
- Imported at: 2026-05-03T02:58:47Z
- Attribution: `runbooks/gooseworks-ai/composites/inbound-lead-triage/RUNBOOK.md`
