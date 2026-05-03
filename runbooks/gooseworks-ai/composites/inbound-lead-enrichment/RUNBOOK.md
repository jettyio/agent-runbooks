---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/inbound-lead-enrichment/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/inbound-lead-enrichment
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Inbound Lead Enrichment
  imported_at: '2026-05-03T02:53:23Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: inbound-lead-enrichment
    confidence: high
secrets: null
---

# Inbound Lead Enrichment — Agent Runbook

## Objective

This runbook enriches incomplete inbound lead records into qualification-ready lead profiles. It researches each company, identifies the lead role and seniority, discovers relevant stakeholders, checks CRM or pipeline relationships, and emits structured outputs for outreach or routing. The workflow is tool-agnostic: operators may use SixtyFour, Orthogonal, web search, HubSpot, Salesforce, or CSV exports depending on available access. It includes human checkpoints for ambiguous matches, sensitive relationship updates, and low-confidence enrichment.

## REQUIRED OUTPUT FILES (MANDATORY)

All files must be written under `{{results_dir}}`, which defaults to `/app/results`.

| File | Description |
|---|---|
| `enriched_leads.json` | Structured enriched lead records, including company, person, stakeholder, relationship, confidence, and provenance fields. |
| `enriched_leads.csv` | Flattened table suitable for CRM import or handoff. |
| `enrichment_report.md` | Human-readable summary of enrichment coverage, data quality, stakeholder findings, relationship flags, and costs. |
| `summary.md` | Executive summary of this run, input counts, output locations, unresolved issues, and recommended next actions. |
| `validation_report.json` | Programmatic validation results for setup, input parsing, enrichment completeness, output generation, and final file checks. |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `results_dir` | `/app/results` | Directory where all required output files are written. |
| `leads_input` | Required | CSV, JSON, CRM export, or pasted table containing inbound leads to enrich. |
| `crm_source` | `none` | CRM or relationship source, such as HubSpot, Salesforce, CSV, or none. |
| `enrichment_tools` | `web-search` | Available company research, person research, and stakeholder discovery tools. |
| `buyer_personas` | empty list | Optional persona definitions used to prioritize stakeholders and fit. |
| `enrichment_depth` | `standard` | Depth per lead tier: minimal, standard, or deep. |

## Dependencies

| Dependency | Required | Description |
|---|---|---|
| Web research or enrichment access | Yes | Used to research company, role, seniority, stakeholders, and public evidence. |
| Lead input data | Yes | Email addresses or partial lead records to enrich. |
| CRM or relationship source | Optional | HubSpot, Salesforce, CSV, or similar source used to detect existing relationships. |
| CSV/JSON writing capability | Yes | Required to emit `enriched_leads.csv`, `enriched_leads.json`, and validation artifacts. |
| Human review availability | Conditional | Required for ambiguous identity matches, low-confidence stakeholder mapping, or sensitive relationship changes. |

## Step 1: Environment Setup

1. Create `results_dir` if it does not exist.
2. Confirm `leads_input` is present and readable.
3. Confirm which enrichment tools and CRM sources are available for the run.
4. Initialize `validation_report.json` with setup, input, enrichment, output, and final verification stages.

```bash
mkdir -p "${results_dir:-/app/results}"
test -n "${leads_input:-}" || echo "leads_input must be supplied by the orchestrator"
```

## Step 2: Configure Client Context

Establish enrichment preferences before processing the first lead. On subsequent runs for the same client, load the saved configuration silently when available.

```json
{
  "enrichment_tools": {
    "company_research": {"primary": "SixtyFour | Orthogonal | web-search", "secondary": "web-search"},
    "person_research": {"primary": "SixtyFour | Orthogonal | web-search", "secondary": "web-search"},
    "stakeholder_finding": {"primary": "SixtyFour | Orthogonal | web-search", "secondary": "web-search"}
  },
  "crm_source": {"tool": "HubSpot | Salesforce | CSV | none", "access_method": ""},
  "buyer_personas": [],
  "enrichment_depth": {
    "tier_1_leads": "deep",
    "tier_2_leads": "deep",
    "tier_3_leads": "standard",
    "tier_4_leads": "minimal",
    "untiered_leads": "standard"
  }
}
```

## Step 3: Assess Data Gaps

For each lead, inventory known fields and classify missing data. Track whether each record needs company research, person research, stakeholder discovery, CRM relationship checks, or human review. Emit a gap inventory containing known fields, missing fields, enrichment depth, and gating issues.

Use these gap classes: `minimal`, `standard`, `deep`, and `human_review_required`. Pause for human input when the same email or name can map to multiple people or companies.

## Step 4: Company Research

Research the organization connected to each lead. Capture company name, website, industry, size, location, growth signals, business model, recent news, and credible evidence URLs or notes. For personal email domains, infer the company only from explicit evidence, such as the lead's public profile or email signature; otherwise mark company identity as unresolved.

Write company findings into each lead record with confidence values and provenance.

## Step 5: Person Research

Identify the person's role, seniority, function, likely buying influence, location, and profile evidence. Resolve aliases carefully and avoid merging records unless there is high-confidence evidence that the identity matches the inbound lead.

If role or company evidence conflicts, preserve both possibilities in the lead record and set `human_review_required=true`.

## Step 6: Stakeholder Discovery

Find relevant stakeholders at the same company based on buyer personas, deal context, and likely buying committee structure. Prioritize stakeholders by function, seniority, public relevance to the problem, and relationship proximity.

Include stakeholder name, title, function, source evidence, confidence, and recommended outreach relevance.

## Step 7: Relationship Check

Check the CRM, pipeline export, or relationship source for existing contacts, accounts, opportunities, open deals, past meetings, owner assignments, and known relationships. Do not overwrite CRM fields directly unless the orchestrator has explicitly granted update permission.

Flag conflicts such as duplicate accounts, existing active opportunities, customer status, do-not-contact markers, and ownership ambiguity.

## Step 8: Compile Outputs

Produce `enriched_leads.json`, `enriched_leads.csv`, and `enrichment_report.md`. Each enriched lead record should include:

| Field | Description |
|---|---|
| `input_lead` | Original lead payload. |
| `company` | Enriched company profile and evidence. |
| `person` | Enriched person profile and evidence. |
| `stakeholders` | Prioritized stakeholder list. |
| `relationships` | CRM, pipeline, ownership, or relationship findings. |
| `confidence` | Per-category confidence and overall confidence. |
| `recommended_next_action` | Qualification, outreach, routing, or human-review recommendation. |
| `provenance` | Sources, timestamps, and tools used. |

The report must summarize input count, enrichment coverage, unresolved fields, relationship flags, cost or tool usage if available, and records requiring human review.

## Step 9: Iterate on Errors (max 3 rounds)

If validation fails or any required output is missing, perform up to max 3 rounds of targeted repair:

1. Read `validation_report.json` and identify the failed stage.
2. Repair only the affected input, enrichment, formatting, or output issue.
3. Re-run the relevant enrichment or output generation step.
4. Re-run final validation before continuing.

Stop after max 3 rounds and mark `overall_passed=false` if required outputs remain missing or empty.

## Step 10: Write Summary

Write `summary.md` with run date, input count, enrichment depth, available tools, CRM source, output paths, records requiring human review, and any unresolved data-quality issues.

## Step 11: Final Checklist

Before completing the run, verify every required output file exists and is non-empty, and validate that JSON and CSV outputs parse.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="${results_dir:-/app/results}"
for f in \
  "$RESULTS_DIR/enriched_leads.json" \
  "$RESULTS_DIR/enriched_leads.csv" \
  "$RESULTS_DIR/enrichment_report.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
python -m json.tool "$RESULTS_DIR/enriched_leads.json" >/dev/null
python -m json.tool "$RESULTS_DIR/validation_report.json" >/dev/null
```

## Final Checklist

- `enriched_leads.json` exists, parses as JSON, and contains one record per input lead.
- `enriched_leads.csv` exists and contains stable headers for CRM import.
- `enrichment_report.md` summarizes coverage, quality, relationship flags, and unresolved issues.
- `summary.md` identifies outputs and follow-up actions.
- `validation_report.json` includes stage results and `overall_passed`.
- Final output verification printed `PASS` for every required file.

## Common Fixes

| Issue | Fix |
|---|---|
| Input rows do not parse | Normalize to CSV or JSON before enrichment and preserve the original payload in `input_lead`. |
| Company identity is ambiguous | Keep all plausible matches, lower confidence, and set `human_review_required=true`. |
| CRM access is unavailable | Mark relationship fields as `not_checked` and continue with public enrichment. |
| Stakeholder discovery is sparse | Use buyer personas and known company functions to broaden the search, while preserving evidence and confidence. |
| Required output is missing | Regenerate only the missing artifact and rerun final verification. |

## Tips

Prefer evidence-backed enrichment over inferred certainty. Preserve provenance for every material claim so downstream qualification and outreach teams can audit why a lead was routed or prioritized.
