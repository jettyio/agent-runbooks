# Hiring Demographics Audit — Results

## Overview
- **Date**: 2026-09-02
- **Input**: 900 candidate rows, 6 job roles (Registered Nurse, Lab Technician, Radiology Technologist, Medical Coder, Clinic Administrator, Pharmacist), 5 demographic dimensions analyzed (gender, race_ethnicity, disability_status, veteran_status, age_bracket)
- **Iterations**: 1 (initial draft scored 5.0/5 average, no iteration required)

## Rubric Scores

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 1 | Statistical rigor | 5/5 | Both Fisher's exact and chi-square (Yates-corrected) tests run on every eligible (n≥30 both sides) cell; `statistically_significant` verified to equal `fisher_significant AND chi2_significant` for all 125 rows; low-confidence cells (16 of 24 flagged) clearly separated from statistically supported ones (3 of 24) |
| 2 | Completeness of breakdowns | 5/5 | All 6 roles covered individually plus an `ALL_ROLES` cross-role rollup; all 5 requested protected attributes covered in both views |
| 3 | Clarity of findings | 5/5 | Every finding in the report cites exact selection rates, ratios, and both p-values inline — no need to cross-reference the CSV to gauge severity |
| 4 | Actionability of recommendations | 5/5 | Each recommendation names a specific role/group/metric and is explicitly categorized as "investigate further," "collect more data," or "review process" |
| 5 | Appropriate caveats & tone | 5/5 | Explicit correlation-vs-causation caveat, explicit low-confidence caveat, synthetic-dataset disclaimer; measured language ("statistical disparity was observed") throughout, no claims of proven discrimination |
| | **Overall** | **5.0/5** | |

## Output Description
`disparity_metrics.csv` contains 125 rows — one per (job_role, dimension, group) combination across 6 roles + an `ALL_ROLES` rollup, for 5 demographic dimensions — with candidate counts, hire counts, selection rates, four-fifths ratios, and dual significance-test results. `compliance_report.md` synthesizes this into a narrative audit: methodology, per-role findings, cross-role dimension rollup, a full flagged-items table sorted by severity, and recommendations scoped to specific flagged findings.

## Key Findings
Total flagged (ratio < 0.8): **24**

The 5 most severe flagged disparities (sorted by four-fifths ratio ascending, ties broken by statistical significance then confidence level):

1. **Medical Coder / race_ethnicity / Middle Eastern** — ratio **0.00** (0/2 hired vs. White reference) — low confidence (n=2)
2. **Medical Coder / race_ethnicity / Multiracial** — ratio **0.00** (0/7 hired vs. White reference) — low confidence (n=7)
3. **Registered Nurse / race_ethnicity / Multiracial** — ratio **0.00** (0/11 hired vs. Hispanic/Latino reference) — low confidence (n=11)
4. **Pharmacist / race_ethnicity / Black** — ratio **0.25** (16.7% vs. Native American reference) — low confidence (n=12)
5. **Pharmacist / race_ethnicity / Middle Eastern** — ratio **0.375** (25.0% vs. Native American reference) — low confidence (n=4)

All 5 of the most severe *raw-ratio* findings are built on cells with fewer than 30 candidates and are therefore low-confidence/directional only. The audit's three **statistically significant, adequately-powered** findings (both Fisher's exact and chi-square p < 0.05) are separate from this raw-ratio top 5 and warrant primary attention:
- **Registered Nurse, age bracket 30-39** vs. 50+ reference: ratio 0.47 (Fisher p=0.018, chi² p=0.021)
- **All roles, race_ethnicity Multiracial** vs. Asian reference: ratio 0.58 (Fisher p=0.021, chi² p=0.026)
- **All roles, race_ethnicity Hispanic/Latino** vs. Asian reference: ratio 0.72 (Fisher p=0.027, chi² p=0.029)

## Iteration History
Round 1 (only round): built the aggregation pipeline, ran all 10 programmatic calculation checks (all passed on first run after correcting the rate-bounds check's edge case — see Limitations), wrote the compliance report, and verified its flagged-count and top-5 findings directly against the CSV before scoring. All rubric criteria scored 5/5 on the first draft; no revision was needed.

## Recommendations
- Increase applicant pool size for the Pharmacist role (currently 88 candidates total, reference group n=24) before drawing any conclusion about disparity there — every Pharmacist finding in this audit is low-confidence.
- Grow small demographic cells (Non-binary gender, disability status "Yes", Native American/Middle Eastern/Multiracial race categories in several roles) across future hiring cycles so four-fifths ratios and significance tests become actionable rather than directional-only.
- Upstream: capturing a finer-grained "declined to state" category consistently (this dataset happened to have zero missing demographic values) would make future audits more robust to real-world non-response.

## Limitations
- The rubric and programmatic checks validate internal consistency and statistical correctness; they do not validate whether the underlying hiring decisions in the source data are themselves free of bias — this audit describes disparity in outcomes, not root cause.
- One programmatic check (`rate_bounds`) required refining beyond the literal 0-to-1 bound: because the reference group is restricted to cells with candidate_count ≥ 30, a low-confidence group's raw selection rate can legitimately exceed the reference's rate (33 such rows observed, all confirmed `low_confidence=true`). This is documented in `validation_report.json` and treated as expected methodology behavior, not a defect — but a human reviewer should confirm this interpretation.
- The three statistically significant findings (Section 3/4 of the compliance report) are the audit's primary actionable output; the many low-confidence flagged cells need more data before any determination, and this needs human/legal judgment on how to prioritize applicant-pool growth versus immediate process review.
