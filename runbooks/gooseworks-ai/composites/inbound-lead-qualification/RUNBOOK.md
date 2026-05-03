---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/inbound-lead-qualification/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/inbound-lead-qualification
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Inbound Lead Qualification
  imported_at: '2026-05-03T02:54:14Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: inbound-lead-qualification
    confidence: high
secrets: null
---

# Inbound Lead Qualification — Agent Runbook

## Objective

Qualifies inbound leads against full ICP criteria — company size, industry, use case fit, role/seniority of the person. Checks CRM and existing customer base for duplicates and existing relationships. Outputs a scored CSV with qualification status, reasoning, and pipeline overlap flags. Tool-agnostic — works with any CRM, enrichment tool, or data source.

This runbook converts the imported skill into a repeatable Jetty execution flow with explicit inputs, required artifacts, validation, and provenance. Preserve the intent of the upstream skill while producing auditable outputs under `/app/results`. When the source procedure requires judgment, document the decision in `summary.md` and keep all generated artifacts deterministic enough for review.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/summary.md` | Executive summary of the run, decisions made, and final status. |
| `/app/results/validation_report.json` | Structured validation report with stages, results, and `overall_passed`. |
| `/app/results/provenance.json` | Source URL, import metadata, parameters used, and timestamp. |
| `/app/results/output.md` | Primary task output produced by following the imported skill. |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `results_dir` | `/app/results` | Directory where all required output files are written. |
| `origin_url` | `https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/inbound-lead-qualification/SKILL.md` | Canonical upstream skill source used for provenance. |
| `user_supplied_url` | `https://skills.gooseworks.ai/skills/inbound-lead-qualification` | URL originally supplied by the operator. |

## Dependencies

| Dependency | Required | Purpose |
|---|---|---|
| `python` | Yes | Write structured metadata and validation reports. |
| `bash` | Yes | Run setup, validation, and final verification commands. |
| Source-specific tools | As needed | Tools referenced by the imported skill: in_pipeline, pipeline_detail, pipeline_status, right_company_wrong_person, right_person_wrong_company, code:json, code:markdown. |

## Step 1: Environment Setup

Create the required output directory and initialize the report files before performing any source-specific work.

```bash
set -euo pipefail
RESULTS_DIR="${RESULTS_DIR:-/app/results}"
mkdir -p "$RESULTS_DIR"
python - <<'PY'
from pathlib import Path
Path('/app/results').mkdir(parents=True, exist_ok=True)
PY
```

## Step 2: Review Source Skill

Read the imported source instructions and identify the concrete task, expected inputs, and completion criteria before acting. The canonical upstream source is recorded in frontmatter as `origin.url`; use that value for provenance instead of any directory mirror.

### Imported Source Outline

### Inbound Lead Qualification

Takes a set of inbound leads and validates each against your full ICP criteria. Not a fast-pass triage (that's `inbound-lead-triage`) — this is the thorough qualification step that determines whether a lead is genuinely worth pursuing, and produces a scored CSV for the team.

### When to Auto-Load

Load this composite when:
- User says "qualify these inbound leads", "check if these leads are ICP", "score my inbound"
- An upstream triage has been completed and leads need deeper qualification
- User has a batch of leads and wants a qualified/disqualified verdict on each

### Architecture

```
[Inbound Leads] → Step 1: Load ICP & Config → Step 2: CRM/Pipeline Check → Step 3: Company Qualification → Step 4: Person Qualification → Step 5: Use Case Fit → Step 6: Score & Verdict → Step 7: Output CSV
```

---

### Step 0: Configuration (Once Per Client)

On first run, establish the ICP definition and CRM access. Save to the current working directory or wherever the user prefers (e.g., `config/lead-qualification.json`).

```json
{
  "icp_definition": {
    "company_size": {
      "min_employees": null,
      "max_employees": null,
      "sweet_spot": "",
      "notes": ""
    },
    "industry": {
      "target_industries": [],
      "excluded_industries": [],
      "notes": ""
    },
    "use_case": {
      "primary_use_cases": [],
      "secondary_use_cases": [],
      "anti_use_cases": [],
      "notes": ""
    },
    "company_stage": {
      "target_stages": [],
      "excluded_stages": [],
      "notes": ""
    },
    "geography": {
      "target_regions": [],
      "excluded_regions": [],
      "notes": ""
    }
  },
  "buyer_personas": [
    {
      "name": "",
      "titles": [],
      "seniority_levels": [],
      "departments": [],
      "is_economic_buyer": false,
      "is_champion": false,
      "is_user": false
    }
  ],
  "hard_disqualifiers": [],
  "hard_qualifiers": [],
  "crm_access": {
    "tool": "HubSpot | Salesforce | CSV export | none",
    "access_method": "",
    "tables_or_objects": []
  },
  "existing_customer_source": {
    "tool": "HubSpot | Salesforce | CSV | none",
    "access_method": ""
  },
  "qualification_prompt_path": "path/to/lead-qualification/prompt.md or null"
}
```

**If `lead-qualification` capability already has a saved qualification prompt:** Reference it directly — don't rebuild ICP criteria from scratch.

**On subsequent runs:** Load config silently.

---

### Process

1. Load the client's ICP config (or qualification prompt from `lead-qualification` capability)
2. Parse the inbound lead list — accept any format:
   - Output from `inbound-lead-triage` (already normalized)
   - Raw CSV with any column structure
   - Pasted list of names/emails/companies
   - CRM export
3. Identify what data is available vs. missing per lead:
   - **Have:** Fields present in the input
   - **Need:** Fields required for qualification but missing
   - **Gap report:** "X leads have company name, Y have title, Z have nothing but email"

### Output

- Parsed lead list with available/missing field inventory
- Gap report for the user

### Human Checkpoint

If >50% of leads are missing critical fields (company name or person title), recommend running `inbound-lead-enrichment` first. Ask: "Many leads are missing company/title data. Want me to enrich them first, or qualify with what's available?"

---

### Process

For each lead, check against existing data sources to identify overlaps:

**Check 1 — Existing customer?**
- Search customer database by company domain/name
- If match found: Flag as `existing_customer` with customer details (plan, account owner, contract status)
- This is NOT a disqualification — it's a routing flag (upsell vs. new business)

**Check 2 — Already in pipeline?**
- Search your CRM (HubSpot, Salesforce, CSV) for the company in active deals
- If match found: Flag as `in_pipeline` with deal details (stage, owner, last activity)
- Critical: Sales rep should know before reaching out that a colleague already has this account

**Check 3 — Previous engagement?**
- Search outreach logs for the email/company
- If match found: Flag as `previously_contacted` with history summary (when, what channel, outcome)

**Check 4 — Known from signal composites?**
- Search your CRM or signal tracking system for the company
- If match found: Flag as `signal_flagged` with signal type and date

## Step 3: Execute Skill Procedure

Follow the upstream skill's procedure in the current workspace. Keep outputs under `/app/results`, avoid writing secrets to disk, and capture any assumptions or operator-supplied values in `summary.md`.

When the skill asks for iterative work, run a bounded loop with max 3 rounds: execute the procedure, inspect the result against the source criteria, apply targeted fixes, and stop early once validation passes.

## Step 4: Generate Required Outputs

Write the primary output, provenance metadata, and a human-readable summary. Include enough context for a reviewer to reproduce the run without reading transient logs.

```bash
python - <<'PY'
import json, datetime as dt
from pathlib import Path
results = Path('/app/results')
results.mkdir(parents=True, exist_ok=True)
now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
(results / 'provenance.json').write_text(json.dumps({
  'origin_url': 'https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/inbound-lead-qualification/SKILL.md',
  'user_supplied_url': 'https://skills.gooseworks.ai/skills/inbound-lead-qualification',
  'imported_by': 'skill-to-runbook-converter@1.1.0',
  'generated_at': now
}, indent=2) + '\n')
if not (results / 'output.md').exists():
    (results / 'output.md').write_text('# Output\n\nComplete the source-specific task and replace this placeholder with the final artifact.\n')
PY
```

## Step 5: Validate Outputs

Check that every required artifact exists, is non-empty, and contains the expected structured fields. Treat missing required files as failures and fix them before proceeding.

```bash
python - <<'PY'
import json, datetime as dt
from pathlib import Path
results = Path('/app/results')
required = ['summary.md', 'validation_report.json', 'provenance.json', 'output.md']
stages = []
for file_name in required:
    path = results / file_name
    stages.append({'name': 'file:' + file_name, 'passed': path.exists() and path.stat().st_size > 0, 'message': str(path)})
overall = all(s['passed'] for s in stages)
report = {
  'version': '1.0.0',
  'run_date': dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z'),
  'stages': stages,
  'results': {'pass': sum(1 for s in stages if s['passed']), 'partial': 0, 'fail': sum(1 for s in stages if not s['passed'])},
  'overall_passed': overall
}
(results / 'validation_report.json').write_text(json.dumps(report, indent=2) + '\n')
raise SystemExit(0 if overall else 1)
PY
```

## Step 6: Iterate on Errors (max 3 rounds)

If validation fails, inspect `/app/results/validation_report.json`, make the smallest targeted correction, and re-run Step 5. Repeat for max 3 rounds, then stop and record remaining failures in `summary.md` if the run still does not pass.

## Common Fixes

| Issue | Fix |
|---|---|
| Missing required output file | Create the file under `/app/results` and re-run validation. |
| Empty summary | Add task outcome, key assumptions, and links or paths to generated artifacts. |
| Provenance missing | Recreate `provenance.json` from the frontmatter `origin` block. |
| Source tool unavailable | Record the unavailable dependency and use the closest deterministic fallback only when it preserves the source intent. |

## Tips

Follow the upstream skill's intent, keep artifacts auditable, and prefer deterministic outputs where the source leaves implementation choices open.

## Final Checklist

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/provenance.json" \
  "$RESULTS_DIR/output.md"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```
