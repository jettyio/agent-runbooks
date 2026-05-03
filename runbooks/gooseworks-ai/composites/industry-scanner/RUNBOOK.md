---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/industry-scanner/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/industry-scanner
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Industry Scanner
  imported_at: '2026-05-03T02:45:35Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: industry-scanner
    confidence: high
secrets: null
---

# Industry Scanner - Agent Runbook

## Objective
Run a daily or weekly industry intelligence scan for a client by using the client's configured keywords, sources, competitor list, and positioning context. The runbook gathers relevant signals from web search, news, blogs, communities, social media, events, funding, jobs, and regulatory sources, then synthesizes a briefing and GTM opportunity ideas. It orchestrates existing collection skills and tools where available; it does not reimplement source-specific scraping logic.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/industry_briefing.md` | Comprehensive industry intelligence briefing for the requested client and lookback period |
| `/app/results/source_findings.json` | Structured list of findings, URLs, source names, timestamps, and relevance notes |
| `/app/results/gtm_opportunities.md` | Strategic GTM opportunity ideas derived from the scan |
| `/app/results/summary.md` | Executive summary of the run, inputs, key findings, and issues |
| `/app/results/validation_report.json` | Programmatic validation report with stages, results, and overall status |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `results_dir` | `/app/results` | Output directory for all required artifacts |
| `client_name` | required | Client identifier used to load `clients/<client>/config/industry-scanner.json` and `clients/<client>/context.md` |
| `lookback_period` | `1` | Number of days to scan; use `7` for weekly deep scans |
| `focus_area` | none | Optional category filter such as competitors, events, funding, regulations, or communities |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| Web/news/search access | External | Yes | Needed to gather current industry signals from configured sources |
| Client industry scanner config | File | Yes | `clients/<client>/config/industry-scanner.json` defines keywords, sources, competitors, and URLs |
| Client context | File | Yes | `clients/<client>/context.md` provides ICP, value props, and positioning |
| Existing source skills | Agent skills | Preferred | Use available skills for blog feeds, Reddit, social, news, web search, events, and related collection tasks |
| Python 3 | CLI | Optional | Useful for JSON validation and final output checks |

## Step 1: Environment Setup

1. Create the output directory and confirm the client inputs are present.
2. Resolve `client_name`, `lookback_period`, and optional `focus_area` before collecting sources.
3. Read `clients/<client>/config/industry-scanner.json` and `clients/<client>/context.md`.
4. Note the current UTC date for output filenames and date-bounded queries.

```bash
mkdir -p /app/results
CLIENT_CONFIG="clients/<client>/config/industry-scanner.json"
CLIENT_CONTEXT="clients/<client>/context.md"
test -s "$CLIENT_CONFIG"
test -s "$CLIENT_CONTEXT"
```

## Step 2: Load Client Configuration

Follow the source skill procedure, using configured client context and bounded source collection.

## Step 3: Collect Industry Signals

Run the configured scans over the selected lookback window. Use the source-specific skills and scripts referenced by the client configuration for blogs, Reddit, social media, news, search, events, funding, jobs, and regulatory updates. Keep each finding tied to its source URL, source type, observed date, and relevance rationale.

When a source fails, record the failure in the validation report and continue with the remaining sources unless the failed source is mandatory for the requested focus area.

## Step 4: Normalize and Deduplicate Findings

Convert raw results into a common record shape with `title`, `url`, `source_type`, `published_or_observed_at`, `entities`, `summary`, `relevance`, and `confidence`. Deduplicate by canonical URL first, then by highly similar title and source.

Write the normalized result set to `/app/results/source_findings.json`.

## Step 5: Analyze Patterns and Prioritize Signals

Cluster findings by competitor movement, customer pain, technology shifts, funding, hiring, events, regulatory changes, partnerships, community discussion, and content trends. Score each cluster for recency, source confidence, fit with the client's ICP, and GTM relevance.

## Step 6: Generate Briefing and GTM Opportunities

Write `/app/results/industry_briefing.md` with the most important signals, why they matter, and cited source URLs. Then write `/app/results/gtm_opportunities.md` with concrete campaign, partnership, messaging, content, sales, or product-led growth ideas tied back to evidence from the scan.

## Step 7: Iterate on Errors (max 3 rounds)

If collection, normalization, or validation fails, perform up to max 3 rounds of targeted repair:

1. Identify the failed source, missing field, or malformed output.
2. Re-run only the affected collection or synthesis step.
3. Re-write the impacted output file.
4. Re-run the final validation script.

After max 3 rounds, keep the partial outputs, mark the failed stages in `/app/results/validation_report.json`, and call out the limitation in `/app/results/summary.md`.

## Final Checklist

Run this verification before finishing.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in   "$RESULTS_DIR/industry_briefing.md"   "$RESULTS_DIR/source_findings.json"   "$RESULTS_DIR/gtm_opportunities.md"   "$RESULTS_DIR/summary.md"   "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
python3 - <<'PY'
import json, pathlib
path = pathlib.Path('/app/results/validation_report.json')
data = json.loads(path.read_text())
assert 'stages' in data and 'overall_passed' in data
print('PASS: validation_report.json has required keys')
PY
```

## Common Fixes

| Issue | Fix |
|---|---|
| Client config missing | Ask for or create `clients/<client>/config/industry-scanner.json` before collecting sources |
| Source returns no results | Broaden keywords, increase lookback within the requested bounds, or mark the source as empty with a note |
| Duplicate findings dominate | Re-run normalization using canonical URLs and title similarity |
| GTM ideas are generic | Re-read client context and tie each idea to a specific finding and ICP pain |
| Missing citations | Add source URLs from `source_findings.json` to the briefing and opportunity documents |

## Tips

Prefer evidence-backed synthesis over volume. Use the client's positioning and ICP to decide which signals are strategically important, and keep low-confidence or uncited claims out of the final recommendations.
