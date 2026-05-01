---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/anthropics/skills/frontend-design"
  source_host: "skills.sh"
  source_title: "frontend-design"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "anthropics"
    skill_name: "frontend-design"
    confidence: "high"
secrets: {}
---

# frontend-design — Agent Runbook

## Objective

Create distinctive, production-grade frontend interfaces with high design quality. This runbook guides an AI agent through building web components, pages, artifacts, posters, or applications — including websites, landing pages, dashboards, React components, and HTML/CSS layouts — while avoiding the generic "AI slop" aesthetics that plague cookie-cutter designs. The agent must commit to a bold, intentional aesthetic direction before writing a single line of code, then implement working, meticulously refined production code that is visually striking and cohesive. The expected output is functional frontend code (HTML/CSS/JS, React, Vue, or similar) that demonstrates extraordinary creative vision matched to the user's requirements.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/frontend_output/index.html` (or equivalent) | The generated frontend artifact (HTML/CSS/JS, React component, etc.) as requested by the user |
| `/app/results/design_rationale.md` | Written explanation of the aesthetic direction chosen: tone, typography, color scheme, motion strategy, and differentiation factor |
| `/app/results/summary.md` | Executive summary with run metadata, design decisions, and any issues encountered |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

## Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| User requirements | *(provided at runtime)* | Frontend requirements: component, page, application, or interface to build. May include context about purpose, audience, or technical constraints |
| Framework preference | *(optional, from user)* | Preferred frontend framework (HTML/CSS/JS, React, Vue, etc.) — defaults to HTML/CSS/JS if not specified |
| Aesthetic constraint | *(optional, from user)* | Any specific aesthetic constraints or brand guidelines to follow |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| Browser or renderer | Runtime | Yes | To preview and validate the generated frontend output |
| Node.js / npm | CLI | Conditional | Required if the user specifies a React or Vue output that needs a build step |
| A modern font CDN | External | Recommended | Google Fonts, Adobe Fonts, or Bunny Fonts for distinctive typography choices |

## Step 1: Environment Setup

Verify prerequisites and prepare the output directory.

```bash
mkdir -p /app/results/frontend_output

# Confirm the user has provided frontend requirements
if [ -z "$FRONTEND_REQUIREMENTS" ]; then
  echo "WARNING: No explicit FRONTEND_REQUIREMENTS env var set — proceeding with task description."
fi

echo "Output directory ready: /app/results/frontend_output"
```

Confirm:
- The user's requirements are clear (component, page, or application to build)
- Any technical constraints (framework, performance, accessibility targets) are noted
- Any brand guidelines or aesthetic preferences are captured

If requirements are ambiguous, document your interpretation in `design_rationale.md` before proceeding.

## Step 2: Design Thinking — Aesthetic Direction

Before writing any code, commit to a clear aesthetic direction. This is the most critical step. Document your choices in `/app/results/design_rationale.md`.

### 2a. Understand the Context

Answer these questions explicitly:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: What is the emotional register? (Choose one extreme and commit to it fully.)
- **Constraints**: What technical requirements apply (framework, performance, accessibility)?
- **Differentiation**: What is the single most memorable thing about this design?

### 2b. Choose a Bold Aesthetic Direction

Pick ONE direction and execute it with full intentionality. Examples of valid directions:

| Direction | Characteristics |
|-----------|-----------------|
| Brutalist/raw | High contrast, raw structure, no decoration, bold typography |
| Maximalist chaos | Overlapping elements, dense information, rich texture, multiple typefaces |
| Retro-futuristic | Sci-fi references, CRT effects, terminal aesthetics, neon accents |
| Organic/natural | Earthy palette, irregular shapes, hand-drawn textures, warm typography |
| Luxury/refined | Generous whitespace, serif typography, gold/neutral accents, restraint |
| Playful/toy-like | Saturated colors, rounded forms, bouncy animations, friendly typography |
| Editorial/magazine | Strong grid, pull quotes, mixed type sizes, journalistic flow |
| Art deco/geometric | Symmetry, gold/black/ivory palette, ornamental details, geometric type |
| Soft/pastel | Muted tones, gentle gradients, light serif fonts, subtle shadows |
| Industrial/utilitarian | Monospace fonts, grid systems, functional color coding, technical precision |

**CRITICAL**: Bold maximalism and refined minimalism both work — the key is intentionality, not intensity. Never default to "clean and modern" with no further direction.

### 2c. Validate Design Choices Against Anti-Patterns

Before coding, explicitly confirm you are NOT using:
- [ ] Overused fonts: Inter, Roboto, Arial, system-ui, Space Grotesk
- [ ] Clichéd color schemes: purple gradients on white backgrounds, generic blue-on-white
- [ ] Predictable layouts: centered hero + card grid + footer
- [ ] Cookie-cutter components: Bootstrap-style buttons, generic modals

Write your completed aesthetic direction to `/app/results/design_rationale.md` before proceeding to Step 3.

## Step 3: Implement the Frontend

Generate working, production-grade code that executes your chosen aesthetic direction precisely.

### 3a. Typography

```
RULE: Choose fonts that are beautiful, unique, and interesting.
- Select a distinctive display font for headings
- Pair it with a refined, readable body font
- Load via CDN (Google Fonts, Bunny Fonts, or system fonts used deliberately)
- NEVER use Inter, Roboto, Arial as the primary display font
```

### 3b. Color & Theme

```
RULE: Commit to a cohesive, dominant palette.
- Define all colors as CSS custom properties (variables)
- Pick 1-2 dominant colors and 1-2 sharp accent colors
- Avoid timid, evenly-distributed multi-color palettes
- Dark themes and light themes are both valid — commit to one
```

### 3c. Motion

```
RULE: Use animations purposefully and memorably.
- For HTML/CSS output: CSS-only animations (no JS dependency required)
- For React output: Motion library preferred when available
- Orchestrate one high-impact page-load sequence (staggered reveals with animation-delay)
- Add scroll-triggered effects and hover states that surprise
- Match animation complexity to aesthetic intensity (maximalist = elaborate, minimalist = subtle)
```

### 3d. Spatial Composition

```
RULE: Break predictable layouts.
- Introduce asymmetry, overlap, diagonal flow, or grid-breaking elements
- Use generous negative space OR deliberate density — no in-between
- Avoid standard hero/cards/footer templates
```

### 3e. Backgrounds & Visual Details

```
RULE: Create atmosphere, not just structure.
- NEVER default to solid white or solid black backgrounds
- Apply at least ONE atmospheric technique:
  gradient mesh / noise texture / geometric pattern /
  layered transparencies / dramatic shadows / decorative borders /
  custom cursor / grain overlay
- Match the technique to the aesthetic direction chosen in Step 2
```

### 3f. Write the Code

Write complete, functional code to `/app/results/frontend_output/`. The output must:
- Be immediately runnable (open in browser, or buildable with documented commands)
- Include all assets inline or via CDN (no broken local file references)
- Be production-grade: no placeholder text like "Lorem ipsum" unless intentionally stylistic
- Match the aesthetic direction committed to in Step 2 with precision

## Step 4: Iterate on Design Quality (max 3 rounds)

After generating the initial output, evaluate it against the design quality checklist. If any check fails, refine the code and re-evaluate. Repeat up to 3 rounds.

### Quality Checklist

| Check | Criteria | Status |
|-------|----------|--------|
| Anti-pattern avoidance | None of the forbidden fonts/colors/layouts are used | pending |
| Aesthetic commitment | A clear aesthetic direction is executed consistently throughout | pending |
| Typography distinctiveness | Font choice is visually memorable and contextually appropriate | pending |
| Color coherence | Palette is dominant, not timid; CSS variables are used | pending |
| Motion quality | At least one high-impact animation is present and purposeful | pending |
| Layout originality | Layout breaks predictable patterns | pending |
| Atmospheric depth | Background and visual details create depth and character | pending |
| Code completeness | All code runs without errors; no broken references | pending |

### Common Fixes

| Issue | Fix |
|-------|-----|
| Generic fonts detected | Replace with a distinctive alternative; update Google Fonts import link |
| Purple gradient present | Replace with palette committed to in design rationale |
| Standard hero/card layout | Introduce grid-breaking element or asymmetric composition |
| Flat background | Apply gradient mesh, noise texture, or layered transparency |
| No animation | Add CSS keyframe animation for page load with staggered reveals |
| Code has broken references | Move external assets to CDN; inline SVGs where appropriate |

## Step 5: Write Design Rationale

Write `/app/results/design_rationale.md` documenting:

```markdown
# Design Rationale — <component/page name>

## Aesthetic Direction
- **Chosen tone**: <e.g., Retro-futuristic>
- **Rationale**: <Why this direction fits the purpose and audience>
- **Differentiation**: <The one thing a viewer will remember>

## Typography
- **Display font**: <name and source>
- **Body font**: <name and source>
- **Why**: <How these choices serve the aesthetic direction>

## Color Palette
- **Dominant**: <color + hex>
- **Accent**: <color + hex>
- **Background**: <color + description>
- **CSS variables**: Listed in the code as `--color-*`

## Motion Strategy
- **Page load**: <description of staggered reveal>
- **Hover states**: <description>
- **Scroll effects**: <description if any>

## Anti-pattern Avoidance
- [ ] No generic fonts used
- [ ] No purple gradients
- [ ] No predictable layout
- [ ] No cookie-cutter components
```

## Step 6: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"

# Check required output files
for f in \
  "$RESULTS_DIR/design_rationale.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# Check that at least one frontend output file was created
if [ -z "$(ls -A "$RESULTS_DIR/frontend_output/" 2>/dev/null)" ]; then
  echo "FAIL: /app/results/frontend_output/ is empty or missing"
else
  echo "PASS: frontend_output directory has content:"
  ls -la "$RESULTS_DIR/frontend_output/"
fi

# Check design rationale covers all required sections
for section in "Aesthetic Direction" "Typography" "Color Palette" "Anti-pattern Avoidance"; do
  if grep -q "$section" "$RESULTS_DIR/design_rationale.md" 2>/dev/null; then
    echo "PASS: design_rationale.md contains '$section'"
  else
    echo "FAIL: design_rationale.md missing '$section' section"
  fi
done

echo "=== VERIFICATION COMPLETE ==="
```

### Final Checklist

- [ ] Frontend output file(s) exist in `/app/results/frontend_output/` and are non-empty
- [ ] Code runs without errors (open in browser or buildable with documented commands)
- [ ] No forbidden fonts (Inter, Roboto, Arial, system-ui, Space Grotesk) used as primary display font
- [ ] No purple-gradient-on-white color scheme
- [ ] No standard hero/cards/footer layout without modification
- [ ] At least one high-impact animation is present
- [ ] Background has atmospheric depth (not plain solid color)
- [ ] `design_rationale.md` documents all required sections
- [ ] `summary.md` written with run metadata and design summary
- [ ] `validation_report.json` written with `overall_passed` field

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Commit to the aesthetic early.** The design direction should be decided in Step 2 before a single line of code is written. Changing direction mid-implementation leads to incoherent results.
- **Match code complexity to aesthetic intensity.** A maximalist design legitimately requires hundreds of lines of CSS with elaborate animations. A minimalist design requires fewer lines but extreme precision in spacing, weight, and proportion. Both are valid — half-hearted execution of either is not.
- **Never converge on defaults.** Each generation should produce a distinct design. If you catch yourself reaching for the same font or layout pattern as a previous run, stop and choose differently.
- **Atmosphere beats decoration.** A single well-chosen texture, gradient mesh, or noise overlay creates more visual depth than adding dozens of decorative elements. Choose one atmospheric technique and execute it fully.
- **The differentiation factor is the north star.** In Step 2, you identify the one thing a viewer will remember. Every subsequent decision — font, color, motion, layout — should serve or reinforce that single memorable quality.
- **Source skill attribution**: This runbook was imported from the `frontend-design` skill published by Anthropics at `https://skills.sh/anthropics/skills/frontend-design` (source: `https://github.com/anthropics/skills`).
