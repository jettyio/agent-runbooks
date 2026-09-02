# Hiring Demographics Audit — Results

## Overview
- **Date**: 2026-09-02
- **Input**: 900 candidate rows, 6 job roles (Clinic Administrator, Lab Technician, Medical Coder, Pharmacist, Radiology Technologist, Registered Nurse), 5 protected-attribute dimensions analyzed (gender, race_ethnicity, disability_status, veteran_status, age_bracket)
- **Iterations**: 1 (initial draft passed the rubric threshold on first evaluation; no rework rounds were required)

## Rubric Scores

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 1 | Statistical rigor | 5/5 | Both Fisher's exact and chi-square (Yates-corrected) tests run on every eligible cell (candidate_count and reference_group count both ≥30); `statistically_significant` verified programmatically to equal `fisher_significant AND chi2_significant` for all 125 rows; low-confidence cells (94/125) clearly separated from the 1 statistically-supported finding. |
| 2 | Completeness of breakdowns | 5/5 | All 6 roles and all 5 dimensions covered individually (Section 2) plus a full cross-role rollup per dimension (Section 3); no role or dimension silently omitted. |
| 3 | Clarity of findings | 5/5 | Full 57-row flagged table with exact selection rates, ratios, and both p-values inline; the one significant finding (Registered Nurse, age 30-39) is called out explicitly with both p-values (0.0176 / 0.0207) rather than requiring cross-referencing the CSV. |
| 4 | Actionability of recommendations | 5/5 | Each recommendation names a specific role/group/metric (e.g., "Registered Nurse, age_bracket 30-39, ratio 0.47") and distinguishes "investigate further" (RN age finding) from "collect more data" (race_ethnicity reference-group instability) from "monitor, no action" (gender, disability, veteran rollups). |
| 5 | Appropriate caveats & tone | 5/5 | Dedicated Caveats section states disparity ≠ discriminatory intent, flags the 75.2% of rows that are low-confidence, and explains the Native American reference-group instability driving most race_ethnicity flags rather than treating it as proof of bias. |
| | **Overall** | **5.0/5** | |

## Output Description
`disparity_metrics.csv` contains 125 rows (6 roles × 5 dimensions + 1 rollup × 5 dimensions, one row per demographic group) with selection rates, four-fifths ratios, dual significance tests, and confidence flags — all 10 programmatic integrity checks passed. `compliance_report.md` synthesizes this into a narrative audit covering methodology, per-role and per-dimension findings, the full list of 57 flagged cells, and actionable recommendations tied to specific findings.

## Key Findings
Total flagged (ratio < 0.8): **57**

The 5 most severe flagged disparities (lowest four-fifths ratio, ties broken by statistical significance then confidence level), computed directly from `disparity_metrics.csv`:

1. **Medical Coder / race_ethnicity / Middle Eastern** — ratio **0.00** (n=2, 0 hires vs. Native American reference at 100%) — low-confidence
2. **Medical Coder / race_ethnicity / Multiracial** — ratio **0.00** (n=7, 0 hires) — low-confidence
3. **Registered Nurse / race_ethnicity / Multiracial** — ratio **0.00** (n=11, 0 hires) — low-confidence
4. **Clinic Administrator / race_ethnicity / Hispanic/Latino** — ratio **0.15** (n=65, 15.4% selected vs. Native American reference at 100%) — low-confidence
5. **Pharmacist / race_ethnicity / Black** — ratio **0.25** (n=12, 16.7% selected) — low-confidence

Separately, the audit's only **statistically significant, non-low-confidence** finding is **Registered Nurse / age_bracket / 30-39** — ratio **0.47** (n=66, 22.7% selected vs. 50+ reference at 48.4%), Fisher's exact p=0.0176, chi-square p=0.0207 (both significant). This is the single finding in the dataset that meets the highest evidentiary bar (adequate sample size on both sides AND agreement between both significance tests) and is flagged in the report as warranting the most direct follow-up.

Note the top-5-by-ratio list above is dominated by very small race_ethnicity cells against an unstable reference group (Native American, n=24 overall); the report's Section 3.2 explains why these should be read directionally rather than as confirmed disparities, distinct from the RN finding above which carries statistical backing.

## Iteration History
- **Round 1**: Built the full pipeline (load/validate → aggregate → dual significance testing → programmatic checks → report). One bug was caught and fixed before finalizing: a floating-point rounding edge case where a true ratio of exactly 0.8 (12/15) computed as 0.7999999999999999 in double precision, causing a false "flagged" result that disagreed with the displayed rounded value. Fixed by rounding the ratio before the threshold comparison, re-ran aggregation, and all 10 programmatic checks then passed. No further rounds were needed — rubric score on the resulting report was 5.0/5 on first evaluation.

## Recommendations
- Grow the Native American applicant pool (currently n=24 across all roles) before treating any race_ethnicity four-fifths ratio as conclusive — it is the reference group in every role and the rollup, and its small size drives 34 of the 57 flagged cells.
- Increase Non-binary applicant volume (currently n=28 overall, 3–10 per role) for the same reason on the gender dimension.
- For the one statistically significant finding (Registered Nurse, age 30-39), the natural next step is a controlled comparison that adjusts for `years_experience` (which is highly correlated with age bracket for this role) to determine whether the age-linked pattern is actually an experience effect.

## Limitations
- This rubric and the programmatic checks validate internal consistency and statistical correctness of the pipeline; they do not and cannot establish real-world discriminatory intent, which would require legal review beyond the scope of this audit.
- 75.2% of the 125 metrics-table rows are low-confidence (group or reference group below n=30); the dataset's per-role demographic granularity is too thin for most subgroup comparisons to be statistically conclusive, which is expected for a 900-row synthetic dataset spread across 6 roles and 5 dimensions.
- The four-fifths rule's dependence on whichever group happens to have the highest observed rate makes it sensitive to noise in small reference groups (see race_ethnicity finding) — this is a known limitation of the heuristic itself, not a defect in this implementation.
