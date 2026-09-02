# Multiple myeloma extraction trade-off plots (Jetty runbook)

**Turn a 12-row agent+model evaluation matrix into five charts that each answer a different
question.** Which combination is most accurate, which is fastest for the accuracy it gets,
which is cheapest per correct result, which agent is more reliable overall, and which
reaches a good answer fastest — rendered with a fixed colorblind-safe palette, one axis per
chart, every one of the 12 combinations labeled, and a hard programmatic
no-overlapping-labels gate before any chart is accepted.

## Flow

1. **Setup** — pandas, matplotlib, adjustText.
2. **Design system** — exact hex values for surface, ink, the two agent hues, and status
   colours; no dual axes, no pies, no default colour cycle.
3. **Derive** — cost per found study, recall per minute, per-agent success/recall/accuracy
   aggregates → `chart_data.json`.
4. **Render + verify** — five PNGs; scatter charts jitter only exactly-coincident points
   (clamped to the data bounds), run adjustText, and assert both zero overlapping labels and
   label locality (every label within 12% of its marker) before saving — dense clusters go
   into an inset zoom instead of having their labels exiled across the chart.
5. **Report** — `summary.md` with a per-chart takeaway and a "which chart to look at" guide.

## Deliverables (`{{results_dir}}/`)

| File | What |
|------|------|
| `charts/recall_vs_field_accuracy.png` | "Which is actually best" quadrant view |
| `charts/recall_vs_runtime.png` | Speed vs completeness (log runtime) |
| `charts/cost_per_found_study.png` | Dollars per correctly-found study, missing-cost slots explicit |
| `charts/agent_reliability_comparison.png` | claude-code vs opencode: success rate, mean recall, mean accuracy |
| `charts/recall_per_minute.png` | Throughput view |
| `chart_data.json` | The exact numbers behind every chart |
| `summary.md`, `validation_report.json` | Takeaways and stage results |

## Input

A 20-column CSV (`agent, model, status, gold_total, num_found, … cost_usd, total_tokens,
duration_seconds, notes`), one row per agent+model combination. The example matrix scores 12
combinations against a ClinicalTrials.gov extraction benchmark (8 scored, 4 zero-output).
The chart logic assumes this schema; a differently-shaped evaluation CSV needs the column
names in Step 3 adjusted.

## Examples

See `examples/` — real runs on Jetty with the input matrix, `expected/` charts and data,
`trajectory.json`, and a thumbnail.
