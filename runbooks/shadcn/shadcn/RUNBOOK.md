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
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "shadcn"
    skill_name: "shadcn"
    confidence: "high"
---

# shadcn/ui — Agent Runbook

## Objective

This runbook guides an AI agent through the full lifecycle of managing shadcn/ui components in a user's project. The agent must search registries for available components, add them as source code, fetch documentation, preview changes before installation, and intelligently merge upstream updates while preserving local modifications. Components are never imported—they are always added as source code via the CLI. The agent enforces strict coding rules across styling, forms, component structure, and icon usage.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/components_added.md` | List of components searched, previewed, or added during this run |
| `/app/results/changes_summary.md` | Summary of all file changes made (dry-run previews and actual adds) |
| `/app/results/summary.md` | Executive summary of the run: components handled, issues found, fixes applied |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

## Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Project context | `npx shadcn@latest info --json` | JSON blob with project config and installed components |
| Target components | *(required)* | One or more component names or registry references to add/update |
| Registry | *(required, ask user if not specified)* | e.g. `@shadcn`, `@magicui`, `@tailark` |
| Operation | `add` \| `update` \| `search` \| `docs` | Action to perform |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `npx shadcn@latest` | CLI | Yes | Primary shadcn/ui CLI for all registry operations |
| `pnpm dlx shadcn@latest` or `bunx --bun shadcn@latest` | CLI | Conditional | Use based on project's `packageManager` field |
| Node.js / npm / pnpm / bun | Runtime | Yes | Required to run the shadcn CLI |
| Project with `components.json` | Config | Yes | Must exist for `add`/`apply`/`preset` operations |

## Step 1: Environment Setup

Verify the environment and inject project context before taking any action.

```bash
# Verify shadcn CLI is accessible
npx shadcn@latest --version

# Get project context (injected automatically, but refresh if needed)
npx shadcn@latest info --json
```

Parse the JSON output and record the following key fields for use in all subsequent steps:
- `aliases` — import alias prefix (e.g. `@/`, `~/`)
- `isRSC` — whether the project uses React Server Components
- `tailwindVersion` — `"v3"` or `"v4"`
- `tailwindCssFile` — path to the global CSS file
- `base` — primitive library (`radix` or `base`)
- `iconLibrary` — icon imports to use
- `resolvedPaths` — actual file-system paths for components, utils, hooks
- `framework` — routing conventions (Next.js App Router, Vite, etc.)
- `packageManager` — use this for all non-shadcn dependency installs

> **IMPORTANT:** Use the project's package runner for all CLI commands: `npx shadcn@latest`, `pnpm dlx shadcn@latest`, or `bunx --bun shadcn@latest` — based on `packageManager`.

## Step 2: Inspect Installed Components

Before adding any component, check what is already installed to avoid duplicates.

```bash
# List installed components from project context
npx shadcn@latest info --json | jq '.components'

# Or list the UI directory directly
ls $(npx shadcn@latest info --json | jq -r '.resolvedPaths.ui')
```

- Do **not** re-add components already installed.
- Do **not** import components that have not been added.

## Step 3: Search Registries

When adding a component, always search first rather than guessing names.

```bash
# Search the primary shadcn registry
npx shadcn@latest search @shadcn -q "<component-name>"

# Search community registries
npx shadcn@latest search @magicui -q "<component-name>"
npx shadcn@latest search @tailark -q "<component-name>"
```

> **IMPORTANT:** Never default to a registry. If the user does not specify one, ask which registry to use.

## Step 4: Fetch Docs and Examples

Before creating, fixing, or using any component, fetch its documentation.

```bash
# Get documentation URLs for components
npx shadcn@latest docs button dialog select

# View a registry item without installing
npx shadcn@latest view @shadcn/button
```

Fetch the returned URLs to get the actual documentation content. Use correct API and usage patterns rather than guessing.

## Step 5: Preview Changes (Dry-Run)

Always preview changes before adding or updating components.

```bash
# Dry-run to see all files that would be affected
npx shadcn@latest add <component> --dry-run

# Show the diff for a specific file
npx shadcn@latest add <component> --diff <file.tsx>
```

Record the dry-run output in `/app/results/changes_summary.md` under a "Preview" section.

## Step 6: Add or Update Components

### Adding new components

```bash
npx shadcn@latest add button card dialog
npx shadcn@latest add @magicui/shimmer-button
```

### Updating existing components (max 3 rounds per component)

For each component to update:

1. Run `npx shadcn@latest add <component> --dry-run` to list affected files.
2. For each file, run `npx shadcn@latest add <component> --diff <file>` to see upstream vs. local diff.
3. Decide per file:
   - **No local changes** → safe to overwrite.
   - **Has local changes** → read the local file, analyze the diff, apply upstream updates while preserving local modifications.
   - **User says "just update everything"** → use `--overwrite`, but confirm first.
4. Apply the decided changes.
5. Re-run step validation (Step 8) to check correctness.
6. Repeat up to 3 rounds total if issues remain.

> **NEVER use `--overwrite` without the user's explicit approval.**
> **NEVER fetch raw files from GitHub manually — always use the CLI.**

## Step 7: Fix Third-Party Imports

After adding components from community registries (e.g. `@bundui`, `@magicui`), fix hardcoded import paths.

```bash
# Get the correct UI alias
npx shadcn@latest info --json | jq '.resolvedPaths.ui'
```

- Replace any hardcoded `@/components/ui/...` paths with the project's actual alias.
- Replace icon imports with the project's `iconLibrary` from the project context.
  - e.g. if registry uses `lucide-react` but project uses `@tabler/icons-react`, swap all imports and icon names.

## Step 8: Review and Validate Added Components

After adding any component or block, always review the added files.

Checklist per component:
- [ ] No missing sub-components (e.g. `SelectItem` without `SelectGroup`)
- [ ] No missing imports
- [ ] Correct component composition (no violations of Critical Rules)
- [ ] Icon imports match project's `iconLibrary`
- [ ] `FieldGroup` + `Field` used for form layout (not raw `div` with `space-y-*`)
- [ ] `asChild` (radix) or `render` (base) used for custom triggers
- [ ] `Dialog`, `Sheet`, `Drawer` all have a Title
- [ ] No `space-x-*` / `space-y-*` — use `flex` + `gap-*`
- [ ] Semantic color tokens used (not raw `bg-blue-500` etc.)
- [ ] No manual `dark:` overrides
- [ ] No manual `z-index` on overlay components

## Step 9: Handle Preset Operations

If the user requests a preset switch:

1. **Inspect current preset**: `npx shadcn@latest preset resolve`
2. **Inspect incoming preset**: `npx shadcn@latest preset decode <code>`
3. Ask the user: **overwrite**, **partial**, **merge**, or **skip**?

| Choice | Command |
|--------|---------|
| Overwrite | `npx shadcn@latest apply <code>` |
| Partial (theme only) | `npx shadcn@latest apply <code> --only theme` |
| Partial (font only) | `npx shadcn@latest apply <code> --only font` |
| Merge | `npx shadcn@latest init --preset <code> --force --no-reinstall`, then smart-merge each installed component |
| Skip | `npx shadcn@latest init --preset <code> --force --no-reinstall` |

> Always run preset commands inside the user's project directory. Pass `--base <current-base>` when using a scratch directory.

## Step 10: Iterate on Errors (max 3 rounds)

If any validation check in Step 8 fails:

1. Read the specific error.
2. Apply the targeted fix from the table below.
3. Re-run the validation checklist.
4. Repeat up to 3 rounds total.

After 3 rounds with unresolved issues, document remaining problems in `/app/results/validation_report.json` and set `overall_passed: false`.

### Common Fixes

| Issue | Fix |
|-------|-----|
| Missing sub-component | Add the missing wrapper (e.g. `SelectGroup` around `SelectItem`) |
| Wrong icon library | Replace icon import and icon name with project's `iconLibrary` equivalent |
| `space-y-*` used for layout | Replace with `flex flex-col gap-*` |
| Raw color class (e.g. `bg-blue-500`) | Replace with semantic token (e.g. `bg-primary`) |
| Manual `dark:` override | Remove and use semantic token |
| Hardcoded import path | Replace with project alias from `resolvedPaths` |
| Dialog/Sheet/Drawer missing Title | Add `DialogTitle`/`SheetTitle`/`DrawerTitle` (use `className="sr-only"` if visually hidden) |

## Step 11: Write Output Files

Write the required output files to `/app/results/`.

### `/app/results/components_added.md`

List all components that were searched, previewed, or added in this run:

```markdown
# Components Handled

| Component | Registry | Action | Status |
|-----------|----------|--------|--------|
| button    | @shadcn  | add    | success |
| dialog    | @shadcn  | add    | success |
```

### `/app/results/changes_summary.md`

Full summary of file changes:

```markdown
# Changes Summary

## Previewed (Dry-Run)
- <file>: <description of changes>

## Applied
- <file>: <description of changes>

## Import Fixes
- <file>: replaced <old-import> with <new-import>
```

## Step 12: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/components_added.md" \
  "$RESULTS_DIR/changes_summary.md" \
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

### Final Checklist

- [ ] All required output files exist and are non-empty
- [ ] All added components pass the review checklist in Step 8
- [ ] No Critical Rule violations remain
- [ ] Import aliases match the project's `resolvedPaths`
- [ ] Icon library matches project's `iconLibrary`
- [ ] `validation_report.json` has `overall_passed: true` (or documents why it is false)
- [ ] Verification script printed PASS for every line

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Prefer existing components.** Always `search` and check installed components before writing custom UI.
- **Never decode preset codes manually.** Use `npx shadcn@latest preset decode <code>` instead.
- **Always use `--dry-run` before updating.** The diff output prevents accidental overwrites.
- **Never skip `--dry-run` on updates.** Even small upstream changes can conflict with local modifications.
- **Check `base` field.** Whether the project uses `radix` or `base` affects prop names (`asChild` vs `render`, etc.).
- **Icon libraries differ.** Never assume `lucide-react`; always check `iconLibrary` from project context.
- **Tailwind v3 vs v4 matters.** CSS variable configuration is different; check `tailwindVersion` first.
- **`components.json` must exist** for `add`, `apply`, and `preset` commands to work.
