# garrytan/gstack-benchmark-models — demo payload

A launch payload for the `garrytan/gstack-benchmark-models` runbook: the runbook, a
`manifest.json`, and three worked examples — each a real production run that benchmarks the
same prompt across Claude, GPT, and Gemini.

```
gstack-benchmark-models/
  RUNBOOK.md                        # the runbook (v1.0.0)
  manifest.json                     # directory metadata
  README.md                         # this file
  examples/
    coding-merge-intervals/         # code prompt
      prompt.md  input.json  trajectory.json  thumbnail.png
      expected/  benchmark.md (primary) · results.json · summary.md · validation_report.json
    extraction-action-items/        # structured-extraction prompt
      prompt.md  input.json  trajectory.json  thumbnail.png  expected/ …
    writing-launch-blurb/           # writing prompt (the differentiating one)
      prompt.md  input.json  trajectory.json  thumbnail.png  expected/ …
```

## Attribution

Converted, with attribution, from **Garry Tan's `benchmark-models` skill** —
[github.com/garrytan/gstack](https://github.com/garrytan/gstack/tree/main/benchmark-models)
(**MIT**). The original wraps the `gstack-model-benchmark` binary plus the Claude / Codex /
Gemini CLIs. This runbook re-implements the same idea **provider-agnostically via litellm**
so it runs on Jetty's sandbox with no local CLI setup, and strips all the gstack-specific
scaffolding (config, telemetry, plan-mode, update checks).

## What it does

Runs the **same prompt** through 2+ models, measures **latency / tokens / cost**, captures
each output, scores **quality 0–10** with an LLM judge, and recommends the **fastest /
cheapest / highest-quality / best-overall** model. Models with no provider key or over
quota are skipped cleanly and reported — one provider down is still a useful benchmark.

## The gallery: three prompt types, one shootout each

Synthetic prompts (a code task, an extraction task, a writing task — *not* gstack's
examples), each benchmarked across `claude-sonnet-4-6`, `gpt-4o`, and `gemini-2.5-flash`:

| # | Prompt | Fastest | Cheapest | Top quality | The signal | Trajectory |
|---|--------|---------|----------|-------------|-----------|-----------|
| 1 | merge-intervals (code) | gpt-4o (2.4s) | gpt-4o | claude / gpt (10) | gemini verbose (2740 tok) + 5× slower | `3d17a697` |
| 2 | notes → JSON (extraction) | gpt-4o (1.5s) | gpt-4o | claude / gpt (10) | all three strong on structured output | `f7a86295` |
| 3 | launch blurb (writing) | gpt-4o (1.7s) | gpt-4o | **claude (9)** | **gpt-4o fastest+cheapest but scored 3/10** — missed the no-hype brief | `1b299910` |

**All 9 model-runs (3 models × 3 prompts) succeeded**; every run is `overall_passed: true`.
Example 3 is the point of the whole skill: the fastest, cheapest model produced the
**worst** writing — you only see that with a judge, not a stopwatch.

## Notes

- **Cost is `null` for `claude-sonnet-4-6`** — litellm has no pricing entry for it. Reported
  honestly, not treated as a failure. `gpt-4o` and `gemini` carry real cost.
- Provider access comes from **Jetty trial keys** (Anthropic / OpenAI / Gemini) on the
  platform; pass your own keys (or an `OPENROUTER_API_KEY`) for production.

## Reproduce (example 3 — the interesting one)

```bash
TOKEN="$(grep '^JETTY_API_TOKEN_JON_RUNBOOKS=' .env | cut -d= -f2-)"
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  --form-string 'init_params={"vars":{"models":"claude-sonnet-4-6,gpt-4o,gemini/gemini-2.5-flash","judge":"true"}}' \
  -F "files=@runbooks/garrytan/gstack-benchmark-models/examples/writing-launch-blurb/prompt.md" \
  "https://flows-api.jetty.io/api/v1/run/jon-runbooks/gstack-benchmark-models"
```
