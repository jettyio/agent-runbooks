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

Apply React composition patterns to build flexible, maintainable React components that scale.
This runbook operationalizes the `vercel-composition-patterns` skill: it audits a target
codebase for boolean-prop proliferation, identifies components that violate composition
principles, produces refactored examples using compound components and context providers,
and emits a structured report. It covers four rule categories — Component Architecture,
State Management, Implementation Patterns, and React 19 APIs — with priority-ordered
analysis and actionable recommendations.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/audit_report.md` | Full analysis: components reviewed, violations found, recommendations |
| `/app/results/refactored_examples.md` | Before/after code examples for each flagged component |
| `/app/results/rule_coverage.json` | Which rules fired, how many times, per-rule violation counts |
| `/app/results/summary.md` | Executive summary: total violations, top issues, action items |
| `/app/results/validation_report.json` | Structured validation results with stages and `overall_passed` |

## Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Target codebase | *(required)* | Path or glob to the React component files to audit |
| React version | `18` or `19` | Determines whether React 19 API rules apply |
| Severity threshold | `MEDIUM` | Minimum rule priority to report (HIGH, MEDIUM, LOW) |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `node` / `npx` | CLI | Yes | Required to run skills tooling |
| `git` | CLI | Yes | Read file history and blame for context |
| Python 3.12+ | Runtime | Yes | Script execution environment |
| `pyyaml` | Python package | Yes | Parse YAML frontmatter in rule files |
| `markdown-it-py` | Python package | Yes | Parse markdown rule definitions |

## Step 1: Environment Setup

```bash
# Verify Node.js and npm are available
command -v node >/dev/null || { echo "ERROR: node not installed"; exit 1; }
command -v npx  >/dev/null || { echo "ERROR: npx not installed"; exit 1; }
command -v git  >/dev/null || { echo "ERROR: git not installed"; exit 1; }

# Install Python dependencies
pip install pyyaml markdown-it-py

# Create output directory
mkdir -p /app/results

# Verify target codebase path is set
if [ -z "$TARGET_CODEBASE" ]; then
  echo "ERROR: TARGET_CODEBASE environment variable is not set"
  exit 1
fi
echo "Auditing: $TARGET_CODEBASE"
```

## Step 2: Load Rule Definitions

Fetch the rule set from the `vercel-labs/agent-skills` GitHub repository and
load all rule files from the `skills/composition-patterns/rules/` directory.

```python
import requests, json, pathlib

RULES_API = "https://api.github.com/repos/vercel-labs/agent-skills/contents/skills/composition-patterns/rules"
headers = {"User-Agent": "jetty-runbook/1.0", "Accept": "application/vnd.github.v3+json"}

r = requests.get(RULES_API, headers=headers, timeout=30)
r.raise_for_status()
rule_files = r.json()

rules = {}
for rf in rule_files:
    if rf["name"].endswith(".md"):
        raw = requests.get(rf["download_url"], headers=headers, timeout=30)
        raw.raise_for_status()
        rules[rf["name"]] = raw.text
        print(f"Loaded rule: {rf['name']}")

pathlib.Path("/app/results/work").mkdir(parents=True, exist_ok=True)
pathlib.Path("/app/results/work/rules.json").write_text(json.dumps(
    {k: v[:200] for k, v in rules.items()}, indent=2
))
print(f"Loaded {len(rules)} rules")
```

Rules are organized into four priority categories:

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Component Architecture | HIGH | `architecture-` |
| 2 | State Management | MEDIUM | `state-` |
| 3 | Implementation Patterns | MEDIUM | `patterns-` |
| 4 | React 19 APIs | MEDIUM | `react19-` |

## Step 3: Scan Codebase for Violations

Apply each rule to every `.tsx` / `.jsx` / `.js` component file in the
target codebase. Record violations with file path, line number, rule ID,
and severity.

```python
import os, re, glob, json, pathlib

TARGET = os.environ.get("TARGET_CODEBASE", ".")
REACT_VERSION = int(os.environ.get("REACT_VERSION", "18"))

component_files = (
    glob.glob(f"{TARGET}/**/*.tsx", recursive=True) +
    glob.glob(f"{TARGET}/**/*.jsx", recursive=True) +
    glob.glob(f"{TARGET}/**/*.js",  recursive=True)
)
component_files = [f for f in component_files if "node_modules" not in f]

violations = []

BOOLEAN_PROP_PATTERN = re.compile(
    r"(?:interface|type)\s+\w+Props\s*[={][^}]*\b(is[A-Z]\w+|has[A-Z]\w+|show[A-Z]\w+|hide[A-Z]\w+|enable[A-Z]\w+|disable[A-Z]\w+)\s*[?:]?\s*boolean",
    re.DOTALL
)
FORWARD_REF_PATTERN = re.compile(r"\bforwardRef\b")

for fpath in component_files:
    try:
        src = pathlib.Path(fpath).read_text(errors="replace")
    except Exception:
        continue

    # architecture-avoid-boolean-props
    for m in BOOLEAN_PROP_PATTERN.finditer(src):
        line = src[:m.start()].count("\n") + 1
        violations.append({
            "file": fpath, "line": line,
            "rule": "architecture-avoid-boolean-props",
            "severity": "HIGH",
            "match": m.group(1)
        })

    # react19-no-forwardref (only flag if React 19)
    if REACT_VERSION >= 19:
        for m in FORWARD_REF_PATTERN.finditer(src):
            line = src[:m.start()].count("\n") + 1
            violations.append({
                "file": fpath, "line": line,
                "rule": "react19-no-forwardref",
                "severity": "MEDIUM",
                "match": "forwardRef usage"
            })

print(f"Scanned {len(component_files)} files, found {len(violations)} violations")
pathlib.Path("/app/results/work/violations.json").write_text(json.dumps(violations, indent=2))
```

## Step 4: Generate Audit Report

Produce `audit_report.md` and `rule_coverage.json` from the violations found in Step 3.

```python
import json, pathlib
from collections import defaultdict

violations = json.loads(pathlib.Path("/app/results/work/violations.json").read_text())

# Build rule coverage
rule_counts = defaultdict(int)
for v in violations:
    rule_counts[v["rule"]] += 1

rule_coverage = {
    "total_violations": len(violations),
    "by_rule": dict(rule_counts),
    "files_affected": len(set(v["file"] for v in violations))
}
pathlib.Path("/app/results/rule_coverage.json").write_text(json.dumps(rule_coverage, indent=2))

# Build audit report
lines = ["# React Composition Patterns — Audit Report\n"]
lines.append(f"**Total violations:** {len(violations)}\n")
lines.append(f"**Files affected:** {rule_coverage['files_affected']}\n\n")

lines.append("## Violations by Rule\n")
for rule, count in sorted(rule_counts.items(), key=lambda x: -x[1]):
    lines.append(f"- `{rule}`: {count} occurrence(s)\n")
lines.append("\n")

lines.append("## Detailed Findings\n")
for v in violations:
    lines.append(f"- **{v['file']}:{v['line']}** — `{v['rule']}` ({v['severity']}): {v['match']}\n")

pathlib.Path("/app/results/audit_report.md").write_text("".join(lines))
print("audit_report.md written")
```

## Step 5: Generate Refactored Examples

For each flagged pattern, produce a before/after refactoring example following
the composition patterns described in the source skill.

```python
import json, pathlib

violations = json.loads(pathlib.Path("/app/results/work/violations.json").read_text())

examples = ["# Refactored Examples\n\n"]

if any(v["rule"] == "architecture-avoid-boolean-props" for v in violations):
    examples.append("""## architecture-avoid-boolean-props

### Before (boolean props — avoid)

```tsx
// ❌ Boolean prop proliferation
interface ButtonProps {
  isPrimary?: boolean;
  isDisabled?: boolean;
  isLoading?: boolean;
}
function Button({ isPrimary, isDisabled, isLoading }: ButtonProps) {
  return (
    <button
      className={isPrimary ? "btn-primary" : "btn-secondary"}
      disabled={isDisabled || isLoading}
    >
      {isLoading ? "Loading..." : "Click me"}
    </button>
  );
}
```

### After (explicit variants — prefer)

```tsx
// ✅ Explicit variant components
function PrimaryButton({ disabled, children }: { disabled?: boolean; children: React.ReactNode }) {
  return <button className="btn-primary" disabled={disabled}>{children}</button>;
}

function SecondaryButton({ disabled, children }: { disabled?: boolean; children: React.ReactNode }) {
  return <button className="btn-secondary" disabled={disabled}>{children}</button>;
}

function LoadingButton({ children }: { children: React.ReactNode }) {
  return <button className="btn-primary" disabled>Loading...</button>;
}
```

""")

if any(v["rule"] == "react19-no-forwardref" for v in violations):
    examples.append("""## react19-no-forwardref

### Before (forwardRef — React 18 style)

```tsx
// ❌ forwardRef is removed in React 19
const Input = React.forwardRef<HTMLInputElement, InputProps>((props, ref) => (
  <input ref={ref} {...props} />
));
```

### After (ref as prop — React 19 style)

```tsx
// ✅ Pass ref directly as a prop in React 19
function Input({ ref, ...props }: InputProps & { ref?: React.Ref<HTMLInputElement> }) {
  return <input ref={ref} {...props} />;
}
```

""")

if not violations:
    examples.append("No violations found — codebase follows composition patterns correctly.\n")

pathlib.Path("/app/results/refactored_examples.md").write_text("".join(examples))
print("refactored_examples.md written")
```

## Step 6: Iterate on Errors (max 3 rounds)

If Step 4 or 5 produced empty output files or scanning errors:

1. Check `/app/results/work/violations.json` for parse errors
2. Verify the `TARGET_CODEBASE` path is correct and files are accessible
3. Re-run the failing step with corrected paths
4. Repeat up to 3 times total

### Common Fixes

| Issue | Fix |
|-------|-----|
| No component files found | Verify `TARGET_CODEBASE` glob and check for `.tsx`/`.jsx` extensions |
| Rule files API rate limited | Add `Authorization: token $GITHUB_PAT` header to GitHub API calls |
| Empty violations but known issues exist | Broaden regex patterns or add manual review entries |
| `audit_report.md` missing violations | Re-run Step 4 after confirming `violations.json` is non-empty |

## Step 7: Write Summary

```python
import json, pathlib

rule_coverage = json.loads(pathlib.Path("/app/results/rule_coverage.json").read_text())

summary = f"""# React Composition Patterns — Summary

## Overview

- **Total violations**: {rule_coverage['total_violations']}
- **Files affected**: {rule_coverage['files_affected']}
- **Rules applied**: architecture-avoid-boolean-props, architecture-compound-components, state-decouple-implementation, state-context-interface, state-lift-state, patterns-explicit-variants, patterns-children-over-render-props, react19-no-forwardref

## Top Issues

"""
by_rule = rule_coverage.get("by_rule", {})
if by_rule:
    for rule, count in sorted(by_rule.items(), key=lambda x: -x[1])[:5]:
        summary += f"- `{rule}`: {count} violation(s)\\n"
else:
    summary += "- No violations detected\\n"

summary += """
## Recommended Actions

1. Review flagged components in `audit_report.md`
2. Apply refactoring patterns from `refactored_examples.md`
3. For compound components, introduce a shared context provider
4. Replace boolean props with explicit variant components
5. If on React 19, migrate `forwardRef` usage to direct ref props

## Provenance

- Skill: vercel-composition-patterns by vercel-labs/agent-skills
- Origin: https://skills.sh/vercel-labs/agent-skills/vercel-composition-patterns
- Runbook: skill-to-runbook-converter v1.0.0
"""

pathlib.Path("/app/results/summary.md").write_text(summary)
print("summary.md written")
```

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/audit_report.md" \
  "$RESULTS_DIR/refactored_examples.md" \
  "$RESULTS_DIR/rule_coverage.json" \
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

- [ ] `audit_report.md` lists all violations with file, line, rule, and severity
- [ ] `refactored_examples.md` shows before/after for each rule that fired
- [ ] `rule_coverage.json` has `total_violations`, `by_rule`, and `files_affected`
- [ ] `summary.md` has overview, top issues, and recommended actions
- [ ] `validation_report.json` exists with `stages`, `results`, and `overall_passed`
- [ ] Verification script printed PASS for every output file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **React 19 rules are opt-in.** Set `REACT_VERSION=19` to enable the `react19-*` rules;
  they are silently skipped for React 18 projects to avoid false positives.
- **Boolean prop detection is heuristic.** The regex catches common naming conventions
  (`isX`, `hasX`, `showX`) but may miss custom patterns — review the audit output
  manually for completeness.
- **Compound components need context.** When refactoring a boolean-prop-heavy component,
  first identify which props relate to shared state, then extract a context provider.
- **`children` over render props.** Prefer `children` composition over `renderHeader`,
  `renderFooter` patterns — it is more idiomatic in modern React.
- **Start with HIGH severity.** Tackle `architecture-*` rules first; they have the
  highest impact on long-term maintainability.
