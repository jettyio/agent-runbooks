---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/shadcn/ui/shadcn"
  source_host: "skills.sh"
  source_title: "shadcn/ui"
  imported_at: "2026-05-01T02:48:19Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "shadcn"
    skill_name: "shadcn"
    confidence: "high"
secrets: {}
---

# shadcn/ui — Agent Runbook

## Objective

This runbook guides an agent through managing shadcn/ui components and projects — adding, searching,
fixing, debugging, styling, and composing UI elements. It provides project context, component docs,
and usage examples sourced from the official shadcn/ui skill (https://skills.sh/shadcn/ui/shadcn).
Apply this runbook when working with shadcn/ui, component registries, presets, or any project with
a `components.json` file. Also applies for tasks involving `shadcn init`, creating an app with
`--preset`, or switching presets.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary of the shadcn/ui task performed |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/component_changes.md` | List of components added, updated, or removed during the run |
| `/app/results/diagnostics.json` | Project context snapshot (`npx shadcn@latest info --json` output) and any errors |

---

## Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Package runner | `npx shadcn@latest` | Adjust to `pnpm dlx shadcn@latest` or `bunx --bun shadcn@latest` based on `packageManager` from project context |
| Target registry | *(required)* | Registry to use when adding components (e.g. `@shadcn`, `@tailark`, `@magicui`). Never guess — ask the user if unspecified |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `npx` / `pnpm dlx` / `bunx` | CLI | Yes | Package runner for all `shadcn@latest` commands |
| `shadcn@latest` | npm package (auto-fetched) | Yes | The shadcn CLI for component management |
| `components.json` | Project file | Yes | Indicates the project is a shadcn/ui project |
| `Node.js` | Runtime | Yes | Required by the CLI |

---

## Step 1: Environment Setup

Verify the project is a shadcn/ui project and capture the package runner.

```bash
# Check that components.json exists
if [ ! -f components.json ]; then
  echo "ERROR: components.json not found — this does not appear to be a shadcn/ui project"
  exit 1
fi

# Determine the package manager (from packageManager field in project context)
# Adjust PKG_RUNNER based on npx/pnpm/bunx availability
PKG_RUNNER="npx shadcn@latest"

# Create output directory
mkdir -p /app/results

echo "Environment ready. Using runner: $PKG_RUNNER"
```

---

## Step 2: Get Project Context

Capture the full project context and save it for diagnostics.

```bash
# Get project info and installed components
$PKG_RUNNER info --json > /app/results/diagnostics.json 2>&1
echo "Project context captured"
cat /app/results/diagnostics.json | head -50
```

Key fields to extract from the JSON output:

| Field | Purpose |
|-------|---------|
| `aliases` | Import prefix (e.g. `@/`, `~/`) — use this, never hardcode |
| `isRSC` | When `true`, components with hooks/events need `"use client"` |
| `tailwindVersion` | `"v4"` uses `@theme inline`; `"v3"` uses `tailwind.config.js` |
| `tailwindCssFile` | Global CSS file for custom variables — always edit this, never create a new one |
| `style` | Component visual treatment (e.g. `nova`, `vega`) |
| `base` | Primitive library: `radix` or `base` |
| `iconLibrary` | Icon package (e.g. `lucide-react`, `@tabler/icons-react`) |
| `resolvedPaths` | Exact file-system destinations for components, utils, hooks |
| `framework` | Routing conventions (e.g. Next.js App Router vs Vite SPA) |
| `packageManager` | Use for non-shadcn dependency installs |
| `preset` | Current preset code and values |

---

## Step 3: Determine Task and Check Installed Components

Before adding or modifying anything, check what is already installed.

```bash
# List installed components from project context
echo "Installed components:"
cat /app/results/diagnostics.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('\n'.join(d.get('components', [])))"

# Or browse the UI directory directly
ls $(cat /app/results/diagnostics.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('resolvedPaths',{}).get('ui','src/components/ui'))")
```

**Do not import components that have not been added. Do not re-add components already installed.**

---

## Step 4: Search for and Install Components (max 3 rounds)

Search the appropriate registry and install required components. Repeat as needed, up to 3 rounds.

```bash
# Search for components before writing custom UI
$PKG_RUNNER search @shadcn -q "sidebar"
$PKG_RUNNER search @tailark -q "stats"

# Get docs and examples for a component BEFORE using it
$PKG_RUNNER docs button dialog select
# Then fetch the returned URLs to read actual API and usage patterns

# Preview changes before installing
$PKG_RUNNER add button --dry-run
$PKG_RUNNER add button --diff button.tsx

# Install components
$PKG_RUNNER add button card dialog

# Install from community registry
$PKG_RUNNER add @magicui/shimmer-button
```

**Registry selection rule:** Never default to a registry. If the user says "add a login block" without
specifying a registry, ask which registry to use.

After adding any component, always:
1. Read all added files
2. Check for missing sub-components (e.g. `SelectItem` without `SelectGroup`)
3. Fix any hardcoded import paths — use `aliases` from project context
4. Replace icon imports with the project's `iconLibrary` from project context
5. Verify compliance with Critical Rules (see Step 6)

---

## Step 5: Handle Preset Operations

When the user asks to switch or apply a preset, always ask for the merge strategy first:
**overwrite, partial, merge, or skip?**

```bash
# Inspect current preset
$PKG_RUNNER preset resolve
$PKG_RUNNER preset resolve --json

# Decode incoming preset
$PKG_RUNNER preset decode a2r6bw
$PKG_RUNNER preset url a2r6bw

# Overwrite: replaces detected components, fonts, CSS variables
$PKG_RUNNER apply a2r6bw

# Partial: update only theme and/or font
$PKG_RUNNER apply a2r6bw --only theme,font

# Merge: preserve local changes
$PKG_RUNNER init --preset a2r6bw --force --no-reinstall
# Then for each installed component, smart-merge with --dry-run + --diff

# Skip: update config and CSS only, leave components as-is
$PKG_RUNNER init --preset a2r6bw --force --no-reinstall
```

Always run preset commands inside the user's project directory (`components.json` must be present for `apply`).

---

## Step 6: Enforce Critical Rules

Apply these rules to all generated or modified code. Fix every violation before marking the task complete.

### Styling & Tailwind

- Use `className` for layout only — never override component colors/typography
- Use `flex` + `gap-*` instead of `space-x-*` / `space-y-*`
- Use `size-*` when width and height are equal (`size-10` not `w-10 h-10`)
- Use `truncate` shorthand (not `overflow-hidden text-ellipsis whitespace-nowrap`)
- Use semantic tokens only (`bg-background`, `text-muted-foreground`) — no raw color values
- Use `cn()` for conditional classes — no manual template literal ternaries
- No manual `z-index` on overlay components (Dialog, Sheet, Popover)

### Forms & Inputs

- Forms use `FieldGroup` + `Field` — never raw `div` with `space-y-*` or `grid gap-*`
- `InputGroup` uses `InputGroupInput`/`InputGroupTextarea` — never raw `Input`/`Textarea` inside
- Option sets (2–7 choices) use `ToggleGroup` — not looped `Button` with manual active state
- `FieldSet` + `FieldLegend` for grouping related checkboxes/radios
- Validation: `data-invalid` on `Field`, `aria-invalid` on the control

### Component Structure

- Items always inside their Group (`SelectItem` → `SelectGroup`, `CommandItem` → `CommandGroup`)
- Use `asChild` (radix) or `render` (base) for custom triggers
- Dialog, Sheet, and Drawer always need an accessible Title (use `className="sr-only"` if visually hidden)
- Use full Card composition: `CardHeader`/`CardTitle`/`CardDescription`/`CardContent`/`CardFooter`
- `Button` has no `isPending`/`isLoading` — compose with `Spinner` + `data-icon` + `disabled`
- `TabsTrigger` must be inside `TabsList`
- `Avatar` always needs `AvatarFallback`

### Use Components, Not Custom Markup

- `Alert` for callouts, `Empty` for empty states, `Separator` instead of `<hr>`
- `Skeleton` for loading placeholders, `Badge` instead of custom styled spans

---

## Step 7: Updating Existing Components (max 3 rounds)

When asked to update a component from upstream while keeping local changes, use smart merge.
**Never fetch raw files from GitHub manually — always use the CLI.**

```bash
# 1. See all files that would be affected
$PKG_RUNNER add <component> --dry-run

# 2. For each file, see upstream diff vs local
$PKG_RUNNER add <component> --diff <file>

# 3. Decide per file:
#    - No local changes → safe to overwrite
#    - Has local changes → apply upstream changes while preserving local modifications
#    - User says "update everything" → use --overwrite (requires explicit user approval)
$PKG_RUNNER add button --overwrite  # only with explicit user approval
```

---

## Step 8: Record Component Changes

After all changes are complete, document what was done.

Write `/app/results/component_changes.md` with:

```markdown
# Component Changes

## Added
- <component name> from <registry>

## Updated
- <component name> — strategy: <smart-merge|overwrite>

## Removed
- <component name>

## Preset Changes
- <preset code applied, strategy used>

## Import Fixes Applied
- <file path>: replaced <old import> with <new import>

## Icon Library Substitutions
- <file path>: replaced <old icon package> with <new icon package>
```

---

## Step 9: Validate the Result

Run a final check to confirm compliance.

```bash
# Re-capture project context to confirm state
$PKG_RUNNER info --json | tee /app/results/diagnostics.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
comps = d.get('components', [])
print(f'Installed components: {len(comps)}')
for c in comps:
    print(f'  - {c}')
"

echo "=== FINAL OUTPUT VERIFICATION ==="
for f in /app/results/summary.md /app/results/validation_report.json /app/results/component_changes.md /app/results/diagnostics.json; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

---

## Step 10: Write Executive Summary

Write `/app/results/summary.md` with:

```markdown
# shadcn/ui Task — Results

## Overview
- **Date**: <run date>
- **Project**: <project name from components.json>
- **Package runner**: <npx|pnpm dlx|bunx>
- **Style**: <style from project context>
- **Base**: <radix|base>

## Actions Taken
<high-level summary of what was done>

## Components

| Action | Component | Registry |
|--------|-----------|----------|
| Added | ... | ... |
| Updated | ... | ... |

## Critical Rule Compliance

| Rule Category | Status | Notes |
|---------------|--------|-------|
| Styling | PASS/FAIL | ... |
| Forms | PASS/FAIL | ... |
| Composition | PASS/FAIL | ... |

## Issues / Manual Follow-up
- <anything requiring human review>

## Provenance
- Source skill: https://skills.sh/shadcn/ui/shadcn
- Runbook: runbooks/shadcn/shadcn/RUNBOOK.md
```

---

## Step 11: Write Validation Report

Write `/app/results/validation_report.json` reflecting actual stage outcomes for this run.

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/component_changes.md" \
  "$RESULTS_DIR/diagnostics.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

### Checklist

- [ ] Project context captured and saved to `diagnostics.json`
- [ ] All requested components installed from the correct registry
- [ ] No components added that were already installed
- [ ] All added files reviewed and import paths corrected
- [ ] Icon library substitutions applied per project's `iconLibrary`
- [ ] All Critical Rules verified (Styling, Forms, Composition)
- [ ] Preset changes applied with correct strategy (overwrite/partial/merge/skip)
- [ ] `component_changes.md` documents all changes made
- [ ] `summary.md` provides an executive summary of the task
- [ ] `validation_report.json` reflects actual stage outcomes
- [ ] Verification script printed PASS for every line

**If ANY item fails, go back and fix it before finishing.**

---

## Tips

- **Prefer `npx shadcn@latest docs` before touching any component.** Always fetch the returned
  URLs to read actual API and usage patterns — never guess props or structure.
- **Check the registry before installing.** Use `npx shadcn@latest search` first. Community
  registries (`@magicui`, `@bundui`, `@tailark`) often have hardcoded import paths — fix them after adding.
- **`isRSC` gate for client components.** When `isRSC=true`, any component using `useState`,
  `useEffect`, event handlers, or browser APIs needs `"use client"` at the top.
- **Never use `--overwrite` without user approval.** It silently discards local changes.
- **Icon library is project-specific.** Never assume `lucide-react`. Always read `iconLibrary`
  from the injected project context and substitute accordingly.
- **Tailwind version matters.** `v4` uses `@theme inline` in CSS; `v3` uses `tailwind.config.js`.
- **Management dir is append-only.** Never delete or rewrite prior records.

---

## Common Fixes

| Issue | Fix |
|-------|-----|
| Component import fails | Check `aliases` from `npx shadcn@latest info` and rewrite hardcoded `@/components/ui/` paths |
| Wrong icon size in button | Remove `size-4`/`w-4 h-4` from icons — use `data-icon` attribute instead |
| `space-y-*` found in form | Replace with `flex flex-col gap-*` |
| Missing `AvatarFallback` | Always add `<AvatarFallback>` inside `<Avatar>` |
| Hardcoded `bg-blue-500` | Replace with semantic token (`bg-primary`, `text-muted-foreground`) |
| Raw `<hr>` used | Replace with `<Separator />` |
| `--overwrite` used without approval | Revert the change, get explicit user confirmation |
| Preset `apply` fails | Ensure `components.json` is present; run inside the project root |
| Validation shows `FAIL` on rule check | Re-read Step 6 and apply each failing rule fix; re-run verify script |
