# deck-generator

Turn a **markdown file** into a polished **HTML slide deck** + a print-ready **16:9 PDF**, using a fixed strategy-deck design system.

You write plain markdown — one `## Slide N` block per slide, each tagged with a layout `[type: …]`. This runbook compiles it into `deck.html` and `deck.pdf`.

## What's here

| File | What it is |
|------|------------|
| `RUNBOOK.md` | The runbook. Self-contained: it carries the full theme CSS and the PDF render script inline, so it runs anywhere. |
| `sample-deck.md` | A complete, annotated **sample input** (fictional "Northwind" company) that exercises every template — use it as the format reference and as a smoke test. |

## Templates

The design system ships with a catalog of Playing-to-Win strategy-deck templates, selected per slide via `[type:]`:

- `cover-dark` / `closing` — dark title & index slides
- `ptw-cascade` — the Playing-to-Win five-box cascade
- `seq-strip` — 3-column sequencing (e.g. ICPs: lead / prosecute / defer)
- `persona-hero` — ICP / persona profiles (portrait + requirements + "three to win")
- `flywheel` — a 6-node loop with a center hub + legend
- `month-bar` — a 12-month timeline with phase decision-gates
- `matrix` — a capability × competitor grid with ●◐○ glyphs
- `compare` — comparison tables
- `cards` — card grids (`cols-2/3/4`)
- `pull-quote` — big statement slides
- `titlebar` — the standard content workhorse

See `RUNBOOK.md` → **The deck-source format** and **Template Catalog** for the full spec, and `sample-deck.md` for a worked example.

## Run it

### On jetty.io (recommended)

Upload your deck-source markdown and run this runbook — Jetty executes it in a sandbox and returns `deck.html` + `deck.pdf`. Via the chat-completions runbook API, pass the runbook as the `system` message, upload your markdown via `jetty.file_paths`, and send an imperative instruction such as *"Compile the uploaded deck-source markdown into deck.html and deck.pdf in the results directory."*

### Locally

Point an agent at `RUNBOOK.md` and set `INPUT_MD` to your markdown file (defaults to auto-detecting the first `*.md` containing `## Slide ` headings). The runbook writes `theme.css` + `render.py`, installs a headless browser (Playwright Chromium, with a system-Chrome fallback), builds `deck.html`, and renders `deck.pdf`.

```
INPUT_MD=sample-deck.md   RESULTS_DIR=./results
```

## Output

`deck.html` (self-contained, CSS inlined) · `deck.pdf` (16:9, one slide per page) · `summary.md` · `validation_report.json`.
