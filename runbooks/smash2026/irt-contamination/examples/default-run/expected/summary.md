# Contamination Audit Lab — SMASH 2026 Paper #20 Run Summary

**Settings:** contamination=0.97, model_ability=0.3, memorization_boost=1.0,
1200 member / 1200 unseen / 3600 calibration items, 102-model population, seed=7.

| Detector       | AUROC before | AUROC after evasion |
|---------------|-------------|---------------------|
| Min-K%++      | 0.96        | 0.50 (−0.46)        |
| Min-K%        | 0.97        | 0.51 (−0.46)        |
| LOSS          | 1.00        | 0.52 (−0.48)        |
| ZLIB          | 1.00        | 0.52 (−0.48)        |
| IRT-residual  | 0.73        | 0.73 (Δ 0.00)       |

**IRT control (uncontaminated):** AUROC 0.484, p = 0.890 (not significant).
**IRT contaminated:** AUROC 0.73, p = 0.002 (significant).
**Answers changed by evasion:** 0 of 2,400.

**Sandbagging cost:** adversary must give back 70% of contamination gains, losing 13.1 benchmark
accuracy points and retaining only 30% of the original score inflation, to push IRT to ~chance.

**Headline:** Confidence detectors collapse from 1.00 to 0.52 AUROC after evasion, while the IRT residual holds unchanged at 0.73.
