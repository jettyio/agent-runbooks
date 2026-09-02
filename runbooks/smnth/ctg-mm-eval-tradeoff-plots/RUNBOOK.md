---
version: "1.3.0"
evaluation: programmatic
agent: claude-code
model: anthropic/claude-sonnet-5
model_provider: openrouter
snapshot: python312-uv
primary_outputs:
  - "charts/recall_vs_field_accuracy.png"
  - "charts/recall_vs_runtime.png"
  - "charts/cost_per_found_study.png"
  - "charts/agent_reliability_comparison.png"
  - "charts/recall_per_minute.png"
secrets: {}
---

# Multiple Myeloma Extraction — Trade-off Visualizations — Agent Runbook

## Objective

Produce a small set of genuinely different charts from `evaluation_matrix.csv` (12 agent+model combinations scored against a ClinicalTrials.gov extraction benchmark) that each answer a distinct question a user would ask when choosing between models: "which is most accurate," "which is fastest for the accuracy it gets," "which is cheapest per correct result," "which agent is more reliable overall," and "which gets to a good answer fastest." Do not produce five variations of the same scatter plot — each chart must earn its place by showing a relationship the others don't.

**Every one of the 12 agent+model combinations must be represented by its own visible, individually labeled point or bar in every per-run chart** (the only exception is `agent_reliability_comparison.png`, which is deliberately aggregate-level). A combination with no usable data (zero_output, or missing cost) still gets a slot on the chart — plotted at its true value (0 where that's the honest number, e.g. recall or recall-per-minute) or marked explicitly as "no data" (for cost) — never silently dropped. **Every label must be fully legible with zero overlap**, including when multiple runs tie on the same value or share a coordinate (e.g. the four zero_output runs all sitting at (0,0), or the four runs tied at 97.87% recall). Use the `adjustText` library (`pip install adjustText`, then `from adjustText import adjust_text`) to auto-resolve collisions with thin leader lines back to each point/bar — do not hand-place 12 labels and hope, and do not skip labeling a point just because it's crowded. If two+ points share the exact same coordinate, add a small deterministic jitter (a few percent of the axis range) so adjustText has room to separate their labels, while keeping the marker itself visually anchored to the true value with a leader line.

Input file: `{{input_file}}` (default `/app/assets/evaluation_matrix.csv`; if that path is absent, use the single CSV under `/app/assets/` — files uploaded through the API are stored as `<run_id>.NN.csv`) — columns: `agent, model, status, gold_total, num_found, num_missing, recall_pct, num_extra_entries, precision_pct, title_accuracy_pct, url_accuracy_pct, status_accuracy_pct, enrollment_accuracy_pct, study_type_accuracy_pct, start_date_accuracy_pct, overall_field_accuracy_pct, cost_usd, total_tokens, duration_seconds, notes`. `status` is `scored` (8 rows) or `zero_output` (4 rows, all N/A for accuracy fields).

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `{{results_dir}}`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `{{results_dir}}/charts/recall_vs_field_accuracy.png` | Scatter, **all 12 runs**: x=recall_pct, y=overall_field_accuracy_pct. The 4 zero_output runs plot at (0, 0) using the critical-red failure marker (field accuracy is genuinely undefined when nothing was found, but 0,0 is the correct visual home for "found nothing, scored nothing" on this axis pair) — every one of the 4 must still get its own visible, non-overlapping label. The "which model is actually best" quadrant view. |
| `{{results_dir}}/charts/recall_vs_runtime.png` | Scatter, **all 12 runs**: x=duration_seconds (log scale), y=recall_pct. Failed/zero-output runs included as a distinct marker. The speed-vs-completeness trade-off. |
| `{{results_dir}}/charts/cost_per_found_study.png` | Bar chart, **all 12 runs** on the x-axis (one bar-slot per agent+model combination, same order as the other charts). The 4 runs with real `cost_usd` data get a real bar (y = cost_usd / num_found, dollars per correctly-found study). The 8 runs with no cost tracking (all opencode runs, plus any zero_output claude-code run lacking cost) get an explicit zero-height slot with an "no cost data" label sitting above the baseline — do NOT simply omit them from the chart, the point is every combination has a visible slot even when the honest answer is "unknown." Sort the 4 real bars ascending; place the "no data" slots after them, grouped and clearly separated. |
| `{{results_dir}}/charts/agent_reliability_comparison.png` | Grouped bar: claude-code vs opencode, 3 grouped metrics — success rate (scored / attempted for that agent), mean recall (scored runs only), mean field accuracy (scored runs only). The "which agent should I even use" view. (This chart is aggregate-level by design, not per-run — it does not need all 12 individual combinations, since the two agent bars already summarize all 13 attempts between them.) |
| `{{results_dir}}/charts/recall_per_minute.png` | Bar chart, **all 12 runs**: recall_pct / (duration_seconds / 60) — how fast each run reaches its recall level. Zero-output runs correctly compute to 0 (0% recall ÷ any runtime = 0) and appear as a visible zero-height bar with a label, not a gap. Sorted descending. |
| `{{results_dir}}/chart_data.json` | The exact derived numbers behind every chart (so results are auditable without re-deriving from the raw matrix) |
| `{{results_dir}}/summary.md` | One paragraph per chart: what it shows, and the one-sentence takeaway a user should draw from it |
| `{{results_dir}}/validation_report.json` | Structured validation results with stages, results, and overall_passed |

If you finish your analysis but have not written all files, go back and write them before stopping.

---

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|------------------|---------|-------------|
| Results directory | `{{results_dir}}` | `/app/results` (Jetty) / `./results` (local) | Output directory for all results |
| Evaluation matrix | `{{input_file}}` | `/app/assets/evaluation_matrix.csv` (Jetty) | Path to the 20-column evaluation matrix CSV (one row per agent+model combination). Uploaded files land in `/app/assets/` |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| pandas | Python package | Yes | CSV loading and aggregation |
| matplotlib | Python package | Yes | Chart rendering |
| adjustText | Python package | Yes | Automatic non-overlapping label placement with leader lines |

---

## Step 1: Environment Setup

```bash
pip install pandas matplotlib adjustText
mkdir -p {{results_dir}}/charts
```

---

## Step 2: Design System — Use These Exact Values (Do Not Substitute)

This is a validated, colorblind-safe palette. Use it exactly — do not pick your own colors, do not use a matplotlib default cycle, do not use a rainbow/jet colormap.

**Chart surface & ink:**
- Figure/axes background: `#fcfcfb`
- Primary text/labels: `#0b0b0b`
- Secondary/muted text (axis ticks, captions): `#52514e`
- Gridlines (hairline, low-contrast, horizontal only where used, never both axes): `#e1e0d9`
- Axis baseline: `#c3c2b7`

**Categorical (identity — use for the two agents, in this fixed order, never swapped or reused for anything else):**
- `claude-code` → blue `#2a78d6`
- `opencode` → orange `#eb6834`

**Status (reserved — never use these for agent identity, only for outcome/state):**
- Failure / zero-output marker: critical red `#d03b3b`
- Best-in-class highlight (e.g. the single 100% recall point), if you choose to call one out: good green `#0ca30c`

**Non-negotiables:**
- One axis per chart. Never a dual y-axis (two different scales sharing one plot). If two measures need comparing, use two separate charts or an indexed/normalized single axis — never `twinx()`.
- Never a pie or 3D chart.
- Legend present on every chart with 2+ series/colors; a single-series chart (like the cost bar) needs no legend box, its title and axis label carry that.
- On the per-run charts (`recall_vs_field_accuracy.png`, `recall_vs_runtime.png`, `cost_per_found_study.png`, `recall_per_minute.png`), label EVERY one of the 12 combinations with its agent/model name (short form, e.g. "oc/kimi-k2" or "cc/gpt-5.6-sol" is fine) — this overrides the usual "label only what matters" rule because the whole point of this re-run is full coverage. Use `adjustText` so all 12 labels stay legible. On `agent_reliability_comparison.png` (the one aggregate chart), label bars normally — value labels on each of the 6 bars is fine since there's no crowding risk there.
- Thin lines (~2px), markers no smaller than ~8px, bars with a small gap between them (not touching), rounded bar corners if easy in matplotlib (e.g. via `patches.FancyBboxPatch` or simply leave square if that adds too much complexity — square corners are an acceptable fallback, do not spend excessive time on this).
- `dpi=180` minimum so PNGs are crisp at normal viewing size. Figure size roughly 9x6 inches per chart unless the content needs more room.

---

## Step 3: Compute Derived Data

Write and run a Python script that:

1. Loads `{{input_file}}` with pandas — all 12 rows.
2. Computes, per row (all 12, not just scored): `cost_per_found = cost_usd / num_found` where both are available and `num_found > 0`, else `None`/NaN (flag as "no data" rather than computing a misleading 0 or infinity). `recall_per_minute = recall_pct / (duration_seconds / 60)` — this is well-defined for all 12 rows including zero_output (recall_pct is 0, so the result is a real 0, not missing).
3. Computes agent-level aggregates across ALL attempted runs (both `scored` and `zero_output`) for `agent_reliability_comparison.png`:
   - `success_rate_pct` = (count of `status == 'scored'` for that agent) / (count of all rows for that agent) × 100
   - `mean_recall_pct` = mean of `recall_pct` over that agent's `scored` rows only
   - `mean_field_accuracy_pct` = mean of `overall_field_accuracy_pct` over that agent's `scored` rows only
4. Writes every computed number into `chart_data.json`, structured per chart (one top-level key per chart file, containing the exact x/y/label values plotted).

---

## Step 4: Render the 5 Charts

Build each chart from Step 3's computed data using matplotlib and the exact palette from Step 2. For `recall_vs_field_accuracy.png` and `recall_vs_runtime.png`, color each point by its `agent` value using the two fixed hues; for the runtime chart, additionally distinguish `zero_output` rows with a different marker shape (e.g. an X or open circle) rather than a third color, and label them with their model name plus "failed" so the failure is legible without relying on color alone. For `cost_per_found_study.png` and `recall_per_minute.png`, a single hue (blue, `#2a78d6`) is fine since there's one series; you may tint the corrupted-data run (claude-code/gpt-5.6-luna, if it appears — check `notes`/known corruption) with the critical red bar instead, with a small annotation, since a low dollar-per-study number there is misleading (the data was wrong, not cheap-and-good).

Save each as its own PNG under `{{results_dir}}/charts/`.

### ⚠️ A prior attempt at this exact runbook shipped `recall_vs_field_accuracy.png` and `recall_vs_runtime.png` with labels literally printed on top of each other — `adjustText` was called but its output was never checked. Do not repeat that. For these two scatter charts specifically, follow this exact procedure, in order:

1. **Use a large figure**: `figsize=(15, 10)`, `dpi=180`.
2. **Jitter exact-duplicate coordinates before plotting**, deterministically (fixed seed, so re-runs are stable) — and **only** exact duplicates, by at most ~1.5% of the axis range, **clamped inside the data bounds** (a recall or accuracy marker must never be drawn above 100% or below 0%; on a log axis never below the smallest real value): the 4 `zero_output` rows on `recall_vs_field_accuracy.png` all sit at the identical point (0, 0) — perturb each by a few percent of the axis range in a small spread pattern (e.g. a tiny arc or grid: `(0,0), (1.5,0.5), (0,1.5), (1.5,1.5)`-style offsets) so `adjustText` has distinct starting positions to work from. Draw a thin gray leader line (`plt.plot` or `ax.annotate` with `arrowprops`) from each jittered marker back to a small shared marker cluster at the true (0,0), OR simply draw all 4 markers at small deterministic offsets around (0,0) — either is fine, the requirement is that all 4 are visibly distinct dots with their own clear label, not one dot with 4 labels stacked on it.
3. **Call `adjust_text` with strong separation**, not defaults:
   ```python
   from adjustText import adjust_text
   texts = [ax.text(x, y, label, fontsize=9) for x, y, label in points]
   adjust_text(
       texts, x=xs, y=ys, ax=ax,
       arrowprops=dict(arrowstyle='-', color='#898781', lw=0.75),
       expand_points=(2.2, 2.2), expand_text=(1.3, 1.3),
       force_points=(0.8, 0.8), force_text=(0.6, 0.6),
       iter_lim=500,
   )
   ```
4. **Programmatically verify zero overlaps AND label locality before accepting the render** — do not trust step 3 blindly. A label that adjustText has pushed halfway across the chart with a long leader line is not legible even though it no longer overlaps anything, so both gates must pass:
   ```python
   fig.canvas.draw()
   renderer = fig.canvas.get_renderer()
   boxes = [t.get_window_extent(renderer=renderer) for t in texts]
   overlaps = [(i, j) for i in range(len(boxes)) for j in range(i+1, len(boxes)) if boxes[i].overlaps(boxes[j])]
   assert not overlaps, f"{len(overlaps)} label pairs still overlap: {overlaps}"
   # Locality gate: every label must stay within 12% of the axes width/height of its own marker
   ax_bbox = ax.get_window_extent(renderer=renderer)
   far = []
   for t, (x, y) in zip(texts, zip(xs, ys)):
       px, py = ax.transData.transform((x, y))
       tb = t.get_window_extent(renderer=renderer)
       dx = min(abs(tb.x0 - px), abs(tb.x1 - px)) if not (tb.x0 <= px <= tb.x1) else 0
       dy = min(abs(tb.y0 - py), abs(tb.y1 - py)) if not (tb.y0 <= py <= tb.y1) else 0
       if dx > 0.12 * ax_bbox.width or dy > 0.12 * ax_bbox.height:
           far.append(t.get_text())
   assert not far, f"labels too far from their markers: {far}"
   ```
5. **If either assertion fails**, do not keep pushing labels farther away. First retry once with a larger figure and stronger `expand_*`/`force_*` (2 attempts total for the plain layout, per Step 6). If a **dense cluster** is the cause — 4 or more points inside any 10% × 10% box of the axes, which is normal when several strong models all score 95–100% — switch to the **inset-zoom layout**: draw the full chart with the cluster's points unlabeled, add `ax.inset_axes` covering roughly 45% of the figure in the empty region of the plot, zoom it to the cluster's bounding box with a little padding, replot and label the cluster's points inside the inset (running the same adjustText + overlap + locality gates on the inset), and mark the zoomed region on the main axes with `ax.indicate_inset_zoom`. Points outside the cluster keep their normal labels on the main axes. If even the inset cannot separate two genuinely coincident points, fall back to numbered circular markers (①②③④) for just those points with a small reference legend box listing "① = agent/model" pairs in empty chart space.
6. Only write the PNG file after the overlap assertion in step 4 passes (or the numbered-marker fallback is used).

---

## Step 5: Evaluate Outputs

| Status | Criteria |
|--------|----------|
| `PASS` | All 5 PNGs exist, are non-trivial in size (>15KB), use the specified palette, have a legend where 2+ series are present, no chart uses a dual y-axis or 3D/pie form, every per-run chart shows all 12 combinations with a visible label each, no two labels overlap, every label sits within 12% of the axes size of its own marker (or the cluster is shown in an inset zoom), and no marker is drawn outside the data bounds |
| `PARTIAL` | Charts render, all 12 combinations are represented, but one used a fallback (e.g. square bar corners instead of rounded) — note the deviation in `summary.md` |
| `FAIL` | Any chart is missing, blank, uses an unapproved color, uses a dual-axis/pie/3D form, is missing one or more of the 12 combinations from a per-run chart, or has any overlapping label |

---

## Step 6: Iterate on Errors (max 3 rounds)

If any chart fails Step 5's criteria, fix the specific issue (palette substitution, missing legend, dual-axis violation, blank render, missing combination, overlapping label) and re-run. After each render, programmatically count that exactly 12 labels/annotations were added to each per-run chart (assert this in code, don't eyeball it) before moving on. Repeat up to 3 times, then note any remaining deviation honestly in `summary.md` rather than silently shipping a broken chart.

### Common Fixes

| Issue | Fix |
|-------|-----|
| Log-scale x-axis on `recall_vs_runtime.png` makes the near-instant failures (15–31s) crowd together | Expected — let `adjustText` fan the labels out with leader lines rather than trying to spread the points themselves artificially |
| `cost_usd` is null for 8 of 12 rows (all opencode runs + some zero-output runs) | Still give each of the 8 a bar-slot in `cost_per_found_study.png` with a "no cost data" label above the baseline — do not omit the slot, only the bar height is missing |
| Matplotlib default color cycle sneaks in when you forget to set `color=` explicitly on every artist | Explicitly pass `color=` on every bar/scatter call — never rely on the default cycle |
| Multiple runs share the exact same (recall, field_accuracy) or (recall, duration) coordinate, so their markers overlap | Add a small deterministic jitter (2–3% of axis range, seeded so it's reproducible) purely for label anchoring — draw a thin leader line from the jittered label back to the true, unjittered marker position |
| `adjustText` labels still collide after a default call | Increase `expand_points`/`expand_text` and iteration count, or pass `arrowprops=dict(arrowstyle='-', color='#898781', lw=0.75)` for visible leader lines; re-render and re-check — do not ship a chart with any two labels overlapping |
| Labels end up far from their points with long leader lines fanning across the chart (adjustText "solved" a dense cluster by exiling the labels) | This fails the locality gate. Use the inset-zoom layout from Step 4.5 for the cluster instead of pushing labels farther away |
| Jittered markers appear above 100% or below 0% | Jitter must be clamped inside the data bounds — reduce the offset and clip; never let a jitter change what value a reader would read off the axis |

---

## Step 7: Write Executive Summary

Write `{{results_dir}}/summary.md` with one clearly-labeled section per chart (matching the 5 filenames), each containing: what the chart shows, and a one-sentence takeaway. Follow with a short "Which chart should I look at?" guide for a user who only has time for one.

---

## Step 8: Write Validation Report

Write `{{results_dir}}/validation_report.json`:

```json
{
  "version": "1.0.0",
  "run_date": "2026-01-01T00:00:00Z",
  "parameters": { "input_file": "<actual path used>" },
  "stages": [
    { "name": "setup", "passed": true, "message": "Environment ready" },
    { "name": "compute", "passed": true, "message": "Derived data computed for all 5 charts" },
    { "name": "render", "passed": true, "message": "All 5 charts rendered" },
    { "name": "evaluation", "passed": true, "message": "All charts pass palette/form checks" },
    { "name": "report_generation", "passed": true, "message": "All output files written" }
  ],
  "results": { "pass": 0, "partial": 0, "fail": 0 },
  "overall_passed": true,
  "output_files": [
    "{{results_dir}}/charts/recall_vs_field_accuracy.png",
    "{{results_dir}}/charts/recall_vs_runtime.png",
    "{{results_dir}}/charts/cost_per_found_study.png",
    "{{results_dir}}/charts/agent_reliability_comparison.png",
    "{{results_dir}}/charts/recall_per_minute.png",
    "{{results_dir}}/chart_data.json",
    "{{results_dir}}/summary.md",
    "{{results_dir}}/validation_report.json"
  ]
}
```

---

## Step 9: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="{{results_dir}}"
for f in "$RESULTS_DIR/charts/recall_vs_field_accuracy.png" "$RESULTS_DIR/charts/recall_vs_runtime.png" "$RESULTS_DIR/charts/cost_per_found_study.png" "$RESULTS_DIR/charts/agent_reliability_comparison.png" "$RESULTS_DIR/charts/recall_per_minute.png" "$RESULTS_DIR/chart_data.json" "$RESULTS_DIR/summary.md" "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

### Checklist

- [ ] All 5 PNGs exist, are non-blank, and use only the specified palette
- [ ] No dual-axis, pie, or 3D chart anywhere
- [ ] Every 2+ series chart has a legend; failure points are distinguished by marker shape, not color alone
- [ ] `recall_vs_field_accuracy.png`, `recall_vs_runtime.png`, `cost_per_found_study.png`, and `recall_per_minute.png` each show and label all 12 agent+model combinations — none silently dropped
- [ ] No two labels overlap on any chart, including where points/bars share a coordinate (verified by eye on the rendered PNG, not just by running adjustText and assuming it worked)
- [ ] `chart_data.json` contains the exact numbers behind every chart
- [ ] `summary.md` explains each chart's takeaway in plain language, plus a "which chart to look at" guide
- [ ] Verification script printed PASS for all files

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- This dataset only has 2 agents and known failure/corruption cases — resist the urge to invent a third categorical color or a rainbow colormap "for variety." Two fixed hues plus a reserved status red is the whole palette.
- The most informative charts here are the ones that reframe the raw numbers into a decision-relevant metric (cost per correct result, recall per minute) rather than just re-plotting columns as-is.
