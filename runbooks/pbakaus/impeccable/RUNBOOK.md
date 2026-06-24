---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: anthropic/claude-sonnet-4.6
model_provider: openrouter
snapshot: python312-uv
# Operation-aware headline deliverable: an `audit` run surfaces audit_report.md;
# a `polish` run surfaces the cleaned-up polished.html. Only files actually
# written by the chosen operation are surfaced, in declaration order.
primary_outputs:
  - polished.html
  - audit_report.md
origin:
  url: "https://github.com/pbakaus/impeccable"
  source_host: "github.com"
  source_title: "impeccable — production-grade frontend design skill"
  imported_at: "2026-06-07T00:00:00Z"
  imported_by: "hand-authored@jetty (de-slop capability)"
  license: "Apache-2.0"
  attribution:
    collection_or_org: "pbakaus"
    skill_name: "impeccable"
    confidence: "high"
  # Provenance carried forward from the upstream NOTICE:
  notice: >-
    impeccable © 2025-2026 Paul Bakaus, Apache-2.0. Builds on Anthropic's
    frontend-design skill (Apache-2.0, © 2025 Anthropic, PBC). Typography
    reference incorporates additions from ehmo's typecraft-guide-skill.
secrets: {}
---

# Impeccable — De-slop a UI — Agent Runbook

## Objective

Detect and remove **AI-slop** from a frontend artifact — the visual and copy tells
that make an interface read as machine-generated: purple→cyan gradients, gradient
text, Inter/Roboto everywhere, side-tab accent borders, nested cards, dark-mode
glows, bounce easing, broken/placeholder images, and SaaS buzzword copy. This
runbook wraps the deterministic detector that ships with [Paul Bakaus's
`impeccable`](https://github.com/pbakaus/impeccable) skill (`impeccable detect`) and
uses it as both the **finder** and the **grader**: it scans an HTML/CSS/JSX file (or
directory, or live URL), reports every anti-pattern, and — in `polish` mode —
rewrites the artifact to remove them, then re-scans to **prove** the page now scans
clean. Because the same tool that finds the slop also verifies the fix, evaluation is
fully programmatic: the polish pass succeeds only when a re-scan exits `0` (zero
anti-patterns) with no new findings introduced. Worked examples — a sloppy SaaS hero
audited, then the same hero and a pricing section polished to zero — ship in
`examples/`.

## Requested Operation (READ FIRST)

**Operation:** {{operation}}

Perform **only** this operation:

- **`audit`** — scan the target and produce a findings report. **Change nothing.**
  Deliverables: `audit_report.json` + `audit_report.md`.
- **`polish`** — scan, then edit the target to remove every finding, then re-scan to
  confirm zero. Deliverables: the cleaned artifact (`polished.html` for a single
  file) + `audit_before.json` + `audit_after.json` + `before_after.md`.

If no operation is given, default to **`audit`** (the safe, read-only path).

## REQUIRED OUTPUT FILES

**Always** write these two to `{{results_dir}}` (every operation):

| File | Description |
|------|-------------|
| `{{results_dir}}/summary.md` | Executive summary: operation, target, finding counts, before/after, any caveats |
| `{{results_dir}}/validation_report.json` | Structured validation with `stages`, `results`, and `overall_passed` |

**Then** write **only** the deliverable(s) for the requested operation:

| Operation | Deliverable(s) in `{{results_dir}}` |
|-----------|-------------------------------------|
| `audit` | `audit_report.json` (raw findings + counts) **and** `audit_report.md` (human report) |
| `polish` | `polished.html` (the cleaned artifact) **and** `audit_before.json` **and** `audit_after.json` **and** `before_after.md` |

The task is NOT complete until `summary.md`, `validation_report.json`, and the
operation's deliverable(s) all exist and are non-empty. **Do not** run the other
operation's work — an `audit` request must NOT modify the target or emit a
`polished.html`.

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|-------------------|---------|-------------|
| Results directory | `{{results_dir}}` | `/app/results` | Output directory for all results |
| Target | `{{target}}` | *(required)* | The artifact to de-slop: an uploaded HTML/CSS/JSX/TSX file (lands in `/app/assets/`), a directory, or an `http(s)://` URL |
| Operation | `{{operation}}` | `audit` | `audit` (report only) or `polish` (fix + re-scan to zero) |
| Provider tells | `{{provider_tells}}` | `none` | `none`, `gpt`, or `gemini` — also report that provider's signature tells (off by default; passed through to `impeccable detect --gpt/--gemini`) |
| Max polish rounds | `{{max_polish_rounds}}` | `3` | Max fix→re-scan iterations before stopping (polish only) |
| Output basename | `{{output_basename}}` | `polished` | Label for the run (the primary output is always `polished.html`) |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| Node.js ≥ 24 | Runtime | Yes | `impeccable` requires Node ≥ 24 (`engines.node >=24`). Step 1 verifies and installs if absent |
| `impeccable` | npm package | Yes | The detector + skill. Resolved via `npx impeccable@latest`; clone fallback pinned to a commit SHA (Step 1) |
| `npx` / `npm` | CLI | Yes | Resolve and run `impeccable detect` |
| `git` | CLI | Conditional | Only for the clone fallback when the npm registry is unreachable |
| Chromium / Puppeteer | Runtime | Conditional | Only for **URL** targets (browser-render scan); file/dir targets use the static-HTML + regex engines and need no browser |

---

## Step 1: Environment Setup

Ensure Node ≥ 24, resolve the `impeccable` CLI, and resolve the target.

```bash
set -e
mkdir -p {{results_dir}}

# --- Node ≥ 24 ---
NODE_MAJOR=$(node -v 2>/dev/null | sed -E 's/^v([0-9]+).*/\1/' || echo 0)
if [ "${NODE_MAJOR:-0}" -lt 24 ]; then
  echo "Node ${NODE_MAJOR} < 24 — installing Node 24"
  curl -fsSL https://deb.nodesource.com/setup_24.x | bash - >/dev/null 2>&1 && apt-get install -y nodejs >/dev/null 2>&1 \
    || (curl -fsSL https://fnm.vercel.app/install | bash && export PATH="$HOME/.local/share/fnm:$PATH" && eval "$(fnm env)" && fnm install 24 && fnm use 24)
fi
echo "node: $(node -v)"

# --- Resolve the impeccable detector ---
# Primary: run straight from npm. Verify it answers before relying on it.
if npx --yes impeccable@latest detect --help >/dev/null 2>&1; then
  IMPECCABLE="npx --yes impeccable@latest detect"
else
  # Fallback: clone the repo pinned to a known-good SHA and run the bundled CLI.
  git clone --depth 1 https://github.com/pbakaus/impeccable /tmp/impeccable
  git -C /tmp/impeccable fetch --depth 1 origin 1aedbcf538e3fa6694ccbf00294cc18e59ba1f21 2>/dev/null || true
  IMPECCABLE="node /tmp/impeccable/cli/bin/cli.js detect"
fi
echo "detector: $IMPECCABLE"
echo "$IMPECCABLE" > {{results_dir}}/.impeccable_cmd   # reused by later steps
```

**Resolve the target** (`{{target}}`):

```bash
# Uploaded files land in /app/assets/. Prefer an explicit {{target}}; otherwise
# pick the first HTML-ish asset.
TARGET="{{target}}"
case "$TARGET" in
  http://*|https://*) : ;;                                  # URL — scanned in browser mode
  "" )                                                       # nothing passed — discover an upload
    TARGET=$(ls /app/assets/*.html /app/assets/*.htm 2>/dev/null | head -1)
    [ -z "$TARGET" ] && TARGET=$(ls /app/assets/*.{css,jsx,tsx,vue,svelte} 2>/dev/null | head -1) ;;
  /*) : ;;                                                   # absolute path
  *) [ -e "/app/assets/$TARGET" ] && TARGET="/app/assets/$TARGET" ;;
esac
[ -z "$TARGET" ] && { echo "ERROR: no target resolved (pass a file, dir, or URL)"; exit 1; }
echo "$TARGET" > {{results_dir}}/.target
echo "target: $TARGET"
```

If no target can be resolved, fail fast and write `validation_report.json` with
`stages[0].passed=false` naming the missing input.

---

## Step 2: Baseline Scan (every operation)

Run the detector once and capture both the findings JSON **and the exit code** —
`impeccable detect` exits **`2`** when anti-patterns are present and **`0`** when the
target is clean. That exit code is the ground truth this runbook is built on.

```bash
IMPECCABLE=$(cat {{results_dir}}/.impeccable_cmd)
TARGET=$(cat {{results_dir}}/.target)

PROV=""
case "{{provider_tells}}" in gpt) PROV="--gpt" ;; gemini) PROV="--gemini" ;; esac

set +e
$IMPECCABLE --json $PROV "$TARGET" > {{results_dir}}/audit_before.json
SCAN_EXIT=$?
set -e
echo "$SCAN_EXIT" > {{results_dir}}/.before_exit

COUNT=$(python3 -c "import json;print(len(json.load(open('{{results_dir}}/audit_before.json'))))")
echo "baseline: $COUNT anti-pattern(s), detector exit $SCAN_EXIT"
```

Each finding has the shape:

```json
{ "antipattern": "side-tab", "name": "Side-tab accent border",
  "description": "Thick colored border on one side of a card …",
  "severity": "warning", "file": "/app/assets/input.html",
  "line": 36, "snippet": "border-left: 4px solid #7c3aed" }
```

---

## Step 3: Execute the Operation

### 3a — `audit` (report only; change nothing)

Group the findings by rule and category, then emit the two reports.

```python
import json, pathlib, collections

R = pathlib.Path("{{results_dir}}")
findings = json.loads((R / "audit_before.json").read_text())
exit_code = int((R / ".before_exit").read_text().strip())

SLOP = {"side-tab","border-accent-on-rounded","overused-font","single-font",
        "flat-type-hierarchy","gradient-text","ai-color-palette","cream-palette",
        "nested-cards","monotonous-spacing","bounce-easing","dark-glow",
        "icon-tile-stack","italic-serif-display","hero-eyebrow-chip",
        "repeated-section-kickers","numbered-section-markers","em-dash-overuse",
        "marketing-buzzword","aphoristic-cadence","oversized-h1","extreme-negative-tracking"}
cat = lambda r: "slop" if r in SLOP else "quality"

by_rule = dict(sorted(collections.Counter(f["antipattern"] for f in findings).items()))
by_cat  = dict(sorted(collections.Counter(cat(f["antipattern"]) for f in findings).items()))

(R / "audit_report.json").write_text(json.dumps({
    "tool": "impeccable detect",
    "source": "https://github.com/pbakaus/impeccable",
    "target": str((R / ".target").read_text().strip()),
    "exit_code": exit_code,
    "finding_count": len(findings),
    "by_category": by_cat,
    "by_rule": by_rule,
    "findings": findings,
}, indent=2, ensure_ascii=False) + "\n")

verdict = ("reads as AI-generated — see tells" if by_cat.get("slop") else
           ("quality issues only" if findings else "clean — no anti-patterns detected"))
lines = [f"# Impeccable audit — `{(R/'.target').read_text().strip()}`", "",
         f"**Findings:** {len(findings)} "
         f"({by_cat.get('slop',0)} AI-slop, {by_cat.get('quality',0)} quality)  ",
         f"**Verdict:** {verdict}", "",
         "| # | Rule | Category | Line | Snippet |",
         "|---|------|----------|------|---------|"]
for i, f in enumerate(findings, 1):
    snip = str(f.get("snippet","")).replace("|","\\|")[:48]
    lines.append(f"| {i} | `{f['antipattern']}` | {cat(f['antipattern'])} | {f.get('line') or '—'} | `{snip}` |")
for i, f in enumerate(findings, 1):
    lines += ["", f"### {i}. {f['name']} (`{f['antipattern']}`)",
              f"- **Location:** line {f.get('line') or '—'} — `{f.get('snippet','')}`",
              f"- **Why it matters:** {f['description']}"]
if not findings:
    lines.append("\n_No anti-patterns detected. The detector exited 0._")
(R / "audit_report.md").write_text("\n".join(lines) + "\n")
print(f"audit: {len(findings)} findings written")
```

Then skip to Step 5 (no fixes in `audit` mode).

### 3b — `polish` (fix → re-scan, max `{{max_polish_rounds}}` rounds)

Read the artifact and **fix every finding**, guided by the rule's `description` and
the **De-slop fix reference** below. Write the cleaned file to
`{{results_dir}}/polished.html`, then re-scan it. Repeat until the re-scan exits `0`
or `{{max_polish_rounds}}` rounds are spent.

> Fix the *root cause*, not the symptom. Removing the gradient text by deleting the
> headline is not a fix. Replace slop with a deliberate, production-grade choice that
> a designer would defend (see the upstream skill's design rules).

**De-slop fix reference** (rule → what the detector wants):

| Rule | The tell | The fix |
|------|----------|---------|
| `overused-font` / `single-font` | Inter / Roboto / Geist / Fraunces / Plus Jakarta Sans / Space Grotesk, or one family for everything | Pair a distinctive display face with a refined body face on a **contrast axis** (serif + humanist sans). Cap at 3 families |
| `gradient-text` | `background-clip:text` + gradient on a heading/metric | Solid color text. Reserve color for intent, not decoration |
| `ai-color-palette` / `cream-palette` | Purple/violet gradient, cyan-on-dark, or reflexive cream/beige surface | A deliberate palette built from one seed hue (OKLCH); bg/surface/ink/muted/accent that belong together |
| `dark-glow` | Dark bg + colored `box-shadow` glow | Subtle, purposeful elevation (neutral, low-spread) — or drop the dark theme |
| `side-tab` / `border-accent-on-rounded` | Thick colored border on one side of a card | Remove the accent stripe; carry emphasis with type, spacing, or a full subtle border |
| `nested-cards` | Card inside a card | Flatten — use spacing, dividers, and typography instead of nested containers |
| `icon-tile-stack` | Rounded-square icon tile stacked above every heading | Side-by-side icon + heading, or let the icon sit in flow without its own tile |
| `hero-eyebrow-chip` / `repeated-section-kickers` | Tiny uppercase tracked label above the hero / repeated as section scaffolding | Drop the eyebrow; fold the kicker into the headline or real structure |
| `bounce-easing` | `cubic-bezier` with negative control points / elastic | Exponential ease-out (`cubic-bezier(0.22,1,0.36,1)` etc.). Real objects decelerate smoothly |
| `marketing-buzzword` | streamline / empower / supercharge / world-class / enterprise-grade / next-generation / cutting-edge | A concrete verb + noun that says what the product literally does |
| `em-dash-overuse` | >2 em-dashes in body copy | Commas, colons, periods, parentheses |
| `oversized-h1` / `extreme-negative-tracking` | Long headline at display size; letter-spacing crushed past legibility | Shorter headline or smaller size; tracking floor ≥ −0.04em |
| `broken-image` | `<img>` with empty/missing/placeholder `src` | Real asset, generated/inline SVG, or remove the tag |
| `gray-on-color` | Gray text on a colored background | A darker shade of the background's own hue, or a transparency of the text color |
| `tight-leading` / `line-length` / `tiny-text` | line-height <1.3, lines >~80ch, body <12px | 1.5–1.7 leading, 65–75ch measure, ≥14px body |

```bash
IMPECCABLE=$(cat {{results_dir}}/.impeccable_cmd)
PROV=""; case "{{provider_tells}}" in gpt) PROV="--gpt";; gemini) PROV="--gemini";; esac

# After EACH editing round, re-scan the cleaned file:
set +e
$IMPECCABLE --json $PROV {{results_dir}}/polished.html > {{results_dir}}/audit_after.json
AFTER_EXIT=$?
set -e
echo "$AFTER_EXIT" > {{results_dir}}/.after_exit
AFTER_COUNT=$(python3 -c "import json;print(len(json.load(open('{{results_dir}}/audit_after.json'))))")
echo "round result: $AFTER_COUNT remaining, exit $AFTER_EXIT"
# Loop back to fixing if AFTER_EXIT != 0 and rounds remain; otherwise continue.
```

When the loop ends, write `before_after.md` (per-rule before/after table, regressions
introduced, and the final verdict). The polish **passes** only if `AFTER_EXIT == 0`
and no new rule ids appear in `audit_after.json` that were not in `audit_before.json`.

---

## Step 4: Iterate on Errors (max 3 rounds)

If a step raised an error, the detector failed to run, or `polish` did not reach a
clean re-scan:

1. Read the specific failure.
2. Apply the relevant fix from Common Fixes.
3. Re-run the affected step.
4. Repeat up to **3 rounds total**, then record the best result honestly in
   `summary.md` with `overall_passed` reflecting reality.

### Common Fixes

| Issue | Fix |
|-------|-----|
| `node: command not found` or Node < 24 | Re-run the Node-24 install block in Step 1; `impeccable` needs `engines.node >=24` |
| `npx` can't reach the registry | Use the clone fallback: `git clone … && node /tmp/impeccable/cli/bin/cli.js detect` (pinned SHA in Step 1) |
| Detector prints nothing on a clean file | That's correct — clean files print `[]` and exit `0`. Don't treat empty output as an error |
| URL scan hangs / no Chromium | Browser mode needs Puppeteer/Chromium. For a file target, scan the file directly (static engine, no browser) |
| Polish keeps re-flagging `marketing-buzzword` | The detector counts buzzword phrases across the whole document; rewrite **all** instances, not just the hero |
| `single-font` persists after swapping `overused-font` | You replaced one overused face with one non-overused face — still a single family. Add a second family on a contrast axis |
| Re-scan introduces a NEW rule (e.g. you added a cream surface) | A fix created fresh slop. Treat any new rule id in `audit_after.json` as a regression and fix it before declaring success |
| Findings reference a linked CSS file | The static-HTML engine follows linked CSS; edit the linked file, not just the inline `<style>` |

---

## Step 5: Validate Outputs (programmatic)

The detector is the grader. Assemble `stages` and decide `overall_passed`:

- **`audit`** passes when `audit_report.json` parses, `finding_count` matches the
  detector output, and `audit_report.md` is non-empty. (An audit that finds slop is
  still a successful audit — the report is the deliverable.)
- **`polish`** passes when the re-scan (`audit_after.json`) is **empty / exit `0`**
  **and** introduces no new rule ids. A run that reduces but doesn't eliminate
  findings is `PARTIAL` — ship it, but set `overall_passed=false` and say so.

```python
import json, pathlib
R = pathlib.Path("{{results_dir}}")
op = "{{operation}}" or "audit"
before = json.loads((R/"audit_before.json").read_text())
stages = [{"name":"setup","passed":True,"message":"Node + impeccable detect resolved"},
          {"name":"scan_before","passed":True,"message":f"{len(before)} findings"}]
if op == "polish":
    after = json.loads((R/"audit_after.json").read_text())
    after_exit = int((R/".after_exit").read_text().strip())
    introduced = sorted({f["antipattern"] for f in after} - {f["antipattern"] for f in before})
    clean = after_exit == 0 and len(after) == 0
    stages += [{"name":"scan_after","passed":clean,"message":f"{len(after)} remaining, exit {after_exit}"},
               {"name":"no_regressions","passed":not introduced,"message":f"{len(introduced)} introduced"}]
    overall = clean and not introduced
else:
    overall = (R/"audit_report.md").exists() and (R/"audit_report.json").exists()
    stages.append({"name":"report","passed":overall,"message":"audit_report.{json,md} written"})
print(json.dumps({"overall_passed": overall, "stages": stages}, indent=2))
```

---

## Step 6: Write Executive Summary

Write `{{results_dir}}/summary.md` with the operation, target, before/after counts,
the rules resolved (polish) or found (audit), the detector exit codes, and any
caveats. End with a Provenance block crediting `impeccable` (Paul Bakaus, Apache-2.0)
and the detector as the grader.

---

## Step 7: Write Validation Report

Write `{{results_dir}}/validation_report.json`:

```json
{
  "version": "1.0.0",
  "run_date": "<ISO-8601>",
  "parameters": { "operation": "<audit|polish>", "target": "<path|url>", "provider_tells": "none" },
  "tool": { "name": "impeccable detect", "source": "https://github.com/pbakaus/impeccable" },
  "stages": [ { "name": "setup", "passed": true, "message": "…" } ],
  "results": { "pass": 0, "partial": 0, "fail": 0 },
  "before_count": 0,
  "after_count": 0,
  "overall_passed": true,
  "output_files": ["…"]
}
```

`overall_passed` is `false` whenever a `polish` re-scan did not reach exit `0`, or a
regression was introduced, or any required output is missing.

---

## Step 8: Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="{{results_dir}}"
OP="{{operation}}"; OP="${OP:-audit}"

for f in "$RESULTS_DIR/summary.md" "$RESULTS_DIR/validation_report.json"; do
  [ -s "$f" ] && echo "PASS: $f ($(wc -c < "$f") bytes)" || echo "FAIL: $f missing or empty"
done

case "$OP" in
  audit)
    for f in "$RESULTS_DIR/audit_report.json" "$RESULTS_DIR/audit_report.md"; do
      [ -s "$f" ] && echo "PASS: $f" || echo "FAIL: $f missing or empty"
    done
    python3 -c "import json;json.load(open('$RESULTS_DIR/audit_report.json'));print('PASS: audit_report.json valid JSON')" \
      || echo "FAIL: audit_report.json invalid"
    ;;
  polish)
    for f in "$RESULTS_DIR/polished.html" "$RESULTS_DIR/audit_before.json" "$RESULTS_DIR/audit_after.json" "$RESULTS_DIR/before_after.md"; do
      [ -s "$f" ] && echo "PASS: $f" || echo "FAIL: $f missing or empty"
    done
    AFTER=$(python3 -c "import json;print(len(json.load(open('$RESULTS_DIR/audit_after.json'))))" 2>/dev/null || echo "?")
    [ "$AFTER" = "0" ] && echo "PASS: re-scan is clean (0 anti-patterns)" \
      || echo "WARN: $AFTER anti-pattern(s) remain — run is PARTIAL, document in summary.md"
    ;;
esac
echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] Node ≥ 24 present and `impeccable detect` resolved (npm or clone fallback)
- [ ] Baseline scan ran; `audit_before.json` is valid JSON; exit code captured
- [ ] **audit:** `audit_report.json` (valid JSON) + `audit_report.md` written; target unchanged
- [ ] **polish:** `polished.html` written; re-scan `audit_after.json` exits `0` (or PARTIAL is documented)
- [ ] **polish:** no new rule ids introduced vs `audit_before.json`
- [ ] `summary.md` records operation, before/after counts, and provenance
- [ ] `validation_report.json` has `stages`, `results`, `overall_passed` reflecting the real re-scan result
- [ ] Verification script printed PASS for every applicable line

**If ANY item fails, return to the relevant step and fix it. Do NOT finish until all applicable items pass.**

---

## Tips

- **The exit code is the contract.** `impeccable detect` exits `2` with findings and
  `0` when clean. A `polish` run is "done" exactly when a re-scan of the output exits
  `0` — don't declare success off a partial reduction or off `summary.md` prose.
- **The detector finds; you fix; the detector re-grades.** This closes the loop
  without an LLM judge. Trust the re-scan, not your own read of the page.
- **Don't trade one tell for another.** Swapping Inter for Fraunces still trips
  `overused-font`; replacing a purple gradient with a reflexive cream surface trips
  `cream-palette`. Any new rule id in the re-scan is a regression.
- **Static vs browser coverage.** File/dir targets use the static-HTML + regex
  engines (fast, no browser) and catch source-level tells. **URL** targets render in
  a real browser and additionally catch layout/contrast rules that only exist after
  paint. Pick the mode that matches the artifact.
- **Provider tells are opt-in.** GPT/Gemini signature tells are gated off by default;
  pass `provider_tells=gpt|gemini` only when you specifically want them.
- **Attribution.** This runbook wraps the `impeccable` skill's detector. Keep the
  upstream credit intact: impeccable © Paul Bakaus (Apache-2.0), building on
  Anthropic's frontend-design skill, with typography additions from ehmo's
  typecraft-guide-skill. See `origin.notice` in the frontmatter.
