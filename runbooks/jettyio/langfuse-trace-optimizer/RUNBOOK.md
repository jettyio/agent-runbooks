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
  source_title: "Langfuse Optimizer — Terminal Bench 2.0 task"
  imported_at: "2026-06-24T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: jettyio
    skill_name: langfuse-trace-optimizer
    author: "Jetty trace-experimentation-agent"
    confidence: high
secrets:
  LANGFUSE_PUBLIC_KEY:
    env: LANGFUSE_PUBLIC_KEY
    description: "Langfuse public key (pk-lf-…). Project Settings → API Keys."
    required: true
  LANGFUSE_SECRET_KEY:
    env: LANGFUSE_SECRET_KEY
    description: "Langfuse secret key (sk-lf-…). Project Settings → API Keys."
    required: true
  LANGFUSE_HOST:
    env: LANGFUSE_HOST
    description: "Langfuse host, e.g. https://cloud.langfuse.com (US) or https://eu.cloud.langfuse.com (EU), or your self-hosted URL."
    required: true
---

# Langfuse Trace Optimizer — LLM Cost & Quality Report — Agent Runbook

> **EXECUTE THIS RUNBOOK NOW.** Connect to the live Langfuse project with the provided
> credentials, pull real trace data, analyze it, and write every deliverable to
> `{{results_dir}}`. This is a task to perform against a live observability backend, not a
> document to summarize. Your first action is a tool call (Step 1). The credentials are already
> provided as environment variables — never pause to ask the user for them.

## Inputs (already provided)

- **Langfuse credentials:** `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` —
  injected as environment variables. They point at a real project with real trace data.
- **Analysis window:** {{window_days}} — how many days back to analyze (default 30).
- **Prior analysis history (optional):** {{analysis_history}} — a timeline of past
  recommendations + merged/closed PRs. If present, factor it in (see Step 9): do not
  re-recommend already-shipped fixes, and check whether prior recommendations had their
  predicted impact.

## Objective

Analyze a project's Langfuse trace data the way a cost-and-quality engineer would, and hand
back a **`recommendations.md`** report that an engineering team can act on this week. The agent
connects to Langfuse, pulls aggregate metrics and individual traces, finds the cost drivers and
failure modes **quantitatively**, then inspects sampled traces **qualitatively** for the
abnormalities aggregates miss (prompt stuffing, retry storms, model misuse, truncation). Every
finding is backed by **actual trace IDs and excerpts**, and every recommendation ships with a
code example and a **measurement plan** (metric, baseline, target, validation window) so the
team can prove the fix worked in Langfuse afterward.

The deliverable is a decision-ready report, not a data dump: a tight executive summary, ranked
recommendations with evidence and code, and an implementation roadmap with effort/impact/timeline.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following to `{{results_dir}}`. The task is NOT complete until every
file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `{{results_dir}}/recommendations.md` | The headline report: executive summary, cost analysis tables, qualitative findings, ≥3 ranked recommendations (each with evidence trace IDs, WHY, code example, measurement plan), and an implementation roadmap. |
| `{{results_dir}}/data/metrics_by_trace.csv` | Per-trace-name aggregates (count, total cost, total tokens, p95 latency) for the analysis window. |
| `{{results_dir}}/data/metrics_by_model.csv` | Per-model aggregates at the observation level (count, cost, tokens). |
| `{{results_dir}}/data/cost_variance.json` | Per-expensive-trace cost distribution (min/mean/median/max/std/p95) and flagged outliers. |
| `{{results_dir}}/data/qualitative_samples.json` | The sampled traces inspected manually, with trace IDs, input/output excerpts, and the abnormality tagged on each. |
| `{{results_dir}}/data/model_pricing.json` | Current model pricing fetched from LiteLLM (provider-filtered). |
| `{{results_dir}}/summary.md` | One-screen executive summary: window, traces analyzed, total cost, top 3 findings, total projected monthly savings. |
| `{{results_dir}}/validation_report.json` | Stage-by-stage self-validation with `overall_passed`. See Step 11. |

Figures (optional) go in `{{results_dir}}/figures/`. If you finish but have not written every
mandatory file, go back and write it.

---

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|------------------|---------|-------------|
| Results directory | `{{results_dir}}` | `/app/results` | Output directory |
| Analysis window (days) | `{{window_days}}` | `30` | How far back to pull traces. The run also computes 3d/7d sub-windows for trend. |
| Top-N expensive traces | `{{top_n}}` | `5` | How many of the most expensive trace names to deep-dive in Steps 4–6. |
| Qualitative sample size | `{{sample_size}}` | `15` | How many individual traces to pull for manual inspection in Step 7. |
| Min recommendations | `{{min_recommendations}}` | `3` | Floor on actionable recommendations in the report. |
| Analysis history | `{{analysis_history}}` | *(optional)* | Prior recommendations + PR timeline to avoid re-recommending shipped fixes. |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST` | Secret | Yes | Auth + endpoint for the live Langfuse project. |
| `langfuse` (pip) | Runtime | Yes | Python SDK (Metrics API + trace/observation listing). |
| `litellm` (pip) | Runtime | Yes | Live model pricing reference (provider-filtered). |
| `pandas` (pip) | Runtime | Yes | Aggregation + CSV output. |
| `matplotlib` (pip) | Runtime | No | Optional cost/latency figures. |

---

## Step 1: Environment Setup & Connectivity Check

Install deps, write the creds to `{{results_dir}}/.env` for reproducibility, and **prove the
connection before doing anything else**. If you cannot connect, STOP — this is a live-data task
and every downstream step depends on it.

```bash
mkdir -p "{{results_dir}}/data" "{{results_dir}}/figures"
pip install -q langfuse litellm pandas matplotlib tabulate

# Persist creds for reproducibility (never echo the secret values into logs).
cat > "{{results_dir}}/.env" <<EOF
LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
LANGFUSE_HOST=${LANGFUSE_HOST}
EOF

[ -n "$LANGFUSE_PUBLIC_KEY" ] && [ -n "$LANGFUSE_SECRET_KEY" ] && [ -n "$LANGFUSE_HOST" ] \
  || { echo "ERROR: missing Langfuse credentials"; exit 1; }
echo "Langfuse host: $LANGFUSE_HOST"
```

```python
# Connectivity gate — STOP IMMEDIATELY IF THIS FAILS.
from langfuse import get_client
langfuse = get_client()
assert langfuse.auth_check(), "Langfuse auth_check() failed — bad keys or host"
print("Langfuse connection OK")
```

If `auth_check()` raises or returns false, do not continue: report the connection failure in
`summary.md` and exit. Do not fabricate analysis against data you could not read.

---

## Step 2: Fetch Live Model Pricing (provider-filtered)

Accurate cost analysis needs current pricing. Fetch it from LiteLLM and filter by the
`litellm_provider` field — **not** by matching model-name substrings, so new families
(`gpt-4.1`, `claude-4`, `gemini-2`) are picked up automatically. Write
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

Keep a `get_model_cost(name)` helper handy (exact → case-insensitive → strip `provider/` prefix
→ shortest substring match) so a Langfuse model string like `openai/gpt-4o` still resolves.

---

## Step 3: Aggregate Metrics — Cost & Volume by Trace and Model

Use the **Metrics API** (cheap aggregates, not row-by-row listing) for the window and two
sub-windows (3d/7d/Nd). Write `metrics_by_trace.csv` and `metrics_by_model.csv`.

```python
import json, pandas as pd
from datetime import datetime, timedelta, timezone
from langfuse import get_client
langfuse = get_client()
WINDOW = int("{{window_days}}")

def metrics(view, dimensions, measures, from_ts, to_ts):
    q = json.dumps({"view": view, "dimensions": dimensions, "metrics": measures,
                    "fromTimestamp": from_ts, "toTimestamp": to_ts})
    return langfuse.api.metrics.metrics(query=q)

to_ts = datetime.now(timezone.utc).isoformat()
from_ts = (datetime.now(timezone.utc) - timedelta(days=WINDOW)).isoformat()

# Per trace name: volume, cost, tokens, p95 latency
by_trace = metrics("traces", [{"field": "name"}],
    [{"measure": "count", "aggregation": "count"},
     {"measure": "totalCost", "aggregation": "sum"},
     {"measure": "totalTokens", "aggregation": "sum"},
     {"measure": "latency", "aggregation": "p95"}], from_ts, to_ts)

# Per model (observation level): how spend splits across models
by_model = metrics("observations", [{"field": "providedModelName"}],
    [{"measure": "count", "aggregation": "count"},
     {"measure": "totalCost", "aggregation": "sum"},
     {"measure": "totalTokens", "aggregation": "sum"}], from_ts, to_ts)

dt = pd.DataFrame(by_trace.data if hasattr(by_trace, "data") else by_trace)
dm = pd.DataFrame(by_model.data if hasattr(by_model, "data") else by_model)
dt.to_csv("{{results_dir}}/data/metrics_by_trace.csv", index=False)
dm.to_csv("{{results_dir}}/data/metrics_by_model.csv", index=False)
print("traces:", len(dt), "| models:", len(dm))
print(dt.sort_values(dt.columns[-3] if len(dt.columns) > 2 else dt.columns[0], ascending=False).head(10))
```

Inspect the shape of the returned rows (the Metrics API returns dimension + metric columns) and
adapt the column names. Compute **avg cost per call** (`totalCost / count`) — it surfaces cheap
high-volume traces vs expensive low-volume ones, which need different fixes.

---

## Step 4: Cost-Variance Deep Dive on the Top-N Expensive Traces

For the `{{top_n}}` most expensive trace names, list individual traces and compute the cost
distribution. High variance is where the money leaks. Write `data/cost_variance.json`.

```python
import json, statistics as st
from langfuse import get_client
langfuse = get_client()
TOP_N = int("{{top_n}}")

# expensive_names: top-N trace names by total cost from Step 3
variance = {}
for name in expensive_names:
    traces = langfuse.api.trace.list(name=name, from_timestamp=from_ts, to_timestamp=to_ts,
                                     limit=500, fields="core,metrics")
    costs = [t.total_cost for t in traces.data if getattr(t, "total_cost", None)]
    if not costs:
        continue
    mean = st.mean(costs); std = st.pstdev(costs) if len(costs) > 1 else 0.0
    outliers = [t.id for t in traces.data
                if getattr(t, "total_cost", None) and t.total_cost > mean + 2 * std]
    variance[name] = {
        "n": len(costs), "min": min(costs), "max": max(costs),
        "mean": round(mean, 6), "median": round(st.median(costs), 6),
        "std": round(std, 6),
        "p95": round(sorted(costs)[int(0.95 * (len(costs) - 1))], 6),
        "outlier_trace_ids": outliers[:10],
    }
json.dump(variance, open("{{results_dir}}/data/cost_variance.json", "w"), indent=2)
print(json.dumps({k: {"n": v["n"], "mean": v["mean"], "p95": v["p95"]} for k, v in variance.items()}, indent=2))
```

A trace name where p95 ≫ median is the signal: a few runs cost 5–20× the typical one. Those
outlier trace IDs feed Steps 5 and 7.

---

## Step 5: Root-Cause the Cost Drivers

For each expensive/outlier trace, pull its observations and test concrete hypotheses. Don't
guess — read the actual generations.

```python
from langfuse import get_client
langfuse = get_client()

def explain_trace(trace_id):
    trace = langfuse.api.trace.get(trace_id)
    obs = langfuse.api.observations.get_many(trace_id=trace_id, type="GENERATION", limit=100)
    gens = obs.data
    return {
        "trace_id": trace_id,
        "n_generations": len(gens),                       # retry storm / agent loop?
        "models": sorted({g.model for g in gens if getattr(g, "model", None)}),
        "max_input_tokens": max((getattr(g, "prompt_tokens", 0) or 0 for g in gens), default=0),
        "max_output_tokens": max((getattr(g, "completion_tokens", 0) or 0 for g in gens), default=0),
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

Find the errors and inconsistency the cost view hides. Use the Metrics API with a level filter,
then catalog patterns.

```python
import json
q = json.dumps({
    "view": "observations",
    "dimensions": [{"field": "traceName"}, {"field": "level"}],
    "metrics": [{"measure": "count", "aggregation": "count"}],
    "filters": [{"column": "level", "operator": "any of",
                 "value": ["ERROR", "WARNING"], "type": "stringOptions"}],
    "fromTimestamp": from_ts, "toTimestamp": to_ts})
errors = langfuse.api.metrics.metrics(query=q)
```

Catalog: timeout patterns (very high latency + error), rate-limit errors, malformed/empty
outputs, and high output-token variance (a sign of inconsistent behavior). Note error **rate**
per trace name, not just absolute counts.

---

## Step 7: Qualitative Trace Assessment (manual inspection)

Aggregates miss the things that actually embarrass a team. Pull `{{sample_size}}` traces across
percentiles (cheapest / median / most expensive / slowest / errored) and **read them**. Write
`data/qualitative_samples.json` with the trace ID, an input/output excerpt, and the abnormality
tag for each.

```python
import json
from langfuse import get_client
langfuse = get_client()
SAMPLE = int("{{sample_size}}")

ABNORMALITIES = {  # tag : how to spot it
  "prompt_stuffing":   "input tokens far exceed the necessary context",
  "response_truncation": "output ends mid-sentence / finish_reason=length",
  "model_confusion":   "output ignores the instruction / wrong format",
  "retry_storm":       "multiple identical generations in one trace",
  "tool_abuse":        "same tool called repeatedly with the same args",
  "empty_output":      "generation returns null/empty",
}

# Build a diverse sample from the expensive names: cheapest 3 + median 3 + top 3 + slowest 3 + errors.
samples = []   # each: {trace_id, trace_name, percentile_bucket, input_excerpt, output_excerpt, abnormality, note}
# ... select via langfuse.api.trace.list(..., fields="core,metrics") sorted by cost/latency,
#     then langfuse.api.trace.get(id) / observations.get_many(id) to read input/output, and
#     truncate excerpts to ~400 chars. Tag each with the matching ABNORMALITIES key (or "clean").
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
   period (and *why* that long), and how to verify it in Langfuse.

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
# Langfuse Trace Analysis — <project> — <date>

## Executive Summary
- Analysis window: <Nd> (<from> → <to>)
- Traces analyzed: <count>  ·  Total cost: $<amount>  ·  Models in use: <list>
- Top 3 findings (one line each)
- Total projected monthly savings: $<amount>

## Cost Analysis
### Most-called traces (table: name, count, total cost, avg cost/call)
### Most-expensive traces (table: name, total cost, count, avg, p95)
### Cost by model (table)

## High-Variance Investigation
Per top trace: cost range (min–max, mean), the root cause, and the evidence trace IDs.

## Failure-Mode Analysis
Error distribution by trace name + the failure patterns cataloged.

## Qualitative Findings
Per abnormality: sample trace ID, what was observed, a truncated input/output sample,
estimated frequency, and why it matters.

## Recommendations
Priority 1..N — each with: The Problem / Why It Matters / Evidence (trace-ID table + sample) /
Recommended Fix (Before-After code) / How to Measure Success (metric, baseline, target,
validation period, how to verify in Langfuse) / Expected Impact.

## Implementation Roadmap
| Priority | Recommendation | Effort | Expected savings | Validation period |
Total estimated monthly savings + the recommended A/B validation approach (version tags).

## Appendix
Methodology, raw data table pointers, model-pricing reference (data/model_pricing.json).
```

Then write `{{results_dir}}/summary.md`: window, traces analyzed, total cost, the top 3 findings,
and the total projected monthly savings — one screen, no tables longer than 5 rows.

---

## Step 11: Self-Validation Report

Write `{{results_dir}}/validation_report.json`:

```json
{
  "version": "1.0.0", "run_date": "<ISO>",
  "backend": "langfuse",
  "parameters": {"window_days": 30, "top_n": 5, "sample_size": 15},
  "stages": [
    {"name": "connect",      "passed": true, "message": "auth_check ok"},
    {"name": "pricing",      "passed": true, "message": "N models priced"},
    {"name": "metrics",      "passed": true, "message": "by-trace + by-model CSVs written"},
    {"name": "variance",     "passed": true, "message": "top-N cost distributions"},
    {"name": "failures",     "passed": true, "message": "error distribution captured"},
    {"name": "qualitative",  "passed": true, "message": "K traces inspected + tagged"},
    {"name": "report",       "passed": true, "message": "recommendations.md written"}
  ],
  "results": {"traces_analyzed": 0, "total_cost_usd": 0.0,
              "recommendations": 0, "qualitative_findings": 0,
              "projected_monthly_savings_usd": 0.0},
  "overall_passed": false
}
```

`overall_passed` is `true` **iff**: the connection succeeded, `recommendations.md` exists with an
Executive Summary + Cost Analysis + Qualitative Findings + Recommendations + Roadmap, there are
≥ `{{min_recommendations}}` recommendations, **each** recommendation has a code example and a
measurement plan, and ≥ 1 finding cites a real trace ID.

---

## Rubric (how this report is judged)

| # | Criterion | 5 (Excellent) | 3 (Acceptable) | 1 (Poor) |
|---|-----------|---------------|-----------------|----------|
| 1 | **Evidence** | Every finding cites real trace IDs + input/output excerpts pulled from the live project | Some findings cite trace IDs; others are generic | Generic advice, no trace evidence |
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
         data/metrics_by_trace.csv data/metrics_by_model.csv data/cost_variance.json \
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

- [ ] `auth_check()` passed — analysis is on **real** data, not invented
- [ ] `metrics_by_trace.csv` + `metrics_by_model.csv` written from the Metrics API
- [ ] Top-`{{top_n}}` cost-variance distributions computed with flagged outlier trace IDs
- [ ] ≥ `{{sample_size}}`-trace qualitative pass done, each tagged + frequency-estimated
- [ ] `recommendations.md` has all five sections and ≥ `{{min_recommendations}}` recommendations
- [ ] Every recommendation has evidence trace IDs, a before/after code example, and a measurement plan
- [ ] `summary.md` fits one screen; `validation_report.json` has `overall_passed`
- [ ] Verification script printed `OVERALL: PASS`

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Connect first, STOP if you can't.** Everything downstream is real-data analysis. A report
  written against data you couldn't read is worse than no report — it's confidently wrong.
- **Prefer the Metrics API for aggregates.** Listing individual traces is for the deep-dive and
  the qualitative sample only — paginate and use `fields="core,metrics"` to keep it cheap.
- **Read the traces.** The qualitative pass is where the embarrassing wins live (a 12k-token
  system prompt re-sent every turn, a retry storm tripling a trace's cost). Aggregates won't
  show you those — your eyes will.
- **Every recommendation earns its place with a number.** Baseline → target, and the validation
  window with the reason (e.g. "7 days to capture the weekly weekend dip"). That's how the team
  proves the fix worked in Langfuse later.
- **Filter pricing by provider, not name.** New model families show up automatically; name-substring
  matching silently misses `claude-4` / `gpt-4.1` / `gemini-2`.
