---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
model_provider: anthropic
snapshot: python312-uv
secrets:
  POSTHOG_PERSONAL_API_KEY:
    env: POSTHOG_PERSONAL_API_KEY
    description: "PostHog personal API key with read access to the Jetty project. Create at <posthog-host>/settings/user-api-keys with scopes: query:read, project:read, insight:read."
    required: true
  POSTHOG_PROJECT_ID:
    env: POSTHOG_PROJECT_ID
    description: "Numeric PostHog project ID for the Jetty project (find at <posthog-host>/settings/project)."
    required: true
---

# PostHog Usage Summary — Jetty Corp Agent Runbook

## Objective

Pull product analytics from PostHog for the Jetty project and produce a concise usage summary covering two time windows: the last 24 hours and the last 7 days. The report quantifies overall activity (events, sessions, active users), highlights the most-used events and pages/features, surfaces noteworthy week-over-day deltas, and identifies any anomalies (spikes, dips, or zero-traffic features). The summary is consumed by the Jetty team to monitor product health and prioritize follow-ups.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `{{results_dir}}`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `{{results_dir}}/usage_summary.md` | Human-readable usage summary with last-24h and last-7d sections, key metrics, top events, top pages, and notable deltas |
| `{{results_dir}}/metrics.json` | Machine-readable metrics for both windows (event counts, unique users, top-N events, top-N pages, session counts) |
| `{{results_dir}}/summary.md` | Executive summary with run metadata, headline numbers, and recommendations |
| `{{results_dir}}/validation_report.json` | Structured validation results with stages, results, and overall_passed |

If you finish your analysis but have not written all files, go back and write them before stopping.

---

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|------------------|---------|-------------|
| Results directory | `{{results_dir}}` | `/app/results` | Output directory for all results |
| PostHog host | `{{posthog_host}}` | `https://us.i.posthog.com` | PostHog API base URL (use `https://eu.i.posthog.com` for EU cloud, or self-hosted URL) |
| Top-N limit | `{{top_n}}` | `10` | How many top events/pages to report per window |
| Timezone | `{{timezone}}` | `UTC` | Timezone for window boundaries and report timestamps |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| PostHog Query API | External API | Yes | Used to run HogQL queries against events (`POST /api/projects/{id}/query`) |
| `POSTHOG_PERSONAL_API_KEY` | Credential | Yes | Personal API key with `query:read` + `project:read` scopes |
| `POSTHOG_PROJECT_ID` | Credential | Yes | Numeric project ID for the Jetty project |
| `httpx` | Python package | Yes | HTTP client for PostHog API calls |
| `python-dateutil` | Python package | Yes | Robust timezone-aware date math for window boundaries |

---

## Step 1: Environment Setup

```bash
# Install dependencies
pip install httpx python-dateutil

# Create output directory
mkdir -p {{results_dir}}

# Verify required secrets are available
for var in POSTHOG_PERSONAL_API_KEY POSTHOG_PROJECT_ID; do
  if [ -z "${!var}" ]; then
    echo "ERROR: $var is not set. Add it to the jetty-corp collection env on Jetty (or export locally)."
    exit 1
  fi
done

echo "Environment ready. Project: $POSTHOG_PROJECT_ID  Host: {{posthog_host}}"
```

Verify credentials and the host URL respond before running real queries:

```bash
curl -sS -o /dev/null -w "HTTP %{http_code}\n" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  "{{posthog_host}}/api/projects/$POSTHOG_PROJECT_ID/"
# Expect: HTTP 200
```

If you get 401, the key is missing or lacks scopes. If 404, the project ID is wrong or the host is wrong (US vs EU cloud).

---

## Step 2: Collect Metrics from PostHog

Use the PostHog Query API with HogQL to compute metrics for both windows in one pass per metric. Run all queries against the project endpoint:

```
POST {{posthog_host}}/api/projects/{POSTHOG_PROJECT_ID}/query/
Authorization: Bearer {POSTHOG_PERSONAL_API_KEY}
Content-Type: application/json

{
  "query": {
    "kind": "HogQLQuery",
    "query": "<HogQL SQL>"
  }
}
```

Run these HogQL queries (run each once per window — `last_24h` and `last_7d` — by swapping the `timestamp >= now() - interval ...` clause):

### 2a: Headline counters

```sql
SELECT
  count() AS event_count,
  count(DISTINCT person_id) AS unique_users,
  count(DISTINCT $session_id) AS sessions
FROM events
WHERE timestamp >= now() - interval 1 day
```

Repeat with `interval 7 day` for the weekly window.

### 2b: Top events by volume

```sql
SELECT event, count() AS n
FROM events
WHERE timestamp >= now() - interval 1 day
GROUP BY event
ORDER BY n DESC
LIMIT {{top_n}}
```

### 2c: Top pages (pageviews)

```sql
SELECT properties.$pathname AS path, count() AS n
FROM events
WHERE event = '$pageview'
  AND timestamp >= now() - interval 1 day
GROUP BY path
ORDER BY n DESC
LIMIT {{top_n}}
```

### 2d: New vs returning users (1d only)

```sql
SELECT
  countIf(person.created_at >= now() - interval 1 day) AS new_users,
  countIf(person.created_at < now() - interval 1 day) AS returning_users
FROM (
  SELECT DISTINCT person_id, any(person.created_at) AS created_at
  FROM events
  WHERE timestamp >= now() - interval 1 day
  GROUP BY person_id
)
```

### 2e: Hourly event volume (1d) and daily event volume (7d)

```sql
-- 1d: hourly buckets
SELECT toStartOfHour(timestamp) AS bucket, count() AS n
FROM events
WHERE timestamp >= now() - interval 1 day
GROUP BY bucket ORDER BY bucket

-- 7d: daily buckets
SELECT toStartOfDay(timestamp) AS bucket, count() AS n
FROM events
WHERE timestamp >= now() - interval 7 day
GROUP BY bucket ORDER BY bucket
```

### Expected response shape

```json
{
  "results": [["row1_col1", "row1_col2"], ["row2_col1", "row2_col2"]],
  "columns": ["col1", "col2"],
  "types": ["...", "..."]
}
```

### Record

Store every query result keyed by `(metric_name, window)` for use in Step 3. Persist raw rows so the validation step can re-check them.

---

## Step 3: Build the Report

Compose `{{results_dir}}/usage_summary.md` using this structure:

```markdown
# Jetty PostHog Usage Summary

_Generated: {ISO timestamp}  ·  Project: {POSTHOG_PROJECT_ID}  ·  Host: {posthog_host}_

## Last 24 hours

- **Events**: {event_count} ({delta vs prior 24h, if computed})
- **Unique users**: {unique_users}
- **Sessions**: {sessions}
- **New users**: {new_users}  ·  **Returning**: {returning_users}

### Top events
| Event | Count |
|---|---|
| ... | ... |

### Top pages
| Path | Pageviews |
|---|---|
| ... | ... |

### Hourly volume
{compact sparkline or list of hour: count}

## Last 7 days

- **Events**: {event_count}
- **Unique users**: {unique_users}
- **Sessions**: {sessions}

### Top events
| Event | Count |
|---|---|
| ... | ... |

### Top pages
| Path | Pageviews |
|---|---|
| ... | ... |

### Daily volume
{day: count list}

## Notable observations

- {1-3 bullets: spikes, dips, new top events compared to weekly baseline, zero-traffic critical events if any}
```

Also write `{{results_dir}}/metrics.json` with both windows' raw numbers:

```json
{
  "generated_at": "...",
  "windows": {
    "last_24h": {
      "event_count": 0,
      "unique_users": 0,
      "sessions": 0,
      "new_users": 0,
      "returning_users": 0,
      "top_events": [{"event": "...", "n": 0}],
      "top_pages": [{"path": "...", "n": 0}],
      "hourly": [{"bucket": "ISO", "n": 0}]
    },
    "last_7d": {
      "event_count": 0,
      "unique_users": 0,
      "sessions": 0,
      "top_events": [...],
      "top_pages": [...],
      "daily": [...]
    }
  }
}
```

---

## Step 4: Evaluate Outputs

Score each window's data and the report against these criteria:

| Status | Criteria |
|--------|----------|
| `PASS` | API calls returned 200 for every query; both windows have non-empty `event_count`; top_events and top_pages each have at least 1 row OR the project genuinely has no traffic (flag this); `usage_summary.md` includes both "Last 24 hours" and "Last 7 days" sections with all metric subsections populated; numbers in `usage_summary.md` match `metrics.json` exactly |
| `PARTIAL` | At least one window populated but the other is missing/empty due to permission/scope issues, OR one of the sub-queries (e.g., hourly volume) failed but headline metrics succeeded |
| `FAIL` | Authentication failed (401/403), project not found (404), all queries returned empty when traffic clearly should exist, or required output files are missing/empty |

Run a programmatic check before writing the summary:

```python
# Pseudocode — adapt to your script
assert metrics["windows"]["last_24h"]["event_count"] is not None
assert metrics["windows"]["last_7d"]["event_count"] >= metrics["windows"]["last_24h"]["event_count"], \
    "7d total should be >= 1d total"
assert len(metrics["windows"]["last_7d"]["top_events"]) > 0 or metrics["windows"]["last_7d"]["event_count"] == 0
```

---

## Step 5: Iterate on Errors (max 3 rounds)

If evaluation returns `FAIL` or `PARTIAL`:

1. Read the exact error (HTTP status, body, or failed assertion)
2. Apply the targeted fix from the Common Fixes table
3. Re-run only the failed query/step
4. Re-evaluate
5. Repeat up to 3 times. After 3 rounds, keep the best result and document remaining gaps in the summary's Limitations section.

### Common Fixes

| Issue | Fix |
|-------|-----|
| `401 Unauthorized` | Personal API key is missing/invalid or lacks `query:read` scope. Recreate the key at `{{posthog_host}}/settings/user-api-keys` with scopes `query:read` + `project:read` and update the jetty-corp collection env. |
| `404 Not Found` on the project endpoint | Wrong `POSTHOG_PROJECT_ID` or wrong host (US vs EU). Confirm the numeric ID at `{{posthog_host}}/settings/project` and switch `{{posthog_host}}` to `https://eu.i.posthog.com` if the project lives in EU cloud. |
| `400 Bad Request` from HogQL query | Quoting issue or unknown column. Test the query in PostHog's SQL editor first. Use double quotes for identifiers if needed and confirm the `events` table is available (older PostHog versions used different table names). |
| `7d event_count` smaller than `1d event_count` | Window math is wrong — re-derive boundaries using `dateutil` in the report's timezone instead of mixing `now()` and local time. |
| Top pages list is empty but events show pageviews | The `$pathname` property is missing on some pageviews. Fall back to `properties.$current_url` and strip the host. |
| Query times out / 504 | Reduce window or push aggregation into HogQL (don't fetch raw events). For 7d top events, use a `SAMPLE` clause or query a smaller subset of properties. |
| `429 Too Many Requests` | Add a 1-2s sleep between queries; PostHog rate-limits the query API on free tiers. |

---

## Step 6: Write Executive Summary

Write `{{results_dir}}/summary.md`:

```markdown
# Jetty PostHog Usage Summary — Run Results

## Overview
- **Run date**: {ISO timestamp}
- **Project**: {POSTHOG_PROJECT_ID}
- **Host**: {posthog_host}
- **Windows**: last 24h, last 7d

## Headline Numbers
| Metric | Last 24h | Last 7d |
|---|---|---|
| Events | ... | ... |
| Unique users | ... | ... |
| Sessions | ... | ... |

## Results Summary
| Status | Count |
|---|---|
| PASS | ... |
| PARTIAL | ... |
| FAIL | ... |

## Notable Observations
- {1-3 bullets — spikes, dips, surprising top events}

## Recommendations
- {What to investigate or follow up on}

## Limitations
- {Any queries that failed after retries}
- {Properties or events that weren't available}
```

---

## Step 7: Write Validation Report

Write `{{results_dir}}/validation_report.json`:

```json
{
  "version": "1.0.0",
  "run_date": "2026-01-01T00:00:00Z",
  "parameters": {
    "posthog_host": "{{posthog_host}}",
    "top_n": "{{top_n}}",
    "timezone": "{{timezone}}"
  },
  "stages": [
    { "name": "setup", "passed": true, "message": "Secrets present, host reachable" },
    { "name": "metrics_1d", "passed": true, "message": "All 1d queries succeeded" },
    { "name": "metrics_7d", "passed": true, "message": "All 7d queries succeeded" },
    { "name": "report_generation", "passed": true, "message": "Markdown + JSON written" },
    { "name": "consistency_checks", "passed": true, "message": "1d <= 7d, no null headline metrics" }
  ],
  "results": {
    "pass": 0,
    "partial": 0,
    "fail": 0
  },
  "overall_passed": true,
  "output_files": [
    "{{results_dir}}/usage_summary.md",
    "{{results_dir}}/metrics.json",
    "{{results_dir}}/summary.md",
    "{{results_dir}}/validation_report.json"
  ]
}
```

---

## Final Checklist (Step 8 — MANDATORY, do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="{{results_dir}}"
for f in "$RESULTS_DIR/usage_summary.md" "$RESULTS_DIR/metrics.json" "$RESULTS_DIR/summary.md" "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# Quick structural sanity check on metrics.json
python3 - <<'PY'
import json, sys, os
p = os.path.join(os.environ.get("RESULTS_DIR", "{{results_dir}}"), "metrics.json")
m = json.load(open(p))
w = m["windows"]
assert "last_24h" in w and "last_7d" in w, "missing windows"
assert w["last_7d"]["event_count"] >= w["last_24h"]["event_count"], "7d < 1d (impossible)"
print("PASS: metrics.json structure ok")
PY
```

### Checklist

- [ ] `usage_summary.md` contains both `## Last 24 hours` and `## Last 7 days` sections, each with headline metrics, top events table, and top pages table
- [ ] `metrics.json` has `windows.last_24h` and `windows.last_7d` with `event_count`, `unique_users`, `sessions`, `top_events`, `top_pages`
- [ ] `summary.md` exists and follows the Step 6 template
- [ ] `validation_report.json` has `stages`, `results`, `overall_passed`, and `output_files`
- [ ] Verification script printed PASS for all files and the structural check
- [ ] Numbers in `usage_summary.md` match `metrics.json` exactly

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- PostHog's free/scale tier rate-limits the query API. Sleep 1-2 seconds between queries and batch related metrics into a single HogQL query when possible (Step 2a is one query, not three).
- HogQL is ClickHouse SQL — `interval 1 day` and `toStartOfHour()` work; standard PostgreSQL syntax does not. Test queries in the PostHog UI's SQL editor (`{{posthog_host}}/sql`) before scripting.
- US vs EU cloud lives at different hosts (`us.i.posthog.com` vs `eu.i.posthog.com`). A 404 on `/api/projects/{id}/` usually means wrong region, not wrong ID.
- The `$pageview` event and its `$pathname` / `$current_url` properties are autocaptured by the PostHog JS snippet — if pages look empty, autocapture might be disabled and you'll need to fall back to manually-instrumented events.
- Personal API keys can be scoped per-project; if you get 403 on a specific project, the key may only have access to others. Re-create with the correct project selected.
- "Yesterday" and "last 24h" are different — `now() - interval 1 day` is a rolling 24h window, not a calendar day. Be explicit in the summary text so the reader isn't confused.
