---
version: 1.2.0
evaluation: visual
agent: claude-code
model: google/nano-banana
model_provider: replicate
snapshot: local
secrets:
  REPLICATE_API_KEY:
    env: REPLICATE_API_KEY
    description: "Replicate API token for google/nano-banana image generation"
    required: true
origin:
  attribution:
    collection_or_org: jettyio
    skill_name: pelican-persona
    confidence: high
---

# pelican-persona — Agent Runbook

## Objective

Turn the Jetty **"Pelly"** logo into an on-brand **persona mascot** for an ICP — same flat
bold-outline brand identity, a new wardrobe + accent color — then rebuild it as a clean,
scalable **SVG** (plus a deck PNG and optional transparent variants). Repeatable for any ICP
(Builder, Operator, Champion, …) or any single-character brand mascot derived from an existing
flat logo.

The output is a single Pelly, **on-model** (white body, big orange gular-pouch beak, navy dot
eye, simple two-leg "boot" feet) and **on-style** (bold navy `#0a1230` outline, flat fills, no
gradients/shading/text), dressed for one ICP and tinted with that ICP's accent. The hard-won
lesson: **hand-authoring the mascot SVG from scratch reads off-model and was rejected — image-to-image
on the real mark is the only reliable route.**

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `{persona}.svg` | Brand-palette-snapped, svgo-optimized vector — the canonical asset. |
| `{persona}.png` | 1400px raster render (cream `#faf8f3` bg) for decks. |
| `{persona}-transparent.svg` | Cream background path stripped — composites on any background. |
| `{persona}-transparent.png` | Cream knocked out via border flood-fill (interior whites survive). |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `persona` | `builder` | ICP / persona slug (required). |
| `wardrobe` | `lavender hoodie and round over-ear headphones` | One garment + at most one accessory that signals the persona (required). |
| `accent_hex` | `#7C5FD9` | The ICP accent color (required). builder=lavender `#7C5FD9` · operator=amber `#F0A91F` · champion=sage `#7C9885`. |
| `props` | `none` | At most one small flat prop/card; leave empty for a clean character. |

## Reference assets (ship with this runbook)

- `ref-pelly-logo.png` — canonical filled logo. **The source of truth for the iconic beak + simple feet.**
- `ref-pelly-up-bold.png` — the bold navy-outline "pelly-up" pose. **The style/pose base.**
- `vectorize.py` — palette-snap → vtracer (smooth pipeline). `transparentize.py` — knock the cream bg out of a
  PNG (border flood-fill) or strip the bg path from a traced SVG. `overlay_prop.py` — add a small prop the
  editor refuses to keep. `gen.py` — thin Replicate wrapper (curl-based; macOS system python has no CA bundle).
- `assets/prop-maple-leaf.svg` — a ready-made white maple leaf for overlays.
- Worked examples: `example-builder.svg` / `example-operator.svg` (gold-standard lavender + amber),
  `example-builder-grey.svg` (alt wardrobe), `example-canada.svg` / `example-canada-alt.svg`
  (Canada-Day pair — the single-ref img2img + transparent + svgo worked example),
  `example-operator-formal.svg` / `example-champion-formal.svg` (yellow blazer + bow tie / sage blazer + lanyard).

> The bold-outline language matches the design-system "feelings" set (`design-systems/assets/pelicans/*.svg`).
> Keep new personas in that language so they read as one family.

## Setup

```bash
source .env                                     # REPLICATE_API_KEY
python3 -m pip install --user vtracer pillow scipy   # vectorizer + image ops
# Also needs: rsvg-convert (librsvg) for renders, npx svgo for optimization.
# macOS system python urllib has NO CA bundle → gen.py shells out to curl for TLS. Keep it that way.
```

## Step 1 — Generate the persona (nano-banana as an EDITOR, not a generator)

The single biggest lever: feed the **real logo + bold-outline base as `image_input`** and ask for the
*smallest change*. Redrawing "from scratch" makes the model over-illustrate (3D, gradients, hallucinated
text); editing a reference keeps it on-model.

```bash
python3 gen.py nano scratch/{persona}-1.png "ref-pelly-up-bold.png,ref-pelly-logo.png" <<'EOF'
Image 1 = the LOCKED Jetty "Pelly" style to match: a pelican in the BOLD navy-outline (#0A1230)
flat sticker style on a cream (#FAF8F3) background, with the large iconic orange (#FFAA00)
gular-pouch beak and simple minimal two-leg feet. Image 2 = the original logo (canonical beak + feet).
Match image 1's exact drawing style, outline weight, beak and feet. Now render the {persona} persona:
dress Pelly in {wardrobe}; use {accent_hex} as the ONLY accent color; {props}.
NO hoodie-if-not-asked, NO code, NO terminal, NO scene clutter. Flat colors only, no shading,
no gradients, no text. Full body centered on cream.
EOF
```

Generate **4–6 variations** (re-run with small nudges: beak angle, head height, accessory size). nano-banana
is stochastic — variety comes from re-running, not from one perfect prompt.

> **Simpler single-ref route (proven 2026-06-27, Canada Day + Operator-formal + Champion-formal):** you don't
> always need the two-reference `gen.py` setup. Render **just `pelly-up.svg` → a 1024² white-bg PNG**
> (`rsvg-convert -w 1024 -h 1024 -b '#ffffff' pelly-up.svg -o in.png`) and feed it as the lone `image_input`
> to `google/nano-banana` (POST `/v1/models/google/nano-banana/predictions`, header `Prefer: wait`, body
> `{"input":{"prompt":...,"image_input":["data:image/png;base64,…"],"output_format":"png"}}`). It keeps the
> bill/eye/feet on-model and edits in the wardrobe cleanly. Build the JSON in Python that reads+base64s the
> file — **passing the base64 via argv blows ARG_MAX** on ~1MB PNGs. The prompt MUST pin "flat-vector, thick
> dark navy outlines, solid flat colors, no gradients/shading" or it drifts painterly. Targeted **pose tweaks**
> work by feeding the prior output back ("straighten the neck / lift the head slightly, keep EVERYTHING else
> identical"). nano-banana occasionally returns a failed/empty generation — just re-run.

## Step 2 — Inspect every output (visual gate)

Open each and check against the rubric below. Regenerate per-issue, feeding the *previous best* back in
as image 1 so the next round keeps what worked. **Beak + feet are the usual failures:**

> **Build a contact sheet at every stage** (raw variants → pose tweaks → final family). Drop the candidates
> into a quick HTML grid — cards on a cream `#f3efe4` bg, `<img>` per variant, a label chip each — and `open`
> it. Judging side-by-side at a glance beats one-by-one, and it's the artifact to show the requester for a pick.

- Beak wrong → add `ref-pelly-logo.png` as a reference and say *"copy the exact large orange gular-pouch
  silhouette + single crease line from image 2."* A deep hanging pouch beats a long flat bill.
- Feet too detailed → say *"two short orange legs + one simple flat webbed foot, low detail, NO splayed
  toes."* (Raster won't fully simplify — Step 4's vector pass is the real fix.)
- A badge/screen prop comes back with **hallucinated text** → forbid letters/numbers explicitly ("BLANK card,
  no text") and re-run; some renders still bake text in — discard those.

## Step 3 — Lock the winner

```bash
cp scratch/{persona}-N.png scratch/{persona}-FINAL.png
```

## Step 4 — Rebuild as SVG (palette-snap → trace)

Do **not** trace the raw raster — its anti-aliased, slightly-off colors trace into mud. First snap every
pixel to the **exact brand palette**, then trace. `vectorize.py` does both, with a **smooth pipeline ON by
default** (3× upscale + a contour blur *before* the snap) so the navy outline traces clean instead of jagged:

```bash
python3 vectorize.py scratch/{persona}-FINAL.png scratch/{persona}-flat.png {persona}.svg {accent}
#   accent ∈ {lavender, amber, sage, greyhoodie, canada, operatoryellow}   ·   5th arg "0" disables smoothing
rsvg-convert -b "#faf8f3" -w 1400 -h 1400 {persona}.svg -o {persona}.png   # QA + deck render
```

Open `{persona}.png` and confirm the SVG render matches the locked raster (colors crisp, outline navy,
body white, pouch orange). A **frayed/jagged outline means you traced without smoothing**. **New accent?**
Sample the real colors first (don't guess) — recipe is in `vectorize.py`'s header.

## Step 5 — Optimize + transparent variants

The raw vtracer SVG is ~220–350KB of noisy paths. **Optimize it** — roughly halves the size, tidies the
markup, no visible change:

```bash
npx -y svgo@latest --multipass -q -i {persona}.svg -o {persona}.svg     # ~350KB → ~170KB
rsvg-convert -b "#f3efe4" -w 420 {persona}.svg -o /tmp/qa.png           # confirm render unchanged
```

**Transparent variants** (when the asset must sit on any background, not just cream). The bird is fully
enclosed by the navy outline, so a border flood-fill removes the cream without eating the white body:

```bash
python3 transparentize.py scratch/{persona}-FINAL.png {persona}-transparent.png   # PNG: cream → alpha
python3 transparentize.py {persona}.svg               {persona}-transparent.svg   # SVG: strip bg path
# QA on a hostile background — magenta exposes any leftover cream halo:
rsvg-convert -b "#ff00b4" -w 420 {persona}-transparent.svg -o /tmp/halo.png
```

If a halo shows, bump the dilation in `transparentize.py` (`iterations=2` → 3). Ship the transparent SVG when
you need background flexibility (it composites on cream too); keep the cream PNG for deck portraits whose card
background is exactly `#faf8f3`.

## Step 6 — Place

- **Design system:** copy `{persona}.svg` (and `-transparent.svg`) → `design-systems/assets/pelicans/` and add
  a card to `design-systems/personas.html` (match the existing card markup; accent tag class carries the ICP).
- **Decks:** drop `{persona}.png` into the deck's `assets/` (the deck portraits sit on a `#faf8f3` card, so the
  cream PNG blends; use the transparent PNG composited onto `#faf8f3` for a guaranteed match) and re-render the
  PDF via the deck's headless-Chrome command.

## Making an ALTERNATE / seasonal pelican (grey Builder, Canada Day, Operator-formal, …)

Two ways, both proven 2026-06-27:

**A. New wardrobe from scratch** — Steps 1–5 with a new `wardrobe` / `accent`. Add the accent to
`vectorize.py`'s `ACCENTS` (sample colors from the chosen raster first — recipe in the script header).

**B. Edit an existing locked mascot** (fastest re-skin) — feed the locked PNG as image 1 and ask for the
smallest change ("keep everything; make the hoodie red"). Two gotchas learned the hard way:

- **The beak drifts on edits.** Also pass the locked mascot as the beak reference and say *"copy image 2's
  beak EXACTLY — it is the source of truth for the bill."* If it still drifts, do a dedicated **beak-fix
  pass** (feed the drifted result + the locked mascot; change ONLY the beak).
- **nano-banana will NOT keep a small high-contrast prop.** A white maple leaf on a red hoodie was stripped
  on *all 8* regenerations (white-on-red is a blind spot). Don't fight it — **add the prop as a vector
  overlay** after vectorizing the body:
  1. Get a clean prop path: hand-make an SVG, or **extract** one from a good raster (near-color mask →
     **flood-fill from a seed inside the prop** to isolate just that blob → crop → upscale →
     `vtracer colormode="binary"`). `assets/prop-maple-leaf.svg` is a ready-made white leaf.
  2. `python3 overlay_prop.py body.svg prop.svg out.svg <cx> <cy> <w> [fill] [render]` — place by eye in
     render-px space, render, nudge, repeat. (Thin stems get dropped by the trace; re-add via the `STEM=`
     env knob, or accept the stemless leaf — it still reads.)

## Quality rubric (gate before "done")

| Criterion | Pass = |
|---|---|
| On-model | white body · big orange gular-pouch beak · single navy dot eye · simple two-leg feet all present |
| On-style | bold navy `#0a1230` outline, flat fills, **no** gradient/shading/3D, **no** baked-in text |
| Iconic beak | deep hanging orange pouch (not a thin flat bill) |
| Simple feet | two legs + minimal webbed foot; no splayed toes |
| Accent discipline | exactly one accent color = the ICP's; wardrobe is one garment + ≤1 accessory |
| Vector clean | SVG renders identical to the locked raster; colors snapped to brand palette; svgo-optimized |
| Family fit | sits naturally beside `design-systems/assets/pelicans/*` |

## Common fixes

- **Over-illustrated / 3D / glossy** → you generated instead of edited. Re-feed the logo and demand "smallest possible change, flat."
- **Hallucinated text on a screen/card/badge** → forbid letters/numbers explicitly ("BLANK, no text"); discard renders that still bake it in; or drop the prop.
- **Muddy SVG colors** → you traced the raw PNG. Always palette-snap first (Step 4).
- **recraft style drift** → `recraft-v3` goes glossy/3D for character work; stick to nano-banana + logo reference. (recraft-v3-svg is only for pure silhouettes.)
- **Jagged / frayed navy outline in the SVG** → you traced without the smooth pipeline. `vectorize.py` smooths by default; don't pass `0` as the 5th arg.
- **Beak/bill changed after a wardrobe edit** → re-feed the locked mascot as the beak reference, or do a separate beak-fix pass.
- **Editor keeps deleting a small prop** → stop regenerating; add it as a vector overlay with `overlay_prop.py`.
- **SVG is still ~220–350KB after a clean trace** → run `svgo` (Step 5); it ~halves it with no visible change.
- **Traced accent looks muted vs the locked render** → the `ACCENTS` entry was sampled from a different/older raster. Re-sample THIS render (PIL quantize recipe in `vectorize.py`'s header) and tune. e.g. the `canada` red was `#d23228` but the real hoodie is brighter `#e33028`. A warm-yellow garment also sits near the `#ffaa00` beak — pick a yellow light/saturated enough to separate (`operatoryellow` ≈ `#eec537`) or the trace merges jacket and beak.
- **Cream halo on a transparent asset over a dark/colored bg** → raise `transparentize.py`'s `binary_dilation(iterations=2)` to 3; QA on magenta.
- **TLS errors from python** → use `curl` (already wired in `gen.py`); macOS system python has no CA bundle.

## Provenance

Built 2026-06-26 over ~6 iteration rounds (editor approach → minimal-element variants → bold-outline
"middle way" from the feelings set → beak/feet correction via multi-reference → vector rebuild). First
outputs: `example-builder.svg` (lavender), `example-operator.svg` (amber), then Champion (sage) + the Flock hero.

**v1.1.0 (2026-06-27):** alternates — grey-hoodie Builder + a Canada-Day Pelly — surfaced the smooth-vectorize,
beak-drift, and vector-overlay lessons.

**v1.2.0 (2026-06-27):** the Canada-Day pair, Operator-formal (yellow blazer + collar bow tie), and
Champion-formal (sage blazer + lanyard badge) hardened the delivery end: the **single-ref img2img route**
(render pelly-up → one `image_input`; ARG_MAX gotcha), **pose-tweak edits**, **contact sheets at every stage**,
**Step 5** = `svgo` optimize + **transparent variants** via `transparentize.py`, and accent-sampling fixes
(`operatoryellow`; brighter `canada` red; `sage` re-sampled). Hand-authoring the mascot SVG from scratch was
tried and **rejected** — img2img on the real mark is the only reliable route.
