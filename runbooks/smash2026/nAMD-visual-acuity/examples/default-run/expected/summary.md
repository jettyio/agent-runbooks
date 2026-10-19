# SMASH 2026 Paper #5 — nAMD Visual Acuity Prognosis (Simulated)

**Patient**: BCVA 50 letters, CST 380 µm, SRF+, IRF+, PED−, VMT−

**Predicted chance of gaining ≥10 ETDRS letters at 1 year**: 51% (cohort base rate 25%)

**Top glass-box contributions**: low BCVA (+0.68 logits, room to gain), SRF present (+0.36), CST 380 µm (+0.23)

**Worst automated misread**: SRF read as absent → predicted chance drops to 33% (−18 pp)

**CV AUC (5-fold)**: EBM automated 0.74 ± 0.04 | EBM measured 0.75 ± 0.04 | Gradient boosting 0.72 ± 0.04 | BCVA alone 0.72 ± 0.03
Paper reports EBM AUC 0.77 ± 0.07; simulated result is within one SD.

**Key finding**: the glass-box EBM recovers the simulation's top features (BCVA, SRF, CST) and adds modest value over a BCVA-only baseline; SRF misdetection is the most consequential automated error for this patient profile.

**SIMULATED COHORT — not for clinical use.**
