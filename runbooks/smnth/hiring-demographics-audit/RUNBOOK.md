---
version: "1.2.0"
evaluation: rubric
agent: claude-code                    # Agent runtime: claude-code | opencode | codex | gemini-cli
model: anthropic/claude-sonnet-5.5      # OpenRouter catalog id — the portable Jetty default
model_provider: openrouter            # Jetty-provisioned routing — runs in any collection, no ANTHROPIC_API_KEY needed
snapshot: python312-uv                # Sandbox: python312-uv | prism-playwright | custom image
# Headline deliverable(s), relative to results_dir, in priority order. spot
# surfaces the first of these as the "Main output" when a run completes; if
# omitted it falls back to the first file written.
primary_outputs:
  - "compliance_report.md"
  - "disparity_metrics.csv"
secrets:                              # Optional — declare sensitive params here
  # EXAMPLE_API_KEY:
  #   env: EXAMPLE_API_KEY            # Collection env var name on Jetty / OS env var locally
  #   description: "API key for ..."
  #   required: true
---

# Hiring Demographics Audit — Agent Runbook

## Objective

Given a dataset of candidates that includes CV/resume data, self-reported demographic attributes, the job role each candidate applied for, and the final hiring decision, produce a statistically grounded fairness/compliance audit. The audit must aggregate outcomes by job role and by demographic dimension (e.g. gender, race/ethnicity, age bracket), compute standard adverse-impact metrics (four-fifths rule ratios, pass-rate gaps, and statistical significance where sample size allows), and surface any role/dimension combinations that show disparity warranting review. The output is a narrative compliance report backed by a structured metrics table, suitable for review by HR/legal stakeholders.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `{{results_dir}}`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `{{results_dir}}/compliance_report.md` | Narrative compliance/fairness report: methodology, findings by role and demographic dimension, flagged disparities, recommendations |
| `{{results_dir}}/disparity_metrics.csv` | Structured table of aggregated metrics — one row per (job_role, demographic_dimension, group) with counts, pass rates, four-fifths ratio, and flag status |
| `{{results_dir}}/summary.md` | Executive summary with scores, feedback, and recommendations |
| `{{results_dir}}/validation_report.json` | Structured validation results — programmatic calculation checks, rubric scores, and overall_passed |

If you finish your work but have not written all files, go back and write them before stopping.

---

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|------------------|---------|-------------|
| Results directory | `{{results_dir}}` | `/app/results` (Jetty) / `./results` (local) | Output directory for all results |
| Input dataset | `{{input_data_path}}` | `/app/assets/synthetic_cvs_hiring.csv` (Jetty) | Path to the candidate dataset CSV. One row per candidate: `candidate_id, name, age, gender, race_ethnicity, disability_status, veteran_status, role_applied, education_level, field_of_study, university_tier, gpa, years_experience, num_previous_roles, num_skills, num_certifications, certifications, referred, cv_text, hired` |
| Protected attributes | `{{protected_attributes}}` | `gender,race_ethnicity,disability_status,veteran_status,age_bracket` | Comma-separated list of demographic columns/dimensions to analyze for disparity. `age_bracket` is derived (see Step 2) — the raw dataset only has numeric `age` |
| Job role field | `{{job_role_field}}` | `role_applied` | Column name identifying the job role/req the candidate applied for |
| Outcome field | `{{outcome_field}}` | `hired` | Column with the hiring decision, encoded as `Yes`/`No` strings — coerce to boolean in Step 2 |
| Disparity threshold | `{{disparity_threshold}}` | `0.8` | Four-fifths rule threshold — a group's selection ratio below this relative to the highest-selection group is flagged |
| Minimum group size | `{{min_group_size}}` | `30` | Minimum candidates in a (role, group) cell before a statistical significance test is attempted; smaller cells are reported but flagged as low-confidence |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| pandas | Python package | Yes | Data loading, cleaning, and aggregation |
| numpy | Python package | Yes | Numerical computation for ratio/rate calculations |
| scipy | Python package | Yes | Statistical significance testing (e.g. chi-square / Fisher's exact test on hiring outcomes by group) |

---

## Step 1: Environment Setup

```bash
# Install dependencies
pip install pandas numpy scipy

# Create output directories
mkdir -p {{results_dir}}

# Verify the input dataset exists — fall back to the uploaded asset if the declared
# path is absent (files uploaded through the API land as /app/assets/<run_id>.NN.csv)
INPUT="{{input_data_path}}"
if [ ! -f "$INPUT" ]; then
  INPUT="$(ls /app/assets/*.csv 2>/dev/null | head -1)"
  if [ ! -f "$INPUT" ]; then
    echo "ERROR: input dataset not found at {{input_data_path}} or /app/assets/*.csv"
    exit 1
  fi
  echo "Using uploaded dataset at $INPUT (record this path in validation_report.json)"
fi
```

Verify all required inputs and assets are available before proceeding.

---

## Step 2: Load and Validate Input Data

Load `{{input_data_path}}` and validate its structure before any analysis:

- Confirm `{{job_role_field}}` (`role_applied`) and `{{outcome_field}}` (`hired`) columns exist.
- Confirm at least one column per attribute listed in `{{protected_attributes}}` exists (`gender`, `race_ethnicity`, `disability_status`, `veteran_status` map directly; `age_bracket` does not exist yet — derive it).
- Coerce `hired` from `Yes`/`No` strings to a boolean indicator. Do the same for `disability_status`, `veteran_status`, and `referred` if used.
- Derive `age_bracket` by bucketing the numeric `age` column, e.g. `<30`, `30-39`, `40-49`, `50+` — use consistent bucket boundaries and document them in the report's methodology section.
- Record row counts before/after dropping rows with missing job role or outcome (do NOT silently drop rows with missing demographic data — treat missing/declined-to-state as its own group category rather than discarding the candidate).
- CV-derived fields (`education_level`, `field_of_study`, `university_tier`, `gpa`, `years_experience`, `num_previous_roles`, `num_skills`, `num_certifications`, `cv_text`) are useful as control variables for interpretation (e.g. "does the disparity persist after accounting for years of experience?") but are not required for the core disparity calculation — mention them in the report only if they help explain a flagged finding.

Log a short data-quality note (row counts, missingness by column) — this will be referenced in the compliance report's methodology section.

---

## Step 3: Aggregate Metrics & Compute Disparity Statistics

For each demographic dimension in `{{protected_attributes}}`, cross-tabulated with `{{job_role_field}}`:

1. Compute per-(role, dimension, group) cell: candidate count, hire count, hire rate (selection rate).
2. Within each role, identify the reference group: **among the groups in that (role, dimension) cell whose `candidate_count` is at least `{{min_group_size}}`, the one with the highest selection rate.** Restricting the reference to adequately sized groups is what keeps a group of 2 candidates hired at 100% from becoming the yardstick for everyone else (a real failure mode of earlier versions of this runbook — it turned every sibling group into a flagged, low-confidence row and hid the genuine disparities). If **no** group in the cell meets `{{min_group_size}}`, fall back to the highest-selection-rate group overall and mark every row in that cell `low_confidence = true`.

   **Deterministic tie-break rule (required — do not pick arbitrarily):** if two or more groups tie for the highest selection rate, resolve the tie in this fixed order: (a) prefer the tied group with the larger `candidate_count`; (b) if still tied, prefer the group whose name is alphabetically first (case-sensitive ASCII order). Record `reference_group_tie_broken = true` on every row belonging to a (job_role, dimension) cell where this rule had to fire, so a reader can see the choice was arbitrary-but-reproducible rather than meaningful.

3. Compute the four-fifths ratio for every other group: `group_selection_rate / reference_group_selection_rate`. Flag any ratio below `{{disparity_threshold}}`.

4. **Statistical significance — run BOTH tests, always, for every eligible cell.** For every (role, dimension, group) cell where both the group and its reference group meet `{{min_group_size}}`, compute:
   - **Fisher's exact test** (two-sided, `scipy.stats.fisher_exact`) on the 2×2 table [group hired/not-hired] vs [reference group hired/not-hired]. This is exact and valid at any sample size.
   - **Pearson chi-square test with Yates' continuity correction** (`scipy.stats.chi2_contingency(correction=True)`) on the same 2×2 table. This is the standard large-sample approximation.

   Do not choose one test over the other based on expected cell counts or any other run-time judgment call — always compute and report both, so results are identical across repeated runs on the same data. Record both p-values separately. Set `statistically_significant = true` **only if both tests agree** (`fisher_p_value < 0.05 AND chi2_p_value < 0.05`). This conservative, fully-specified combination rule removes the ambiguity that previously caused different runs to pick different tests and get different p-values.

5. Also compute an overall (role-agnostic) rollup per dimension, since some roles may have too few candidates per group to be individually meaningful. **The rollup's `job_role` value MUST be the exact literal string `ALL_ROLES`** (not `__ALL_ROLES__`, not `All Roles`, no variants) — this keeps output joinable and diffable across runs.

6. Write the full table to `{{results_dir}}/disparity_metrics.csv` with columns: `job_role, dimension, group, candidate_count, hire_count, selection_rate, reference_group, reference_group_tie_broken, four_fifths_ratio, flagged, fisher_p_value, fisher_significant, chi2_p_value, chi2_significant, statistically_significant, low_confidence`.

`low_confidence` should be `true` whenever a cell falls below `{{min_group_size}}`, or its reference group does (only possible when no group in the cell qualified) — these cells still get reported (transparency matters for an audit) but must be clearly marked as directional-only, not conclusive. `fisher_p_value`/`chi2_p_value`/`fisher_significant`/`chi2_significant` should be left null/blank for low-confidence cells (below `{{min_group_size}}`) since neither test is meaningful there.

---

## Step 4: Programmatic Validation of Calculations (hard gate)

Before writing the narrative report, verify the calculations in `{{results_dir}}/disparity_metrics.csv` are internally correct. This is a pass/fail gate — do not proceed to Step 5 until it passes.

Checks:

- **Row completeness**: every combination of `job_role` × dimension × group observed in the input data appears exactly once in the output table.
- **Count conservation**: for each (job_role, dimension), the sum of `candidate_count` across groups equals the total candidates for that role in the input data.
- **Rate bounds**: every `selection_rate` and `four_fifths_ratio` is between 0 and 1 inclusive (or explicitly null when the reference group has zero hires).
- **Flag consistency**: `flagged` is `true` if and only if `four_fifths_ratio < {{disparity_threshold}}`.
- **Low-confidence consistency**: `low_confidence` is `true` if and only if `candidate_count < {{min_group_size}}` (or the reference group's count is below the threshold).
- **Reference group correctness**: for each (job_role, dimension), the recorded `reference_group` has the highest `selection_rate` among the groups in that cell with `candidate_count >= {{min_group_size}}` (or among all groups when none qualify), and a qualifying group was never passed over in favour of a smaller one.
- **Tie-break determinism**: for every (job_role, dimension) cell where multiple groups share the max `selection_rate`, the recorded `reference_group` matches what the Step 3 tie-break rule (larger `candidate_count`, then alphabetically first) would produce, and `reference_group_tie_broken` is `true` on those rows.
- **Rollup literal correctness**: every rollup row's `job_role` is exactly `ALL_ROLES` — no other spelling or casing appears anywhere in the file.
- **Dual-test presence**: every row with `low_confidence == false` has non-null `fisher_p_value` AND `chi2_p_value` (both tests were actually run, not just one).
- **Significance combination rule**: `statistically_significant == (fisher_significant AND chi2_significant)` for every row, and `fisher_significant`/`chi2_significant` correctly reflect `p < 0.05` on their respective p-values.

Write the pass/fail result of each check (with counts of any violating rows) into the `programmatic_checks` section of `{{results_dir}}/validation_report.json` (see Step 10). If any check fails, fix the aggregation logic in Step 3 and re-run before continuing — do not hand-patch the CSV.

---

## Step 5: Generate Compliance Report

Write `{{results_dir}}/compliance_report.md` synthesizing the validated metrics into a narrative report for HR/legal review.

Requirements:
- **Methodology section**: describe the dataset (row counts, date range if available, data-quality notes from Step 2), the disparity metric used (four-fifths rule + significance testing), and its limitations.
- **Findings by job role**: for each role with meaningful data, summarize selection rates by demographic group and call out any flagged disparities.
- **Findings by demographic dimension (rollup)**: cross-role view of where disparities concentrate.
- **Flagged items table or list**: every `flagged == true` row from `disparity_metrics.csv`, with role, dimension, group, ratio, and confidence level, sorted by severity (lowest ratio first, non-low-confidence items prioritized). For any row with `low_confidence == false`, cite **both** `fisher_p_value` and `chi2_p_value` side by side (not just one) — do not select or omit one test's result.
- **Recommendations**: concrete, actionable next steps (e.g. "review screening criteria for {role}", "increase applicant pool size for {group} in {role} before drawing conclusions") — not generic boilerplate.
- **Caveats**: explicitly state that correlation in aggregate hiring data does not by itself establish discriminatory intent, and that low-confidence findings need more data before action.

---

## Step 6: Evaluate Report Against Rubric

**Before assigning any score, independently re-derive the numbers — do not score from memory or impression.** Self-scoring is prone to optimism bias: an agent that just wrote a report tends to rate it well without re-checking it against the source data. To counter this, before scoring criterion 6 (and to inform criteria 1-3), you MUST:

1. Compute `true_flagged_count = count(flagged == true)` directly from `{{results_dir}}/disparity_metrics.csv` and compare it to whatever flagged-count figure `compliance_report.md` states. They must match exactly.
2. Compute the "true top 5": sort all `flagged == true` rows by `four_fifths_ratio` ascending, breaking ties by (`statistically_significant` true first, then `low_confidence` false first). Confirm these 5 (job_role, dimension, group) tuples are the ones actually surfaced as the report's most severe findings — not a different, milder subset.
3. Spot-check at least one cited ratio and one cited p-value pair (both `fisher_p_value` and `chi2_p_value`) per protected attribute dimension against the CSV directly.

Only after completing this verification should you score `{{results_dir}}/compliance_report.md` against each criterion on a 1-5 scale:

### Rubric

| # | Criterion | 5 (Excellent) | 3 (Acceptable) | 1 (Poor) |
|---|-----------|---------------|-----------------|----------|
| 1 | Statistical rigor | Four-fifths ratios and both significance tests are correctly applied and interpreted; low-confidence cells are clearly distinguished from statistically supported findings; `statistically_significant` values verified to equal `fisher_significant AND chi2_significant` | Metrics are computed correctly but confidence/significance nuance is thin or inconsistently applied | Metrics are miscomputed, misapplied, or significance/confidence is not addressed at all |
| 2 | Completeness of breakdowns | Every job role and every protected attribute in `{{protected_attributes}}` is covered, both per-role and in cross-role rollup | Most roles/dimensions covered but a few are missing or thinly treated | Only a subset of roles or dimensions analyzed, or rollup view missing entirely |
| 3 | Clarity of findings | A reader unfamiliar with the raw data can immediately identify which roles/groups are flagged and why, with both p-values cited inline | Findings are present but require cross-referencing the CSV to understand severity or scope | Findings are vague, unsupported by cited numbers, or buried in prose |
| 4 | Actionability of recommendations | Recommendations are specific to the flagged findings (named role/group/metric) and distinguish "investigate further" from "collect more data" from "review process" | Recommendations are reasonable but generic, not tied to specific flagged findings | No recommendations, or recommendations unrelated to the actual findings |
| 5 | Appropriate caveats & tone | Report clearly separates statistical disparity from proof of discrimination, flags low-confidence results, and uses measured, non-alarmist language suitable for legal/HR review | Caveats present but incomplete, or tone occasionally overstates certainty | No caveats about causation/confidence, or alarmist/definitive language not supported by the data |
| 6 | Factual self-consistency | Every quantitative claim in `compliance_report.md` — total flagged count, top-severity findings list, cited ratios and p-values — is verified in step 1-3 above to exactly match `disparity_metrics.csv`, with zero discrepancies found | At most one minor, non-headline discrepancy found (e.g. a rounding difference), and it does not affect which findings are surfaced as most severe | Any headline number (total flagged count, or the identity of the top-severity findings) does not match the CSV |

**Pass threshold: overall average >= 4.0, no individual criterion below 3, AND criterion 6 (Factual self-consistency) specifically >= 4.** Criterion 6 exists precisely to catch cases where a report reads well but states a wrong number — a generically high overall average must not paper over that. If the Step 6 verification in steps 1-3 above ever found a discrepancy (even one later fixed by re-running Step 5), criterion 6 for this evaluation round cannot score above 3, since it demonstrates the report was not correct in its first draft.

Record your scores and reasoning for each criterion, including the concrete verification results from steps 1-3 above (not just an impression).

---

## Step 7: Iterate on Weak Criteria (max 3 rounds)

If the rubric score is below the pass threshold:

1. Identify the **lowest-scoring criteria** (below 3 first, then below 4)
2. Consult the Common Fixes table below for targeted improvements
3. Make focused edits — change only what addresses the weak criteria
4. Re-score with Step 6 rubric
5. Repeat up to 3 times total

After 3 rounds, keep the best-scoring version and note remaining weaknesses in the summary.

### Common Fixes

| Weak Criterion | Common Issue | Fix |
|----------------|-------------|-----|
| Statistical rigor | Significance testing skipped or applied to cells below `{{min_group_size}}` without flagging | Re-check `low_confidence` flags against Step 4 output; explicitly state confidence level next to every ratio cited |
| Completeness of breakdowns | A role or protected attribute with sparse data was silently dropped from the narrative | Add an explicit "insufficient data" note for that role/dimension instead of omitting it — an audit should account for every dimension requested |
| Clarity of findings | Findings described only in prose with no numbers | Pull the exact selection rates and four-fifths ratios from `disparity_metrics.csv` into the findings text |
| Actionability of recommendations | Recommendations are generic ("promote diversity", "review hiring practices") | Tie each recommendation to a specific flagged (role, group) pair and the metric that triggered the flag |
| Appropriate caveats & tone | Report states disparities as proven bias | Reword to "statistical disparity was observed" language; add the standard caveat paragraph about correlation vs. causation and low-confidence cells |
| Factual self-consistency | A cited total, ratio, or p-value doesn't match `disparity_metrics.csv`, or the "most severe" findings list omits a lower-ratio/significant row that exists in the CSV | Recompute the flagged count and the top-5-by-severity list directly from the CSV with code (do not restate from memory) and replace the report's figures with those exact values |

---

## Step 8: Write Executive Summary

Write `{{results_dir}}/summary.md` with the following structure:

```markdown
# Hiring Demographics Audit — Results

## Overview
- **Date**: {run date}
- **Input**: {row count, role count, dimensions analyzed}
- **Iterations**: {how many rounds of refinement}

## Rubric Scores

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 1 | Statistical rigor | X/5 | {Brief justification} |
| 2 | Completeness of breakdowns | X/5 | {Brief justification} |
| 3 | Clarity of findings | X/5 | {Brief justification} |
| 4 | Actionability of recommendations | X/5 | {Brief justification} |
| 5 | Appropriate caveats & tone | X/5 | {Brief justification} |
| | **Overall** | **X.X/5** | |

## Output Description
{2-3 sentences describing the report and metrics table}

## Key Findings
Total flagged (ratio < {{disparity_threshold}}): **{true_flagged_count computed directly from disparity_metrics.csv}**

{The 5 most severe flagged disparities — computed by sorting disparity_metrics.csv by four_fifths_ratio ascending, ties broken by statistically_significant (true first) then low_confidence (false first). Do NOT hand-pick a "representative" subset — this must be the literal top 5 by ratio.}

## Iteration History
{What changed in each round and why}

## Recommendations
- {What could be improved with more iteration}
- {Upstream changes — e.g. more granular demographic capture, larger sample size — that would improve confidence}

## Limitations
- {What the rubric and programmatic checks do not capture}
- {Subjective aspects that may need human/legal review}
```

---

## Step 9: Validate Summary Accuracy Against Source Data (hard gate — max 2 rounds)

This is the step that would have caught the actual failure mode observed in prior runs: `summary.md` is written *after* the rubric evaluation in Step 6, so nothing was ever checking its numbers. A report can pass Step 6's rubric with a perfect score while the separately-written executive summary states the wrong flagged count or lists the wrong "most severe" findings. This gate closes that hole with an objective, code-based check — not another self-assessment.

Using code (not recollection), re-derive from `{{results_dir}}/disparity_metrics.csv`:

1. `true_flagged_count = count(flagged == true)`.
2. `true_top5` = the 5 (job_role, dimension, group) tuples with the lowest `four_fifths_ratio` among `flagged == true` rows, ties broken by `statistically_significant` (true first) then `low_confidence` (false first).

Then check `{{results_dir}}/summary.md`:

- **Flagged-count match**: the number following "Total flagged (ratio < {{disparity_threshold}}):" in the Key Findings section equals `true_flagged_count` exactly.
- **Top-5 match**: all 5 tuples in `true_top5` are identifiable in the Key Findings bullets (by job role, dimension/group, and a ratio that matches the CSV to at least 2 decimal places).

If either check fails, rewrite the Key Findings section of `summary.md` using the freshly recomputed values (do not hand-edit individual numbers) and re-check. Repeat up to 2 times total. Record the final outcome — do not proceed to Step 10 until this gate passes or the 2-round budget is exhausted (in which case note the discrepancy explicitly in the Limitations section rather than leaving it silently wrong).

---

## Step 10: Write Validation Report

Write `{{results_dir}}/validation_report.json`:

```json
{
  "version": "1.0.0",
  "run_date": "2026-01-01T00:00:00Z",
  "parameters": {
    "input_data_path": "/app/assets/synthetic_cvs_hiring.csv",
    "protected_attributes": "gender,race_ethnicity,disability_status,veteran_status,age_bracket",
    "job_role_field": "role_applied",
    "outcome_field": "hired",
    "disparity_threshold": 0.8,
    "min_group_size": 30
  },
  "stages": [
    { "name": "setup", "passed": true, "message": "Environment ready" },
    { "name": "data_loading", "passed": true, "message": "Input parsed and validated" },
    { "name": "aggregation", "passed": true, "message": "Disparity metrics computed" },
    { "name": "programmatic_validation", "passed": true, "message": "All calculation checks passed" },
    { "name": "report_generation", "passed": true, "message": "Compliance report generated" },
    { "name": "rubric_evaluation", "passed": true, "message": "Rubric score: X.X/5" },
    { "name": "summary_accuracy_validation", "passed": true, "message": "summary.md flagged-count and top-5 verified against CSV" }
  ],
  "programmatic_checks": {
    "row_completeness": { "passed": true, "violations": 0 },
    "count_conservation": { "passed": true, "violations": 0 },
    "rate_bounds": { "passed": true, "violations": 0 },
    "flag_consistency": { "passed": true, "violations": 0 },
    "low_confidence_consistency": { "passed": true, "violations": 0 },
    "reference_group_correctness": { "passed": true, "violations": 0 },
    "tie_break_determinism": { "passed": true, "violations": 0 },
    "rollup_literal_correctness": { "passed": true, "violations": 0 },
    "dual_test_presence": { "passed": true, "violations": 0 },
    "significance_combination_rule": { "passed": true, "violations": 0 }
  },
  "summary_accuracy_check": {
    "flagged_count_match": true,
    "top5_match": true,
    "rounds_needed": 1,
    "passed": true
  },
  "rubric_scores": {
    "statistical_rigor": { "score": 5, "notes": "..." },
    "completeness_of_breakdowns": { "score": 4, "notes": "..." },
    "clarity_of_findings": { "score": 4, "notes": "..." },
    "actionability_of_recommendations": { "score": 5, "notes": "..." },
    "appropriate_caveats_and_tone": { "score": 4, "notes": "..." },
    "factual_self_consistency": { "score": 5, "notes": "..." }
  },
  "overall_score": 4.5,
  "pass_threshold": 4.0,
  "iterations": 1,
  "overall_passed": true,
  "output_files": [
    "{{results_dir}}/compliance_report.md",
    "{{results_dir}}/disparity_metrics.csv",
    "{{results_dir}}/summary.md",
    "{{results_dir}}/validation_report.json"
  ]
}
```

`overall_passed` must be `true` only if **all** of: every `programmatic_checks` entry passed, `summary_accuracy_check.passed` is `true`, and the rubric `overall_score` meets the pass threshold (including criterion 6 >= 4, per Step 6).

---

## Step 11: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="{{results_dir}}"
for f in "$RESULTS_DIR/compliance_report.md" "$RESULTS_DIR/disparity_metrics.csv" "$RESULTS_DIR/summary.md" "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

### Checklist

- [ ] `disparity_metrics.csv` exists and passed every programmatic check in Step 4 (including tie-break determinism, rollup literal correctness, dual-test presence, and the significance combination rule)
- [ ] `compliance_report.md` exists and meets quality bar (rubric >= 4.0, no criterion below 3, factual self-consistency >= 4)
- [ ] `summary.md` exists, passed the Step 9 accuracy gate (flagged count and top-5 match the CSV), and includes rubric scores and key findings
- [ ] `validation_report.json` exists with `programmatic_checks`, `summary_accuracy_check`, `rubric_scores`, `overall_score`, and `overall_passed`
- [ ] Verification script printed PASS for all files

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- `hired`, `disability_status`, `veteran_status`, and `referred` are all encoded as literal `Yes`/`No` strings in the source CSV, not booleans — coerce explicitly rather than relying on truthy string checks.
- `age` is a raw integer; there is no pre-built `age_bracket` column. Pick bucket boundaries once in Step 2 and reuse them consistently in both the metrics table and the report — don't let the report re-derive brackets independently of the CSV.
- The reference group is chosen only among groups that meet `{{min_group_size}}` (v1.2.0+). Earlier versions used the highest-rate group regardless of size, which let a 2-candidate group hired at 100% define the ratio for every other group in the cell.
- `race_ethnicity` and `gender` are the most reliably populated demographic columns; check `disability_status`/`veteran_status` for skew (they may be predominantly `No` with a small `Yes` minority) — small minority cells will frequently trip `low_confidence`, which is expected and should be reported as such, not treated as an error.
- `cv_text` is a free-text synthetic summary already redundant with the structured columns (years_experience, education_level, etc.) — no NLP extraction is needed from it; use the structured fields directly.
- This is a synthetic dataset for audit-methodology purposes, not a real EEOC/OFCCP filing — the four-fifths rule is used as a standard, well-understood disparity heuristic, not a claim of legal compliance certification.

