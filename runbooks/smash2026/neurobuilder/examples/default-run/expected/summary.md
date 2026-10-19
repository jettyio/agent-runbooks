## Mini NeuroBuilder — SMASH 2026 #17 run summary

**Settings:** messiness=1, 12 BIDS subjects (24 recordings), 10 clinical patients (26 recordings), annotations=present, window=5 s, seed=7, max_repairs=2, 3 repeated runs.

**Scorecard:** 50/50 recordings retained · 374/374 metadata values matched · 50/50 provenance verified · 0 decoys indexed · 224/224 native events (F1 = 1.0000) · 0 fabricated events · 1074/1074 five-second windows · 2 ineligible_duration recordings · status **partial_pass** (conflicts present for researcher review).

**Conflicts:** 7/7 planted conflicts surfaced — 2 sampling-rate mismatches, 2 missing events files, 1 duplicate subject row, 1 events past recording end, 1 implausible unit. Zero spurious flags. Trusting the mismatched sidecar sampling rates unchecked would have produced 23 wrong-sized windows.

**Repairs:** 0 — the Inspector's first proposal indexed all 50 recordings correctly on the first attempt.

**Repeats:** 3/3 completed at temperature 1.0; all 3 passed with an identical Events hash.

**Fabrication trap:** LLM-only baseline emitted 0 events for 6 unannotated clinical recordings (the model declined without annotation data); gated pipeline also emitted 0 clinical events.

**LLM calls:** 11 total (8 main run including 3 repeat × 1 each + 1 fabrication trap + Planner).
