---
version: 1.0.0
evaluation: programmatic
agent: codex
model: gpt-5.5
snapshot: python312-uv
origin:
  url: https://raw.githubusercontent.com/adewale/swiss-poster-skill/e8e0b9f1e03a5d832067ef8c6e0e64eac91fa10e/swiss-poster/SKILL.md
  user_supplied_url: https://github.com/adewale/swiss-poster-skill
  is_directory_mirror: false
  source_host: raw.githubusercontent.com
  source_title: Swiss Poster Design System
  imported_at: '2026-05-07T17:14:48Z'
  imported_by: skill-to-runbook-converter@1.1.0
  attribution:
    collection_or_org: adewale
    skill_name: swiss-poster
    confidence: high
secrets: {}
---

# Swiss Poster Design System — Agent Runbook

## Objective

Apply the Swiss Poster design system to a webpage or frontend surface using Tailwind CSS and disciplined visual composition. The runbook converts the source skill's design guidance into an auditable implementation workflow with explicit outputs, bounded iteration, validation, and provenance. Use it when the task asks for poster-style layouts with extreme typographic scale, grid-breaking composition, overlap, bleed, crop, and a restrained but bold accent system.

Source description: Apply a Swiss Poster design system using Tailwind CSS. Use when asked to style a webpage with poster-style layouts where elements break the grid, overlap, bleed off edges, and use extreme typographic scale. Implements IBM Plex Sans, stone color palette, opacity hierarchy, and compositional techniques from Weingart, Troxler, Hofmann, and Odermatt & Tissi.

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|---|---|
| `/app/results/summary.md` | Executive summary of the design application, changed files, and validation result |
| `/app/results/validation_report.json` | Structured validation results with stages, results, and `overall_passed` |
| `/app/results/design_application.md` | Notes mapping source principles to concrete UI changes |
| `/app/results/visual_review.md` | Viewport review findings, screenshots or manual review notes, and any residual issues |

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| Results directory | `/app/results` | Output directory where required artifacts are written |
| Target surface | Current workspace | Page, component, or app screen to restyle |
| Accent color | Project-appropriate | Exactly one bold accent color used in large confident fields |
| Iteration limit | `max 3 rounds` | Maximum design refinement rounds before final validation |

## Dependencies

| Dependency | Type | Required | Description |
|---|---|---|---|
| `CSS` | Tool or asset | Required | Referenced by the source skill |
| `HTML/CSS editing environment` | Tool or asset | Required | Referenced by the source skill |
| `IBM Plex Sans` | Tool or asset | Required | Referenced by the source skill |
| `Tailwind` | Tool or asset | Required | Referenced by the source skill |
| `Tailwind CSS` | Tool or asset | Required | Referenced by the source skill |
| `css` | Tool or asset | Required | Referenced by the source skill |
| `html` | Tool or asset | Required | Referenced by the source skill |
| `js` | Tool or asset | Required | Referenced by the source skill |
| `tailwind` | Tool or asset | Required | Referenced by the source skill |

## Step 1: Environment Setup

1. Confirm the target page or component is identified and the local project can be built or previewed.
2. Create `/app/results` if it does not already exist.
3. Inspect the existing design system, Tailwind configuration, font loading, and responsive breakpoints.
4. If Tailwind is not available, translate the source utility guidance into the project's native CSS approach without changing the visual principles.

## Step 2: Source Principles

Use these source sections as the implementation checklist:

- `Six Principles`
- `Typography`
- `Color System`
- `Stone palette (light mode → dark mode)`
- `Opacity hierarchy`
- `Accent color`
- `Grid & Breakout`
- `The grid is a starting point`
- `Breaking the grid (the goal)`
- `Overlap patterns`
- `Rotation & Diagonal Energy`
- `Responsive Design`

### Six Principles

1. **Grid as launchpad.** Start with a 12-column grid, then let key elements escape it. Oversized type, images, and color blocks should break column boundaries, overlap neighbors, or bleed off the viewport edge. The grid exists so the breakout has meaning. 2. **Extreme scale contrast.** Place 20rem display type next to 11px labels. A single word can fill the viewport width. The tension between massive and tiny *is* the hierarchy. Never settle for moderate size differences. 3. **Overlap and layer.** Elements should collide — text over images, type over type, color blocks overlapping content. Use `relative`/`absolute` positioning, negative margins, and z-index stacking to create depth. 4. **Bleed and crop.** Let elements escape their containers. Type cropped by the viewport edge, images that extend past the layout, color blocks that run off-screen. A composition that's cut off implies ...

### Typography

**Primary font:** IBM Plex Sans (Google Fonts) ```html <link rel="preconnect" href="https://fonts.googleapis.com"> <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,100;0,300;0,400;0,500;0,600;0,700;1,300;1,400&display=swap" rel="stylesheet"> ``` **Fallback chain** (in order of preference): | Font | Source | Character | | ---- | ------ | --------- | | IBM Plex Sans | Google Fonts | Primary. Rational, slightly condensed, 1960s systems rationalism | | Hanken Grotesk | Google Fonts | Closest to Neue Haas Grotesk lineage | | Barlow | Google Fonts | Condensed Swiss-grid proportions, strong vertical rhythm | | Host Grotesk | Google Fonts | Warm grotesque, good at all sizes | | DM Sans | Google Fonts | Clean neo-grotesque fallback | | system-ui | Built-in | Last resort | ```css font-family: 'IBM Plex Sans', 'Hanken Grotesk', 'Barlow', 'Host Grotesk', 'DM Sans', ...

### Stone palette (light mode → dark mode)

| Role | Light | Dark | Tailwind | | ---- | ----- | ---- | -------- | | Page background | `stone-50` | `stone-950` | `bg-stone-50 dark:bg-stone-950` | | Surface / card | `stone-100` | `stone-900` | `bg-stone-100 dark:bg-stone-900` | | Subtle surface | `stone-200` | `stone-800` | `bg-stone-200 dark:bg-stone-800` | | Border | `stone-200` | `stone-800` | `border-stone-200 dark:border-stone-800` | | Primary text | `stone-900` | `stone-50` | `text-stone-900 dark:text-stone-50` | | Secondary text | `stone-900/70` | `stone-50/70` | `text-stone-900/70 dark:text-stone-50/70` | | Tertiary text | `stone-900/40` | `stone-50/40` | `text-stone-900/40 dark:text-stone-50/40` |

### Opacity hierarchy

To de-emphasize text, reduce opacity — never change the hue. ``` Full presence: text-stone-900 (primary) Softer: text-stone-900/70 (secondary, labels) Quiet: text-stone-900/40 (tertiary, captions) Ghosted: text-stone-900/20 (disabled, placeholder) ``` Dark mode: replace `stone-900` with `stone-50`. The opacity values stay identical.

### Accent color

Each project uses **one** accent color. Default is Swiss poster red. | Name | Hex | Tailwind arbitrary | | ---- | --- | ------------------ | | Swiss Red (default) | `#C8102E` | `[#C8102E]` | | Cobalt | `#003B8E` | `[#003B8E]` | | Golden | `#F0B429` | `[#F0B429]` | | Forest | `#2D6A4F` | `[#2D6A4F]` | **Poster-style accent usage — bolder than International Style:** ``` Full field: bg-[#C8102E] Full-width bands, large shapes, hero backgrounds Overlay: bg-[#C8102E]/80 Translucent overlay on images or sections Muted: bg-[#C8102E]/60 Hover states, secondary elements Tint: bg-[#C8102E]/20 Background washes, card tints Ghost: bg-[#C8102E]/10 Very subtle tints ``` The poster style permits large accent surfaces. A full-width red band, a half-page accent block, or accent type at mega scale are all correct. The International Style limited accent to 10–15% of visual surface; poster style can ...

### Grid & Breakout

**Base unit:** 8px. Spacing is multiples of 8, but elements are free to escape the grid.

### The grid is a starting point

```html <!-- Standard 12-column grid — the foundation --> <div class="grid grid-cols-12 gap-4 md:gap-8"> <div class="col-span-12 md:col-span-8">...</div> <div class="col-span-12 md:col-span-4">...</div> </div> ```

### Breaking the grid (the goal)

Elements escape their grid cells using negative margins, absolute positioning, and overflow: ```html <!-- Type that bleeds left out of its container --> <div class="max-w-6xl mx-auto px-8 relative"> <h1 class="text-[clamp(6rem,15vw,20rem)] font-bold leading-[0.85] -ml-[0.04em] text-stone-900 dark:text-stone-50"> PLAKAT </h1> </div> <!-- Element that escapes its column into the neighbor --> <div class="grid grid-cols-12 gap-8"> <div class="col-span-5 relative"> <div class="absolute -right-24 top-0 w-64 h-64 bg-[#C8102E]"></div> </div> <div class="col-span-7">...</div> </div> <!-- Full-bleed accent band that ignores the container --> <div class="bg-[#C8102E] -mx-[100vw] px-[100vw] py-16"> <div class="max-w-6xl mx-auto">...</div> </div> ```

### Overlap patterns

```html <!-- Text overlapping a color block --> <div class="relative"> <div class="w-2/3 h-64 bg-[#C8102E]"></div> <h2 class="absolute -bottom-8 right-0 text-7xl font-bold text-stone-900 dark:text-stone-50"> Gestaltung </h2> </div> <!-- Stacked layers with offset --> <div class="relative"> <div class="bg-stone-200 dark:bg-stone-800 p-12 ml-16 mt-16">Content</div> <div class="absolute top-0 left-0 w-32 h-32 bg-[#C8102E]"></div> </div> ``` ---

## Step 3: Design Application

1. Establish a 12-column compositional grid, then deliberately let primary elements break it.
2. Add IBM Plex Sans or the closest available grotesque fallback.
3. Create extreme scale contrast between viewport-scale type and compact labels.
4. Layer text, images, and color fields with controlled overlap, z-index, negative margins, and crop.
5. Use exactly one accent color boldly; keep neutral structure quiet enough for the accent to carry the poster effect.
6. Write `/app/results/design_application.md` with a concise mapping from each applied source principle to the files and UI elements changed.

## Step 4: Responsive and Accessibility Review

1. Review desktop and mobile viewports for clipped text, illegible contrast, accidental overlap, and inaccessible focus states.
2. Keep intentional crop and bleed, but correct any overlap that blocks interaction or hides required content.
3. Verify font loading has a reliable fallback chain and does not cause layout instability.
4. Write `/app/results/visual_review.md` with viewport sizes checked and issues fixed or deferred.

## Step 5: Iterate on Errors (max 3 rounds)

If visual review or build validation fails, run up to max 3 rounds of targeted fixes. In each round, record the failed check, apply only the necessary adjustment, rerun the relevant build or preview check, and update `/app/results/visual_review.md`.

## Step 6: Common Fixes

| Issue | Fix |
|---|---|
| Display type overflows unpredictably | Use stable `clamp()` bounds and explicit line-height |
| Page reads as generic Swiss minimalism | Increase scale contrast, crop, overlap, or accent-field size |
| Accent color dominates every element | Keep one accent but reserve it for large fields and decisive details |
| Mobile layout hides content | Reduce absolute positioning at narrow widths while preserving hierarchy |
| Font is unavailable | Use the documented grotesque fallback chain |

## Step 7: Final Checklist

Run this verification before finishing:

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="/app/results"
for f in "$RESULTS_DIR/summary.md" "$RESULTS_DIR/validation_report.json" "$RESULTS_DIR/design_application.md" "$RESULTS_DIR/visual_review.md"; do
  if [ ! -s "$f" ]; then
    echo "FAIL: $f is missing or empty"
  else
    echo "PASS: $f ($(wc -c < "$f") bytes)"
  fi
done
```

The final response should summarize files changed, validation performed, and any manual follow-up.

## Tips

Prefer decisive composition over decoration: the poster effect should come from scale, crop, layering, grid tension, and one confident accent color.
