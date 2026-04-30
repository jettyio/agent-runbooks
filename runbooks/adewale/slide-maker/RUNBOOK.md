---
version: 1.0.0
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: https://skills.sh/adewale/slide-maker/slide-maker
  source_host: skills.sh
  source_title: slide-maker
  imported_at: '2026-04-30T03:56:55Z'
  imported_by: skill-to-runbook-converter@1.0.0
  attribution:
    collection_or_org: adewale
    skill_name: slide-maker
    confidence: high
---

# slide-maker — Agent Runbook

## Objective

Generate presentation decks grounded in real GitHub projects, or walk through a structured brief-to-slides process. This skill supports creating and updating native Slidev deck projects — complete with a compiled `slides.md`, a `deck.spec.md` specification, and a project `README.md`. Use when the user asks to create a presentation, slide deck, talk, pitch, keynote, or Slidev project — especially when they want slides based on an existing codebase, architecture, or project documentation. The workflow spans eight phases: determine mode, gather sources, intake narrative principles, choose style, write the spec, compile slides, validate quality, and deliver the finished deck.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`. The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/deck.spec.md` | The slide deck specification (always required) |
| `/app/results/slides.md` | The compiled Slidev slides (always required) |
| `/app/results/README.md` | Project README for the deck (always required) |
| `/app/results/styles/tokens.css` | CSS token overrides (when visual customization is needed) |
| `/app/results/summary.md` | Executive summary with run metadata, mode, and any issues |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Goal or update instructions | *(required)* | What to create or update — e.g. "pitch deck for ProjectX from its GitHub repo" |
| Mode | `create` | `create` or `update` a Slidev deck project |
| Source repo URL | *(optional)* | GitHub repository URL to base a project deck on |
| Style preset | `default` | Visual style preset (see STYLE_PRESETS.md for options) |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `Node.js` / `npm` | Runtime | Yes | Required to run Slidev |
| `@slidev/cli` | npm package | Yes | Slidev CLI for compiling and previewing decks |
| GitHub API / `gh` | External API | Optional | Clone source repos when building project decks |
| `STYLE_PRESETS.md` | Reference doc | Phase 4 only | Visual presets and token palettes |
| `DECK_SPEC.md` | Reference doc | Phase 5 only | Spec schema |
| `SLIDE_KINDS.md` | Reference doc | Phase 5 only | Slide type catalog |
| `COMPILER_RULES.md` | Reference doc | Phase 6 only | Compilation rules |
| `SLIDEV_REFERENCE.md` | Reference doc | Phase 6 only | Slidev features reference |
| `PRESENTATION_PHILOSOPHY.md` | Reference doc | Phase 3 only | Rhetorical principles |
| `STORYTELLING.md` | Reference doc | Phase 3 only | Narrative structure |

## Step 1: Environment Setup

Verify the environment and install required dependencies.

```bash
# Check Node.js and npm
command -v node >/dev/null || { echo "ERROR: Node.js not installed"; exit 1; }
command -v npm  >/dev/null || { echo "ERROR: npm not installed"; exit 1; }

# Install Slidev CLI if not present
npm list -g @slidev/cli 2>/dev/null || npm install -g @slidev/cli

# Create output directory
mkdir -p /app/results/styles

# Verify required inputs are provided
if [ -z "$GOAL" ]; then
  echo "ERROR: GOAL (goal or update instructions) is not set"
  exit 1
fi
echo "Environment setup complete. Mode: ${MODE:-create}"
```

Load reference documents **only when entering the relevant phase**. Do not load all files upfront.

| Phase | Load these files | Purpose |
|-------|-----------------|---------|
| 1. Determine mode | (none) | — |
| 2. Gather sources | `SOURCES.md` (project decks only) | Source-material lookup, extraction heuristics, through-line, project identity |
| 3. Intake | `PRESENTATION_PHILOSOPHY.md`, `STORYTELLING.md` | Rhetorical principles, narrative structure, through-line design |
| 4. Style direction | `STYLE_PRESETS.md` | Visual presets and token palettes |
| 5. Write spec | `DECK_SPEC.md`, `SLIDE_KINDS.md` | Spec schema and slide type catalog |
| 6. Compile | `COMPILER_RULES.md`, `SLIDEV_REFERENCE.md` | Compilation phases, Slidev features |
| 7. Validate | `ACCEPTANCE_CHECKLIST.md`, `LLM_TELLS.md` | Quality gates |
| 8. Deliver | (none) | — |

## Step 2: Determine Mode

Identify whether this is a **create** or **update** run.

- **Create**: No existing `slides.md` — start from scratch.
- **Update**: An existing `slides.md` is present — apply targeted changes from the goal.

```bash
if [ -f "/app/results/slides.md" ]; then
  MODE="update"
else
  MODE="create"
fi
echo "Mode detected: $MODE"
```

Unsupported: standalone HTML, PPTX, HTML-to-Slidev, non-project artifacts. If the goal implies these, redirect to a Slidev deck project and explain why.

## Step 3: Gather Source Material (project decks only)

> Load `SOURCES.md` at this phase (project decks only).

For **project decks** (user provided a GitHub repo or codebase):
- Clone or fetch the repository
- Extract: project name, tagline, key architecture, noteworthy features, open issues, recent releases
- Identify a **through-line**: the single most important idea or narrative arc for this audience
- Capture project identity signals for use in style direction

For **brief-driven decks** (no repo):
- Collect from the user: topic, audience, key message, desired slide count, and any existing material

## Step 4: Intake — Narrative Principles

> Load `PRESENTATION_PHILOSOPHY.md` and `STORYTELLING.md` at this phase.

Apply rhetorical and narrative principles to shape the deck's arc:
- Establish a clear through-line (one sentence that captures the deck's core argument)
- Map a narrative structure (e.g. problem to insight to solution to proof to call to action)
- Identify the audience and calibrate complexity accordingly

## Step 5: Style Direction

> Load `STYLE_PRESETS.md` at this phase.

Select or confirm a visual style preset. If the user specified one, apply it. Otherwise, suggest a preset based on the project identity and audience.

If token overrides are needed, prepare `styles/tokens.css`.

## Step 6: Write or Revise `deck.spec.md`

> Load `DECK_SPEC.md` and `SLIDE_KINDS.md` at this phase.

Write the slide deck specification to `/app/results/deck.spec.md`. The spec must include:
- Through-line (one sentence)
- Slide list with: slide number, kind (from SLIDE_KINDS.md), headline, speaker notes outline
- Visual preset selected
- Key source references for each slide

For **update** mode: apply only the changes indicated in the goal; preserve unchanged slides.

Validation gate — do not proceed to Step 7 until:
- [ ] Through-line is one sentence, present in the spec
- [ ] Every slide has a kind and a headline
- [ ] Slide count is within the agreed range

## Step 7: Compile the Deck

> Load `COMPILER_RULES.md` and `SLIDEV_REFERENCE.md` at this phase.

Compile `/app/results/slides.md` from the approved spec. Follow all compiler rules:
- Apply the Slidev frontmatter block at the top of `slides.md`
- Use Slidev layout directives (`layout: cover`, `layout: two-cols`, etc.) as specified
- Apply token overrides from `styles/tokens.css` if present
- Do NOT add content not in the approved spec

```bash
# Verify the deck compiles without errors
cd /app/results && slidev build --out dist/ 2>&1 | tail -20
```

Compilation must exit 0. If it fails, fix compiler errors before proceeding (max 3 rounds).

## Step 8: Iterate on Errors (max 3 rounds)

If Step 6 validation or Step 7 compilation fails:

1. Read the specific failure message
2. Apply the targeted fix:

   | Issue | Fix |
   |-------|-----|
   | Through-line missing or multi-sentence | Rewrite to a single clear sentence |
   | Unknown slide kind | Use the closest kind from `SLIDE_KINDS.md` or `content` |
   | Slidev syntax error | Consult `SLIDEV_REFERENCE.md` for correct syntax |
   | Slide count out of range | Merge or split slides to hit the target range |
   | Token CSS syntax error | Validate CSS syntax; check `styles/tokens.css` |

3. Re-run the failed step and overwrite the output
4. Repeat up to 3 times total

After 3 rounds, if compilation still fails, write the failure into `summary.md` and set `overall_passed=false` in `validation_report.json`.

## Step 9: Validate

> Load `ACCEPTANCE_CHECKLIST.md` and `LLM_TELLS.md` at this phase.

Run through the acceptance checklist. Flag any LLM tells (filler phrases, unsupported claims, generic transitions).

| Gate | Criterion |
|------|-----------|
| Spec completeness | All slides have kind + headline + notes outline |
| Through-line | Visible in cover slide and callback in closing slide |
| Source grounding | Every factual claim traceable to a source reference |
| No LLM tells | Zero instances flagged by `LLM_TELLS.md` |
| Compilation | `slidev build` exits 0 |
| Output files | All required outputs exist and are non-empty |

## Step 10: Deliver

Write the final deliverables to `/app/results/`:
- `deck.spec.md` — approved spec
- `slides.md` — compiled Slidev slides
- `README.md` — project README with deck title, through-line, how to run, slide count, preset used
- `styles/tokens.css` — token overrides (if applicable)

## Step 11: Write Validation Report

Write `/app/results/validation_report.json` reflecting all stage outcomes.

## Step 12: Write Executive Summary

Write `/app/results/summary.md` with run metadata, mode detected, through-line, slide count, preset used, validation results, and any issues.

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/deck.spec.md" \
  "$RESULTS_DIR/slides.md" \
  "$RESULTS_DIR/README.md" \
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

- [ ] `deck.spec.md` exists with through-line and full slide list
- [ ] `slides.md` compiles without errors via `slidev build`
- [ ] `README.md` contains deck title, through-line, and run instructions
- [ ] `styles/tokens.css` written if visual overrides were needed
- [ ] `summary.md` documents mode, through-line, slide count, preset, and any issues
- [ ] `validation_report.json` has `stages`, `results`, and `overall_passed`
- [ ] All quality gates in Step 9 passed
- [ ] Verification script printed PASS for every required file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Load documents progressively.** Each reference doc is large — load only the ones relevant to the current phase. Loading them all upfront wastes context and may confuse earlier phases.
- **Through-line first.** Before writing a single slide, nail the through-line. Every slide decision flows from it.
- **Spec before compile.** Never start `slides.md` without an approved `deck.spec.md`. The spec is the contract.
- **Grounding over generality.** For project decks, every factual claim should trace back to a specific file, commit, README section, or issue in the source repo. Avoid generic statements.
- **LLM tells are silent failures.** Run `LLM_TELLS.md` checks before delivery. Phrases like "In conclusion", "Delve into", or unsupported superlatives undermine credibility.
- **`slidev build` is the ground truth.** If the build fails, the deck is not done, regardless of how good `slides.md` looks in a text editor.
