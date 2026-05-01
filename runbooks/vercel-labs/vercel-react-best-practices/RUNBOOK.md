---
version: 1.0.0
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
  source_host: skills.sh
  source_title: Vercel React Best Practices
  imported_at: '2026-05-01T02:22:00Z'
  imported_by: skill-to-runbook-converter@1.0.0
  attribution:
    collection_or_org: vercel-labs
    skill_name: vercel-react-best-practices
    confidence: high
---
# Vercel React Best Practices — Agent Runbook

## Objective

Apply Vercel Engineering's comprehensive React and Next.js performance optimization guidelines when writing, reviewing, or refactoring React/Next.js code. This runbook covers 70 rules across 8 priority categories — from critical waterfall elimination and bundle-size optimization through server-side performance, client-side data fetching, re-render reduction, rendering efficiency, JavaScript micro-optimizations, and advanced patterns. Use it to systematically audit a codebase, produce a prioritized set of code changes, and generate a structured findings report.

Reference these guidelines when:
- Writing new React components or Next.js pages
- Implementing data fetching (client or server-side)
- Reviewing code for performance issues
- Refactoring existing React/Next.js code
- Optimizing bundle size or load times

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files before the task is considered complete.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary with audit results, rules applied, and any issues found |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/audit_findings.md` | Detailed list of rules triggered, code locations, and recommended fixes |
| `/app/results/applied_changes.diff` | Unified diff of all code changes applied (or empty if review-only mode) |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Target path | *(required)* | Path to the React/Next.js codebase to audit |
| Mode | `review` | `review` (report only) or `apply` (make changes) |
| Categories | `all` | Comma-separated list of rule category prefixes to run |
| Max fixes per category | `10` | Maximum number of automated fixes to apply per category |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `node` / `npm` | CLI | Yes | Required to analyze Next.js/React project and run build tools |
| `next` | npm package | Yes | Next.js framework (project dependency) |
| `react` | npm package | Yes | React library (project dependency) |
| `@next/bundle-analyzer` | npm package | Optional | Bundle size analysis for `bundle-` category rules |
| `swr` | npm package | Optional | Recommended for `client-` category rules |

---

## Step 1: Environment Setup

```bash
echo "=== Environment Setup ==="
# Verify required tools
command -v node >/dev/null || { echo "ERROR: node not installed"; exit 1; }
command -v npm  >/dev/null || { echo "ERROR: npm not installed"; exit 1; }

# Create output directories
mkdir -p /app/results

# Verify the target codebase exists and is a React/Next.js project
TARGET="${TARGET_PATH:-$(pwd)}"
if [ ! -f "$TARGET/package.json" ]; then
  echo "ERROR: No package.json found at $TARGET"
  exit 1
fi

# Check for React/Next.js dependencies
if ! grep -q '"react"\|"next"' "$TARGET/package.json"; then
  echo "WARNING: No react or next dependency found — ensure this is a React project"
fi

echo "Target: $TARGET"
echo "Node: $(node --version)"
echo "Setup complete."
```

---

## Step 2: Audit Waterfall Elimination (CRITICAL — Priority 1)

Apply the `async-` rule category. These are the highest-impact rules.

Rules to check:
- `async-cheap-condition-before-await` — Check cheap sync conditions before awaiting
- `async-defer-await` — Move await into branches where actually used
- `async-parallel` — Use `Promise.all()` for independent operations
- `async-dependencies` — Use `better-all` for partial dependencies
- `async-api-routes` — Start promises early, await late in API routes
- `async-suspense-boundaries` — Use Suspense to stream content

```bash
echo "=== Auditing: Eliminating Waterfalls (async-) ==="
# Scan for sequential awaits that could be parallelized
grep -rn "await " "$TARGET" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
  | grep -v "node_modules" | head -50

# Detect files with multiple top-level awaits (waterfall candidates)
grep -rl "await " "$TARGET" --include="*.ts" --include="*.tsx" \
  | grep -v "node_modules" | xargs -I{} sh -c 'count=$(grep -c "await " "{}"); [ "$count" -gt 2 ] && echo "$count {}"' \
  | sort -rn | head -20
```

Document each finding with file path, line number, rule ID, and suggested fix in `/app/results/audit_findings.md`.

---

## Step 3: Audit Bundle Size (CRITICAL — Priority 2)

Apply the `bundle-` rule category.

Rules to check:
- `bundle-barrel-imports` — Import directly, avoid barrel files
- `bundle-analyzable-paths` — Prefer statically analyzable import paths
- `bundle-dynamic-imports` — Use `next/dynamic` for heavy components
- `bundle-defer-third-party` — Load analytics/logging after hydration
- `bundle-conditional` — Load modules only when feature is activated
- `bundle-preload` — Preload on hover/focus for perceived speed

```bash
echo "=== Auditing: Bundle Size (bundle-) ==="
# Find barrel import patterns (index.ts re-exports)
grep -rn "from '.*index'" "$TARGET" --include="*.ts" --include="*.tsx" \
  | grep -v "node_modules" | head -30

# Find heavy third-party imports that should use next/dynamic
grep -rn "^import " "$TARGET" --include="*.tsx" --include="*.jsx" \
  | grep -v "node_modules" | head -50
```

---

## Step 4: Audit Server-Side Performance (HIGH — Priority 3)

Apply the `server-` rule category.

Rules to check:
- `server-cache-react` — Use `React.cache()` for per-request deduplication
- `server-cache-lru` — Use LRU cache for cross-request caching
- `server-dedup-props` — Avoid duplicate serialization in RSC props
- `server-hoist-static-io` — Hoist static I/O (fonts, logos) to module level
- `server-no-shared-module-state` — Avoid module-level mutable request state in RSC/SSR
- `server-serialization` — Minimize data passed to client components
- `server-parallel-fetching` — Restructure components to parallelize fetches
- `server-after-nonblocking` — Use `after()` for non-blocking operations

```bash
echo "=== Auditing: Server-Side Performance (server-) ==="
# Find server components with un-cached fetch calls
grep -rn "async function\|async const" "$TARGET/app" --include="*.tsx" --include="*.ts" \
  | grep -v "node_modules" | head -30

# Find module-level mutable state in server components
grep -rn "^let \|^var " "$TARGET/app" \
  --include="*.ts" --include="*.tsx" | grep -v "node_modules" | head -20
```

---

## Step 5: Audit Client-Side Data Fetching (MEDIUM-HIGH — Priority 4)

Apply the `client-` rule category.

Rules to check:
- `client-swr-dedup` — Use SWR for automatic request deduplication
- `client-event-listeners` — Deduplicate global event listeners
- `client-passive-event-listeners` — Use passive listeners for scroll/wheel/touch
- `client-localstorage-schema` — Version and minimize localStorage data

```bash
echo "=== Auditing: Client-Side Data Fetching (client-) ==="
# Find useEffect-based fetches that should use SWR
grep -rn "useEffect" "$TARGET" --include="*.tsx" --include="*.jsx" \
  | grep "fetch\|axios" | grep -v "node_modules" | head -30

# Find addEventListener without passive option for scroll/wheel/touch
grep -rn "addEventListener" "$TARGET" --include="*.ts" --include="*.tsx" \
  | grep "scroll\|wheel\|touchstart" | grep -v "passive" | grep -v "node_modules" | head -20
```

---

## Step 6: Audit Re-render Optimization (MEDIUM — Priority 5)

Apply the `rerender-` rule category.

Key rules:
- `rerender-defer-reads` — Don't subscribe to state only used in callbacks
- `rerender-memo` — Extract expensive work into memoized components
- `rerender-dependencies` — Use primitive dependencies in effects
- `rerender-lazy-state-init` — Pass function to `useState` for expensive initial values
- `rerender-no-inline-components` — Don't define components inside components

```bash
echo "=== Auditing: Re-render Optimization (rerender-) ==="
# Find potential inline component definitions
grep -rn "= (" "$TARGET" --include="*.tsx" --include="*.jsx" \
  | grep -v "node_modules" | grep "return\|=>" | head -30
```

---

## Step 7: Audit Rendering Performance (MEDIUM — Priority 6)

Apply the `rendering-` rule category.

Key rules:
- `rendering-hoist-jsx` — Extract static JSX outside components
- `rendering-conditional-render` — Use ternary, not `&&` for conditionals with falsy values
- `rendering-hydration-no-flicker` — Use inline script for client-only data
- `rendering-activity` — Use `Activity` component for show/hide

```bash
echo "=== Auditing: Rendering Performance (rendering-) ==="
# Find && conditional renders that might need to be ternary
grep -rn "{.*&&.*<" "$TARGET" --include="*.tsx" --include="*.jsx" \
  | grep -v "node_modules" | head -30
```

---

## Step 8: Audit JavaScript Performance (LOW-MEDIUM — Priority 7)

Apply the `js-` rule category.

Key rules:
- `js-index-maps` — Build Map for repeated lookups
- `js-cache-property-access` — Cache object properties in loops
- `js-combine-iterations` — Combine multiple filter/map into one loop
- `js-early-exit` — Return early from functions

```bash
echo "=== Auditing: JavaScript Performance (js-) ==="
# Find chained filter/map that could be combined
grep -rn "\.filter(" "$TARGET" --include="*.ts" --include="*.tsx" \
  | grep -v "node_modules" | head -20
```

---

## Step 9: Audit Advanced Patterns (LOW — Priority 8)

Apply the `advanced-` rule category.

Key rules:
- `advanced-event-handler-refs` — Store event handlers in refs
- `advanced-init-once` — Initialize app once per app load
- `advanced-use-latest` — `useLatest` for stable callback refs

```bash
echo "=== Auditing: Advanced Patterns (advanced-) ==="
grep -rn "useCallback" "$TARGET" --include="*.tsx" \
  | grep -v "node_modules" | head -20
```

---

## Step 10: Iterate on Errors (max 3 rounds)

If any audit step produces errors or fails to scan correctly:

1. Read the specific error from the step output
2. Apply targeted fix:
   - If files not found: verify `TARGET_PATH` is set correctly
   - If grep syntax error: simplify the pattern and re-run
   - If missing tool: install via `npm install -g` or `apt-get`
3. Re-run the affected step
4. Repeat up to 3 times total

After 3 rounds, document remaining failures in `summary.md` and mark `overall_passed=false` in `validation_report.json`.

---

## Step 11: Write Audit Findings

Compile all findings into `/app/results/audit_findings.md`:

```markdown
# React Best Practices Audit Findings

## Summary
- Target: <path>
- Rules checked: <N>
- Findings: <count>

## Findings by Category

### async- (Waterfall Elimination) — CRITICAL
| Rule | File | Line | Description | Severity |
|------|------|------|-------------|----------|
| ... | ... | ... | ... | CRITICAL |

### bundle- (Bundle Size) — CRITICAL
...
```

If mode is `apply`, generate a unified diff of all applied changes:
```bash
git diff > /app/results/applied_changes.diff
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
  "$RESULTS_DIR/audit_findings.md" \
  "$RESULTS_DIR/applied_changes.diff"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] `summary.md` exists with overview of all audit categories and finding counts
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] `audit_findings.md` exists with findings organized by rule category
- [ ] `applied_changes.diff` exists (may be empty for review-only mode)
- [ ] All 8 rule categories were evaluated (or skipped with reason documented)
- [ ] Critical (`async-`, `bundle-`) findings are flagged and prioritized
- [ ] Verification script printed PASS for every line

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **Start with CRITICAL rules.** Fixing waterfall and bundle issues typically yields 2–5x performance improvements before touching other categories.
- **Use the Quick Reference table** in the source SKILL.md to quickly identify which rule prefix applies to a given pattern.
- **Individual rule files** at `rules/<rule-id>.md` in the `vercel-labs/agent-skills` repository contain detailed before/after code examples.
- **Full compiled document** is available at `AGENTS.md` in the same repository for an expanded explanation of every rule.
- **Run bundle analysis** with `ANALYZE=true npm run build` when using `@next/bundle-analyzer` to get a visual breakdown before and after `bundle-` fixes.
- **Server components** deserve special attention: module-level mutable state (`server-no-shared-module-state`) can cause subtle request-level data leaks in RSC/SSR contexts.

## Common Fixes

| Issue | Fix |
|-------|-----|
| Sequential `await` calls | Wrap independent calls in `Promise.all([...])` (`async-parallel`) |
| Barrel file imports | Import directly from source file (`bundle-barrel-imports`) |
| `useEffect`-based fetch | Replace with SWR `useSWR` hook (`client-swr-dedup`) |
| Inline component definitions | Move to module-level const (`rerender-no-inline-components`) |
| `&&` conditional render | Replace with ternary `? <Component /> : null` (`rendering-conditional-render`) |
| Non-passive scroll listener | Add `{ passive: true }` option (`client-passive-event-listeners`) |
| Repeated `filter().map()` | Combine into single `reduce` or `flatMap` (`js-combine-iterations`) |
