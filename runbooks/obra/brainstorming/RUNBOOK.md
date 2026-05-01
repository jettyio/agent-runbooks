---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/obra/superpowers/brainstorming"
  source_host: "skills.sh"
  source_title: "Brainstorming Ideas Into Designs"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "obra"
    skill_name: "brainstorming"
    confidence: "high"
secrets: {}
---

# Brainstorming Ideas Into Designs — Agent Runbook

## Objective

Help turn ideas into fully formed designs and specs through natural collaborative dialogue. This runbook enforces a hard gate: no code, scaffolding, or implementation actions until a design has been presented and the user has approved it. Start by understanding the current project context, ask questions one at a time to refine the idea, propose multiple approaches, present a design in sections, write and review a spec document, then transition to implementation planning via the `writing-plans` skill.

> **HARD GATE:** Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until you have presented a design and the user has approved it. This applies to EVERY project regardless of perceived simplicity.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files. The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/design_doc.md` | The validated design spec (mirrors what was committed to `docs/superpowers/specs/`) |
| `/app/results/approaches.md` | The 2–3 proposed approaches with trade-offs and recommendation |
| `/app/results/summary.md` | Executive summary: design decisions, approaches considered, approval status |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Topic / idea | *(required)* | The idea, feature, or problem to brainstorm |
| Spec output path | `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` | Where the design doc is committed in the repo |
| Visual companion | `false` | If `true`, offer a browser-based companion for mockups and diagrams |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `git` | CLI | Yes | Commit the design document to the repository |
| `writing-plans` skill | Skill | Yes | Invoked after approval to generate the implementation plan |
| `elements-of-style:writing-clearly-and-concisely` | Skill | No | Optional — used to improve spec prose quality |
| Visual companion | Tool | No | Browser-based tool for mockups and diagrams (token-intensive) |

---

## Step 1: Environment Setup

Verify required context is available before brainstorming begins.

```bash
# Confirm we are inside a git repository
git rev-parse --show-toplevel || { echo "ERROR: not in a git repo"; exit 1; }

# Ensure results directory exists
mkdir -p /app/results

# Confirm the topic was provided
if [ -z "$TOPIC" ]; then
  echo "ERROR: TOPIC is not set. Pass the idea or feature name."
  exit 1
fi
echo "Setup complete. Topic: $TOPIC"
```

---

## Step 2: Explore Project Context

Before asking any questions, understand the current project state. Read files, docs, and recent commits.

```bash
# Get an overview of the project structure
git log --oneline -10
ls -la
cat README.md 2>/dev/null || echo "No README.md found"
ls docs/ 2>/dev/null || echo "No docs/ directory"
```

Key things to identify:
- Existing patterns, conventions, and technology choices
- Recent work that may be related to the topic
- Any existing specs or prior design documents under `docs/superpowers/specs/`
- Whether the project is large enough to require decomposition

> **Scope check:** If the request describes multiple independent subsystems (e.g., "build a platform with chat, file storage, billing, and analytics"), flag this immediately. Help the user decompose before drilling into details. Each sub-project gets its own spec → plan → implementation cycle.

---

## Step 3: Offer Visual Companion (Conditional)

If the topic will involve visual content (mockups, layouts, diagrams), offer the visual companion — **as its own message, no other content combined**.

```
Some of what we're working on might be easier to explain if I can show it to you
in a web browser. I can put together mockups, diagrams, comparisons, and other
visuals as we go. This feature is still new and can be token-intensive. Want to
try it? (Requires opening a local URL)
```

Wait for the user's response. If they decline, proceed with text-only brainstorming.
If they accept, read `skills/brainstorming/visual-companion.md` before continuing.

Skip this step entirely if the topic is clearly non-visual.

---

## Step 4: Ask Clarifying Questions (max 9 rounds)

Ask questions **one at a time** to understand purpose, constraints, and success criteria. Prefer multiple-choice questions when possible.

Focus areas:
- What problem is this solving? Who benefits?
- What does success look like?
- Are there constraints (performance, security, existing APIs, deadlines)?
- What is explicitly out of scope?

Rules:
- One question per message — if a topic needs more exploration, break it into multiple messages
- Do not overwhelm with lists of questions
- Be flexible: go back and clarify if something doesn't make sense

---

## Step 5: Propose 2–3 Approaches

Present 2–3 different approaches conversationally with trade-offs. Lead with your recommended option and explain why.

Write the approaches to `/app/results/approaches.md`:

```markdown
# Approaches for <topic>

## Approach A: <name> (Recommended)
<description>

**Pros:** ...
**Cons:** ...
**Why recommended:** ...

## Approach B: <name>
<description>

**Pros:** ...
**Cons:** ...

## Approach C: <name> (optional)
<description>

**Pros:** ...
**Cons:** ...
```

After presenting approaches, confirm which direction the user wants to pursue before proceeding.

---

## Step 6: Present Design in Sections

Once you understand what you're building, present the design in sections scaled to their complexity. After **each section**, ask whether it looks right before continuing.

Sections to cover (adapt to project complexity):

1. **Architecture overview** — high-level components and how they relate
2. **Component detail** — each major unit: what it does, how it's used, what it depends on
3. **Data flow** — how data moves through the system
4. **Error handling** — failure modes and recovery strategies
5. **Testing approach** — how the design can be validated

Design principles to apply:
- Break the system into smaller units each with one clear purpose
- Each unit should communicate through well-defined interfaces
- For each unit: what does it do, how do you use it, what does it depend on?
- Can someone understand a unit without reading its internals? Can internals change without breaking consumers?

For existing codebases: explore existing structure first, follow patterns, and include targeted improvements only where they directly serve the current goal.

---

## Step 7: Write Design Document

After the user approves the design, write the spec to the repository.

```bash
SPEC_DATE=$(date -u +%Y-%m-%d)
SPEC_SLUG="<topic-slug>"  # lowercase, hyphens, no spaces
SPEC_PATH="docs/superpowers/specs/${SPEC_DATE}-${SPEC_SLUG}-design.md"

mkdir -p "$(dirname "$SPEC_PATH")"
# Write the approved design to the spec file
cat > "$SPEC_PATH" << 'SPEC_EOF'
# <Topic> Design

## Overview
<summary>

## Architecture
<content>

## Components
<content>

## Data Flow
<content>

## Error Handling
<content>

## Testing Approach
<content>
SPEC_EOF

# Commit the spec
git add "$SPEC_PATH"
git commit -m "Add design spec: ${SPEC_SLUG}"

# Also copy to results
cp "$SPEC_PATH" /app/results/design_doc.md
echo "Design doc committed: $SPEC_PATH"
```

Optionally apply `elements-of-style:writing-clearly-and-concisely` skill to improve prose.

---

## Step 8: Spec Self-Review (max 3 rounds)

After writing the spec, review it with fresh eyes:

1. **Placeholder scan:** Any "TBD", "TODO", incomplete sections, or vague requirements? Fix them inline.
2. **Internal consistency:** Do any sections contradict each other? Does the architecture match feature descriptions?
3. **Scope check:** Is this focused enough for a single implementation plan, or does it need decomposition?
4. **Ambiguity check:** Could any requirement be interpreted two different ways? If so, pick one and make it explicit.

Fix any issues inline. No need for a full re-review — just fix and continue.

If fixes are made, commit the updated spec:

```bash
git add "$SPEC_PATH"
git commit -m "Spec self-review fixes: ${SPEC_SLUG}"
cp "$SPEC_PATH" /app/results/design_doc.md
```

---

## Step 9: User Reviews Written Spec

After the self-review, ask the user to review the written spec before proceeding:

> "Spec written and committed to `<path>`. Please review it and let me know if you want to make any changes before we start writing out the implementation plan."

Wait for the user's response. If they request changes, make them and re-run Step 8. Only proceed once the user explicitly approves.

---

## Step 10: Transition to Implementation

Once the spec is approved, invoke the `writing-plans` skill to generate a detailed implementation plan.

```bash
echo "Design approved. Invoking writing-plans skill."
# Invoke: writing-plans skill
```

> **Important:** Do NOT invoke `frontend-design`, `mcp-builder`, or any other implementation skill. The **only** skill invoked after brainstorming is `writing-plans`.

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/design_doc.md" \
  "$RESULTS_DIR/approaches.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# Verify design doc is committed
if git log --oneline | grep -q "design spec"; then
  echo "PASS: Design spec committed to git"
else
  echo "FAIL: Design spec not found in git log"
fi

echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] Project context explored (files, docs, recent commits reviewed)
- [ ] Visual companion offered if topic involved visual content
- [ ] Clarifying questions asked one at a time
- [ ] 2–3 approaches proposed with trade-offs and recommendation
- [ ] Design presented in sections with user approval after each
- [ ] Design doc written to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` and committed
- [ ] Spec self-review completed (no TBD/TODO/contradictions/ambiguity remaining)
- [ ] User approved the written spec
- [ ] `writing-plans` skill invoked (and no other implementation skill)
- [ ] `/app/results/design_doc.md` exists and is non-empty
- [ ] `/app/results/approaches.md` exists and is non-empty
- [ ] `/app/results/summary.md` exists and is non-empty
- [ ] `/app/results/validation_report.json` exists with `overall_passed`

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **One question at a time.** Never combine questions into a list — it overwhelms the user and produces worse answers. If a topic needs several questions, ask them sequentially.
- **YAGNI ruthlessly.** Remove unnecessary features from all designs. Simple, well-bounded units are easier to build, test, and understand.
- **Lead with your recommendation.** When proposing approaches, don't present them as equally weighted — have a view and explain it clearly.
- **Scale sections to complexity.** A truly simple project needs only a few sentences per section, not 300 words. Match depth to the actual complexity.
- **The hard gate is real.** Even a "quick config change" benefits from a 2-sentence design presentation. The habit of pausing before implementing saves far more time than it costs.
- **Only writing-plans comes next.** After approval, invoke `writing-plans` and nothing else. Other skills (frontend-design, mcp-builder, etc.) are never the right next step from brainstorming.
- **Visual companion is a tool, not a mode.** Accepting it doesn't mean every message goes through the browser. Decide per question: would the user understand this better by seeing it or reading it?
