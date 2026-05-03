---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/goose-graphics/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/goose-graphics
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: goose-graphics
  imported_at: '2026-05-03T02:45:42Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: goose-graphics
    confidence: high
secrets: {}
---

# goose-graphics - Agent Runbook

## Objective

Use the Goose Graphics skill to generate a portable visual artifact from a brief, optional references, and Gooseworks community-published styles and formats. The source describes `goose-graphics` as a visual skill pack for agent ecosystems that discovers styles and formats, optionally extracts style from reference images, generates HTML, and exports rendered PNGs through a browser workflow. This runbook makes that process Jetty-deployable by declaring outputs, bounded validation, and a repeatable final checklist.

Source description: Portable visual skill pack for the Agent Skills ecosystem (Claude Code, Claude Desktop, Claude Cowork, Claude Design, Goose, Cursor, Codex). Discovers community-published styles + formats via the gooseworks CLI, runs an extract-style workflow on reference images, and exports rendered PNGs via Playwright.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/summary.md` | Executive summary of the generated graphic, selected style, render path, and any caveats |
| `/app/results/validation_report.json` | Structured validation results for setup, render, screenshot, and output checks |
| `/app/results/goose-graphics.html` | Self-contained HTML source used for the visual render |
| `/app/results/goose-graphics.png` | Final rendered PNG output |
| `/app/results/browser_console.json` | Browser console messages when a browser renderer is used |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `results_dir` | `/app/results` | Output directory for all required files |
| `brief` | required | Text description of the visual to produce |
| `style` | auto-discover | Gooseworks style slug or description |
| `format` | `png` | Output format target |
| `refs` | none | Optional image references or source material |
| `output_name` | `goose-graphics` | Base filename for generated artifacts |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| `node` / `npx` | CLI | Yes | Runs Gooseworks catalog helpers and optional browser tooling |
| `gooseworks` | npm package | Yes | Discovers and fetches Gooseworks styles and formats |
| `playwright` | Browser tooling | Recommended | Captures deterministic screenshots from generated HTML |
| Python 3 | CLI | Yes | Writes validation and summary JSON/Markdown artifacts |

## Step 1: Environment Setup

Create the output directory, verify Node.js and Python are available, and install any missing runtime helpers.

```bash
mkdir -p /app/results /app/results/work
command -v node >/dev/null || { echo "ERROR: node is required"; exit 1; }
command -v npx >/dev/null || { echo "ERROR: npx is required"; exit 1; }
python - <<'PY'
import json, pathlib
pathlib.Path('/app/results/validation_report.json').write_text(json.dumps({
  "setup": "started"
}, indent=2))
PY
```

## Step 2: Resolve Inputs

Read the requested visual brief and normalize optional parameters. If `brief` is missing, ask one focused question before continuing. Default `output_dir` to `/app/results`, default `format` to a single PNG render, and leave `style` unset until discovery if the operator did not provide one.

## Step 3: Discover Style And Format

Use the Gooseworks catalog to list or search published styles and formats. Prefer the most specific style whose description matches the brief, then fetch the slim `DESIGN.md` spec for the chosen style and any selected format.

```bash
npx -y gooseworks@latest styles list || true
npx -y gooseworks@latest formats list || true
```

## Step 4: Prepare References

If image references are provided, copy them into `/app/results/work/references` and extract any reusable style notes before generating HTML. Keep references optional; a text-only brief is valid.

## Step 5: Generate HTML

Generate a self-contained HTML file at `/app/results/work/goose-graphics.html`. The HTML must implement the selected visual style, include all required assets inline or by stable local paths, and be sized for the target format.

## Step 6: Screenshot Render

Render the HTML with Playwright or an equivalent browser screenshot tool and write the final PNG to `/app/results/goose-graphics.png`. Capture browser console errors in `/app/results/browser_console.json` when the renderer supports it.

## Step 7: Validate Outputs

Check that the generated PNG and HTML exist, are non-empty, and that the PNG has plausible dimensions. Record the validation result in `/app/results/validation_report.json`.

## Step 8: Iterate on Errors (max 3 rounds)

If validation fails or the render is visibly incomplete, perform up to max 3 rounds of targeted fixes. Each round should change only the HTML, referenced assets, or renderer settings needed to satisfy the validation finding, then re-run the screenshot and validation steps.

## Step 9: Final Checklist

Run the final verification script and write `/app/results/summary.md`.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in   "$RESULTS_DIR/summary.md"   "$RESULTS_DIR/validation_report.json"   "$RESULTS_DIR/goose-graphics.html"   "$RESULTS_DIR/goose-graphics.png"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

## Common Fixes

| Issue | Fix |
|---|---|
| Gooseworks catalog command unavailable | Re-run through `npx -y gooseworks@latest ...` and capture stderr in the validation report |
| Screenshot is blank | Open the HTML in a browser, check console errors, and fix missing assets or script failures |
| Output file is too small | Re-render after ensuring the page has stable viewport dimensions and visible content |
| Style does not match the brief | Fetch a more specific style spec and repeat the HTML generation step |

## Source Procedure Notes

The upstream skill includes these major sections, preserved here as implementation guidance:

- 1. Overview
- 2. Invocation
- 3. Discovering styles and formats
- 4. Publishing your style
- 5. Publishing your format
- 6. Host compatibility
- 7. First-Run Setup
- 8. Interactive Workflow
- 9. Step 1: Discover Intent
- 10. Step 2: Select Style
- 11. Step 3: Image Sources (Optional)
- 12. Step 4: Output Path
- 13. Step 5: Generate HTML
- 14. Step 6: Screenshot
- 15. Step 7: Deliver
- 16. Special Modes
- 17. Manifest format
- 18. File reference

## Tips

Prefer fetching the smallest relevant Gooseworks style or format spec before generating HTML, and keep generated render assets inside `/app/results` so validation and downstream collection remain deterministic.
