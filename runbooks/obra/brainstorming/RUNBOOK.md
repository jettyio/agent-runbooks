---
version: 1.0.0
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: https://skills.sh/obra/superpowers/brainstorming
  source_host: skills.sh
  source_title: brainstorming
  imported_at: '2026-05-01T02:44:10Z'
  imported_by: skill-to-runbook-converter@1.0.0
  attribution:
    collection_or_org: obra
    skill_name: brainstorming
    confidence: high
---

# Brainstorming Ideas Into Designs — Agent Runbook

## Objective

Help the user turn ideas into fully formed designs and specifications through natural collaborative dialogue. This runbook guides an agent to explore project context, ask clarifying questions one at a time, propose 2-3 implementation approaches with trade-offs, present a structured design for approval, write a formal design document, and then transition to implementation planning. The process enforces a **hard gate**: no implementation action may be taken until the user has reviewed and approved a design. This applies universally — simple projects are where unexamined assumptions cause the most wasted work.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/design_doc.md` | The final approved design document written during the brainstorming process |
| `/app/results/approaches.md` | The 2-3 proposed approaches with trade-offs and recommendation |
| `/app/results/clarifying_questions.md` | Log of all clarifying questions asked and answers received |
| `/app/results/summary.md` | Executive summary of the brainstorming session and design outcome |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Topic / idea | *(required)* | The feature, project, or change to brainstorm |
| Project context path | `.` | Root of the project to explore for context |
| Spec output path | `docs/superpowers/specs/` | Where to write the design document |
| Design doc date | *(current date)* | Date prefix for the spec file name |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `git` | CLI | Yes | Check recent commits for project context |
| File system access | Runtime | Yes | Read project files, docs, and write design doc |
| User interaction | Human-in-loop | Yes | Clarifying questions and design approval require user responses |

---

## Step 1: Environment Setup

Verify the environment is ready and the project context is accessible.

```bash
echo "=== Brainstorming Environment Setup ==="
# Verify git is available for context exploration
command -v git >/dev/null && echo "PASS: git available" || echo "WARN: git not available"

# Create output directories
mkdir -p /app/results
mkdir -p "$(dirname "${SPEC_OUTPUT_PATH:-docs/superpowers/specs}")"

# Verify topic was provided
if [ -z "${TOPIC}" ]; then
  echo "ERROR: TOPIC parameter is required"
  exit 1
fi
echo "Topic: ${TOPIC}"
echo "Setup complete"
```

---

## Step 2: Explore Project Context

Before asking any questions, explore the current project state to ground your understanding.

```bash
# Check project structure
ls -la .
git log --oneline -10 2>/dev/null || echo "No git history"
find . -name "*.md" -not -path "*/node_modules/*" -not -path "*/.git/*" | head -20
```

Actions:
1. Read any existing documentation in `docs/`, `README.md`, or similar
2. Review recent git commits to understand recent work
3. Identify existing patterns, architecture decisions, and conventions
4. Note any existing specs in `docs/superpowers/specs/` that might be related

---

## Step 3: Assess Scope

Before asking detailed questions, assess the scope of the request.

- If the request describes **multiple independent subsystems** (e.g., "build a platform with chat, file storage, billing, and analytics"), flag this immediately. Help the user decompose into sub-projects: what are the independent pieces, how do they relate, what order should they be built?
- For **appropriately-scoped projects**, proceed to Step 4.
- Each sub-project gets its own spec → plan → implementation cycle.

---

## Step 4: Offer Visual Companion (if applicable)

**This step is its own message. Do NOT combine it with any other content.**

If the topic is likely to involve visual questions (mockups, layouts, architecture diagrams), offer the visual companion:

> "Some of what we're working on might be easier to explain if I can show it to you in a web browser. I can put together mockups, diagrams, comparisons, and other visuals as we go. This feature is still new and can be token-intensive. Want to try it? (Requires opening a local URL)"

Wait for the user's response before proceeding. If they decline, continue with text-only mode.

---

## Step 5: Ask Clarifying Questions (max 9 rounds)

Ask clarifying questions **one at a time** to understand purpose, constraints, and success criteria. Prefer multiple-choice questions when possible.

Focus areas:
- What problem does this solve? Who uses it?
- What are the hard constraints (performance, security, compatibility)?
- What does success look like?
- What are the non-goals (YAGNI)?

**Rules:**
- One question per message — never bundle multiple questions
- If a topic needs more exploration, break it into multiple sequential questions
- Stop when you have enough to propose 2-3 approaches

Log all questions and answers to `/app/results/clarifying_questions.md` as you go.

---

## Step 6: Propose 2-3 Approaches (max 3 rounds)

Present 2-3 different implementation approaches with trade-offs. Lead with your recommended option.

Format each approach as:
- **Name**: Short descriptive title
- **Description**: What it does and how
- **Trade-offs**: Pros and cons
- **Best for**: When this approach shines

Write the approaches to `/app/results/approaches.md`.

Wait for the user to select or refine before proceeding.

---

## Step 7: Present Design Sections

Once the approach is selected, present the design **section by section**, asking for approval after each.

Required sections (scale to complexity):
1. **Architecture** — Overall structure, components, and how they connect
2. **Components** — Individual units with clear purpose and interfaces
3. **Data Flow** — How data moves through the system
4. **Error Handling** — Failure modes and recovery strategies
5. **Testing** — How each component will be verified

Design principles to apply:
- Break into smaller units with one clear purpose each
- Well-defined interfaces — can someone understand a unit without reading internals?
- Prefer isolation over coupling
- Follow existing patterns in the codebase

After each section: "Does this look right so far?"

If the user requests changes, revise and re-present that section.

---

## Step 8: Write Design Document

After the user approves all design sections, write the validated design to:
`docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`

(Override path with user preferences if stated.)

The document should be clear, unambiguous, and implementation-ready. Use concise prose — each section scaled to its complexity.

```bash
# Commit the design document
SPEC_FILE="docs/superpowers/specs/$(date +%Y-%m-%d)-${TOPIC_SLUG}-design.md"
git add "$SPEC_FILE"
git commit -m "Add design spec for ${TOPIC}"
```

Copy the design doc to `/app/results/design_doc.md` as well.

---

## Step 9: Spec Self-Review

After writing the spec, perform a self-review with fresh eyes:

| Check | Criteria |
|-------|----------|
| Placeholder scan | No "TBD", "TODO", incomplete sections, or vague requirements |
| Internal consistency | No contradictions between sections; architecture matches features |
| Scope check | Focused enough for a single implementation plan |
| Ambiguity check | Every requirement has exactly one interpretation |

Fix any issues inline. No re-review needed — just fix and move on.

---

## Step 10: User Review Gate

Ask the user to review the written spec:

> "Spec written and committed to `<path>`. Please review it and let me know if you want to make any changes before we start writing out the implementation plan."

Wait for user's response. If they request changes, make them and re-run the spec review loop (Step 9). Only proceed once the user explicitly approves.

---

## Step 11: Transition to Implementation Planning

After user approves the spec, invoke the `writing-plans` skill to create a detailed implementation plan.

**Do NOT invoke any other skill.** `writing-plans` is the next and only step.

```
# Invoke writing-plans skill
# This is the terminal state of the brainstorming process
```

---

## Step 12: Write Executive Summary

Write `/app/results/summary.md` capturing the full brainstorming session:

```markdown
# Brainstorming Session Summary

## Topic
<topic or idea brainstormed>

## Design Decision
<selected approach and rationale>

## Spec Location
<path to committed design doc>

## Key Decisions Made
- <Decision 1>
- <Decision 2>

## Open Questions
- <Any unresolved items>

## Next Steps
- Review spec at <path>
- Invoke writing-plans to begin implementation planning
```

---

## Step 13: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/design_doc.md" \
  "$RESULTS_DIR/approaches.md" \
  "$RESULTS_DIR/clarifying_questions.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] Project context explored (files, docs, recent commits reviewed)
- [ ] Scope assessed — single project or decomposed into sub-projects
- [ ] Visual companion offered if applicable (own message, no other content)
- [ ] Clarifying questions asked one at a time until sufficient understanding
- [ ] 2-3 approaches proposed with trade-offs; user selected one
- [ ] Design presented section by section with user approval at each
- [ ] Design document written to `docs/superpowers/specs/` and committed
- [ ] Spec self-review completed (no TODOs, no contradictions, unambiguous)
- [ ] User reviewed and approved the spec
- [ ] `writing-plans` skill invoked as next step
- [ ] `/app/results/design_doc.md` exists and is non-empty
- [ ] `/app/results/approaches.md` exists and is non-empty
- [ ] `/app/results/clarifying_questions.md` exists and is non-empty
- [ ] `/app/results/summary.md` exists and is non-empty
- [ ] `/app/results/validation_report.json` exists with `overall_passed`

**If ANY item fails, go back and fix it before finishing.**

---

## Tips

- **One question at a time** — don't overwhelm with multiple questions; if a topic needs more exploration, break it into multiple sequential messages.
- **Multiple choice preferred** — easier to answer than open-ended when possible.
- **YAGNI ruthlessly** — remove unnecessary features from all designs; the right design is the minimum that meets the requirements.
- **Explore alternatives** — always propose 2-3 approaches before settling on one.
- **Incremental validation** — present design section by section, get approval before moving on; do not present the full design at once.
- **The hard gate is absolute** — do NOT write any code, scaffold any project, or take any implementation action until the user has approved the design. This applies even for "obviously simple" projects.
- **Visual companion is opt-in per session, but per-question by choice** — even after the user accepts, decide for each question whether visual or text treatment is better.
- **Explore existing code before proposing changes** — follow existing patterns; include targeted improvements only where they serve the current goal.
