# Hiring Demographics Compliance/Fairness Audit

**Prepared for:** HR / Legal review
**Scope:** Candidate-level hiring outcomes across 12 job roles, cross-tabulated by five demographic dimensions
**Disparity threshold:** Four-fifths rule (ratio < 0.80 flagged) | **Minimum group size for reliable inference:** 30 candidates

---

## 1. Methodology

### 1.1 Dataset

- **Source:** `synthetic_cvs_hiring.csv`-equivalent dataset uploaded for this run (1,000 candidate rows, one row per candidate, 12 distinct `role_applied` values). This is a **synthetic** dataset created for audit-methodology testing, not a real applicant population — findings illustrate the analytical method, not an actual EEOC/OFCCP filing.
- **Row counts:** 1,000 candidates loaded; 1,000 retained after validating `role_applied` and `hired` were both present (0 rows dropped for missing role or outcome).
- **Outcome field:** `hired` was supplied as literal `Yes`/`No` strings and coerced to boolean. `disability_status`, `veteran_status`, and `referred` were coerced the same way.
- **Missing/declined demographic data:** No rows had missing values in `gender`, `race_ethnicity`, `disability_status`, or `veteran_status` in this run. Had any existed, they would have been retained as an explicit `"Declined to state"` group rather than dropped, consistent with treating non-disclosure as its own category.
- **Age brackets:** the raw dataset only contains numeric `age`. Candidates were bucketed once, consistently, into: **`<30`** (age < 30), **`30-39`** (30 ≤ age < 40), **`40-49`** (40 ≤ age < 50), **`50+`** (age ≥ 50). These same buckets are used in both `disparity_metrics.csv` and this report.
- **Group sizes per role:** roles range from ~75 to ~96 candidates each (average ≈83). Because demographic groups (especially minority race/ethnicity categories, disability status = Yes, veteran status = Yes, and Non-binary gender) are a further subdivision of an already-small per-role population, **most within-role demographic cells fall below the n=30 reliability threshold** — this is expected and is exactly why a cross-role rollup (`ALL_ROLES`) is reported alongside each role.
- CV-derived fields (education, GPA, years of experience, skills, certifications, `cv_text`) were **not** used in the core disparity calculation; they are referenced below only where they help interpret a flagged finding.

### 1.2 Disparity metric

For each **(job role, demographic dimension, group)** cell we computed the **selection rate** (hires ÷ candidates). Within each (role, dimension) cell, the **reference group** is the group with the highest selection rate **among groups that meet the n≥30 minimum**; if no group in the cell reaches 30, the reference falls back to the highest-rate group overall and every row in that cell is marked `low_confidence = true`. Ties are broken deterministically: larger `candidate_count` wins, then alphabetically-first group name — any cell where this fired is marked `reference_group_tie_broken = true` in the CSV.

The **four-fifths ratio** = group selection rate ÷ reference group selection rate. A ratio below **0.80** is `flagged`.

### 1.3 Statistical significance

For every cell where **both** the group and its reference group meet n≥30, we ran two independent tests on the 2×2 hired/not-hired table against the reference group: **Fisher's exact test** (two-sided) and a **Pearson chi-square test with Yates' continuity correction**. A finding is marked `statistically_significant = true` only if **both** tests agree at p < 0.05. Both p-values are always reported side-by-side — no single test is used to decide significance. Cells below the size threshold (`low_confidence = true`) do not receive p-values; significance testing is not meaningful on samples that small, and this is flagged rather than silently computed anyway.

### 1.4 Limitations

- **Small-cell instability:** a demographic group with, say, 3 candidates can show a 0% or 100% selection rate purely from noise. All such cells are marked `low_confidence` in the data and are reported for transparency but should be treated as **directional only, not conclusive**.
- **A four-fifths ratio above 1.0 in a low-confidence cell is expected, not an error:** because the reference group must itself have ≥30 candidates, a tiny subgroup can occasionally out-perform it, producing a ratio > 1. This does not indicate a data or calculation error — it is a direct consequence of restricting the reference to an adequately-sized comparison group.
- **Correlation ≠ causation:** a statistically significant disparity in aggregate hiring outcomes is not, by itself, evidence of discriminatory intent or a violation. It indicates a pattern that warrants further review of the underlying process (sourcing, screening criteria, interview stages), not a legal conclusion.
- This audit does not control for role-specific qualification requirements (e.g., years of experience, degree field) beyond what is implicit in who applied; where a CV-derived field plausibly explains a flagged gap, it is noted in Section 2.

---

## 2. Findings by Job Role

Across the 12 individual roles (excluding the `ALL_ROLES` rollup), **13 of 100 role-level, adequately-sized (non-low-confidence) cells were flagged**, all in the **gender** dimension — no role-level cell in `race_ethnicity`, `disability_status`, or `veteran_status` had both groups large enough to be non-low-confidence *and* fall below the 0.80 ratio (age_bracket had none non-low-confidence at all at the individual-role level; role populations of ~80 split four ways rarely clear n=30 per bucket).

**Statistically significant, adequately-sized findings by role (both tests p<0.05):**

- **Financial Analyst — gender, Female:** 47 candidates, 13 hires, selection rate 27.7% vs. Male reference (46 candidates, 63.0% selection rate). Four-fifths ratio **0.44** (well below 0.80). Fisher's exact p = **0.0008**, chi-square p = **0.0013** — statistically significant by both tests. This is the most severe *adequately-sized* finding in the entire dataset.

**Other role-level flagged-but-not-statistically-significant gender gaps** (ratio < 0.80, both groups n≥30, but p ≥ 0.05 on at least one test — treat as suggestive, not confirmed):

| Role | Group | Selection rate | Reference (rate) | Ratio | Fisher p | Chi² p |
|---|---|---|---|---|---|---|
| Business Analyst | Female | 21.9% (32) | Male (40.5%) | 0.54 | 0.133 | 0.149 |
| Product Manager | Female | 20.0% (35) | Male (31.7%) | 0.63 | 0.302 | 0.371 |
| HR Coordinator | Male | 36.4% (44) | Female (50.0%) | 0.73 | 0.260 | 0.317 |
| Marketing Specialist | Female | 35.1% (37) | Male (45.5%) | 0.77 | 0.373 | 0.475 |

For these four, the direction is consistent with the significant Financial Analyst finding, but neither test crosses the significance threshold individually for these smaller effect sizes — larger applicant pools would be needed to confirm whether this is a real pattern.

**Small-cell (low-confidence) role-level flags:** the remaining 91 flagged rows are all in cells below n=30 (frequently `Non-binary` gender — 1–4 candidates per role — and small race/ethnicity or disability/veteran categories with a single 0-hire or 100%-hire outcome). These appear in every role and are reported in full in `disparity_metrics.csv`, but by design carry no p-values and should not be read as evidence of anything on their own; see Section 4 for the complete list and Section 1.4 for why they occur.

**Interpretation note (Financial Analyst):** the CV-derived fields do not obviously explain the gap — median years-of-experience and GPA for Female Financial Analyst applicants in this dataset are comparable to Male applicants, so the disparity is not simply an artifact of a weaker underlying applicant pool. This makes it the top candidate for a targeted screening-process review (Section 6).

### 2.1 All 12 roles at a glance (gender — the only dimension with adequately-sized comparisons at individual-role level)

Every role has at least 30 Male and 30 Female candidates, so gender is the one dimension where a same-role, adequately-sized comparison is possible everywhere. The table below covers all 12 roles (Non-binary omitted here as it is a low-confidence cell — 1 to 4 candidates — in every single role; see `disparity_metrics.csv` for those rows):

| Role | Female N | Female rate | Male N | Male rate | Reference | Ratio | Flagged |
|---|---|---|---|---|---|---|---|
| Accountant | 39 | 38.5% | 44 | 45.5% | Male | 0.85 | No |
| Business Analyst | 32 | 21.9% | 42 | 40.5% | Male | **0.54** | **Yes** |
| Customer Success Manager | 47 | 38.3% | 32 | 46.9% | Male | 0.82 | No |
| Data Analyst | 43 | 37.2% | 39 | 33.3% | Female | 0.90 | No |
| Financial Analyst | 47 | 27.7% | 46 | 63.0% | Male | **0.44** | **Yes** |
| HR Coordinator | 36 | 50.0% | 44 | 36.4% | Female | **0.73** | **Yes** |
| Marketing Specialist | 37 | 35.1% | 44 | 45.5% | Male | **0.77** | **Yes** |
| Operations Manager | 41 | 36.6% | 34 | 44.1% | Male | 0.83 | No |
| Product Manager | 35 | 20.0% | 41 | 31.7% | Male | **0.63** | **Yes** |
| Sales Representative | 39 | 35.9% | 47 | 42.6% | Male | 0.84 | No |
| Software Engineer | 42 | 30.9% | 39 | 30.8% | Female | 0.99 | No |
| UX Designer | 36 | 38.9% | 45 | 42.2% | Male | 0.92 | No |

Five of 12 roles show a flagged gender gap; only Financial Analyst clears both significance tests (Section 2 above). Accountant, Customer Success Manager, Data Analyst, Operations Manager, Sales Representative, Software Engineer, and UX Designer show **no flagged gender gap** (ratios 0.82–0.99) and have **no other adequately-sized dimension to report** — every race/ethnicity, disability, veteran, and age cell in those seven roles falls below the n=30 minimum (a direct consequence of splitting an ~80-candidate role population across 6-8 demographic categories per dimension). This is why Section 3's cross-role rollup, not the per-role view, is the reliable source for race/ethnicity, age, disability, and veteran-status findings — confirmed programmatically: for `race_ethnicity` and `age_bracket`, the *only* non-low-confidence role-level rows in the entire dataset are trivial self-comparisons (a single group in that cell happens to clear n=30 and is therefore compared against itself, ratio = 1.0 by definition) — there is not one role in this dataset where two different race/ethnicity or age groups both independently clear n=30.

---

## 3. Findings by Demographic Dimension (Cross-Role Rollup)

The `ALL_ROLES` rollup pools all 1,000 candidates per dimension, which is where n≥30 is achievable for every group and where the clearest, most reliable disparity signal in this dataset lives.

### Gender (rollup)
- Male: 497 candidates, 42.1% selection rate (reference).
- Female: 474 candidates, 34.4% selection rate. Ratio **0.82** — just above the 0.80 threshold, **not flagged** at the rollup level, though Fisher/chi² both show p<0.05 (p=0.015 / p=0.017), meaning the gap is statistically real but not large enough to trip four-fifths.
- Non-binary: 29 candidates, 27.6% selection rate. Ratio 0.66, **flagged**, but `low_confidence` (n<30) — directional only.

### Race/Ethnicity (rollup) — the strongest pattern in this audit
White is the reference group (387 candidates, 46.5% selection rate). **Every other race/ethnicity category is flagged**, and four of six are statistically significant by both tests:

| Group | N | Selection rate | Ratio | Fisher p | Chi² p | Sig. (both) |
|---|---|---|---|---|---|---|
| Hispanic/Latino | 160 | 26.9% | **0.58** | 0.000023 | 0.000032 | **Yes** |
| Black | 145 | 33.8% | **0.73** | 0.010 | 0.011 | **Yes** |
| Multiracial | 67 | 32.8% | 0.71 | 0.045 | 0.052 | No (fails chi²) |
| Middle Eastern | 58 | 34.5% | 0.74 | 0.091 | 0.115 | No |
| Asian | 157 | 36.3% | 0.78 | 0.036 | 0.038 | **Yes** |
| Native American | 26 | 34.6% | 0.74 | — | — | low_confidence (n<30) |

Hispanic/Latino and Black candidates show the largest, most statistically robust gaps relative to White candidates — both comfortably exceed n=30 on both sides and pass both significance tests with very low p-values. This is the single clearest disparity signal in the dataset and it is consistent across the applicant pool as a whole, not an artifact of any one role.

### Age bracket (rollup)
40-49 is the reference group (210 candidates, 50.5% selection rate — notably the highest of any bracket). All three other brackets are flagged and statistically significant:

| Bracket | N | Selection rate | Ratio | Fisher p | Chi² p |
|---|---|---|---|---|---|
| <30 | 191 | 25.1% | **0.50** | <0.0001 | <0.0001 |
| 30-39 | 257 | 36.6% | 0.72 | 0.0027 | 0.0034 |
| 50+ | 342 | 38.6% | 0.76 | 0.0079 | 0.0081 |

The under-30 bracket shows the largest gap of any dimension in the rollup view (ratio 0.50) and is highly statistically significant, on a large sample (n=191) — this is not a low-confidence artifact.

### Disability status (rollup)
No: 875 candidates, 38.4% (reference). Yes: 125 candidates, 35.2%, ratio 0.92 — **not flagged**, not significant (p=0.55 both tests).

### Veteran status (rollup)
No: 935 candidates, 38.1% (reference). Yes: 65 candidates, 36.9%, ratio 0.97 — **not flagged**, not significant (p=0.90/0.96).

---

## 4. Flagged Items — Full List (Sorted by Severity)

**Total flagged (ratio < 0.80): 104 of 234 rows** (91 low-confidence, 13 adequately-sized; 7 of the 13 are statistically significant by both tests).

Below are the 5 lowest-ratio flagged rows in the dataset overall (strict sort by `four_fifths_ratio` ascending, ties broken by `statistically_significant` [true first], then `low_confidence` [false first], then larger `candidate_count`, then alphabetically). **All five of these extreme (ratio = 0.00) rows are small, `low_confidence` cells where a handful of candidates in a minority category happened to receive zero offers** — they are the mathematically most extreme ratios in the table, but the smallest and least reliable. They are reported here for completeness (an audit should not hide its most extreme numbers), but the findings that actually warrant HR/legal attention are the statistically significant, adequately-sized findings in Sections 2–3 below this table.

| Rank | Role | Dimension | Group | N | Hires | Selection rate | Reference | Ratio | Confidence |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Business Analyst | race_ethnicity | Black | 7 | 0 | 0% | White | 0.00 | Low (n=7) |
| 2 | Business Analyst | race_ethnicity | Middle Eastern | 7 | 0 | 0% | White | 0.00 | Low (n=7) |
| 3 | HR Coordinator | race_ethnicity | Multiracial | 7 | 0 | 0% | Middle Eastern | 0.00 | Low (n=7) |
| 4 | Software Engineer | race_ethnicity | Hispanic/Latino | 7 | 0 | 0% | White | 0.00 | Low (n=7) |
| 5 | Business Analyst | disability_status | Yes | 5 | 0 | 0% | No | 0.00 | Low (n=5) |

**Statistically-significant, adequately-sized flagged findings (the actionable set), sorted by ratio:**

| Role | Dimension | Group | N | Selection rate | Reference | Ratio | Fisher p | Chi² p |
|---|---|---|---|---|---|---|---|---|
| Financial Analyst | gender | Female | 47 | 27.7% | Male (63.0%) | **0.44** | 0.0008 | 0.0013 |
| ALL_ROLES | age_bracket | <30 | 191 | 25.1% | 40-49 (50.5%) | **0.50** | <0.0001 | <0.0001 |
| ALL_ROLES | race_ethnicity | Hispanic/Latino | 160 | 26.9% | White (46.5%) | **0.58** | 0.00002 | 0.00003 |
| ALL_ROLES | race_ethnicity | Black | 145 | 33.8% | White (46.5%) | 0.73 | 0.0104 | 0.0111 |
| ALL_ROLES | age_bracket | 30-39 | 257 | 36.6% | 40-49 (50.5%) | 0.72 | 0.0027 | 0.0034 |
| ALL_ROLES | age_bracket | 50+ | 342 | 38.6% | 40-49 (50.5%) | 0.76 | 0.0079 | 0.0081 |
| ALL_ROLES | race_ethnicity | Asian | 157 | 36.3% | White (46.5%) | 0.78 | 0.0356 | 0.0375 |

Flagged-but-not-significant and low-confidence rows in full are in `disparity_metrics.csv`.

---

## 5. Caveats

- **Statistical disparity is not proof of discriminatory intent.** The findings above describe patterns in aggregate outcome data; they do not, by themselves, establish that any individual hiring decision was made on a prohibited basis. Determining causation requires review of the actual decision-making process (job-relatedness of criteria, consistency of application, individual case review) — outside the scope of this statistical audit.
- **Low-confidence findings need more data before any action is taken.** 91 of the 104 flagged rows are below the n=30 threshold and are reported for transparency only; treating a 5- or 7-candidate cell as evidence of a problem would itself be a statistical error.
- **This is a synthetic dataset** built for testing this audit methodology, not a real applicant population — it should not be cited as evidence about any actual employer's practices.
- The four-fifths rule is a widely used **screening heuristic**, not itself a legal standard of proof, and its output should be read alongside (not instead of) the significance tests and confidence flags above.

---

## 6. Recommendations

1. **Review Financial Analyst screening/interview criteria for gender-based outcomes.** This is the single most severe, statistically robust, adequately-sized finding (Female selection rate 27.7% vs. Male 63.0%, ratio 0.44, p<0.001 on both tests). Recommended action: audit the specific screening rubric, interviewer composition, and pass/fail stage breakdown for this role; the CV-derived fields do not show an obvious qualifications gap that would explain the difference.
2. **Investigate the under-30 age-bracket gap at the cross-role level.** Ratio 0.50 vs. the 40-49 reference, on a large, reliable sample (n=191), p<0.0001. Recommended action: check whether entry-level candidates are being screened against criteria (e.g., years-of-experience minimums) that structurally disadvantage younger applicants regardless of demonstrated skill, and whether that criterion is job-related and consistently applied.
3. **Investigate Hispanic/Latino and Black candidate selection rates at the cross-role level.** Both show large, highly significant gaps versus White candidates (ratios 0.58 and 0.73, p<0.02 on both tests) on samples large enough to be reliable (n=160 and n=145). Recommended action: review sourcing channels and early-stage screening filters across roles for consistency of application across race/ethnicity groups; this pattern recurs across the applicant pool rather than concentrating in one role, which points toward a process-level rather than role-specific review.
4. **Collect more data before drawing conclusions on:** Business Analyst (Female, ratio 0.54, p=0.13–0.15 — directionally consistent with the Financial Analyst finding but underpowered at n=32), Product Manager and Marketing Specialist Female gaps, and every `low_confidence` cell (Non-binary gender, Native American, disability/veteran-status minority groups) — these need a larger applicant pool per role/group before any inference is reliable. Recommended action: track these categories longitudinally as pool sizes grow rather than acting on the current snapshot.
5. **Do not act on the four Section 4 zero-hire cells (n≤7) as standalone evidence.** They are mathematically the most extreme ratios in the table but the least reliable; they should be re-examined only once/if those specific (role, group) cells accumulate more applicants.
6. **Improve demographic data granularity where feasible.** Race/ethnicity and gender are well-populated in this dataset; disability and veteran status skew heavily toward "No" with small "Yes" minorities, which limits confidence for those dimensions specifically — a larger or longer-accumulated applicant sample would materially improve the reliability of any future audit on those two dimensions.
