# Hiring Demographics Audit — Results

## Overview
- **Date**: 2026-09-02
- **Input**: 1,200 candidate rows; 5 job roles (Software Engineer, QA Engineer, Data Scientist, Product Manager, Engineering Manager); 5 demographic dimensions analyzed (gender, race_ethnicity, disability_status, veteran_status, age_bracket)
- **Iterations**: 1 (rubric passed on first round; no Step 7 revision needed)

## Rubric Scores

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 1 | Statistical rigor | 5/5 | Fisher's exact + chi² (Yates-corrected) run on every eligible cell; `statistically_significant` verified programmatically to equal `fisher_significant AND chi2_significant` with 0 violations |
| 2 | Completeness of breakdowns | 5/5 | All 5 roles and all 5 dimensions covered per-role and in the ALL_ROLES rollup |
| 3 | Clarity of findings | 5/5 | Full flagged-items table cites role, dimension, group, ratio, and both p-values for every one of the 22 flagged rows |
| 4 | Actionability of recommendations | 5/5 | Recommendations name specific role/group/metric combinations, distinguishing "investigate" from "collect more data" from "monitor" |
| 5 | Appropriate caveats & tone | 5/5 | Explicit correlation-vs-causation and low-confidence caveats; measured, non-alarmist language throughout |
| | **Overall** | **5.0/5** | |

## Output Description
`disparity_metrics.csv` contains 90 rows — one per (job_role, dimension, group) combination across 5 roles + an ALL_ROLES rollup, for 5 demographic dimensions — with candidate/hire counts, selection rates, four-fifths ratios, and dual significance tests (Fisher's exact and chi-square with Yates' correction). `compliance_report.md` synthesizes these into a narrative audit with per-role findings, a cross-role rollup, a full flagged-items table, and targeted recommendations. All 10 programmatic calculation checks (row completeness, count conservation, rate bounds, flag/low-confidence consistency, reference-group and tie-break correctness, rollup literal spelling, dual-test presence, and the significance combination rule) passed on the first run.

## Key Findings
Total flagged (ratio < 0.8): **22**

The 5 most severe flagged disparities (lowest four-fifths ratio, ties broken by statistical significance then confidence):

1. **Engineering Manager / veteran_status / "Yes"** — ratio **0.00** (0 of 7 hired vs. 34.96% for "No"). Low-confidence (n=7, well under the 30-candidate minimum) — directional only.
2. **Software Engineer / race_ethnicity / Hispanic/Latino** — ratio **0.43** (14.55% selection, n=55, vs. Asian reference 33.64%). Statistically significant (Fisher p=0.0095, chi² p=0.0163).
3. **Software Engineer / gender / Female** — ratio **0.45** (13.95% selection, n=129, vs. Male reference 31.18%). Statistically significant (Fisher p=0.0002, chi² p=0.0004).
4. **Product Manager / race_ethnicity / Black** — ratio **0.46** (20.00% selection, n=20, vs. White reference 43.94%). Low-confidence (n=20, under the 30-candidate minimum) — directional only.
5. **Software Engineer / age_bracket / <30** — ratio **0.56** (19.64% selection, n=168, vs. 40-49 reference 35.09%). Statistically significant (Fisher p=0.0291, chi² p=0.0282).

Notably, 3 of these top 5 findings are statistically significant and concentrated in the **Software Engineer** role; the other 2 are low-confidence due to small group sizes. At the cross-role (ALL_ROLES) level, age is the dimension with the clearest company-wide, well-powered disparity: both the `<30` (ratio 0.72, p<0.006) and `30-39` (ratio 0.75, p<0.018) brackets are flagged and statistically significant against the 40-49 reference group.

## Iteration History
- **Round 1**: Metrics computed, all 10 programmatic checks passed immediately, report drafted and self-verified against the CSV with zero discrepancies. No revision required.

## Recommendations
- With more data, disability_status and veteran_status cells (currently 98 and 60 "Yes" candidates respectively, spread thin across 5 roles) would clear the 30-candidate threshold more often, converting several currently-low-confidence flags into statistically testable findings.
- Upstream, capturing a finer-grained age or tenure signal (rather than only birth-year-derived age) could clarify whether the age disparity reflects experience differences or age itself — cross-referencing against `years_experience`/`num_previous_roles` (present in the source data but not required for this audit) would sharpen criterion-1 rigor further.
- Larger per-role applicant volume for smaller demographic groups (e.g., Product Manager Black candidates, n=20) would let significance testing run where it currently cannot.

## Limitations
- The rubric and programmatic checks validate internal consistency and statistical correctness of the *aggregation pipeline*; they do not and cannot validate whether the underlying hiring decisions in the source data were themselves fair — that determination requires human/legal review of the actual screening process, not just the outcome statistics.
- Ratios and significance are reported at face value; no attempt was made to control for legitimate, job-related covariates (experience, education, GPA) in the disparity calculation itself, only to flag where such follow-up would be worthwhile (see recommendations above and Section 6 caveats in `compliance_report.md`).
- This is a synthetic dataset; findings should not be interpreted as evidence about any real hiring process.
