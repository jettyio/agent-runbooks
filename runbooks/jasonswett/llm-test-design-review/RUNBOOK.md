---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
model_provider: anthropic
snapshot: python312-uv
# The headline deliverable — the human-readable review.
primary_outputs:
  - review.md
origin:
  url: "https://github.com/jasonswett/llm-skills/blob/main/test-design-review/SKILL.md"
  source_host: "github.com"
  source_title: "test-design-review"
  imported_at: "2026-06-07T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "jasonswett"
    skill_name: "test-design-review"
    author: "Jason Swett (github.com/jasonswett)"
    license: "unspecified by source repo — converted to a runbook with attribution; review guidelines © their author"
    confidence: "high"
secrets: {}
---

# Test Design Review — Agent Runbook

> Converted, with attribution, from **Jason Swett's `test-design-review` skill**
> (github.com/jasonswett/llm-skills). The review guidelines below are his; this runbook
> wraps them in an executable review process with structured, auditable outputs.

> **EXECUTE THIS RUNBOOK NOW.** Review the code with tools and write every deliverable to
> `{{results_dir}}`. This is a task to perform, not a document to summarize. Your first
> action is a tool call (Step 1).

## Inputs (already provided)

- **Code under review:** the test file(s) uploaded into `/app/assets/` (`*.rb`,
  `*_spec.rb`, `*_test.rb`, `*.rs`, `*.py`, or a `*.diff` / `*.patch`). If a diff is
  present, review only the changed lines; otherwise review the whole file(s).
- **Focus guideline (optional):** {{focus_guideline}} — restrict the review to one
  guideline id when set, otherwise review against all of them.

## Objective

Review the supplied tests for **design quality** against the guidelines catalogued below,
and produce a precise, actionable review. Tests are executable specifications; the review
judges how well each test reads as a specification — does it describe a scenario and its
expected outcome, assert on observable behavior rather than implementation details, stay
at one level of abstraction, and avoid arbitrariness and noise? For **each violation**:
name the guideline, quote the offending code with its location, explain why it violates
the guideline, and suggest a concrete fix. Group findings by guideline. A test file with
no violations is a valid result — report zero findings, don't invent them.

> **Review with fresh eyes.** Per the source skill, a test-design review should be done by
> an agent that did *not* write the code. Treat the input as unfamiliar; judge it on its
> own terms.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following to `{{results_dir}}`. The task is NOT complete until
every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `{{results_dir}}/review.md` | The human-readable review: findings grouped by guideline, each with the offending code, why it violates the guideline, and a suggested fix. The headline deliverable. |
| `{{results_dir}}/findings.json` | Structured findings — one object per violation (see schema in Step 4). May be `[]` when the tests are clean. |
| `{{results_dir}}/summary.md` | Executive summary: per-guideline violation counts, files reviewed, overall assessment. |
| `{{results_dir}}/validation_report.json` | Stage-by-stage validation with `overall_passed`. See Step 6. |

If you finish reviewing but have not written all files, go back and write them first.

---

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|------------------|---------|-------------|
| Results directory | `{{results_dir}}` | `/app/results` (Jetty) / `./results` (local) | Output directory for all results |
| Code under review | *(uploaded)* | test file(s) / diff in `/app/assets/` | What to review |
| Focus guideline | `{{focus_guideline}}` | *(empty = all)* | Optional single guideline id to restrict the review to |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| *(none)* | — | — | The review is reasoning over source text; no packages or test runtime are required. |

---

## Step 1: Environment Setup

```bash
mkdir -p "{{results_dir}}"
shopt -s nullglob 2>/dev/null || true
FILES=$(ls /app/assets/*.rb /app/assets/*_spec.rb /app/assets/*_test.rb /app/assets/*.rs /app/assets/*.py /app/assets/*.diff /app/assets/*.patch 2>/dev/null)
echo "Files to review:"; echo "$FILES"
[ -n "$FILES" ] || { echo "ERROR: no code files found in /app/assets"; exit 1; }
```

Read each file in full before reviewing.

---

## Guidelines Catalog (the review criteria)

Review every test against each guideline. Each has an `id` (use it in `findings.json`),
the rule, and a bad → good contrast.

| id | Guideline | The rule |
|----|-----------|----------|
| `specification-format` | Specification format | A test name should answer "in scenario X, what should happen?" — not vague ("it works correctly", "it handles errors"). |
| `behavior-not-implementation` | Test behavior, not implementation | Assert on observable behavior, not internal/implementation details or hard-coded incidental values. |
| `describe-the-essence` | Describe the essence | `describe`/`context` strings should capture the scenario's meaning (`"rerunning only failed tests"`), not a code token (`"scope=failed"`). |
| `avoid-arbitrariness` | Avoid arbitrariness | Don't retrieve records with `.first`/`.last` (order-dependent, fragile). Use explicit `change`/`where` queries instead. |
| `essential-not-incidental` | Assert essentials, not incidentals | Only assert what matters. Drop redundant assertions implied by others (e.g. `be_successful` next to a body assertion). |
| `one-level-of-abstraction` | Don't mix levels of abstraction | A block should operate at one level; push incidental setup/details out of the essential flow. |
| `avoid-forward-reference` | Avoid forward reference | Don't reference a `let`/variable before it's defined; order definitions before use, or inline the value. |
| `no-have-current-path` | Don't use `have_current_path` | Too coupled to the URL/implementation. Assert on what the user sees on the page. |
| `observable-not-method-calls` | Assert observable outcomes, not method calls | Avoid mock assertions like `expect(x).to have_received(:foo)` (tests means). Assert the real end result. Stub only true externals. |
| `test-ends-not-means` | Test ends, not means | For caching/perf, assert the observable difference (e.g. zero extra DB queries), not the mechanism (`Rails.cache.read`). |
| `high-level-of-abstraction` | Maintain a high level of abstraction | Hide dense incidental details behind a well-named helper (defined *after* the test); show the essence. |
| `no-private-method-hacks` | Don't hack to test private methods | Never `send`/`public_send` to reach private methods — make the method public instead. |
| `no-tight-coupling` | Don't tightly couple to implementation | Don't set up state via internal shapes (`json_output: {...}`) when a behavioral input (`exit_code: 0`) expresses the scenario. |
| `arrange-act-assert` | Use Arrange / Act / Assert | Structure the test into clear arrange, act, and assert phases. |
| `no-speculative-coding` | No speculative coding | Scrutinize cargo-culted choices (e.g. an unexplained `wait: 3`); remove what isn't justified. |
| `no-instance-variable-set` | Never `instance_variable_set` | If it seems necessary, that signals poor design — find it and suggest a specific refactor. |
| `no-described-class` | Don't use `described_class` | It adds obscurity; use the actual class name. |

> The full bad/good examples for each guideline live in the source skill
> (linked in the frontmatter `origin`). Apply the rule above; cite the `id` in findings.

---

## Step 2: Review

For each file, read it fully, then walk the Guidelines Catalog top to bottom. For every
violation, capture: the `guideline` id, the `file`, the `line_start`/`line_end`, the exact
`offending_code` (quoted), a one-sentence `why`, a concrete `suggested_fix` (show the
corrected code), and a `severity` (`high` = misleads about behavior or is brittle;
`medium` = noise/coupling; `low` = stylistic). If `{{focus_guideline}}` is set, review only
that guideline. Do **not** invent violations — only report real ones.

---

## Step 3: (reserved)

---

## Step 4: Write `findings.json`

One object per violation:

```json
[
  {
    "guideline": "avoid-arbitrariness",
    "severity": "high",
    "file": "user_spec.rb",
    "line_start": 14,
    "line_end": 16,
    "offending_code": "user = User.last\nexpect(user.email).to eq(\"a@b.com\")",
    "why": "Retrieving the record with .last depends on insertion order and is fragile.",
    "suggested_fix": "expect { post users_path, params: {...} }.to change { User.where(email: \"a@b.com\").count }.by(1)"
  }
]
```

Write `[]` if there are no violations.

---

## Step 5: Write `review.md`

Group findings **by guideline** (matching the source skill's "group by guideline"). For
each guideline with ≥1 finding, write a section: the guideline name, then each finding as
the offending code (fenced), a one-line why, and the suggested fix (fenced). Open with a
one-paragraph overall assessment and a per-guideline count table. If there are zero
findings, say so plainly and note what the tests do well.

---

## Step 6: Evaluate & Validate

Assign the review one status, then write `validation_report.json`.

| Status | Criteria |
|--------|----------|
| `PASS` | Every input file was read; `findings.json` is valid and every finding has all required fields with a `guideline` id from the catalog, a quoted `offending_code`, and a concrete `suggested_fix`; `review.md` groups findings by guideline; a clean file correctly yields `[]`. |
| `PARTIAL` | Review produced but with gaps — a finding missing `suggested_fix`/location, or `review.md` not grouped by guideline. |
| `FAIL` | No review produced, `findings.json` invalid, or a finding cites a `guideline` id not in the catalog. |

```json
{
  "version": "1.0.0",
  "run_date": "<ISO timestamp>",
  "parameters": { "focus_guideline": "{{focus_guideline}}" },
  "stages": [
    { "name": "setup",        "passed": true, "message": "Input files resolved" },
    { "name": "review",       "passed": true, "message": "Reviewed N files against the catalog" },
    { "name": "findings",     "passed": true, "message": "Wrote F findings, all fields present, all ids in catalog" },
    { "name": "review_doc",   "passed": true, "message": "review.md grouped by guideline" },
    { "name": "report",       "passed": true, "message": "All output files written" }
  ],
  "results": { "files_reviewed": 0, "findings": 0, "by_guideline": {} },
  "overall_passed": true
}
```

`overall_passed` is `true` iff every stage passed and every finding's `guideline` is in the
catalog.

---

## Step 7: Iterate (max 3 rounds)

If validation fails (invalid JSON, a finding missing fields, an unknown guideline id, or
`review.md` not grouped), fix it and re-validate. Max 3 rounds; then surface the remaining
issue in `summary.md`.

---

## Step 8: Write Executive Summary

Write `{{results_dir}}/summary.md`:

```markdown
# Test Design Review — Results

## Overview
- **Date**: <ISO timestamp>  ·  **Files reviewed**: <list>  ·  **Focus**: {{focus_guideline}} (or "all")

## Findings by guideline
| Guideline | Count | Severity (H/M/L) |
|-----------|-------|------------------|

## Overall assessment
<2–4 sentences: the dominant problems, what the tests do well, the single highest-value fix.>

## Notes / Limitations
<e.g. only the diff was reviewed; language-specific guideline N/A.>
```

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="{{results_dir}}"
for f in "$RESULTS_DIR/review.md" "$RESULTS_DIR/findings.json" "$RESULTS_DIR/summary.md" "$RESULTS_DIR/validation_report.json"; do
  [ -s "$f" ] && echo "PASS: $f ($(wc -c < "$f") bytes)" || echo "FAIL: $f is missing or empty"
done
python3 - <<PY
import json
CATALOG={"specification-format","behavior-not-implementation","describe-the-essence","avoid-arbitrariness",
 "essential-not-incidental","one-level-of-abstraction","avoid-forward-reference","no-have-current-path",
 "observable-not-method-calls","test-ends-not-means","high-level-of-abstraction","no-private-method-hacks",
 "no-tight-coupling","arrange-act-assert","no-speculative-coding","no-instance-variable-set","no-described-class"}
f=json.load(open("$RESULTS_DIR/findings.json"))
bad=[x for x in f if x.get("guideline") not in CATALOG]
missing=[x for x in f if not (x.get("offending_code") and x.get("suggested_fix") and x.get("file"))]
print("FAIL: unknown guideline ids:", [x.get("guideline") for x in bad]) if bad else print("PASS: all guideline ids in catalog")
print("FAIL: findings missing fields:", len(missing)) if missing else print(f"PASS: {len(f)} findings, all fields present")
PY
echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] Every input file was read in full (or only the diff's changed lines, if a diff)
- [ ] `findings.json` is valid; every finding has `guideline` (from the catalog), `file`, `offending_code`, `why`, `suggested_fix`, `severity`
- [ ] `review.md` groups findings by guideline; each shows offending code + a concrete fix
- [ ] A clean file yields `[]` — no invented violations
- [ ] `summary.md` has the per-guideline count table and an overall assessment
- [ ] `validation_report.json` has `stages`, `results`, `overall_passed`
- [ ] Verification script printed `PASS` for every line

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Tests are executable specifications.** The clearest lens: does each test read as "in
  scenario X, Y should happen?" If you can't tell the scenario or the expected outcome from
  the name and body, that's a `specification-format` or `describe-the-essence` finding.
- **Means vs ends is the through-line.** Many guidelines are one idea — assert the *end*
  (observable outcome) not the *means* (a method call, a cache key, a URL). When in doubt,
  ask "if the implementation changed but behavior stayed the same, would this test still
  pass?" If no, it's coupled to means.
- **Quote, locate, fix.** Every finding must show the offending code, its line range, and a
  concrete corrected version — a review without a fix isn't actionable.
- **Don't over-report.** A clean test is a valid outcome. Inventing borderline findings
  erodes trust in the review. Severity-rank so the reader sees the high-value fixes first.
- **Most examples are Ruby/RSpec**, but the principles are language-agnostic; apply them to
  Rust/Python tests too (skip Ruby-only ids like `no-described-class` where they don't map).
