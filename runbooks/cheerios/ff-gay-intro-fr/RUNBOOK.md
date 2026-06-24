---
version: "1.0.0"
evaluation: rubric
agent: opencode
model: anthropic/claude-sonnet-4.6
model_provider: openrouter
snapshot: python312-uv
secrets:
  REPLICATE_API_TOKEN:
    env: REPLICATE_API_TOKEN
    description: "Replicate API token. Used to call bytedance/seedance-2.0 for video and google/nano-banana for keyframe generation. Get one at https://replicate.com/account/api-tokens."
    required: true
---

# Fast & Furious — Intro Gay (FR) — Agent Runbook

## Objective

Generate a 30-second French-language opening scene in the spirit of *The Fast and the Furious*, reimagined with an openly queer/gay aesthetic — leather, chrome, neon, slow homoerotic camera work, two male leads exchanging charged looks across rumbling muscle cars at dusk. The agent writes a tight bilingual treatment (French dialogue + English camera notes), produces two chained 15-second video clips via `bytedance/seedance-2.0` on Replicate, and uses `google/nano-banana` to generate consistent character keyframes that bridge the cut. Final output is a single stitched 30-second `.mp4` with French audio, scored against a 5-criterion rubric covering script quality, video consistency, queer-aesthetic execution, French-language fidelity, and overall cinematic impact.

---

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following files to `{{results_dir}}`.
The task is NOT complete until every file exists and is non-empty. No exceptions.**

| File | Description |
|------|-------------|
| `{{results_dir}}/intro_30s.mp4` | Final 30-second stitched opener with French audio (the deliverable) |
| `{{results_dir}}/clip_01.mp4` | First 15s clip (downloaded from Replicate) |
| `{{results_dir}}/clip_02.mp4` | Second 15s clip (downloaded from Replicate) |
| `{{results_dir}}/keyframe_opening.png` | Nano Banana keyframe used as the start of clip 1 |
| `{{results_dir}}/keyframe_bridge.png` | Nano Banana keyframe used as the end of clip 1 / start of clip 2 |
| `{{results_dir}}/keyframe_closing.png` | Nano Banana keyframe used as the end of clip 2 |
| `{{results_dir}}/script.md` | Bilingual treatment: French dialogue/voice-over + English camera/staging notes, scene-by-scene |
| `{{results_dir}}/summary.md` | Executive summary with rubric scores, iteration history, and recommendations |
| `{{results_dir}}/validation_report.json` | Structured validation results with rubric scores and `overall_passed` |

If you finish your work but have not written all files, go back and write them before stopping.

---

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|------------------|---------|-------------|
| Results directory | `{{results_dir}}` | `/app/results` | Output directory for all artifacts |
| Resolution | `{{resolution}}` | `1080p` | Seedance output resolution. One of `480p`, `720p`, `1080p`. |
| Aspect ratio | `{{aspect_ratio}}` | `21:9` | Cinemascope-ish framing for the F&F feel. One of `16:9`, `21:9`, `1:1`, etc. |
| Setting | `{{setting}}` | `"Marseille port at golden hour, rain-slick docks, neon signs reflecting in puddles"` | The location/mood. Override for a different city or time of day. |
| Lead 1 description | `{{lead_1}}` | `"early 30s, North African-French, shaved fade, gold chain, black leather jacket over bare chest, fingerless gloves"` | Reference description for the first male lead. |
| Lead 2 description | `{{lead_2}}` | `"late 20s, ash-blond, jawline, white tank top, faded denim, silver crucifix, smudged eyeliner"` | Reference description for the second male lead. |
| Car 1 | `{{car_1}}` | `"matte-black 1970 Dodge Charger with violet underglow"` | First hero car. |
| Car 2 | `{{car_2}}` | `"candy-pink Toyota Supra Mk4 with chrome wheels"` | Second hero car. |

---

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| `REPLICATE_API_TOKEN` | Credential | Yes | Authenticates calls to `bytedance/seedance-2.0` and `google/nano-banana` |
| `bytedance/seedance-2.0` | External API | Yes | Image-to-video with `image` (start) + `last_frame_image` (end) + native audio |
| `google/nano-banana` | External API | Yes | Keyframe generation/editing for character & scene consistency across the cut |
| `replicate` | Python package | Yes | Replicate Python SDK |
| `requests` | Python package | Yes | For downloading generated assets |
| `ffmpeg` | System binary | Yes | Concatenate the two 15s clips into a single 30s mp4 |

---

## Step 1: Environment Setup

```bash
# Install Python deps
pip install replicate requests

# Verify ffmpeg is on PATH (pre-installed on python312-uv snapshot)
which ffmpeg || { echo "ERROR: ffmpeg not found"; exit 1; }

# Create output directory
mkdir -p {{results_dir}}

# Verify required secret
if [ -z "$REPLICATE_API_TOKEN" ]; then
  echo "ERROR: REPLICATE_API_TOKEN is not set. Add it to the cheerios collection environment on Jetty (or export locally)."
  exit 1
fi

# Smoke-test the token: list models the token can see
python -c "import replicate, os; r = replicate.Client(api_token=os.environ['REPLICATE_API_TOKEN']); print('Replicate auth OK')"
```

If the smoke test fails with 401, the token is missing or invalid. If it fails with a timeout, check network egress from the sandbox.

---

## Step 2: Write the Bilingual Treatment

Draft `{{results_dir}}/script.md` before generating any video. The script is what every downstream evaluation hinges on — do not skip this step.

Structure the script as **two acts**, one per clip:

```markdown
# Fast & Furious — Intro Gay (FR)

## Logline (FR)
{One sentence in French capturing the hook}

## Act 1 (0:00 – 0:15) — "L'arrivée"
**Setting**: {{setting}}
**Camera**: {English staging notes — lens, movement, light}
**Action**: {English beat sheet}
**Voice-over / Dialogue (FR)**:
> {French line 1}
> {French line 2}

## Act 2 (0:15 – 0:30) — "Le regard"
**Setting**: {{setting}}, slight time elapsed
**Camera**: {English staging notes}
**Action**: {English beat sheet}
**Voice-over / Dialogue (FR)**:
> {French line 1}
> {French line 2}

## Character Bible
- **Lead 1**: {{lead_1}}
- **Lead 2**: {{lead_2}}
- **Car 1**: {{car_1}}
- **Car 2**: {{car_2}}

## Vibe Notes
- Queer-coded: lingering looks, hands brushing, a shared cigarette, no explicit content
- F&F signature: low-angle car worship, slow-mo, engine snarl, family-coded loyalty
- Color palette: deep magenta + cyan + amber sodium light
```

Requirements:
- All spoken dialogue and voice-over **must be idiomatic, natural French** — not translated English. Aim for verlan/slang sparingly, but make it sound like French cinema, not a dub.
- Each act must be ≤15 seconds spoken — keep lines short (≤8 words each), max 2 lines per act.
- The "gay" element is **aesthetic and emotional** (looks, framing, charged silence) — no explicit content. This is an opener, not a scene.
- Camera notes in English so Seedance can use them as part of the prompt.

---

## Step 3: Generate Keyframes with Nano Banana

Generate three keyframes that lock in character + car + lighting consistency across the cut. The model is `google/nano-banana` (image input/output, supports editing prompts).

For each keyframe, build a prompt that bakes in:
- The character bible (lead 1, lead 2 descriptions)
- The car descriptions
- The setting
- The specific framing for that beat
- A consistent color palette / lens / film stock cue (e.g. "shot on Kodak Vision3 500T, anamorphic, magenta-cyan grade")

```python
import os, replicate, requests
from pathlib import Path

client = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])
results_dir = Path("{{results_dir}}")

def gen_keyframe(prompt: str, out_path: Path, reference_image: str | None = None):
    """Call nano-banana. For the bridge and closing frames, pass the previous frame as
    image_input so the model edits in-place rather than re-rolling characters."""
    inputs = {"prompt": prompt}
    if reference_image:
        inputs["image_input"] = [reference_image]
    output = client.run("google/nano-banana", input=inputs)
    # nano-banana returns a single image URL (or a FileOutput object in newer SDKs)
    url = str(output) if hasattr(output, "url") is False else output.url
    out_path.write_bytes(requests.get(url, timeout=60).content)
    return out_path

# Keyframe 1 — opening: wide, both leads + cars in frame, dusk
opening_prompt = """
Cinematic film still, 21:9 anamorphic, Marseille port at golden hour, rain-slick docks,
neon signs reflecting in puddles. In the foreground: a matte-black 1970 Dodge Charger
with violet underglow on the left, a candy-pink Toyota Supra Mk4 with chrome wheels on
the right, both idling. Standing between the two cars, facing each other in profile:
Lead 1 (early 30s, North African-French, shaved fade, gold chain, black leather jacket
over bare chest, fingerless gloves) and Lead 2 (late 20s, ash-blond, white tank top,
faded denim, silver crucifix, smudged eyeliner). Deep magenta and cyan light. Shot on
Kodak Vision3 500T, shallow depth of field, light haze, gentle rain.
"""
gen_keyframe(opening_prompt, results_dir / "keyframe_opening.png")

# Keyframe 2 — bridge: tight on the two leads' faces, shared look. Pass keyframe 1 to lock identity.
bridge_prompt = """
Edit the scene so the camera pushes in to a tight two-shot of the same two men, eyes
locked, the pink Supra's headlight bloom just behind them. Keep the exact same faces,
hair, jewelry, and wardrobe. Magenta-cyan grade. Anamorphic 21:9.
"""
gen_keyframe(bridge_prompt, results_dir / "keyframe_bridge.png",
             reference_image=str(results_dir / "keyframe_opening.png"))

# Keyframe 3 — closing: low-angle hero shot, both cars roaring off side by side, leads in driver seats
closing_prompt = """
Edit the scene to a low-angle hero shot: both cars now driving side-by-side toward camera
on the wet dock at night, headlights blazing, the same two men visible in their respective
driver seats (Lead 1 in the Charger on the left, Lead 2 in the Supra on the right).
Identical faces and wardrobe as before. Heavy motion blur on the wheels, deep magenta and
cyan neon reflections, anamorphic 21:9.
"""
gen_keyframe(closing_prompt, results_dir / "keyframe_closing.png",
             reference_image=str(results_dir / "keyframe_bridge.png"))
```

After this step, **open each PNG and visually inspect**: same faces? same jewelry? same cars? If any drift, regenerate that specific frame with a stronger reference prompt before moving on.

---

## Step 4: Generate Two 15-Second Clips with Seedance 2.0

Use `bytedance/seedance-2.0` with `image` (start) + `last_frame_image` (end) for each clip. This is the key mechanism for consistency — Seedance interpolates between the two locked keyframes you just generated, so faces and cars don't morph.

```python
def gen_clip(prompt: str, start_image: Path, end_image: Path, out_path: Path,
             reference_images: list[Path] | None = None):
    inputs = {
        "prompt": prompt,
        "image": open(start_image, "rb"),
        "last_frame_image": open(end_image, "rb"),
        "duration": 15,
        "resolution": "{{resolution}}",
        "aspect_ratio": "{{aspect_ratio}}",
        "generate_audio": True,
    }
    if reference_images:
        inputs["reference_images"] = [open(p, "rb") for p in reference_images]
    output = client.run("bytedance/seedance-2.0", input=inputs)
    url = str(output) if hasattr(output, "url") is False else output.url
    out_path.write_bytes(requests.get(url, timeout=300).content)
    return out_path

# Clip 1 prompt: pull camera-notes + FR VO from script.md Act 1
clip1_prompt = """
[Act 1 — 'L'arrivée'] Slow push-in from a wide two-car standoff on a rain-slick Marseille
dock at golden hour, neon signs reflecting in puddles, into a tight two-shot of two men
locking eyes between their idling cars. Deep magenta-cyan grade, anamorphic, light rain,
engine rumble. Voice-over in French (male, low, intimate): 'On ne choisit pas sa famille.
On la reconnaît.' Cinematic, F&F-inspired, queer aesthetic — charged looks, no dialogue
spoken on-camera, only voice-over.
"""
gen_clip(clip1_prompt,
         results_dir / "keyframe_opening.png",
         results_dir / "keyframe_bridge.png",
         results_dir / "clip_01.mp4",
         reference_images=[results_dir / "keyframe_opening.png"])

# Clip 2 prompt: Act 2
clip2_prompt = """
[Act 2 — 'Le regard'] From a tight two-shot, the two men break the look, climb into their
cars in slow-motion (Lead 1 into the matte-black Charger, Lead 2 into the candy-pink
Supra), engines snarling. Match-cut to a low-angle hero shot: both cars accelerate side-by-side
toward camera on the wet dock at night, neon blooming, tires spinning. Magenta-cyan grade,
anamorphic, heavy motion blur, V8 + 2JZ engine duet. On-screen dialogue, French, shouted
between cars at speed: '— Tu me suis?' '— Toujours.' End on the cars vanishing into the
neon haze.
"""
gen_clip(clip2_prompt,
         results_dir / "keyframe_bridge.png",
         results_dir / "keyframe_closing.png",
         results_dir / "clip_02.mp4",
         reference_images=[results_dir / "keyframe_bridge.png"])
```

Notes:
- Seedance 2.0's `duration` max is 15 — do not request more.
- `last_frame_image` is the critical knob for cross-clip consistency. The end of clip 1 = the start of clip 2 (both pointed at `keyframe_bridge.png`), so the cut is seamless.
- `generate_audio: true` gives you ambient + dialogue. The model lip-syncs reasonably well to short French lines, but spoken dialogue may need re-rolling if pronunciation drifts (see Common Fixes).
- Each Seedance 2.0 call at 1080p/15s takes ~3–6 minutes. Budget for it.

---

## Step 5: Stitch with ffmpeg

Concatenate `clip_01.mp4` + `clip_02.mp4` into a single 30-second `intro_30s.mp4`. Use stream copy (no re-encode) to avoid quality loss; fall back to re-encode only if codecs mismatch.

```bash
cd {{results_dir}}

# Build the concat list
cat > concat.txt <<EOF
file 'clip_01.mp4'
file 'clip_02.mp4'
EOF

# Fast path: stream copy
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy intro_30s.mp4 || {
  echo "Stream copy failed (likely codec mismatch). Re-encoding..."
  ffmpeg -y -f concat -safe 0 -i concat.txt \
    -c:v libx264 -preset medium -crf 18 \
    -c:a aac -b:a 192k \
    intro_30s.mp4
}

# Verify duration is ~30s
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 intro_30s.mp4)
echo "Final duration: ${DUR}s"
```

If the duration is significantly off (<28s or >32s), one of the clips came back short — regenerate that clip with the same prompt before proceeding.

---

## Step 6: Evaluate Against Rubric

Score the final `intro_30s.mp4` against each criterion on a 1-5 scale. Watch the full 30 seconds at least twice with audio on.

### Rubric

| # | Criterion | 5 (Excellent) | 3 (Acceptable) | 1 (Poor) |
|---|-----------|---------------|-----------------|----------|
| 1 | **Script quality (FR)** | French is idiomatic and cinematic; lines land emotionally; rhythm matches on-screen action; voice-over and dialogue feel written by a French screenwriter | French is grammatically correct but stilted or translated-feeling; lines are functional but not memorable | Awkward translations, grammar errors, slang misused, or lines that read like an English script run through a translator |
| 2 | **Video consistency** | Same faces, hair, jewelry, wardrobe, and cars across both clips and across the cut; no identity drift; lighting and grade match between clips | Minor drift in one element (e.g., chain disappears in clip 2) but characters are clearly the same people; grade is close | Characters or cars morph between clips; lighting or color grade shifts visibly at the cut; reads as two unrelated shots |
| 3 | **Queer-aesthetic execution** | The "gay" framing is unmistakable but tasteful — earned through camera language (lingering looks, framing, body language) rather than explicit content; feels confident, not parodic | The aesthetic reads as queer-friendly but could be interpreted as just "stylish" — the homoerotic charge is present but soft | Reads as straight-coded; or veers into camp/parody; or pushes into explicit content that breaks the "opener" tone |
| 4 | **F&F genre fidelity** | Instantly reads as F&F: muscle/import cars, low angles, slow-mo, engine sound design, family-loyalty undertone; could intercut with a real F&F film | Has some F&F elements (cars, neon) but lacks the genre's signature camera and sound language | Generic action/music-video feel; cars are background instead of co-stars; no recognizable F&F DNA |
| 5 | **Cinematic impact** | First 5 seconds hook, last 5 seconds make you want the next scene; technical craft (focus, exposure, audio mix) is broadcast-quality; would screen well in front of a real audience | Watchable end-to-end but missing one of: a strong hook, a strong button, or clean technical execution | Pacing is flat, audio is muddy, focus or exposure is off, or no narrative momentum |

**Pass threshold: overall average ≥ 4.0, no individual criterion below 3.**

Record your scores and one sentence of reasoning per criterion in `summary.md` and `validation_report.json`.

---

## Step 7: Iterate on Weak Criteria (max 3 rounds)

If the rubric score is below the pass threshold:

1. Identify the **lowest-scoring criterion**
2. Consult Common Fixes below for the targeted intervention
3. Make the focused edit — regenerate only what's needed (don't reroll the whole pipeline)
4. Re-score with Step 6 rubric
5. Repeat up to 3 times total

After 3 rounds, keep the best-scoring version and document the remaining weakness in `summary.md`.

### Common Fixes

| Weak Criterion | Common Issue | Fix |
|----------------|-------------|-----|
| Script quality (FR) | Lines feel translated, not written | Rewrite voice-over with concrete sensory verbs and shorter sentences; check that idioms exist in French cinema (e.g., "On ne choisit pas sa famille" is fine; "C'est la vie famille" is not). Regenerate the affected clip with the new prompt. |
| Script quality (FR) | Spoken French audio is mispronounced by Seedance | Shorten the line to ≤5 words, prefer voice-over over on-camera dialogue (no lip-sync constraint), or post-dub by generating audio separately with a TTS step and muxing with ffmpeg. |
| Video consistency | Characters drift between clip 1 and clip 2 | Regenerate `keyframe_bridge.png` with a stronger reference (pass both `keyframe_opening.png` AND the script's character bible as a longer prompt). Then regenerate both clips using the new bridge frame. |
| Video consistency | Cars change shape or color | Add explicit, repeated car descriptions to every Seedance prompt and include the keyframe with the car visible as `reference_images`. |
| Queer-aesthetic execution | Reads as straight | Add explicit camera direction: "lingering eye contact, hand brushes shoulder, breath visible in cold air, no kiss." Avoid generic "stylish" prompts. |
| Queer-aesthetic execution | Veers into parody | Strip out adjectives like "fabulous," "glittery," "campy"; ground the look in real queer subcultures (leather, eyeliner) rather than caricature. |
| F&F genre fidelity | No engine sound / no low angles | Explicitly prompt: "low-angle hero shot of the car," "V8 rumble at idle then snarl," "tire smoke," "slow-motion shifter pull." |
| Cinematic impact | Weak ending | Rewrite the last 3 seconds: cars vanishing into haze, a single line of FR voice-over over black, or a freeze-frame on a glance. Regenerate clip 2 only. |
| Cinematic impact | Muddy audio | Set `generate_audio: false` on Seedance for the failing clip, generate clean dialogue+SFX separately, mux with ffmpeg's `-c:a aac`. |

---

## Step 8: Write Executive Summary

Write `{{results_dir}}/summary.md`:

```markdown
# Fast & Furious — Intro Gay (FR) — Results

## Overview
- **Date**: {run date}
- **Setting**: {{setting}}
- **Resolution / Aspect**: {{resolution}} / {{aspect_ratio}}
- **Iterations**: {how many rounds of refinement}
- **Final duration**: {N}s

## Rubric Scores

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 1 | Script quality (FR) | X/5 | {Brief justification} |
| 2 | Video consistency | X/5 | {Brief justification} |
| 3 | Queer-aesthetic execution | X/5 | {Brief justification} |
| 4 | F&F genre fidelity | X/5 | {Brief justification} |
| 5 | Cinematic impact | X/5 | {Brief justification} |
| | **Overall** | **X.X/5** | |

## Script
{Inline the final French treatment from script.md}

## Iteration History
{What changed in each round and why}

## Recommendations
- {What could be improved with more iteration}
- {Upstream changes that would improve quality (e.g. swap Seedance 2.0 → Seedance 2.0 + ElevenLabs French TTS)}

## Limitations
- {What the rubric does not capture}
- {Subjective aspects that may need human review}
```

---

## Step 9: Write Validation Report

Write `{{results_dir}}/validation_report.json`:

```json
{
  "version": "1.0.0",
  "run_date": "2026-01-01T00:00:00Z",
  "parameters": {
    "resolution": "1080p",
    "aspect_ratio": "21:9",
    "setting": "...",
    "lead_1": "...",
    "lead_2": "...",
    "car_1": "...",
    "car_2": "..."
  },
  "stages": [
    { "name": "setup",          "passed": true, "message": "ffmpeg + replicate token verified" },
    { "name": "script",         "passed": true, "message": "Bilingual treatment written" },
    { "name": "keyframes",      "passed": true, "message": "3 keyframes generated via nano-banana" },
    { "name": "video_clips",    "passed": true, "message": "2 clips generated via seedance-2.0 with locked start/end frames" },
    { "name": "stitch",         "passed": true, "message": "Final 30s mp4 assembled via ffmpeg concat" },
    { "name": "evaluation",     "passed": true, "message": "Rubric score: X.X/5" }
  ],
  "rubric_scores": {
    "script_quality_fr":       { "score": 5, "notes": "..." },
    "video_consistency":       { "score": 4, "notes": "..." },
    "queer_aesthetic":         { "score": 4, "notes": "..." },
    "ff_genre_fidelity":       { "score": 5, "notes": "..." },
    "cinematic_impact":        { "score": 4, "notes": "..." }
  },
  "overall_score": 4.4,
  "pass_threshold": 4.0,
  "iterations": 1,
  "overall_passed": true,
  "output_files": [
    "{{results_dir}}/intro_30s.mp4",
    "{{results_dir}}/clip_01.mp4",
    "{{results_dir}}/clip_02.mp4",
    "{{results_dir}}/keyframe_opening.png",
    "{{results_dir}}/keyframe_bridge.png",
    "{{results_dir}}/keyframe_closing.png",
    "{{results_dir}}/script.md",
    "{{results_dir}}/summary.md",
    "{{results_dir}}/validation_report.json"
  ]
}
```

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="{{results_dir}}"
FAIL=0
for f in \
  "$RESULTS_DIR/intro_30s.mp4" \
  "$RESULTS_DIR/clip_01.mp4" \
  "$RESULTS_DIR/clip_02.mp4" \
  "$RESULTS_DIR/keyframe_opening.png" \
  "$RESULTS_DIR/keyframe_bridge.png" \
  "$RESULTS_DIR/keyframe_closing.png" \
  "$RESULTS_DIR/script.md" \
  "$RESULTS_DIR/summary.md" \
  "$RESULTS_DIR/validation_report.json"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
    FAIL=$((FAIL+1))
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done

# Spot-check the final mp4
if [ -s "$RESULTS_DIR/intro_30s.mp4" ]; then
  DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$RESULTS_DIR/intro_30s.mp4" 2>/dev/null)
  echo "intro_30s.mp4 duration: ${DUR}s (target: ~30s)"
fi

if [ "$FAIL" -gt 0 ]; then
  echo "OVERALL: FAIL ($FAIL missing files)"
  exit 1
fi
echo "OVERALL: PASS"
```

### Checklist

- [ ] `intro_30s.mp4` exists, is ~30 seconds, plays with audio, meets rubric (≥4.0 overall, no criterion below 3)
- [ ] Both `clip_01.mp4` and `clip_02.mp4` exist as intermediate artifacts
- [ ] All three Nano Banana keyframes exist and show character/car consistency
- [ ] `script.md` exists with bilingual treatment (FR dialogue + EN camera notes)
- [ ] `summary.md` exists with rubric scores, iteration history, and recommendations
- [ ] `validation_report.json` exists with `rubric_scores`, `overall_score`, and `overall_passed`
- [ ] Verification script printed PASS for all files

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **`last_frame_image` is the magic.** Seedance 2.0 interpolates between `image` and `last_frame_image`, which is what keeps the same face/car across the cut. Using only `image` will let the model drift the identity over 15 seconds.
- **Nano Banana is an edit model, not a generator.** For keyframes 2 and 3, pass the previous keyframe as `image_input` and *describe the edit* ("change to a tight two-shot, same faces") rather than re-describing the whole scene from scratch. You'll get much tighter identity lock.
- **French ≠ translated English.** Idiomatic French dialogue is short and image-rich ("On la reconnaît" not "We recognize her as it"). If a line wouldn't work in a Jacques Audiard film, rewrite it.
- **Don't oversell the "gay" part in prompts.** Words like "homoerotic" or "queer" in image/video prompts often get model refusals or veer into stereotypes. Describe the *behavior* (eye contact, body language, framing) and let the aesthetic emerge.
- **Audio drift is the most common Seedance failure mode** for FR. If lip-sync is bad, switch to voice-over framing (off-screen narration) in the script — there's nothing to sync to.
- **Budget**: each Seedance 2.0 call at 1080p/15s takes 3–6 minutes and costs ~$0.40–$0.80. Nano Banana is faster (~10s) and cheap. Expect a full successful run with one iteration to run ~10–15 minutes wall-clock.
- **Cinemascope (21:9)** is what sells the "movie opener" feel. Don't downgrade to 16:9 unless the platform requires it.
