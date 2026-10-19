## TRACE Simulator — Run Summary

**Settings:** codebook_size=48, prior_strength=5, rho=0.5, region_weight=0.5, steer_strength=1.0,
hard_negative_share=0.3, harm_onset=0.4, seed=3.
Sequence: `benign:20, caution:8, benign:6, harmful:14, benign:6` (54 tokens).

**Detection:** TRACE streaming F1 0.959, FPR 1.5% (hard-neg FPR 4.8%).
DiffMean streaming F1 0.606, FPR 32.8% (hard-neg FPR 57.1%). Threshold 0.550, median stop at 50.6% through harmful responses.

**Steering (λ=1.0):** ASR 0.94 → 0.18 (TRACE), ΔRef +0.00.
Global direction: ASR → 0.00, but ΔRef +0.46 (disrupts 46% of safe responses).

**Your sequence:** stopped at token 39 (harmful onset at token 35); 33 tokens edited.

**Headline:** TRACE streaming F1 0.96 vs DiffMean 0.61; ASR cut from 0.94 to 0.18 with ΔRef +0.00,
while the global direction reaches ASR 0.00 but causes ΔRef +0.46.
All numbers are from a simulated activation world — not Qwen3-8B or the paper's benchmarks.
