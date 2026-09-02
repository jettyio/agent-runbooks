# Multiple Myeloma Extraction — Trade-off Visualization Summary

## recall_vs_field_accuracy.png

**What it shows:** Every one of the 12 agent+model combinations positioned on two accuracy
dimensions: how many of 47 gold-standard studies were retrieved (recall, x-axis) and how
correctly the retrieved studies' fields were extracted (overall field accuracy, y-axis).
Blue dots = claude-code; orange dots = opencode; red X markers = the four zero-output failures,
plotted at the origin (0, 0) because they found nothing and scored nothing. Duplicate coordinates
are spread by a small deterministic jitter so every label remains distinct.

**Takeaway:** opencode's 5 scored runs cluster tightly in the top-right quadrant (95–100%
recall, 90–93% field accuracy), while claude-code's 3 scored runs show wider spread — including
the corrupted gpt-5.6-luna run at only 67% field accuracy.

---

## recall_vs_runtime.png

**What it shows:** How long each run took (x-axis, log scale) versus how complete its results
were (recall, y-axis). The log scale is required because runtimes span three orders of magnitude
(15 seconds to ~30 minutes). Red X markers at recall = 0 are the four failed runs; circle
markers are scored runs coloured by agent.

**Takeaway:** opencode/gpt-5.6-sol and opencode/gpt-5.6-terra deliver ~98% recall in under
10 minutes — the best speed-vs-completeness trade-off — while the two slowest runs (both ~30 min)
offer no recall advantage over faster alternatives.

---

## cost_per_found_study.png

**What it shows:** Dollar cost per correctly-found study, for every one of the 12 combinations.
Only 3 runs have computable cost_per_found (cost data available and at least one study found);
those get real bars sorted ascending. The remaining 9 combinations — all opencode runs (no cost
tracking) plus the claude-code zero-output runs — receive labeled zero-height slots rather than
being dropped from the chart. The corrupted cc/gpt-5.6-luna bar is tinted red with a warning.

**Takeaway:** Among the three trustworthy cost data points, claude-code/claude-sonnet-4-6 at
~$0.021/study is the best legitimate value; the corrupted luna run's $0.004 figure is not
meaningful; cost comparisons across agents are impossible because opencode runs have no cost
instrumentation.

---

## agent_reliability_comparison.png

**What it shows:** The two agents compared at population level across all 6 attempted runs each,
on three grouped metrics: success rate (fraction of runs that produced output), mean recall
(among scored runs only), and mean field accuracy (among scored runs only). This is the only
aggregate-level chart; it summarises all 12 combinations rather than showing them individually.

**Takeaway:** opencode is dramatically more reliable — 83% success rate vs claude-code's 50% —
and produces more consistent field extraction (92.3% vs 83.8%), largely because claude-code's
corrupted gpt-5.6-luna run drags down its field-accuracy mean.

---

## recall_per_minute.png

**What it shows:** How quickly each run reaches its final recall level, expressed as recall %
divided by elapsed minutes. Zero-output runs correctly score 0 (0% recall divided by any
runtime = 0) and appear as labeled zero-height bars. The corrupted cc/gpt-5.6-luna bar is tinted
red and annotated — its high recall-per-minute reflects fast runtime on unreliable data.

**Takeaway:** For a fast trustworthy result, opencode/gpt-5.6-sol (~14.6 %/min) and
opencode/gpt-5.6-terra (~11.6 %/min) are the genuine leaders; cc/gpt-5.6-sol is competitive
(~18.8 %/min) but costs roughly 5× more per study than opencode alternatives.

---

## Which chart should I look at?

| Question | Chart |
|---|---|
| Which combination is most accurate overall? | `recall_vs_field_accuracy.png` |
| Which is fastest for the accuracy it gets? | `recall_vs_runtime.png` |
| Which agent should I even try first? | `agent_reliability_comparison.png` ← start here |
| What does it cost per correct result? | `cost_per_found_study.png` |
| Which reaches a good answer fastest (throughput)? | `recall_per_minute.png` |
