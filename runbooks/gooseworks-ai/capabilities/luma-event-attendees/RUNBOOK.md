---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/luma-event-attendees/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/luma-event-attendees
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: luma-event-attendees
  imported_at: '2026-05-03T02:54:55Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: luma-event-attendees
    confidence: high
secrets:
  APIFY_API_TOKEN:
    env: APIFY_API_TOKEN
    description: Apify API token required only when running Apify search mode for
      full Luma guest profiles.
    required: false
---

# luma-event-attendees — Agent Runbook

## Objective
Convert the `luma-event-attendees` skill into a repeatable workflow for finding Luma event people data. The runbook supports a free direct-scrape mode for event metadata and hosts, and an Apify-backed search mode for fuller guest profiles with social links and bios. It normalizes all discovered people into stable JSON and CSV outputs for outreach prospecting, while preserving raw evidence and validation metadata.

The source was discovered through the Gooseworks skills directory and imported from the pinned upstream GitHub `SKILL.md`, not from the rendered directory mirror.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/people.json` | Normalized list of speakers, hosts, featured guests, and other people discovered from the selected Luma source |
| `/app/results/people.csv` | CSV export of the normalized people records for outreach workflows |
| `/app/results/events.json` | Event metadata and event URLs processed during the run |
| `/app/results/raw_response.json` | Raw direct-scrape or Apify response payloads retained for traceability |
| `/app/results/summary.md` | Executive summary of mode, inputs, counts, output paths, and notable limitations |
| `/app/results/validation_report.json` | Structured validation report with stages, result counts, and `overall_passed` |

The task is not complete until every file above exists and is non-empty. For empty result sets, write valid empty JSON or CSV with headers and explain the reason in `summary.md`.

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `results_dir` | `/app/results` | Directory where all required output files must be written |
| `mode` | `direct` | `direct` scrapes specific Luma URLs for metadata and hosts; `apify` searches Luma through the Apify actor for fuller profiles |
| `luma_urls` | empty | One or more `https://lu.ma/...` event URLs for direct mode |
| `search_query` | empty | Search phrase such as `AI San Francisco` for Apify mode |
| `output_format` | `json,csv` | Export formats to produce; this runbook always writes both required JSON and CSV outputs |

## Dependencies

| Dependency | Required | Notes |
|---|---|---|
| `python3` | Yes | Used for fetching, parsing, normalization, and validation |
| `requests` | Yes | HTTP client for Luma pages and Apify API calls |
| `beautifulsoup4` | Yes for direct mode | Parses embedded event metadata and host information from Luma HTML |
| `APIFY_API_TOKEN` | Only for `apify` mode | Required to call the `lexis-solutions/lu-ma-scraper` actor |
| Apify actor `lexis-solutions/lu-ma-scraper` | Only for `apify` mode | Paid actor referenced by the source skill; verify subscription or trial before use |

## Step 1: Environment Setup

```bash
python3 -m pip install requests beautifulsoup4
mkdir -p /app/results /app/results/work
```

Validate the selected mode before making network calls. If `mode=apify`, require `APIFY_API_TOKEN`; if `mode=direct`, require at least one Luma event URL.

## Step 2: Resolve Inputs

For direct mode, normalize each provided Luma URL by trimming whitespace and requiring an `https://lu.ma/` prefix. For Apify mode, trim the search query and preserve it in `events.json` so the run is auditable.

If both `luma_urls` and `search_query` are supplied, prefer the mode value. Do not silently combine direct and Apify runs unless the operator explicitly asks for both.

## Step 3: Direct Scrape Luma Events

Fetch each Luma event page with a normal browser-like user agent. Extract event title, start time, location, canonical URL, and host cards from embedded JSON or HTML. Guest profiles may be unavailable in direct mode unless they are publicly embedded in the page.

Example source command preserved from the skill:

```bash
python3 scripts/scrape_event.py https://lu.ma/abc123
```

## Step 4: Apify Search Mode

When `mode=apify`, call the Apify actor `lexis-solutions/lu-ma-scraper` with the provided search query and poll until the actor run completes. Capture the full actor dataset payload into `raw_response.json` before normalizing records.

Example source command preserved from the skill:

```bash
python3 scripts/scrape_event.py --search "AI San Francisco"
```

The source notes a flat Apify subscription cost for the actor. Treat pricing and availability as external conditions that should be verified before a production run.

## Step 5: Normalize People Records

Produce one record per person with these fields when available: `name`, `role`, `event_title`, `event_url`, `bio`, `linkedin`, `twitter`, `instagram`, `website`, `source_mode`, and `source_evidence`. Deduplicate by normalized name plus event URL, preferring records with more profile links and longer bios.

Write event-level metadata to `/app/results/events.json` and raw payloads to `/app/results/raw_response.json`.

## Step 6: Export Results

Write `/app/results/people.json` as an array of normalized objects. Write `/app/results/people.csv` with stable headers even when no people are found.

```python
import csv, json, pathlib
results = pathlib.Path('/app/results')
people = json.loads((results / 'people.json').read_text())
fields = ['name', 'role', 'event_title', 'event_url', 'bio', 'linkedin', 'twitter', 'instagram', 'website', 'source_mode']
with (results / 'people.csv').open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for row in people:
        writer.writerow({k: row.get(k, '') for k in fields})
```

## Step 7: Iterate on Errors (max 3 rounds)

If a fetch, parse, export, or validation step fails, inspect the specific stage message in `validation_report.json`, apply the smallest targeted fix, and rerun the failed stage. Stop after max 3 rounds and write the remaining issue to `summary.md` with `overall_passed=false` if required files still cannot be produced.

### Common Fixes

| Issue | Fix |
|---|---|
| Direct scrape returns no hosts | Check whether Luma changed the embedded JSON shape; save the HTML snippet that was inspected in `raw_response.json` |
| Apify run is unauthorized | Confirm `APIFY_API_TOKEN` is set and that the actor is rented or available on the account |
| CSV columns shift between rows | Use the fixed header list in Step 6 and write missing values as empty strings |
| Duplicate people appear | Deduplicate by lowercased `name` plus canonical `event_url` and keep the richer record |
| Required output file is empty | Write a valid empty JSON array/object or CSV header and explain the empty result in `summary.md` |

## Step 8: Write Summary and Validation

Write `/app/results/summary.md` with the selected mode, input URLs or search query, event count, people count, output paths, and limitations such as missing guest visibility in direct mode.

Write `/app/results/validation_report.json` with setup, input, fetch, normalization, export, and final output stages. Set `overall_passed=false` if any required file is missing or invalid.

## Final Checklist

Run this verification before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/people.json" \
  "$RESULTS_DIR/people.csv" \
  "$RESULTS_DIR/events.json" \
  "$RESULTS_DIR/raw_response.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
python3 - <<'PY_VERIFY'
import csv, json, pathlib
root = pathlib.Path('/app/results')
json.loads((root / 'people.json').read_text())
json.loads((root / 'events.json').read_text())
json.loads((root / 'raw_response.json').read_text())
with (root / 'people.csv').open(newline='') as f:
    headers = next(csv.reader(f))
required = {'name', 'event_url', 'source_mode'}
missing = required.difference(headers)
if missing:
    raise SystemExit(f'Missing CSV headers: {sorted(missing)}')
report = json.loads((root / 'validation_report.json').read_text())
if not isinstance(report.get('overall_passed'), bool):
    raise SystemExit('validation_report.json must include boolean overall_passed')
print('PASS: structured output files parse correctly')
PY_VERIFY
```

Checklist:

- [ ] `people.json`, `events.json`, and `raw_response.json` parse as JSON
- [ ] `people.csv` has stable outreach columns
- [ ] `summary.md` describes the selected mode and any missing-data limitations
- [ ] `validation_report.json` includes stages, result counts, and `overall_passed`
- [ ] Verification script printed PASS for every required output file

## Tips

Use direct mode when only host and event metadata are needed. Use Apify mode when outreach requires richer guest profiles with LinkedIn, Twitter, Instagram, website, or biography fields.
