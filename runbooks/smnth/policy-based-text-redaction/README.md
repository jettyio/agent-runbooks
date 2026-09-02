# Policy-based text redaction (Jetty runbook)

**Redact only what each record's own policy says to redact.** The input is a JSON array of
records, each carrying a domain, a bulleted set of policy statements, and a raw text. The
runbook replaces just the spans a stated policy covers with labelled markers
(`[REDACTED: PERSON_1]`, `[REDACTED: SCHEDULE]`, …), keeps greetings, sign-offs and
non-sensitive connective text intact, and scores itself against a five-criterion rubric that
penalises both leaks and wholesale blackouts.

## Flow

1. **Parse** — map each policy statement to the concrete spans it applies to.
2. **Redact** — literal substring replacement, every alias and re-mention, entities numbered
   in order of first appearance so who-said-what survives without re-identifying anyone.
3. **Rubric** — policy compliance, context preservation, precision, marker consistency,
   readability (1–5 each; pass ≥ 4.0 overall, nothing below 3).
4. **Iterate** — up to 3 rounds on the weakest records only.

## Deliverables (`{{results_dir}}/`)

| File | What |
|------|------|
| `redacted_dataset.json` | Every input record, all original fields plus `redacted_text` |
| `summary.md` | Rubric scores, per-record notes, iteration history |
| `validation_report.json` | Structured rubric scores, `overall_score`, `overall_passed` |

## Parameters

`input_file` (JSON array of `{id, domain, policy, policy_ids, text}`) ·
`redaction_marker` (default `[REDACTED: {category}]`).

## Examples

See `examples/` — real runs on Jetty with the input dataset, `expected/` outputs,
`trajectory.json`, and a thumbnail. Rubric scores are self-assessed by the agent, not by a
separate judge model.
