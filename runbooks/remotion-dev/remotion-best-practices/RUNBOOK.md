---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
origin:
  url: "https://skills.sh/remotion-dev/skills/remotion-best-practices"
  source_host: "skills.sh"
  source_title: "remotion-best-practices"
  imported_at: "2026-05-01T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "remotion-dev"
    skill_name: "remotion-best-practices"
    confidence: "high"
secrets: {}
---

# remotion-best-practices — Agent Runbook

## Objective

This runbook encodes best practices for Remotion, a framework for creating videos programmatically using React. It guides an agent through setting up a Remotion project, running the preview studio, rendering frames, and applying domain-specific rules for animations, audio, captions, assets, fonts, transitions, and other Remotion subsystems. Use this runbook whenever you are working with Remotion code to obtain domain-specific knowledge and follow established conventions. The runbook also documents how to load specialized rule files for advanced topics such as FFmpeg operations, silence detection, and audio visualization.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary with run metadata and any issues encountered |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/project_scaffold.txt` | Output of the project scaffolding command (or confirmation it was skipped) |
| `/app/results/render_check.txt` | Output of the optional single-frame render check (or "skipped" if omitted) |
| `/app/results/studio_start.txt` | Confirmation or output of the Remotion Studio start command |

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Project name | `my-video` | Name of the new Remotion project to scaffold |
| Composition ID | *(required for render check)* | ID of the composition to render a still from |
| Frame number | `30` | Frame index for the one-frame render check (zero-based; frame 30 = 1 second at 30 fps) |
| Scale | `0.25` | Scale factor for the one-frame render still |
| Use Tailwind | `false` | Whether to scaffold with TailwindCSS support (default: no Tailwind) |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `node` / `npx` | Runtime | Yes | Node.js runtime required to run Remotion CLI commands |
| `npm` / `yarn` / `pnpm` | Package manager | Yes | Used to install Remotion and project dependencies |
| `ffmpeg` | CLI | Conditional | Required for video trimming, silence detection, and other media operations |
| `@remotion/cli` | npm package | Yes | Remotion CLI (`npx remotion`) for studio, render, and still commands |
| `create-video` | npx package | Yes | Scaffolding tool for new Remotion projects |
| `@remotion/three` | npm package | Optional | Required when using 3D content with React Three Fiber |
| `@remotion/lottie` | npm package | Optional | Required when embedding Lottie animations |
| `@remotion/light-leaks` | npm package | Optional | Required for light-leak overlay effects |
| `mediabunny` | npm package | Optional | Required for video/audio dimension and duration queries |

---

## Step 1: Environment Setup

Verify the runtime environment before proceeding.

```bash
echo "=== ENVIRONMENT SETUP ==="
node --version || { echo "ERROR: node not installed"; exit 1; }
npx --version || { echo "ERROR: npx not available"; exit 1; }

# Optionally check FFmpeg availability (needed for some rules)
ffmpeg -version 2>/dev/null && echo "FFmpeg: available" || echo "FFmpeg: not installed (optional, required for video trimming/silence detection)"

mkdir -p /app/results
echo "Environment ready" | tee /app/results/studio_start.txt
```

---

## Step 2: Scaffold a New Remotion Project

When starting in an empty folder or workspace with no existing Remotion project, scaffold one using the blank template:

```bash
PROJECT_NAME="${PROJECT_NAME:-my-video}"

npx create-video@latest --yes --blank --no-tailwind "$PROJECT_NAME" 2>&1 | tee /app/results/project_scaffold.txt
cd "$PROJECT_NAME"
npm install 2>&1 | tee -a /app/results/project_scaffold.txt
echo "Project scaffolded: $PROJECT_NAME"
```

Replace `my-video` with a suitable project name. If a project already exists in the working directory, skip this step and note it in `/app/results/project_scaffold.txt`:

```bash
if [ -f "package.json" ] && grep -q "remotion" package.json 2>/dev/null; then
  echo "Existing Remotion project detected — skipping scaffold" | tee /app/results/project_scaffold.txt
fi
```

---

## Step 3: Start the Remotion Studio (Preview)

Start the Remotion Studio to preview video compositions interactively:

```bash
# Start studio — note: this is a long-running process; run in background or interactively
echo "Starting Remotion Studio..." | tee -a /app/results/studio_start.txt
npx remotion studio 2>&1 &
STUDIO_PID=$!
echo "Studio PID: $STUDIO_PID" >> /app/results/studio_start.txt
echo "Studio started; access at http://localhost:3000" >> /app/results/studio_start.txt
```

In an automated context, skip the interactive studio and proceed to the render check instead.

---

## Step 4: Optional — One-Frame Render Check

Render a single frame to sanity-check layout, colors, or timing. Skip for trivial edits, pure refactors, or when you already have enough confidence from Studio or prior renders.

```bash
COMPOSITION_ID="${COMPOSITION_ID:-}"
FRAME="${FRAME:-30}"
SCALE="${SCALE:-0.25}"

if [ -z "$COMPOSITION_ID" ]; then
  echo "COMPOSITION_ID not set — skipping render check" | tee /app/results/render_check.txt
else
  echo "Running one-frame render check: composition=$COMPOSITION_ID frame=$FRAME scale=$SCALE"
  npx remotion still "$COMPOSITION_ID" \
    --scale="$SCALE" \
    --frame="$FRAME" \
    --output=/app/results/still-output.png 2>&1 | tee /app/results/render_check.txt
  echo "Still render complete" >> /app/results/render_check.txt
fi
```

At 30 fps, `--frame=30` is the one-second mark (`--frame` is zero-based).

---

## Step 5: Apply Remotion Best-Practice Rules

Load and apply the appropriate rule files for the task at hand. Each rule file covers a specific Remotion subsystem. Consult the relevant rule based on what you are implementing:

| Subsystem | Rule file | When to load |
|-----------|-----------|--------------|
| Subtitles / captions | `rules/subtitles.md` | Dealing with captions or subtitles |
| FFmpeg operations | `rules/ffmpeg.md` | Trimming videos or other FFmpeg tasks |
| Silence detection | `rules/silence-detection.md` | Detecting and trimming silent segments |
| Audio visualization | `rules/audio-visualization.md` | Spectrum bars, waveforms, bass-reactive effects |
| Sound effects | `rules/sfx.md` | Adding sound effects |
| 3D content | `rules/3d.md` | Three.js / React Three Fiber in Remotion |
| Animations | `rules/animations.md` | Fundamental animation skills |
| Asset loading | `rules/assets.md` | Images, videos, audio, fonts |
| Audio | `rules/audio.md` | Importing, trimming, volume, speed, pitch |
| Dynamic metadata | `rules/calculate-metadata.md` | Dynamic duration, dimensions, props |
| Video decode check | `rules/can-decode.md` | Check if video can be decoded via Mediabunny |
| Charts | `rules/charts.md` | Bar, pie, line, stock charts |
| Compositions | `rules/compositions.md` | Defining compositions, stills, folders |
| Frame extraction | `rules/extract-frames.md` | Extract frames at specific timestamps |
| Fonts | `rules/fonts.md` | Google Fonts and local fonts |
| Audio duration | `rules/get-audio-duration.md` | Get audio file duration via Mediabunny |
| Video dimensions | `rules/get-video-dimensions.md` | Get video width/height via Mediabunny |
| Video duration | `rules/get-video-duration.md` | Get video duration via Mediabunny |
| GIFs | `rules/gifs.md` | GIFs synchronized with Remotion's timeline |
| Images | `rules/images.md` | Embedding images using the Img component |
| Light leaks | `rules/light-leaks.md` | Light leak overlay effects |
| Lottie | `rules/lottie.md` | Embedding Lottie animations |
| DOM measurement | `rules/measuring-dom-nodes.md` | Measuring DOM element dimensions |
| Text measurement | `rules/measuring-text.md` | Measuring text, fitting to containers |
| Sequencing | `rules/sequencing.md` | Delay, trim, limit duration of items |
| TailwindCSS | `rules/tailwind.md` | Using TailwindCSS in Remotion |
| Text animations | `rules/text-animations.md` | Typography and text animation |
| Timing | `rules/timing.md` | interpolate, Bézier easing, springs |
| Transitions | `rules/transitions.md` | Scene transition patterns |
| Transparent video | `rules/transparent-videos.md` | Rendering with transparency |
| Trimming | `rules/trimming.md` | Cutting beginning/end of animations |
| Videos | `rules/videos.md` | Embedding videos — trim, volume, speed |
| Parameters | `rules/parameters.md` | Parametrizable video with Zod schema |
| Maps | `rules/maps.md` | Mapbox map with animation |
| Voiceover | `rules/voiceover.md` | AI-generated voiceover via ElevenLabs TTS |

For each rule applicable to your task, fetch the rule file from the GitHub source and apply its guidance before writing code:

```bash
BASE_RAW="https://raw.githubusercontent.com/remotion-dev/skills/HEAD/skills/remotion"
RULE="${RULE:-animations}"
curl -sSf "$BASE_RAW/rules/$RULE.md" | cat
```

---

## Step 6: Iterate on Errors (max 3 rounds)

If any Remotion CLI command fails or a render produces unexpected output:

1. Read the error output carefully
2. Consult the relevant rule file from Step 5 for the failing subsystem
3. Apply the fix suggested by the rule or by common Remotion troubleshooting patterns
4. Re-run the failing command
5. Repeat up to 3 times total

### Common Fixes

| Issue | Fix |
|-------|-----|
| `composition not found` | Check composition ID spelling; run `npx remotion compositions` to list all |
| Missing Remotion package | Run `npm install @remotion/<package>` for the relevant subpackage |
| FFmpeg not found | Install FFmpeg via system package manager: `apt-get install -y ffmpeg` or `brew install ffmpeg` |
| `ENOMEM` during render | Reduce `--concurrency` flag or lower `--scale` for the still render |
| Blank/black frame | Ensure assets (images, videos, audio) are imported via `staticFile()` not raw paths |
| Font not loading | Use `@remotion/google-fonts` or preload fonts with `continueRender`/`delayRender` |

---

## Step 7: Write Results

Write all required output files and capture final state:

```bash
# Confirm studio and render outputs exist
ls -lh /app/results/ 2>&1

# Write summary
cat > /app/results/summary.md << 'SUMMARY'
# Remotion Best Practices — Run Summary

## Status
Run completed.

## Steps executed
- Environment verified
- Project scaffolded (or existing project detected)
- Remotion Studio started (background or skipped in automated context)
- One-frame render check executed (or skipped)
- Rule files consulted as needed

## Issues
None (update this section if any step failed)
SUMMARY

echo "Results written to /app/results/"
```

---

## Step 8: Final Verification

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/project_scaffold.txt" \
  "$RESULTS_DIR/studio_start.txt" \
  "$RESULTS_DIR/render_check.txt" \
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

---

## Tips

- **Prefer raw sources.** When fetching Remotion rule files from GitHub, always use `raw.githubusercontent.com` URLs — the HTML viewer contains navigation chrome that pollutes content.
- **Rule files are additive.** Load only the rule files relevant to your task; there is no need to load all 30+ rules upfront.
- **`npx remotion still` is cheap.** Use the one-frame render check frequently for quick feedback on layout and timing, using `--scale=0.25` to keep it fast.
- **Use `staticFile()` for all assets.** Remotion's asset system requires that all static assets (images, videos, audio) are referenced via `staticFile('filename')`, not as raw file paths or external URLs — this ensures they are bundled correctly.
- **`delayRender` / `continueRender` for async resources.** Whenever you load fonts, fetch data, or do async work inside a Remotion component, wrap it with `delayRender()` and call `continueRender()` when ready, to prevent the renderer from capturing frames before the resource is available.
- **Attribution.** This runbook was imported from `https://skills.sh/remotion-dev/skills/remotion-best-practices` (source: `remotion-dev/skills` on GitHub). For the most up-to-date rules, consult the upstream repository directly.
