---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/pbakaus/impeccable/polish"
  source_host: "skills.sh"
  source_title: "Polish — Impeccable Design Skill"
  imported_at: "2026-05-01T02:59:42Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "pbakaus"
    skill_name: "polish"
    confidence: "medium"
---

# Polish — Agent Runbook

## Objective

Perform a meticulous final quality pass on a frontend interface to catch all the small details that separate good work from great work. This runbook guides an agent through systematic UI polish: visual alignment, typography, color/contrast, interaction states, micro-interactions, accessibility, responsiveness, and code quality. Polish is always the last step — the interface must be functionally complete before this runbook is applied. The agent must align all changes to the project's existing design system rather than introducing one-off implementations.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/polish_report.md` | Itemized findings across all polish dimensions with severity and resolution notes |
| `/app/results/checklist.md` | Completed polish checklist (every item marked pass/fail/na with notes) |
| `/app/results/design_system_notes.md` | Design system conventions discovered during Step 2, including token names and drift classification |
| `/app/results/summary.md` | Executive summary of polish session: issues found, fixed, deferred |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Quality bar | `flagship` | `MVP` (functional, minimal polish) or `flagship` (exhaustive polish) |
| Design context path | auto-detect | Path to `PRODUCT.md` / `DESIGN.md` or directory containing them |
| Target feature | *(required)* | Name or path of the feature/component being polished |
| Breakpoints to test | `mobile,tablet,desktop` | Comma-separated list of viewport sizes to verify |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| Functional codebase | Prerequisite | Yes | The feature must be functionally complete before polishing |
| `PRODUCT.md` | File | Yes | Product context: users, brand, tone, anti-references |
| `DESIGN.md` | File | Recommended | Design tokens: colors, typography, spacing, components |
| Browser DevTools | Tool | Yes | Inspect spacing, contrast, and layout in real browser |
| Real device(s) | Hardware | Yes | Verify touch targets and text size on actual devices |
| Accessibility checker | Tool | Yes | WAVE, axe, or equivalent for WCAG contrast and ARIA checks |

## Step 1: Environment Setup

Verify prerequisites before touching any code.

```bash
echo "=== POLISH PRE-FLIGHT ==="

# Verify functional completeness was declared
if [ -z "$TARGET_FEATURE" ]; then
  echo "ERROR: TARGET_FEATURE env var required. Set it to the feature/component path."
  exit 1
fi

# Check for design context files
PRODUCT_MD=$(find . -maxdepth 3 -name "PRODUCT.md" | head -1)
DESIGN_MD=$(find . -maxdepth 3 -name "DESIGN.md" | head -1)

[ -n "$PRODUCT_MD" ] && echo "PASS: PRODUCT.md found at $PRODUCT_MD" || echo "WARN: PRODUCT.md not found — polish will use visible codebase conventions"
[ -n "$DESIGN_MD"  ] && echo "PASS: DESIGN.md found at $DESIGN_MD"   || echo "WARN: DESIGN.md not found — will infer tokens from existing code"

mkdir -p /app/results
echo "PASS: Output directory ready"
```

**CRITICAL**: Do not proceed if the feature is not functionally complete. Polish before functionality is wasteful and often introduces regressions.

## Step 2: Design System Discovery

Before any edits, map the existing design system. Polish without system alignment is decoration on top of drift.

1. **Load context files** — Read `PRODUCT.md` and `DESIGN.md` (or equivalent). Extract:
   - Color tokens (names and values)
   - Spacing scale (e.g., 4px base, t-shirt sizes, or named tokens)
   - Typography styles (families, sizes, weights, line heights)
   - Component library location and import patterns
   - Motion conventions (duration ranges, easing curves, reduced-motion policy)
   - Naming conventions for variables and components

2. **Scan the codebase for conventions** — Even without formal docs, the code reveals the system:
   ```bash
   # Find token definitions
   grep -r "spacing\|color\|font\|radius" src/ --include="*.css" --include="*.ts" | grep -E "^\s*--" | sort -u | head -40
   # Find shared component imports
   grep -r "from.*components\|from.*ui" src/ --include="*.tsx" | grep -oE "from '[^']+'" | sort | uniq -c | sort -rn | head -20
   ```

3. **Identify and classify drift** — For every deviation from the system, assign a root cause:
   - **Missing token** — the value should exist as a token but doesn't yet
   - **One-off implementation** — a shared component already exists but wasn't used
   - **Conceptual misalignment** — flow, IA, or hierarchy doesn't match neighboring features

4. **Write `design_system_notes.md`** with all discovered conventions and drift findings.

**If anything about the system is ambiguous, ask — never guess at design system principles.**

## Step 3: Pre-Polish Assessment

Understand the current state before making changes.

1. **Review completeness** — confirm the feature is fully functional, list any known issues to preserve as TODOs, establish the quality bar (`MVP` or `flagship`), and note the ship timeline.

2. **Walk the user's path** — experience the feature as the end user before opening DevTools:
   - Use the feature end-to-end
   - Note friction points, confusion, and anything that feels off
   - Ask: does this match the shape of neighboring features?

3. **Triage issues** — classify each issue as:
   - **Cosmetic** — looks off, does not block the user
   - **Functional** — breaks, blocks, or confuses the experience
   
   When polish time is limited, functional issues ship first.

4. **Document findings** in `/app/results/polish_report.md` with a running list as you discover and resolve issues.

## Step 4: Polish Systematically (max 3 rounds per dimension)

Work through all dimensions methodically. For each dimension: inspect → find issues → fix → verify. Never move on leaving known issues unresolved unless explicitly deferred.

### 4.1 Visual Alignment & Spacing

- Enable grid overlay and verify all elements align to the grid
- Check all spacing values against the design token scale — no arbitrary values
- Verify optical alignment for icons (may need 1–2px offset for visual centering)
- Test at all declared breakpoints
- **Fix**: Replace hard-coded pixel gaps with design token references

### 4.2 Information Architecture & Flow

- Compare this feature's shape to 2–3 neighboring features: does the same conceptual weight get the same visual weight?
- Verify the flow shape (modal vs full-page, inline edit vs route, save-on-blur vs explicit submit) matches established patterns
- Check that nouns and verbs match the rest of the product vocabulary
- Verify empty → loading → loaded → error transitions match adjacent features

### 4.3 Typography

- Confirm heading/body/caption size and weight hierarchy is consistent throughout
- Verify body text line length (45–75 characters)
- Check for widows and orphans in long text blocks
- Confirm no FOUT/FOIT on font load

### 4.4 Color & Contrast

```bash
# Quick contrast audit using axe-cli (if available)
npx axe --disable=color-contrast-enhanced <URL> 2>/dev/null | grep -i contrast || echo "Run contrast check manually in browser DevTools"
```

- All text meets WCAG AA (4.5:1 body, 3:1 large text)
- No hard-coded hex/rgb values — all colors reference tokens
- Tinted neutrals: no pure gray (`#808080`) or pure black — add subtle chroma
- Gray text never on colored backgrounds — use a shade of that color or transparency

### 4.5 Interaction States

Every interactive element must have all 8 states: default, hover, focus, active, disabled, loading, error, success.

```bash
# Find interactive elements missing focus styles
grep -rn "button\|input\|select\|textarea\|a" src/ --include="*.css" | grep -v "focus" | head -20
```

### 4.6 Micro-interactions & Transitions

- All state changes animate at 150–300ms with ease-out easing
- No bounce or elastic easing — they feel dated
- Test at 60fps (Chrome DevTools Performance panel)
- Verify `prefers-reduced-motion` media query disables/reduces animations

### 4.7 Content & Copy

- Same things named the same everywhere
- Consistent capitalization rule applied (Title Case vs Sentence case)
- No typos; grammar is consistent
- Labels don't end in periods unless all labels do

### 4.8 Forms & Inputs

- All inputs have associated `<label>` elements (not just placeholder text)
- Required fields clearly marked
- Error messages are helpful and recovery-oriented
- Tab order is logical; no focus traps

### 4.9 Edge Cases

- Loading state: every async action has visible feedback
- Empty state: welcoming message, not blank space
- Error state: clear message + recovery path
- Long content: test with 3× expected max input length
- Offline: graceful degradation if applicable

### 4.10 Responsiveness

- Test at mobile (375px), tablet (768px), desktop (1280px)
- All touch targets ≥ 44×44px
- No text smaller than 14px on mobile
- No horizontal scroll at any tested breakpoint

### 4.11 Performance

- No Cumulative Layout Shift (CLS > 0.1 fails Core Web Vitals)
- Images have explicit width/height or aspect-ratio to prevent reflow
- Lazy-load below-the-fold media

### 4.12 Code Quality

```bash
# Find console.log calls
grep -rn "console\." src/ --include="*.ts" --include="*.tsx" --include="*.js" | grep -v "\.test\." | grep -v "\/\/"
# Find TODO/FIXME markers
grep -rn "TODO\|FIXME\|HACK\|XXX" src/ --include="*.ts" --include="*.tsx"
# TypeScript any usage
grep -rn ": any\|as any" src/ --include="*.ts" --include="*.tsx"
```

Remove all console logs, dead code, unused imports. No TypeScript `any` without explicit justification.

## Step 5: Complete the Polish Checklist

Mark every item in `/app/results/checklist.md` as `pass`, `fail`, or `n/a`:

```markdown
# Polish Checklist

| Item | Status | Notes |
|------|--------|-------|
| Aligned to design system (drift named and resolved by root cause) | | |
| IA and flow shape match neighboring features | | |
| Visual alignment perfect at all breakpoints | | |
| Spacing uses design tokens consistently | | |
| Typography hierarchy consistent | | |
| All interactive states implemented | | |
| All transitions smooth (60fps) | | |
| Copy consistent and polished | | |
| Icons consistent and properly sized | | |
| All forms properly labeled and validated | | |
| Error states helpful | | |
| Loading states clear | | |
| Empty states welcoming | | |
| Touch targets ≥ 44×44px | | |
| Contrast ratios meet WCAG AA | | |
| Keyboard navigation works | | |
| Focus indicators visible | | |
| No console errors or warnings | | |
| No layout shift on load | | |
| Works in all supported browsers | | |
| Respects reduced motion preference | | |
| Code is clean (no TODOs, console.logs, commented code) | | |
```

## Step 6: Iterate on Errors (max 3 rounds)

If any checklist item is `fail`:

1. Document the issue in `polish_report.md` with: dimension, description, severity (cosmetic/functional), and proposed fix
2. Apply the fix
3. Re-verify the specific item
4. Repeat up to 3 times per issue

After 3 rounds, if an item is still failing:
- Mark it `deferred` in the checklist with rationale
- Log it as a follow-up in `summary.md`
- Never ship a `fail` for a **functional** issue — escalate to the team

### Common Fixes

| Issue | Fix |
|-------|-----|
| Hard-coded spacing / pixel gaps | Replace with design token reference (e.g., `var(--space-4)` or `spacing.md`) |
| Missing hover/focus/active state | Add the state CSS using the existing token palette; verify with keyboard navigation |
| Contrast ratio failure | Switch text or background to a darker/lighter token; verify at 4.5:1 with DevTools |
| Animation jank or >300ms | Switch to `transform`/`opacity` properties; cap duration at 300ms with ease-out easing |
| Missing empty state | Add a placeholder with an icon, heading, and action CTA matching neighboring empty states |
| Layout shift on load | Add explicit `width`/`height` or `aspect-ratio` to images and async-loaded containers |
| One-off component instead of shared | Import the design-system equivalent and delete the local copy |
| Console errors in production | Trace to root cause; remove debug logging; fix unhandled promise rejections |
| TypeScript `any` usage | Narrow the type using the actual data shape or introduce a typed interface |
| Tab order broken | Use `tabindex` values or reorder DOM elements to match visual reading order |

## Step 7: Final Verification

Before marking polish complete:

1. **Use it yourself** — interact with the feature as an end user for at least 2 minutes
2. **Test on real devices** — not just browser DevTools; at minimum one mobile device
3. **Request a fresh-eyes review** — have someone who hasn't seen the feature try it
4. **Compare to design** — if a design mockup exists, do a side-by-side comparison
5. **Test all states** — walk through every state, not just the happy path

## Step 8: Clean Up

After polishing, improve code hygiene:

- **Replace custom implementations** with design system components where equivalents now exist
- **Remove orphaned code** — styles, components, or files made obsolete by polish changes
- **Consolidate new values into tokens** — if a new value was introduced, check if it should become a token
- **Verify DRY principles** — look for duplication introduced during polish and consolidate

## Step 9: Write Results and Summary

Write `/app/results/summary.md`:

```markdown
# Polish Session Results

## Feature
<feature name and path>

## Quality Bar
<MVP|flagship>

## Issues Found
| Dimension | Issue | Severity | Status |
|-----------|-------|----------|--------|
| ... | ... | cosmetic/functional | fixed/deferred |

## Deferred Items
<List any items deferred with rationale and suggested follow-up>

## Design System Notes
<Key conventions discovered; any drift patched or escalated>

## Outcome
<Overall assessment: ready to ship / needs follow-up>
```

## Step 10: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/polish_report.md" \
  "$RESULTS_DIR/checklist.md" \
  "$RESULTS_DIR/design_system_notes.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== END VERIFICATION ==="
```

### Checklist

- [ ] `polish_report.md` exists with itemized findings across all dimensions
- [ ] `checklist.md` exists with all items marked pass/fail/n/a
- [ ] `design_system_notes.md` exists with discovered tokens and drift classification
- [ ] `summary.md` exists with issue counts, deferred items, and ship recommendation
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Verification script printed PASS for every line
- [ ] No functional issues remain in `fail` state
- [ ] All deferred items documented with rationale

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Prefer root-cause fixes.** A misaligned element is a symptom — find whether it's a missing token, a one-off component, or a conceptual flow mismatch, then fix the root cause.
- **Sweat the details.** Zoom in. Squint at it. The little things add up. Polish until it feels effortless, looks intentional, and works flawlessly.
- **Consistent quality level over perfection in one area.** Never perfect one corner while leaving another rough.
- **Design system alignment is not optional.** Polish without alignment is decoration on top of drift and makes the next person's job harder.
- **Reduced motion is not optional.** The `prefers-reduced-motion` check must be verified, not assumed.
- **Fresh eyes catch things.** Always get a second review before marking polish complete.
- **Never introduce bugs while polishing.** After each fix, verify that the feature still works end-to-end.
