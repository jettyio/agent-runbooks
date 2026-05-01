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
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "anthropics"
    skill_name: "skill-creator"
    confidence: "high"
secrets: {}
---

# Skill Creator — Agent Runbook

## Objective

Create, test, and iteratively improve AI agent skills with structured evaluation and benchmarking. This runbook guides an agent through the full skill development lifecycle: capturing user intent, drafting a SKILL.md, running parallel test evaluations with and without the skill, generating interactive review outputs, iterating based on user feedback, and optionally optimizing the skill's description for triggering accuracy. The agent adapts the workflow to the user's familiarity with technical concepts and their current position in the development cycle.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files before the task is complete. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/skill.md` | The final authored SKILL.md for the new or improved skill |
| `/app/results/evals/evals.json` | Test cases used during evaluation |
| `/app/results/benchmark.json` | Aggregated benchmark results from grading runs |
| `/app/results/summary.md` | Executive summary with skill overview, evaluation results, and iteration history |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Skill name | *(required)* | Identifier for the skill being created or improved |
| Skill directory | `/app/results/skill/` | Location where the skill folder will be written |
| Workspace directory | `/app/results/workspace/` | Where iteration results, eval outputs, and benchmarks are stored |
| Existing skill path | *(optional)* | Path to an existing skill to improve; omit when creating from scratch |
| Max iterations | `3` | Maximum improvement cycles before final packaging |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `python3` | CLI | Yes | Run grading scripts, generate eval viewer, optimize description |
| `eval-viewer/generate_review.py` | Script | Yes | Generates interactive HTML reviewer for eval outputs |
| `scripts/package_skill.py` | Script | Yes | Packages the skill folder into a `.skill` file |
| `scripts/run_loop.py` | Script | Conditional | Description optimization loop — requires `claude -p` CLI |
| `claude` CLI | CLI | Conditional | Required for description optimization (`claude -p`) |
| Claude API / subagents | Agent capability | Conditional | Parallel eval runs (not available in Claude.ai) |

---

## Step 1: Environment Setup

```bash
echo "=== Setting up skill creator environment ==="
mkdir -p /app/results/skill
mkdir -p /app/results/workspace
mkdir -p /app/results/evals

# Verify Python is available
python3 --version || { echo "ERROR: python3 not installed"; exit 1; }

# Check if subagents are available (Claude Code vs Claude.ai)
echo "Checking execution environment..."
# If running in Claude.ai: sequential mode, no baseline runs, no browser viewer
# If running in Cowork/Claude Code: parallel subagents, baselines, static viewer output
```

Determine the user's starting point:
- **New skill from scratch**: Proceed to Step 2 (Capture Intent)
- **Improving an existing skill**: Snapshot it first, then proceed to Step 4 (Run Evaluations)
- **Just eval/test**: Proceed directly to Step 4

---

## Step 2: Capture Intent and Interview

### Capture Intent

Start by understanding the user's intent. If the current conversation already contains a workflow the user wants to capture (e.g., "turn this into a skill"), extract answers from the conversation history first — the tools used, the sequence of steps, corrections the user made, input/output formats observed.

Answer these questions (fill from context where possible; ask the user for the rest):

1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What is the expected output format?
4. Should we set up test cases? (recommended for objectively verifiable outputs; optional for subjective tasks)

### Interview and Research

Proactively ask about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until this is settled.

Check available MCPs — if useful for research, investigate in parallel via subagents when available.

---

## Step 3: Write the SKILL.md

Based on the interview, produce the skill file at `/app/results/skill/SKILL.md`.

Required frontmatter fields:
- `name`: Skill identifier (lowercase, hyphen-separated)
- `description`: When to trigger AND what it does. Make it slightly "pushy" to counter Claude's tendency to undertrigger. Include specific phrases and contexts.
- `compatibility`: Required tools/dependencies (optional; omit if not needed)

### Skill Anatomy

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    — Executable code for deterministic/repetitive tasks
    ├── references/ — Docs loaded into context as needed
    └── assets/     — Files used in output (templates, icons, fonts)
```

### Writing Guidelines

- Use imperative form in instructions
- Explain *why* things are important, not just *what* to do — prefer theory of mind over rigid MUSTs
- Keep SKILL.md under 500 lines; use references/ for overflow with clear pointers
- Include input/output examples in this format:
  ```markdown
  **Example:**
  Input: <user message>
  Output: <expected result>
  ```
- For large reference files (>300 lines), include a table of contents
- For multi-domain skills, organize by variant under `references/`

After drafting, write test cases to `/app/results/evals/evals.json`:

```json
{
  "skill_name": "<skill-name>",
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

Share the test prompts with the user for approval before running.

---

## Step 4: Run Evaluations (max 3 rounds)

This section is one continuous sequence — do not stop partway through. Do NOT use `/skill-test` or any other testing skill.

Organize results under `/app/results/workspace/iteration-<N>/eval-<name>/`.

### Step 4a: Spawn All Runs in the Same Turn

For each test case, launch both runs simultaneously (or sequentially if subagents are unavailable):

**With-skill run:**
```
- Skill path: /app/results/skill/
- Task: <eval prompt>
- Input files: <eval files, or "none">
- Save outputs to: /app/results/workspace/iteration-<N>/eval-<name>/with_skill/outputs/
```

**Baseline run** (context-dependent):
- **New skill**: No skill access. Same prompt, save to `without_skill/outputs/`
- **Improving existing skill**: Snapshot first (`cp -r <skill-path> /app/results/workspace/skill-snapshot/`), then point baseline at snapshot. Save to `old_skill/outputs/`
- **Claude.ai**: Skip baseline entirely

Write `eval_metadata.json` for each eval directory:

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### Step 4b: Draft Assertions While Runs Progress

While runs are executing, create quantitative assertions for each eval. Explain the assertions to the user. Assertions go into the `assertions` field of `eval_metadata.json`. See `references/schemas.md` for the full assertion schema.

### Step 4c: Capture Timing Data

Save to each eval directory's `timing.json`:

```json
{
  "total_tokens": 0,
  "duration_ms": 0,
  "total_duration_seconds": 0.0
}
```

### Step 4d: Grade and Generate Eval Viewer

1. Grade each run against assertions using `agents/grader.md` instructions
2. Aggregate results into `/app/results/workspace/iteration-<N>/benchmark.json`
3. **ALWAYS generate the eval viewer before evaluating results yourself:**

```bash
# Claude Code / Cowork (static output):
nohup python3 eval-viewer/generate_review.py \
  /app/results/workspace/iteration-N \
  --skill-name "<skill-name>" \
  --benchmark /app/results/workspace/iteration-N/benchmark.json \
  --static /app/results/workspace/iteration-N/review.html \
  > /dev/null 2>&1 &

# Local with browser:
python3 eval-viewer/generate_review.py \
  /app/results/workspace/iteration-N \
  --skill-name "<skill-name>" \
  --benchmark /app/results/workspace/iteration-N/benchmark.json
```

Present the review link to the user and wait for their feedback.

### Step 4e: Read Feedback

Feedback is saved to `feedback.json` (downloaded from viewer in Cowork, or written by the server locally):

```json
{
  "reviews": [
    {
      "run_id": "eval-0-with_skill",
      "feedback": "the chart is missing axis labels",
      "timestamp": "..."
    }
  ],
  "status": "complete"
}
```

---

## Step 5: Iterate on the Skill (max 3 rounds)

Apply improvements based on user feedback and quantitative benchmark results:

- **Generalize from feedback** — do not overfit to specific test examples
- **Keep prompts lean** — remove non-essential content
- **Explain reasoning** — preserve the "why" behind instructions
- **Look for repeated work** — patterns across test cases reveal abstraction opportunities

Iteration loop:
1. Apply improvements to `/app/results/skill/SKILL.md`
2. Rerun all test cases into a new `iteration-<N+1>/` directory
3. Generate the eval viewer with the previous iteration as reference
4. Wait for user review
5. Read `feedback.json` and repeat

Stop when: user is satisfied, feedback is empty, or no meaningful progress after 3 rounds.

---

## Step 6: Description Optimization (Optional)

Run only after the skill content is finalized and the user agrees it is in good shape. Requires `claude -p` (Claude Code environments only — skip on Claude.ai).

### Generate Trigger Eval Queries

Create 20 eval queries (8–10 should-trigger, 8–10 should-not-trigger):

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

- **Should-trigger**: different phrasings of same intent, casual/formal variations, uncommon cases
- **Should-not-trigger**: near-misses with keywords, adjacent domains, tricky edge cases

Present the eval set to the user for review and approval.

### Run the Optimization Loop

Use the model ID from your current system prompt:

```bash
python3 -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path /app/results/skill/ \
  --model <model-id> \
  --max-iterations 5 \
  --verbose
```

Periodically tail the output to give the user updates on iteration progress and scores.

The script splits the eval set 60/40 train/test, evaluates the current description (running each query 3×), calls Claude to propose improvements based on failures, and re-evaluates each new description. After up to 5 iterations, it returns `best_description` selected by test score (not train, to avoid overfitting) and an HTML report.

### Apply the Result

Update `/app/results/skill/SKILL.md` frontmatter with `best_description`. Show the user a before/after comparison with scores.

---

## Step 7: Package and Present

Package the finished skill:

```bash
python3 -m scripts.package_skill /app/results/skill/
```

Copy the resulting `.skill` file to `/app/results/`. If the `present_files` tool is available, present it directly to the user; otherwise, tell the user the path so they can download it.

For existing-skill updates:
- Preserve the original `name` field from the skill's frontmatter unchanged
- The output `.skill` filename must match the original skill name (not `-v2`)

---

## Step 8: Write Summary and Benchmark

Copy the final benchmark to `/app/results/benchmark.json`.

Write `/app/results/summary.md`:

```markdown
# Skill Creator — Results

## Skill Overview
- **Skill Name**: <name>
- **Description**: <final description>
- **Created/Updated**: <date>

## Evaluation Summary

| Iteration | Evals Run | Assertions Passed | User Feedback |
|-----------|-----------|-------------------|---------------|
| 1 | ... | ... | ... |

## Description Optimization
- **Before**: <original description>
- **After**: <optimized description>
- **Test score improvement**: ...

## Output Files
- Skill: /app/results/skill/SKILL.md
- Package: /app/results/<skill-name>.skill
- Benchmark: /app/results/benchmark.json
```

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/skill/SKILL.md" \
  "$RESULTS_DIR/evals/evals.json" \
  "$RESULTS_DIR/benchmark.json" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# Verify SKILL.md has required frontmatter fields
python3 - << 'EOF'
import yaml, pathlib, re
skill = pathlib.Path("/app/results/skill/SKILL.md").read_text()
fm = re.match(r'^---\n(.*?)\n---', skill, re.DOTALL)
if not fm:
    print("FAIL: SKILL.md missing frontmatter")
else:
    data = yaml.safe_load(fm.group(1))
    for field in ('name', 'description'):
        if field not in data:
            print(f"FAIL: SKILL.md missing required field: {field}")
        else:
            print(f"PASS: SKILL.md has '{field}'")
EOF
```

### Checklist

- [ ] `/app/results/skill/SKILL.md` exists with `name` and `description` frontmatter
- [ ] `/app/results/evals/evals.json` exists with at least 2 test cases
- [ ] `/app/results/benchmark.json` exists with grading results
- [ ] `/app/results/summary.md` exists with iteration history and final description
- [ ] `/app/results/validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Eval viewer was generated and shown to the user before each iteration
- [ ] User confirmed satisfaction before packaging
- [ ] Verification script printed PASS for every line

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Pay attention to user context cues.** Adjust technical vocabulary to match the user's familiarity — "evaluation" and "benchmark" are borderline OK; "JSON" and "assertion" need confirmed understanding before using without explanation.
- **ALWAYS generate the eval viewer before evaluating results yourself.** The human review step is critical — get results in front of the user ASAP before making corrections.
- **Generalize from feedback, don't overfit.** If a user says "add more axis labels", ask whether this should always be the default — not just for this test case.
- **Lean toward under-specifying.** Skills that over-constrain Claude leave no room for adaptation. Explain the intent; trust Claude to handle the details.
- **Description "pushiness" matters.** Claude tends to undertrigger skills. Make descriptions slightly aggressive: include "use this whenever…" phrasing.
- **Preserve original names on updates.** If improving an existing skill, never rename it. The output must use the same `name` as the original.
- **Claude.ai vs Claude Code.** In Claude.ai: sequential runs, no baseline, no browser viewer, no description optimization. In Claude Code / Cowork: full parallel workflow, static `--static` flag for viewer, description optimization via `run_loop.py`.

## Common Fixes

| Issue | Fix |
|-------|-----|
| Eval viewer not opening in Cowork | Use `--static <output_path>` flag to write standalone HTML |
| Skill not triggering in tests | Description may be too narrow — add more trigger phrases and contexts |
| Skill body over 500 lines | Move sections to `references/` and add clear pointers from SKILL.md |
| Overfitting to test cases | Step back and generalize the principle, not the specific example |
| `claude -p` not found | Description optimization requires Claude Code — skip on Claude.ai |
| Packaging fails with permissions | Stage in `/tmp/<skill-name>/`, then copy to output directory |
