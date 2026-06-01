---
version: 1.0.0
evaluation: programmatic
agent: claude-code
model: claude-sonnet-4-6
snapshot: python312-uv
secrets: {}
origin:
  attribution:
    collection_or_org: jettyio
    skill_name: deck-generator
    confidence: high
---

# deck-generator — Agent Runbook

## Objective

Turn a single **deck-source markdown file** into a polished, self-contained **HTML slide deck** and a print-ready **16:9 PDF**, using a fixed design system. The author writes plain markdown — one `## Slide N` block per slide, each tagged with a layout `[type: …]` — and this runbook compiles it into `deck.html` + `deck.pdf`.

The design system ships with a catalog of strategy-deck templates: a **Playing-to-Win 5-box cascade**, **ICP persona** slides, a **network-loop flywheel**, **sequencing strips**, a **12-month month-bar**, **capability/comparison matrices**, **card grids**, **pull-quotes**, and dark **cover/closing** slides. The author picks a template per slide; this runbook renders it on-brand.

Use this when someone uploads a markdown file in the deck-source format (see **`sample-deck.md`** in this runbook's directory for a complete, annotated example that exercises every template) and wants the HTML + PDF deck back.

## REQUIRED OUTPUT FILES (MANDATORY)

**You MUST write all of the following to `{{results_dir}}` (default `/app/results`). The task is NOT complete until every file exists and is non-empty.**

| File | Description |
|------|-------------|
| `{{results_dir}}/deck.html` | Self-contained HTML deck (theme CSS inlined; fonts via Google Fonts CDN) |
| `{{results_dir}}/deck.pdf` | Rendered 16:9 PDF, one slide per page |
| `{{results_dir}}/theme.css` | The design-system stylesheet written in Step 1 (kept for reference/debug) |
| `{{results_dir}}/summary.md` | Run metadata: deck title, slide count, templates used, validation results, any issues |
| `{{results_dir}}/validation_report.json` | Structured validation: `{ "stages": [...], "results": {...}, "overall_passed": true|false }` |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Results directory | `/app/results` | Output directory for all results (`./results` when run locally) |
| Input deck markdown | *(required)* | Path to the uploaded deck-source `.md`. On Jetty it arrives via file upload (`init_params.file_paths[0]`); locate it in Step 1. |
| Brand wordmark | *(from each slide's `[brand:]`)* | Optional override for the cover/closing wordmark if the source omits it. |

> **INPUTS (fill these before running, or let Step 1 auto-detect):**
> - `INPUT_MD` = path to the deck-source markdown to compile (the file the user uploaded).
> - `RESULTS_DIR` = `/app/results` on Jetty, `./results` locally.
>
> If `INPUT_MD` is not set, Step 1 auto-detects the first `.md` in the working tree that contains a `## Slide ` heading and is not this `RUNBOOK.md`.

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| Python 3.10+ | Runtime | Yes | Runs the PDF render script |
| A headless browser | Runtime | Yes | Chromium via Playwright (preferred, self-provisions) or a system `chrome`/`chromium` binary |
| Google Fonts CDN | External | Yes (render) / Optional (offline) | Outfit · Nunito Sans · Geist Mono. If offline, the deck still renders with system-font fallbacks. |

---

## The deck-source format (input spec)

The input is one markdown file. Everything before the first `## Slide` heading is preamble (an optional title/notes block) and is ignored except for a deck title.

Each slide is:

```
## Slide N — Human Title

[type: <template-name>]
[palette: <lavender|amber|sage|...>]      ← optional colour emphasis
[brand: WORDMARK] [page: N / TOTAL]       ← brand shows on cover/closing; page shows on every slide

**Eyebrow:** short kicker line
**Headline:** the slide's main line (use *italics* for accent words)
**Lede:** optional supporting paragraph
... template-specific blocks (cards, tables, bullets, callouts) ...
**Footer:** small source/footnote line
```

- Slides are separated by `---` on its own line.
- `**bold markers**` (`**Eyebrow:**`, `**Headline:**`, `**Lede:**`, `**Footer:**`, `**Card:**`) are structural cues, not literal output.
- Blockquotes (`>`) are pull-quotes / callouts.
- `*word*` → accent emphasis (renders in the palette colour); `**word**` → bold.
- Punctuation signature: em-dash `—`, middle-dot `·`, right-arrow `→`, en-dash ranges `5–8`.

**Supported `[type:]` values** (full HTML in the Template Catalog, Step 3):

| `[type:]` | Use for |
|-----------|---------|
| `cover-dark` | Title / cover slide (dark) |
| `titlebar` | Standard content slide (eyebrow + headline + body) |
| `ptw-cascade` | Playing-to-Win five-box cascade |
| `seq-strip` | 3-column sequencing (e.g. ICPs: lead / prosecute / defer) |
| `persona-hero` | ICP / persona slide (portrait + profile) |
| `flywheel` | A 6-node loop/flywheel with a center hub + legend |
| `month-bar` | 12-cell timeline + phase decision-gate cards |
| `cards` | A grid of cards (`cols-2`/`cols-3`/`cols-4`) |
| `compare` | A comparison table |
| `matrix` | A capability×competitor matrix with ●◐○ glyphs |
| `pull-quote` | A big statement slide (dark or light) |
| `closing` | Closing / index slide (dark) |

If a slide's `[type:]` is missing or unknown, fall back to `titlebar`.

---

## Step 1: Environment Setup

Create the results directory, write the design-system stylesheet and the render helper, install a headless browser, and locate the input markdown.

```bash
set -e
RESULTS_DIR="${RESULTS_DIR:-/app/results}"
mkdir -p "$RESULTS_DIR"

# --- locate the input deck-source markdown ---
if [ -z "$INPUT_MD" ]; then
  INPUT_MD="$(grep -rl '^## Slide ' . --include='*.md' 2>/dev/null \
    | grep -v 'RUNBOOK.md' | head -n1)"
fi
if [ -z "$INPUT_MD" ] || [ ! -f "$INPUT_MD" ]; then
  echo "ERROR: no deck-source markdown found. Set INPUT_MD to the uploaded file."; exit 1
fi
echo "Input deck: $INPUT_MD"
echo "Slides found: $(grep -c '^## Slide ' "$INPUT_MD")"

# --- install a headless browser (Playwright Chromium preferred) ---
pip install --quiet playwright 2>/dev/null && \
  ( python -m playwright install --with-deps chromium 2>/dev/null \
    || python -m playwright install chromium 2>/dev/null ) || \
  echo "NOTE: Playwright unavailable; render.py will fall back to a system chrome/chromium."
```

Write the design-system stylesheet to `$RESULTS_DIR/theme.css` with **exactly** this content:

```css
:root {
  --bg: #faf8f3; --surface: #ffffff; --surface-muted: #f3efe4; --bg-inverse: #0a1230;
  --fg: #0a1230; --fg-muted: #44403c; --fg-subtle: #78716c; --fg-faint: #a8a29e;
  --accent: #f0a91f; --accent-strong: #d88f0e; --lavender: #7c5fd9; --lavender-soft: #ece6fb;
  --sage: #7c9885; --sage-soft: #e4ece6; --amber-soft: #fbe9c3; --border: #e8e1ce;
  --radius-sm: 4px; --radius-md: 6px; --radius-lg: 10px; --radius-xl: 16px; --radius-2xl: 24px;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { font-family: "Nunito Sans", system-ui, sans-serif; color: var(--fg-muted); background: var(--fg-faint); line-height: 1.55; }
.deck { width: 100%; }
.slide { width: 100vw; min-height: 100vh; padding: 64px clamp(40px, 6vw, 96px); background: var(--bg); color: var(--fg-muted); display: flex; flex-direction: column; border-bottom: 1px solid var(--border); position: relative; overflow: hidden; }
.slide.dark { background: var(--bg-inverse); color: #d5d2c8; }
.slide.dark .h1, .slide.dark .h2, .slide.dark .h3 { color: #faf8f3; }
.slide.dark .eyebrow { color: var(--accent); }
.slide.dark .meta { color: #a8a29e; }
.slide.dark .lede, .slide.dark .body { color: #c8c4b8; }
.slide-head { display: flex; justify-content: space-between; align-items: center; font-family: "Geist Mono", monospace; font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--fg-subtle); margin-bottom: 48px; }
.slide.dark .slide-head { color: #a8a29e; }
/* Brand bar = a text wordmark (set per slide via [brand:]); no external logo asset. */
.slide-head .brand { color: var(--fg); font-family: "Geist Mono", monospace; font-weight: 700; letter-spacing: 0.2em; font-size: 13px; text-transform: uppercase; }
.slide.dark .slide-head .brand { color: var(--accent); }
.slide-head .pageno { font-variant-numeric: tabular-nums; }
.corner-page { position: absolute; top: 40px; right: clamp(40px, 6vw, 96px); font-family: "Geist Mono", monospace; font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--fg-subtle); font-variant-numeric: tabular-nums; z-index: 5; }
.slide.dark .corner-page { color: #a8a29e; }
.titlebar { display: flex; gap: 16px; align-items: center; margin-bottom: 22px; }
.titlebar .brand { display: none; }
.titlebar-text { min-width: 0; }
.titlebar-text .eyebrow { margin-bottom: 8px; }
.titlebar-text .h1, .titlebar-text .h2, .titlebar-text .tag { margin-bottom: 0; }
.eyebrow { font-family: "Geist Mono", monospace; font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--accent-strong); font-weight: 500; margin-bottom: 18px; display: inline-block; }
.eyebrow.lavender { color: var(--lavender); }
.eyebrow.sage { color: var(--sage); }
.h1 { font-family: "Outfit", sans-serif; font-weight: 400; font-size: clamp(40px, 5vw, 72px); line-height: 1.06; letter-spacing: -0.025em; color: var(--fg); margin: 0 0 22px 0; max-width: 22ch; }
.h1 em { font-style: normal; color: var(--lavender); font-weight: 500; }
.h1 .accent-text { color: var(--accent-strong); font-weight: 500; }
.h1 .sage-text { color: var(--sage); font-weight: 500; }
.h2 { font-family: "Outfit", sans-serif; font-weight: 400; font-size: clamp(32px, 3.4vw, 46px); line-height: 1.08; letter-spacing: -0.025em; color: var(--fg); margin: 0 0 22px 0; max-width: 62ch; }
.h2 em { font-style: italic; color: var(--lavender); }
.h3 { font-family: "Nunito Sans", sans-serif; font-weight: 500; font-size: 20px; line-height: 1.2; letter-spacing: -0.018em; color: var(--fg); margin: 0 0 8px 0; }
.slide.dark .h3 { color: var(--bg); }
.lede { font-size: 19px; line-height: 1.55; color: var(--fg-muted); max-width: 64ch; margin: 0 0 26px 0; }
.body { font-size: 15px; line-height: 1.55; color: var(--fg-muted); }
.body.small { font-size: 13px; line-height: 1.5; }
.meta { font-family: "Geist Mono", monospace; font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--fg-subtle); font-weight: 500; }
.tag { display: inline-block; font-family: "Geist Mono", monospace; font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; font-weight: 500; padding: 4px 10px; border-radius: var(--radius-sm); background: var(--surface); border: 1px solid var(--border); color: var(--fg); }
.tag.lavender { background: var(--lavender-soft); border-color: transparent; color: var(--lavender); }
.tag.sage { background: var(--sage-soft); border-color: transparent; color: #5a755f; }
.tag.amber { background: var(--amber-soft); border-color: transparent; color: var(--accent-strong); }
.row { display: flex; gap: 28px; align-items: flex-start; }
.row.cols-2 > * { flex: 1 1 0; min-width: 0; }
.grid { display: grid; gap: 22px; }
.grid.cols-2 { grid-template-columns: 1fr 1fr; }
.grid.cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid.cols-4 { grid-template-columns: repeat(4, 1fr); }
.grid.cols-5 { grid-template-columns: repeat(5, 1fr); }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 22px; }
.card.muted { background: var(--surface-muted); border-color: transparent; }
.card.dark { background: var(--bg-inverse); border-color: transparent; color: #d5d2c8; }
.card.dark .h3 { color: #faf8f3; }
.card.lavender-accent .card-eyebrow { color: var(--lavender); }
.card.amber-accent .card-eyebrow { color: var(--accent-strong); }
.card.sage-accent .card-eyebrow { color: #5a755f; }
.card.lavender-bg { background: var(--lavender-soft); border-color: transparent; }
.card.amber-bg { background: var(--amber-soft); border-color: transparent; }
.card.sage-bg { background: var(--sage-soft); border-color: transparent; }
.card-eyebrow { font-family: "Geist Mono", monospace; font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--fg-subtle); margin-bottom: 10px; }
.stat { font-family: "Outfit", sans-serif; font-weight: 400; font-size: 44px; line-height: 1; letter-spacing: -0.03em; color: var(--fg); margin: 0; }
.stat.lavender { color: var(--lavender); } .stat.amber { color: var(--accent-strong); } .stat.sage { color: var(--sage); }
.stat-label { font-family: "Geist Mono", monospace; font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--fg-subtle); margin-top: 8px; line-height: 1.4; }
ul.clean { list-style: none; padding: 0; margin: 0; }
ul.clean li { padding: 10px 0; border-bottom: 1px solid var(--border); font-size: 15px; line-height: 1.5; }
ul.clean li:last-child { border-bottom: none; }
ul.clean li .num { font-family: "Geist Mono", monospace; font-size: 11px; color: var(--fg-subtle); margin-right: 12px; letter-spacing: 0.1em; }
ul.bullets { list-style: none; padding: 0; margin: 0; }
ul.bullets li { position: relative; padding-left: 20px; margin-bottom: 10px; font-size: 15px; line-height: 1.5; }
ul.bullets li::before { content: ""; position: absolute; left: 0; top: 9px; width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }
ul.bullets.lavender li::before { background: var(--lavender); }
ul.bullets.sage li::before { background: var(--sage); }
ul.bullets.dark li { color: #d5d2c8; }
.slide-foot { margin-top: auto; padding-top: 32px; font-family: "Geist Mono", monospace; font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--fg-faint); display: flex; justify-content: flex-start; }
.portrait { width: 100%; aspect-ratio: 1; border-radius: var(--radius-2xl); overflow: hidden; background: var(--surface); border: 1px solid var(--border); position: relative; }
.portrait.ph { display: flex; align-items: center; justify-content: center; background: var(--surface-muted); }
.portrait.ph .ph-mark { font-family: "Outfit", sans-serif; font-weight: 300; font-size: 72px; color: var(--fg-faint); letter-spacing: -0.03em; }
.persona-hero { display: grid; grid-template-columns: 320px 1fr; gap: 48px; align-items: center; }
table.compare { width: 100%; border-collapse: collapse; font-size: 14px; }
table.compare th, table.compare td { text-align: left; padding: 12px 14px; border-bottom: 1px solid var(--border); vertical-align: top; }
table.compare th { font-family: "Geist Mono", monospace; font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--fg-subtle); font-weight: 500; border-bottom: 1px solid var(--fg); }
table.compare td strong { color: var(--fg); font-weight: 600; }
table.compare.big { font-size: 16px; }
table.compare.big th, table.compare.big td { padding: 17px 16px; }
table.compare.matrix th, table.compare.matrix td { text-align: center; padding: 9px 6px; }
table.compare.matrix th.cap, table.compare.matrix td.cap { text-align: left; padding-left: 0; }
table.compare.matrix td.cap { color: var(--fg-muted); font-size: 13px; }
table.compare.matrix .you { background: var(--lavender-soft); }
table.compare.matrix th.you { color: var(--lavender); }
.cap-y { color: var(--sage); font-weight: 700; } .cap-p { color: var(--accent-strong); font-weight: 700; } .cap-n { color: var(--fg-faint); }
.flywheel { position: relative; width: 660px; height: 356px; flex-shrink: 0; margin: 4px auto 0; }
.fw-ring { position: absolute; left: 82px; top: 50px; width: 496px; height: 256px; border: 2px dashed var(--lavender); border-radius: 50%; opacity: 0.5; }
.fw-hub { position: absolute; left: 330px; top: 178px; transform: translate(-50%, -50%); width: 226px; text-align: center; }
.fw-hub .fw-turn { font-size: 21px; color: var(--lavender); line-height: 1; }
.fw-hub .fw-q { font-family: "Outfit", sans-serif; font-size: 17px; font-weight: 500; color: var(--fg); letter-spacing: -0.015em; margin-top: 2px; }
.fw-hub .fw-a { font-size: 12px; line-height: 1.4; color: var(--fg-subtle); margin-top: 4px; }
.fw-node { position: absolute; transform: translate(-50%, -50%); width: 150px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 8px 12px; text-align: center; }
.fw-node .fw-num { display: inline-flex; align-items: center; justify-content: center; width: 19px; height: 19px; border-radius: 50%; background: var(--lavender); color: #fff; font-family: "Geist Mono", monospace; font-size: 10px; font-weight: 600; margin-bottom: 2px; }
.fw-node strong { display: block; font-family: "Outfit", sans-serif; font-weight: 500; font-size: 15px; color: var(--fg); letter-spacing: -0.01em; }
.fw-node .fw-sub { display: block; font-size: 11px; line-height: 1.25; color: var(--fg-subtle); margin-top: 1px; }
.fw-node.n1 { left: 330px; top: 50px; } .fw-node.n2 { left: 545px; top: 114px; } .fw-node.n3 { left: 545px; top: 242px; }
.fw-node.n4 { left: 330px; top: 306px; } .fw-node.n5 { left: 115px; top: 242px; } .fw-node.n6 { left: 115px; top: 114px; }
.fw-legend { display: flex; flex-wrap: wrap; gap: 6px 18px; justify-content: center; margin-top: 10px; font-size: 12px; color: var(--fg-muted); }
.fw-legend span strong { color: var(--lavender); font-weight: 600; margin-right: 4px; }
.ptw-cascade { display: flex; flex-direction: column; margin-top: 14px; }
.ptw-step { display: grid; grid-template-columns: 250px 1fr; border: 1px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; background: var(--surface); align-self: flex-start; }
.ptw-step .ptw-label { padding: 16px 20px; display: flex; flex-direction: column; justify-content: center; }
.ptw-step .ptw-num { font-family: "Geist Mono", monospace; font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--fg-subtle); font-weight: 600; }
.ptw-step .ptw-topic { font-family: "Outfit", sans-serif; font-weight: 600; font-size: 21px; line-height: 1.08; letter-spacing: -0.02em; color: var(--fg); margin-top: 5px; }
.ptw-step .ptw-q { font-family: "Geist Mono", monospace; font-size: 10px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--fg-faint); margin-top: 7px; line-height: 1.4; }
.ptw-step .ptw-content { padding: 16px 22px; border-left: 1px solid var(--border); display: flex; align-items: center; }
.ptw-step .ptw-content .ptw-body { font-size: 12px; line-height: 1.45; color: var(--fg-muted); width: 100%; }
.ptw-step .ptw-content strong { color: var(--fg); font-weight: 600; }
.ptw-step .ptw-content .ptw-sub { font-family: "Geist Mono", monospace; font-size: 9.5px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--fg-subtle); margin-right: 6px; }
.ptw-step .ptw-content ul.ptw-list { list-style: none; padding: 0; margin: 0; }
.ptw-step .ptw-content ul.ptw-list li { position: relative; padding-left: 15px; margin-bottom: 4px; font-size: 12px; line-height: 1.4; }
.ptw-step .ptw-content ul.ptw-list li:last-child { margin-bottom: 0; }
.ptw-step .ptw-content ul.ptw-list li::before { content: ""; position: absolute; left: 0; top: 7px; width: 5px; height: 5px; border-radius: 50%; background: var(--accent); }
.ptw-step.c-lav .ptw-content ul.ptw-list li::before { background: var(--lavender); }
.ptw-step.c-amb .ptw-content ul.ptw-list li::before { background: var(--accent); }
.ptw-step.c-sage .ptw-content ul.ptw-list li::before { background: var(--sage); }
.ptw-step.c-lav .ptw-label { background: var(--lavender-soft); } .ptw-step.c-lav .ptw-topic { color: var(--lavender); }
.ptw-step.c-amb .ptw-label { background: var(--amber-soft); } .ptw-step.c-amb .ptw-topic { color: var(--accent-strong); }
.ptw-step.c-sage .ptw-label { background: var(--sage-soft); } .ptw-step.c-sage .ptw-topic { color: #5a755f; }
.ptw-arrow { color: var(--fg-faint); font-size: 16px; line-height: 1; padding: 4px 0; text-align: left; }
.seq-strip { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; border: 1px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; background: var(--surface); }
.seq-strip .seq-cell { padding: 24px; border-right: 1px solid var(--border); }
.seq-strip .seq-cell:last-child { border-right: none; }
.seq-strip .seq-cell.lead { background: var(--lavender-soft); }
.seq-strip .seq-cell.prosecute { background: var(--amber-soft); }
.seq-strip .seq-cell.defer { background: var(--sage-soft); }
.seq-strip .seq-cell .order { font-family: "Outfit", sans-serif; font-size: 48px; font-weight: 300; line-height: 1; color: var(--fg); letter-spacing: -0.03em; margin-bottom: 6px; }
.seq-strip .seq-cell .seq-label { font-family: "Geist Mono", monospace; font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--fg-muted); margin-bottom: 12px; font-weight: 500; }
.seq-strip .seq-cell .seq-icp { font-family: "Outfit", sans-serif; font-size: 22px; font-weight: 500; color: var(--fg); margin-bottom: 8px; letter-spacing: -0.018em; }
.seq-strip .seq-cell .seq-desc { font-size: 13px; line-height: 1.5; color: var(--fg-muted); }
.month-bar { display: grid; grid-template-columns: repeat(12, 1fr); gap: 0; margin: 20px 0 12px 0; border: 1px solid var(--border); border-radius: var(--radius-md); overflow: hidden; }
.month-bar .month-cell { padding: 12px 8px; text-align: center; font-family: "Geist Mono", monospace; font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--fg-subtle); font-weight: 500; border-right: 1px solid var(--border); }
.month-bar .month-cell:last-child { border-right: none; }
.month-bar .month-cell.p1 { background: var(--lavender-soft); color: var(--lavender); }
.month-bar .month-cell.p2 { background: var(--amber-soft); color: var(--accent-strong); }
.month-bar .month-cell.p3 { background: var(--sage-soft); color: #5a755f; }
.pull-quote { font-family: "Outfit", sans-serif; font-weight: 300; font-size: clamp(30px, 3.6vw, 48px); line-height: 1.2; letter-spacing: -0.025em; color: var(--fg); max-width: 30ch; }
.slide.dark .pull-quote { color: var(--bg); }
.pull-quote em { font-style: normal; color: var(--accent-strong); font-weight: 500; }
.slide.dark .pull-quote em { color: var(--accent); }
.callout { background: var(--amber-soft); border-radius: var(--radius-lg); padding: 18px 22px; font-size: 14px; line-height: 1.55; color: var(--fg-muted); }
.callout.lavender { background: var(--lavender-soft); } .callout.sage { background: var(--sage-soft); } .callout.muted { background: var(--surface-muted); }
.callout strong { color: var(--fg); }
.highlight-strip { display: flex; gap: 12px; flex-wrap: wrap; margin: 18px 0; }
.pulse { display: inline-flex; align-items: center; gap: 8px; font-family: "Geist Mono", monospace; font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; padding: 6px 12px; border-radius: 999px; background: var(--surface); border: 1px solid var(--border); color: var(--fg); font-weight: 500; }
.pulse .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }
.pulse.lavender .dot { background: var(--lavender); } .pulse.sage .dot { background: var(--sage); }
/* Print spread — 16:9 deck format. preferCSSPageSize honours this @page. */
@page { size: 13.333in 7.5in; margin: 0; }
@media print {
  html, body { background: var(--bg); margin: 0; padding: 0; }
  * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  .slide { width: 13.333in; height: 7.5in; min-height: 7.5in; max-height: 7.5in; padding: 0.4in 0.65in; box-sizing: border-box; page-break-after: always; page-break-inside: avoid; break-after: page; break-inside: avoid; border-bottom: none; overflow: hidden; display: flex; flex-direction: column; }
  .slide:last-child { page-break-after: auto; }
  .h1 { font-size: 48px !important; line-height: 1.04 !important; margin-bottom: 14px !important; }
  .h2 { font-size: 32px !important; line-height: 1.06 !important; margin-bottom: 16px !important; }
  .h3 { font-size: 17px !important; }
  .lede { font-size: 15px !important; line-height: 1.45 !important; margin-bottom: 14px !important; }
  .body { font-size: 12px !important; line-height: 1.4 !important; }
  .pull-quote { font-size: 32px !important; line-height: 1.15 !important; }
  .eyebrow { font-size: 10px !important; margin-bottom: 10px !important; }
  .tag { font-size: 9px !important; padding: 3px 8px !important; }
  .meta { font-size: 9px !important; }
  .card { padding: 12px 14px !important; }
  .slide-head { margin-bottom: 20px !important; font-size: 9px !important; }
  .corner-page { top: 0.3in !important; font-size: 9px !important; }
  .titlebar { margin-bottom: 14px !important; gap: 12px !important; }
  .titlebar-text .eyebrow { margin-bottom: 6px !important; }
  .slide-foot { padding-top: 14px !important; font-size: 9px !important; }
  .grid { gap: 12px !important; } .row { gap: 14px !important; }
  .seq-strip .seq-cell { padding: 14px !important; }
  .seq-strip .seq-cell .order { font-size: 32px !important; }
  .seq-strip .seq-cell .seq-icp { font-size: 16px !important; }
  .seq-strip .seq-cell .seq-desc { font-size: 11px !important; }
  table.compare th, table.compare td { padding: 6px 8px !important; font-size: 11px !important; }
  ul.clean li { padding: 6px 0 !important; font-size: 11px !important; }
  ul.bullets li { font-size: 11px !important; margin-bottom: 6px !important; line-height: 1.35 !important; padding-left: 14px !important; }
  .highlight-strip { margin: 10px 0 !important; gap: 8px !important; }
  .pulse { font-size: 9px !important; padding: 4px 9px !important; }
  .callout { padding: 12px 14px !important; font-size: 11px !important; }
  .card-eyebrow { font-size: 9px !important; margin-bottom: 6px !important; }
  .persona-hero { grid-template-columns: 240px 1fr !important; gap: 24px !important; }
  .portrait.ph .ph-mark { font-size: 56px !important; }
  .ptw-cascade { margin-top: 8px !important; }
  .ptw-step { grid-template-columns: 210px 1fr !important; }
  .ptw-step .ptw-label { padding: 9px 14px !important; }
  .ptw-step .ptw-topic { font-size: 16px !important; margin-top: 3px !important; }
  .ptw-step .ptw-num { font-size: 8px !important; }
  .ptw-step .ptw-q { font-size: 8px !important; margin-top: 4px !important; }
  .ptw-step .ptw-content { padding: 9px 16px !important; }
  .ptw-step .ptw-content .ptw-body { font-size: 10px !important; line-height: 1.4 !important; }
  .ptw-step .ptw-content .ptw-sub { font-size: 8px !important; }
  .ptw-step .ptw-content ul.ptw-list li { font-size: 10px !important; line-height: 1.35 !important; margin-bottom: 3px !important; padding-left: 13px !important; }
  .ptw-step .ptw-content ul.ptw-list li::before { top: 6px !important; }
  .ptw-arrow { font-size: 12px !important; padding: 2px 0 !important; }
  .month-bar .month-cell { padding: 8px 4px !important; font-size: 9px !important; }
}
```

Write the render helper to `$RESULTS_DIR/render.py` with **exactly** this content:

```python
#!/usr/bin/env python3
"""Render a self-contained HTML deck to a 16:9 PDF (one slide per page)."""
import sys, pathlib, shutil, subprocess
html_path = pathlib.Path(sys.argv[1]).resolve()
pdf_path = pathlib.Path(sys.argv[2]).resolve()
url = html_path.as_uri()

def via_playwright():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(url, wait_until="networkidle")
        pg.emulate_media(media="print")
        pg.pdf(path=str(pdf_path), print_background=True, prefer_css_page_size=True)
        b.close()

def via_chrome():
    candidates = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
                  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    for exe in candidates:
        path = exe if "/" in exe else shutil.which(exe)
        if path and pathlib.Path(path).exists():
            subprocess.run([path, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            "--print-to-pdf-no-header", "--no-margins",
                            f"--print-to-pdf={pdf_path}", "--virtual-time-budget=15000", url],
                           check=True)
            return True
    return False

try:
    via_playwright()
except Exception as e:
    print(f"[render] Playwright unavailable ({e}); trying system Chrome/Chromium…", file=sys.stderr)
    if not via_chrome():
        print("[render] ERROR: no headless browser found.", file=sys.stderr)
        sys.exit(1)
print(f"[render] wrote {pdf_path}")
```

---

## Step 2: Parse the deck-source markdown

Read `$INPUT_MD`. Split on lines that are exactly `---`. The first chunk before `## Slide` is preamble — pull a deck title from it if present (an `# Title` line), otherwise use the cover slide's headline.

For each slide chunk, extract:
- `n` and human title from `## Slide N — Title`
- `type`, `palette`, `brand`, `page` from the `[...]` tags
- the marker blocks: `**Eyebrow:**`, `**Headline:**`, `**Lede:**`, `**Footer:**`, any bullet lists, markdown tables, blockquotes, and template-specific blocks (cards labelled with `▍`, numbered loop nodes, seq cells, etc.)

Keep a running list `slides[]` with the parsed fields. Record `TOTAL = len(slides)`. If a slide's `[page:]` omits the denominator, fill it as `n / TOTAL`.

Convert inline markdown in any text you place into HTML: `*x*` → `<em>x</em>`, `**x**` → `<strong>x</strong>`, `` `x` `` → `<code>x</code>`, and keep `—` `·` `→` `≥` `≤` `×` literal.

---

## Step 3: Template Catalog

For each slide, emit a `<section class="slide …">`. Dark templates (`cover-dark`, `closing`, and any slide whose `[type:]` line contains `dark`) add `class="slide dark"`. Light content slides use the `corner-page` + `titlebar` pattern; cover/closing use `slide-head`.

**`cover-dark`** — title slide:
```html
<section class="slide dark">
  <div class="slide-head"><div class="brand">{BRAND}</div><div class="pageno">{PAGE}</div></div>
  <div style="margin-top:40px;max-width:60ch;">
    <div class="eyebrow" style="color:var(--accent);">{EYEBROW}</div>
    <h1 class="h1" style="color:var(--bg);font-size:clamp(56px,6vw,92px);max-width:18ch;">{HEADLINE}</h1>
    <p class="lede" style="color:#c8c4b8;max-width:64ch;font-size:21px;margin-top:28px;">{LEDE}</p>
  </div>
  <div class="slide-foot" style="color:var(--fg-faint);"><span>{FOOTER}</span></div>
</section>
```

**`titlebar`** — standard content slide (the workhorse):
```html
<section class="slide">
  <div class="corner-page">{PAGE}</div>
  <div class="titlebar"><div class="brand"></div><div class="titlebar-text">
    <div class="eyebrow {palette}">{EYEBROW}</div>
    <h2 class="h2">{HEADLINE}</h2>
  </div></div>
  {BODY}            <!-- ledes, card grids, tables, bullets, callouts -->
  <div class="slide-foot"><span>{FOOTER}</span></div>
</section>
```
Compose `{BODY}` from the slide's blocks: a `**Lede:**` → `<p class="lede">`; a card list → `<div class="grid cols-N">` of `<div class="card …">`; a markdown table → `table.compare`; bullets → `ul.bullets`; a `>` quote → `<div class="callout {palette}">`.

**`ptw-cascade`** — five Playing-to-Win boxes, staggered, with ↓ arrows. Box colours: Box 1 `c-lav`, Boxes 2–3 `c-amb`, Boxes 4–5 `c-sage`. Each box:
```html
<div class="ptw-cascade">
  <div class="ptw-step c-lav" style="margin-left:0;">
    <div class="ptw-label"><div class="ptw-num">Box 1</div><div class="ptw-topic">{TOPIC}</div><div class="ptw-q">{QUESTION}</div></div>
    <div class="ptw-content"><div class="ptw-body">{ANSWER — text or <ul class="ptw-list"><li>…</li></ul>}</div></div>
  </div>
  <div class="ptw-arrow" style="margin-left:118px;">↓</div>
  <!-- repeat for Box 2 (c-amb, margin-left 64px / arrow 182px), Box 3 (c-amb, 128px / 246px),
       Box 4 (c-sage, 192px / 310px), Box 5 (c-sage, 256px, no trailing arrow) -->
</div>
```
Use `<span class="ptw-sub">Customers</span> …` to label sub-points inside a box.

**`seq-strip`** — 3 sequenced columns (e.g. ICP lead / prosecute / defer):
```html
<div class="seq-strip">
  <div class="seq-cell lead"><div class="seq-label">{LABEL}</div><div class="order">⟶</div>
    <div class="seq-icp">{NAME}</div><div class="seq-desc">{DESC}</div></div>
  <div class="seq-cell prosecute">…</div>
  <div class="seq-cell defer">…</div>
</div>
```
Optionally follow with a `<div class="grid cols-3">` of "why" notes (`<div class="meta">▍ …</div>` + `<p class="body small">`).

**`persona-hero`** — ICP / persona profile:
```html
<section class="slide"><div class="corner-page">{PAGE}</div>
  <div class="persona-hero" style="margin-top:0;">
    <div class="portrait ph"><span class="ph-mark">{INITIALS}</span></div>   <!-- or <img src> if an image path is given -->
    <div>
      <div class="titlebar"><div class="brand"></div><div class="titlebar-text">
        <span class="tag {palette}">{TAG}</span>
        <h1 class="h1" style="margin-top:10px;font-size:clamp(42px,4.4vw,60px);max-width:16ch;">{HEADLINE}</h1>
      </div></div>
      <p class="lede" style="max-width:60ch;font-size:16px;">{LEDE}</p>
      <div class="highlight-strip">{PULSES: <span class="pulse {palette}"><span class="dot"></span>…</span>}</div>
      <div class="grid cols-2" style="gap:14px;">{TWO CARDS: card muted + card-eyebrow + ul.bullets}</div>
      <div class="callout {palette}">{NOTE}</div>
    </div>
  </div>
  <div class="slide-foot"><span>{FOOTER}</span></div>
</section>
```

**`flywheel`** — 6-node loop + center hub + legend. Nodes `n1…n6` are pre-positioned by CSS (top, clockwise):
```html
<div class="flywheel">
  <div class="fw-ring"></div>
  <div class="fw-hub"><div class="fw-turn">&#8635;</div><div class="fw-q">{HUB Q}</div><div class="fw-a">{HUB A}</div></div>
  <div class="fw-node n1"><span class="fw-num">1</span><strong>{V1}</strong><span class="fw-sub">{sub}</span></div>
  … n2…n6 …
</div>
<div class="fw-legend">{<span><strong>Term</strong> definition</span> …}</div>
<div class="callout lavender">{KICKER}</div>
```

**`month-bar`** — 12-cell timeline (`p1`/`p2`/`p3` shade the phases) + decision-gate cards:
```html
<div class="month-bar">{12 × <div class="month-cell p1|p2|p3">M1…M12</div>}</div>
<div class="grid cols-3" style="gap:14px;">{phase cards: card lavender-bg / amber-bg / sage-bg}</div>
```

**`compare`** — a `table.compare` (add `big` for fewer/larger rows). **`matrix`** — `table.compare matrix`; cells use `<td class="cap-y">●</td>` (strong), `cap-p">◐` (partial), `cap-n">○` (none); first column `class="cap"`; the "you"/own column gets `class="you"` on `<th>`/`<td>`.

**`pull-quote`** — `<p class="pull-quote">{TEXT with <em> accents}</p>` (on a `slide` or `slide dark`).

**`closing`** — like `cover-dark` plus a 4-column index footer (`<div style="display:grid;grid-template-columns:repeat(4,1fr);…">` of `<div class="meta">▍ …</div>` + reference).

> Match the source decks' density: headlines ≤ ~16 words, card bullets ≤ ~14 words, one idea per slide. When a slide overflows 7.5in in print, prefer cutting words over shrinking type.

---

## Step 4: Assemble `deck.html`

Write `$RESULTS_DIR/deck.html`:

1. `<!DOCTYPE html>` + `<head>` with the Google Fonts link (Outfit, Nunito Sans, Geist Mono) and **the entire `theme.css` inlined inside a single `<style>` block** (read it back from `$RESULTS_DIR/theme.css` and paste it — the file must be self-contained so it renders anywhere).
2. `<body><div class="deck"> … all slide sections in order … </div></body>`.
3. Set `<title>` to the deck title.

Inlining the CSS (rather than linking) is required so the single HTML file is portable.

## Step 5: Render `deck.pdf`

```bash
RESULTS_DIR="${RESULTS_DIR:-/app/results}"
python "$RESULTS_DIR/render.py" "$RESULTS_DIR/deck.html" "$RESULTS_DIR/deck.pdf"
```

## Step 6: Validate

| Gate | Criterion |
|------|-----------|
| HTML present | `deck.html` exists, non-empty, contains one `<section class="slide` per source slide |
| CSS inlined | `deck.html` contains `<style>` with `.slide {` (not just a `<link>`) |
| PDF present | `deck.pdf` exists and is non-empty |
| Page count | PDF page count **equals** the number of source slides |
| No overflow | Spot-check: no slide's content is visually clipped (headlines/bullets fit one 16:9 page) |
| Fidelity | Every source slide's headline + footer text appears in `deck.html` |

Check the PDF page count:
```bash
python - "$RESULTS_DIR/deck.pdf" <<'PY'
import sys, re
data = open(sys.argv[1], "rb").read()
m = re.findall(rb"/Count\s+(\d+)", data)
print("pdf_pages:", max(int(x) for x in m) if m else "unknown")
PY
```

## Step 7: Iterate on failures (max 3 rounds)

| Issue | Fix |
|-------|-----|
| PDF page count ≠ slide count | A slide overflowed onto two pages — trim its content or split it; re-render |
| Content clipped | Reduce words; move a sub-block to a card; never shrink the base type below the print sizes |
| `render.py` failed | Ensure a browser installed in Step 1; otherwise the system-Chrome fallback needs `chromium`/`google-chrome` on PATH |
| Fonts look wrong offline | Acceptable — system fallbacks apply; note it in `summary.md` |
| Unknown `[type:]` | Render as `titlebar`; note the substitution in `summary.md` |

Re-run Steps 4–6 after each fix. After 3 rounds, write remaining issues to `summary.md` and set `overall_passed=false`.

## Step 8: Write Report

- `summary.md` — deck title, slide count, the `[type:]` used per slide, validation gate results, browser used (Playwright vs system Chrome), and any issues or substitutions.
- `validation_report.json` — `{ "stages": [...], "results": { "slides": N, "pdf_pages": N, "gates": {...} }, "overall_passed": true|false }`.

## Final Checklist (MANDATORY — do not skip)

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="${RESULTS_DIR:-/app/results}"
for f in "$RESULTS_DIR/deck.html" "$RESULTS_DIR/deck.pdf" "$RESULTS_DIR/theme.css" \
         "$RESULTS_DIR/summary.md" "$RESULTS_DIR/validation_report.json"; do
  [ -s "$f" ] && echo "PASS: $f ($(wc -c < "$f") bytes)" || echo "FAIL: $f missing/empty"
done
echo "=== VERIFICATION COMPLETE ==="
```

- [ ] `deck.html` exists, CSS inlined, one `<section class="slide">` per source slide
- [ ] `deck.pdf` renders, page count == slide count
- [ ] `theme.css` written
- [ ] `summary.md` lists slide count + per-slide template + validation results
- [ ] `validation_report.json` has `stages`, `results`, `overall_passed`
- [ ] Verification script printed PASS for every file

**If ANY item fails, fix it and re-run. Do NOT finish until all pass.**

## Tips

- **The author writes markdown; you compile HTML.** Don't invent content — render exactly what each slide block says, choosing the template from `[type:]`.
- **One slide = one 16:9 page.** The print CSS (`@page 13.333in × 7.5in`) does the sizing; your job is to keep each slide's content within it. Page-count mismatch is the #1 failure — fix by trimming, not by shrinking type.
- **Inline the CSS.** `deck.html` must be a single portable file; linking `theme.css` breaks when the file is moved or downloaded.
- **Dark vs light.** Cover and closing are dark and use `.slide-head` (with the `{BRAND}` wordmark); content slides are light and use `.corner-page` + `.titlebar` (no wordmark, page number in the corner).
- **Palette discipline.** lavender / amber / sage are the only accent families. By convention lavender = the primary/builder track, amber = the secondary track, sage = deferred/tertiary — but the source's `[palette:]` always wins.
- **Persona images are optional.** If a `persona-hero` slide gives an image path, use `<img>`; otherwise render the `.portrait.ph` placeholder with the persona's initials so the deck still renders with no external assets.
- **See `sample-deck.md`** in this directory for a complete, annotated source that exercises every template — use it as the canonical reference and as a smoke test (`INPUT_MD=sample-deck.md`).
