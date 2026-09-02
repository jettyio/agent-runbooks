# Hiring Demographics Audit — Compliance Report

**Prepared for:** HR / Legal review
**Dataset:** Synthetic candidate/hiring records, 1,200 rows
**Scope:** Adverse-impact screening across 5 job roles and 5 demographic dimensions

---

## 1. Methodology

### 1.1 Dataset

- **Source file:** `f7d170dd.00.csv` (uploaded asset; the declared default path `/app/assets/software_hiring_1200.csv` was not present, so the uploaded file was used per the runbook's fallback rule).
- **Rows:** 1,200 candidates. No rows had missing `role_applied` or `hired` values, so 0 rows were dropped (1,200 before → 1,200 after).
- **Missingness:** No missing values in any demographic column (`gender`, `race_ethnicity`, `disability_status`, `veteran_status`, `age`). The only column with missing data was `certifications` (526 blanks, expected for candidates with none listed) — not used in disparity calculations. Because no demographic values were actually missing in this dataset, no "Unknown/Declined" category needed to be populated in practice, though the pipeline supports it defensively.
- **Job roles (n):** Software Engineer (399), QA Engineer (301), Data Scientist (201), Product Manager (169), Engineering Manager (130).
- **Outcome:** `hired` coerced from `Yes`/`No` strings to boolean (828 No / 372 Yes overall, 31.0% base hire rate). `disability_status` and `veteran_status` were likewise coerced from `Yes`/`No` strings.
- **Age brackets:** the raw `age` column (range 22–61) was bucketed into four fixed brackets used consistently throughout this report and the metrics table: **`<30`, `30-39`, `40-49`, `50+`**.

### 1.2 Disparity Metrics

For each (job role × demographic dimension) cell, and for a role-agnostic (`ALL_ROLES`) rollup of each dimension:

1. **Reference group selection:** among groups with at least **30** candidates in the cell, the group with the highest selection (hire) rate is the reference. If no group in the cell reaches 30 candidates, the highest-rate group overall is used instead and every row in that cell is marked `low_confidence = true`. This guards against a small group's high hire rate becoming an unstable benchmark for everyone else.
2. **Tie-breaking:** if multiple groups tie for the highest rate, ties are broken deterministically — first by larger candidate count, then by alphabetically-first group name. Cells where this rule fired are marked `reference_group_tie_broken = true`.
3. **Four-fifths ratio:** `group selection rate ÷ reference group selection rate`. Ratios below **0.80** are flagged (the standard four-fifths/80% adverse-impact rule).
4. **Statistical significance:** for every cell where *both* the group and its reference group have ≥30 candidates, two tests are run on the resulting 2×2 (hired/not-hired) contingency table: a two-sided **Fisher's exact test** and a **Pearson chi-square test with Yates' continuity correction**. A finding is marked `statistically_significant = true` only when **both** tests agree at p < 0.05 — a deliberately conservative rule chosen to avoid cherry-picking whichever test happens to produce a lower p-value.
5. **Low-confidence cells** (candidate count < 30, or a fallback reference group < 30) are still reported for transparency but are explicitly excluded from significance testing and should be treated as directional only.
6. **Minimum group size:** 30 candidates, applied uniformly to reference-group eligibility and to significance-test eligibility.

### 1.3 Limitations

- This is a **synthetic dataset** used for audit-methodology demonstration; findings here are not an EEOC/OFCCP compliance certification.
- The four-fifths rule and significance tests describe **statistical disparity in aggregate outcomes**, not intent or cause. Legitimate, job-related factors (e.g., experience, education) that happen to correlate with a protected attribute can produce a disparity without discrimination — see the control-variable notes under each flagged finding below.
- Many `disability_status` (98/1200 "Yes") and `veteran_status` (60/1200 "Yes") cells fall under the 30-candidate threshold once split by role, which is expected given how small those minority groups are, not a data error — those findings are directional-only.
- Every programmatic self-consistency check described in the runbook (row completeness, count conservation, rate bounds, flag/low-confidence consistency, reference-group and tie-break correctness, rollup literal spelling, dual-test presence, and the significance combination rule) was run against `disparity_metrics.csv` and **all 10 checks passed** on first execution — see `validation_report.json`.

---

## 2. Findings by Job Role

### Software Engineer (n=399, overall hire rate 26.3%)
The role with the most numerous and most statistically supported disparities in the dataset.
- **Gender:** Male reference (31.2% selection, n=263). **Female selection rate 13.95% (n=129), ratio 0.45 — flagged, statistically significant (Fisher p=0.0002, chi² p=0.0004).** Non-binary (n=7) is too small to test (low-confidence).
- **Race/ethnicity:** Asian reference (33.6%, n=107). **Hispanic/Latino 14.55% (n=55), ratio 0.43 — flagged, statistically significant (Fisher p=0.0095, chi² p=0.0163).** White 23.7% (n=194), ratio 0.70 — flagged, but not statistically significant (Fisher p=0.079, chi² p=0.086). Black 30.2% (n=43), ratio 0.90 — not flagged.
- **Age bracket:** 40-49 reference (35.1%, n=57). **<30 19.6% (n=168), ratio 0.56 — flagged, statistically significant (Fisher p=0.029, chi² p=0.028).** 30-39 27.8% (n=151), ratio 0.79 — flagged, not statistically significant (Fisher p=0.31, chi² p=0.39).
- **Disability/veteran status:** no flagged disparities; veteran "Yes" (n=14) is low-confidence.

### QA Engineer (n=301, overall hire rate 33.9%)
No flagged disparity reaches statistical significance in this role.
- **Race/ethnicity:** Black reference (40.6%, n=32). White 32.4% (n=136), ratio 0.80 — borderline flagged (just under the threshold), not statistically significant (Fisher p=0.41, chi² p=0.50).
- Gender, disability, veteran, and age brackets show no flagged ratios in this role.

### Data Scientist (n=201, overall hire rate 34.8%)
- **Age bracket:** 40-49 reference (40.0%, n=35). 30-39 24.2% (n=62), ratio 0.60 — flagged, not statistically significant (Fisher p=0.11, chi² p=0.16).
- **Gender:** Non-binary (n=9, ratio 0.62 vs. Female reference) and **disability status "Yes"** (n=17, ratio 0.70 vs. "No") are flagged but low-confidence — both groups are well under the 30-candidate threshold.

### Product Manager (n=169, overall hire rate 32.5%)
- **Race/ethnicity:** White reference (43.9%, n=66). **Asian 29.2% (n=48), ratio 0.66 — flagged, not statistically significant (Fisher p=0.12, chi² p=0.16).** Hispanic/Latino 34.3% (n=35), ratio 0.78 — flagged, not statistically significant (Fisher p=0.40, chi² p=0.47). Black (n=20), ratio 0.46 — flagged but low-confidence.
- Gender, disability, veteran, and age brackets show no non-low-confidence flags.

### Engineering Manager (n=130, overall hire rate 33.1%)
Smallest role by sample size; several flagged cells are low-confidence as a result.
- **Race/ethnicity:** White reference (37.5%, n=56). **Asian 21.4% (n=42), ratio 0.57 — flagged, not statistically significant (Fisher p=0.12, chi² p=0.14).** Black (n=15), ratio 0.71 — flagged but low-confidence.
- **Gender:** Male reference (39.5%, n=76). Female 23.5% (n=51), ratio 0.60 — flagged, not statistically significant (Fisher p=0.083, chi² p=0.093), just above the conventional p<0.05 line.
- **Age bracket:** 40-49 reference (39.1%, n=46). 50+ 22.9% (n=35), ratio 0.58 — flagged, not statistically significant (Fisher p=0.15, chi² p=0.19). 30-39 (n=42), ratio 0.79 — flagged, not statistically significant.
- **Veteran status:** "Yes" (n=7, 0 hires) — ratio 0.00, flagged but low-confidence (well below the 30-candidate threshold; directional only).

---

## 3. Findings by Demographic Dimension (Cross-Role Rollup)

The `ALL_ROLES` rollup pools candidates across all five roles for each dimension, giving more statistical power where individual-role cells are too small.

- **Gender:** Reference group is **Non-binary** (42.9% selection, n=35 — legitimately meets the 30-candidate threshold and has the highest pooled rate). Female pooled selection rate is 27.3% (n=440), ratio 0.64 — flagged, not statistically significant (Fisher p=0.054, chi² p=0.076, both just above 0.05). Male pooled rate 32.7% (n=725), ratio 0.76 — flagged, not statistically significant.
- **Race/ethnicity:** Reference group is Black (32.1% pooled selection, n=134). No other group falls below the 0.80 ratio at the pooled level (White 0.98, Hispanic/Latino 0.93, Asian 0.95) — the role-level race/ethnicity disparities seen above (e.g., Software Engineer Hispanic/Latino, Product Manager Asian) do not persist when pooled across roles, suggesting they may be concentrated in specific roles rather than reflecting a company-wide pattern.
- **Disability status:** No pooled disparity (ratio 0.91, not flagged).
- **Veteran status:** No pooled disparity (ratio 0.97, not flagged).
- **Age bracket:** Reference group is 40-49 (39.0% pooled selection, n=210). **<30 pooled selection rate 28.1% (n=463), ratio 0.72 — flagged, statistically significant (Fisher p=0.0055, chi² p=0.0060).** **30-39 pooled selection rate 29.3% (n=423), ratio 0.75 — flagged, statistically significant (Fisher p=0.0151, chi² p=0.0178).** 50+ ratio 0.89, not flagged. Age is the dimension with the clearest, best-powered, statistically significant disparity when viewed across the whole company: candidates under 40 are hired at meaningfully lower rates than the 40-49 reference group, and this holds up at large sample size.

---

## 4. Flagged Items (All 22 Flagged Rows, Ratio < 0.80)

Sorted by severity (lowest ratio first); non-low-confidence, statistically significant items are the highest-priority findings.

| Job Role | Dimension | Group | Ratio | Fisher p | Chi² p | Stat. Sig. | Confidence |
|---|---|---|---|---|---|---|---|
| Engineering Manager | veteran_status | Yes | 0.00 | — | — | No | **Low** (n=7) |
| Software Engineer | race_ethnicity | Hispanic/Latino | 0.43 | 0.0095 | 0.0163 | **Yes** | High |
| Software Engineer | gender | Female | 0.45 | 0.0002 | 0.0004 | **Yes** | High |
| Product Manager | race_ethnicity | Black | 0.46 | — | — | No | **Low** (n=20) |
| Software Engineer | age_bracket | <30 | 0.56 | 0.0291 | 0.0282 | **Yes** | High |
| Engineering Manager | race_ethnicity | Asian | 0.57 | 0.1211 | 0.1370 | No | High |
| Engineering Manager | age_bracket | 50+ | 0.58 | 0.1523 | 0.1889 | No | High |
| Engineering Manager | gender | Female | 0.60 | 0.0831 | 0.0930 | No | High |
| Data Scientist | age_bracket | 30-39 | 0.60 | 0.1127 | 0.1609 | No | High |
| Data Scientist | gender | Non-binary | 0.62 | — | — | No | **Low** (n=9) |
| ALL_ROLES | gender | Female | 0.64 | 0.0538 | 0.0763 | No | High |
| Product Manager | race_ethnicity | Asian | 0.66 | 0.1214 | 0.1582 | No | High |
| Data Scientist | disability_status | Yes | 0.70 | — | — | No | **Low** (n=17) |
| Software Engineer | race_ethnicity | White | 0.70 | 0.0785 | 0.0859 | No | High |
| Engineering Manager | race_ethnicity | Black | 0.71 | — | — | No | **Low** (n=15) |
| ALL_ROLES | age_bracket | <30 | 0.72 | 0.0055 | 0.0060 | **Yes** | High |
| ALL_ROLES | age_bracket | 30-39 | 0.75 | 0.0151 | 0.0178 | **Yes** | High |
| ALL_ROLES | gender | Male | 0.76 | 0.2693 | 0.2873 | No | High |
| Product Manager | race_ethnicity | Hispanic/Latino | 0.78 | 0.3988 | 0.4671 | No | High |
| Engineering Manager | age_bracket | 30-39 | 0.79 | 0.5050 | 0.5627 | No | High |
| Software Engineer | age_bracket | 30-39 | 0.79 | 0.2789 | 0.3937 | No | High |
| QA Engineer | race_ethnicity | White | 0.80 | 0.4097 | 0.4954 | No | High |

**Total flagged rows: 22.** Of these, **5** are both non-low-confidence and statistically significant by the dual-test rule: Software Engineer (Hispanic/Latino, Female, <30 age bracket), and the ALL_ROLES rollup for age bracket (<30 and 30-39).

---

## 5. Recommendations

1. **Priority review — Software Engineer role.** Three independent, statistically significant disparities converge on this single role: gender (Female selection ratio 0.45, p<0.001 on both tests), race/ethnicity (Hispanic/Latino ratio 0.43, p<0.02 on both tests), and age (<30 ratio 0.56, p<0.03 on both tests). Because all three land in the same role, recommend a targeted review of the Software Engineer screening/interview process specifically — job requirements, interview rubric, and who conducts screening — rather than a company-wide policy change.
2. **Investigate the company-wide age pattern (<40 selection gap).** The ALL_ROLES rollup shows candidates under 30 (ratio 0.72, p<0.006) and 30-39 (ratio 0.75, p<0.015) are hired at significantly lower rates than the 40-49 reference group, and this is powered by large sample sizes (n=463 and n=423 respectively) so it is not a small-sample artifact. Recommend cross-referencing this against `years_experience` and `num_previous_roles` (available as control variables in the source data) to determine whether the gap is explained by experience differences or persists after controlling for it — the latter would warrant a closer look at age-related bias in screening.
3. **Collect more data before concluding on low-confidence flags.** Seven flagged rows are marked low-confidence purely due to small group size (Engineering Manager veteran "Yes" n=7; Product Manager race Black n=20; Data Scientist gender Non-binary n=9 and disability "Yes" n=17; Engineering Manager race Black n=15). These should not be treated as established findings — recommend continuing to monitor these cells as applicant volume grows, and consider whether outreach could increase applicant pool size for smaller demographic groups in these roles before drawing conclusions.
4. **Monitor, but do not yet act on, the borderline QA Engineer and Product Manager race/ethnicity findings.** QA Engineer (White, ratio 0.80) sits exactly at the four-fifths line and is not statistically significant; Product Manager (Asian, ratio 0.66; Hispanic/Latino, ratio 0.78) show meaningful ratios but neither test reaches significance at current sample sizes. Recommend re-running this audit once each role has more candidates in the smaller groups before escalating.
5. **Race/ethnicity disparities appear role-specific, not systemic.** The ALL_ROLES rollup for race/ethnicity shows no flagged ratio (lowest is 0.93), while several individual roles do show flags. This suggests any real effect is concentrated in specific role pipelines (especially Software Engineer) rather than a uniform company-wide pattern — recommend focusing remediation effort on the flagged roles rather than a blanket policy change.
6. **No action indicated for disability status or veteran status at the company-wide level** — pooled ratios are 0.91 and 0.97 respectively, both above the four-fifths threshold. Continue to track these as sample sizes grow given how small these subgroups currently are.

---

## 6. Caveats

- **Correlation is not causation.** A four-fifths ratio below 0.80, even when statistically significant, describes an aggregate outcome disparity. It does not by itself establish discriminatory intent or a causal link to a protected attribute — legitimate, job-related factors that correlate with the attribute (experience, education, role-specific skills) can produce the same statistical pattern. Findings in Section 4 should be read as "warrants review," not "proven bias."
- **Low-confidence findings need more data, not more conclusions.** Every row marked low-confidence in this report reflects a group below the 30-candidate minimum sample size for either the group itself or its reference group. These are reported for transparency (an audit should not silently hide small groups) but are directional only and should not be the sole basis for a policy or personnel decision.
- **Dual-test agreement is a conservative bar.** This report only calls a finding "statistically significant" when both Fisher's exact test and the chi-square test with continuity correction agree at p<0.05. Several ratios below 0.80 (e.g., QA Engineer White, Product Manager Hispanic/Latino) do not clear this bar and are reported as directional findings, not statistically confirmed ones.
- **Synthetic data.** This dataset and audit are for methodology demonstration. No claim is made that this constitutes a legal compliance filing or determination under EEOC/OFCCP standards.
