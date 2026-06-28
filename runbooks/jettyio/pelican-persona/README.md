# pelican-persona

Turn the Jetty **"Pelly"** logo into an on-brand **persona mascot** for any ICP — same flat bold-outline
identity, new wardrobe + accent — then rebuild it as a clean, scalable **SVG** (plus a deck PNG and optional
transparent variants).

The method that works: **nano-banana as an image editor on the real mark** (not a from-scratch generator),
then palette-snap → vtracer → svgo. Hand-authoring the mascot SVG was tried and rejected.

- **`RUNBOOK.md`** — the full process (Steps 1–6 + rubric + common fixes).
- **`vectorize.py`** — palette-snap → trace (smooth pipeline). **`transparentize.py`** — cream → transparent
  (PNG flood-fill / SVG bg-strip). **`overlay_prop.py`** — add a prop the editor refuses to keep.
  **`gen.py`** — Replicate wrapper.
- **`ref-pelly-*.png`** — the locked style/beak references. **`assets/prop-maple-leaf.svg`** — reusable prop.
- **`example-*.svg`** — gold-standard outputs (builder, operator, builder-grey, canada(-alt),
  operator-formal, champion-formal).

Needs `REPLICATE_API_KEY`, Python (`vtracer`, `pillow`, `scipy`), `rsvg-convert`, and `npx svgo`.
