---
version: "1.0.0"
evaluation: rubric
agent: claude-code
model: anthropic/claude-sonnet-4.6
model_provider: openrouter
snapshot: python312-uv
# The headline deliverable — the rendered launch video.
primary_outputs:
  - brag.mp4
origin:
  url: "https://github.com/latent-spaces/brag"
  source_host: "github.com"
  source_title: "/brag — turn the project you built into a short, shareable launch video"
  imported_at: "2026-06-24T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: latent-spaces
    skill_name: brag
    author: "latent-spaces — github.com/latent-spaces/brag"
    license: "unspecified (no LICENSE file in source)"
    confidence: high
secrets:
  GEMINI_API_KEY:
    env: GEMINI_API_KEY
    description: "Optional. Enables Gemini frame analysis on `hyperframes snapshot` for a stronger automated visual gut-check. The render itself needs no API key."
    required: false
---

# /brag — Turn a Project Into a Launch Video — Agent Runbook

> Converted, with attribution, from **/brag** (github.com/latent-spaces/brag) — a Claude Code
> skill that turns the project you built into a short, shareable launch video. The video is
> composed and rendered **locally** with [Hyperframes](https://www.npmjs.com/package/hyperframes)
> (`npx hyperframes`) — headless Chromium + FFmpeg, **no API key required**.

> **EXECUTE THIS RUNBOOK NOW.** Read the project, plan the brag, compose it in Hyperframes, render
> it, and write every deliverable to `{{results_dir}}`. This is a task to perform, not a document
> to summarize. Your first action is a tool call (Step 1). The inputs are already provided below —
> never pause to ask the user for them.

## Inputs (already provided)

- **The project to brag about** — provided one of two ways:
  - **A URL** — {{project_url}} — the live project site. Captured with `npx hyperframes capture`.
  - **Uploaded files** — any project files dropped into `/app/assets/` (e.g. `index.html`,
    `styles.css`, a `README.md`). Used directly when no URL is given.
- **Tone:** {{tone}} — a preset (`default` · `polished` · `yc-parody` · `chaotic` · `deadpan` ·
  `cinematic` · `app-store`) or a freeform direction like *"fake Series A launch from 2016"*.
- **Format:** {{format}} (`landscape` / `vertical` / `square`) · **Duration:** {{duration}} ·
  **Title:** {{title}} · **Music:** {{music}} · **SFX:** {{sfx}}.

## Objective

Turn a project into a short, polished, **shareable launch video** the way `/brag` does: read the
project to understand what it actually is, plan a brag concept *specific to this project* (not a
generic SaaS reel), storyboard it to the brag creative laws, hand a focused brief to **Hyperframes**
to compose it, then render `brag.mp4` and write the share copy. `/brag` owns the story — the
product angle, tone, and which moments to show; Hyperframes owns the concrete composition, timing,
and render.

The deliverable is one **15–25 second** video that lands a hook in the first 2 seconds, shows at
least one **real** UI/copy/visual from the product, keeps every line on screen long enough to read,
and comes with a postable caption. Confident, playful, specific — the work has to back up the brag.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following to `{{results_dir}}`. The task is NOT complete until every
file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `{{results_dir}}/brag.mp4` | The rendered launch video — 15–25s, the planned format, with the audio layer (unless disabled). The headline deliverable. |
| `{{results_dir}}/brag-plan.md` | The creative north star: the angle, hook, key moments, outro, tone, visual identity, audio direction, and a beat-by-beat **storyboard** whose scene durations sum to 15–25s. |
| `{{results_dir}}/composition-brief.md` | The Hyperframes handoff brief — product positioning, source material, copy that must appear verbatim, and the storyboard as the creative contract. |
| `{{results_dir}}/share-copy.txt` | One postable caption (1–3 sentences), tone-matched, specific to the project. No generic "excited to share". |
| `{{results_dir}}/frames/` | A few `hyperframes snapshot` PNG key frames used for the visual self-check (Step 6). |
| `{{results_dir}}/validation_report.json` | Stage-by-stage self-validation with `overall_passed`. See Step 7. |

If you finish but have not written every file, go back and write it.

> **Keep `{{results_dir}}` lean — deliverables only.** Build the Hyperframes project, capture, and
> the source clone all live under **`/tmp`** (see Steps 1–5), NOT in `{{results_dir}}`. The scaffold
> is 800+ files; saving it as run artifacts overruns the platform's upload/heartbeat window and the
> run is retried and fails. Only the files in the table above belong in `{{results_dir}}`.

---

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|------------------|---------|-------------|
| Results directory | `{{results_dir}}` | `/app/results` | Output directory |
| Project URL | `{{project_url}}` | *(required if no uploads)* | The live project to capture and brag about |
| Tone | `{{tone}}` | `default` | A preset or a freeform creative direction |
| Format | `{{format}}` | `landscape` | `landscape` (1920×1080) / `vertical` (1080×1920) / `square` (1080×1080) |
| Duration | `{{duration}}` | `auto` | Target seconds; `auto` picks 15–25s for the tone |
| Title | `{{title}}` | *(inferred)* | Override the product name shown in the video |
| Music | `{{music}}` | `on` | `on` uses a bundled track from the source repo; `off` renders silent |
| SFX | `{{sfx}}` | `on` | `on` adds tasteful motion-matched sound effects; `off` disables them |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `node` ≥ 22 + `npx` | Runtime | Yes | Runs the Hyperframes CLI. Pre-installed on `python312-uv`. |
| `chromium` | Runtime | Yes | Headless render engine. Pre-installed on `python312-uv` (`/usr/bin/chromium`). |
| `ffmpeg` | Runtime | Yes | Encodes the MP4. **Installed in Step 1** (not in the base snapshot). |
| `git` | Runtime | Yes | Clones the source repo for its bundled music/SFX + references. Pre-installed. |
| `hyperframes` (npx) | Runtime | Yes | Composition + render toolchain. Fetched via `npx` at run time. |
| `GEMINI_API_KEY` | Secret | No | Optional frame analysis on `hyperframes snapshot`. |

---

## Step 1: Environment Setup

Verify the toolchain, install FFmpeg (the only missing piece on `python312-uv`), point Hyperframes
at the system Chromium, and clone the **source `/brag` repo** so you have its bundled music + SFX
and step references locally.

```bash
set -e
RESULTS="{{results_dir}}"; mkdir -p "$RESULTS/frames"
echo "node: $(node -v)  (need >= 22)"; node -e 'process.exit(+process.versions.node.split(".")[0] >= 22 ? 0 : 1)'

# Chromium for the headless render (pre-baked on python312-uv). The sandbox has a tiny
# /dev/shm, which crashes Chromium mid-render — so force --disable-dev-shm-usage.
export CHROME_PATH="$(command -v chromium || command -v chromium-browser || echo /usr/bin/chromium)"
export PUPPETEER_EXECUTABLE_PATH="$CHROME_PATH"
export CHROMIUM_FLAGS="--disable-dev-shm-usage --no-sandbox"
export PUPPETEER_ARGS="--disable-dev-shm-usage --no-sandbox"
echo "chromium: $CHROME_PATH"; "$CHROME_PATH" --version || true

# FFmpeg: try apt, fall back to a pip-provided static binary on PATH.
if ! command -v ffmpeg >/dev/null 2>&1; then
  (apt-get update && apt-get install -y --no-install-recommends ffmpeg) 2>/dev/null || {
    pip install -q imageio-ffmpeg
    ln -sf "$(python -c 'import imageio_ffmpeg,os;print(imageio_ffmpeg.get_ffmpeg_exe())')" /usr/local/bin/ffmpeg
  }
fi
ffmpeg -version | head -1

# Source repo: bundled music (assets/music) + the brag references. Clone OUTSIDE
# {{results_dir}} (to /tmp/brag_src) so its hundreds of asset files are NOT saved as run
# artifacts, and sparse-checkout only what we use (skip the heavy docs/examples videos).
SRC_DIR="/tmp/brag_src"
if [ ! -d "$SRC_DIR/.git" ]; then
  git clone --depth 1 --filter=blob:none --sparse https://github.com/latent-spaces/brag "$SRC_DIR" 2>/dev/null \
    && git -C "$SRC_DIR" sparse-checkout set skills/brag/assets skills/brag/references \
    || echo "WARN: could not clone source repo — proceeding without bundled audio (music may be off)"
fi
BRAG_ASSETS="$SRC_DIR/skills/brag/assets"
ls "$BRAG_ASSETS/music"/*.mp3 2>/dev/null | head -1 || echo "(no bundled music — video will render silent)"

# Install the Hyperframes + GSAP authoring skills for this agent, and confirm the toolchain.
npx -y hyperframes@latest skills 2>/dev/null || true
npx -y hyperframes@latest doctor || echo "NOTE: doctor flagged items — address any 'missing' before render"
```

`doctor` must show Node ≥ 22, Chromium, and FFmpeg available. If FFmpeg is still missing after the
fallback, STOP and report it — the render cannot produce an MP4 without it.

---

## Step 2: Inspect the Project (answer the 9-question rubric)

Get the source material. If `{{project_url}}` is set, capture it; otherwise read the uploaded files
in `/app/assets/`.

```bash
# Capture into /tmp (intermediate, outside {{results_dir}}) so it isn't saved as run artifacts.
SRC="/tmp/brag_source"; mkdir -p "$SRC"
if [ -n "{{project_url}}" ] && [ "{{project_url}}" != "" ]; then
  ( cd "$SRC" && npx -y hyperframes@latest capture "{{project_url}}" ) \
    || curl -fsSL "{{project_url}}" -o "$SRC/index.html"   # fallback: raw HTML
else
  cp -r /app/assets/* "$SRC"/ 2>/dev/null || true
fi
echo "=== source material (in /tmp/brag_source) ==="; ls -R "$SRC" | head -40
```

Now **read** the source the way `/brag`'s Step 1 does — `index.html` first (title, hero headline,
tagline, section headings, CTA, testimonials), then `styles.css` (palette via `:root` custom
properties, display + body fonts), then any README / routed screens for the *product in use*.
Answer all nine questions in writing (they drive the plan):

1. **What is the app?** One sentence — what it actually does (or claims to).
2. **Funniest / most impressive claim?** The one line that earns a reaction.
3. **Visual hook?** The strongest CSS visual — a palette moment, a card, a UI element.
4. **What real UI should be shown?** The most video-worthy section.
5. **Shortest satisfying length?** 15s? 20? The minimum to land the joke/claim.
6. **Tone?** Use `{{tone}}` if given; else infer a preset **and** a one-line creative direction.
7. **Audio feel?** Music role + likely SFX moments (bias toward a polished layer unless disabled).
8. **Share caption?** Draft one sentence — it becomes `share-copy.txt`.
9. **The user flow worth showing?** The 2–3 beats of *using* the product (entry → key action →
   result), pulled from routes/components — not the landing page's section list. If it's a
   landing-page-only static site, write "none — landing-page only" and lean on the strongest visual.

Record the exact background / text / accent colors and the display + body fonts — they become the
video's visual identity. **Gate:** you can answer all nine.

---

## Step 3: Plan & Storyboard → `brag-plan.md`

Write `{{results_dir}}/brag-plan.md` — one focused page, the creative contract. It specifies what
the video must communicate and which project material to use; it does **not** prescribe Hyperframes
implementation details. Structure: *What is this app · The angle · Hook (first 2–3s) · Key moments ·
Outro/punchline · User flow worth showing · Tone (preset + creative direction + interpretation) ·
Format + Duration · Visual identity (exact colors + fonts + strongest element) · Share copy (draft)
· Audio direction · Storyboard (scene-by-scene)*.

**Scene count + pacing by tone** (the pattern `Hook → Reveal → 2–3 highlights → Punchline`, adapted):

| Tone | Scenes | Pacing |
|---|---|---|
| `default` | 4–5 | Comfortable; each moment breathes |
| `polished` | 3–4 | Fewer scenes, longer holds — restraint |
| `yc-parody` | 4–5 | Structured; the joke is the straight delivery |
| `chaotic` | 6–8 | Rapid; some scenes < 2s |
| `deadpan` | 3–4 | Long holds, big empty space, one thought at a time |
| `cinematic` | 4–5 | Wide shots, big type, dramatic reveals |
| `app-store` | 4–6 | Feature cards, clean reveals |

**Reading-time floor (non-negotiable):** keep pace through motion and cuts, **never** by flashing
text. A short label needs ~0.8s settled; a sentence ~0.3s/word (min ~1.2s; the hook gets the most).
Fast-in, then **hold** — never fast-in, then gone. If a scene carries more text than its duration
allows, cut copy or split the scene; do not speed it up.

**Bias the centerpiece to the user flow** (Q9). If the product has a real flow, the centerpiece
scenes show the working app (cursor drops a file → progress fills → result thumbnails pop in), not a
diagram of what it does. Stat cards / hero blocks frame the flow, at most one, not as a substitute.
Look for **sequential reveals** (cards/stats one-by-one) and **simulated interaction** (a click, a
swipe, typing) and commit to them explicitly in the scene description — they make the product feel
alive.

**Gate:** `brag-plan.md` exists with a full storyboard; scene durations **sum to 15–25s** (count them).

---

## Step 4: Compose with Hyperframes → `composition/`

Write `{{results_dir}}/composition-brief.md` (the boundary: positioning/copy/tone/source/moments are
yours; structure/timing/mechanics are Hyperframes'), then scaffold and build the composition.

```bash
# Build the composition in a WORK dir OUTSIDE results. The Hyperframes scaffold (node_modules,
# assets, captured fonts) is 800+ files — saving it as run artifacts overruns the upload/heartbeat
# window and the run is retried and fails. Only deliverables go to {{results_dir}}.
WORK="/tmp/brag_work"; mkdir -p "$WORK"; cd "$WORK"
case "{{format}}" in
  vertical) DIM="1080x1920";; square) DIM="1080x1080";; *) DIM="1920x1080";;
esac
npx -y hyperframes@latest init composition --format "$DIM" 2>/dev/null \
  || npx -y hyperframes@latest init composition

# Audio: copy a bundled track in (unless music is off), so the render has a local asset.
# (Source repo was sparse-cloned to /tmp/brag_src in Step 1 — NOT into results.)
if [ "{{music}}" != "off" ] && [ -d "/tmp/brag_src/skills/brag/assets/music" ]; then
  mkdir -p "$WORK/composition/assets/music"
  cp "$(ls /tmp/brag_src/skills/brag/assets/music/*.mp3 | head -1)" "$WORK/composition/assets/music/" || true
fi
```

Now author the composition in `/tmp/brag_work/composition/` following the **HyperFrames skill**
(installed in Step 1) and the brief. Apply the brag creative laws: show at least one real UI/copy/visual
from the project; keep every line readable; stay 15–25s; use the project's actual palette + fonts. If
music is on, detect beats (`npx hyperframes beats /tmp/brag_work/composition/assets/music/<track>.mp3`)
and **beat-lock 1–3 major reveals** (±0.15s) and snap sequential, non-text accents to the beat grid —
but never outrun the reading-time floor. Match transitions to tone (hard cuts for `chaotic`/`yc-parody`,
slow crossfades for `deadpan`/`polished`).

> **Avoid the lint rejections seen in practice:**
> - **Fonts:** `hyperframes lint` **rejects external font imports** (Google Fonts `@import`/`<link>`).
>   Use the fonts the capture saved locally (under `/tmp/brag_source/capture/`) via `@font-face`, or
>   fall back to a system font stack. Never `@import` a web-font CDN.
> - **Timelines:** give every animated element a hard initial state (a `gsap.set`/`tl.set` at t=0)
>   so nothing flashes pre-animation; register every timeline. These are the two errors `lint` flags
>   most. The "track density" message is an advisory **warning**, not a blocker — ignore it for a
>   short single-file video.
> - The capture's extracted material is at `/tmp/brag_source/capture/extracted/` —
>   `visible-text.txt`, `tokens.json` (palette + fonts), `asset-descriptions.md`. Read those for the
>   real copy, colors, and fonts instead of guessing.

```bash
cd /tmp/brag_work/composition && npx -y hyperframes@latest lint
```

**Gate:** `npx hyperframes lint` passes with **zero errors** inside `composition/`. Fix anything it
flags (track overlaps, unregistered timelines, missing ids) before rendering.

---

## Step 5: Render → `brag.mp4`

Optionally inspect layout/overflow, then render the composition (in `/tmp`) straight to the **MP4 in
`{{results_dir}}`** — the video is the only large file that belongs in results.

```bash
RESULTS="{{results_dir}}"; cd /tmp/brag_work/composition
export CHROME_PATH="$(command -v chromium || echo /usr/bin/chromium)"; export PUPPETEER_EXECUTABLE_PATH="$CHROME_PATH"
export CHROMIUM_FLAGS="--disable-dev-shm-usage --no-sandbox"; export PUPPETEER_ARGS="--disable-dev-shm-usage --no-sandbox"
npx -y hyperframes@latest inspect  || true   # text/container overflow across the timeline
# Default to DRAFT quality: a frame-by-frame high render can blow the 30-min agent timeout in the
# sandbox. Draft is fast, reliable, and fine for a short social clip.
npx -y hyperframes@latest render --quality draft -o "$RESULTS/brag.mp4" \
  || npx -y hyperframes@latest render -o "$RESULTS/brag.mp4"
ls -la "$RESULTS/brag.mp4"
# duration sanity (must land 15–25s)
ffprobe -v error -show_entries format=duration -of csv=p=0 "$RESULTS/brag.mp4" || true
```

**Gate:** `{{results_dir}}/brag.mp4` exists, is non-empty, and `ffprobe` reports a duration in the
15–25s window. Only retry at `--quality high` if there is time budget left and draft looked rough.

---

## Step 6: Snapshot Key Frames + Visual Self-Check

Capture a few key frames and look at them — this backstops the "show the thing" and "keep text
readable" creative laws without watching the whole render.

```bash
RESULTS="{{results_dir}}"; cd /tmp/brag_work/composition
npx -y hyperframes@latest snapshot --output "$RESULTS/frames" || \
  npx -y hyperframes@latest snapshot   # writes PNG key frames (Gemini analysis if GEMINI_API_KEY set)
ls "$RESULTS/frames"/*.png 2>/dev/null | head
```

Open the frames. Confirm: the hook frame reads in isolation; at least one frame shows **real**
product UI/copy (not abstract filler); no frame has clipped or unreadable text; the palette matches
the project. If a frame fails, fix the composition (Step 4) and re-render (Step 5) — up to 2 rounds.

---

## Step 7: Share Copy + Validation Report

First, **prune `{{results_dir}}` to deliverables only.** If the composition, capture, clone, or any
`node_modules` leaked into results, saving hundreds of artifacts overruns the platform's
upload/heartbeat window and the whole run is retried and then fails — even though `brag.mp4`
rendered fine. This guard removes anything that is not a known deliverable:

```bash
RESULTS="{{results_dir}}"; cd "$RESULTS"
find . -maxdepth 1 -mindepth 1 \
  ! -name 'brag.mp4' ! -name 'brag-plan.md' ! -name 'composition-brief.md' \
  ! -name 'share-copy.txt' ! -name 'validation_report.json' ! -name 'frames' \
  -exec rm -rf {} + 2>/dev/null || true
echo "results now holds $(find . -type f | wc -l | tr -d ' ') files (expect < 30):"; ls -la "$RESULTS"
```

Then write `{{results_dir}}/share-copy.txt` — one postable caption (1–3 sentences), tone-matched,
specific to the project, no generic "excited to share". (Multi-platform variants, if any, go in a
separate `share-copy-variants.md` — keep `share-copy.txt` to the single canonical caption.)

Then write `{{results_dir}}/validation_report.json`:

```json
{
  "version": "1.0.0", "run_date": "<ISO>",
  "source": "latent-spaces/brag",
  "parameters": {"tone": "{{tone}}", "format": "{{format}}", "music": "{{music}}", "sfx": "{{sfx}}"},
  "stages": [
    {"name": "setup",    "passed": true, "message": "node>=22, chromium, ffmpeg, hyperframes ready"},
    {"name": "inspect",  "passed": true, "message": "9-question rubric answered from source"},
    {"name": "plan",     "passed": true, "message": "brag-plan.md storyboard sums to 15-25s"},
    {"name": "compose",  "passed": true, "message": "hyperframes lint passed, 0 errors"},
    {"name": "render",   "passed": true, "message": "brag.mp4 rendered"},
    {"name": "deliver",  "passed": true, "message": "share-copy.txt written"}
  ],
  "results": {"duration_seconds": 0.0, "format": "{{format}}", "tone": "{{tone}}",
              "shows_real_ui": true, "music": "{{music}}"},
  "overall_passed": false
}
```

`overall_passed` is `true` **iff**: `hyperframes lint` passed, `brag.mp4` exists with a duration in
15–25s, `brag-plan.md` + `composition-brief.md` + `share-copy.txt` all exist, and a snapshot frame
shows real product UI/copy.

---

## Rubric (how the brag is judged)

| # | Criterion | 5 (Excellent) | 3 (Acceptable) | 1 (Poor) |
|---|-----------|---------------|-----------------|----------|
| 1 | **Hook** | First 2s land a specific, attention-earning moment | A hook exists but is generic | Slow/no hook; opens on a logo or filler |
| 2 | **Specificity** | Feels made for *this* project — its copy, palette, claims | Mostly specific, some generic filler | Could be any product's reel |
| 3 | **Shows the thing** | ≥1 scene shows real product UI/copy/flow (the app in use) | Shows a recreated UI element | Abstract patterns / color washes only |
| 4 | **Readability** | Every line holds long enough to read; pace from motion | One or two lines a touch fast | Text flashes by; unreadable |
| 5 | **Craft & length** | 15–25s, tone-true pacing, clean transitions, polished audio layer | In range but uneven pacing/audio | Out of range or sloppy/jarring |

"Streamline your workflow" and generic SaaS language are banned (criterion 2). Humor, when present,
must come from the project's own absurdity — not from trying to be funny.

---

## Final Checklist (MANDATORY — do not skip)

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="{{results_dir}}"; FAIL=0
for f in brag.mp4 brag-plan.md composition-brief.md share-copy.txt validation_report.json; do
  if [ -s "$RESULTS_DIR/$f" ]; then echo "PASS: $f ($(wc -c < "$RESULTS_DIR/$f") bytes)";
  else echo "FAIL: $f missing/empty"; FAIL=$((FAIL+1)); fi
done
# Results must stay LEAN — deliverables only (composition is built in /tmp, not saved as artifacts).
NF=$(find "$RESULTS_DIR" -type f 2>/dev/null | wc -l | tr -d ' '); echo "result files: $NF (expect < 30)"
[ "$NF" -lt 60 ] || { echo "FAIL: $NF files in results — composition/ leaked in? build it under /tmp"; FAIL=$((FAIL+1)); }
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$RESULTS_DIR/brag.mp4" 2>/dev/null | cut -d. -f1)
echo "brag.mp4 duration: ${DUR:-?}s"
{ [ -n "$DUR" ] && [ "$DUR" -ge 15 ] && [ "$DUR" -le 26 ]; } || { echo "FAIL: duration outside 15-25s"; FAIL=$((FAIL+1)); }
FR=$(ls "$RESULTS_DIR"/frames/*.png 2>/dev/null | wc -l | tr -d ' '); echo "key frames: $FR"
[ "$FR" -ge 1 ] || { echo "FAIL: no snapshot frames"; FAIL=$((FAIL+1)); }
[ "$FAIL" -gt 0 ] && { echo "OVERALL: FAIL ($FAIL)"; exit 1; }; echo "OVERALL: PASS"
```

### Checklist

- [ ] Toolchain ready: Node ≥ 22, Chromium, FFmpeg, Hyperframes (`doctor` clean)
- [ ] All nine inspection questions answered from the project's real source
- [ ] `brag-plan.md` storyboard scene durations sum to 15–25s
- [ ] `composition-brief.md` written; `hyperframes lint` passed with zero errors
- [ ] `brag.mp4` rendered; `ffprobe` duration is 15–25s
- [ ] ≥1 snapshot frame shows real product UI/copy (not abstract filler)
- [ ] `share-copy.txt` is one tone-matched, project-specific caption
- [ ] `{{results_dir}}` holds **only** deliverables (< 30 files) — composition/clone/capture stayed in `/tmp`
- [ ] Verification script printed `OVERALL: PASS`

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **The hook is everything.** Plan the first 2 seconds before anything else — they decide whether
  anyone watches the other 20. A logo is not a hook.
- **Show the thing.** The strongest material is the product *in use* (the flow from Q9), not its
  marketing of itself. Recreate a working-app moment before reaching for stat cards.
- **Pace with motion, not by hiding text.** Lines can SLAM in fast and then HOLD — fast-in plus an
  adequate hold reads as punchy *and* legible. Flashing text just reads as broken.
- **Specific over generic, always.** Use the project's real copy, palette, and claims. If a line
  could belong to any product's launch reel, cut it.
- **Audio is part of the polish.** Default to a music bed + tasteful, motion-matched SFX from the
  source repo's bundled assets; beat-lock the big reveals. Go silent only when the user disabled
  audio or silence is genuinely the stronger choice.
- **Let Hyperframes own the mechanics.** Give it the story, copy, tone, and moments; let it choose
  the composition structure, exact timing, and render. Run `lint` before every render.
- **Results = deliverables only (load-bearing).** Do all heavy work in `/tmp` (clone → `/tmp/brag_src`,
  capture → `/tmp/brag_source`, composition → `/tmp/brag_work`). The Hyperframes scaffold alone is
  800+ files; if it lands in `{{results_dir}}`, the artifact upload overruns the run's heartbeat
  window, the activity is retried, and a perfectly-good render is reported as a failure. The Step 7
  prune is the safety net — don't rely on it; keep results clean by construction.
- **Render `--quality draft`.** A high frame-by-frame render can exceed the 30-min agent budget;
  draft renders in a couple of minutes and looks fine for a 20s social clip.
