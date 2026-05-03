---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/google-ad-scraper/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/google-ad-scraper
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: google-ad-scraper
  imported_at: '2026-05-03T02:32:39Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: google-ad-scraper
    confidence: high
secrets:
  APIFY_API_TOKEN:
    env: APIFY_API_TOKEN
    required: true
    description: Apify API token used to run the burbn/google-ads-search actor.
---

# Google Ads Scraper — Agent Runbook

## Objective

Scrape competitor Google Ads creatives and campaign metadata for a supplied domain or company name using the Apify `burbn/google-ads-search` actor. The runbook produces a traceable research packet with raw ad data, a concise summary, and validation metadata. Use it for competitive ad research, messaging analysis, and creative format review while preserving the source parameters and execution status.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`. The task is not complete until every file exists and is non-empty.**

| File | Description |
|---|---|
| `/app/results/google_ads_results.json` | Raw structured ad records returned by the Google Ads scraper |
| `/app/results/google_ads_summary.md` | Human-readable summary of advertisers, ad formats, messages, and notable creatives |
| `/app/results/query_metadata.json` | Resolved input parameters, actor configuration, run id, and source domain/company |
| `/app/results/summary.md` | Executive summary of the run, key findings, and output locations |
| `/app/results/validation_report.json` | Structured validation results with stages, counts, and `overall_passed` |

## Parameters

| Parameter | Template Variable | Default | Description |
|---|---|---|---|
| Results directory | `/app/results` | `/app/results` | Output directory where all required files are written |
| Query mode | `{query_mode}` | `domain` | Search mode: `domain` or `company` |
| Domain | `{domain}` | *(none)* | Advertiser domain to search, such as `hubspot.com` |
| Company | `{company}` | *(none)* | Company name to resolve before searching, such as `Nike` |
| Max ads | `{max_ads}` | `30` | Maximum number of ads to retrieve |
| Output format | `{output_format}` | `json` | Output style for scraper execution: `json` or `summary` |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| `python3` | CLI | Yes | Runs the scraper and validation helpers |
| `requests` | Python package | Yes | Calls Apify and any domain-resolution endpoints |
| `APIFY_API_TOKEN` | Secret | Yes | Token for the Apify API |
| Apify actor `burbn/google-ads-search` | External API | Yes | Retrieves Google Ads Transparency data |

## Step 1: Environment Setup

```bash
mkdir -p /app/results /app/results/work
python3 -m pip install requests

if [ -z "$APIFY_API_TOKEN" ]; then
  echo "ERROR: APIFY_API_TOKEN is not set"
  exit 1
fi
```

Validate that `query_mode` is either `domain` or `company`. Require `domain` when `query_mode=domain`, require `company` when `query_mode=company`, and write any setup failure to `/app/results/validation_report.json` before exiting.

## Step 2: Resolve Search Target

Normalize the search parameters into `/app/results/query_metadata.json`. For domain searches, lowercase and trim the supplied domain. For company searches, resolve the company to the best available advertiser domain before invoking the scraper, and record both the original company name and resolved domain.

## Step 3: Run Google Ads Scraper

Invoke the Apify `burbn/google-ads-search` actor with the resolved domain and requested limit. Persist the raw response exactly as structured JSON in `/app/results/google_ads_results.json`.

```bash
python3 skills/google-ad-scraper/scripts/search_google_ads.py \
  --domain "$DOMAIN" \
  --max-ads "${MAX_ADS:-30}" \
  --output json > /app/results/google_ads_results.json
```

If the local skill script is unavailable, call the Apify API directly with `requests` and the `APIFY_API_TOKEN`, preserving the same output schema as closely as possible.

## Step 4: Analyze Results

Read `/app/results/google_ads_results.json` and produce `/app/results/google_ads_summary.md` with the advertiser searched, number of ads returned, dominant formats, recurring calls to action, visible landing page patterns, and notable creative messages. Keep claims tied to fields present in the scraped data.

## Step 5: Validate Outputs

Check that all mandatory files exist and that `google_ads_results.json`, `query_metadata.json`, and `validation_report.json` parse as JSON. Mark the validation as `PASS` when all required files are non-empty and JSON files parse, `PARTIAL` when the scrape completed but returned zero ads, and `FAIL` when setup, scraping, or required file generation failed.

## Step 6: Iterate on Errors (max 3 rounds)

If validation returns `FAIL` or `PARTIAL`, inspect the failing stage, apply the smallest targeted fix, and re-run the affected step. Repeat for max 3 rounds, then write the final status to `/app/results/validation_report.json` and stop if the status is still `FAIL`.

### Common Fixes

| Issue | Fix |
|---|---|
| Missing `APIFY_API_TOKEN` | Stop and report the missing secret in `validation_report.json` |
| Domain returns no ads | Retry with company mode or a canonical root domain |
| Actor timeout | Lower `max_ads` and retry once |
| JSON parse failure | Capture the raw response in `/app/results/work/raw_response.txt` and emit a clear validation failure |

## Step 7: Write Executive Summary

Write `/app/results/summary.md` with the run date, resolved domain or company, number of ads returned, output file list, validation status, and any manual follow-up. Mention if the actor returned no ads or if attribution to a domain was ambiguous.

## Final Checklist

Run this verification script before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/google_ads_results.json" \
  "$RESULTS_DIR/google_ads_summary.md" \
  "$RESULTS_DIR/query_metadata.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

python3 - <<'PY'
import json
from pathlib import Path
for path in ["google_ads_results.json", "query_metadata.json", "validation_report.json"]:
    json.loads((Path("/app/results") / path).read_text())
print("PASS: JSON outputs parse")
PY
```

## Tips

- Start with domain mode when the advertiser website is known; it is the most direct path through the source skill.
- Keep `max_ads` modest for first runs so actor failures are easier to distinguish from sparse ad inventory.
- Treat zero returned ads as a research result, but mark validation `PARTIAL` and include the searched domain in the summary.
