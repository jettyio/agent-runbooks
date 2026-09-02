# Hiring demographics audit (Jetty runbook)

**Audit a hiring dataset for adverse impact — with the numbers checked by code, not by
impression.** Given one row per candidate (role applied for, hiring decision, self-reported
demographics), the runbook computes four-fifths ratios per (role, dimension, group), runs
*both* Fisher's exact and chi-square tests on every eligible cell, and writes a narrative
compliance report for HR/legal review backed by a structured metrics table. Two hard gates
protect the result: a programmatic validation of the calculations, and a fact-check that
re-derives the executive summary's flagged count and top-5 findings from the CSV before the
run may pass.

## Flow

1. **Load + validate** — coerce Yes/No fields, derive `age_bracket`, keep
   declined-to-state as its own group.
2. **Aggregate** — selection rates, deterministic reference-group tie-break, four-fifths
   ratio, dual significance tests, `ALL_ROLES` rollup → `disparity_metrics.csv`.
3. **Programmatic validation (hard gate)** — ten internal-consistency checks.
4. **Report** — methodology, findings by role and by dimension, flagged items with both
   p-values, specific recommendations, caveats.
5. **Rubric** — six criteria incl. *factual self-consistency*; the agent must re-derive the
   headline numbers before scoring.
6. **Summary accuracy gate** — code re-checks `summary.md` against the CSV (max 2 rounds).

## Deliverables (`{{results_dir}}/`)

| File | What |
|------|------|
| `compliance_report.md` | Narrative fairness/compliance report |
| `disparity_metrics.csv` | One row per (job_role, dimension, group): counts, rates, ratio, flags, both p-values |
| `summary.md` | Executive summary, fact-checked against the CSV |
| `validation_report.json` | Programmatic checks, summary-accuracy gate, rubric scores, `overall_passed` |

## Parameters

`input_data_path` · `protected_attributes` · `job_role_field` · `outcome_field` ·
`disparity_threshold` (0.8) · `min_group_size` (30).

## Examples

See `examples/` — real runs on Jetty over **synthetic** candidate datasets (audit-methodology
demonstrations, not real filings). Statistical disparity does not by itself establish
discriminatory intent; the report says so, and so should you.
