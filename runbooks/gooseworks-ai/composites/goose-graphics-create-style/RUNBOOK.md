---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/goose-graphics-create-style/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/goose-graphics-create-style
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Create Goose Graphics Style
  imported_at: '2026-05-03T02:23:46Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: goose-graphics-create-style
    confidence: high
secrets: {}
---

# Create Goose Graphics Style — Agent Runbook

## Objective

Create and publish a reusable Gooseworks graphics style from a single reference image. The runbook analyzes the source image as an aesthetic system, drafts a slim style spec, renders a required hero example plus 2-3 additional format examples, writes a valid `gooseworks-style.json` manifest, and publishes it through `npx gooseworks styles publish`. The generated style must be discoverable for future `/goose-graphics --style <slug> --format <any>` calls.

Source summary: End-to-end skill that turns a single reference image into a published Gooseworks style — analyzes the image, drafts the slim style spec, renders a hero example plus 2-3 additional formats via Playwright, writes the `gooseworks-style.json` manifest, and publishes via `npx gooseworks styles publish` so other agents can discover it. Mirrors goose-graphics-create-format but for styles.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/gooseworks-style.json` | Published style manifest with `designMd`, examples, slug/name, mood group, and exactly one hero example |
| `/app/results/poster.png` | Hero rendered example; use `isHero: true` in the manifest |
| `/app/results/carousel.png` | Additional rendered example showing the style in a square format |
| `/app/results/infographic.png` | Additional rendered example showing the style in a tall format |
| `/app/results/summary.md` | Executive summary with selected slug, mood group, publish result, and output paths |
| `/app/results/validation_report.json` | Structured validation results and final output verification status |

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| Results directory | `/app/results` | Directory where final artifacts and reports must be written |
| Reference image | required | PNG/JPG/WebP image used to infer the style aesthetic |
| Style name / slug | optional | Lowercase-kebab-case slug; propose 2-3 candidates when omitted |
| Mood group | optional | One of `Dark & Moody`, `Light & Editorial`, `Organic & Warm`, `Bold & Energetic`, `Retro & Cinematic`, `Structural & Technical`, `Friendly Corporate` |
| Publish flag | `true` | Whether to run `npx gooseworks styles publish`; leave false only for local validation |

## Dependencies

| Dependency | Required | Purpose |
|---|---:|---|
| `node` and `npx` | Yes | Run Gooseworks CLI commands |
| `gooseworks` CLI | Yes | List, inspect, validate, and publish styles |
| `goose-graphics` skill | Yes | Provides the screenshot renderer used for example images |
| Playwright Chromium | Yes | Renders HTML examples to PNG |
| Gooseworks login | Yes | Authenticates `npx gooseworks styles publish` |
| Reference image readable by the agent | Yes | Source for visual analysis |

## Step 1: Environment Setup

```bash
mkdir -p /app/results/style-work /app/results/style-work/examples
command -v node >/dev/null || { echo "ERROR: node is required"; exit 1; }
command -v npx  >/dev/null || { echo "ERROR: npx is required"; exit 1; }
npx gooseworks styles list >/tmp/gooseworks-styles-list.txt
test -d goose-graphics/screenshot/node_modules || (
  cd goose-graphics/screenshot && npm install && npx playwright install chromium
)
```

If the user has not supplied a reference image path, stop and ask for it. If `npx gooseworks styles list` fails because the user is not authenticated, run `npx gooseworks login` before continuing.

## Step 2: Check Existing Styles

Search the catalog before creating a new style:

```bash
npx gooseworks styles list
npx gooseworks styles search "<short aesthetic description>"
```

If a community-published style already covers the reference aesthetic, use the normal `goose-graphics` flow with that existing style and write `summary.md` explaining that no new style was published.

## Step 3: Analyze the Reference Image

Read the image and write the analysis in plain text before drafting files. Cover palette, typography, layout and shape language, signature visual moves, and mood/category. Treat the style as an aesthetic system: palette, type, density, rhythm, surfaces, borders, shadows, and repeatable visual moves that can flex across poster, carousel, infographic, slides, chart, story, and tweet formats.

Do not describe the style as a fixed composition such as "five cards in a bento grid." Reframe fixed layout observations into reusable principles that can survive across every format.

## Step 4: Pick Name, Slug, and Mood Group

Use the provided `--name` when present. Otherwise propose 2-3 lowercase-kebab-case candidates derived from the signature moves and ask the user to pick one. Check for collisions:

```bash
npx gooseworks styles get <slug>
```

If the slug already exists, suggest an alternative. Choose or confirm one of the seven supported mood groups before packaging the manifest.

## Step 5: Draft the Slim Style Spec

Create the markdown that will become the manifest `designMd` field. Keep it under about 200 lines / 8KB and use this structure:

1. H1 display name.
2. Tagline paragraph describing the aesthetic and signature move.
3. `## Palette` table with `Hex | Role` columns.
4. `## Typography` with Google Fonts link, CSS variables, role table, and 3-5 principles.
5. `## Layout` with a required `Format padding` line for carousel, infographic, slides, poster, story, chart, and tweet.
6. `## Do / Don't` with five bullets each.
7. `## CSS snippets` with `:root` variables and 1-2 ready-to-paste snippets.

Fetch a known slim spec if the structure is unclear:

```bash
npx gooseworks styles get dot-grid-stat
```

## Step 6: Render Hero and Additional Examples

Use the standard catalog brief for every example:

```text
5 Tips for Building a Startup in 2026
1. Ship fast, learn faster
2. Build AI into the core
3. Hire for leverage, not headcount
4. Obsess over 10 users before 10,000
5. Revenue beats runway
```

Render one hero and 2-3 additional examples using exact format dimensions. Prefer hero formats in this order: poster, carousel, infographic, slides, chart, story, tweet. Write the required examples to `/app/results/poster.png`, `/app/results/carousel.png`, and `/app/results/infographic.png`.

## Step 7: Package and Publish

Write `/app/results/gooseworks-style.json` with the chosen slug, mood group, `designMd`, and examples array. The examples array must not be empty and exactly one example must have `isHero: true`.

```bash
npx gooseworks styles publish /app/results/gooseworks-style.json --yes
```

Record the published slug, CLI result, and any server-suggested slug in `/app/results/summary.md`.

## Step 8: Iterate on Errors (max 3 rounds)

If rendering, manifest validation, or publishing fails, run at most 3 rounds:

1. Read the exact error message.
2. Fix only the failing artifact or manifest field.
3. Re-render or re-run publish as needed.
4. Update `/app/results/validation_report.json` with the attempt and result.

Stop after 3 rounds and mark `overall_passed=false` if the style still cannot be rendered or published.

## Common Fixes

| Issue | Fix |
|---|---|
| Missing hero | Mark exactly one manifest example with `isHero: true` |
| Empty examples array | Add the hero plus at least two additional examples |
| Slug collision | Accept the server suggestion with `--yes` or choose a new lowercase-kebab-case slug |
| Screenshot dependencies missing | Run `npm install` and `npx playwright install chromium` under `goose-graphics/screenshot` |
| Style spec too composition-specific | Rewrite fixed layout details as reusable palette, type, shape, and motion principles |

## Step 9: Final Checklist

Write `/app/results/validation_report.json` and run this verification script:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/gooseworks-style.json" \
  "$RESULTS_DIR/poster.png" \
  "$RESULTS_DIR/carousel.png" \
  "$RESULTS_DIR/infographic.png" \
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
report = json.loads(pathlib.Path('/app/results/validation_report.json').read_text())
assert 'stages' in report and 'results' in report
assert isinstance(report.get('overall_passed'), bool)
print('PASS: validation_report.json has stages, results, and overall_passed')
PY
```

## Final Checklist

- `gooseworks-style.json` exists and has `designMd`, `examples`, slug/name, mood group, and exactly one hero.
- Hero and additional PNG examples exist and are non-empty.
- The standard brief was used for all examples.
- Publish succeeded or `summary.md` clearly explains why publication was skipped.
- `validation_report.json` records every stage and the final verification result.

## Tips

Always check the existing Gooseworks catalog before publishing a new style. Keep the style spec aesthetic-only, not format-specific, and use the same startup brief for every rendered example so catalog reviewers can compare styles consistently.
