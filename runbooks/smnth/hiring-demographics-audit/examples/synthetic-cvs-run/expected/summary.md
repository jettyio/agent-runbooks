# Hiring Demographics Audit — Results

## Overview
- **Date**: 2026-09-02
- **Input**: 1,000 candidates, 12 job roles, 5 demographic dimensions analyzed (`gender`, `race_ethnicity`, `disability_status`, `veteran_status`, `age_bracket`)
- **Iterations**: 1 round (initial draft met the pass threshold on first scoring; a completeness gap in the per-role breakdown was fixed before finalizing the score, so the scored/finalized report reflects that fix)

## Rubric Scores

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 1 | Statistical rigor | 5/5 | Fisher's exact + chi-square (Yates) always run together; `statistically_significant` verified to equal `fisher_significant AND chi2_significant` on every row; low-confidence cells clearly separated from statistically supported ones. |
| 2 | Completeness of breakdowns | 5/5 | All 12 roles and all 5 dimensions covered per-role and in the `ALL_ROLES` rollup, including an explicit table of all 12 roles' gender rates and a note on why race/age/disability/veteran findings live at the rollup level. |
| 3 | Clarity of findings | 5/5 | Every finding is backed by a table with exact selection rates, ratios, and both p-values side by side. |
| 4 | Actionability of recommendations | 5/5 | Recommendations name specific role/group/metric combinations and distinguish "investigate process," "collect more data," and "do not act on this cell." |
| 5 | Appropriate caveats & tone | 5/5 | Dedicated caveats section; "statistical disparity observed" language used throughout rather than claims of proven discrimination; synthetic-dataset and low-confidence caveats explicit. |
| | **Overall** | **5.0/5** | |

## Output Description
`compliance_report.md` is a narrative fairness/compliance audit covering methodology (age-bracket definitions, significance-testing rules, limitations), per-role and cross-role findings for all 5 demographic dimensions, a full flagged-items list, caveats, and 6 concrete recommendations. `disparity_metrics.csv` is the underlying structured table — 234 rows, one per (job_role, dimension, group), each with candidate/hire counts, selection rate, reference group, four-fifths ratio, both significance-test p-values, and confidence flags.

## Key Findings
Total flagged (ratio < 0.8): **104**

The 5 most severe flagged disparities (strict sort of all `flagged == true` rows by `four_fifths_ratio` ascending, ties broken by `statistically_significant` [true first] then `low_confidence` [false first]) — **all five are ratio = 0.00, low-confidence cells** (small subgroups with zero hires), which is why the report treats them as evidence of nothing on their own and instead foregrounds the larger, statistically-significant findings below the table:

1. **Business Analyst — race_ethnicity — Black**: 7 candidates, 0 hires, ratio **0.00** vs. reference White (low confidence, n<30).
2. **Business Analyst — race_ethnicity — Middle Eastern**: 7 candidates, 0 hires, ratio **0.00** vs. reference White (low confidence, n<30).
3. **HR Coordinator — race_ethnicity — Multiracial**: 7 candidates, 0 hires, ratio **0.00** vs. reference Middle Eastern (low confidence, n<30).
4. **Software Engineer — race_ethnicity — Hispanic/Latino**: 7 candidates, 0 hires, ratio **0.00** vs. reference White (low confidence, n<30).
5. **Business Analyst — disability_status — Yes**: 5 candidates, 0 hires, ratio **0.00** vs. reference No (low confidence, n<30).

**The findings that actually warrant HR/legal attention** are the statistically significant, adequately-sized ones: **Financial Analyst — gender — Female** (ratio 0.44, p=0.0008/0.0013, n=47); the cross-role **age_bracket <30** gap (ratio 0.50, p<0.0001, n=191); and the cross-role **race_ethnicity Hispanic/Latino** (ratio 0.58, p=0.00002/0.00003, n=160) and **Black** (ratio 0.73, p=0.010/0.011, n=145) gaps versus White candidates.

## Iteration History
- **Round 1**: Built the full pipeline (data load/validation, per-role and rollup aggregation, four-fifths ratios, dual significance testing), passed all 10 programmatic checks in Step 4 on the first run except an initial mis-specified "rate bounds" check, which was corrected (not the underlying data) once analysis showed the >1.0 ratios only occur in low-confidence cells by mathematical necessity of the reference-selection rule — this is documented in `validation_report.json`. Self-verified the report's flagged count, top-5 severity list, and per-dimension spot checks against the CSV with zero discrepancies, then closed a completeness gap (7 of 12 roles were not individually named in the narrative) by adding an explicit all-12-roles gender table before finalizing the rubric score at 5.0/5 — no further iteration rounds were needed.

## Recommendations
- Review Financial Analyst screening criteria for the Female/Male selection-rate gap (highest-confidence, most severe adequately-sized finding).
- Investigate the under-30 age-bracket and Hispanic/Latino / Black race-ethnicity gaps at the process level across the whole applicant pool, since these are large-sample, statistically significant, and not concentrated in any single role.
- Grow applicant-pool size before drawing conclusions on Non-binary gender, Native American, and disability/veteran-status minority cells in every role — these are structurally too small (often n<10) to support any inference at the current sample size.
- Upstream improvement: capture demographic data at a more granular, consistently completed level (especially disability/veteran status, which skew heavily toward "No") so future audits have larger denominators and fewer low-confidence cells.

## Limitations
- The rubric and programmatic checks validate internal consistency and statistical correctness; they do not and cannot establish whether any flagged disparity reflects a discriminatory process versus a confounded but legitimate factor (e.g., role-specific requirements not captured in this dataset).
- This is a synthetic dataset built to test the audit methodology, not a real employer's applicant data — absolute findings should not be generalized beyond this run.
- Low-confidence findings (91 of 104 flagged rows) are directional only; no significance test is meaningful below n=30, so they cannot be escalated into firm conclusions no matter how extreme the observed ratio looks.
