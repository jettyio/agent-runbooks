# Hiring Demographics Audit — Compliance Report

**Prepared:** 2026-08-19  
**Dataset:** `/app/assets/synthetic_cvs_hiring.csv` (synthetic dataset, audit-methodology purposes)  
**Audit Standard:** Four-fifths (80%) rule, supplemented by Fisher's exact test and Pearson chi-square test

---

## 1. Methodology

### 1.1 Dataset Overview

| Item | Value |
|------|-------|
| Total candidate records | 1,000 |
| Records dropped (missing role or outcome) | 0 |
| Unique job roles analyzed | 12 |
| Overall hire rate | 38.0% |
| Date range | Not available in dataset |

**Data-quality notes:**
- The `certifications` column had 305 missing values; this column was not used in disparity calculations.
- All other required columns (`role_applied`, `hired`, `age`, `gender`, `race_ethnicity`, `disability_status`, `veteran_status`) were fully populated.
- Candidates with missing demographic data (none observed for core attributes) would have been retained with a "Unknown/Declined" category rather than dropped.
- `disability_status` and `veteran_status` exhibit significant skew: 87.5% report no disability; 93.5% report non-veteran status. Small `Yes` minorities frequently fall below the minimum group size threshold for statistical testing.

### 1.2 Protected Attributes Analyzed

| Attribute | Source | Notes |
|-----------|--------|-------|
| `gender` | Direct column | Values: Male, Female, Non-binary |
| `race_ethnicity` | Direct column | Values: White, Asian, Black, Hispanic/Latino, Multiracial, Middle Eastern, Native American |
| `disability_status` | Direct column (Yes/No string → retained as string category) | |
| `veteran_status` | Direct column (Yes/No string → retained as string category) | |
| `age_bracket` | Derived from numeric `age` | Buckets: <30, 30–39, 40–49, 50+ |

**Age bracket boundaries (fixed):** `[0, 30)` → `<30`; `[30, 40)` → `30-39`; `[40, 50)` → `40-49`; `[50, ∞)` → `50+`. These boundaries were determined once during data loading and are used consistently throughout the analysis and this report.

### 1.3 Disparity Metrics

**Four-fifths (80%) rule:** For each (job role, demographic dimension), the group with the highest selection (hire) rate is designated the reference group. Every other group's ratio (`group_rate / reference_rate`) is computed; a ratio below **0.80** is flagged as a potential adverse impact indicator.

**Reference group tie-breaking:** When two or more groups share the maximum selection rate, the reference group is chosen by: (1) larger candidate count; (2) alphabetically first name. Rows where this rule fired have `reference_group_tie_broken = true` in the metrics table.

**Statistical significance:** Two tests are always computed for every eligible cell (both the comparison group **and** its reference group must have ≥ 30 candidates):
- **Fisher's exact test** (two-sided, `scipy.stats.fisher_exact`) — exact, valid at any sample size
- **Pearson chi-square with Yates' continuity correction** (`scipy.stats.chi2_contingency`, `correction=True`) — large-sample approximation

A finding is considered `statistically_significant` **only if both tests agree** (Fisher p < 0.05 **AND** chi-square p < 0.05). This conservative rule prevents artifacts from test selection.

**Minimum group size:** Cells where either the comparison group or reference group has fewer than 30 candidates are marked `low_confidence = true`. These cells are reported for transparency but should not support firm conclusions.

### 1.4 Limitations

- Statistical disparity in aggregate hiring data does not establish discriminatory intent. Multiple confounders (qualifications, role-specific requirements, pipeline composition) may explain observed differences.
- The dataset is synthetic and generated for audit-methodology purposes; findings should not be extrapolated to real-world populations.
- With 12 roles and 5 demographic dimensions, multiple comparisons inflate the chance of false positives. No multiplicity correction (e.g., Bonferroni) was applied; findings should be treated as hypothesis-generating rather than confirmatory.
- Low-confidence cells (below 30 candidates) are directional only and require additional data before any action is warranted.

---

## 2. Summary of Findings

**Total flagged cells (four-fifths ratio < 0.80):** 134 across all (role, dimension, group) combinations.

| Dimension | Flagged Cells | High-Confidence Flagged | Statistically Significant |
|-----------|--------------|------------------------|--------------------------|
| `gender` | 20 | 4 | 1 |
| `race_ethnicity` | 69 | 6 | 4 |
| `age_bracket` | 29 | 3 | 3 |
| `disability_status` | 8 | 0 | 0 |
| `veteran_status` | 8 | 0 | 0 |
| **Total** | **134** | **13** | **8** |

*"High-confidence" = both comparison and reference groups have ≥ 30 candidates. "Statistically significant" = both Fisher's exact and chi-square tests return p < 0.05.*

---

## 3. Findings by Demographic Dimension (Cross-Role Rollup)

### 3.1 Gender

Across all 1,000 candidates, males have the highest selection rate (42.1%), followed by females (34.4%) and Non-binary candidates (27.6%).

| Group | n | Hired | Selection Rate | 4/5 Ratio | Flagged | Confidence |
|-------|---|-------|---------------|-----------|---------|------------|
| Male (reference) | 497 | 209 | 42.1% | 1.000 | No | High |
| Female | 474 | 163 | 34.4% | 0.818 | No | High |
| Non-binary | 29 | 8 | 27.6% | 0.656 | **Yes** | **Low** |

The Non-binary group's ratio of 0.656 is below the 0.80 threshold, but with only 29 candidates across all roles, this finding is **low-confidence**. No statistical testing was performed for this group given its size. A dataset with ≥ 30 Non-binary candidates would be needed before drawing conclusions.

### 3.2 Race/Ethnicity

White candidates have the highest selection rate (46.5%). Six of six non-White groups are flagged across all roles.

| Group | n | Hired | Selection Rate | 4/5 Ratio | Flagged | Fisher p | Chi2 p | Stat. Sig. | Confidence |
|-------|---|-------|---------------|-----------|---------|----------|--------|------------|------------|
| White (reference) | 387 | 180 | 46.5% | 1.000 | No | — | — | — | High |
| Asian | 157 | 57 | 36.3% | 0.781 | **Yes** | 0.035640 | 0.037539 | **Yes** | High |
| Black | 145 | 49 | 33.8% | 0.727 | **Yes** | 0.010433 | 0.011092 | **Yes** | High |
| Middle Eastern | 58 | 20 | 34.5% | 0.741 | **Yes** | 0.091201 | 0.115051 | No | High |
| Multiracial | 67 | 22 | 32.8% | 0.706 | **Yes** | 0.045456 | 0.051588 | No | High |
| Hispanic/Latino | 160 | 43 | 26.9% | 0.578 | **Yes** | 0.000023 | 0.000032 | **Yes** | High |
| Native American | 26 | 9 | 34.6% | 0.744 | **Yes** | — | — | — | **Low** |

**Hispanic/Latino** candidates show the most severe disparity at a four-fifths ratio of 0.578 — a selection rate of 26.9% vs. 46.5% for White candidates — and this is highly statistically significant (Fisher p < 0.0001, chi-square p < 0.0001). **Black** (ratio 0.727, Fisher p = 0.010, chi-square p = 0.011) and **Asian** (ratio 0.781, Fisher p = 0.036, chi-square p = 0.038) candidates also show statistically significant disparities. **Middle Eastern** (ratio 0.741) and **Multiracial** (ratio 0.706) are flagged but do not meet the dual-test significance threshold. **Native American** is flagged but low-confidence (n = 26).

### 3.3 Age Bracket

The 40–49 age bracket has the highest selection rate (50.5%). Three of three younger/older brackets are flagged.

| Group | n | Hired | Selection Rate | 4/5 Ratio | Flagged | Fisher p | Chi2 p | Stat. Sig. | Confidence |
|-------|---|-------|---------------|-----------|---------|----------|--------|------------|------------|
| 40–49 (reference) | 210 | 106 | 50.5% | 1.000 | No | — | — | — | High |
| 50+ | 342 | 132 | 38.6% | 0.765 | **Yes** | 0.007851 | 0.008105 | **Yes** | High |
| 30–39 | 257 | 94 | 36.6% | 0.725 | **Yes** | 0.002683 | 0.003435 | **Yes** | High |
| <30 | 191 | 48 | 25.1% | 0.498 | **Yes** | < 0.0001 | < 0.0001 | **Yes** | High |

The **<30 age bracket** is the single most severe high-confidence disparity in the dataset, with a four-fifths ratio of 0.498 and highly significant dual-test results (Fisher p ≈ 0, chi-square p ≈ 0). Candidates under 30 are hired at roughly half the rate of 40–49 year olds. The **30–39** (ratio 0.725) and **50+** (ratio 0.765) brackets are also flagged with statistical significance, suggesting that the 40–49 cohort is systematically favored.

### 3.4 Disability Status

Across all roles, candidates reporting a disability have a selection rate of 35.2% vs. 38.4% for those without (ratio 0.917). This is **not flagged** (above 0.80 threshold). No further action is indicated by this metric alone.

### 3.5 Veteran Status

Veterans have a selection rate of 36.9% vs. 38.1% for non-veterans (ratio 0.970). This is **not flagged**. No disparity signal detected.

---

## 4. Findings by Job Role

This section covers roles where at least one high-confidence flagged finding exists. All other roles are noted with their overall hire rate; per-role demographic breakdowns with small group sizes are low-confidence.

### 4.1 Financial Analyst — Gender Disparity (High Confidence, Statistically Significant)

Overall hire rate: 44.8% (43 hired / 96 applicants)

| Group | n | Hired | Selection Rate | 4/5 Ratio | Fisher p | Chi2 p | Stat. Sig. |
|-------|---|-------|---------------|-----------|----------|--------|------------|
| Male (reference) | 46 | 29 | 63.0% | 1.000 | — | — | — |
| Female | 47 | 13 | 27.7% | **0.439** | **0.000826** | **0.001283** | **Yes** |
| Non-binary | 3 | 1 | 33.3% | 0.529 | — | — | Low confidence |

**The most severe high-confidence, statistically significant per-role finding in the dataset.** Female candidates in the Financial Analyst role are hired at 27.7% vs. 63.0% for male candidates (four-fifths ratio 0.439). Both Fisher's exact (p = 0.0008) and chi-square (p = 0.0013) tests confirm this is highly unlikely due to chance. This finding warrants urgent review of the Financial Analyst screening and selection process.

### 4.2 Business Analyst — Gender Disparity (High Confidence, Not Statistically Significant)

Overall hire rate: 32.0% (24 hired / 75 applicants)

| Group | n | Hired | Selection Rate | 4/5 Ratio | Fisher p | Chi2 p | Stat. Sig. |
|-------|---|-------|---------------|-----------|----------|--------|------------|
| Male (reference) | 42 | 17 | 40.5% | 1.000 | — | — | — |
| Female | 32 | 7 | 21.9% | **0.540** | 0.132577 | 0.149078 | No |
| Non-binary | 1 | 0 | 0.0% | 0.000 | — | — | Low confidence |

Female candidates in the Business Analyst role are flagged (ratio 0.540), but neither significance test reaches p < 0.05. The finding is directionally concerning — the gap is large — but with 32 female applicants, the sample is at the minimum threshold and the signal may not be robust. Larger samples or role-level process review are recommended.

### 4.3 Product Manager — Gender Disparity (High Confidence, Not Statistically Significant)

Overall hire rate: 25.3% (20 hired / 79 applicants)

| Group | n | Hired | Selection Rate | 4/5 Ratio | Fisher p | Chi2 p | Stat. Sig. |
|-------|---|-------|---------------|-----------|----------|--------|------------|
| Male (reference) | 41 | 13 | 31.7% | 1.000 | — | — | — |
| Female | 35 | 7 | 20.0% | **0.631** | 0.301875 | 0.371346 | No |
| Non-binary | 3 | 0 | 0.0% | 0.000 | — | — | Low confidence |

Product Manager has the lowest overall hire rate (25.3%) of any role. Female candidates are flagged (ratio 0.631) but the difference is not statistically significant at the dual-test threshold. Monitor for persistence as the candidate pool grows.

### 4.4 HR Coordinator — Gender Disparity (High Confidence, Not Statistically Significant, Male Disadvantaged)

Overall hire rate: 41.5% (34 hired / 82 applicants)

| Group | n | Hired | Selection Rate | 4/5 Ratio | Fisher p | Chi2 p | Stat. Sig. |
|-------|---|-------|---------------|-----------|----------|--------|------------|
| Female (reference) | 36 | 18 | 50.0% | 1.000 | — | — | — |
| Male | 44 | 16 | 36.4% | **0.727** | 0.259899 | 0.317242 | No |
| Non-binary | 2 | 0 | 0.0% | 0.000 | — | — | Low confidence |

In HR Coordinator, **female** candidates are the reference group (highest selection rate), and male candidates are flagged (ratio 0.727). This is one of two roles where the typically lower-selection group benefits; it is not statistically significant and may reflect applicant pool composition. Noted for completeness.

### 4.5 Marketing Specialist — Gender Disparity (High Confidence, Not Statistically Significant)

Overall hire rate: 40.2%

Female candidates: ratio = 0.773 (Fisher p = 0.373, chi-square p = 0.475) — flagged but not statistically significant.

### 4.6 All Other Roles

For the remaining roles (Accountant, Customer Success Manager, Data Analyst, Operations Manager, Sales Representative, Software Engineer, UX Designer), no high-confidence gender disparity is flagged at the four-fifths threshold. Race/ethnicity and age bracket per-role cells are predominantly low-confidence due to small group sizes within individual roles; the cross-role rollup (Section 3) provides the statistically meaningful view for those dimensions.

---

## 5. Flagged Items — Prioritized List

**Total flagged cells (four-fifths ratio < 0.80):** 134

The table below lists all flagged findings sorted by severity: lowest four-fifths ratio first, ties broken by statistically significant (true first) then low-confidence (false first). This is the canonical ordering derived directly from `disparity_metrics.csv`.

### Top 5 Most Severe Flagged Findings (by four-fifths ratio, all ties resolved per methodology)

| Rank | Role | Dimension | Group | 4/5 Ratio | Stat. Sig. | Low Confidence | Note |
|------|------|-----------|-------|-----------|------------|----------------|------|
| 1 | Business Analyst | gender | Non-binary | **0.000** | — | **Yes** | n = 1; directional only |
| 2 | HR Coordinator | gender | Non-binary | **0.000** | — | **Yes** | n = 2; directional only |
| 3 | Marketing Specialist | gender | Non-binary | **0.000** | — | **Yes** | n = 1; directional only |
| 4 | Operations Manager | gender | Non-binary | **0.000** | — | **Yes** | n = 1; directional only |
| 5 | Product Manager | gender | Non-binary | **0.000** | — | **Yes** | n = 3; directional only |

**Important interpretation note:** These five findings share ratio = 0.000 because Non-binary candidates happened to receive zero hires in these roles. All five are **low-confidence** (group sizes of 1–3 candidates). Statistical testing was not performed and cannot be performed at these sample sizes. These results reflect data sparsity, not a statistically sound disparity signal. They are reported here for transparency and because the four-fifths rule mechanically produces ratio = 0 for any zero-hire group. No action should be taken based solely on these findings; what is needed is a larger Non-binary applicant pool.

### High-Confidence Flagged Findings (n ≥ 30 for both groups, listed by severity)

| Role | Dimension | Group | 4/5 Ratio | Fisher p | Chi2 p | Stat. Sig. |
|------|-----------|-------|-----------|----------|--------|------------|
| Financial Analyst | gender | Female | **0.439** | 0.000826 | 0.001283 | **Yes** |
| ALL_ROLES | age_bracket | <30 | **0.498** | < 0.0001 | < 0.0001 | **Yes** |
| Business Analyst | gender | Female | 0.540 | 0.132577 | 0.149078 | No |
| ALL_ROLES | race_ethnicity | Hispanic/Latino | 0.578 | 0.000023 | 0.000032 | **Yes** |
| Product Manager | gender | Female | 0.631 | 0.301875 | 0.371346 | No |
| ALL_ROLES | race_ethnicity | Multiracial | 0.706 | 0.045456 | 0.051588 | No |
| ALL_ROLES | age_bracket | 30–39 | 0.725 | 0.002683 | 0.003435 | **Yes** |
| ALL_ROLES | race_ethnicity | Black | 0.727 | 0.010433 | 0.011092 | **Yes** |
| HR Coordinator | gender | Male | 0.727 | 0.259899 | 0.317242 | No |
| ALL_ROLES | race_ethnicity | Middle Eastern | 0.741 | 0.091201 | 0.115051 | No |
| ALL_ROLES | age_bracket | 50+ | 0.765 | 0.007851 | 0.008105 | **Yes** |
| Marketing Specialist | gender | Female | 0.773 | 0.373185 | 0.474872 | No |
| ALL_ROLES | race_ethnicity | Asian | 0.781 | 0.035640 | 0.037539 | **Yes** |

### Selected Low-Confidence Flagged Findings (directional only — n < 30)

| Role | Dimension | Group | 4/5 Ratio | Note |
|------|-----------|-------|-----------|------|
| ALL_ROLES | gender | Non-binary | 0.656 | n = 29 total |
| ALL_ROLES | race_ethnicity | Native American | 0.744 | n = 26 total |
| Product Manager | age_bracket | <30 | 0.191 | n = 14; directional only |
| Data Analyst | age_bracket | <30 | 0.222 | n = 16; directional only |
| Operations Manager | age_bracket | <30 | 0.269 | n = 12; directional only |
| Multiple roles | age_bracket | <30, 30–39, 50+ | 0.19–0.79 | All per-role age cells are low-confidence |

*A full listing of all 134 flagged rows (including all low-confidence cells) is available in `disparity_metrics.csv`.*

---

## 6. Recommendations

The following recommendations are tied to specific flagged findings.

**Immediate (statistically significant, high-confidence findings):**

1. **Financial Analyst — Gender (Female, ratio 0.439, Fisher p = 0.0008, chi-square p = 0.0013):** Conduct an immediate audit of the Financial Analyst selection pipeline. Examine screening criteria, interview panels, and scoring rubrics for gender-correlated bias. Compare female and male candidates' qualifications (experience, education, GPA) in this role specifically to determine whether the disparity persists after controlling for qualifications, or whether it reflects differential application of criteria.

2. **All Roles — Age Bracket (<30, ratio 0.498, p ≈ 0 on both tests):** Review whether any role-level qualifications (years of experience thresholds, seniority requirements) disproportionately screen out candidates under 30. Assess whether these requirements are job-relevant and consistently applied. Age-based selection disparities carry legal exposure under the Age Discrimination in Employment Act (ADEA) in employment contexts.

3. **All Roles — Race/Ethnicity (Hispanic/Latino, ratio 0.578, Fisher p < 0.0001; Black, ratio 0.727, Fisher p = 0.010; Asian, ratio 0.781, Fisher p = 0.036):** Undertake a sourcing and screening audit across all roles. Review: (a) whether job postings reach diverse applicant pools; (b) whether structured interview guides and standardized scoring are used; (c) whether any pre-screen filters (keyword-based résumé screening) have disparate impact. These findings are statistically robust and span the entire organization.

4. **All Roles — Age Bracket (30–39, ratio 0.725, p = 0.003; 50+, ratio 0.765, p = 0.008):** The pattern across three of four age brackets (all except 40–49) is consistent with a systematic preference for mid-career candidates. Evaluate whether this reflects legitimate experience matching or implicit age-based preferences.

**Monitor / Investigate Further (flagged but not statistically significant):**

5. **Business Analyst — Gender (Female, ratio 0.540, p = 0.133):** This gap is large enough to be practically concerning even though it does not reach the dual-test significance threshold with the current sample. Re-examine in 6 months or when additional applicant data is available; the Business Analyst pipeline warrants monitoring.

6. **Product Manager — Gender (Female, ratio 0.631, p = 0.302):** Similar to Business Analyst: the gap is concerning, and the lack of significance likely reflects sample size rather than absence of a pattern. Increase applicant pool and re-evaluate.

7. **All Roles — Race/Ethnicity (Middle Eastern, ratio 0.741, p = 0.091/0.115; Multiracial, ratio 0.706, p = 0.046/0.052):** These groups are flagged on the four-fifths rule and show p-values near but above 0.05. The Multiracial result is borderline (Fisher p = 0.046 < 0.05 but chi-square p = 0.052 > 0.05); the dual-test rule correctly withholds the significance label. Monitor as data accumulates.

**Collect More Data:**

8. **Non-binary candidates (n = 29 across all roles):** With fewer than 30 total Non-binary applicants, no statistical conclusion is possible. Ensure the applicant tracking system accurately captures gender identity and expand the applicant pool; revisit this dimension when n ≥ 30.

9. **Native American candidates (n = 26 across all roles):** Similarly, increase outreach and revisit when sample size is adequate.

10. **Disability and veteran status — per-role cells:** Most per-role cells for these dimensions fall below the minimum group size. The aggregate-level ratios (0.917 for disability, 0.970 for veteran status) do not indicate a systemic problem, but should be tracked annually.

---

## 7. Caveats and Disclaimer

- **Correlation is not causation.** The four-fifths rule flags statistical disparity in outcomes; it does not establish that discrimination occurred. Qualified candidates may differ systematically between groups in ways not captured by the available data fields.
- **Low-confidence findings are directional only.** Any (role, dimension, group) cell where either the comparison or reference group has fewer than 30 candidates should be treated as a signal to gather more data, not a basis for action.
- **This dataset is synthetic.** It was generated for audit-methodology testing and does not represent a real organization. Findings should not be cited in any legal or compliance context without validation against real data.
- **Multiple comparisons.** With 134 total flagged cells across 5 dimensions and 12 roles plus rollup, some flags are expected by chance. The dual-test significance requirement and the high-confidence filter reduce false positives; however, an additional Bonferroni or Benjamini-Hochberg correction would be appropriate for a formal EEOC/OFCCP filing.
- **Legal review required.** This report is a statistical screening tool. Any decision to alter hiring processes, communicate findings to regulators, or take disciplinary action should involve qualified legal counsel.
