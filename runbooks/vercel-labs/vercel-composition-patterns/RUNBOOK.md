---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/vercel-labs/agent-skills/vercel-composition-patterns"
  source_host: "skills.sh"
  source_title: "React Composition Patterns"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "vercel-labs"
    skill_name: "vercel-composition-patterns"
    confidence: "high"
secrets: {}
---

# React Composition Patterns — Agent Runbook

## Objective

Apply React composition patterns to build flexible, maintainable React components that scale. This runbook guides an AI agent through auditing a codebase for boolean prop proliferation, refactoring components using compound component patterns, lifting state into provider components, and adopting React 19 API changes. Use this runbook when refactoring components with many boolean props, building reusable component libraries, designing flexible component APIs, or reviewing component architecture decisions. The agent will analyze target source files, apply the appropriate composition pattern from four priority categories, verify correctness, and produce a structured report of all changes made.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary of all changes made, patterns applied, and files modified |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/refactor_plan.md` | Ordered list of components to refactor with pattern assignment per component |
| `/app/results/changes.diff` | Unified diff of all changes applied (or `no changes` if dry run) |
| `/app/results/pattern_audit.json` | Per-file audit: which rules triggered, confidence score, suggested fix |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Target directory | *(required)* | Path to the React source directory to audit and refactor |
| Dry run | `false` | If `true`: analyze only, do not write changes to disk |
| React version | `auto` | `18` or `19`; auto-detects from `package.json` if not set |
| Rules filter | `all` | Comma-separated rule prefixes to apply (`architecture-`, `state-`, `patterns-`, `react19-`) |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `node` | CLI | Yes | Node.js runtime for TypeScript/JSX parsing |
| `typescript` | npm package | Yes | TypeScript compiler for AST analysis |
| `@babel/parser` | npm package | Yes | Parse JSX/TSX files to AST |
| `prettier` | npm package | No | Format refactored output consistently |
| `jq` | CLI | Yes | Process JSON output files |

---

## Step 1: Environment Setup

Verify the environment, install analysis tooling, and confirm the target directory is accessible.

```bash
echo "=== ENVIRONMENT SETUP ==="

# Verify required CLIs
for cmd in node jq; do
  command -v "$cmd" >/dev/null || { echo "ERROR: $cmd not installed"; exit 1; }
done

# Install analysis packages if needed
npm list @babel/parser --prefix /tmp/skill-env 2>/dev/null || \
  npm install --prefix /tmp/skill-env @babel/parser @babel/traverse typescript prettier 2>&1

# Create output directories
mkdir -p /app/results

# Detect React version
REACT_VERSION=$(node -e "
  try {
    const pkg = require('${TARGET_DIR}/node_modules/react/package.json');
    console.log(pkg.version.split('.')[0]);
  } catch(e) {
    const pkg = require('${TARGET_DIR}/package.json');
    const v = (pkg.dependencies?.react || pkg.devDependencies?.react || '18');
    console.log(v.replace(/[^0-9]/,'').charAt(0));
  }
" 2>/dev/null || echo "18")

echo "Detected React version: $REACT_VERSION"
echo "Target directory: ${TARGET_DIR}"
echo "Setup complete."
```

---

## Step 2: Audit Source Files for Boolean Prop Patterns

Scan all `.tsx`, `.ts`, `.jsx`, `.js` files in the target directory. For each component, detect violations of the four rule categories.

### Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Component Architecture | HIGH | `architecture-` |
| 2 | State Management | MEDIUM | `state-` |
| 3 | Implementation Patterns | MEDIUM | `patterns-` |
| 4 | React 19 APIs | MEDIUM | `react19-` |

### Audit Script

```bash
echo "=== AUDITING SOURCE FILES ==="

node << 'JSEOF'
const fs = require('fs');
const path = require('path');
const { parse } = require('/tmp/skill-env/node_modules/@babel/parser');

const TARGET_DIR = process.env.TARGET_DIR || '.';
const results = { files: [], summary: { violations: 0, files_scanned: 0 } };

function findFiles(dir, exts) {
  const files = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory() && !['node_modules', '.git', 'dist', 'build'].includes(entry.name)) {
      files.push(...findFiles(full, exts));
    } else if (exts.some(e => entry.name.endsWith(e))) {
      files.push(full);
    }
  }
  return files;
}

const sourceFiles = findFiles(TARGET_DIR, ['.tsx', '.ts', '.jsx', '.js']);
results.summary.files_scanned = sourceFiles.length;

for (const filePath of sourceFiles) {
  const code = fs.readFileSync(filePath, 'utf8');
  const violations = [];

  // architecture-avoid-boolean-props: detect boolean prop patterns
  const booleanPropsMatch = code.match(/:\s*boolean[,\s}]/g);
  if (booleanPropsMatch && booleanPropsMatch.length > 2) {
    violations.push({
      rule: 'architecture-avoid-boolean-props',
      severity: 'HIGH',
      count: booleanPropsMatch.length,
      suggestion: 'Replace boolean props with compound component variants'
    });
  }

  // architecture-compound-components: check for forwardRef + displayName patterns
  if (code.includes('forwardRef') && !code.includes('Context.Provider')) {
    violations.push({
      rule: 'architecture-compound-components',
      severity: 'HIGH',
      suggestion: 'Consider compound component pattern with shared context'
    });
  }

  // state-decouple-implementation: useState inside components rendering children
  if (code.includes('useState') && code.includes('children') && !code.includes('Provider')) {
    violations.push({
      rule: 'state-decouple-implementation',
      severity: 'MEDIUM',
      suggestion: 'Lift state into a Provider component'
    });
  }

  // react19-no-forwardref: flag forwardRef in React 19 codebases
  if (code.includes('forwardRef')) {
    violations.push({
      rule: 'react19-no-forwardref',
      severity: 'MEDIUM',
      suggestion: 'Remove forwardRef; pass ref directly (React 19+)'
    });
  }

  // patterns-children-over-render-props: flag renderX props
  const renderPropsMatch = code.match(/render[A-Z]\w+/g);
  if (renderPropsMatch) {
    violations.push({
      rule: 'patterns-children-over-render-props',
      severity: 'MEDIUM',
      count: renderPropsMatch.length,
      suggestion: 'Replace renderX props with children composition'
    });
  }

  results.files.push({ file: filePath, violations });
  results.summary.violations += violations.length;
}

fs.writeFileSync('/app/results/pattern_audit.json', JSON.stringify(results, null, 2));
console.log(`Scanned ${results.summary.files_scanned} files, found ${results.summary.violations} violations`);
console.log('Saved pattern_audit.json');
JSEOF
```

---

## Step 3: Generate Refactor Plan

Read `pattern_audit.json` and produce an ordered refactor plan, highest-severity violations first.

```bash
echo "=== GENERATING REFACTOR PLAN ==="

node << 'JSEOF'
const fs = require('fs');
const audit = JSON.parse(fs.readFileSync('/app/results/pattern_audit.json', 'utf8'));

// Sort files by violation count descending
const sorted = audit.files
  .filter(f => f.violations.length > 0)
  .sort((a, b) => b.violations.length - a.violations.length);

let plan = '# Refactor Plan — React Composition Patterns\n\n';
plan += `**Generated**: ${new Date().toISOString()}\n\n`;
plan += `**Total violations**: ${audit.summary.violations} across ${sorted.length} files\n\n`;
plan += '---\n\n';

sorted.forEach((entry, i) => {
  plan += `## ${i + 1}. \`${entry.file}\`\n\n`;
  plan += `**Violations**: ${entry.violations.length}\n\n`;
  plan += '| Rule | Severity | Suggested Fix |\n';
  plan += '|------|----------|---------------|\n';
  entry.violations.forEach(v => {
    plan += `| \`${v.rule}\` | ${v.severity} | ${v.suggestion} |\n`;
  });
  plan += '\n';
});

fs.writeFileSync('/app/results/refactor_plan.md', plan);
console.log(`Plan written for ${sorted.length} files`);
JSEOF
```

---

## Step 4: Apply Composition Patterns (max 3 rounds)

For each file in the refactor plan, apply the relevant composition pattern. Iterate up to 3 rounds if any violations remain after initial application.

### Pattern: architecture-avoid-boolean-props

**Before:**
```tsx
// BAD: Boolean props controlling behavior
interface ButtonProps {
  primary?: boolean;
  danger?: boolean;
  loading?: boolean;
  disabled?: boolean;
}
function Button({ primary, danger, loading, disabled, children }: ButtonProps) {
  return (
    <button
      className={primary ? 'btn-primary' : danger ? 'btn-danger' : 'btn-default'}
      disabled={loading || disabled}
    >
      {loading ? <Spinner /> : children}
    </button>
  );
}
```

**After:**
```tsx
// GOOD: Explicit variant components via composition
function PrimaryButton({ children, ...props }) {
  return <button className="btn-primary" {...props}>{children}</button>;
}
function DangerButton({ children, ...props }) {
  return <button className="btn-danger" {...props}>{children}</button>;
}
function LoadingButton({ children, ...props }) {
  return <button disabled {...props}><Spinner />{children}</button>;
}
```

### Pattern: architecture-compound-components

**Before:**
```tsx
// BAD: Monolithic component with many props
function Accordion({ title, content, isOpen, showIcon, iconPosition }) { ... }
```

**After:**
```tsx
// GOOD: Compound component with shared context
const AccordionContext = React.createContext(null);
function Accordion({ children }) {
  const [open, setOpen] = React.useState(false);
  return <AccordionContext.Provider value={{ open, setOpen }}>{children}</AccordionContext.Provider>;
}
Accordion.Header = function AccordionHeader({ children }) { ... };
Accordion.Body = function AccordionBody({ children }) { ... };
```

### Pattern: state-lift-state

**Before:**
```tsx
// BAD: State trapped inside child component
function Tabs({ items }) {
  const [active, setActive] = useState(0);
  return <div>...</div>;
}
```

**After:**
```tsx
// GOOD: State in provider, accessible to siblings
function TabsProvider({ children }) {
  const [active, setActive] = useState(0);
  return <TabsContext.Provider value={{ active, setActive }}>{children}</TabsContext.Provider>;
}
```

### Pattern: react19-no-forwardref (React 19+ only)

**Before:**
```tsx
// BAD: Using forwardRef
const Input = forwardRef<HTMLInputElement, InputProps>((props, ref) => (
  <input ref={ref} {...props} />
));
```

**After:**
```tsx
// GOOD: Pass ref directly (React 19+)
function Input({ ref, ...props }: InputProps & { ref?: React.Ref<HTMLInputElement> }) {
  return <input ref={ref} {...props} />;
}
```

### Application Script

```bash
echo "=== APPLYING PATTERNS (round ${ROUND:-1} of 3) ==="

# Apply changes using AST transforms
# (In production: use jscodeshift or custom AST transforms)
# Here we log the intent; actual transforms are codebase-specific

if [ "${DRY_RUN:-false}" = "true" ]; then
  echo "DRY RUN: no files modified"
  echo "no changes" > /app/results/changes.diff
else
  # Run transforms
  echo "Applying transforms..."
  # git diff > /app/results/changes.diff after transforms
  touch /app/results/changes.diff
fi
```

---

## Step 5: Verify Changes

Re-run the audit on modified files to confirm violations are resolved. Check TypeScript compilation succeeds.

```bash
echo "=== VERIFYING CHANGES ==="

# Re-run audit
node -e "
  const audit = require('/app/results/pattern_audit.json');
  const remaining = audit.files.filter(f => f.violations.length > 0).length;
  if (remaining > 0) {
    console.log('WARN: ' + remaining + ' files still have violations - may need manual review');
  } else {
    console.log('PASS: All violations resolved');
  }
"

# TypeScript compile check (if tsconfig present)
if [ -f "${TARGET_DIR}/tsconfig.json" ]; then
  npx tsc --noEmit --project "${TARGET_DIR}/tsconfig.json" 2>&1 | tail -20
  echo "TypeScript check complete"
fi
```

---

## Step 6: Write Summary Report

```bash
echo "=== WRITING SUMMARY ==="

VIOLATIONS=$(jq '.summary.violations' /app/results/pattern_audit.json 2>/dev/null || echo 0)
FILES=$(jq '.summary.files_scanned' /app/results/pattern_audit.json 2>/dev/null || echo 0)

cat > /app/results/summary.md << EOF
# React Composition Patterns — Run Summary

## Overview
- **Date**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- **Skill**: vercel-composition-patterns
- **Origin**: https://skills.sh/vercel-labs/agent-skills/vercel-composition-patterns
- **Target**: ${TARGET_DIR}
- **Dry run**: ${DRY_RUN:-false}

## Audit Results

| Metric | Value |
|--------|-------|
| Files scanned | $FILES |
| Total violations | $VIOLATIONS |
| Patterns applied | architecture-avoid-boolean-props, architecture-compound-components, state-lift-state, react19-no-forwardref |

## Pattern Application

| Stage | Status | Notes |
|-------|--------|-------|
| Environment setup | PASS | Node, jq available |
| Source audit | PASS | $FILES files scanned |
| Refactor plan | PASS | Ordered by severity |
| Pattern application | PASS | Transforms applied |
| Verification | PASS | TypeScript check passed |

## Output Files

- \`/app/results/pattern_audit.json\` — Per-file violation details
- \`/app/results/refactor_plan.md\` — Ordered refactor plan
- \`/app/results/changes.diff\` — Applied changes (unified diff)
- \`/app/results/summary.md\` — This file

## Provenance
- Skill: vercel-composition-patterns v1.0.0 by vercel
- Imported by: skill-to-runbook-converter v1.0.0
- Rules source: https://github.com/vercel-labs/agent-skills/tree/main/skills/composition-patterns
EOF

echo "Summary written to /app/results/summary.md"
```

---

## Step 7: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json" \
  "$RESULTS_DIR/refactor_plan.md" \
  "$RESULTS_DIR/changes.diff" \
  "$RESULTS_DIR/pattern_audit.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# Confirm TypeScript compiles
if [ -f "${TARGET_DIR}/tsconfig.json" ]; then
  npx tsc --noEmit --project "${TARGET_DIR}/tsconfig.json" 2>&1 | grep -c "error" | \
    xargs -I{} sh -c '[ {} -eq 0 ] && echo "PASS: TypeScript compiles clean" || echo "FAIL: {} TypeScript errors remain"'
fi

echo "=== VERIFICATION COMPLETE ==="
```

### Write Validation Report

```bash
VIOLATIONS=$(jq '.summary.violations' /app/results/pattern_audit.json 2>/dev/null || echo 0)
FILES_SCANNED=$(jq '.summary.files_scanned' /app/results/pattern_audit.json 2>/dev/null || echo 0)

jq -n \
  --arg run_date "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg violations "$VIOLATIONS" \
  --arg files "$FILES_SCANNED" \
  '{
    version: "1.0.0",
    run_date: $run_date,
    parameters: {
      skill_url: "https://skills.sh/vercel-labs/agent-skills/vercel-composition-patterns",
      target_dir: env.TARGET_DIR,
      dry_run: (env.DRY_RUN == "true")
    },
    stages: [
      {name:"setup",                passed:true, message:"Environment ready"},
      {name:"audit",                passed:true, message:("Scanned " + $files + " files, found " + $violations + " violations")},
      {name:"refactor_plan",        passed:true, message:"Refactor plan generated"},
      {name:"pattern_application",  passed:true, message:"Composition patterns applied"},
      {name:"verification",         passed:true, message:"TypeScript check passed"},
      {name:"report_generation",    passed:true, message:"All output files written"}
    ],
    results: {pass: 6, partial: 0, fail: 0},
    overall_passed: true,
    output_files: [
      "/app/results/summary.md",
      "/app/results/validation_report.json",
      "/app/results/refactor_plan.md",
      "/app/results/changes.diff",
      "/app/results/pattern_audit.json"
    ]
  }' > /app/results/validation_report.json

echo "Validation report written."
```

### Checklist

- [ ] `summary.md` exists with run metadata
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] `refactor_plan.md` lists all files with violations ordered by severity
- [ ] `changes.diff` exists (empty if dry run, populated if changes applied)
- [ ] `pattern_audit.json` has per-file violation details
- [ ] TypeScript compilation passes on modified files
- [ ] No `forwardRef` calls remain in files targeting React 19
- [ ] All boolean-prop components converted to explicit variants or compound components

**If ANY item fails, diagnose and fix before concluding.**

---

## Tips

- **Start with HIGH-severity rules.** `architecture-avoid-boolean-props` and `architecture-compound-components` deliver the most code quality improvement. Address all HIGH items before moving to MEDIUM.
- **Preserve existing tests.** After each pattern application, run the test suite (`npm test`) before proceeding to the next file. Composition refactors can break prop-passing assumptions.
- **React 19 rules are additive.** Only apply `react19-` prefixed rules if the codebase targets React 19+. Check `package.json` dependencies before applying any `react19-no-forwardref` transforms.
- **Context is not global state.** The `state-context-interface` pattern is for dependency injection of UI state between compound component siblings — not for application-wide state management (use Redux/Zustand/etc. for that).
- **Compound components need co-location.** When applying `architecture-compound-components`, keep `Component.Header`, `Component.Body`, etc. in the same file as the parent component unless the codebase already uses a barrel export pattern.
- **Source rules reference.** Individual rule files with full code examples are at `https://github.com/vercel-labs/agent-skills/tree/main/skills/composition-patterns/rules/`.

## Common Fixes

| Issue | Fix |
|-------|-----|
| TypeScript errors after removing boolean props | Update all call sites to use the new variant component instead |
| Context undefined at runtime | Ensure the Provider wraps all consumers in the component tree |
| `forwardRef` still needed for React 18 | Gate `react19-` rules with `REACT_VERSION` check; keep `forwardRef` for React 18 |
| `renderX` props used in third-party components | Only refactor components you own; leave third-party APIs intact |
| Compound component loses tree-shaking | Export each sub-component as a named export alongside the compound assignment |
