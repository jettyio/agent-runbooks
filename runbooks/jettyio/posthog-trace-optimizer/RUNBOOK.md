---
version: "1.0.0"
evaluation: rubric
agent: claude-code
model: anthropic/claude-sonnet-4.6
model_provider: openrouter
snapshot: python312-uv
# The headline deliverable — the cost-optimization report.
primary_outputs:
  - recommendations.md
origin:
  url: "https://github.com/jettyio/trace-experimentation-agent/tree/main/tbench2/datasets/traces/langfuse-optimizer"
  source_host: "github.com"
  source_title: "Langfuse Optimizer — Terminal Bench 2.0 task (PostHog sink variant)"
  imported_at: "2026-06-24T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: jettyio
    skill_name: posthog-trace-optimizer
    author: "Jetty trace-experimentation-agent"
    confidence: high
secrets:
  POSTHOG_API_KEY:
    env: POSTHOG_API_KEY
    description: "PostHog personal API key (phx_…) with query:read scope. Settings → Personal API keys."
    required: true
  POSTHOG_PROJECT_ID:
    env: POSTHOG_PROJECT_ID
    description: "PostHog project ID (the numeric ID in your project URL / Settings)."
    required: true
  POSTHOG_HOST:
    env: POSTHOG_HOST
    description: "PostHog host, e.g. https://us.posthog.com (US), https://eu.posthog.com (EU), or your self-hosted URL."
    required: true
---

# PostHog Trace Optimizer — LLM Cost & Quality Report — Agent Runbook

> **EXECUTE THIS RUNBOOK NOW.** Connect to the live PostHog project with the provided
> credentials, query the LLM-analytics events, analyze them, and write every deliverable to
> `{{results_dir}}`. This is a task to perform against a live observability backend, not a
> document to summarize. Your first action is a tool call (Step 1). The credentials are already
> provided as environment variables — never pause to ask the user for them.

> **Same analysis, different sink.** This is the PostHog counterpart of `jettyio/langfuse-trace-optimizer`.
> The methodology is identical; only the data source changes — PostHog **LLM analytics** emits
> `$ai_generation` events, queried with **HogQL** via the query API, instead of Langfuse's
> Metrics API.

## Inputs (already provided)

- **PostHog credentials:** `POSTHOG_API_KEY`, `POSTHOG_PROJECT_ID`, `POSTHOG_HOST` — injected as
  environment variables. They point at a real project capturing `$ai_generation` events.
- **Analysis window:** {{window_days}} — how many days back to analyze (default 30).
- **Prior analysis history (optional):** {{analysis_history}} — a timeline of past
  recommendations + merged/closed PRs. If present, factor it in (see Step 9): do not
  re-recommend already-shipped fixes, and check whether prior recommendations had their
  predicted impact.

## Objective

Analyze a project's PostHog **LLM-analytics** data the way a cost-and-quality engineer would, and
hand back a **`recommendations.md`** report an engineering team can act on this week. The agent
queries PostHog (HogQL over `$ai_generation` events) for aggregate cost/latency and individual
traces, finds the cost drivers and failure modes **quantitatively**, then inspects sampled traces
**qualitatively** for the abnormalities aggregates miss (prompt stuffing, retry storms, model
misuse, truncation). Every finding is backed by **actual trace IDs and input/output excerpts**,
and every recommendation ships with a code example and a **measurement plan** (metric, baseline,
target, validation window) so the team can prove the fix worked in PostHog afterward.

The deliverable is a decision-ready report, not a data dump: a tight executive summary, ranked
recommendations with evidence and code, and an implementation roadmap with effort/impact/timeline.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following to `{{results_dir}}`. The task is NOT complete until every
file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `{{results_dir}}/recommendations.md` | The headline report: executive summary, cost analysis tables, qualitative findings, ≥3 ranked recommendations (each with evidence trace IDs, WHY, code example, measurement plan), and an implementation roadmap. |
| `{{results_dir}}/data/metrics_by_span.csv` | Per-operation aggregates (`$ai_span_name`: count, total cost, total tokens, p95 latency) for the analysis window. |
| `{{results_dir}}/data/metrics_by_model.csv` | Per-model aggregates (`$ai_model`: count, cost, tokens, error rate). |
| `{{results_dir}}/data/cost_variance.json` | Per-expensive-operation cost distribution (min/mean/median/max/std/p95) and flagged outlier trace IDs. |
| `{{results_dir}}/data/qualitative_samples.json` | The sampled traces inspected manually, with trace IDs, input/output excerpts, and the abnormality tagged on each. |
| `{{results_dir}}/data/model_pricing.json` | Current model pricing fetched from LiteLLM (provider-filtered) — used to cross-check PostHog's computed costs. |
| `{{results_dir}}/summary.md` | One-screen executive summary: window, generations analyzed, total cost, top 3 findings, total projected monthly savings. |
| `{{results_dir}}/validation_report.json` | Stage-by-stage self-validation with `overall_passed`. See Step 11. |

Figures (optional) go in `{{results_dir}}/figures/`. If you finish but have not written every
mandatory file, go back and write it.

---

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|------------------|---------|-------------|
| Results directory | `{{results_dir}}` | `/app/results` | Output directory |
| Analysis window (days) | `{{window_days}}` | `30` | How far back to query events. The run also computes 3d/7d sub-windows for trend. |
| Top-N expensive operations | `{{top_n}}` | `5` | How many of the most expensive `$ai_span_name`s to deep-dive in Steps 4–6. |
| Qualitative sample size | `{{sample_size}}` | `15` | How many individual traces to pull for manual inspection in Step 7. |
| Min recommendations | `{{min_recommendations}}` | `3` | Floor on actionable recommendations in the report. |
| Analysis history | `{{analysis_history}}` | *(optional)* | Prior recommendations + PR timeline to avoid re-recommending shipped fixes. |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `POSTHOG_API_KEY` / `POSTHOG_PROJECT_ID` / `POSTHOG_HOST` | Secret | Yes | Auth + endpoint for the live PostHog project. |
| `requests` (pip) | Runtime | Yes | Calls the PostHog query API (HogQL). |
| `litellm` (pip) | Runtime | Yes | Live model pricing reference (cross-checks PostHog's computed cost). |
| `pandas` (pip) | Runtime | Yes | Aggregation + CSV output. |
| `matplotlib` (pip) | Runtime | No | Optional cost/latency figures. |

---

## Step 1: Environment Setup & Connectivity Check

Install deps, write the creds to `{{results_dir}}/.env` for reproducibility, and **prove the
connection before doing anything else**. If you cannot connect, STOP — this is a live-data task
and every downstream step depends on it.

```bash
mkdir -p "{{results_dir}}/data" "{{results_dir}}/figures"
pip install -q requests litellm pandas matplotlib tabulate

cat > "{{results_dir}}/.env" <<EOF
POSTHOG_API_KEY=${POSTHOG_API_KEY}
POSTHOG_PROJECT_ID=${POSTHOG_PROJECT_ID}
POSTHOG_HOST=${POSTHOG_HOST}
EOF

[ -n "$POSTHOG_API_KEY" ] && [ -n "$POSTHOG_PROJECT_ID" ] && [ -n "$POSTHOG_HOST" ] \
  || { echo "ERROR: missing PostHog credentials"; exit 1; }
echo "PostHog host: $POSTHOG_HOST  project: $POSTHOG_PROJECT_ID"
```

```python
# Connectivity gate — STOP IMMEDIATELY IF THIS FAILS.
import os, requests
HOST = os.environ["POSTHOG_HOST"].rstrip("/")
PID  = os.environ["POSTHOG_PROJECT_ID"]
KEY  = os.environ["POSTHOG_API_KEY"]
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

def hogql(sql: str):
    """Run a HogQL query against the project and return (columns, rows)."""
    r = requests.post(f"{HOST}/api/projects/{PID}/query/",
                      headers=HEADERS, json={"query": {"kind": "HogQLQuery", "query": sql}},
                      timeout=120)
    r.raise_for_status()
    j = r.json()
    return j.get("columns", []), j.get("results", [])

# Auth + sanity: are there any $ai_generation events at all?
cols, rows = hogql(
    "SELECT count() FROM events WHERE event = '$ai_generation' "
    f"AND timestamp >= now() - INTERVAL {int('{{window_days}}')} DAY")
n = rows[0][0] if rows else 0
print(f"PostHog connection OK — {n} $ai_generation events in window")
assert n and n > 0, "No $ai_generation events found — is LLM analytics instrumented on this project?"
```

If the request 401/403s, or there are **zero** `$ai_generation` events, do not continue: report
the connection/instrumentation failure in `summary.md` and exit. Do not fabricate analysis against
data you could not read.

> **PostHog `$ai_generation` property cheat-sheet** (used throughout):
> `$ai_model`, `$ai_provider`, `$ai_input_tokens`, `$ai_output_tokens`, `$ai_total_cost_usd`,
> `$ai_latency` (seconds), `$ai_trace_id`, `$ai_span_name`, `$ai_input` (prompt JSON),
> `$ai_output_choices` (completion JSON), `$ai_is_error`, `$ai_http_status`.

---

## Step 2: Fetch Live Model Pricing (provider-filtered, cross-check)

PostHog computes `$ai_total_cost_usd` itself, but its map can lag new models (cost shows null).
Fetch current pricing from LiteLLM, filtered by the `litellm_provider` field — **not** by matching
model-name substrings — so new families (`gpt-4.1`, `claude-4`, `gemini-2`) are picked up
automatically. Use it to backfill any generation PostHog priced at null. Write
`{{results_dir}}/data/model_pricing.json`.

```python
import litellm, json
TARGET_PROVIDERS = {"openai","anthropic","vertex_ai","gemini","azure","azure_ai",
                    "deepseek","mistral","bedrock","cohere","groq"}

def fetch_model_costs() -> dict:
    out = {}
    for name, info in litellm.model_cost.items():
        if (info.get("litellm_provider") or "").lower() not in TARGET_PROVIDERS:
            continue
        ic = info.get("input_cost_per_token") or 0
        oc = info.get("output_cost_per_token") or 0
        if ic == 0 and oc == 0:
            continue
        mode = (info.get("mode") or "").lower()
        if mode and mode not in ("chat", "completion"):
            continue
        out[name] = {"input_cost_per_token": ic, "output_cost_per_token": oc,
                     "litellm_provider": info.get("litellm_provider"), "mode": info.get("mode")}
    return out

costs = fetch_model_costs()
json.dump(costs, open("{{results_dir}}/data/model_pricing.json", "w"), indent=2)
print(f"Pricing for {len(costs)} models written.")
```

Keep a `get_model_cost(name)` helper (exact → case-insensitive → strip `provider/` prefix →
shortest substring match) so a PostHog model string like `gpt-4o-2024-08-06` still resolves.

---

## Step 3: Aggregate Metrics — Cost & Volume by Operation and Model

Use **HogQL** for cheap aggregates over the window. PostHog's `$ai_span_name` is the analog of
Langfuse's trace name (the logical operation); `$ai_trace_id` groups generations into one trace.
Write `metrics_by_span.csv` and `metrics_by_model.csv`.

```python
import pandas as pd
W = int("{{window_days}}")

# Per operation: volume, cost, tokens, p95 latency, error rate
cols, rows = hogql(f"""
SELECT coalesce(nullIf(properties.$ai_span_name, ''), 'unnamed') AS operation,
       count() AS calls,
       round(sum(toFloat(properties.$ai_total_cost_usd)), 6) AS total_cost_usd,
       sum(toInt(properties.$ai_input_tokens) + toInt(properties.$ai_output_tokens)) AS total_tokens,
       round(quantile(0.95)(toFloat(properties.$ai_latency)), 3) AS p95_latency_s,
       round(avg(if(properties.$ai_is_error, 1, 0)), 4) AS error_rate
FROM events
WHERE event = '$ai_generation' AND timestamp >= now() - INTERVAL {W} DAY
GROUP BY operation
ORDER BY total_cost_usd DESC
""")
by_span = pd.DataFrame(rows, columns=cols)
by_span["avg_cost_per_call"] = by_span["total_cost_usd"] / by_span["calls"].clip(lower=1)
by_span.to_csv("{{results_dir}}/data/metrics_by_span.csv", index=False)

# Per model: how spend splits across models
cols, rows = hogql(f"""
SELECT coalesce(nullIf(properties.$ai_model, ''), 'unknown') AS model,
       count() AS calls,
       round(sum(toFloat(properties.$ai_total_cost_usd)), 6) AS total_cost_usd,
       sum(toInt(properties.$ai_input_tokens) + toInt(properties.$ai_output_tokens)) AS total_tokens,
       round(avg(if(properties.$ai_is_error, 1, 0)), 4) AS error_rate
FROM events
WHERE event = '$ai_generation' AND timestamp >= now() - INTERVAL {W} DAY
GROUP BY model
ORDER BY total_cost_usd DESC
""")
by_model = pd.DataFrame(rows, columns=cols)
by_model.to_csv("{{results_dir}}/data/metrics_by_model.csv", index=False)

print("operations:", len(by_span), "| models:", len(by_model))
print(by_span.head(10).to_string(index=False))
```

**avg cost per call** surfaces cheap high-volume operations vs expensive low-volume ones — they
need different fixes. Re-run the by-operation query for 3-day and 7-day windows too, to spot a
cost trend (a model swap, a prompt that grew).

---

## Step 4: Cost-Variance Deep Dive on the Top-N Expensive Operations

For the `{{top_n}}` most expensive operations, pull per-**trace** cost (sum the generations within
each `$ai_trace_id`) and compute the distribution. High variance is where the money leaks. Write
`data/cost_variance.json`.

```python
import json, statistics as st
TOP_N = int("{{top_n}}")
expensive_ops = by_span.head(TOP_N)["operation"].tolist()

variance = {}
for op in expensive_ops:
    safe = op.replace("'", "''")
    cols, rows = hogql(f"""
    SELECT properties.$ai_trace_id AS trace_id,
           round(sum(toFloat(properties.$ai_total_cost_usd)), 6) AS trace_cost
    FROM events
    WHERE event = '$ai_generation'
      AND coalesce(nullIf(properties.$ai_span_name, ''), 'unnamed') = '{safe}'
      AND timestamp >= now() - INTERVAL {W} DAY
    GROUP BY trace_id HAVING trace_cost > 0
    ORDER BY trace_cost DESC LIMIT 500
    """)
    costs = [r[1] for r in rows]
    if not costs:
        continue
    mean = st.mean(costs); std = st.pstdev(costs) if len(costs) > 1 else 0.0
    outliers = [r[0] for r in rows if r[1] > mean + 2 * std]
    variance[op] = {
        "n": len(costs), "min": min(costs), "max": max(costs),
        "mean": round(mean, 6), "median": round(st.median(costs), 6), "std": round(std, 6),
        "p95": round(sorted(costs)[int(0.95 * (len(costs) - 1))], 6),
        "outlier_trace_ids": outliers[:10],
    }
json.dump(variance, open("{{results_dir}}/data/cost_variance.json", "w"), indent=2)
print(json.dumps({k: {"n": v["n"], "mean": v["mean"], "p95": v["p95"]} for k, v in variance.items()}, indent=2))
```

An operation where p95 ≫ median is the signal: a few traces cost 5–20× the typical one. Those
outlier trace IDs feed Steps 5 and 7.

---

## Step 5: Root-Cause the Cost Drivers

For each outlier trace, pull its generations and test concrete hypotheses. Don't guess — read the
actual `$ai_generation` rows.

```python
def explain_trace(trace_id: str):
    safe = trace_id.replace("'", "''")
    cols, rows = hogql(f"""
    SELECT properties.$ai_model AS model,
           toInt(properties.$ai_input_tokens) AS in_tok,
           toInt(properties.$ai_output_tokens) AS out_tok,
           properties.$ai_span_name AS span
    FROM events
    WHERE event = '$ai_generation' AND properties.$ai_trace_id = '{safe}'
    ORDER BY timestamp
    """)
    return {
        "trace_id": trace_id,
        "n_generations": len(rows),                       # retry storm / agent loop?
        "models": sorted({r[0] for r in rows if r[0]}),
        "max_input_tokens": max((r[1] or 0 for r in rows), default=0),
        "max_output_tokens": max((r[2] or 0 for r in rows), default=0),
    }
```

Hypotheses to confirm or rule out, per trace:

| Driver | Tell | Fix direction |
|--------|------|---------------|
| **Prompt bloat** | `max_input_tokens` huge vs task | Trim context / prompt caching / RAG relevance filter |
| **Model misuse** | premium model on a trivial step | Downgrade to a budget tier (Haiku / 4o-mini / Flash) |
| **Retry storm** | many near-identical generations in one trace | Idempotency / backoff / dedupe |
| **Context stuffing** | whole history re-sent every turn | Summarize / window the context |

---

## Step 6: Failure-Mode Detection

Find the errors and inconsistency the cost view hides. PostHog flags failed calls with
`$ai_is_error` and carries `$ai_http_status` / `$ai_error`.

```python
cols, rows = hogql(f"""
SELECT coalesce(nullIf(properties.$ai_span_name, ''), 'unnamed') AS operation,
       toInt(properties.$ai_http_status) AS http_status,
       count() AS errors
FROM events
WHERE event = '$ai_generation' AND properties.$ai_is_error
  AND timestamp >= now() - INTERVAL {W} DAY
GROUP BY operation, http_status
ORDER BY errors DESC
""")
for r in rows:
    print(r)
```

Catalog: timeout patterns (very high `$ai_latency` + error), rate-limit errors (HTTP 429),
malformed/empty `$ai_output_choices`, and high output-token variance (a sign of inconsistent
behavior). Note error **rate** per operation (already in `metrics_by_span.csv`), not just absolute
counts.

---

## Step 7: Qualitative Trace Assessment (manual inspection)

Aggregates miss the things that actually embarrass a team. Pull `{{sample_size}}` traces across
percentiles (cheapest / median / most expensive / slowest / errored) and **read** their `$ai_input`
and `$ai_output_choices`. Write `data/qualitative_samples.json` with the trace ID, an
input/output excerpt, and the abnormality tag for each.

```python
import json
SAMPLE = int("{{sample_size}}")

ABNORMALITIES = {  # tag : how to spot it
  "prompt_stuffing":   "input tokens far exceed the necessary context",
  "response_truncation": "output ends mid-sentence / finish_reason=length",
  "model_confusion":   "output ignores the instruction / wrong format",
  "retry_storm":       "multiple identical generations in one trace",
  "tool_abuse":        "same tool called repeatedly with the same args",
  "empty_output":      "generation returns null/empty",
}

def read_generation(trace_id: str):
    safe = trace_id.replace("'", "''")
    cols, rows = hogql(f"""
    SELECT properties.$ai_span_name, properties.$ai_model,
           toString(properties.$ai_input), toString(properties.$ai_output_choices),
           toFloat(properties.$ai_total_cost_usd), toInt(properties.$ai_input_tokens)
    FROM events
    WHERE event = '$ai_generation' AND properties.$ai_trace_id = '{safe}'
    ORDER BY timestamp LIMIT 1
    """)
    return rows[0] if rows else None

# Build a diverse sample: cheapest 3 + median 3 + most-expensive 3 + slowest 3 + errored,
# drawn from the trace IDs surfaced in Step 4 (and an errored-trace query). For each, read the
# first generation, truncate $ai_input / $ai_output_choices to ~400 chars, and tag the matching
# ABNORMALITIES key (or "clean").
samples = []  # {trace_id, operation, percentile_bucket, input_excerpt, output_excerpt, abnormality, note}
json.dump(samples[:SAMPLE], open("{{results_dir}}/data/qualitative_samples.json", "w"), indent=2)
print(f"Inspected {min(len(samples), SAMPLE)} traces.")
```

For every abnormality you tag, record an **estimated frequency** ("seen in ~4/15 sampled
`agent_loop` traces"). That estimate is what makes a qualitative finding actionable.

---

## Step 8: Rank Recommendations (evidence + WHY + code + measurement)

Turn findings into **at least `{{min_recommendations}}`** ranked recommendations. Each one MUST
have all five parts — a recommendation without a measurement plan is an opinion, not an
engineering action:

1. **The problem** — one tight paragraph.
2. **Why it matters** — quantified business/technical impact ("~40% of monthly spend").
3. **Evidence from your traces** — a table of real trace IDs + cost/tokens + the specific issue,
   plus one truncated input/output sample.
4. **The fix** — a `# Before` / `# After` Python code example.
5. **How to measure success** — metric to track, current baseline, target after fix, validation
   period (and *why* that long), and how to verify it in PostHog (filter the `$ai_generation`
   insight by `$ai_span_name`, compare cost before/after).

Rank by impact × ease. The cost-optimization menu to draw from:

| Strategy | When | Expected savings |
|----------|------|------------------|
| Model downgrade | premium model on simple tasks | 50–90% |
| Prompt caching / compression | large repeated context | 20–40% |
| Context trimming (RAG relevance) | over-stuffed contexts | 30–50% |
| Response/semantic caching | repeated identical queries | variable |

---

## Step 9: Factor in Prior Analysis History (if provided)

If `{{analysis_history}}` is non-empty, it lists past recommendations and the PRs that acted on
them. Use it to make this report a *follow-up*, not a repeat:

- **Don't re-recommend shipped fixes.** For any merged PR, pull the diff (`gh pr view <n>`,
  `gh pr diff <n>`) to see what actually changed, and skip recommendations it already covers.
- **Check predicted impact.** Compare current metrics to the baselines/targets from prior
  recommendations — did the fix land its number? Call out hits and misses explicitly.
- **Read closed-without-merge PRs.** The comments say what the team rejected and why; don't
  re-propose it.
- **Surface regressions.** Flag anything that got worse since the last analysis.

If `{{analysis_history}}` is empty, skip this step and note "first analysis — no prior history".

---

## Step 10: Write `recommendations.md` (the report) + `summary.md`

Assemble `{{results_dir}}/recommendations.md` with this structure:

```markdown
# PostHog LLM Trace Analysis — <project> — <date>

## Executive Summary
- Analysis window: <Nd> (<from> → <to>)
- Generations analyzed: <count>  ·  Total cost: $<amount>  ·  Models in use: <list>
- Top 3 findings (one line each)
- Total projected monthly savings: $<amount>

## Cost Analysis
### Most-called operations (table: $ai_span_name, count, total cost, avg cost/call)
### Most-expensive operations (table: $ai_span_name, total cost, count, avg, p95)
### Cost by model (table)

## High-Variance Investigation
Per top operation: cost range (min–max, mean), the root cause, and the evidence trace IDs.

## Failure-Mode Analysis
Error distribution by operation + HTTP status + the failure patterns cataloged.

## Qualitative Findings
Per abnormality: sample trace ID, what was observed, a truncated input/output sample,
estimated frequency, and why it matters.

## Recommendations
Priority 1..N — each with: The Problem / Why It Matters / Evidence (trace-ID table + sample) /
Recommended Fix (Before-After code) / How to Measure Success (metric, baseline, target,
validation period, how to verify in PostHog) / Expected Impact.

## Implementation Roadmap
| Priority | Recommendation | Effort | Expected savings | Validation period |
Total estimated monthly savings + the recommended A/B validation approach (compare an
`$ai_span_name` / version property before vs after).

## Appendix
Methodology, raw data table pointers, model-pricing reference (data/model_pricing.json).
```

Then write `{{results_dir}}/summary.md`: window, generations analyzed, total cost, the top 3
findings, and the total projected monthly savings — one screen, no tables longer than 5 rows.

---

## Step 11: Self-Validation Report

Write `{{results_dir}}/validation_report.json`:

```json
{
  "version": "1.0.0", "run_date": "<ISO>",
  "backend": "posthog",
  "parameters": {"window_days": 30, "top_n": 5, "sample_size": 15},
  "stages": [
    {"name": "connect",      "passed": true, "message": "query API ok; $ai_generation events present"},
    {"name": "pricing",      "passed": true, "message": "N models priced"},
    {"name": "metrics",      "passed": true, "message": "by-span + by-model CSVs written"},
    {"name": "variance",     "passed": true, "message": "top-N cost distributions"},
    {"name": "failures",     "passed": true, "message": "error distribution captured"},
    {"name": "qualitative",  "passed": true, "message": "K traces inspected + tagged"},
    {"name": "report",       "passed": true, "message": "recommendations.md written"}
  ],
  "results": {"generations_analyzed": 0, "total_cost_usd": 0.0,
              "recommendations": 0, "qualitative_findings": 0,
              "projected_monthly_savings_usd": 0.0},
  "overall_passed": false
}
```

`overall_passed` is `true` **iff**: the connection succeeded and `$ai_generation` events were
present, `recommendations.md` exists with an Executive Summary + Cost Analysis + Qualitative
Findings + Recommendations + Roadmap, there are ≥ `{{min_recommendations}}` recommendations,
**each** recommendation has a code example and a measurement plan, and ≥ 1 finding cites a real
trace ID.

---

## Rubric (how this report is judged)

| # | Criterion | 5 (Excellent) | 3 (Acceptable) | 1 (Poor) |
|---|-----------|---------------|-----------------|----------|
| 1 | **Evidence** | Every finding cites real `$ai_trace_id`s + input/output excerpts pulled from the live project | Some findings cite trace IDs; others are generic | Generic advice, no trace evidence |
| 2 | **Cost analysis** | Both volume and cost tables present, avg-cost-per-call computed, model split shown | Tables present but shallow | Missing or unbacked by data |
| 3 | **Qualitative depth** | ≥2 abnormalities found by manual inspection with frequency estimates | 1 abnormality, thinly evidenced | No manual inspection |
| 4 | **Actionability** | ≥3 recs, each with WHY + before/after code + measurement plan (metric, baseline, target, window) | Recs present but missing code or measurement plan | Vague suggestions, no code |
| 5 | **Roadmap** | Prioritized by impact×effort with quantified savings + validation timelines | Listed but unprioritized/unquantified | Absent |

A recommendation **without** a measurement plan does not count toward criterion 4. Describe the
*target* the team should hit, not just the current state.

---

## Final Checklist (MANDATORY — do not skip)

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="{{results_dir}}"; FAIL=0
for f in recommendations.md summary.md validation_report.json \
         data/metrics_by_span.csv data/metrics_by_model.csv data/cost_variance.json \
         data/qualitative_samples.json data/model_pricing.json; do
  if [ -s "$RESULTS_DIR/$f" ]; then echo "PASS: $f ($(wc -c < "$RESULTS_DIR/$f") bytes)";
  else echo "FAIL: $f missing/empty"; FAIL=$((FAIL+1)); fi
done
for sec in "Executive Summary" "Cost Analysis" "Qualitative Findings" "Recommendations" "Implementation Roadmap"; do
  grep -q "$sec" "$RESULTS_DIR/recommendations.md" && echo "PASS: section '$sec'" \
    || { echo "FAIL: section '$sec' missing"; FAIL=$((FAIL+1)); }
done
RECS=$(grep -c -E "^### (Priority|Recommendation)" "$RESULTS_DIR/recommendations.md" 2>/dev/null || echo 0)
echo "recommendations found: $RECS"
[ "$RECS" -ge 3 ] || { echo "FAIL: fewer than 3 recommendations"; FAIL=$((FAIL+1)); }
grep -q '```python' "$RESULTS_DIR/recommendations.md" || { echo "FAIL: no code example in report"; FAIL=$((FAIL+1)); }
[ "$FAIL" -gt 0 ] && { echo "OVERALL: FAIL ($FAIL)"; exit 1; }; echo "OVERALL: PASS"
```

### Checklist

- [ ] Query API connected and `$ai_generation` events present — analysis is on **real** data
- [ ] `metrics_by_span.csv` + `metrics_by_model.csv` written from HogQL aggregates
- [ ] Top-`{{top_n}}` cost-variance distributions computed with flagged outlier trace IDs
- [ ] ≥ `{{sample_size}}`-trace qualitative pass done, each tagged + frequency-estimated
- [ ] `recommendations.md` has all five sections and ≥ `{{min_recommendations}}` recommendations
- [ ] Every recommendation has evidence trace IDs, a before/after code example, and a measurement plan
- [ ] `summary.md` fits one screen; `validation_report.json` has `overall_passed`
- [ ] Verification script printed `OVERALL: PASS`

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Connect first, STOP if you can't** (or if there are zero `$ai_generation` events). A report
  written against data you couldn't read is worse than no report — it's confidently wrong.
- **HogQL escapes matter.** Operation/trace names go into queries — double single-quotes (`''`)
  and prefer parameterizing by an allow-list of values you already pulled, not raw user strings.
- **PostHog already costs your calls.** `$ai_total_cost_usd` is computed server-side; only fall
  back to the LiteLLM pricing map for models PostHog priced at null (new releases).
- **Read the traces.** The qualitative pass is where the embarrassing wins live (a 12k-token
  system prompt re-sent every turn, a retry storm tripling a trace's cost). `$ai_input` /
  `$ai_output_choices` carry the actual payloads — read them.
- **Every recommendation earns its place with a number.** Baseline → target, and the validation
  window with the reason. That's how the team proves the fix worked in a PostHog insight later.
