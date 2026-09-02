# Multiple Myeloma Extraction — Trade-off Visualizations: Summary

Source data: `/app/assets/81a3cc18.00.csv` — 12 agent+model combinations (6 `claude-code`, 6 `opencode`), 9 `scored` and 3 `zero_output`.

## recall_vs_field_accuracy.png

Plots recall against overall field accuracy for all 12 runs. Eight runs cluster tightly between 95–100% recall and 98–100% field accuracy (shown in a zoomed inset since they'd otherwise overlap), one run (`oc/kimi-k2.5`) trails badly on field accuracy (79.8%) despite reasonable recall (90.5%) because it populated the URL field with API record links instead of clinicaltrials.gov study pages, and three zero-output runs sit at the origin. **Takeaway:** near-perfect recall does not guarantee near-perfect accuracy — `oc/kimi-k2.5` shows a model can find most of the right studies and still deliver a field-accuracy failure due to one systematically wrong column.

## recall_vs_runtime.png

Plots recall against wall-clock duration (log scale) for all 12 runs, with zero-output runs marked as an X in their agent's color rather than a third hue. The fastest runs to score highly are `cc/gpt-5.6-terra` (297s, 100% recall) and `oc/gpt-5.6-terra` (302s, 100% recall); the slowest run, `cc/kimi-k2.5`, took 1502s and still produced zero output. **Takeaway:** runtime and recall are not correlated once a model actually completes the task — the two fastest *and* two slowest runs in this dataset include both a top scorer and a total failure, so speed alone tells you nothing about whether you'll get a usable result.

## cost_per_found_study.png

Bar chart of dollars spent per correctly-found study, for the 4 runs that have both cost and found-study data (all `claude-code`), with the other 8 runs (all `opencode`, plus the two `claude-code` runs that lack usable found-study cost data) shown as explicit "no cost data" slots rather than omitted. `cc/gpt-5.6-terra` is the cheapest at $0.047/study; `cc/opus-5` is the most expensive at $0.232/study — roughly 5x more for the same 100% recall. **Takeaway:** among the only runs with cost visibility, model choice swings cost-per-correct-result by 5x even when recall is identical, and opencode's lack of cost instrumentation means its runs currently can't be judged on this axis at all.

## agent_reliability_comparison.png

Aggregate grouped bars comparing `claude-code` and `opencode` across all attempts (not just scored ones): success rate, mean recall (scored runs only), and mean field accuracy (scored runs only). `opencode` completes more often (83.3% vs 66.7% success rate), but `claude-code`'s scored runs are slightly more accurate on both recall (98.8% vs 98.1%) and field accuracy (99.0% vs 95.8%) — the accuracy gap is driven almost entirely by opencode's one bad `kimi-k2.5` run dragging its mean down. **Takeaway:** opencode fails less often, but when claude-code does complete a run, it's marginally more trustworthy on the numbers it reports.

## recall_per_minute.png

Bar chart of recall percentage divided by runtime in minutes, sorted descending, for all 12 runs — zero-output runs correctly compute to a real 0 and appear as a visible zero-height bar. `cc/gpt-5.6-terra` (20.2) and `oc/gpt-5.6-terra` (19.9) lead by a wide margin; `oc/kimi-k2.5`, despite scoring, is the slowest-to-value scored run at 4.6. **Takeaway:** the `gpt-5.6-terra` model reaches full recall roughly 2-4x faster per unit of accuracy than the flagship Claude/GPT models in this benchmark, making it the best pick when time-to-answer matters as much as correctness.

## Which chart should I look at?

- **Choosing the most accurate model overall:** `recall_vs_field_accuracy.png`
- **Choosing under a time budget:** `recall_vs_runtime.png` or `recall_per_minute.png`
- **Choosing under a cost budget:** `cost_per_found_study.png` (but note 8 of 12 runs have no cost data)
- **Choosing an agent framework (not a model):** `agent_reliability_comparison.png`

If you only have time for one: **`recall_vs_field_accuracy.png`** — it answers "which model is actually best" directly, and its inset makes clear that most of the field is bunched at the top with only one silent accuracy failure and three outright failures to worry about.

## Deviations from spec

None. All 5 charts render with the exact specified palette, every per-run chart labels all 12 combinations with zero overlapping labels (programmatically verified via bounding-box and locality gates), no dual-axis/pie/3D charts were used, and the dense 8-point cluster in `recall_vs_field_accuracy.png` uses the inset-zoom fallback as permitted by the runbook (rather than plain adjustText, which would not have separated 8 points crowded into a ~5%x2% region).

Note: the runbook's generic description says 8 `scored` / 4 `zero_output` rows; the actual uploaded CSV has 9 `scored` / 3 `zero_output` rows. All charts and numbers reflect the actual data.
