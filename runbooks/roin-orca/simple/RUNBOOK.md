---
version: 1.0.0
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: https://skills.sh/roin-orca/skills/simple
  source_host: skills.sh
  source_title: Fun Brainstorming
  imported_at: '2026-05-01T02:44:04Z'
  imported_by: skill-to-runbook-converter@1.0.0
  attribution:
    collection_or_org: roin-orca
    skill_name: simple
    confidence: high
---

# Fun Brainstorming — Agent Runbook

## Objective

Invoke before any creative or architectural work — feature design, component creation, or behavioral changes. A streamlined brainstorming process optimized for fast, focused decision-making

This runbook implements the **Simple** brainstorming framework: a structured yet lightweight process designed to move from idea to actionable direction quickly. It preserves the rigor of collaborative design — exploring intent, evaluating trade-offs, and validating decisions — while eliminating process overhead that does not scale to small and medium tasks. The agent guides the user through Discover, Propose, Converge, Capture, and Implement phases with no code or implementation output until the user has explicitly approved a direction.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary of the brainstorming session: chosen direction, key decisions, rationale |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/direction.md` | Capture document: the approved design direction (what, why, key decisions) |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Task description | *(required)* | The feature, component, or change to brainstorm |
| Context | *(optional)* | Additional codebase context, constraints, or success criteria |
| Max clarification rounds | `3` | Maximum questions allowed in the Discover phase |
| Max revision rounds | `2` | Maximum Converge revision iterations before escalating |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| Claude Code agent | Agent | Yes | Runs the brainstorming conversation |
| User input | Human | Yes | Approve/reject proposed directions during Converge phase |

## Step 1: Environment Setup

Create the output directory and verify the task description is provided.

```bash
echo "=== Simple Brainstorming Setup ==="
mkdir -p /app/results

# Verify task description is available
if [ -z "$TASK_DESCRIPTION" ]; then
  echo "ERROR: TASK_DESCRIPTION is not set. Provide a description of the task to brainstorm."
  exit 1
fi
echo "Task: $TASK_DESCRIPTION"
echo "Results dir: /app/results"
echo "Setup complete."
```

## Step 2: Discover -- Understand the Task

Assess the project context: codebase conventions, existing patterns, and relevant constraints. Ask **at most 3 focused clarifying questions** (prefer multiple-choice). Batch related questions together in a single message. If the request is already clear, skip straight to Step 3.

**Ground Rules (DO NOT SKIP)**

Do NOT write any code, scaffold any files, or take any implementation action until the user has explicitly approved a direction in Step 4. This applies even when the task seems obvious. The whole point of brainstorming is to pause and think before building. Respect that boundary.

Questions to address (if not already clear):

1. What is the intended outcome and success criteria?
2. What constraints apply (performance, compatibility, team conventions)?
3. Are there existing patterns or components that should be reused or replaced?

Record the answers before proceeding.

## Step 3: Propose -- Present Two Approaches

Present exactly **2 approaches** with trade-offs. Lead with your recommendation and explain why. Keep each option to a short paragraph. Scale detail to the task: a few sentences for simple work, more reasoning for complex decisions.

Format:

```
**Recommended: Option A -- <name>**
<Short description of the approach>
Trade-offs: <pros and cons>

**Alternative: Option B -- <name>**
<Short description of the approach>
Trade-offs: <pros and cons>

**Recommendation:** Option A because <reason>
```

## Step 4: Converge -- Get Explicit Approval (max 2 rounds)

Present the proposal and wait for explicit user approval. If rejected, revise and repropose. **max 2 revision rounds**. If still not aligned after 2 rounds, ask the user to state what they want directly.

Track revision rounds internally and stop re-proposing after 2 failed rounds.

## Step 5: Capture -- Record the Chosen Direction

Write the approved direction to `/app/results/direction.md`:

```markdown
# Chosen Direction

## What
<One sentence: what we are building/changing>

## Why
<One sentence: the reason this approach was chosen over alternatives>

## Key Decisions
- <Decision 1>
- <Decision 2>
- <Decision 3>

## Approved at
<ISO-8601 timestamp>
```

Write it to the first file created during implementation, or share it in chat if no file is created immediately.

## Step 6: Implement -- Begin Building

Only after `/app/results/direction.md` has been written and the user has explicitly approved: begin implementation. Reference the direction document throughout to stay on track.

## Step 7: Iterate on Errors (max 3 rounds)

If any validation check fails:

1. Read the specific failed check from `validation_report.json`
2. Apply a targeted fix
3. Re-validate
4. Repeat up to 3 times total

After 3 rounds with unresolved failures, abort and write the failure into `summary.md` with `overall_passed: false`.

## Step 8: Write Executive Summary

Write `/app/results/summary.md`:

```markdown
# Simple Brainstorming Session -- Summary

## Task
<Task description>

## Chosen Direction
<One-paragraph summary of the approved direction>

## Key Decisions
- <Decision 1>
- <Decision 2>

## Outcome
<What was built or the next steps>
```

## Step 9: Final Checklist (MANDATORY -- do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/direction.md"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== FINAL OUTPUT VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] `direction.md` exists and records the approved direction with what/why/key-decisions
- [ ] `summary.md` exists and summarizes the session
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] No code or scaffolding was written before explicit user approval in Step 4
- [ ] Verification script printed PASS for every line

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Speed over ceremony** -- Value thinking over artifacts. Skip formality wherever it does not add real value.
- **YAGNI** -- Design only for what is needed right now. Speculative design creates more problems than it solves.
- **Bias toward action** -- When two options are close in quality, pick one and go. Movement creates clarity.
- **Batched discovery** -- Ask clarifying questions together, not one at a time. Get what you need in one round and move forward.
- **Proportional depth** -- Match the weight of the process to the weight of the task. A small bug fix might go through Steps 2-3 in a single message. A new subsystem deserves a more thorough exploration.
