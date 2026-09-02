# Hiring Demographics Audit — Compliance Report

**Scope:** Healthcare hiring dataset, 900 candidates across 6 job roles.
**Methodology:** Four-fifths (80%) adverse-impact rule, cross-checked with two independent statistical significance tests.
**Status:** Synthetic dataset, methodology audit — not a legal/regulatory determination.

---

## 1. Methodology

### 1.1 Dataset

- **Source:** `/app/assets/c31e02a8.00.csv` — 900 candidate records, 1 row per candidate.
- **Job roles (`role_applied`):** Registered Nurse (205), Lab Technician (186), Radiology Technologist (150), Medical Coder (136), Clinic Administrator (135), Pharmacist (88).
- **Outcome (`hired`):** encoded as `Yes`/`No` in the source file, coerced to boolean. Overall hire rate: 334/900 = **37.1%**.
- **Row handling:** all 900 rows had a valid `role_applied` and `hired` value — **0 rows dropped**. No demographic field (`gender`, `race_ethnicity`, `disability_status`, `veteran_status`, `age`) had missing values, so no candidate needed to be assigned a "declined to state" bucket. The only missingness in the dataset is in `certifications` (167 blanks, meaning "no certifications listed") — a free-text field not used in the disparity calculation.
- **Age bracket derivation:** `age` (raw integer, range 22–63) was bucketed into four groups used consistently throughout this report and the metrics table: **`<30`, `30-39`, `40-49`, `50+`**.

### 1.2 Disparity metrics

For every (job role × demographic dimension × group) cell, and for a role-agnostic rollup (`job_role = ALL_ROLES`) per dimension, we computed:

- **Selection rate** = hires / candidates in that cell.
- **Reference group** = the group with the highest selection rate, restricted to groups with **candidate_count ≥ 30** in that cell. Restricting eligibility to adequately-sized groups is a deliberate choice: without it, a group of 2–3 candidates hired at 100% could become the yardstick that every other group is measured against, manufacturing spurious flags. If no group in a cell reaches 30, the highest-rate group overall is used instead and every row in that cell is marked `low_confidence = true`. Ties are broken deterministically (larger `candidate_count`, then alphabetically first) and marked with `reference_group_tie_broken = true` where this occurred.
- **Four-fifths ratio** = group selection rate ÷ reference group selection rate. Ratios below **0.8** are `flagged`.
- **Statistical significance** — for every cell where both the group and its reference group have ≥ 30 candidates, we ran **both** a two-sided Fisher's exact test and a Pearson chi-square test with Yates' continuity correction on the 2×2 [hired/not-hired] × [group/reference] table. A finding is only marked `statistically_significant = true` if **both** tests agree (p < 0.05). Cells below the size threshold are marked `low_confidence` and no significance test is reported for them, since neither test is reliable at that sample size.

### 1.3 Limitations

- The four-fifths rule is a widely used screening heuristic, not a legal determination of discrimination. A flagged ratio indicates a **statistical disparity worth investigating**, not proven bias.
- Many demographic groups (Non-binary gender, Native American, Middle Eastern, Multiracial race/ethnicity, disability status "Yes", veteran status "Yes") are small minorities in this dataset. Cells built on them are frequently `low_confidence` — directional only, not conclusive — and should not be treated as either "cleared" or "confirmed" findings.
- This is a synthetic dataset assembled for audit-methodology demonstration, not a real EEOC/OFCCP filing.

---

## 2. Findings by Job Role

*(Only flagged cells are shown per role; a role with no line items below had no ratio fall below 0.8 for any dimension. Full detail for every group in every role is in `disparity_metrics.csv`.)*

### Registered Nurse (n=205, overall hire rate 45.9%)
- **Age bracket 30-39** vs. reference **50+**: selection rate 22.7% vs. 48.3%, ratio **0.47** — **flagged, statistically significant** (Fisher p=0.018, chi²p=0.021).
- Race/ethnicity **Black** (n=31) vs. reference **Hispanic/Latino**: ratio 0.75 — flagged, not statistically significant (Fisher p=0.45, chi²p=0.56).
- Race/ethnicity **Multiracial** (n=11, low confidence): ratio 0.00 — 0 of 11 hired.
- Age bracket **<30** vs. **50+**: ratio 0.62 — flagged, not statistically significant (Fisher p=0.11, chi²p=0.13).

### Lab Technician (n=186, overall hire rate ~41%)
- Disability status **Yes** (n=18, low confidence): ratio 0.53 vs. **No**.
- Race/ethnicity **Multiracial** (n=14, low confidence): ratio 0.75 vs. **White**.
- Gender **Non-binary** (n=10, low confidence): ratio 0.71 vs. **Male**.
- Age bracket **50+** vs. **30-39**: ratio 0.62 — flagged, not statistically significant (Fisher p=0.08, chi²p=0.10).
- Age bracket **<30** vs. **30-39**: ratio 0.79 — flagged, not statistically significant.

### Radiology Technologist (n=150)
- Disability status **Yes** (n=18, low confidence): ratio 0.80 vs. **No** — borderline flag, directional only.

### Medical Coder (n=136)
- Race/ethnicity **Middle Eastern** (n=2, low confidence): ratio 0.00 — 0 of 2 hired.
- Race/ethnicity **Multiracial** (n=7, low confidence): ratio 0.00 — 0 of 7 hired.

### Clinic Administrator (n=135)
- Gender **Non-binary** (n=5, low confidence): ratio 0.71 vs. **Male**.

### Pharmacist (n=88 — smallest role, most cells low-confidence)
- Race/ethnicity **Black** (n=12, low confidence): ratio 0.25 vs. **Native American**.
- Race/ethnicity **Middle Eastern** (n=4, low confidence): ratio 0.375.
- Age bracket **<30** (n=20, low confidence): ratio 0.60.
- Age bracket **50+** (n=15, low confidence): ratio 0.67.
- Race/ethnicity **Hispanic/Latino** (n=22, low confidence): ratio 0.75.
- Race/ethnicity **Multiracial** (n=6, low confidence): ratio 0.75.
- Race/ethnicity **White** (n=21, low confidence): ratio 0.64.
- Gender **Non-binary** (n=4, low confidence): ratio 0.52.
- **Note:** Pharmacist is the smallest role (88 candidates); every group except the reference (Native American, n=24, itself below 30 — this entire cell falls back to `low_confidence=true` for every row) is under the 30-candidate threshold. None of the Pharmacist findings meet the bar for a statistical claim; more applicant volume is needed before drawing conclusions about this role.

---

## 3. Findings by Demographic Dimension (Cross-Role Rollup)

Rollup rows (`job_role = ALL_ROLES`) pool all 900 candidates per dimension, giving the best-powered view of where disparity concentrates:

| Dimension | Group | n | Selection rate | Reference | Ratio | Flagged | Fisher p | Chi² p | Sig. |
|---|---|---|---|---|---|---|---|---|---|
| gender | Female | 471 | 36.1% | Male | 0.95 | No | 0.622 | 0.630 | No |
| gender | Male | 401 | 37.9% | (ref) | 1.00 | No | — | — | No |
| gender | Non-binary | 28 | 42.9% | Male | 1.13 | No (low conf.) | — | — | — |
| race_ethnicity | Asian | 134 | 44.8% | (ref) | 1.00 | No | — | — | No |
| race_ethnicity | Black | 131 | 38.9% | Asian | 0.87 | No | 0.384 | 0.401 | No |
| race_ethnicity | **Hispanic/Latino** | 195 | 32.3% | Asian | **0.72** | **Yes** | **0.027** | **0.029** | **Yes** |
| race_ethnicity | Middle Eastern | 49 | 38.8% | Asian | 0.87 | No | 0.504 | 0.577 | No |
| race_ethnicity | **Multiracial** | 54 | 25.9% | Asian | **0.58** | **Yes** | **0.021** | **0.026** | **Yes** |
| race_ethnicity | Native American | 24 | 62.5% | Asian | 1.40 | No (low conf.) | — | — | — |
| race_ethnicity | White | 313 | 35.8% | Asian | 0.80 | Yes (borderline) | 0.089 | 0.092 | No |
| disability_status | No | 792 | 37.6% | (ref) | 1.00 | No | — | — | No |
| disability_status | Yes | 108 | 33.3% | No | 0.89 | No | 0.398 | 0.447 | No |
| veteran_status | No | 838 | 36.5% | Yes | 0.81 | No | 0.176 | 0.221 | No |
| veteran_status | Yes | 62 | 45.2% | (ref) | 1.00 | No | — | — | No |
| age_bracket | 30-39 | 260 | 35.8% | 40-49 | 0.84 | No | 0.134 | 0.138 | No |
| age_bracket | 40-49 | 222 | 42.8% | (ref) | 1.00 | No | — | — | No |
| age_bracket | 50+ | 192 | 35.4% | 40-49 | 0.83 | No | 0.131 | 0.152 | No |
| age_bracket | <30 | 226 | 34.5% | 40-49 | 0.81 | No | 0.081 | 0.089 | No |

**Takeaway:** `race_ethnicity` is the only dimension with well-powered (n≥30 on both sides), statistically significant flags in the cross-role rollup — **Hispanic/Latino** (ratio 0.72) and **Multiracial** (ratio 0.58) candidates are selected at meaningfully lower rates than the highest-selection reference group (Asian), and both survive both significance tests. Gender, disability status, veteran status, and age bracket show no statistically significant disparity at the rollup level; the only near-threshold rollup item (White, ratio 0.80) does not reach significance (p=0.089/0.092).

---

## 4. Flagged Items (all `flagged == true` rows, sorted by severity)

24 of 125 metric rows are flagged (four-fifths ratio < 0.8). Sorted by ratio ascending, ties broken by (statistically significant first, then non-low-confidence first):

| # | Job role | Dimension | Group | n | Selection rate | Reference | Ratio | Fisher p | Chi² p | Sig. | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Medical Coder | race_ethnicity | Middle Eastern | 2 | 0.0% | White | 0.00 | — | — | — | **Low** |
| 2 | Medical Coder | race_ethnicity | Multiracial | 7 | 0.0% | White | 0.00 | — | — | — | **Low** |
| 3 | Registered Nurse | race_ethnicity | Multiracial | 11 | 0.0% | Hispanic/Latino | 0.00 | — | — | — | **Low** |
| 4 | Pharmacist | race_ethnicity | Black | 12 | 16.7% | Native American | 0.25 | — | — | — | **Low** |
| 5 | Pharmacist | race_ethnicity | Middle Eastern | 4 | 25.0% | Native American | 0.375 | — | — | — | **Low** |
| 6 | Registered Nurse | age_bracket | 30-39 | 66 | 22.7% | 50+ | **0.47** | **0.018** | **0.021** | **Yes** | High |
| 7 | Pharmacist | gender | Non-binary | 4 | 25.0% | Female | 0.52 | — | — | — | **Low** |
| 8 | Lab Technician | disability_status | Yes | 18 | 22.2% | No | 0.53 | — | — | — | **Low** |
| 9 | ALL_ROLES | race_ethnicity | Multiracial | 54 | 25.9% | Asian | **0.58** | **0.021** | **0.026** | **Yes** | High |
| 10 | Pharmacist | age_bracket | <30 | 20 | 30.0% | 30-39 | 0.60 | — | — | — | **Low** |
| 11 | Lab Technician | age_bracket | 50+ | 84 | 29.8% | 30-39 | 0.62 | 0.079 | 0.101 | No | High |
| 12 | Registered Nurse | age_bracket | <30 | 57 | 29.8% | 50+ | 0.62 | 0.106 | 0.134 | No | High |
| 13 | Pharmacist | race_ethnicity | White | 21 | 42.9% | Native American | 0.64 | — | — | — | **Low** |
| 14 | Pharmacist | age_bracket | 50+ | 15 | 33.3% | 30-39 | 0.67 | — | — | — | **Low** |
| 15 | Lab Technician | gender | Non-binary | 10 | 30.0% | Male | 0.71 | — | — | — | **Low** |
| 16 | Clinic Administrator | gender | Non-binary | 5 | 20.0% | Male | 0.71 | — | — | — | **Low** |
| 17 | ALL_ROLES | race_ethnicity | Hispanic/Latino | 195 | 32.3% | Asian | **0.72** | **0.027** | **0.029** | **Yes** | High |
| 18 | Registered Nurse | race_ethnicity | Black | 31 | 29.0% | Hispanic/Latino | 0.75 | 0.447 | 0.556 | No | High |
| 19 | Pharmacist | race_ethnicity | Hispanic/Latino | 22 | 50.0% | Native American | 0.75 | — | — | — | **Low** |
| 20 | Pharmacist | race_ethnicity | Multiracial | 6 | 50.0% | Native American | 0.75 | — | — | — | **Low** |
| 21 | Lab Technician | race_ethnicity | Multiracial | 14 | 28.6% | White | 0.75 | — | — | — | **Low** |
| 22 | Lab Technician | age_bracket | <30 | 42 | 38.1% | 30-39 | 0.79 | 0.474 | 0.522 | No | High |
| 23 | ALL_ROLES | race_ethnicity | White | 313 | 35.8% | Asian | 0.80 | 0.089 | 0.092 | No | High |
| 24 | Radiology Technologist | disability_status | Yes | 18 | 33.3% | No | 0.80 | — | — | — | **Low** |

**Reading this table:** the ratio ranking alone is dominated by very small cells (rows 1–5, 7, 8, 10, 13–16, 19–21, 24 are all `low_confidence`, driven by groups with fewer than 30 candidates — several have single-digit sample sizes). Ratios of 0.00 for a 2- or 7-person group hired zero times are dramatic-looking but statistically unsupported. The rows that combine a low ratio **with** a large enough sample to run both significance tests, and where both tests agree at p<0.05, are the three that should draw primary attention: **row 6 (Registered Nurse, age 30-39), row 9 (Multiracial candidates, all roles), and row 17 (Hispanic/Latino candidates, all roles)**.

---

## 5. Recommendations

1. **Investigate further — Registered Nurse hiring by age bracket.** Candidates aged 30-39 applying for Registered Nurse are hired at less than half the rate (22.7%) of the 50+ reference group (48.3%), and this is statistically significant on both tests (Fisher p=0.018, chi² p=0.021). Recommend a manual review of the Registered Nurse screening/interview criteria and rubric to check for age-correlated proxies (e.g., years of experience weighting) that could produce this pattern, since years_experience is a CV field that correlates mechanically with age.
2. **Investigate further — race/ethnicity disparity for Hispanic/Latino and Multiracial candidates, all roles.** Both groups show statistically significant lower selection rates versus the Asian reference group at the cross-role level (Hispanic/Latino: 32.3% vs 44.8%, ratio 0.72, p=0.027/0.029; Multiracial: 25.9% vs 44.8%, ratio 0.58, p=0.021/0.026). Because this is a rollup finding, recommend checking whether the disparity is concentrated in specific roles (Registered Nurse and Medical Coder both show flagged, if less-powered, Multiracial-related cells) or is broad-based, and whether it persists after controlling for years_experience, education_level, or university_tier as a first-pass explanatory check before treating it as unexplained.
3. **Collect more data before concluding — Pharmacist role generally.** With only 88 total candidates and a Native American reference group of just 24, every Pharmacist finding in this audit is `low_confidence`. Recommend increasing the Pharmacist applicant pool (or pooling additional hiring cycles) before drawing any conclusion about disparity in this role — the eight flagged Pharmacist cells should not be acted on as-is.
4. **Collect more data before concluding — small demographic cells across all roles.** Non-binary gender, disability status "Yes", Native American and Middle Eastern race/ethnicity, and every age×role combination under 30 candidates are directional-only. Recommend targeted outreach or a longer observation window to grow these cells to the point where a four-fifths ratio and significance test are actionable, rather than either dismissing or acting on the current low-confidence readings.
5. **Review process, not investigate individually — White candidates, all-roles rollup.** The ratio (0.80) sits exactly at the four-fifths threshold and is not statistically significant (p=0.089/0.092). No action indicated beyond continued monitoring in future audit cycles.
6. **No action indicated** for gender (excluding the low-confidence Non-binary cells), disability status, and veteran status at the cross-role level — none of these approached statistical significance.

---

## 6. Caveats

- **Correlation is not causation.** A four-fifths ratio below 0.8, even when statistically significant, documents a disparity in observed outcomes. It does not, by itself, establish that the disparity is caused by discriminatory intent or an unlawful practice — legitimate, job-related, non-discriminatory factors could explain part or all of an observed gap, and this audit did not attempt to isolate such factors beyond noting where a CV-derived control (e.g., years of experience) might be worth checking.
- **Low-confidence findings need more data, not more scrutiny of the same data.** 16 of the 24 flagged cells in this report are built on fewer than 30 candidates somewhere in the comparison and are marked `low_confidence`. These are reported for transparency (an audit should show every dimension requested, not hide small cells) but should not be treated as equivalent in weight to the three statistically significant, adequately-powered findings in Section 4.
- **This is a methodology audit on a synthetic dataset**, not a legal compliance certification and not a substitute for review by qualified HR/legal counsel before any policy or personnel action is taken.
