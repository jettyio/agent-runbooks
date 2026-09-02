# Hiring Demographics Audit — Compliance Report

**Prepared for:** HR / Legal review
**Dataset:** Healthcare hiring candidate records (synthetic)
**Scope:** 900 candidates across 6 job roles, evaluated against 5 protected-attribute dimensions

---

## 1. Methodology

### 1.1 Dataset

The input dataset (`healthcare_hiring_900.csv`) contains 900 candidate records, one row per candidate, spanning 6 job roles:

| Job Role | Candidates | Hires | Overall Selection Rate |
|---|---|---|---|
| Clinic Administrator | 135 | 37 | 27.4% |
| Lab Technician | 186 | 74 | 39.8% |
| Medical Coder | 136 | 53 | 39.0% |
| Pharmacist | 88 | 39 | 44.3% |
| Radiology Technologist | 150 | 61 | 40.7% |
| Registered Nurse | 205 | 70 | 34.1% |
| **Total** | **900** | **334** | **37.1%** |

No rows were dropped: `role_applied` and `hired` were populated for all 900 candidates, and there was no missing demographic data (`gender`, `race_ethnicity`, `disability_status`, `veteran_status`, `age` were fully populated). The only column with missingness was `certifications` (167 blanks, expected for candidates who listed none — not used in this analysis). Because the dataset had complete demographic data, no "Declined/Unknown" category was needed in practice, though the pipeline supports one and would use it if future data collection introduces missingness.

`hired`, `disability_status`, `veteran_status`, and `referred` were coerced from literal `Yes`/`No` strings to booleans before aggregation.

### 1.2 Age brackets

The raw dataset provides numeric `age` (range 22–63, mean 39.4) with no pre-built bracket. We derived `age_bracket` using fixed boundaries applied consistently throughout this analysis and the underlying metrics table:

- `<30`
- `30-39`
- `40-49`
- `50+`

### 1.3 Disparity metrics

For each (job role × demographic dimension) combination, and for a role-agnostic rollup (`job_role = ALL_ROLES`), we computed:

- **Selection rate** — hires / candidates, per group.
- **Reference group** — the group with the highest selection rate in that cell. Ties are broken deterministically: (a) larger candidate count wins, (b) if still tied, alphabetically-first group name wins. Rows affected by a tie-break carry `reference_group_tie_broken = true` in the metrics table.
- **Four-fifths ratio** — `group_selection_rate / reference_group_selection_rate`. A ratio below **0.80** is `flagged` per the standard four-fifths (80%) rule used in U.S. adverse-impact screening (EEOC Uniform Guidelines heuristic — see caveats below).
- **Statistical significance** — for every cell where *both* the group and its reference group have at least **30** candidates, we ran two tests on the 2×2 (hired/not-hired × group/reference) table: a two-sided **Fisher's exact test** and a **Pearson chi-square test with Yates' continuity correction**. A cell is marked `statistically_significant = true` only if **both** tests independently agree (p < 0.05 on both). This conservative, dual-test rule was applied uniformly — no discretionary choice of test was made per cell.
- **Low confidence** — any cell where the group or its reference group has fewer than 30 candidates is marked `low_confidence = true`. These cells are still reported (transparency), but significance tests were not run on them (results would not be statistically meaningful), and they should be read as directional signals only, not conclusive findings.

The full structured output is in `disparity_metrics.csv` (125 rows: 6 roles × 5 dimensions, plus 1 rollup × 5 dimensions, with one row per group). All 10 programmatic integrity checks (row completeness, count conservation, rate bounds, flag consistency, low-confidence consistency, reference-group correctness, tie-break determinism, rollup literal correctness, dual-test presence, significance-combination rule) passed against this table — see `validation_report.json`.

### 1.4 Limitations of this methodology

- The four-fifths rule is a screening heuristic, not a legal determination of discrimination. It is sensitive to small reference-group sizes (see §3.2).
- This is a **synthetic dataset** built for audit-methodology demonstration, not a real EEOC/OFCCP filing.
- CV-derived fields (education, GPA, years of experience, certifications, etc.) were not used in the core disparity calculation; they are referenced below only where they help interpret a specific flagged finding.

---

## 2. Findings by Job Role

Below, selection rates are reported by dimension for each role; only findings with a four-fifths ratio below 0.80 are called "flagged." Full detail for every group is in `disparity_metrics.csv`.

**Clinic Administrator** (n=135, 27.4% hired — the lowest-hiring role overall). `race_ethnicity` shows the widest spread: Native American candidates (n=2, both hired) sit at 100% and become the reference group for every race_ethnicity comparison in this role, driving ratios as low as **0.15** for Hispanic/Latino candidates (n=65, 15.4% selected) and **0.29–0.50** for Middle Eastern, White, Asian, Black, and Multiracial candidates. All of these cells are `low_confidence` (small group and/or reference-group size), so none carry a significance test. `age_bracket` also shows a gradient — 50+ candidates have the highest rate, with 30-39, 40-49, and <30 all flagged (ratios 0.67–0.73), all low-confidence. `disability_status` (No group flagged at 0.69 vs. small Yes reference) and `gender` (Non-binary flagged at 0.71, n=5) are also low-confidence.

**Lab Technician** (n=186, 39.8% hired). Similar `race_ethnicity` pattern with Native American (n=5) as reference; Multiracial (0.48), Hispanic/Latino (0.52), Black (0.61), and White (0.63) are flagged, all low-confidence. `age_bracket`: 50+ is flagged at 0.48 against a 40-49 reference — low-confidence. `disability_status`: Yes group (n=18) flagged at 0.53 vs. No — low-confidence. `gender`: Non-binary (n=10) flagged at 0.71 — low-confidence.

**Medical Coder** (n=136, 39.0% hired). The most extreme ratios in the dataset appear here: Middle Eastern (n=2, 0 hires) and Multiracial (n=7, 0 hires) candidates show a ratio of **0.00** against the Native American reference (n=2, both hired) — both cells are low-confidence given the tiny sample sizes on both sides of the comparison. White (0.30), Hispanic/Latino (0.43), Asian (0.48), and Black (0.54) are also flagged, all low-confidence. `veteran_status`: non-veterans flagged at 0.64 against a very small veteran reference group (n=12) — low-confidence.

**Pharmacist** (n=88, 44.3% hired — the highest-hiring role overall, smallest role by volume). Black (n=12, 0.25) and Middle Eastern (n=4, 0.375) candidates are flagged against the Native American reference (n=3) — low-confidence given very small cells throughout. `age_bracket`: both `<30` (0.53) and `50+` (0.58) are flagged relative to a 40-49 reference — low-confidence (each group below 30). `gender`: Non-binary (n=4) flagged at 0.52 — low-confidence. `disability_status`: No group flagged at 0.68 vs. a small Yes reference (n=8) — low-confidence.

**Radiology Technologist** (n=150, 40.7% hired). `gender`: both Male (0.60) and Female (0.61) are flagged against a very small Non-binary reference (n=3, 2 hires) — low-confidence and highly reference-driven (see §3.2). `race_ethnicity`: Asian (0.67) and Multiracial (0.75) flagged against Native American reference (n=4) — low-confidence.

**Registered Nurse** (n=205, 34.1% hired, the largest role by volume). This role produced the **only statistically significant, non-low-confidence flagged finding** in the entire audit: candidates aged **30-39** (n=66, 22.7% selected) had a four-fifths ratio of **0.47** against the **50+** reference group (n=31, 48.4% selected) — **Fisher's exact p = 0.0176, chi-square p = 0.0207** (both < 0.05, so `statistically_significant = true`). The `<30` age group (n=57, 29.8% selected, ratio 0.62) also fell below the four-fifths line but did **not** reach significance (Fisher p = 0.1062, chi-square p = 0.1343). Notably, for this role, mean `years_experience` rises sharply with age bracket (30-39: 6.4 yrs; 40-49: 12.6 yrs; 50+: 20.6 yrs), so age and tenure are highly correlated — the disparity may substantially reflect an experience gap rather than age itself (see Recommendations). `race_ethnicity` for this role also shows Multiracial (n=11, 0 hires, ratio 0.00) and Black (n=31, ratio 0.58) flagged, both low-confidence.

---

## 3. Findings by Demographic Dimension (Cross-Role Rollup)

The `ALL_ROLES` rollup pools all 900 candidates per dimension, giving much larger cell sizes and therefore more statistically reliable (though role-blind) comparisons.

### 3.1 Gender (rollup)
Female (n=471, 36.1%), Male (n=401, 37.9%), Non-binary (n=28, 42.9%, reference group). No rollup ratio falls below 0.80 (Female: 0.84, Male: 0.88) — **not flagged** at the aggregate level, though the Non-binary reference group itself is `low_confidence` (n=28 < 30), so the rollup ratios are marked low-confidence and directional only. At the per-role level, Non-binary reference groups are extremely small (n=3–10), producing several flagged-but-low-confidence comparisons for Male/Female candidates in Radiology Technologist and Registered Nurse — these should not be read as evidence of disparity against Male/Female candidates; they reflect noise in a very small reference cell.

### 3.2 Race/Ethnicity (rollup) — requires a structural caveat
This is where the analysis surfaces the most flagged cells (34 of 57), and nearly every one shares a common driver: **Native American candidates (n=24 overall, 2–8 per role) have the highest selection rate in every single role and in the rollup**, and consequently become the reference group in all 7 race_ethnicity comparisons. Because this group is small everywhere it appears, its selection rate is unstable — a difference of one or two hires shifts it substantially. At the rollup level: Native American 62.5% (reference), Asian 44.8% (ratio 0.72, flagged), Black 38.9% (0.62, flagged), White 35.8% (0.57, flagged), Middle Eastern 38.8% (0.62, flagged), Hispanic/Latino 32.3% (0.52, flagged), Multiracial 25.9% (0.41, flagged). **All race_ethnicity rollup rows are `low_confidence`** because the reference group (Native American, n=24) is below the 30-candidate threshold — none of these comparisons could be statistically tested, and none should be treated as confirmed disparities. The pattern (every non-reference group flagged) is itself a signal that the reference point, not necessarily the other groups, is the unstable element. See Recommendations for how to address this without more data collection.

### 3.3 Disability Status (rollup)
No (n=792, 37.6%, reference) vs. Yes (n=108, 33.3%, ratio 0.89) — **not flagged**, and this rollup comparison is high-confidence (both groups ≥30). At the per-role level, the Yes group falls below 30 in every single role (8–30 candidates), so all per-role disability comparisons are low-confidence; several are flagged directionally (Lab Technician 0.53, Pharmacist 0.68, Clinic Administrator 0.69) but none are statistically testable.

### 3.4 Veteran Status (rollup)
Yes (n=62, 45.2%, reference) vs. No (n=838, 36.5%, ratio 0.81) — **not flagged** (just above threshold) and high-confidence. Per-role veteran subgroups are all below 30 (2–20 candidates), so per-role veteran comparisons (e.g., Medical Coder 0.64, Registered Nurse 0.73) are low-confidence and directional only.

### 3.5 Age Bracket (rollup)
40-49 (n=222, 42.8%, reference), 30-39 (n=260, 35.8%, ratio 0.84), <30 (n=226, 34.5%, ratio 0.81), 50+ (n=192, 35.4%, ratio 0.83). **No rollup age cell is flagged**, and all four rollup cells are high-confidence (all groups ≥30). This makes the Registered Nurse-specific finding (§2, 30-39 ratio 0.47, significant) notable: it is a role-specific effect that does not appear in the pooled data, meaning it is diluted by other roles at the aggregate level and should be examined at the role level, not dismissed because the rollup looks flat.

---

## 4. Flagged Items (Full List, Most Severe First)

57 of 125 rows (45.6%) in `disparity_metrics.csv` are flagged (`four_fifths_ratio < 0.80`). Sorted by ratio ascending (most severe first), with statistically-significant and higher-confidence findings prioritized among ties. Only **1 of 57** flagged rows is both non-low-confidence and statistically significant (highlighted).

| Job Role | Dimension | Group | n | Selection Rate | Reference Group | 4/5 Ratio | Fisher p | Chi2 p | Confidence |
|---|---|---|---|---|---|---|---|---|---|
| Medical Coder | race_ethnicity | Middle Eastern | 2 | 0.0% | Native American | 0.000 | — | — | LOW (n<30) |
| Medical Coder | race_ethnicity | Multiracial | 7 | 0.0% | Native American | 0.000 | — | — | LOW (n<30) |
| Registered Nurse | race_ethnicity | Multiracial | 11 | 0.0% | Native American | 0.000 | — | — | LOW (n<30) |
| Clinic Administrator | race_ethnicity | Hispanic/Latino | 65 | 15.4% | Native American | 0.154 | — | — | LOW (n<30) |
| Pharmacist | race_ethnicity | Black | 12 | 16.7% | Native American | 0.250 | — | — | LOW (n<30) |
| Clinic Administrator | race_ethnicity | Middle Eastern | 7 | 28.6% | Native American | 0.286 | — | — | LOW (n<30) |
| Medical Coder | race_ethnicity | White | 53 | 30.2% | Native American | 0.302 | — | — | LOW (n<30) |
| Clinic Administrator | race_ethnicity | White | 28 | 32.1% | Native American | 0.321 | — | — | LOW (n<30) |
| Clinic Administrator | race_ethnicity | Asian | 11 | 36.4% | Native American | 0.364 | — | — | LOW (n<30) |
| Pharmacist | race_ethnicity | Middle Eastern | 4 | 25.0% | Native American | 0.375 | — | — | LOW (n<30) |
| Registered Nurse | gender | Female | 105 | 32.4% | Non-binary | 0.389 | — | — | LOW (n<30) |
| Registered Nurse | gender | Male | 94 | 33.0% | Non-binary | 0.396 | — | — | LOW (n<30) |
| ALL_ROLES | race_ethnicity | Multiracial | 54 | 25.9% | Native American | 0.415 | — | — | LOW (n<30) |
| Clinic Administrator | race_ethnicity | Black | 14 | 42.9% | Native American | 0.429 | — | — | LOW (n<30) |
| Medical Coder | race_ethnicity | Hispanic/Latino | 21 | 42.9% | Native American | 0.429 | — | — | LOW (n<30) |
| **Registered Nurse** | **age_bracket** | **30-39** | **66** | **22.7%** | **50+** | **0.470** | **0.0176** | **0.0207** | **Significant** |
| Lab Technician | race_ethnicity | Multiracial | 14 | 28.6% | Native American | 0.476 | — | — | LOW (n<30) |
| Lab Technician | age_bracket | 50+ | 84 | 29.8% | 40-49 | 0.479 | — | — | LOW (n<30) |
| Medical Coder | race_ethnicity | Asian | 27 | 48.1% | Native American | 0.481 | — | — | LOW (n<30) |
| Clinic Administrator | race_ethnicity | Multiracial | 8 | 50.0% | Native American | 0.500 | — | — | LOW (n<30) |
| ALL_ROLES | race_ethnicity | Hispanic/Latino | 195 | 32.3% | Native American | 0.517 | — | — | LOW (n<30) |
| Lab Technician | race_ethnicity | Hispanic/Latino | 29 | 31.0% | Native American | 0.517 | — | — | LOW (n<30) |
| Pharmacist | gender | Non-binary | 4 | 25.0% | Female | 0.523 | — | — | LOW (n<30) |
| Pharmacist | age_bracket | <30 | 20 | 30.0% | 40-49 | 0.525 | — | — | LOW (n<30) |
| Lab Technician | disability_status | Yes | 18 | 22.2% | No | 0.533 | — | — | LOW (n<30) |
| Medical Coder | race_ethnicity | Black | 24 | 54.2% | Native American | 0.542 | — | — | LOW (n<30) |
| ALL_ROLES | race_ethnicity | White | 313 | 35.8% | Native American | 0.573 | — | — | LOW (n<30) |
| Registered Nurse | race_ethnicity | Black | 31 | 29.0% | Native American | 0.581 | — | — | LOW (n<30) |
| Pharmacist | age_bracket | 50+ | 15 | 33.3% | 40-49 | 0.583 | — | — | LOW (n<30) |
| Radiology Technologist | gender | Male | 73 | 39.7% | Non-binary | 0.596 | — | — | LOW (n<30) |
| Lab Technician | race_ethnicity | Black | 22 | 36.4% | Native American | 0.606 | — | — | LOW (n<30) |
| Radiology Technologist | gender | Female | 74 | 40.5% | Non-binary | 0.608 | — | — | LOW (n<30) |
| Lab Technician | age_bracket | <30 | 42 | 38.1% | 40-49 | 0.614 | — | — | LOW (n<30) |
| Registered Nurse | age_bracket | <30 | 57 | 29.8% | 50+ | 0.616 | 0.1062 | 0.1343 | Not significant |
| ALL_ROLES | race_ethnicity | Middle Eastern | 49 | 38.8% | Native American | 0.620 | — | — | LOW (n<30) |
| ALL_ROLES | race_ethnicity | Black | 131 | 38.9% | Native American | 0.623 | — | — | LOW (n<30) |
| Lab Technician | race_ethnicity | White | 79 | 38.0% | Native American | 0.633 | — | — | LOW (n<30) |
| Medical Coder | veteran_status | No | 124 | 37.1% | Yes | 0.636 | — | — | LOW (n<30) |
| Pharmacist | race_ethnicity | White | 21 | 42.9% | Native American | 0.643 | — | — | LOW (n<30) |
| Clinic Administrator | age_bracket | 30-39 | 40 | 25.0% | 50+ | 0.667 | — | — | LOW (n<30) |
| Radiology Technologist | race_ethnicity | Asian | 21 | 33.3% | Native American | 0.667 | — | — | LOW (n<30) |
| Pharmacist | disability_status | No | 80 | 42.5% | Yes | 0.680 | — | — | LOW (n<30) |
| Clinic Administrator | age_bracket | 40-49 | 39 | 25.6% | 50+ | 0.684 | — | — | LOW (n<30) |
| Registered Nurse | race_ethnicity | White | 75 | 34.7% | Native American | 0.693 | — | — | LOW (n<30) |
| Clinic Administrator | disability_status | No | 119 | 26.1% | Yes | 0.695 | — | — | LOW (n<30) |
| Lab Technician | gender | Non-binary | 10 | 30.0% | Male | 0.711 | — | — | LOW (n<30) |
| Clinic Administrator | gender | Non-binary | 5 | 20.0% | Male | 0.714 | — | — | LOW (n<30) |
| ALL_ROLES | race_ethnicity | Asian | 134 | 44.8% | Native American | 0.716 | — | — | LOW (n<30) |
| Registered Nurse | veteran_status | No | 185 | 33.0% | Yes | 0.733 | — | — | LOW (n<30) |
| Clinic Administrator | age_bracket | <30 | 40 | 27.5% | 50+ | 0.733 | — | — | LOW (n<30) |
| Pharmacist | race_ethnicity | Hispanic/Latino | 22 | 50.0% | Native American | 0.750 | — | — | LOW (n<30) |
| Pharmacist | race_ethnicity | Multiracial | 6 | 50.0% | Native American | 0.750 | — | — | LOW (n<30) |
| Radiology Technologist | race_ethnicity | Multiracial | 8 | 37.5% | Native American | 0.750 | — | — | LOW (n<30) |
| Registered Nurse | race_ethnicity | Asian | 32 | 37.5% | Native American | 0.750 | — | — | LOW (n<30) |
| Radiology Technologist | race_ethnicity | White | 57 | 38.6% | Native American | 0.772 | — | — | LOW (n<30) |
| Registered Nurse | race_ethnicity | Hispanic/Latino | 36 | 38.9% | Native American | 0.778 | — | — | LOW (n<30) |
| Lab Technician | age_bracket | 30-39 | 31 | 48.4% | 40-49 | 0.780 | — | — | LOW (n<30) |

---

## 5. Recommendations

1. **Investigate further — Registered Nurse, age_bracket 30-39.** This is the only finding in the audit that is simultaneously flagged (ratio 0.47), non-low-confidence, and statistically significant on both tests (Fisher p=0.018, chi-square p=0.021). Before concluding this reflects age-based screening, review whether `years_experience` (which averages 6.4 years for this bracket vs. 20.6 years for 50+) is being used as a de facto proxy for age in screening or interview scoring. Recommend a structured review of RN screening criteria that separates years-of-experience weighting from age-correlated assumptions, and a sample audit of rejected 30-39 RN applications to check whether comparably-experienced older candidates were treated differently.

2. **Collect more data before drawing conclusions on race_ethnicity.** 34 of 57 flagged cells stem from `race_ethnicity`, and nearly all are driven by the Native American group (n=24 total, 2–8 per role) serving as an unstable reference point. This is a data-volume problem, not necessarily a hiring-process problem: recommend expanding sourcing/outreach to grow this applicant pool to a size that supports reliable comparison (target ≥30 per role), and in the interim, treat the current reference-group choice as provisional. Consider re-running the four-fifths comparison using the *largest* group (e.g., White, n=313) as an alternate reference point for a sensitivity check, since the rule does not mandate using the highest-rate group specifically.

3. **Review process, not headcount, for disability_status and veteran_status at the per-role level.** Both dimensions are well-powered at the rollup level (792/108 and 838/62) and show **no flagged disparity in the rollup** (ratios 0.89 and 0.81 respectively). The flagged per-role cells (e.g., Lab Technician disability Yes at 0.53, Medical Coder veteran No at 0.64) are artifacts of small per-role subgroup sizes, not a rollup-level pattern. Recommend monitoring these at the rollup level going forward rather than acting on per-role noise, and re-evaluating if per-role sample sizes grow.

4. **Gender findings do not warrant action at this sample size.** The rollup shows no flagged gender disparity (Female 0.84, Male 0.88 against a Non-binary reference of n=28). Per-role flags against Non-binary reference groups of 3–10 candidates (Radiology Technologist, Pharmacist, Lab Technician, Clinic Administrator) are single- or double-digit-hire artifacts. Recommend expanding Non-binary applicant volume before this dimension can be meaningfully assessed at the role level; no process change is indicated by current data.

5. **General process recommendation.** Given that Registered Nurse and Clinic Administrator show the widest within-role selection-rate spreads across dimensions, prioritize a documentation review of the screening/interview rubric used for those two roles specifically, to confirm criteria are applied consistently regardless of demographic group.

---

## 6. Caveats

- **Correlation is not proof of discriminatory intent.** A four-fifths ratio below 0.80, even where statistically significant, reflects an observed aggregate pattern in outcomes. It does not, by itself, establish that any individual decision was made on a prohibited basis, nor does it rule out legitimate, job-related explanations (e.g., the experience/age correlation noted for Registered Nurse candidates in §2).
- **Low-confidence findings are directional only.** 94 of 125 rows (75.2%) in the metrics table are `low_confidence` because a group or its reference group has fewer than 30 candidates. These are reported for transparency but should not be used as the basis for any action beyond "monitor and collect more data."
- **Reference-group instability materially affects the race_ethnicity results.** Because the same small group (Native American) is the reference point in every role and in the rollup for this dimension, the apparent "disparity" for every other race/ethnicity group is mathematically the mirror image of that one group's sampling noise, not six or seven independent findings.
- **This is a synthetic dataset for audit-methodology demonstration**, not a real EEOC/OFCCP compliance filing. The four-fifths rule and significance tests applied here are standard, well-understood heuristics, not a certification of legal compliance or non-compliance.
