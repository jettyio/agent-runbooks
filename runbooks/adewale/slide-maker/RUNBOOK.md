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

Generate presentation decks grounded in real GitHub projects, or walk through a structured brief-to-slides process. This skill supports creating and updating native Slidev deck projects — complete with a compiled `slides.md`, a `deck.spec.md` specification, a printable `deck.pdf`, and a project `README.md`. Use when the user asks to create a presentation, slide deck, talk, pitch, keynote, or Slidev project — especially when they want slides based on an existing codebase, architecture, or project documentation. The workflow spans eight phases: determine mode, gather sources, intake narrative principles, choose style, write the spec, compile slides, validate quality, and deliver the finished deck.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`. The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/deck.spec.md` | The slide deck specification (always required) |
| `/app/results/slides.md` | The compiled Slidev slides (always required) |
| `/app/results/deck.pdf` | The compiled deck exported to PDF via `slidev export` (always required) |
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
| Style preset | `auto` | Visual style preset — pass a slug from the **Style Preset Catalog** in Step 5 (e.g. `bold-signal`, `vintage-editorial`, `terminal-green`). `auto` lets the agent pick one by mood. |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `Node.js` / `npm` | Runtime | Yes | Required to run Slidev |
| `@slidev/cli` | npm package | Yes | Slidev CLI for compiling and previewing decks |
| `playwright-chromium` | npm package | Yes | Headless Chromium that `slidev export` drives to render `deck.pdf` |
| GitHub API / `gh` | External API | Optional | Clone source repos when building project decks |

This runbook is **self-contained** — slide kinds, the deck-spec schema, Slidev
syntax, compiler rules, and validation checklists are all inline in the steps
that use them. There are no external reference files to fetch.

## Step 1: Environment Setup

Verify the environment and install required dependencies.

```bash
# Check Node.js and npm
command -v node >/dev/null || { echo "ERROR: Node.js not installed"; exit 1; }
command -v npm  >/dev/null || { echo "ERROR: npm not installed"; exit 1; }

# Install Slidev CLI if not present
npm list -g @slidev/cli 2>/dev/null || npm install -g @slidev/cli

# Install the headless Chromium that `slidev export` uses to render the PDF
npm list -g playwright-chromium 2>/dev/null || npm install -g playwright-chromium

# Create output directory
mkdir -p /app/results/styles

# Verify required inputs are provided
if [ -z "$GOAL" ]; then
  echo "ERROR: GOAL (goal or update instructions) is not set"
  exit 1
fi
echo "Environment setup complete. Mode: ${MODE:-create}"
```

The work proceeds in eight phases. Every reference each phase needs is inline in
the step shown below — read it when you reach that step rather than loading it
all upfront.

| Phase | Covered by | Purpose |
|-------|-----------|---------|
| 1. Determine mode | Step 2 | Create vs. update |
| 2. Gather sources | Step 3 | Source-material lookup, extraction heuristics, through-line, project identity |
| 3. Intake | Step 4 (Presentation principles + Narrative arcs) | Rhetorical principles, narrative structure, through-line design |
| 4. Style direction | Step 5 (Style Preset Catalog) | Visual presets and token palettes |
| 5. Write spec | Step 6 (Deck-spec schema + Slide Kinds catalog) | Spec schema and slide type catalog |
| 6. Compile | Step 7 (Slidev reference + Compiler rules) | Compilation rules, Slidev features |
| 7. Validate | Step 9 (Acceptance checklist + LLM tells) | Quality gates |
| 8. Deliver | Steps 10–11 | Export the deck to PDF, then write final deliverables |

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

For **project decks** (user provided a GitHub repo or codebase):
- Clone or fetch the repository
- Extract: project name, tagline, key architecture, noteworthy features, open issues, recent releases
- Identify a **through-line**: the single most important idea or narrative arc for this audience
- Capture project identity signals for use in style direction

For **brief-driven decks** (no repo):
- Collect from the user: topic, audience, key message, desired slide count, and any existing material

**Extraction heuristics**

- Prefer primary sources in this order: `README` → architecture/design docs → code comments and module layout → recent commits/releases → open issues.
- For every claim you intend to put on a slide, note the exact source (file, commit, README section, or issue number). Anything you can't trace is a candidate to cut, not to assert.
- If the user supplied images/screenshots, inspect each one, mark it USABLE or NOT USABLE (with a reason), and let the usable set co-design the outline — e.g. 3 product screenshots naturally imply 3 feature slides.
- Capture identity signals for Step 5: dominant brand colors, logo, tone (playful vs. enterprise), and the audience's technical depth.

## Step 4: Intake — Narrative Principles

Shape the deck's arc before writing any slide:
- Establish a clear through-line (one sentence that captures the deck's core argument)
- Map a narrative structure (see **Narrative arcs** below)
- Identify the audience and calibrate complexity accordingly

**Presentation principles**

- **One idea per slide.** If a slide argues two things, split it. Large type, strong hierarchy, generous whitespace beat dense walls of text.
- **Show, don't tell.** Prefer a diagram, a real metric, a screenshot, or a code excerpt over an abstract bullet describing it.
- **Earn every claim.** Each factual statement should trace to a source from Step 3. Cut what you can't ground.
- **Distinctive over generic.** Avoid "AI slop" — predictable layouts, purple-on-white gradients, and default system fonts. Commit to one cohesive aesthetic (set in Step 5) with dominant colors and sharp accents.
- **Calibrate density to delivery.** Speaker-led decks: 1–3 bullets/slide, lots of section beats and statement slides. Read-first decks (sent async): denser, self-contained slides with 4–6 bullets or cards.

**Narrative arcs** — pick the one that fits the goal:

| Arc | Shape | Good for |
|-----|-------|----------|
| Problem → Insight → Solution → Proof → CTA | Classic persuasive build | Pitch decks, launches |
| Context → Tension → Resolution | Story spine | Talks, keynotes |
| What → Why it matters → How → What's next | Explainer | Teaching, internal updates |
| Status quo → What changed → Implications | Before/after | Roadmaps, retros |

Restate the through-line on the cover and call back to it on the closing slide.

## Step 5: Style Direction

> The full preset catalog is **inline below** — no external `STYLE_PRESETS.md` is required.

Select or confirm a visual style preset:

- If the user passed a **Style preset** slug, apply that preset exactly.
- If the value is `auto` (the default), pick a preset using the **Pick by mood** map below, then state in `summary.md` which preset you chose and why.

Each preset defines a font pairing and a color palette. When you need to deviate from a preset's tokens (brand colors, a custom typeface), write the overrides to `/app/results/styles/tokens.css`.

### Style Preset Catalog

Pass the **slug** (first column) as the `Style preset` parameter. The default recommendation is **Bold Signal** — a versatile dark theme with strong visual hierarchy.

| Slug | Preset | Theme | Vibe | Fonts (display / body) | Key colors |
|------|--------|-------|------|------------------------|------------|
| `bold-signal` | Bold Signal | Dark | Confident, bold, high-impact (default) | Archivo Black / Space Grotesk | bg `#1a1a1a` · accent `#FF5722` · text `#ffffff` |
| `electric-studio` | Electric Studio | Dark | Clean, professional, high-contrast | Manrope / Manrope | bg `#0a0a0a` · accent `#4361ee` · text `#ffffff` |
| `creative-voltage` | Creative Voltage | Dark | Creative, energetic, retro-modern | Syne / Space Mono | bg `#1a1a2e` · primary `#0066ff` · neon `#d4ff00` |
| `dark-botanical` | Dark Botanical | Dark | Elegant, sophisticated, premium | Cormorant / IBM Plex Sans | bg `#0f0f0f` · text `#e8e4df` · accent `#d4a574` |
| `notebook-tabs` | Notebook Tabs | Light | Editorial, organized, tactile | Bodoni Moda / DM Sans | card `#f8f6f1` · tabs `#98d4bb`→`#ffe6a7` · text `#2d2d2d` |
| `pastel-geometry` | Pastel Geometry | Light | Friendly, modern, approachable | Plus Jakarta Sans | bg `#c8d9e6` · card `#faf9f7` · pills `#f0b4d4`→`#7c6aad` |
| `split-pastel` | Split Pastel | Light | Playful, friendly, creative | Outfit | peach `#f5e6dc` · lavender `#e4dff0` · text `#1a1a1a` |
| `vintage-editorial` | Vintage Editorial | Light | Witty, editorial, personality-driven | Fraunces / Work Sans | cream `#f5f3ee` · text `#1a1a1a` · accent `#e8d4c0` |
| `neon-cyber` | Neon Cyber | Dark | Futuristic, high-energy | Space Grotesk / IBM Plex Mono | navy `#0a0f1c` · cyan + magenta neon |
| `terminal-green` | Terminal Green | Dark | Developer / technical | IBM Plex Mono | bg `#0d1117` · terminal green `#39d353` |
| `swiss-modern` | Swiss Modern | Light | Bauhaus, minimal, grid-driven | Helvetica Neue / Inter | black + white · red `#ff3300` |
| `paper-and-ink` | Paper & Ink | Light | Literary, calm, editorial | Spectral / Inter | cream `#faf9f7` · charcoal · crimson `#c41e3a` |

### Pick by mood

When `Style preset` is `auto`, choose by the feeling the audience should leave with:

- **Impressed / confident** → Bold Signal, Electric Studio, Dark Botanical
- **Excited / energized** → Creative Voltage, Neon Cyber, Split Pastel
- **Calm / focused** → Notebook Tabs, Paper & Ink, Swiss Modern
- **Inspired / moved** → Dark Botanical, Vintage Editorial, Pastel Geometry
- **Technical / developer** → Terminal Green, Electric Studio

When in doubt, use **Bold Signal**.

## Step 6: Write or Revise `deck.spec.md`

Write the slide deck specification to `/app/results/deck.spec.md`. The spec is the
contract for Step 7 — compile only what the spec describes.

**Deck-spec schema.** The spec must include:
- **Through-line** — one sentence.
- **Meta** — selected style preset (slug from Step 5), target slide count/range, density mode (speaker-led or read-first), audience.
- **Slide list** — one entry per slide with:
  - `number` — sequential slide number
  - `kind` — from the **Slide Kinds catalog** below
  - `headline` — the slide's single claim, written out
  - `notes` — a 1–3 line speaker-notes outline
  - `sources` — file / commit / README section / issue backing each factual claim (project decks)

### Slide Kinds catalog

Each kind maps to a Slidev built-in layout (used in Step 7). Use `content` when nothing else fits.

| Kind | Slidev `layout:` | Use for |
|------|------------------|---------|
| `cover` | `cover` | Opening slide — deck title + through-line |
| `intro` | `intro` | Title + author/context |
| `section` | `section` | Marks the start of a new section |
| `content` | `default` | General point with a headline + 1–6 bullets |
| `two-column` | `two-cols` | Side-by-side compare / text + visual |
| `two-column-header` | `two-cols-header` | Shared header over two columns |
| `image` | `image`, `image-left`, `image-right` | A screenshot/diagram as the focus |
| `quote` | `quote` | A pulled quotation with prominence |
| `statement` | `statement` | A single bold assertion |
| `fact` | `fact` | One big metric/number with prominence |
| `code` | `default` (fenced code block) | A code excerpt or config |
| `full` | `full` | Edge-to-edge visual / diagram |
| `closing` | `end` | Recap of the through-line + call to action |

For **update** mode: apply only the changes indicated in the goal; preserve unchanged slides.

Validation gate — do not proceed to Step 7 until:
- [ ] Through-line is one sentence, present in the spec
- [ ] Every slide has a kind (from the catalog) and a headline
- [ ] Slide count is within the agreed range

## Step 7: Compile the Deck

Compile `/app/results/slides.md` from the approved spec. **Do NOT add content not in the approved spec.**

### Slidev reference

A Slidev deck is a single Markdown file. Slides are separated by a line containing only `---`. Per-slide options go in a YAML frontmatter block immediately after the separator.

- **Headmatter** (the very first frontmatter block) sets deck-wide config:
  ```yaml
  ---
  theme: default
  title: <deck title>
  transition: slide-left
  ---
  ```
- **Per-slide frontmatter** sets the layout and slide options:
  ```yaml
  ---
  layout: two-cols
  class: text-center
  background: /images/cover.png
  ---
  ```
- **Common layouts** (map slide kinds → these): `cover`, `intro`, `section`, `default`, `two-cols`, `two-cols-header`, `image-left`, `image-right`, `image`, `quote`, `statement`, `fact`, `full`, `center`, `end`.
- **Two-column** content uses a `::right::` slot divider between the left and right columns (`::left::`/`::right::` for `two-cols-header`).
- **Speaker notes** are an HTML comment at the end of a slide: `<!-- notes here -->`.
- **Code** uses fenced blocks with a language; line highlighting via `{2,4-6}` after the language.
- **Styling**: apply preset token overrides from `styles/tokens.css`; per-slide tweaks via the `class:` key + UnoCSS utilities.

### Compiler rules

- Start `slides.md` with the headmatter block, then emit slides in spec order.
- One spec slide → one Slidev slide. Use the `layout:` mapped from each slide's `kind`.
- **Split, don't shrink.** If a slide's content exceeds its density budget, break it into two slides rather than cramming or reducing font size. If a change causes overflow, split automatically and note it in `summary.md`.
- Keep every factual claim traceable to the `sources` recorded in the spec.
- Put the speaker-notes outline into each slide's `<!-- ... -->` notes comment.

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
   | Unknown slide kind | Use the closest kind from the Slide Kinds catalog (Step 6) or `content` |
   | Slidev syntax error | Consult the Slidev reference (Step 7) for correct syntax |
   | Slide count out of range | Merge or split slides to hit the target range |
   | Token CSS syntax error | Validate CSS syntax; check `styles/tokens.css` |

3. Re-run the failed step and overwrite the output
4. Repeat up to 3 times total

After 3 rounds, if compilation still fails, write the failure into `summary.md` and set `overall_passed=false` in `validation_report.json`.

## Step 9: Validate

Run the acceptance checklist below, then scan every slide and speaker note for the **LLM tells** listed underneath.

**Acceptance checklist**

| Gate | Criterion |
|------|-----------|
| Spec completeness | All slides have kind + headline + notes outline |
| Through-line | Visible in cover slide and callback in closing slide |
| Source grounding | Every factual claim traceable to a source reference |
| Density | No slide exceeds its density budget; overflow was split, not shrunk |
| No internal leakage | No slide text exposes runbook/spec internals — kind names, `layout:` values, preset slugs, file paths, "Option A/B", or the raw goal text |
| No LLM tells | Zero instances from the list below |
| Compilation | `slidev build` exits 0 |
| Output files | All required outputs exist and are non-empty |

**LLM tells** — find and rewrite any of these:

- Filler openers/closers: "In conclusion", "In today's fast-paced world", "It's worth noting that", "At the end of the day", "Let's dive in", "Delve into".
- Hollow intensifiers and hedges: "very", "really", "truly", "seamless", "robust", "powerful", "cutting-edge", "game-changing", "revolutionary", "leverage", "utilize" (use "use").
- Unsupported superlatives ("the best", "the most advanced") with no source behind them.
- Generic transitions ("Moving on", "Next up", "Now let's talk about") and empty agenda restatements.
- Symmetry tics: every slide having exactly three bullets, or three-item lists everywhere regardless of content.
- Design slop flagged in Step 4: default system fonts, purple-on-white gradients, cookie-cutter card grids.

## Step 10: Export to PDF

Print the validated deck to PDF with Slidev's built-in exporter. Run this **after** Step 9 passes so the PDF reflects the final slides.

```bash
cd /app/results

# slidev export renders each slide through headless Chromium → deck.pdf
slidev export slides.md --output deck.pdf --timeout 60000 2>&1 | tail -20

# Confirm a non-empty PDF was produced
if [ -s /app/results/deck.pdf ]; then
  echo "PASS: deck.pdf ($(wc -c < /app/results/deck.pdf) bytes)"
else
  echo "FAIL: deck.pdf was not produced"
fi
```

- One page per slide by default. To bake click-through animations into extra pages, add `--with-clicks`.
- If export fails because Chromium is missing, run `npm install -g playwright-chromium` (Step 1 already does this) and retry once.
- If the PDF still can't be produced after one retry, record the failure in `summary.md`, set `overall_passed=false` in `validation_report.json`, and continue — never silently skip it.

## Step 11: Deliver

Write the final deliverables to `/app/results/`:
- `deck.spec.md` — approved spec
- `slides.md` — compiled Slidev slides
- `deck.pdf` — the deck exported to PDF
- `README.md` — project README with deck title, through-line, how to run, slide count, preset used
- `styles/tokens.css` — token overrides (if applicable)

## Step 12: Write Validation Report

Write `/app/results/validation_report.json` reflecting all stage outcomes, including the PDF export result.

## Step 13: Write Executive Summary

Write `/app/results/summary.md` with run metadata, mode detected, through-line, slide count, preset used, validation results, and any issues.

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/deck.spec.md" \
  "$RESULTS_DIR/slides.md" \
  "$RESULTS_DIR/deck.pdf" \
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
- [ ] `deck.pdf` was exported via `slidev export` and is non-empty
- [ ] `README.md` contains deck title, through-line, and run instructions
- [ ] `styles/tokens.css` written if visual overrides were needed
- [ ] `summary.md` documents mode, through-line, slide count, preset, and any issues
- [ ] `validation_report.json` has `stages`, `results`, and `overall_passed`
- [ ] All quality gates in Step 9 passed
- [ ] Verification script printed PASS for every required file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Read each step when you reach it.** This runbook is self-contained — the catalogs and references (style presets, slide kinds, Slidev syntax, validation) live in the step that uses them. Don't try to fetch external docs; there are none.
- **Through-line first.** Before writing a single slide, nail the through-line. Every slide decision flows from it.
- **Spec before compile.** Never start `slides.md` without an approved `deck.spec.md`. The spec is the contract.
- **Grounding over generality.** For project decks, every factual claim should trace back to a specific file, commit, README section, or issue in the source repo. Avoid generic statements.
- **LLM tells are silent failures.** Run the LLM-tells scan in Step 9 before delivery. Phrases like "In conclusion", "Delve into", or unsupported superlatives undermine credibility.
- **`slidev build` is the ground truth.** If the build fails, the deck is not done, regardless of how good `slides.md` looks in a text editor.
