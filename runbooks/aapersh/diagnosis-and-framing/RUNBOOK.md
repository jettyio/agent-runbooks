---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: anthropic/claude-sonnet-4.6
model_provider: openrouter
snapshot: python312-uv
# The headline deliverable — the board-ready strategic diagnosis.
primary_outputs:
  - diagnosis.md
origin:
  url: "https://github.com/aapersh/strategy-skills-for-claude/tree/main/skills/01-diagnosis-and-framing"
  source_host: "github.com"
  source_title: "01 — Diagnosis & Framing (21 McKinsey-Style Strategy Skills for Claude)"
  imported_at: "2026-06-10T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.1.0"
  is_directory_mirror: false
  attribution:
    collection_or_org: "aapersh"
    source_collection: "strategy-skills-for-claude"
    skill_name: "diagnosis-and-framing"
    author: "aapersh — github.com/aapersh/strategy-skills-for-claude"
    license: "unspecified (no LICENSE file in source repo; collection is independent/unofficial)"
    confidence: "high"
    note: >-
      The source 'skill' is a bundle of three method files (situation-assessment.md,
      growth-barriers.md, assumption-audit.md). This runbook composes all three into a
      single diagnosis pass so a reviewer gets one board-ready artifact. The McKinsey/MBB
      method (MECE, hypothesis-led, fact-before-recommendation) is general consulting
      practice; this is a re-expression of the method with attribution, not a copy.
secrets: {}
---

# Diagnosis & Framing — Strategic Diagnosis — Agent Runbook

> Converted, with attribution, from **01 — Diagnosis & Framing**
> (github.com/aapersh/strategy-skills-for-claude) — a McKinsey-style strategy skill bundle.
> The source ships three methods as separate files; this runbook composes them into one
> pass: **establish the fact base → find the binding constraint → audit the load-bearing
> assumptions → frame the decision.** The product is a single board-ready `diagnosis.md`.

> **EXECUTE THIS RUNBOOK NOW.** This is a task to perform and write to disk, not a document
> to summarize back. Produce the diagnosis with the rigor below and write every deliverable
> to `{{results_dir}}` using file-writing tools. Your first action is a tool call (Step 1).

## Inputs (already provided)

You do **not** need to ask the user for these — they are injected at launch. Read them here
and use them verbatim. If `situation` is empty, fail fast per Step 1.

- **Situation** (`{{situation}}`): the business / market / product / function being diagnosed,
  plus whatever facts are available (financials, KPIs, market signals, recent changes).
- **Decision** (`{{decision}}`): the decision or question the diagnosis must inform
  (e.g. "Should we raise a Series B to fund a move upmarket?"). May be empty — if so, infer
  the most consequential decision implied by the situation and state it explicitly.
- **Context file** (optional): if a file was uploaded, its path(s) are in
  `init_params.file_paths`. Read it for additional facts before diagnosing.

## Objective

Produce a defensible, **fact-first** strategic diagnosis that a leadership team or board can
act on. Do the work in the order a top-tier consultant would: build the baseline before
debating solutions, isolate the *one or two* constraints that actually bind, surface the
beliefs the strategy rests on, and end with a clear framed recommendation. Separate **facts,
interpretations, and assumptions** at every step — never recommend before the baseline is
established. The headline deliverable is `diagnosis.md`; `summary.md` and
`validation_report.json` make the run auditable and gradeable.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following to `{{results_dir}}`. The task is NOT complete until
every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `{{results_dir}}/diagnosis.md` | **The primary deliverable.** Full diagnosis: Executive Read → Situation Assessment → Growth Barrier → Assumption Audit → Framed Recommendation. Structure is fixed in Step 3. |
| `{{results_dir}}/summary.md` | One-screen executive summary: the answer-first read, the binding constraint, the one recommendation, and the top open question. |
| `{{results_dir}}/validation_report.json` | Programmatic self-check (Step 4): `stages`, `results`, `overall_passed`. |

If you finish your analysis but have not written all three files, go back and write them
before stopping.

---

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|------------------|---------|-------------|
| Results directory | `{{results_dir}}` | `/app/results` | Output directory for all results |
| Situation | `{{situation}}` | *(required)* | The business/decision context + available facts |
| Decision | `{{decision}}` | *(optional)* | The decision the diagnosis must inform; inferred if empty |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| Python 3.12 | Runtime | Yes | Runs the Step 4 validation script |
| `python -m json`/stdlib | Stdlib | Yes | No third-party packages needed |
| An LLM agent runtime | Agent | Yes | `claude-code` (default) drives the reasoning and writes the files |

No network access or secrets are required — this is a pure reasoning task over the provided
inputs. (If a context file was uploaded, only local file reads are needed.)

---

## Step 1: Setup & Input Guard

```bash
mkdir -p {{results_dir}}
```

- Read `{{situation}}`. If it is empty, whitespace, or still the literal placeholder, **fail
  fast**: write `validation_report.json` with `stages[0] = {name:"setup", passed:false,
  message:"situation input missing"}`, `overall_passed:false`, and stop.
- Read `{{decision}}`. If empty, infer the single most consequential decision the situation
  implies and record it; you will state it explicitly in the Executive Read.
- If `init_params.file_paths` is non-empty, read each file and fold its facts into the fact
  base (label them by source).

Do **not** start recommending yet. The next step is to separate what you know from what you
believe.

---

## Step 2: Build the Fact Base (separate facts, interpretations, assumptions)

Before any analysis, sort everything the situation gives you into three labelled buckets:

- **Facts** — verifiable, sourced, point-in-time or trend (e.g. "ARR $14M, YoY growth fell
  90% → 28% over 4 quarters").
- **Interpretations** — what a fact *might* mean (e.g. "deceleration suggests the core
  segment is saturating"). Mark confidence: high / medium / low.
- **Assumptions / unknowns** — beliefs not yet evidenced, and gaps you'd want filled.

Work **MECE** across these lenses so nothing is double-counted or missed: financial
performance, market position, customer momentum, competitive posture, operating health,
organizational constraints. Identify the *few* facts that actually matter for the decision —
resist the urge to list everything.

This separation is the quality bar the whole diagnosis is graded against. Keep it honest:
if a number is an estimate, say so; if a claim is an inference, label it.

---

## Step 3: Write `diagnosis.md` (the three methods, composed)

Write `{{results_dir}}/diagnosis.md` with **exactly** this structure. Every section is
required; tables must have the named columns (the Step 4 validator checks for them).

```markdown
# Strategic Diagnosis — <subject>

## Executive Read
<One answer-first paragraph: where the business really is, the decision being framed
(state it explicitly), and the single most important implication. No hedging.>

## 1. Situation Assessment
*Establishes the fact-based baseline before any recommendation.*

### Fact Base
| Area | Evidence (fact) | Interpretation | Confidence |
|---|---|---|---|
<≥4 rows across the MECE lenses. "Area" = financial/market/customer/competitive/operating/org.>

### Momentum Signals
| Signal | Direction | Why It Matters |
|---|---|---|
<Trend, not just point-in-time. Direction = improving / flat / deteriorating.>

### Strategic Issues
1. <issue> 2. <issue> 3. <issue>

### Open Questions
<The questions that must be answered before committing to a strategy.>

## 2. Growth Barrier Diagnosis
*Isolates the constraint that actually binds — not a list of initiatives.*

### Growth Gap
<Target, current trajectory, size of the gap.>

### Driver Tree
<MECE breakdown of the growth equation: acquisition × activation × conversion × retention ×
expansion × pricing × capacity. Show where momentum breaks.>

### Barrier Assessment
| Driver | Evidence | Impact | Confidence | Root Cause vs Symptom |
|---|---|---|---|---|
<One row per driver. Use evidence to separate cause from symptom.>

### Binding Constraint
<The ONE (at most two) constraint most limiting growth, stated plainly. This is the spine of
the recommendation.>

### Recommended Actions
1. <action tied to the constraint> 2. <action> 3. <action>
<Every action must trace to the diagnosed constraint.>

## 3. Assumption Audit
*Surfaces the load-bearing beliefs and turns the weak ones into tests.*

### Strategy Being Tested
<Brief description of the plan/decision whose assumptions you are auditing.>

### Assumption Register
| Assumption | Category | Importance | Evidence Strength | Risk |
|---|---|---|---|---|
<Include implicit assumptions, not only stated ones. Category = market/customer/economic/
operational/competitive/organizational.>

### Load-Bearing Assumptions
1. <assumption + why it carries the strategy's weight>
2. <assumption + why it carries the strategy's weight>

### Test Plan
| Assumption | Test | Data Needed | Owner | Decision Trigger |
|---|---|---|---|---|
<≥2 rows. Each test needs a concrete owner and a trigger that says what action follows if the
assumption fails. No vague tests.>

## 4. Framed Recommendation
**Verdict:** <Proceed | Pause | Test first | Redesign>

<2–4 sentences: what to do, anchored to the binding constraint and the assumption audit.
State what would change the verdict. End with the implication for the decision named in the
Executive Read.>
```

Quality bar (the diagnosis is judged on these — they mirror the source skill):
- Do **not** recommend before establishing the baseline.
- Label facts, interpretations, and assumptions separately throughout.
- Highlight **trend and momentum**, not only point-in-time performance.
- Name **one or two** binding constraints, not a long issue list.
- Every recommended action and every test traces to the diagnosis.
- Each test in the plan has evidence needed, an owner, and a decision trigger.

---

## Step 4: Evaluate, Validate & Iterate (max 3 rounds)

Run a programmatic structural check on `diagnosis.md` and write the result. This does not
grade prose taste — it enforces the method's non-negotiables so a weak pass can't slip
through.

```python
import json, os, re, pathlib
RD = pathlib.Path("{{results_dir}}")
doc = (RD / "diagnosis.md").read_text() if (RD / "diagnosis.md").exists() else ""
low = doc.lower()

def has(*needles): return all(n.lower() in low for n in needles)
def table_cols(*cols):  # a markdown table header row containing all named columns exists
    for line in doc.splitlines():
        if line.strip().startswith("|") and all(c.lower() in line.lower() for c in cols):
            return True
    return False

checks = [
    ("executive_read",   has("## Executive Read")),
    ("fact_base_table",  table_cols("Evidence", "Interpretation", "Confidence")),
    ("momentum",         has("Momentum Signals")),
    ("driver_tree",      has("Driver Tree")),
    ("binding_constraint", has("Binding Constraint")),
    ("barrier_table",    table_cols("Driver", "Impact", "Root Cause")),
    ("assumption_register", table_cols("Assumption", "Importance", "Evidence Strength")),
    ("test_plan",        table_cols("Test", "Owner", "Decision Trigger")),
    ("framed_verdict",   bool(re.search(r"verdict:[*\s]*(proceed|pause|test first|redesign)", low))),
    ("facts_labeled",    has("fact") and has("interpretation") and has("assumption")),
    ("no_placeholders",  not re.search(r"TODO|FIXME|TBD|<[a-z][a-z _/|+]*>", doc)),
]
# count test-plan rows and fact-base rows for a stronger gate
def count_rows(after_header):
    rows, seen = 0, False
    for line in doc.splitlines():
        if after_header.lower() in line.lower(): seen = True; continue
        if seen:
            if line.strip().startswith("|") and "---" not in line: rows += 1
            elif line.strip().startswith("## "): break
    return rows
checks.append(("test_plan_rows>=2", count_rows("Decision Trigger") >= 2))

passed = [c for c, ok in checks if ok]
failed = [c for c, ok in checks if not ok]
verdict = "PASS" if not failed else ("PARTIAL" if len(failed) <= 2 else "FAIL")

report = {
  "version": "1.0.0",
  "parameters": {"has_decision": bool("{{decision}}".strip())},
  "stages": [
    {"name": "setup",    "passed": True, "message": "inputs read"},
    {"name": "fact_base","passed": ("fact_base_table" in passed), "message": "facts/interpretations/confidence separated"},
    {"name": "growth_barrier","passed": ("binding_constraint" in passed and "barrier_table" in passed), "message": "binding constraint isolated"},
    {"name": "assumption_audit","passed": ("test_plan" in passed and "test_plan_rows>=2" in passed), "message": "load-bearing assumptions → tests with owner+trigger"},
    {"name": "structure","passed": (verdict != "FAIL"), "message": f"{len(passed)}/{len(checks)} checks: failed={failed}"},
  ],
  "results": {"checks_total": len(checks), "checks_passed": len(passed), "verdict": verdict},
  "overall_passed": (verdict != "FAIL"),
}
(RD / "validation_report.json").write_text(json.dumps(report, indent=2))
print(verdict, "failed:", failed)
```

| Status | Criteria |
|--------|----------|
| `PASS` | All structural checks pass — every section present, every named table column present, a single explicit verdict, test plan has ≥2 rows with Owner + Decision Trigger |
| `PARTIAL` | ≤2 checks fail (ship, but note the gaps in `summary.md`) |
| `FAIL` | >2 checks fail — go back to Step 3 |

**Iterate (max 3 rounds):** if `FAIL`, read `failed` from the report, fix the specific
missing section/column in `diagnosis.md`, and re-run this script. After 3 rounds keep the
best result and flag remaining gaps in `summary.md`.

### Common Fixes

| Issue | Fix |
|-------|-----|
| `fact_base_table` fails | The Fact Base table header must literally contain `Evidence`, `Interpretation`, `Confidence` |
| `binding_constraint` fails | Add a `### Binding Constraint` heading naming the ONE constraint — don't bury it in a list |
| `test_plan` / `test_plan_rows` fails | Test Plan table needs `Test`, `Owner`, `Decision Trigger` columns and ≥2 real rows |
| `framed_verdict` fails | Section 4 must start `**Verdict:** Proceed\|Pause\|Test first\|Redesign` |
| `no_placeholders` fails | Replace every `<bracketed>` template hint and TODO with real content |
| `facts_labeled` fails | The doc must explicitly use the words fact, interpretation, and assumption — that separation is the method |

---

## Step 5: Write Executive Summary

Write `{{results_dir}}/summary.md`:

```markdown
# Strategic Diagnosis — Summary

## Overview
- **Subject**: <what was diagnosed>
- **Decision framed**: <the decision from the Executive Read>
- **Date**: <run date>

## The Read (answer-first)
<2–3 sentences.>

## Binding Constraint
<The one constraint, plainly.>

## Recommendation
**<Proceed | Pause | Test first | Redesign>** — <one sentence + what would change it>

## Top Open Question
<The single most decision-relevant unknown.>

## Validation
- Verdict: <PASS|PARTIAL|FAIL>, checks <passed>/<total>
- Any gaps: <from validation_report.json, or "none">
```

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="{{results_dir}}"
for f in "$RESULTS_DIR/diagnosis.md" "$RESULTS_DIR/summary.md" "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then echo "FAIL: $f is missing or empty"; else echo "PASS: $f ($(wc -c < "$f") bytes)"; fi
done
python3 - "$RESULTS_DIR" <<'PY'
import json, sys, pathlib
rd = pathlib.Path(sys.argv[1])
try:
    r = json.load(open(rd / "validation_report.json"))
    print(f"PASS: validation_report verdict={r['results']['verdict']} overall_passed={r['overall_passed']}")
except Exception as e:
    print("FAIL: validation_report.json unreadable:", e)
PY
echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] `diagnosis.md` exists, non-empty, and follows the fixed Step 3 structure
- [ ] Facts, interpretations, and assumptions are labelled separately throughout
- [ ] The Fact Base leads; no recommendation appears before the baseline is established
- [ ] Exactly one (at most two) **Binding Constraint** is named
- [ ] Every recommended action and every test traces to the diagnosis
- [ ] The Test Plan has ≥2 rows, each with an Owner and a Decision Trigger
- [ ] Section 4 states a single explicit **Verdict**
- [ ] `summary.md` and `validation_report.json` written; verification script prints PASS for each

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Baseline before recommendation.** The most common failure of strategy prompts is
  answering before the work is structured. Resist it: the Fact Base section must stand on its
  own before the constraint or the recommendation appears.
- **Label confidence honestly.** A low-confidence interpretation flagged as such is more
  useful than a confident guess. The Fact Base `Confidence` column is load-bearing.
- **One constraint, not ten.** Treat growth as a system and find where it actually breaks.
  A diagnosis that lists ten issues has diagnosed nothing.
- **Implicit assumptions are where strategies die.** The Assumption Audit should surface the
  beliefs nobody stated out loud, not just restate the plan.
- **Every test needs a trigger.** "Validate pricing" is not a test. "Run a 3-cohort price
  test; if conversion drops >15% at the higher price, hold price and revisit packaging" is.
- **Synthetic or sanitized inputs only for shared examples.** When capturing sample outputs,
  use a fictional or fully-anonymized company — never a real customer's confidential data.
