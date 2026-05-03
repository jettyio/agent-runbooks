---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/playbooks/signal-detection-pipeline/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/signal-detection-pipeline
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Signal Detection Pipeline
  imported_at: '2026-05-03T02:46:01Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: signal-detection-pipeline
    confidence: high
secrets: {}
---
# Signal Detection Pipeline — Agent Runbook

## Objective

Detect buying signals from multiple sources, qualify leads, and generate outreach context. This runbook monitors multiple buying-signal sources, combines the evidence into a prioritized account list, and produces outreach context for qualified leads. Operators should run only the sources relevant to the target ICP, then deduplicate, score, enrich, and review the resulting leads before outreach.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/signal_report.md` | Narrative report of sources searched, signal quality, and prioritized leads |
| `/app/results/leads.csv` | Consolidated lead table with company, signal sources, strength, context, and outreach angle |
| `/app/results/summary.md` | Executive summary of run metadata, inputs, lead counts, and review notes |
| `/app/results/validation_report.json` | Structured validation results with stages, result counts, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `results_dir` | `/app/results` | Output directory for all required files |
| `client_solution` | required | Product, service, or problem area to detect buying intent for |
| `icp_criteria` | required | Target industry, company size, geography, personas, and exclusion criteria |
| `signal_sources` | `job postings,funding,conference attendance,reddit,linkedin` | Comma-separated signal sources to run |
| `keywords` | inferred from `client_solution` | Problem, job, funding, content, and community search terms |
| `time_window` | `last 90 days` | Recency window used when collecting and scoring signals |
| `max_leads` | `50` | Maximum number of leads to include in the final prioritized table |

Inferred source inputs from the skill: job keywords, ICP criteria, industry, funding stage filter, event URLs or topic search, relevant subreddits, keywords, and time frame.

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| `python` | CLI | Yes | Used for validation and optional CSV normalization |
| `requests` | Python package | Optional | Useful for API-backed source collection when available |
| `pandas` | Python package | Optional | Useful for deduplication and CSV cleanup |
| Web search access | External tool | Yes | Used to enrich top leads with company details |
| Source-specific skills | Agent skills | Conditional | `job-posting-intent`, `funding-signal-monitor`, `luma-event-attendees`, `reddit-post-finder`, `linkedin-post-research`, and `linkedin-commenter-extractor` when those sources are selected |

## Step 1: Environment Setup

Create the output directory and capture the resolved run inputs before collecting signals.

```bash
mkdir -p /app/results /app/results/work
cat > /app/results/work/run_inputs.json <<'JSON'
{
  "results_dir": "/app/results",
  "client_solution": "<resolved client_solution>",
  "icp_criteria": "<resolved icp_criteria>",
  "signal_sources": "job postings,funding,conference attendance,reddit,linkedin",
  "time_window": "last 90 days",
  "max_leads": 50
}
JSON
```

If `client_solution` or `icp_criteria` is not resolved, stop and write `validation_report.json` with setup marked as failed.

## Step 2: Select Signal Sources

Run the sources relevant to the client ICP. Each source is independent and can be collected in parallel when tooling is available.

| Source | Strength | Input | Expected output |
|---|---|---|---|
| Job posting signals | Strongest | Job keywords and ICP criteria | Qualified companies with hiring intent and outreach angles |
| Funding signals | Strong | Industry and funding stage filter | Funded companies with timing context |
| Conference attendance signals | Medium | Event URLs or topic search | Person and company list |
| Reddit pain signals | Medium | Keywords and relevant subreddits | Posts with authors and context |
| LinkedIn content signals | Medium | Keywords and time frame | Posters and commenters with engagement data |

Write each raw source result under `/app/results/work/` using a source-specific filename such as `job_posting_signals.json` or `reddit_pain_signals.json`.

## Step 3: Collect Source Evidence

For every selected source, capture enough evidence to explain why each lead is in market. Prefer structured records with these fields: `company`, `person`, `source`, `signal_date`, `signal_summary`, `source_url`, `confidence_notes`, and `outreach_angle`.

When source-specific skills are available, run them using the inputs in Step 1. When a source-specific skill is unavailable, use web search or manual research to gather equivalent evidence and document the fallback in `signal_report.md`.

## Step 4: Combine Signals

Deduplicate companies across all selected sources and preserve every signal attached to each company. Multi-signal companies should be retained as the strongest leads.

```python
# Pseudocode for normalization; adapt to the actual source files collected.
# Load source records, group by normalized company domain/name, and retain all evidence rows.
```

Score each lead using source quality and recency. Job posting plus funding is highest intent, LinkedIn content plus Reddit complaint validates pain, and single conference attendance is awareness-level only.

## Step 5: Enrich Top Leads

Use web search to enrich the highest-scoring companies with current company details, relevant contacts, buying trigger context, and a concise outreach angle. Keep citations or source URLs in the working notes so a reviewer can audit the evidence.

## Step 6: Human Checkpoint

After combining signals, review the consolidated list before outreach. Remove companies that do not match the ICP, downgrade weak or stale evidence, and confirm that the outreach context follows from the collected signals.

## Step 7: Write Final Outputs

Create `/app/results/leads.csv` with this header:

```csv
company,signal_sources,signal_strength,context,outreach_angle,source_urls,review_status
```

Create `/app/results/signal_report.md` summarizing selected sources, notable signal clusters, excluded leads, scoring rationale, and the final prioritized list.

## Step 8: Iterate on Errors (max 3 rounds)

If validation fails or the lead table is incomplete, run up to max 3 rounds of targeted fixes: fill missing required files, normalize malformed CSV rows, add missing source URLs, or re-score leads with ambiguous evidence. Stop after 3 rounds and record any residual issue in `summary.md` and `validation_report.json`.

## Common Fixes

| Issue | Fix |
|---|---|
| Missing `leads.csv` | Re-run Step 7 and write the required CSV header even if no leads were found |
| Missing source URLs | Revisit source evidence and add at least one audit URL or note `not_available` with rationale |
| Weak ICP fit | Move the company to excluded leads in `signal_report.md` |
| Duplicate company rows | Merge rows and combine `signal_sources` with semicolon separators |
| No selected sources returned evidence | Write an empty `leads.csv`, explain the zero-result search in `signal_report.md`, and keep validation passing |

## Final Checklist

Run the verification script before finishing.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in   "$RESULTS_DIR/signal_report.md"   "$RESULTS_DIR/leads.csv"   "$RESULTS_DIR/summary.md"   "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
python - <<'VERIFY_PY'
import csv, json, pathlib
results = pathlib.Path('/app/results')
with (results / 'leads.csv').open(newline='') as f:
    header = next(csv.reader(f), [])
required = ['company','signal_sources','signal_strength','context','outreach_angle','source_urls','review_status']
missing = [c for c in required if c not in header]
print('PASS: leads.csv header complete' if not missing else 'FAIL: missing CSV columns ' + ', '.join(missing))
report = json.loads((results / 'validation_report.json').read_text())
print('PASS: validation_report overall_passed true' if report.get('overall_passed') is True else 'FAIL: validation_report overall_passed is not true')
VERIFY_PY
```

## Tips

Run independent signal sources in parallel when possible, but consolidate and review them before outreach. Treat multi-signal companies as the strongest leads and keep the evidence trail visible in the final report.

## Source Skill Notes

Imported from a Gooseworks directory mirror. The resolved upstream source is `https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/playbooks/signal-detection-pipeline/SKILL.md`.
