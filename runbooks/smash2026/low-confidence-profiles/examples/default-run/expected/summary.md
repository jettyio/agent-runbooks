# SMASH 2026 Paper #9 — Run Summary

**Dataset**: Synthetic 100,000-patient MIMIC-like cohort (30-day readmission)
**Removed subgroup**: Patients under 50 (age<50) from training only

**Population verdict**: No harmful covariate shift detected (Detectron median p = 0.19)

**Flagged profiles**: 2 of 5 tested profiles (covering 47% of patients):
- `hemoglobin ≤ 11.55 & creatinine ≤ 1.695` — 31% of patients, AUC 0.69 → 0.64, mean age 68.9 → 61.1 (HCS detected, p = 0.0095)
- `hemoglobin ≤ 13.05 & hemoglobin > 11.55 & creatinine ≤ 1.075` — 16% of patients, AUC 0.72 → 0.70 (HCS detected, p = 0.0248)

**Three-shift contrast**: Age shift localized (population no HCS; profiles flagged). Sex shift broad (population HCS p = 1.06e-28; all 7 profiles flagged, 97% of patients). Race shift broad (population HCS p = 0.000352; 5/7 profiles flagged, 79% of patients). Mirrors the paper's finding exactly.

**Headline**: Age<50 shift missed at population level but found in 2 profiles covering 47% of patients; worst profile (31%) AUC 0.69 → 0.64, consistent with paper's MIMIC-IV result (AUC endpoint 0.64).
