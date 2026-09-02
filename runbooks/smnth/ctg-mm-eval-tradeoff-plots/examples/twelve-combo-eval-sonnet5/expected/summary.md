# Multiple Myeloma Extraction — Agent/Model Trade-off Summary

Source data: `/app/assets/6c1ecf5c.00.csv` (the uploaded evaluation matrix), 12 agent+model combinations, 8 `scored` and 4 `zero_output`.

## recall_vs_field_accuracy.png

Plots recall (did the run find all the studies?) against overall field accuracy (were the fields on the studies it found actually correct?) for all 12 runs. The four `zero_output` runs sit at (0, 0) in red, jittered apart with leader lines so all four are individually labeled instead of stacking into one dot. The standout finding: `cc/gpt-5.6-luna` reaches 97.87% recall — as good as almost anything else on the chart — but its field accuracy collapses to 66.67% (its title and enrollment accuracy are both 0%, unlike every other scored run), so it lands far to the right but well below the main cluster.

**Takeaway:** recall alone is a misleading proxy for quality — `cc/gpt-5.6-luna` looks competitive on recall but is the worst-performing scored run once field accuracy is considered, while `opencode/kimi-k2` (the lone 100%-recall run, marked green) also has merely mid-pack field accuracy (90.78%), so no single run dominates on both axes simultaneously.

## recall_vs_runtime.png

Plots duration (log scale) against recall for all 12 runs, coloring points by agent and marking the four `zero_output` runs with an X in their agent's color plus a "(failed)" label. Runtimes span nearly two orders of magnitude (15s to 1810s) with no consistent relationship between how long a run took and whether it succeeded — some failures died in 15-31 seconds, others burned 800-1800 seconds before delivering nothing.

**Takeaway:** longer runtime buys no reliability guarantee — the fastest scored run (`oc/gpt-5.6-sol`, ~400s) and slowest scored run (`cc/claude-sonnet-4-6`, ~1808s) land in the same 95-100% recall band, while two of the four failures ran longer than most successes.

## cost_per_found_study.png

Bar chart of dollars spent per correctly-found study, one slot per combination. Only 3 of 12 runs have both a tracked cost and at least one found study, so the chart shows those 3 real bars (sorted ascending) followed by a divider and 9 explicit "no data" slots — 8 marked "no cost data" (all `opencode` runs don't track cost at all) and 1 (`cc/gpt-5.6-terra`, zero_output) marked "cost tracked, 0 studies found" since it spent $0.35 but found nothing, making cost-per-study undefined rather than zero. The cheapest-looking bar, `cc/gpt-5.6-luna` at $0.004/study, is flagged in red: it's cheap only because it's the corrupted run from the field-accuracy chart (0% title/enrollment accuracy), so a low dollar figure there is not something to copy.

**Takeaway:** cost data barely exists for this benchmark (only claude-code runs tracked it), and the one run that looks like a bargain is actually the corrupted one — `cc/claude-sonnet-4-6` at $0.0205/found-study is the only trustworthy "good and cheap" data point here.

## agent_reliability_comparison.png

Aggregate grouped bars comparing claude-code vs opencode across all attempts (not just scored runs): success rate, mean recall (scored only), mean field accuracy (scored only). claude-code succeeded in only 3 of 6 attempts (50%) vs opencode's 5 of 6 (83.3%); on the runs that did succeed, recall is nearly identical (97.2% vs 97.4%) but claude-code's mean field accuracy is dragged down to 83.8% by the corrupted `gpt-5.6-luna` run, versus opencode's 92.3%.

**Takeaway:** opencode is the more reliable agent overall — it fails less often and its successful runs are not weighed down by a corrupted extraction the way claude-code's are.

## recall_per_minute.png

Bar chart of recall_pct ÷ (duration_seconds / 60) — how quickly each run reaches its recall level — for all 12 runs, sorted descending. The four `zero_output` runs correctly compute to 0.00 and appear as visible red zero-height bars rather than being dropped. `cc/gpt-5.6-luna` tops the chart at 24.25 %/min, followed by `cc/gpt-5.6-sol` (18.76) and `oc/gpt-5.6-sol` (14.63); note that the top spot is again the corrupted run, so "fastest" here does not mean "best."

**Takeaway:** if you only care about getting to a usable recall number quickly, `cc/gpt-5.6-sol` (18.76 %/min, and *not* corrupted) is the standout — fast and one of only two runs with trustworthy field accuracy above 92%.

## Which chart should I look at?

- **Choosing a model for production quality:** `recall_vs_field_accuracy.png` — it's the only chart that shows recall can lie about quality.
- **Choosing for speed under time pressure:** `recall_per_minute.png` — but skip the top bar (corrupted) and pick the second.
- **Choosing an agent (not a model):** `agent_reliability_comparison.png` — opencode fails less and isn't corrupted.
- **Budget-constrained:** `cost_per_found_study.png` — but note only 3 of 12 runs have any cost data at all, and the cheapest of those is the corrupted one.
- **Understanding the speed/completeness trade-off in general:** `recall_vs_runtime.png` — shows runtime doesn't predict success.

## Noted deviations

None — all 5 charts render with the specified palette, all 12 combinations are individually labeled on every per-run chart, and the programmatic overlap check (`get_window_extent` bounding-box comparison) passed on the first render for both scatter charts. Leader lines for jittered/relocated labels are drawn as manually-clipped segments (data point → nearest text bounding-box edge) rather than via `adjustText`'s built-in `arrowprops`, because the latter's `ax.annotate` fallback (triggered by matplotlib's headless Agg backend) drew arrows that visually struck through several labels; the manual clipping keeps the same visual intent (thin gray leader lines back to each point) without that artifact.
