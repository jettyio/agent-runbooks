---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/vercel-labs/agent-skills/web-design-guidelines"
  source_host: "skills.sh"
  source_title: "Web Interface Guidelines"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "vercel-labs"
    skill_name: "web-design-guidelines"
    confidence: "high"
secrets: {}
---

# Web Interface Guidelines — Agent Runbook

## Objective

Review UI code files for compliance with the Vercel Web Interface Guidelines. The agent reads the specified files and checks them against a comprehensive set of rules covering accessibility, focus states, forms, animation, typography, content handling, images, performance, navigation, touch interaction, safe areas, dark mode, locale, hydration safety, hover states, and copy conventions. Output is concise and high signal-to-noise, grouped by file with `file:line` references. Each finding states the issue and location; explanations are included only when the fix is non-obvious.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/review_report.md` | Compliance review output grouped by file with `file:line` findings |
| `/app/results/summary.md` | Executive summary with file count, total findings, and pass/fail per category |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| `arguments` | *(required)* | File or glob pattern to review, e.g. `src/components/*.tsx` |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `git` | CLI | No | For resolving file paths within a repository |
| Source files | Files | Yes | The UI source files matching `<arguments>` |

## Step 1: Environment Setup

Verify the target files exist and are readable before proceeding.

```bash
echo "=== Environment Setup ==="
# Confirm arguments were supplied
if [ -z "$ARGUMENTS" ]; then
  echo "ERROR: No file or pattern specified. Pass the target via ARGUMENTS."
  exit 1
fi

# Expand the pattern and confirm at least one file matches
FILES=$(ls $ARGUMENTS 2>/dev/null)
if [ -z "$FILES" ]; then
  echo "ERROR: No files found matching pattern: $ARGUMENTS"
  exit 1
fi

echo "Files to review:"
echo "$FILES"
echo ""
mkdir -p /app/results
```

## Step 2: Read and Analyse Files

For each file matching `$ARGUMENTS`, read its content and check it against every rule category below. Record each violation as a finding.

### Accessibility Rules

- Icon-only buttons need `aria-label`
- Form controls need `<label>` or `aria-label`
- Interactive elements need keyboard handlers (`onKeyDown`/`onKeyUp`)
- `<button>` for actions, `<a>`/`<Link>` for navigation (not `<div onClick>`)
- Images need `alt` (or `alt=""` if decorative)
- Decorative icons need `aria-hidden="true"`
- Async updates (toasts, validation) need `aria-live="polite"`
- Use semantic HTML (`<button>`, `<a>`, `<label>`, `<table>`) before ARIA
- Headings hierarchical `<h1>`–`<h6>`; include skip link for main content
- `scroll-margin-top` on heading anchors

### Focus States

- Interactive elements need visible focus: `focus-visible:ring-*` or equivalent
- Never `outline-none` / `outline: none` without focus replacement
- Use `:focus-visible` over `:focus` (avoid focus ring on click)
- Group focus with `:focus-within` for compound controls

### Forms

- Inputs need `autocomplete` and meaningful `name`
- Use correct `type` (`email`, `tel`, `url`, `number`) and `inputmode`
- Never block paste (`onPaste` + `preventDefault`)
- Labels clickable (`htmlFor` or wrapping control)
- Disable spellcheck on emails, codes, usernames (`spellCheck={false}`)
- Checkboxes/radios: label + control share single hit target (no dead zones)
- Submit button stays enabled until request starts; spinner during request
- Errors inline next to fields; focus first error on submit
- Placeholders end with `…` and show example pattern
- `autocomplete="off"` on non-auth fields to avoid password manager triggers
- Warn before navigation with unsaved changes (`beforeunload` or router guard)

### Animation

- Honor `prefers-reduced-motion` (provide reduced variant or disable)
- Animate `transform`/`opacity` only (compositor-friendly)
- Never `transition: all`—list properties explicitly
- Set correct `transform-origin`
- SVG: transforms on `<g>` wrapper with `transform-box: fill-box; transform-origin: center`
- Animations interruptible—respond to user input mid-animation

### Typography

- `…` not `...`
- Curly quotes `"` `"` not straight `"`
- Non-breaking spaces: `10&nbsp;MB`, `⌘&nbsp;K`, brand names
- Loading states end with `…`: `"Loading…"`, `"Saving…"`
- `font-variant-numeric: tabular-nums` for number columns/comparisons
- Use `text-wrap: balance` or `text-pretty` on headings (prevents widows)

### Content Handling

- Text containers handle long content: `truncate`, `line-clamp-*`, or `break-words`
- Flex children need `min-w-0` to allow text truncation
- Handle empty states—don't render broken UI for empty strings/arrays
- User-generated content: anticipate short, average, and very long inputs

### Images

- `<img>` needs explicit `width` and `height` (prevents CLS)
- Below-fold images: `loading="lazy"`
- Above-fold critical images: `priority` or `fetchpriority="high"`

### Performance

- Large lists (>50 items): virtualize (`virtua`, `content-visibility: auto`)
- No layout reads in render (`getBoundingClientRect`, `offsetHeight`, `offsetWidth`, `scrollTop`)
- Batch DOM reads/writes; avoid interleaving
- Prefer uncontrolled inputs; controlled inputs must be cheap per keystroke
- Add `<link rel="preconnect">` for CDN/asset domains
- Critical fonts: `<link rel="preload" as="font">` with `font-display: swap`

### Navigation & State

- URL reflects state—filters, tabs, pagination, expanded panels in query params
- Links use `<a>`/`<Link>` (Cmd/Ctrl+click, middle-click support)
- Deep-link all stateful UI (if uses `useState`, consider URL sync via nuqs or similar)
- Destructive actions need confirmation modal or undo window—never immediate

### Touch & Interaction

- `touch-action: manipulation` (prevents double-tap zoom delay)
- `-webkit-tap-highlight-color` set intentionally
- `overscroll-behavior: contain` in modals/drawers/sheets
- During drag: disable text selection, `inert` on dragged elements
- `autoFocus` sparingly—desktop only, single primary input; avoid on mobile

### Safe Areas & Layout

- Full-bleed layouts need `env(safe-area-inset-*)` for notches
- Avoid unwanted scrollbars: `overflow-x-hidden` on containers, fix content overflow
- Flex/grid over JS measurement for layout

### Dark Mode & Theming

- `color-scheme: dark` on `<html>` for dark themes (fixes scrollbar, inputs)
- `<meta name="theme-color">` matches page background
- Native `<select>`: explicit `background-color` and `color` (Windows dark mode)

### Locale & i18n

- Dates/times: use `Intl.DateTimeFormat` not hardcoded formats
- Numbers/currency: use `Intl.NumberFormat` not hardcoded formats
- Detect language via `Accept-Language` / `navigator.languages`, not IP
- Brand names, code tokens, identifiers: wrap with `translate="no"` to prevent garbled auto-translation

### Hydration Safety

- Inputs with `value` need `onChange` (or use `defaultValue` for uncontrolled)
- Date/time rendering: guard against hydration mismatch (server vs client)
- `suppressHydrationWarning` only where truly needed

### Hover & Interactive States

- Buttons/links need `hover:` state (visual feedback)
- Interactive states increase contrast: hover/active/focus more prominent than rest

### Content & Copy

- Active voice: "Install the CLI" not "The CLI will be installed"
- Title Case for headings/buttons (Chicago style)
- Numerals for counts: "8 deployments" not "eight"
- Specific button labels: "Save API Key" not "Continue"
- Error messages include fix/next step, not just problem
- Second person; avoid first person
- `&` over "and" where space-constrained

### Anti-patterns (flag these)

- `user-scalable=no` or `maximum-scale=1` disabling zoom
- `onPaste` with `preventDefault`
- `transition: all`
- `outline-none` without focus-visible replacement
- Inline `onClick` navigation without `<a>`
- `<div>` or `<span>` with click handlers (should be `<button>`)
- Images without dimensions
- Large arrays `.map()` without virtualization
- Form inputs without labels
- Icon buttons without `aria-label`
- Hardcoded date/number formats (use `Intl.*`)
- `autoFocus` without clear justification

## Step 3: Write Review Report

Write `/app/results/review_report.md` using the output format below. Group findings by file. Use `file:line` references (VS Code clickable). Be terse—state issue and location. Skip explanation unless fix is non-obvious. No preamble.

```text
## src/Button.tsx

src/Button.tsx:42 - icon button missing aria-label
src/Button.tsx:18 - input lacks label
src/Button.tsx:55 - animation missing prefers-reduced-motion
src/Button.tsx:67 - transition: all → list properties

## src/Modal.tsx

src/Modal.tsx:12 - missing overscroll-behavior: contain
src/Modal.tsx:34 - "..." → "…"

## src/Card.tsx

✓ pass
```

For files with no violations, output `✓ pass`.

## Step 4: Iterate on Errors (max 3 rounds)

If any rule categories were skipped or files were unreadable:

1. Note the specific failure
2. Re-attempt with adjusted glob pattern or fallback to individual file reads
3. Retry up to 3 times total before recording the error in the summary

After 3 rounds, record any unresolved skips as `⚠ skipped – unreadable` in the report.

## Step 5: Write Summary

Write `/app/results/summary.md` with:

- Total files reviewed
- Total findings by category
- Files that fully passed (`✓ pass`)
- Any files skipped due to errors

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/review_report.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

### Checklist

- [ ] `review_report.md` exists and covers all files matching `$ARGUMENTS`
- [ ] `summary.md` exists with file count and finding totals
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Every reviewed file has either findings or `✓ pass`
- [ ] No files were silently skipped

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Be terse.** The original skill says "sacrifice grammar for brevity." One finding per line. No preamble.
- **`file:line` format is mandatory.** This makes findings clickable in VS Code.
- **Check anti-patterns first.** They are the most common violations and fastest to scan for.
- **`✓ pass` is a valid output.** Not every file will have violations—explicitly mark clean files.
- **Group by file, not by rule.** Reviewers read one file at a time; don't scatter a file's findings across the report.
- **`prefers-reduced-motion` is easy to miss.** Any `transition:` or `animation:` CSS should trigger a check.
