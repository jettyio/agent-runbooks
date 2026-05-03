---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/visual-brand-extractor/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/visual-brand-extractor
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Visual Brand Extractor
  imported_at: '2026-05-03T02:45:27Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: visual-brand-extractor
    confidence: high
secrets: null
---

# Visual Brand Extractor — Agent Runbook

## Objective

Extract a client's visual identity from their website and convert the findings into reusable brand artifacts. The runbook uses web page content, CSS, metadata, and visible design patterns to identify color roles, font pairings, layout conventions, and the overall visual direction. It produces a slide style preset, a structured brand config JSON file, extraction notes, and a short summary that downstream content tools can consume. This import was resolved from a Gooseworks directory mirror to the pinned upstream GitHub `SKILL.md` before generation.

## REQUIRED OUTPUT FILES (MANDATORY)

All output files MUST be written under `/app/results`.

| File | Description |
|---|---|
| `/app/results/visual_brand_identity.md` | Human-readable visual identity report for the target client |
| `/app/results/slide_preset.json` | Reusable slide preset with colors, typography, and layout style settings |
| `/app/results/brand_config.json` | Structured brand configuration JSON for content asset generation |
| `/app/results/extraction_notes.md` | Notes about source pages inspected, ambiguity, fallbacks, and confidence |
| `/app/results/summary.md` | Executive summary of the extraction run and generated artifacts |
| `/app/results/validation_report.json` | Programmatic validation report with stages, results, and `overall_passed` |

## Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `results_dir` | path | No | `/app/results` | Directory where all required output files are written |
| website-url | string | Yes |  | Client's homepage or landing page URL |
| client-name | string | Yes |  | For naming the output files |
| additional-pages | string | No |  | Product page, docs page, etc. for richer extraction |
| `max_pages` | integer | No | `5` | Maximum number of pages to inspect during extraction |
| `confidence_threshold` | number | No | `0.65` | Minimum confidence for assigning a color or font role without a note |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---:|---|
| WebFetch or equivalent browser fetch tool | Agent tool | Yes | Fetches the target website, CSS, and related public pages |
| Python 3.12 | Runtime | Yes | Runs JSON validation and optional artifact checks |
| `requests` | Python package | No | Useful when the environment allows direct HTTP fetches |
| `beautifulsoup4` | Python package | No | Useful for structured HTML parsing when direct scripting is available |
| `jq` | CLI | No | Optional inspection of generated JSON artifacts |

## Step 1: Environment Setup

1. Create the results directory and confirm the required inputs are present.
2. Normalize the client name into a filesystem-safe slug for internal references.
3. Initialize a validation log with setup status and resolved parameters.

```bash
mkdir -p /app/results
python - <<'PY'
import json, pathlib
required = ["WEBSITE_URL", "CLIENT_NAME"]
missing = [name for name in required if not globals().get(name)]
pathlib.Path("/app/results/setup_check.json").write_text(json.dumps({"missing": missing}, indent=2))
PY
```

If a required input is missing, stop after writing `/app/results/validation_report.json` with `overall_passed=false`.

## Step 2: Fetch Target Pages

Fetch the client's homepage first, then inspect up to `max_pages` additional pages that best expose product UI, pricing, docs, case studies, or marketing layouts. Prefer canonical public pages and same-origin CSS. Record each fetched URL, HTTP status, content type, and whether the page was useful in `/app/results/extraction_notes.md`.

For JavaScript-rendered sites, use rendered page text and linked static assets when raw HTML is sparse. If stylesheets are blocked, continue with visible page evidence and document the limitation.

## Step 3: Extract Color Palette

Inspect CSS custom properties, meta theme colors, explicit CSS color declarations, utility classes, inline styles, and visible page screenshots or rendered styles when available. Group colors into roles:

| Role | Evidence to Prefer |
|---|---|
| `background` | Body, section, and app shell backgrounds |
| `surface` | Cards, panels, modals, navigation containers |
| `primary` | Main CTA, links, selected states, product accent |
| `secondary` | Supporting accents and alternate CTA treatment |
| `text` | Body copy, headings, muted text, inverse text |
| `border` | Dividers, input outlines, card borders |

Classify whether the site primarily reads as light, dark, mixed, or system-adaptive. Keep no more than eight core colors in the preset unless the brand clearly requires more.

## Step 4: Extract Typography

Identify font sources from CSS imports, `@font-face`, Google Fonts links, CSS variables, and computed font-family declarations. Separate display and body typography when the evidence supports it. When proprietary fonts appear, choose practical fallbacks and explain the substitution in `/app/results/extraction_notes.md`.

## Step 5: Analyze Visual Patterns

Summarize layout density, corner radius, border usage, shadow treatment, image style, icon style, animation tendencies, CTA shape, and spacing rhythm. Synthesize the brand vibe in concrete design language that can guide slide and asset generation without relying on vague adjectives alone.

## Step 6: Generate Brand Artifacts

Write the required artifacts:

1. `/app/results/visual_brand_identity.md` with sections for palette, typography, layout, visual motifs, confidence, and examples.
2. `/app/results/slide_preset.json` with slide-friendly tokens for backgrounds, surfaces, text, accent, heading font, body font, radius, chart palette, and visual style.
3. `/app/results/brand_config.json` with structured fields for client name, source URLs, colors, fonts, layout patterns, and fallback notes.
4. `/app/results/extraction_notes.md` with fetched pages, source evidence, assumptions, and edge cases.
5. `/app/results/summary.md` with the target site, client name, artifact list, confidence, and manual follow-up.

## Step 7: Validate Artifacts

Run structural checks before finishing:

```bash
python - <<'PY'
import json, pathlib
results = pathlib.Path("/app/results")
required = [
    "visual_brand_identity.md",
    "slide_preset.json",
    "brand_config.json",
    "extraction_notes.md",
    "summary.md",
]
stages = []
for name in required:
    path = results / name
    stages.append({"name": f"exists:{name}", "passed": path.exists() and path.stat().st_size > 0})
for name in ["slide_preset.json", "brand_config.json"]:
    try:
        json.loads((results / name).read_text())
        stages.append({"name": f"json:{name}", "passed": True})
    except Exception as exc:
        stages.append({"name": f"json:{name}", "passed": False, "message": str(exc)})
overall = all(stage.get("passed") for stage in stages)
(results / "validation_report.json").write_text(json.dumps({
    "version": "1.0.0",
    "stages": stages,
    "results": {
        "pass": sum(1 for s in stages if s.get("passed")),
        "partial": 0,
        "fail": sum(1 for s in stages if not s.get("passed")),
    },
    "overall_passed": overall,
}, indent=2))
PY
```

## Step 8: Iterate on Errors (max 3 rounds)

If validation fails, perform a targeted correction and re-run Step 7. Limit the repair loop to max 3 rounds. If JSON is invalid, fix only the malformed artifact. If a file is missing, regenerate only that file from the existing extraction notes. If the confidence is low because source pages were sparse, keep the artifacts but mark the limitation clearly in `summary.md` and `extraction_notes.md`.

## Common Fixes

| Issue | Fix |
|---|---|
| `slide_preset.json` does not parse | Re-emit strict JSON with double-quoted keys and no trailing commas |
| Too many colors were captured | Reduce to role-based core colors and move extras to notes |
| Fonts are proprietary or unavailable | Keep the original name as evidence and provide system or Google Font fallbacks |
| JavaScript-rendered page has sparse HTML | Use rendered evidence, meta tags, linked assets, and document confidence |
| Brand has both light and dark modes | Select the dominant marketing mode and include alternate tokens where clear |

## Final Checklist

Run this exact verification before stopping:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/visual_brand_identity.md" \
  "$RESULTS_DIR/slide_preset.json" \
  "$RESULTS_DIR/brand_config.json" \
  "$RESULTS_DIR/extraction_notes.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
python - <<'PY'
import json, pathlib
for name in ["slide_preset.json", "brand_config.json", "validation_report.json"]:
    json.loads((pathlib.Path("/app/results") / name).read_text())
print("PASS: JSON artifacts parse")
PY
```

- [ ] `visual_brand_identity.md` exists and includes palette, typography, layout, and confidence notes
- [ ] `slide_preset.json` parses as JSON and includes color and typography tokens
- [ ] `brand_config.json` parses as JSON and includes source URLs and fallback notes
- [ ] `extraction_notes.md` records fetched pages and ambiguous evidence
- [ ] `summary.md` lists generated artifacts and manual follow-up
- [ ] `validation_report.json` has `stages`, `results`, and `overall_passed`
- [ ] Verification script printed PASS for every required file

## Tips

The source skill defines a direct agent workflow: fetch a client's site, inspect pages and CSS, extract reusable colors, classify typography, analyze visual patterns, and produce a slide preset plus a brand configuration.

The generated runbook keeps the source process intact while adding deterministic output files, validation, and final verification suitable for Jetty programmatic evaluation.

Carry over the source skill's practical guidance: inspect CSS variables first, then visible declarations and utility classes; classify colors by role rather than by raw frequency; separate display and body fonts; and keep extraction notes explicit when a site is sparse, heavily JavaScript-rendered, or exposes multiple themes.

## Source Skill Reference

The original upstream skill content is preserved separately by the importer in `/app/results/source.md`. The canonical upstream source for this runbook is:

`https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/capabilities/visual-brand-extractor/SKILL.md`
