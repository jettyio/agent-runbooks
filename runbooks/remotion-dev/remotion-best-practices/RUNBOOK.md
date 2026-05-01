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
  imported_at: "2026-05-01T02:58:14Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "remotion-dev"
    skill_name: "remotion-best-practices"
    confidence: "high"
secrets: {}
---

# remotion-best-practices — Agent Runbook

## Objective

This runbook implements best practices for building video compositions with Remotion and React. Best practices for Remotion - Video creation in React. It covers project scaffolding, live preview, single-frame sanity checks, captioning, FFmpeg operations, audio visualization, sound effects, and a comprehensive library of domain-specific rule files for 30+ Remotion topics including animations, 3D, charts, typography, transitions, and AI voiceovers. Use this runbook whenever working on Remotion-based video projects to apply the correct patterns and avoid common pitfalls.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `/app/results`.
The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `/app/results/summary.md` | Executive summary of the runbook execution, steps taken, and outcomes |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |

If you finish your work but have not written all files, go back and write them before stopping.

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results |
| Project name | `my-video` | Name for a new Remotion project (used in scaffold command) |
| Composition ID | *(required for render)* | The Remotion composition identifier to render |
| Render frame | `30` | Frame number for one-frame sanity check (`--frame` is zero-based; frame 30 ≈ 1 second at 30 fps) |
| Render scale | `0.25` | Scale factor for sanity-check still render |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `node` / `npm` | Runtime | Yes | Node.js runtime for all Remotion CLI commands |
| `npx` | CLI | Yes | Used to invoke `create-video`, `remotion studio`, and `remotion still` |
| `ffmpeg` | CLI | Conditional | Required for video trimming, silence detection, and loudnorm operations |
| Remotion project | Workspace | Yes | An existing or newly scaffolded Remotion project directory |
| ElevenLabs API key | Secret | Conditional | Required only when generating AI voiceovers |

## Step 1: Environment Setup

Verify the required tools are available and the workspace is ready.

```bash
# Check Node and npx
node --version || { echo "ERROR: node not installed"; exit 1; }
npx --version  || { echo "ERROR: npx not installed"; exit 1; }

# Optional: check ffmpeg (required for silence detection and trimming)
command -v ffmpeg && echo "ffmpeg available" || echo "WARN: ffmpeg not found — some rules will be unavailable"

# Create results directory
mkdir -p /app/results
```

## Step 2: New Project Setup (Skip if project already exists)

Use this skills whenever you are dealing with Remotion code to obtain the domain-specific knowledge.

When in an empty folder or workspace with no existing Remotion project, scaffold one:

```bash
npx create-video@latest --yes --blank --no-tailwind my-video
cd my-video
npm install
```

Replace `my-video` with a suitable project name.

## Step 3: Start Preview

Start the Remotion Studio to preview compositions live:

```bash
npx remotion studio
```

Remotion Studio opens a browser at `http://localhost:3000` and hot-reloads on file changes.

## Step 4: One-Frame Render Check (Optional)

Run a one-frame render to sanity-check layout, colors, and timing before a full render.
Skip for trivial edits, pure refactors, or when confidence is already high from Studio.

```bash
npx remotion still [composition-id] --scale=0.25 --frame=30
```

At 30 fps, `--frame=30` is the one-second mark (`--frame` is zero-based).

## Step 5: Apply Domain-Specific Rules

Load the relevant rule files from the `rules/` directory based on your task. Each file provides detailed explanations and code examples:

| Rule file | Topic |
|-----------|-------|
| `rules/3d.md` | 3D content using Three.js and React Three Fiber |
| `rules/animations.md` | Fundamental animation patterns |
| `rules/assets.md` | Importing images, videos, audio, and fonts |
| `rules/audio.md` | Audio: importing, trimming, volume, speed, pitch |
| `rules/calculate-metadata.md` | Dynamic composition duration, dimensions, and props |
| `rules/can-decode.md` | Check browser video decodability via Mediabunny |
| `rules/charts.md` | Bar, pie, line, and stock chart patterns |
| `rules/compositions.md` | Compositions, stills, folders, default props |
| `rules/extract-frames.md` | Frame extraction at specific timestamps via Mediabunny |
| `rules/fonts.md` | Google Fonts and local fonts |
| `rules/get-audio-duration.md` | Audio duration via Mediabunny |
| `rules/get-video-dimensions.md` | Video width/height via Mediabunny |
| `rules/get-video-duration.md` | Video duration via Mediabunny |
| `rules/gifs.md` | GIFs synchronized with Remotion's timeline |
| `rules/images.md` | Embedding images with the `Img` component |
| `rules/light-leaks.md` | Light leak overlay effects (`@remotion/light-leaks`) |
| `rules/lottie.md` | Lottie animations in Remotion |
| `rules/measuring-dom-nodes.md` | DOM element dimension measurement |
| `rules/measuring-text.md` | Text dimensions, container fitting, overflow |
| `rules/sequencing.md` | Delay, trim, and duration limiting |
| `rules/tailwind.md` | TailwindCSS integration |
| `rules/text-animations.md` | Typography and text animation patterns |
| `rules/timing.md` | `interpolate`, Bézier easing, and springs |
| `rules/transitions.md` | Scene transition patterns |
| `rules/transparent-videos.md` | Transparency output rendering |
| `rules/trimming.md` | Trimming: cut beginning or end of animations |
| `rules/videos.md` | Embedding videos: trimming, volume, speed, looping, pitch |
| `rules/parameters.md` | Parametrizable videos with Zod schemas |
| `rules/maps.md` | Mapbox map integration and animation |
| `rules/silence-detection.md` | Adaptive silence detection via FFmpeg |
| `rules/voiceover.md` | AI-generated voiceover via ElevenLabs TTS |

### Captions and Subtitles

When dealing with captions or subtitles, load `./rules/subtitles.md` for detailed guidance.

### FFmpeg Operations

For video trimming, silence detection, or audio normalization, FFmpeg must be available:

```bash
command -v ffmpeg || { echo "ERROR: ffmpeg required for this operation"; exit 1; }
```

Load `./rules/ffmpeg.md` for operation-specific patterns.

### Silence Detection

When trimming silent segments from video or audio:

```bash
# Load the silence detection rule for detailed FFmpeg loudnorm + silencedetect patterns
# See: rules/silence-detection.md
```

### Audio Visualization

For spectrum bars, waveforms, or bass-reactive effects, load `./rules/audio-visualization.md`.

### Sound Effects

For sound effect integration, load `./rules/sfx.md`.

## Step 6: Iterate on Errors (max 3 rounds)

If the Remotion Studio or render fails:

1. Read the error output carefully
2. Identify the failing component or rule from Step 5
3. Load the relevant rule file and apply the fix
4. Re-run the failing command
5. Repeat up to 3 times total

After 3 rounds, if the issue persists, document the blocker in `/app/results/summary.md` and exit.

### Common Fixes

| Issue | Fix |
|-------|-----|
| `Cannot find module` | Run `npm install` in the project root; check `rules/assets.md` for import patterns |
| Composition not rendering | Verify composition ID matches `defaultProps`; see `rules/compositions.md` |
| Audio out of sync | Check `startFrom`/`endAt` props; see `rules/audio.md` |
| FFmpeg not found | Install ffmpeg or skip FFmpeg-dependent operations |
| Slow render | Use `--scale=0.25` for quick checks; avoid heavy computations in render loop |
| Font not loading | Follow `rules/fonts.md` — fonts must be loaded via `loadFont()` before use |

## Step 7: Write Results

Write the output files required by this runbook.

```bash
# Write summary
cat > /app/results/summary.md << 'SUMMARY'
# Remotion Best Practices — Execution Summary

## Run Date
$(date -u +%Y-%m-%dT%H:%M:%SZ)

## Steps Completed
- [ ] Environment verified
- [ ] Project scaffolded or existing project detected
- [ ] Preview started (if applicable)
- [ ] One-frame render check (if applicable)
- [ ] Domain rules applied
- [ ] Errors resolved

## Outcomes
<!-- Describe what was built or fixed -->

## Issues
<!-- Document any unresolved issues -->
SUMMARY

echo "summary.md written"
```

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
echo "=== DONE ==="
```

### Checklist

- [ ] Remotion project is scaffolded or existing project is detected
- [ ] Remotion Studio starts without errors (`npx remotion studio`)
- [ ] One-frame render passes (if applicable)
- [ ] All domain-specific rules reviewed and applied for the task
- [ ] `/app/results/summary.md` exists and describes the work done
- [ ] `/app/results/validation_report.json` exists with `overall_passed` field
- [ ] Verification script printed PASS for every file

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

## Tips

- **Load rule files on demand.** This skill bundles 30+ rule files — load only the ones relevant to your current task to avoid context bloat.
- **Prefer `npx remotion studio` over `npx remotion render` for iteration.** Studio gives instant feedback without a full render cycle.
- **Frame numbers are zero-based.** At 30 fps, frame 30 = second 1, frame 60 = second 2.
- **Scaffold with `--blank --no-tailwind` for clean starts.** Add TailwindCSS later via `rules/tailwind.md` if needed.
- **FFmpeg is optional but powerful.** If FFmpeg is unavailable, skip silence detection and trimming steps; note the limitation in `summary.md`.
- **Parametrize compositions with Zod.** For reusable, data-driven videos, see `rules/parameters.md` to add type-safe props.
- **AI voiceover requires ElevenLabs credentials.** See `rules/voiceover.md` and ensure the API key is available before starting.
