---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/linkedin-post-research/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/linkedin-post-research
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: LinkedIn Post Research
  imported_at: '2026-05-03T16:41:42Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: linkedin-post-research
    confidence: high
secrets:
  APIFY_API_TOKEN:
    env: APIFY_API_TOKEN
    description: Apify API token used to run the LinkedIn posts search actor
    required: true
---

# LinkedIn Post Research — Agent Runbook

## Objective

Search LinkedIn posts by one or more keywords using the Apify `apimaestro/linkedin-posts-search-scraper-no-cookies` actor. The runbook returns author details, post text, engagement metrics, dates, hashtags, activity IDs, and direct LinkedIn URLs without requiring LinkedIn cookies or login. Use it to research what people are saying about a topic, discover high-engagement posts, identify thought leaders, or build a warm-lead pipeline from post engagement.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|------|-------------|
| `/app/results/linkedin_posts.json` | Normalized JSON array of unique LinkedIn posts returned by the search |
| `/app/results/linkedin_posts.csv` | CSV export with author, headline, keyword, engagement, date, URL, activity ID, hashtags, and preview fields |
| `/app/results/search_metadata.json` | Search parameters, actor run metadata, result counts, deduplication counts, and cost/status details |
| `/app/results/summary.md` | Executive summary of keywords searched, top posts, notable authors, and issues |
| `/app/results/validation_report.json` | Structured validation report with setup, execution, output, and schema checks |

The task is not complete until every required file exists and is non-empty.

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|-------------------|---------|-------------|
| Results directory | `results_dir` | `/app/results` | Directory where all required output files are written |
| Keywords | `keywords` | required | One or more LinkedIn search keywords |
| Max items | `max_items` | `50` | Maximum posts to request per keyword |
| Sort by | `sort_by` | `relevance` | Sort order accepted by the actor: `relevance` or `date_posted` |
| Timeout seconds | `timeout_seconds` | `120` | Maximum seconds to wait for the Apify actor run |
| Output formats | `output_formats` | `json,csv` | Local exports to produce after normalization |

## Inputs

```yaml
inputs:
  results_dir:
    type: path
    required: false
    default_jetty: /app/results
    default_local: ./results
  keywords:
    type: array
    items: string
    required: true
    min_items: 1
  max_items:
    type: integer
    required: false
    default: 50
  sort_by:
    type: string
    required: false
    default: relevance
    enum: [relevance, date_posted]
  timeout_seconds:
    type: integer
    required: false
    default: 120
```

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `python3` | CLI | Yes | Runs the search and normalization script |
| `requests` | Python package | Yes | Calls the Apify API |
| `APIFY_API_TOKEN` | Secret | Yes | Authenticates requests to Apify |
| Apify actor access | External API | Yes | Uses `apimaestro/linkedin-posts-search-scraper-no-cookies` |

## Step 1: Environment Setup

1. Create the results directory and verify required inputs are present.
2. Verify `APIFY_API_TOKEN` is set without printing its value.
3. Install Python dependencies if needed.

```bash
mkdir -p /app/results
python3 -m pip install requests
python3 - <<'PY'
import os, sys
if not os.environ.get("APIFY_API_TOKEN"):
    sys.exit("ERROR: APIFY_API_TOKEN is not set")
PY
```

If setup fails, write `validation_report.json` with the `setup` stage marked `passed=false`, then stop.

## Step 2: Run LinkedIn Post Searches

For each keyword, submit an Apify actor run with `keyword`, `maxItems`, and `sortBy`. Poll until the run reaches `SUCCEEDED`, `FAILED`, `ABORTED`, or the configured timeout. Retry a failed or timed-out actor run once with the same parameters before marking the keyword failed.

```bash
curl -X POST "https://api.apify.com/v2/acts/apimaestro~linkedin-posts-search-scraper-no-cookies/runs?token=$APIFY_API_TOKEN"   -H "Content-Type: application/json"   -d '{"keyword":"AI agents","maxItems":50,"sortBy":"date_posted"}'
```

## Step 3: Fetch and Normalize Results

Fetch the actor dataset items for each successful run. Normalize each item to this schema: `author`, `author_headline`, `author_profile_url`, `keyword`, `reactions`, `comments`, `shares`, `reactions_by_type`, `date`, `post_preview`, `full_text`, `url`, `activity_id`, `hashtags`, `is_repost`, and `content_type`.

Deduplicate posts across keywords by `activity_id`. When a duplicate appears for multiple keywords, keep the post with the highest reaction count and preserve all matched keywords in metadata.

## Step 4: Sort and Export Outputs

Sort the final post list by total reactions descending when `sort_by=relevance`, or by post date descending when `sort_by=date_posted`. Write JSON and CSV outputs to `/app/results/linkedin_posts.json` and `/app/results/linkedin_posts.csv`.

Also write `/app/results/search_metadata.json` with the input parameters, actor IDs, run statuses, dataset IDs, raw item counts, deduplicated count, failed keywords, retry count, and any cost information returned by Apify.

## Step 5: Summarize Findings

Write `/app/results/summary.md` with:

- Keywords searched and final result count
- Top posts by engagement or newest posts by date, depending on `sort_by`
- Notable authors and repeated themes
- Failed keywords or actor errors
- Direct links to the highest-signal posts

## Step 6: Validate Outputs

Validate that every required output file exists and is non-empty. Parse `linkedin_posts.json` as JSON, verify it is an array, and check that each object has `author`, `keyword`, `url`, and `activity_id` fields when results are present. Parse `search_metadata.json` and verify it includes `keywords`, `runs`, and `deduplicated_count`.

## Step 7: Iterate on Errors (max 3 rounds)

If validation fails or the actor returns zero results for all keywords, run up to max 3 rounds of targeted fixes:

| Issue | Fix |
|-------|-----|
| `APIFY_API_TOKEN` not set | Stop and ask the operator to provide the secret |
| Apify run fails or times out | Retry once, then broaden the keyword if the user permits changes |
| `0` results | Try a broader keyword or reduce restrictive phrasing |
| JSON/CSV schema mismatch | Re-run normalization from the fetched dataset items |
| Missing output file | Regenerate only the missing file, then rerun validation |

After max 3 rounds, write remaining failures into `validation_report.json` and `summary.md`.

## Final Checklist

Run this verification before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in   "$RESULTS_DIR/linkedin_posts.json"   "$RESULTS_DIR/linkedin_posts.csv"   "$RESULTS_DIR/search_metadata.json"   "$RESULTS_DIR/summary.md"   "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
python3 - <<'PY'
import json, pathlib
root = pathlib.Path('/app/results')
posts = json.loads((root / 'linkedin_posts.json').read_text())
meta = json.loads((root / 'search_metadata.json').read_text())
assert isinstance(posts, list), 'linkedin_posts.json must be a JSON array'
assert 'keywords' in meta and 'runs' in meta and 'deduplicated_count' in meta, 'metadata missing required keys'
print('PASS: JSON outputs parse and required keys are present')
PY
```

## Common Fixes

| Error | Fix |
|-------|-----|
| `APIFY_API_TOKEN` not set | Ask user to add it to the runtime environment |
| Apify run fails or times out | Retry once. If it still fails, try a broader keyword. |
| `0` results | Keyword may be too specific. Try broader terms. |
| CSV contains unescaped commas/newlines | Regenerate CSV with Python `csv.DictWriter` |

## Tips

No LinkedIn cookies, login, or session tokens are needed. Keep keywords concise, use repeated `--keyword` inputs for related terms, and sort by `date_posted` when recency matters more than engagement.
