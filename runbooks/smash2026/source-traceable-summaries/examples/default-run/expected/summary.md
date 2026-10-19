Settings: brief prompt, Claude Haiku (small) summarizer and judge, all 6 noise types active, style comparison on, noise ladder on.

Main run: judge 6/10, blocked by 2 gates — contradiction (HbA1c 7.2% vs 8.1% silently resolved) and intended_use (no verification statement). Layer-2 metrics look perfect: 100% gold recall, 100% supported claims, all 10 gold items covered — the gates caught what recall could not.

Style comparison: only the careful prompt passed all gates (7/10, released). Brief (6/10) and naive (3/10) were both blocked; naive also failed med_bounds (lisinopril stop date missing).

Noise ladder: intended_use gate fails on every run (brief prompt never emits a verification statement). Contradiction gate first fires at step 3 (conflicting labs) — the judge simultaneously scored 9/10, the sharpest divergence. 1 of 9 variants scored >=7/10 yet failed a clinical gate.

Key finding: 100% extraction accuracy and citation coverage do not prevent a release-blocking gate failure. The judge-gate agreement across all 9 variants was 56%.
