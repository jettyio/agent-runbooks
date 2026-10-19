Settings: task AMD preset, left eye at inference, prevalence 0.06, inter-eye correlation 0.6, alpha 0.03, noise L/R 2.0/2.0, 3,500 patients, 10 cohorts, seed 0. Toy simulated paired-eye features, not ODIR images.
Detailed split, left eye: AUROC baseline 0.711 -> one-eye student 0.702, difference -0.010 [95% CI -0.033, +0.012]. Two-eye teacher 0.729.
Across 10 cohorts: mean Δ AUROC +0.024 (SD 0.021), positive in 8 of 10.
Threshold trade-off on the detailed split: FPR 0.027 -> 0.047, precision 0.357 -> 0.244; the sign flips across cohorts (Δ precision -0.113 to +0.158).
Sweep (extension): Δ AUROC peaks at +0.049 near inter-eye correlation 0.4 (alpha 0.1) and is +0.014 at 0.95.
Headline: across 10 cohorts the one-eye student gained +0.024 AUROC on average, but this card's split shows -0.010.
