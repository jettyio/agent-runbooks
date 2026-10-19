# SMASH 2026 · Paper #2 · Run Summary

**Classes and support:** No DR (3), Mild (1), Moderate (1), Severe (0), Proliferative (0) — default MESSIDOR-like setup.

**Headline:** Ungated residual transfer (VLM ranking or ontology ranking) made missing-class recall worse in 46–50% of support draws; the evidence gate reduced that to 16% and added +2.37 missing-class recall points [+1.72, +2.95].

**NTR ungated → gated:** VLM 50% → gated 16%; Ont 46% → gated 16%. Gated: 42 of 50 draws improved, 0 unchanged.

**Gates per missing class:** Severe=0.514±0.019 (d_min=1, q_vlm=0.402); Proliferative=0.215±0.008 (d_min=2, q_vlm=0.137). Moderate was the top source in all 50 seeds for both classes.

**Beta sweep:** Ungated NTR stays below 20% for β ≤ 0.3 but reaches 50% at β=1. Gated at β=1 (NTR=16%, ΔMCR=+2.37) outperforms ungated at any single β value, confirming the gate adds value beyond a fixed step size reduction.

**Synthetic world caveat:** Absolute accuracies differ from MESSIDOR; supported-class recall does not drop (ΔSCR=+0.97 vs paper −1.20) because the synthetic geometry lacks the inductive bias present in real VLM features.
