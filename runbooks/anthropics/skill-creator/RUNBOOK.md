---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/anthropics/skills/skill-creator"
  source_host: "skills.sh"
  source_title: "Skill Creator"
  imported_at: "2026-05-01T02:40:55Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "anthropics"
    skill_name: "skill-creator"
    confidence: "high"
secrets: {}
---

# Skill Creator — Agent Runbook

## Objective

This runbook guides an AI agent through the complete lifecycle of creating,
testing, iteratively improving, and packaging AI agent skills. Starting from
intent capture and research, the agent drafts a SKILL.md, writes test cases,
runs parallel evaluations with and without the skill, reviews quantitative
benchmark results with the user, and iterates until the skill meets quality
standards. After finalizing the skill body, the runbook covers description
optimization to improve triggering accuracy, blind A/B comparison for rigorous
quality verification, and environment-specific adaptations for Claude.ai,
Cowork, and headless deployments.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files before the task is complete.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `<skill-name>-workspace/iteration-N/benchmark.json` | Aggregated benchmark results for the final iteration |
| `<skill-name>-workspace/iteration-N/benchmark.md` | Human-readable benchmark summary |
| `<skill-name>/SKILL.md` | Final skill file with optimized description in YAML frontmatter |
| `evals/evals.json` | Test case definitions with assertions |
| `/app/results/summary.md` | Executive summary with skill name, final benchmark scores, and any issues |
| `/app/results/validation_report.json` | Structured validation results with stages and `overall_passed` |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for validation and summary files |
| Skill intent | *(required)* | What the skill should enable Claude to do |
| Skill name | *(required)* | Slug identifier for the skill (e.g., `my-skill`) |
| Workspace dir | `<skill-name>-workspace/` | Sibling to the skill directory; holds iteration outputs |
| Skill path | *(required)* | Path to the skill directory containing SKILL.md |
| Model ID | `claude-sonnet-4-6` | Model powering the current session (used in description optimization) |
| Max optimization iterations | `5` | Maximum rounds for description optimizer |
| Run test cases | `true` | Whether to spawn subagent test runs |
| Dry run | `false` | If `true`, generate skill and evals but skip subagent test runs |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `python3` | CLI | Yes | Run aggregation and viewer scripts |
| `claude` CLI | CLI | Yes (description opt) | Used by `scripts/run_loop.py` for description optimization |
| `eval-viewer/generate_review.py` | Script | Yes | Generates the browser-based review UI |
| `scripts/aggregate_benchmark` | Script | Yes | Aggregates per-eval grading into benchmark.json |
| `scripts/run_loop` | Script | Yes (description opt) | Runs the description optimization loop |
| `scripts/package_skill` | Script | Optional | Packages the skill into a `.skill` bundle |
| `agents/grader.md` | Reference | Yes | Instructions for the grader subagent |
| `agents/comparator.md` | Reference | Optional | Instructions for blind A/B comparison |
| `agents/analyzer.md` | Reference | Optional | Instructions for benchmark analysis |
| `references/schemas.md` | Reference | Yes | JSON schemas for evals.json, grading.json, benchmark.json |
| `assets/eval_review.html` | Asset | Yes (description opt) | HTML template for trigger eval review |
| Subagent support | Runtime | Recommended | Enables parallel test execution and baseline runs |

---

## Step 1: Environment Setup

Verify the environment has all required tools and the skill path is valid.

```bash
# Check Python is available
python3 --version || { echo "ERROR: python3 not found"; exit 1; }

# Check claude CLI (needed for description optimization)
command -v claude >/dev/null 2>&1 && echo "claude CLI present" || echo "WARN: claude CLI not found (description optimization will be unavailable)"

# Verify skill path exists or create it
SKILL_NAME="${SKILL_NAME:-my-skill}"
SKILL_PATH="${SKILL_PATH:-./$SKILL_NAME}"
mkdir -p "$SKILL_PATH"
mkdir -p "$SKILL_PATH/evals"
mkdir -p "${SKILL_NAME}-workspace"
mkdir -p /app/results

echo "Setup complete. Skill path: $SKILL_PATH"
```

---

## Step 2: Capture Intent

Understand the user's intent before writing anything. If the current
conversation already contains a workflow the user wants to capture (e.g.,
they say "turn this into a skill"), extract answers from history first.

Ask (or infer from context) the following four questions:

1. **What should this skill enable Claude to do?**
2. **When should this skill trigger?** (specific user phrases and contexts)
3. **What is the expected output format?**
4. **Should we set up test cases?**
   - Skills with objectively verifiable outputs (file transforms, data
     extraction, code generation, fixed workflow steps) benefit from test cases.
   - Skills with subjective outputs (writing style, art) often do not.
   - Suggest the appropriate default, but let the user decide.

If the user already has a draft skill, skip to Step 4 (Run & Evaluate).

---

## Step 3: Interview and Research

Before writing the SKILL.md, proactively gather:

- Edge cases and boundary conditions
- Input/output formats and example files
- Success criteria and acceptance tests
- Dependencies (MCPs, external APIs, CLI tools)

Check available MCPs — if useful for research (doc search, similar skills,
best practices), research in parallel via subagents if available, otherwise
inline. Come prepared with context to minimize burden on the user.

---

## Step 4: Write the SKILL.md

Based on the user interview, produce `<skill-path>/SKILL.md` with this structure:

```markdown
---
name: <skill-identifier>
description: <When to trigger + what it does. Make it "a little bit pushy" to
             counteract Claude's tendency to undertrigger — e.g., "Use this
             skill whenever the user mentions X, Y, or Z, even if they don't
             explicitly ask for it.">
---

# <Skill Title>

<One-paragraph overview explaining the skill's purpose and high-level approach>

## <Section 1>
...
```

**Key writing guidelines:**

- **Description field** is the primary triggering mechanism. Include both
  *what* the skill does and *when* to use it. Avoid vague triggers; be specific.
- **Progressive Disclosure**: keep SKILL.md under 500 lines. Offload large
  reference content to `references/` files with clear pointers.
- **Bundled resources**: place executable scripts in `scripts/`, reference
  docs in `references/`, templates/assets in `assets/`.
- **Writing style**: explain the *why* behind instructions. Prefer imperative
  form. Avoid heavy-handed ALWAYS/NEVER; explain reasoning so the model
  understands the purpose, not just the rule.
- **Anatomy**:

```
skill-name/
├── SKILL.md (required — name + description frontmatter, markdown body)
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Templates, icons, fonts
```

Write a draft, then review it with fresh eyes before proceeding.

---

## Step 5: Write Test Cases

After drafting the skill, create 2–3 realistic test prompts — the kind of
message a real user would actually send. Share them with the user for
confirmation before running.

Save to `evals/evals.json` (assertions can be empty at this stage):

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

See `references/schemas.md` for the full schema including the `assertions`
field (added in Step 6).

---

## Step 6: Run & Evaluate (max 5 iterations)

This is one continuous sequence — do not stop partway through.

### 6.1 Spawn all runs in the same turn

For each test case, spawn two subagents in the **same turn** — one with the
skill, one as baseline. Do not run with-skill first and then come back for
baselines.

**With-skill run:**
```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about>
```

**Baseline run** (same prompt):
- *New skill*: no skill at all — save to `without_skill/outputs/`.
- *Improving existing skill*: snapshot the old version first
  (`cp -r <skill-path> <workspace>/skill-snapshot/`), point baseline at snapshot,
  save to `old_skill/outputs/`.

Write `eval_metadata.json` per eval directory:
```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### 6.2 Draft assertions while runs are in progress

Do not just wait — draft quantitative assertions now and explain them to
the user. Update `eval_metadata.json` and `evals/evals.json` with finalized
assertions. Good assertions are objectively verifiable and descriptively named.

Required grading output fields (exact names — the viewer depends on these):
`text`, `passed`, `evidence`.

### 6.3 Capture timing data as each run completes

When a subagent task completes, you receive `total_tokens` and `duration_ms`.
Save immediately to `timing.json` in each run directory:
```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```
This is the only opportunity to capture this data — do not batch.

### 6.4 Grade, aggregate, and launch the viewer

Once all runs finish:

1. **Grade** — spawn a grader subagent reading `agents/grader.md`, save
   `grading.json` per run. For assertions checkable programmatically, write and
   run a script (faster, more reliable, reusable).

2. **Aggregate** — run from the skill-creator directory:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```
   Produces `benchmark.json` and `benchmark.md`. Put each with_skill version
   before its baseline counterpart.

3. **Analyst pass** — read `agents/analyzer.md` ("Analyzing Benchmark Results")
   and surface non-discriminating assertions, high-variance evals, and
   time/token tradeoffs.

4. **Launch the viewer** — **IMPORTANT: do this BEFORE evaluating results
   yourself. Get outputs in front of the user ASAP.**
   ```bash
   nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```
   For iteration 2+: also pass `--previous-workspace <workspace>/iteration-<N-1>`.

   **Headless/Cowork:** use `--static <output_path>` to write a standalone
   HTML file. The "Submit All Reviews" button downloads `feedback.json`.

5. Tell the user: *"I've opened the results in your browser. 'Outputs' lets you
   click through test cases and leave feedback; 'Benchmark' shows the
   quantitative comparison. Come back when you're done."*

### 6.5 Read the feedback

When the user is done, read `feedback.json`:
```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."}
  ],
  "status": "complete"
}
```
Empty feedback = the user thought it was fine. Focus improvements on evals
with specific complaints.

Kill the viewer server when done:
```bash
kill $VIEWER_PID 2>/dev/null
```

---

## Step 7: Iterate on Errors (max 3 rounds)

After reading feedback, improve the skill and re-run:

1. **Generalize from feedback** — create skills that work across many prompts,
   not just the test examples. Avoid overfitting or rigid MUST/NEVER rules.
   Explain the *why* rather than enforcing mechanics blindly.
2. **Keep the prompt lean** — remove instructions that don't pull their weight.
   Read transcripts (not just final outputs) to spot wasted work.
3. **Bundle repeated work** — if all 3 test cases resulted in subagents writing
   the same helper script, put it in `scripts/` and reference it from SKILL.md.

After improving, repeat the iteration loop (Step 6) into
`iteration-<N+1>/`. Keep going until:
- The user says they're happy
- All feedback is empty
- No meaningful progress in the last round

**Common Fixes:**

| Issue | Fix |
|-------|-----|
| Output missing required structure | Add a template section with explicit format example |
| Skill over-triggers | Narrow the description with more specific context phrases |
| Skill under-triggers | Make the description "pushier" per the description-writing guide |
| Subagents reinvent the same helper | Bundle the helper into `scripts/`, reference from SKILL.md |
| Grading.json field names wrong | Ensure fields are `text`, `passed`, `evidence` (not `name`/`met`/`details`) |
| Viewer not generating | Explicitly run `generate_review.py` before self-evaluating |

---

## Step 8: Advanced — Blind Comparison (Optional)

For rigorous comparison between two skill versions, use the blind comparison
system in `agents/comparator.md` and `agents/analyzer.md`. An independent
agent evaluates both outputs without knowing which is which. This is optional
and most users won't need it — the human review loop is usually sufficient.

---

## Step 9: Description Optimization

After finalizing the skill body, offer to optimize the description for better
triggering accuracy.

### 9.1 Generate 20 trigger eval queries

Create a mix of should-trigger (8–10) and should-not-trigger (8–10) queries.
Make them realistic and specific — include file paths, personal context, company
names, typos, abbreviations, and varying length. Focus on **edge cases** and
**near-misses** rather than clear-cut examples.

Save as JSON:
```json
[
  {"query": "ok so my boss just sent me this xlsx file ...", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

### 9.2 Review with user

1. Read `assets/eval_review.html`
2. Replace `__EVAL_DATA_PLACEHOLDER__` with the JSON array,
   `__SKILL_NAME_PLACEHOLDER__` with the skill name,
   `__SKILL_DESCRIPTION_PLACEHOLDER__` with the current description
3. Write to `/tmp/eval_review_<skill-name>.html` and open it
4. User edits queries, toggles should-trigger flags, then clicks "Export Eval Set"
5. Read the downloaded `~/Downloads/eval_set.json` (check for `eval_set (1).json`)

### 9.3 Run the optimization loop

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model claude-sonnet-4-6 \
  --max-iterations 5 \
  --verbose
```

Use the model ID from your system prompt. The loop: splits 60% train / 40%
held-out test, evaluates the current description (3 runs per query), proposes
improvements based on failures, iterates up to 5 times, selects `best_description`
by test score (not train score) to avoid overfitting.

Periodically tail the output to give the user progress updates.

### 9.4 Apply the result

Take `best_description` from the JSON output, update SKILL.md frontmatter,
and show the user a before/after diff with final scores.

---

## Step 10: Package and Present

If the `present_files` tool is available:

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

Direct the user to the resulting `.skill` file path for installation.

---

## Step 11: Environment-Specific Adaptations

### Claude.ai

- **No subagents**: run test cases sequentially, executing SKILL.md instructions
  inline. Skip baseline runs.
- **No browser**: skip `generate_review.py`. Present results directly in
  conversation; ask for feedback inline.
- **No benchmarking**: skip quantitative benchmarks. Focus on qualitative
  user feedback.
- **Description optimization**: requires `claude -p` CLI — skip if unavailable.
- **Blind comparison**: requires subagents — skip.
- **Updating an existing skill**: preserve the original `name` frontmatter.
  Copy to `/tmp/skill-name/` before editing (installed path may be read-only).

### Cowork

- Subagents are available — full parallel test execution works.
- No display: use `--static <output_path>` for the eval viewer to write
  standalone HTML. User clicks to open in their browser.
- Feedback: "Submit All Reviews" downloads `feedback.json`. Copy it into
  the workspace directory for the next iteration.
- Packaging works — `package_skill.py` just needs Python and a filesystem.
- Description optimization (`run_loop.py`) works fine in Cowork.
- **Updating an existing skill**: follow the Claude.ai update guidance above.

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
SKILL_NAME="${SKILL_NAME:-my-skill}"
WORKSPACE="${SKILL_NAME}-workspace"

# Check SKILL.md exists and has frontmatter
if [ -f "${SKILL_NAME}/SKILL.md" ]; then
  echo "PASS: ${SKILL_NAME}/SKILL.md exists"
  python3 -c "import yaml,re,pathlib; t=pathlib.Path('${SKILL_NAME}/SKILL.md').read_text(); m=re.match(r'^---\n(.*?)\n---',t,re.DOTALL); fm=yaml.safe_load(m.group(1)); assert 'name' in fm and 'description' in fm; print('PASS: SKILL.md frontmatter valid')"
else
  echo "FAIL: ${SKILL_NAME}/SKILL.md missing"
fi

# Check evals
[ -f "evals/evals.json" ] && echo "PASS: evals/evals.json" || echo "FAIL: evals/evals.json missing"

# Check benchmark for latest iteration
LATEST=$(ls -d "${WORKSPACE}"/iteration-* 2>/dev/null | sort -V | tail -1)
if [ -n "$LATEST" ]; then
  [ -f "${LATEST}/benchmark.json" ] && echo "PASS: benchmark.json" || echo "FAIL: benchmark.json missing in ${LATEST}"
  [ -f "${LATEST}/benchmark.md" ] && echo "PASS: benchmark.md" || echo "FAIL: benchmark.md missing in ${LATEST}"
fi

# Check required output files
for f in /app/results/summary.md /app/results/validation_report.json; do
  [ -s "$f" ] && echo "PASS: $f ($(wc -c < "$f") bytes)" || echo "FAIL: $f missing or empty"
done
```

### Checklist

- [ ] `SKILL.md` exists with valid YAML frontmatter (`name`, `description`)
- [ ] `evals/evals.json` written with at least 2 test cases and assertions
- [ ] At least one complete iteration directory with `benchmark.json` and `benchmark.md`
- [ ] User has reviewed results via the eval viewer (or inline on Claude.ai)
- [ ] Description optimization completed or explicitly skipped (with user consent)
- [ ] `summary.md` written with skill name, final benchmark scores, and issues
- [ ] `validation_report.json` written with `stages`, `results`, and `overall_passed`
- [ ] Verification script printed PASS for every line

**If ANY item fails, go back and fix it before stopping.**

---

## Tips

- **Prefer bundling over re-invention.** If subagents consistently write the
  same helper script, that script belongs in `scripts/`. Future invocations
  should not pay the reinvention cost.
- **Never skip the eval viewer.** Even if benchmark numbers look great,
  the human review step catches qualitative issues that metrics miss. Run
  `generate_review.py` BEFORE self-evaluating.
- **Progressive disclosure prevents bloat.** If SKILL.md approaches 500 lines,
  introduce a `references/` file with a table of contents and link to it from
  SKILL.md. Lean SKILL.md = fast context loading on every trigger.
- **"Pushy" descriptions beat vague ones.** Claude undertriggers by default.
  Explicitly naming contexts in the description ("even if they don't mention X")
  materially improves trigger rates.
- **Explain the why, not just the what.** Instructions backed by reasoning
  generalize better than rigid rules. Avoid ALWAYS/NEVER in all-caps unless
  truly necessary.
- **Management dir is append-only.** Never delete or rewrite prior iteration
  records — duplicate-detection and variance analysis depend on full history.
- **Attribution low-confidence isn't a blocker.** It surfaces in the PR body
  so a human reviewer can rename the directory before merging.
