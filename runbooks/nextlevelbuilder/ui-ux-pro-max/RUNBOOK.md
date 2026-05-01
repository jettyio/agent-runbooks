---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/nextlevelbuilder/ui-ux-pro-max-skill/ui-ux-pro-max"
  source_host: "skills.sh"
  source_title: "UI/UX Pro Max - Design Intelligence"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "nextlevelbuilder"
    skill_name: "ui-ux-pro-max"
    confidence: "high"
---

# UI/UX Pro Max - Design Intelligence — Agent Runbook

## Objective

Apply comprehensive UI/UX design intelligence to web and mobile applications by leveraging a curated database of 50+ styles, 161 color palettes, 57 font pairings, 161 product type patterns, 99 UX guidelines, and 25 chart types across 10 technology stacks (React, Next.js, Vue, Svelte, SwiftUI, React Native, Flutter, Tailwind, shadcn/ui, and HTML/CSS). The agent must analyze user requirements, generate a complete design system, and implement or review UI code using priority-ranked rules for accessibility, touch interaction, performance, and responsive layout. All design decisions must be surfaced with explicit reasoning and documented in the required output files.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**All files must be written to `/app/results`. Task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/design_system.md` | Generated design system: chosen style, color palette, typography, spacing, and component guidance |
| `/app/results/ux_review.md` | UX review report with priority-ranked rule violations and recommendations |
| `/app/results/component_specs.md` | Component-level specifications for buttons, modals, forms, tables, cards, and charts |
| `/app/results/summary.md` | Executive summary with design decisions, stack used, and any issues |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

---

## Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Results directory | `/app/results` | Output directory for all generated files |
| Target stack | *(required — e.g. `react`, `nextjs`, `vue`, `svelte`, `tailwind`)* | Technology stack for implementation guidance |
| Product type | *(required — e.g. `saas`, `dashboard`, `landing-page`, `e-commerce`)* | Product type for design system selection |
| Style preference | *(optional — e.g. `glassmorphism`, `minimalism`, `neumorphism`)* | Preferred UI style; agent selects best-fit if omitted |
| Mode | *(optional — `light` or `dark`, default `light`)* | Light or dark mode preference |
| Search tool path | `python3 src/ui-ux-pro-max/scripts/search.py` | Path to the skill's search script (if available locally) |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `python3` | CLI | Yes | Run design system search scripts |
| `bash` | Shell | Yes | Execute search and setup commands |
| `nextlevelbuilder/ui-ux-pro-max-skill` | GitHub repo | Recommended | Source of design data and search scripts |

---

## Step 1: Environment Setup

Verify the environment and clone the skill repository if the search scripts are needed.

```bash
# Verify Python 3 is available
python3 --version || { echo "ERROR: python3 not found"; exit 1; }

# Create output directory
mkdir -p /app/results

# Clone or update the skill repo (required for search scripts)
if [ ! -d "/app/results/work/ui-ux-pro-max-skill" ]; then
  git clone --depth=1 https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git \
    /app/results/work/ui-ux-pro-max-skill
fi

SKILL_ROOT="/app/results/work/ui-ux-pro-max-skill"
SEARCH_CMD="python3 $SKILL_ROOT/src/ui-ux-pro-max/scripts/search.py"

echo "Environment ready"
echo "Search command: $SEARCH_CMD"
```

Confirm the search script is functional:

```bash
$SEARCH_CMD "saas" --domain product -n 3 2>/dev/null || echo "Search script unavailable — proceed with embedded rules"
```

---

## Step 2: Analyze User Requirements

Identify which design triggers apply to the current task. Use the following criteria to determine invocation level:

### Must Invoke This Skill When:
- Designing new pages (Landing Page, Dashboard, Admin, SaaS, Mobile App)
- Creating or refactoring UI components (buttons, modals, forms, tables, charts)
- Choosing color schemes, typography systems, spacing, or layout systems
- Reviewing UI code for UX, accessibility, or visual consistency
- Implementing navigation structures, animations, or responsive behavior
- Making product-level design decisions (style, information hierarchy, brand)
- Improving perceived quality, clarity, or usability of interfaces

### Recommended When:
- UI looks "not professional enough" but the reason is unclear
- Receiving feedback on usability or user experience
- Pre-launch UI quality optimization
- Aligning cross-platform design (Web / iOS / Android)
- Building design systems or reusable component libraries

### Skip When:
- Pure backend logic development
- API or database design only
- Performance optimization unrelated to the interface
- Infrastructure or DevOps work
- Non-visual scripts or automation tasks

**Decision rule**: If the task will change how a feature **looks, feels, moves, or is interacted with**, invoke this skill.

Write your determination to `/app/results/summary.md` (initial section).

---

## Step 3: Iterate on Design System Generation (max 3 rounds)

Generate a complete design system by querying the search tool for style, color, typography, and product-type recommendations. Combine results into a coherent design system document.

### Step 3a: Product Type Query

```bash
# Query product type patterns
$SEARCH_CMD "$PRODUCT_TYPE" --domain product -n 5
```

Expected output: recommended styles, color approaches, component priorities for the product type.

### Step 3b: Style Selection

```bash
# Query style details (use the style returned from product query or user preference)
$SEARCH_CMD "$STYLE_PREFERENCE" --domain style -n 3
```

### Step 3c: Typography

```bash
# Query font pairings for the style
$SEARCH_CMD "$STYLE_PREFERENCE" --domain typography -n 3
```

### Step 3d: Color Palette

```bash
# Query color palettes for product type
$SEARCH_CMD "$PRODUCT_TYPE" --domain color -n 5
```

### Step 3e: Stack-Specific Guidelines

```bash
# Query stack-specific best practices
$SEARCH_CMD "$TARGET_STACK" --domain stack -n 5 2>/dev/null || \
  echo "Stack domain not available — apply embedded React/Next.js rules"
```

After each query round, evaluate whether the design system is complete. Repeat up to **max 3 rounds** if results are insufficient or contradictory.

Write the consolidated design system to `/app/results/design_system.md` using this structure:

```markdown
# Design System — <Product Type> on <Stack>

## Chosen Style
- Name: <style>
- Rationale: <why this style fits the product type>

## Color Palette
- Primary: <hex>
- Secondary: <hex>
- Background: <hex>
- Surface: <hex>
- Error: <hex>
- Text: <hex>

## Typography
- Heading font: <font name> (Google Fonts import)
- Body font: <font name>
- Scale: 12 / 14 / 16 / 20 / 24 / 32 / 48px

## Spacing System
- Base unit: 4px
- Scale: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64px

## Border Radius
- Small: 4px | Medium: 8px | Large: 16px | Full: 9999px

## Shadows
- sm: 0 1px 2px rgba(0,0,0,0.05)
- md: 0 4px 6px rgba(0,0,0,0.07)
- lg: 0 10px 15px rgba(0,0,0,0.1)

## Component Guidance
- <component>: <guidance>
```

---

## Step 4: Apply Priority-Ranked UX Rules

Evaluate the UI against the 10 priority categories. For each category, record violations and recommendations.

### Priority Rules Reference

| Priority | Category | Level |
|----------|----------|-------|
| 1 | Accessibility | CRITICAL |
| 2 | Touch & Interaction | CRITICAL |
| 3 | Performance | HIGH |
| 4 | Style Selection | HIGH |
| 5 | Layout & Responsive | HIGH |
| 6 | Typography & Color | MEDIUM |
| 7 | Animation | MEDIUM |
| 8 | Forms & Feedback | MEDIUM |
| 9 | Navigation Patterns | HIGH |
| 10 | Charts & Data | LOW |

### Accessibility (Priority 1 — CRITICAL)

Check:
- [ ] All interactive elements have ARIA labels or visible labels
- [ ] Color contrast meets WCAG AA (4.5:1 for text, 3:1 for large text)
- [ ] Keyboard navigation works for all interactive elements
- [ ] Focus indicators are visible
- [ ] Images have alt text
- [ ] Form fields have associated labels

### Touch & Interaction (Priority 2 — CRITICAL)

Check:
- [ ] Touch targets are at least 44×44px (iOS HIG) / 48×48dp (Material Design)
- [ ] No hover-only interactions on mobile
- [ ] Swipe gestures do not conflict with browser navigation
- [ ] Tap feedback is immediate (< 100ms)

### Performance (Priority 3 — HIGH)

Check:
- [ ] Images are lazy-loaded below the fold
- [ ] Animations use `transform` / `opacity` only (no layout-triggering properties)
- [ ] Bundle size: no unnecessary dependencies
- [ ] Core Web Vitals targets: LCP < 2.5s, FID < 100ms, CLS < 0.1

### Layout & Responsive (Priority 5 — HIGH)

Check:
- [ ] Mobile-first breakpoints (320px, 768px, 1024px, 1440px)
- [ ] No horizontal scroll on mobile
- [ ] Grid/flex layouts collapse gracefully
- [ ] Touch-friendly navigation on mobile (hamburger menu or bottom nav)

Write UX review results to `/app/results/ux_review.md`.

---

## Step 5: Generate Component Specifications

For each required component, write implementation-ready specifications using the chosen stack and design system.

```bash
# Query component-specific guidance
for component in button modal form table card chart; do
  echo "=== $component ==="
  $SEARCH_CMD "$component" --domain style -n 2 2>/dev/null || true
done
```

Write component specifications to `/app/results/component_specs.md` with:
- Component name
- Variants (primary, secondary, ghost, destructive)
- States (default, hover, active, disabled, loading)
- Sizing (sm, md, lg)
- Stack-specific code snippet

---

## Step 6: Pre-Delivery Checklist

Run through the pre-delivery checklist and record all findings.

### Visual Quality
- [ ] Consistent spacing (multiples of 4px base unit)
- [ ] Consistent border radius across same-level elements
- [ ] Shadows appropriate to elevation hierarchy
- [ ] Colors from the defined palette only
- [ ] Icons from a single icon family

### Interaction
- [ ] All interactive elements have hover and active states
- [ ] Loading states for all async actions
- [ ] Empty states for lists and data tables
- [ ] Error states for forms

### Light/Dark Mode
- [ ] Both modes tested (if dark mode is enabled)
- [ ] No hard-coded `#000000` or `#ffffff` colors in components
- [ ] CSS custom properties / design tokens used for theming

### Layout
- [ ] Tested at 320px, 768px, 1024px, 1440px
- [ ] No overflow or clipping at any breakpoint
- [ ] Navigation adapts correctly on mobile

### Accessibility
- [ ] Screen reader announces dynamic content changes
- [ ] Skip navigation link present on desktop
- [ ] Color is never the sole means of conveying information

---

## Step 7: Write Summary and Validation Report

### Summary

Write `/app/results/summary.md`:

```markdown
# UI/UX Pro Max — Run Summary

## Design Decisions
- Product type: <value>
- Stack: <value>
- Chosen style: <value>
- Color palette: <name>
- Typography: <heading> / <body>
- Mode: <light|dark>

## UX Issues Found
| Priority | Category | Issue | Status |
|----------|----------|-------|--------|
| ... | ... | ... | Fixed / Flagged |

## Output Files
- design_system.md: <bytes>
- ux_review.md: <bytes>
- component_specs.md: <bytes>

## Issues / Manual Follow-up
- <any remaining issues>
```

### Validation Report

Write `/app/results/validation_report.json` (see Step 8 for schema).

---

## Step 8: Write Validation Report

Write `/app/results/validation_report.json`:

```json
{
  "version": "1.0.0",
  "run_date": "<ISO-8601 UTC>",
  "parameters": {
    "skill_url": "https://skills.sh/nextlevelbuilder/ui-ux-pro-max-skill/ui-ux-pro-max",
    "target_stack": "<stack>",
    "product_type": "<product_type>",
    "style_preference": "<style or auto>"
  },
  "stages": [
    { "name": "setup",              "passed": true,  "message": "Environment ready, skill repo cloned" },
    { "name": "requirements",       "passed": true,  "message": "Task classified as UI/UX work" },
    { "name": "design_system",      "passed": true,  "message": "Design system generated with style=<x>, palette=<y>" },
    { "name": "ux_review",          "passed": true,  "message": "<N> rules checked, <M> violations found" },
    { "name": "component_specs",    "passed": true,  "message": "<N> components specified" },
    { "name": "pre_delivery",       "passed": true,  "message": "Checklist complete, <N> items flagged" },
    { "name": "report_generation",  "passed": true,  "message": "All output files written" }
  ],
  "results": {
    "pass": 0,
    "partial": 0,
    "fail": 0
  },
  "overall_passed": true,
  "output_files": [
    "/app/results/design_system.md",
    "/app/results/ux_review.md",
    "/app/results/component_specs.md",
    "/app/results/summary.md",
    "/app/results/validation_report.json"
  ]
}
```

---

## Final Checklist

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/design_system.md" \
  "$RESULTS_DIR/ux_review.md" \
  "$RESULTS_DIR/component_specs.md" \
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

- [ ] `design_system.md` exists with chosen style, palette, typography, and spacing
- [ ] `ux_review.md` exists with priority-ranked rule evaluation
- [ ] `component_specs.md` exists with at least 3 components specified
- [ ] `summary.md` exists with design decisions and issue log
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] All output files are non-empty
- [ ] Verification script printed PASS for every file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Query the search tool first.** Before applying embedded rules, query `search.py` with the exact product type and style — the database may have more specific guidance than the embedded quick-reference rules.
- **Stack matters.** Always pass `--domain stack` for the target technology to get implementation-specific patterns (e.g. Tailwind class names vs. SwiftUI modifiers vs. Flutter widget tree structure).
- **Design tokens over hard-coded values.** Define all colors, spacing, and typography as CSS custom properties or platform-specific tokens — this ensures light/dark mode works correctly and design system updates propagate automatically.
- **Accessibility is non-negotiable.** Priority 1 rules (accessibility) must pass before shipping. Use axe DevTools or Lighthouse to verify programmatically.
- **Mobile-first, always.** Start layout design at 320px and scale up — never design desktop-first and try to compress for mobile.
- **Color is never the sole signal.** Pair color with icons, text labels, or patterns for error states, status indicators, and data encoding (especially for colorblind users).
- **Bounded iteration.** The design system generation loop (Step 3) runs max 3 rounds — if results are still incomplete, document the gap in `summary.md` and proceed with the best available information.

## Common Fixes

| Issue | Fix |
|-------|-----|
| Search script not found | Clone `nextlevelbuilder/ui-ux-pro-max-skill` and verify `src/ui-ux-pro-max/scripts/search.py` exists |
| No palette matches product type | Use `--domain color` with style name instead of product type |
| Stack domain returns no results | Use `react` or `tailwind` as a fallback; document in summary |
| Font not loading | Add Google Fonts `<link>` in `<head>` before any stylesheet that references the font |
| Dark mode colors clashing | Ensure all color values use CSS custom properties; verify at `prefers-color-scheme: dark` breakpoint |
| Accessibility contrast fail | Use a luminance-based contrast checker; lighten/darken palette neutrals until WCAG AA threshold (4.5:1) is met |
