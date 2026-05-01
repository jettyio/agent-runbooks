---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/pbakaus/impeccable/polish"
  source_host: "skills.sh"
  source_title: "impeccable/polish — Final Quality Polish for Frontend UI"
  imported_at: "2026-05-01T02:43:57Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "impeccable"
    skill_name: "polish"
    confidence: "high"
---

# impeccable/polish — Agent Runbook

## Objective

Perform a meticulous final quality pass on a frontend interface to catch all the small details that separate good work from great work. The agent will discover the project's design system, assess the current state of the target, systematically polish it across all visual and interaction dimensions (alignment, spacing, typography, color, interaction states, micro-interactions, copy, icons, forms, edge cases, and responsiveness), and verify that the result is production-ready. This runbook is derived from the `polish` sub-command of the `impeccable` skill by pbakaus, a comprehensive frontend design system for AI agents.

Polish is the last step, not the first — the target must be functionally complete before this runbook is invoked. The agent must align every change to the existing design system rather than introducing new patterns, and must maintain a consistent quality level across the entire feature rather than perfecting one corner while leaving others rough.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary of the polish run: what was changed, why, and any issues found |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/polish_checklist.md` | Completed polish checklist with pass/fail/skip per item and notes |
| `/app/results/design_system_notes.md` | Design system discovery notes: tokens found, drift identified, conventions documented |
| `/app/results/changes.md` | Ordered log of every change made during the polish pass with before/after reasoning |

If you finish the polish pass but have not written all files, go back and write them before stopping.

---

## Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Target | *(required — pass as argument)* | The UI feature, component, file, or route to polish |
| Quality bar | `flagship` | Polish intensity: `mvp` (functional only) or `flagship` (full craft) |
| Design system path | *(auto-discovered)* | Path to PRODUCT.md / DESIGN.md or equivalent design system docs |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `node` | CLI | Yes | Run impeccable's context loader (`load-context.mjs`) |
| `npx impeccable` | CLI | Yes | Invoke the impeccable tool for context gathering |
| Browser DevTools | External | Recommended | Visual inspection of alignment, contrast, and interaction states |
| PRODUCT.md | File | Yes | Brand, tone, users — required for design-system alignment |
| DESIGN.md | File | Recommended | Color tokens, spacing scale, typography — strongly recommended |
| WCAG contrast checker | Tool | Yes | Verify all text meets WCAG AA contrast ratios |

---

## Step 1: Environment Setup

Verify all prerequisites and load project context before any design work.

```bash
# Verify node is present
command -v node >/dev/null || { echo "ERROR: node not installed"; exit 1; }

# Create results directory
mkdir -p /app/results

# Verify target is specified
if [ -z "$TARGET" ]; then
  echo "ERROR: TARGET is not set. Set TARGET to the file, component, or route to polish."
  exit 1
fi

echo "Target: $TARGET"
echo "Quality bar: ${QUALITY_BAR:-flagship}"
```

**Pre-flight check (state before editing any files):**

```text
IMPECCABLE_PREFLIGHT: context=? product=? command_reference=polish shape=not_required image_gate=not_required mutation=closed
```

Do not open `mutation=open` until all gates pass.

---

## Step 2: Design System Discovery

**Aligning to the design system is non-optional.** Polish without alignment is decoration on top of drift.

```bash
# Load context using impeccable's loader
node {{scripts_path}}/load-context.mjs
```

Consume the full JSON output. Never pipe through `head`, `tail`, `grep`, or `jq`.

Then document the following in `/app/results/design_system_notes.md`:

1. **Find the design system**: Search for PRODUCT.md, DESIGN.md, component libraries, style guides, or token definitions. Study the core patterns: design principles, target audience, color tokens, spacing scale, typography styles, component API, motion conventions.

2. **Note the conventions**: How are shared components imported? What spacing scale is used? Which colors come from tokens vs hard-coded values? What motion and interaction patterns are established? What flow shapes are used for comparable actions (modal vs full-page, inline vs route, save-on-blur vs explicit submit)?

3. **Identify drift and name the root cause**: For every deviation, classify it as:
   - **Missing token** — value should exist in the system but doesn't
   - **One-off implementation** — a shared component already exists but wasn't used
   - **Conceptual misalignment** — the feature's flow, IA, or hierarchy doesn't match neighboring features

   The fix differs by category: patch the value, swap to the shared component, or rework the flow. Fixing the symptom without naming the cause is how drift compounds.

**If anything about the design system is ambiguous, ask — never guess.**

Write a `design_system_notes.md` with:
- PRODUCT.md summary (users, brand, tone, anti-references)
- DESIGN.md summary (color tokens, spacing scale, typography)
- Drift inventory (each item: type, location, root cause, fix)

---

## Step 3: Pre-Polish Assessment

Understand the current state before touching anything. Do **not** skip this step.

### Completeness Gate

Answer these questions explicitly before proceeding:

1. Is the feature functionally complete? (If NO, stop and return to the developer.)
2. Are there known issues to preserve? (Mark these with TODOs — do not fix them during polish.)
3. What is the quality bar? (`mvp` = functional only; `flagship` = full craft)
4. When does it ship? (Triage if ship time < 1 hour)

### Experience Walk

Think experience-first: walk the user path from the target audience's perspective before opening DevTools. Who uses this, and what's the best possible experience for them?

### Triage

Identify and classify every issue as:

- **Cosmetic** — looks off, does not impede the user
- **Functional** — breaks, blocks, or confuses the experience

When polish time is tight, functional issues ship first; cosmetic ones can land in a follow-up.

Write a triage list to `/app/results/changes.md` in the format:
```
| Issue | Classification | Priority | Proposed Fix |
```

---

## Step 4: Systematic Polish Pass

Work through each dimension methodically. Record every change in `/app/results/changes.md` with reasoning. Maintain consistent quality — never perfect one area while leaving others rough.

### 4.1 Visual Alignment & Spacing

- Pixel-perfect alignment: everything lines up to grid
- Consistent spacing: all gaps use spacing scale (no random pixel values)
- Optical alignment: adjust for visual weight (icons may need offset for optical centering)
- Responsive consistency: spacing and alignment work at all breakpoints
- Grid adherence: elements snap to baseline grid

**Check**: enable grid overlay, inspect spacing with browser DevTools, test at multiple viewport sizes.

### 4.2 Information Architecture & Flow

Match the *shape* of the experience to the design system, not just the surface:

- Progressive disclosure: match how much is revealed when, compared to neighboring features
- Established user flows: multi-step actions follow the same shape as comparable flows elsewhere (modal vs full-page, inline edit vs separate route, save-on-blur vs explicit submit)
- Hierarchy & complexity: same conceptual weight gets same visual weight throughout
- Empty, loading, and arrival transitions: match adjacent features
- Naming and mental model: use the same nouns and verbs as the rest of the system

### 4.3 Typography Refinement

- Hierarchy consistency: same elements use same sizes/weights throughout
- Line length: 45–75 characters for body text
- Line height: appropriate for font size and context
- No widows/orphans: no single words on last line
- Kerning: adjust letter spacing where needed (especially headlines)
- Font loading: no FOUT/FOIT flashes

### 4.4 Color & Contrast

- Contrast ratios: all text meets WCAG AA standards
- Consistent token usage: no hard-coded colors, all use design tokens
- Theme consistency: works in all theme variants
- Color meaning: same colors mean same things throughout
- Accessible focus: focus indicators visible with sufficient contrast
- Tinted neutrals: no pure gray or pure black — add subtle color tint (0.01 chroma)
- Gray on color: never put gray text on colored backgrounds — use a shade of that color or transparency

### 4.5 Interaction States

Every interactive element needs **all** of these states implemented:

| State | Description |
|-------|-------------|
| Default | Resting state |
| Hover | Subtle feedback (color, scale, shadow) |
| Focus | Keyboard focus indicator — never remove without replacement |
| Active | Click/tap feedback |
| Disabled | Clearly non-interactive |
| Loading | Async action feedback |
| Error | Validation or error state |
| Success | Successful completion |

Missing states create confusion and broken experiences.

### 4.6 Micro-interactions & Transitions

- Smooth transitions: all state changes animated appropriately (150–300ms)
- Consistent easing: use `ease-out-quart`/`quint`/`expo` — never bounce or elastic
- No jank: smooth animations; avoid casual layout-property animation (use `transform`/`opacity`)
- Appropriate motion: motion serves purpose, not decoration
- Reduced motion: respect `prefers-reduced-motion`

### 4.7 Content & Copy

- Consistent terminology: same things called same names throughout
- Consistent capitalization: Title Case vs. Sentence case applied consistently
- Grammar & spelling: no typos
- Appropriate length: not too wordy, not too terse
- Punctuation consistency: periods on sentences, not on labels

### 4.8 Icons & Images

- Consistent style: all icons from same family or matching style
- Appropriate sizing: icons sized consistently for context
- Proper alignment: icons align with adjacent text optically
- Alt text: all images have descriptive alt text
- Loading states: images don't cause layout shift, proper aspect ratios
- Retina support: 2x assets for high-DPI screens

### 4.9 Forms & Inputs

- Label consistency: all inputs properly labeled
- Required indicators: clear and consistent
- Error messages: helpful and consistent
- Tab order: logical keyboard navigation
- Validation timing: consistent (on blur vs on submit)

### 4.10 Edge Cases & Error States

- Loading states: all async actions have loading feedback
- Empty states: helpful, not just blank space
- Error states: clear messages with recovery paths
- Long content: handles very long names, descriptions, etc.
- Offline: appropriate handling if applicable

### 4.11 Responsiveness

- All breakpoints: test mobile (375px), tablet (768px), desktop (1280px+)
- Touch targets: 44×44px minimum on touch devices
- Readable text: no text smaller than 14px on mobile
- No horizontal scroll: content fits viewport
- Appropriate reflow: content adapts logically

### 4.12 Performance

- No layout shift: elements don't jump after load (CLS)
- Smooth interactions: no lag or jank
- Optimized images: appropriate formats and sizes
- Lazy loading: off-screen content loads lazily

### 4.13 Code Quality

- Remove console logs: no debug logging in production
- Remove commented code: clean up dead code
- Remove unused imports: clean up unused dependencies
- Consistent naming: follow established conventions
- Accessibility: proper ARIA labels and semantic HTML

---

## Step 5: Iterate on Issues (max 3 rounds)

After the first systematic pass, do a fresh-eyes review:

1. Use the feature yourself — actually interact with it end-to-end
2. Check the polish checklist (Step 6) against the current state
3. Re-examine any items that failed
4. Apply fixes and re-verify
5. Repeat up to 3 rounds total

After 3 rounds, if items are still failing, document them explicitly in `summary.md` as **known issues for follow-up** and continue.

**Common Fixes**

| Issue | Fix |
|-------|-----|
| Hard-coded color value | Replace with the nearest design token |
| Missing interaction state | Implement the state following adjacent component patterns |
| Spacing not on grid | Snap to the documented spacing scale |
| Typography hierarchy inconsistent | Align to the type scale in DESIGN.md |
| Drift in flow shape | Rework IA to match the established pattern in neighboring features |
| Custom component duplicating a shared one | Replace with the shared component |
| Gray text on colored background | Use a shade of the background color or transparency instead |

**Absolute Bans** — match-and-refuse; if you're about to write any of these, rewrite with different structure:

- Side-stripe borders: `border-left`/`border-right` > 1px as colored accent — rewrite with full borders, background tints, or nothing
- Gradient text: `background-clip: text` + gradient — use a single solid color
- Glassmorphism as default: blurs and glass cards used decoratively
- The hero-metric template: big number, small label, supporting stats, gradient accent
- Identical card grids: same-sized cards with icon + heading + text, repeated endlessly
- Modal as first thought: exhaust inline/progressive alternatives first

---

## Step 6: Complete Polish Checklist

Write `/app/results/polish_checklist.md` with a status for each item:

```markdown
| Item | Status | Notes |
|------|--------|-------|
| Aligned to the design system (drift named and resolved by root cause) | PASS/FAIL/SKIP | |
| IA and flow shape match neighboring features | | |
| Visual alignment perfect at all breakpoints | | |
| Spacing uses design tokens consistently | | |
| Typography hierarchy consistent | | |
| All interactive states implemented | | |
| All transitions smooth (60fps) | | |
| Copy consistent and polished | | |
| Icons consistent and properly sized | | |
| All forms properly labeled and validated | | |
| Error states are helpful | | |
| Loading states are clear | | |
| Empty states are welcoming | | |
| Touch targets 44×44px minimum | | |
| Contrast ratios meet WCAG AA | | |
| Keyboard navigation works | | |
| Focus indicators visible | | |
| No console errors or warnings | | |
| No layout shift on load | | |
| Works in all supported browsers | | |
| Respects reduced motion preference | | |
| Code is clean (no TODOs, console.logs, commented code) | | |
```

---

## Step 7: Final Verification

Before marking as done:

1. **Use it yourself**: Actually interact with the feature end-to-end — happy path and edge cases
2. **Test on real devices**: Not just browser DevTools simulations
3. **Compare to design**: Match the intended visual design
4. **Check all states**: Default, hover, focus, active, disabled, loading, error, success, empty
5. **Check all breakpoints**: Mobile (375px), tablet (768px), desktop (1280px+)

### Clean Up

After polishing, ensure code quality:

- **Replace custom implementations**: If the design system provides a component you reimplemented, switch to the shared version
- **Remove orphaned code**: Delete unused styles, components, or files made obsolete by polish
- **Consolidate tokens**: If you introduced new values, check whether they should be tokens
- **Verify DRYness**: Look for duplication introduced during polishing and consolidate

---

## Step 8: Write Output Files

Write all required output files to `/app/results/`:

### summary.md

```markdown
# Polish Run — Results

## Overview
- **Date**: <run date>
- **Target**: <target>
- **Quality bar**: <mvp|flagship>
- **Design system**: <PRODUCT.md found / DESIGN.md found>
- **Rounds**: <1|2|3>

## Polish Summary
- **Issues found**: <count>
- **Issues resolved**: <count>
- **Issues deferred**: <count>
- **Absolute bans encountered**: <count>

## Checklist Results
- **PASS**: <count>
- **FAIL**: <count>
- **SKIP**: <count>

## Known Issues / Follow-up
- <Any deferred issues>
- <Any PARTIAL findings>

## Provenance
- Origin: https://skills.sh/pbakaus/impeccable/polish
- Runbook: runbooks/impeccable/polish/RUNBOOK.md
```

### validation_report.json

```json
{
  "version": "1.0.0",
  "run_date": "<ISO-8601>",
  "parameters": {
    "target": "<target>",
    "quality_bar": "flagship"
  },
  "stages": [
    { "name": "setup",               "passed": true, "message": "Environment verified, context loaded" },
    { "name": "design_system",       "passed": true, "message": "Design system discovered, N drift items found" },
    { "name": "assessment",          "passed": true, "message": "Pre-polish assessment complete, N issues triaged" },
    { "name": "polish_pass",         "passed": true, "message": "Systematic polish pass complete" },
    { "name": "iteration",           "passed": true, "message": "max 3 rounds — N rounds needed" },
    { "name": "checklist",           "passed": true, "message": "Polish checklist complete" },
    { "name": "final_verification",  "passed": true, "message": "Final verification passed" },
    { "name": "output_files",        "passed": true, "message": "All required output files written" }
  ],
  "results": {
    "pass": 0,
    "partial": 0,
    "fail": 0
  },
  "overall_passed": true,
  "output_files": [
    "/app/results/summary.md",
    "/app/results/validation_report.json",
    "/app/results/polish_checklist.md",
    "/app/results/design_system_notes.md",
    "/app/results/changes.md"
  ]
}
```

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/polish_checklist.md" \
  "$RESULTS_DIR/design_system_notes.md" \
  "$RESULTS_DIR/changes.md"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# Verify validation report
if python3 -c "import json,sys; d=json.load(open('$RESULTS_DIR/validation_report.json')); sys.exit(0 if d.get('overall_passed') else 1)" 2>/dev/null; then
  echo "PASS: validation_report.json overall_passed=true"
else
  echo "WARN: validation_report.json overall_passed=false — review issues"
fi

echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] `summary.md` exists and summarizes the polish run
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] `polish_checklist.md` exists with status for every item
- [ ] `design_system_notes.md` exists with drift inventory
- [ ] `changes.md` exists with ordered log of every change
- [ ] All interaction states are implemented for every interactive element
- [ ] All text meets WCAG AA contrast ratios
- [ ] All spacing uses design tokens (no hard-coded pixel values)
- [ ] Absolute bans (side-stripe borders, gradient text, glassmorphism, hero-metric template, identical card grids) are not present
- [ ] Code is clean: no console.logs, commented-out code, or unused imports
- [ ] `prefers-reduced-motion` is respected
- [ ] Keyboard navigation works end-to-end

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Design system first, always.** Run the context loader before touching any file. Polishing without knowing the design system creates drift — not quality.
- **Name the root cause, not just the symptom.** When you find drift, classify it as missing token, one-off implementation, or conceptual misalignment. The fix differs, and fixing the symptom compounds the problem.
- **The AI slop test.** If someone could look at this interface and say "AI made that" without doubt, it's failed. First-order check: can someone guess the theme from the category? Second-order: can someone guess the aesthetic from category + anti-references? Both must fail.
- **Triage ruthlessly when time is short.** Functional issues ship first. Consistent quality across the whole feature beats perfection in one corner.
- **Gray on color is always wrong.** Never put gray text on colored backgrounds — use a shade of that color or transparency.
- **em dashes are banned.** Use commas, colons, semicolons, periods, or parentheses. Not `--` either.
- **Polish the checklist in order.** Alignment and spacing first — everything else builds on the grid. Typography and color next. Interaction states last.
