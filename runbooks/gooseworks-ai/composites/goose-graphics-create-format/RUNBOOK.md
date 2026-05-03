---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/gooseworks-ai/goose-skills/296901414500a3a2d26b37e410f92e0406bf94a2/skills/composites/goose-graphics-create-format/SKILL.md
  user_supplied_url: https://skills.gooseworks.ai/skills/goose-graphics-create-format
  is_directory_mirror: true
  source_host: raw.githubusercontent.com
  source_title: Create Goose Graphics Format
  imported_at: '2026-05-03T02:33:59Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: gooseworks-ai
    skill_name: goose-graphics-create-format
    confidence: high
secrets: null
---

# Create Goose Graphics Format — Agent Runbook

## Objective

Create and publish a new Gooseworks graphics format when the existing community formats do not cover the user's requested surface or content structure. The runbook guides an agent through selecting one of the fixed supported canvases, drafting a reusable `contentRulesMd` spec, rendering at least one example PNG, publishing through `npx gooseworks formats publish`, and reporting the published slug. Use when the user wants a new named format with its own content rules — a story cover, a podcast cover, a square testimonial — that maps to one of the seven built-in canvas sizes (carousel, infographic, slides, poster, story, chart, tweet). The new format defines new rules and a new slug; it inherits dimensions from one of those canvases. **Custom canvas dimensions are not supported.** If the user wants a canvas size that isn't in the seven built

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `gooseworks-format.json` | Format manifest ready for `npx gooseworks formats publish`. |
| `example-1.png` | At least one rendered example image; additional examples are recommended. |
| `summary.md` | Summary of the chosen canvas, slug, examples, publish URL, and any limitations. |
| `validation_report.json` | Structured validation for setup, manifest, examples, publish, and final outputs. |

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `results_dir` | `/app/results` | Output directory for generated manifest drafts, examples, summary, and validation report. |
| `working_dir` | `./gooseworks-format` | Local directory that will contain `gooseworks-format.json` and rendered example PNGs. |
| `canvas_slug` | required | One of `poster`, `infographic`, `carousel`, `slides`, `story`, `chart`, or `tweet`. |
| `format_slug` | inferred | Lowercase kebab-case slug for the new published format. |
| `style_slugs` | `matt-gray` plus alternatives | Published Gooseworks styles used to render required examples. |

Inferred user inputs:

- A brief describing the canvas: dimensions, intended use (platform / surface),
- Optional: a reference image showing the desired layout.

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| `npx gooseworks` | CLI | Yes | Lists, fetches, publishes, and updates Gooseworks formats and styles. |
| `goose-graphics` skill pack | Skill | Yes | Provides screenshot rendering for examples. |
| Node.js and npm | CLI | Yes | Runs the screenshot tool and installs Playwright dependencies. |
| Playwright Chromium | Runtime | Yes | Required by the `goose-graphics` screenshot tool. |
| Gooseworks account | External service | Yes | Publishing requires `npx gooseworks login`. |

Referenced tools from the source skill: `bash`, `json`, `npx gooseworks formats get <slug>`, `npx gooseworks formats list`, `npx gooseworks formats publish`, `npx gooseworks login`, `npx gooseworks styles get <slug>`, `npx gooseworks styles list | head`.

## Step 1: Environment Setup

1. Create the output directory and a dedicated working directory.
2. Confirm the `goose-graphics` skill is installed in the workspace.
3. Confirm screenshot dependencies are installed for `goose-graphics/screenshot`.
4. Confirm the user is signed in with `npx gooseworks login`.

```bash
mkdir -p "${RESULTS_DIR:-/app/results}" "${WORKING_DIR:-./gooseworks-format}"
npx gooseworks formats list >/tmp/gooseworks-formats.txt
npx gooseworks styles list >/tmp/gooseworks-styles.txt
test -d goose-graphics/screenshot/node_modules || \
  (cd goose-graphics/screenshot && npm install && npx playwright install chromium)
```

## Step 2: Check Existing Formats

Run `npx gooseworks formats list` or `npx gooseworks formats search "<term>"` before creating anything new. If an existing format fits the user's request, stop and report the existing slug instead of publishing a duplicate.

```bash
npx gooseworks formats search "${SEARCH_TERM:-format}" || true
```

## Step 3: Pick a Supported Canvas

Choose exactly one built-in canvas. A new format is a new slug and new content rules over an existing canvas; it is not a new custom width and height.

| Canvas slug | Dimensions | Best for |
|---|---:|---|
| `poster` | `1080x1350` | Vertical hero composition, single panel |
| `infographic` | `1080xvariable` | Tall vertical scroll, multi-section |
| `carousel` | `1080x1080` | Square single panel or multi-slide |
| `slides` | `1920x1080` | Widescreen presentation |
| `story` | `1080x1920` | Vertical full-screen stories |
| `chart` | `1080x1080` | Square data visualization |
| `tweet` | `1080x1080` | Square testimonial or social card |

If the user requests dimensions outside this list, explain that custom canvas dimensions require a code change to `goose-graphics` `FORMAT_CONFIGS`, then suggest the closest supported canvas.

## Step 4: Define Name, Slug, and Content Rules

Suggest 2-3 descriptive lowercase kebab-case slugs. Check the preferred slug before using it:

```bash
npx gooseworks formats get "$FORMAT_SLUG"
```

Draft `contentRulesMd` with these elements:

- When to use the format instead of alternatives.
- Exact maximum content density: word counts, item counts, image requirements, and panel count.
- Per-section content rules for header, body, CTA, footer, hero media, or brand marks.
- Typography hierarchy suitable for the chosen canvas dimensions.
- Spacing, padding, margins, and rhythm.

## Step 5: Render Example Images

Render at least one example PNG and preferably 2-3 examples across contrasting published styles.

```bash
npx gooseworks styles list | head
npx gooseworks styles get "$STYLE_SLUG" > "$WORKING_DIR/style-$STYLE_SLUG.json"
node goose-graphics/screenshot/screenshot.js \
  --format "$CANVAS_SLUG" \
  --input "$WORKING_DIR/example-1.html" \
  --output "$WORKING_DIR/example-1.png" \
  --font-delay 1500
```

The HTML must be self-contained, use fixed pixel sizes, and match the selected canvas dimensions exactly.

## Step 6: Write `gooseworks-format.json`

Create the manifest in the working directory.

```json
{
  "name": "Story Cover",
  "slug": "story-cover",
  "description": "1080x1920 vertical canvas for Instagram and TikTok stories. Single-panel composition, 5-word title max, large hero image or stat, optional brand mark in the lower 10% of the canvas.",
  "width": 1080,
  "height": 1920,
  "contentRulesMd": "## Rules\n\n- Title: 5 words max, large display\n- One hero element in the upper 70% of the canvas\n- Optional brand mark in the lower 10%",
  "tags": ["story", "vertical", "social"],
  "examples": [
    { "file": "./example-1.png", "styleSlug": "matt-gray", "caption": "Paired with matt-gray" }
  ]
}
```

## Step 7: Validate Before Publish

Validate that the manifest has a 20-1000 character description, at least 50 characters of `contentRulesMd`, 3-10 lowercase tags, and at least one rendered example file. Confirm `width` and `height` match the selected built-in canvas.

```bash
python - <<'PY'
import json, pathlib, sys
root = pathlib.Path("${WORKING_DIR:-./gooseworks-format}")
manifest = json.loads((root / "gooseworks-format.json").read_text())
errors = []
if not (20 <= len(manifest.get("description", "")) <= 1000): errors.append("description length")
if len(manifest.get("contentRulesMd", "")) < 50: errors.append("contentRulesMd too short")
if not (3 <= len(manifest.get("tags", [])) <= 10): errors.append("tag count")
if not manifest.get("examples"): errors.append("at least one example required")
for ex in manifest.get("examples", []):
    if not (root / ex["file"]).exists(): errors.append(f"missing example {ex['file']}")
print(json.dumps({"passed": not errors, "errors": errors}, indent=2))
sys.exit(1 if errors else 0)
PY
```

## Step 8: Publish

Publish from the working directory. Use `--yes` when scripted so a server-suggested slug can be accepted automatically after a collision.

```bash
cd "$WORKING_DIR"
npx gooseworks formats publish --yes
```

Record the published slug, catalog URL, selected dimensions, and style slugs used for examples.

## Step 9: Iterate on Errors (max 3 rounds)

If validation or publish fails, run at most 3 rounds of targeted fixes. Fix only the failing item, re-render examples when visual output changes, re-run validation, and then retry publish. Stop after 3 rounds and write the remaining issue to `summary.md` and `validation_report.json`.

## Common Fixes

| Issue | Fix |
|---|---|
| Slug already taken | Accept the CLI suggestion with `--yes` or choose a more specific slug. |
| Custom dimensions requested | Pick the closest built-in canvas and explain the limitation. |
| Empty examples rejected | Render at least `example-1.png` and include it in the manifest. |
| Screenshot dependency missing | Run `npm install` and `npx playwright install chromium` under `goose-graphics/screenshot`. |
| Description too vague | Lead with canvas, surface, text density, platform, audience, and use case. |

## Step 10: Final Checklist

Write `summary.md` and `validation_report.json`, then verify all mandatory outputs.

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="${RESULTS_DIR:-/app/results}"
WORKING_DIR="${WORKING_DIR:-./gooseworks-format}"
for f in \
  "$WORKING_DIR/gooseworks-format.json" \
  "$WORKING_DIR/example-1.png" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

## Final Checklist

- `gooseworks-format.json` exists and contains name, slug, description, width, height, `contentRulesMd`, tags, and examples.
- At least one rendered example PNG exists and matches the chosen canvas dimensions.
- `summary.md` reports the published slug, catalog URL, dimensions, and example styles.
- `validation_report.json` reports setup, manifest validation, example rendering, publish, and output verification.
- The final verification script prints `PASS` for every required output.

## Tips

Same shape as styles — 50–200 words, keyword-dense — but lead with **canvas
and content density** instead of mood.
- Lead with canvas + surface: `"1080×1080 square testimonial card for X
feed posts."`
- Mention single-panel vs multi-panel and approximate text limits.
- Mention intended platform / surface (`Instagram Stories`, `LinkedIn`,

### Source Workflow Notes


