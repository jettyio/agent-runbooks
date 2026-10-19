# Gap Audit — Diabetes 130-US, Age (10–29 vs 60+)

**Dataset/comparison:** Diabetes 130-US Hospitals, youngest (10–29) vs oldest (60+), 30-day readmission outcome.

**Sensitivity gap:** +0.120 [−0.057, +0.235] — CI spans zero (paper reports +0.104 [−0.070, +0.232]; results agree closely).

**PPV gap:** raw +0.099 → standardized to pooled prevalence (π = 0.114) +0.104 — gap grows by ~5%, no sign flip.

**Threshold range:** sensitivity gap spans −0.080 to +0.245 across τ ∈ [0.02, 0.80]; reverses sign below the training-prevalence threshold (τ = 0.117).

**Multiverse sign counts:** 19 of 36 specs give a negative gap, 13 a positive one (spanning −0.237 to +0.148).

**Headline:** The +0.120 youngest−oldest sensitivity gap reverses in 19 of 36 analytic specifications, and the 95% CI already spans zero [−0.057, +0.235].
