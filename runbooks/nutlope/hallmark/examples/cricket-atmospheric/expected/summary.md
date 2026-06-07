# Cricket — Hallmark Build Summary

## Inferred Design Context

**Brief:** A landing page for Cricket — a late-night AI voice companion that captures, transcribes, and threads the half-formed ideas you have at 2am into something you can act on by morning.

**Audience:** Writers, founders, and makers who think after dark.

**One action:** Start a free nightly capture.

**Tone:** Austere (given) — stripped back, confident, no filler.

**Genre:** Atmospheric (inferred) — brief signals: AI, voice, late-night, nocturnal, "calm … not loud SaaS". Atmospheric matches: dark canvas, sparse layout, radial bloom, confident display type against deep background.

**Theme:** Midnight (auto-resolved from atmospheric cluster: Bloom / Midnight / Terminal / Aurora / Lumen). Midnight chosen for its dark warm-amber canvas — OKLCH paper at 12% lightness, hue 40, accent at oklch(72% 0.18 55) — the exact register of a screen at 2am.

**Macrostructure:** Narrative Workflow (#14) — Cricket has four clearly sequential product stages (Speak → Transcribe → Thread → Act). Numbered stage labels with horizontal sweep reveals; avoids the banned "centered hero → 3 equal cards → CTA → footer" fingerprint.

**Nav:** N9 Edge-aligned minimal — wordmark hard-left, single CTA hard-right, vast empty center. "The absence is the design."

**Footer:** Ft2 Inline single line — wordmark + middot-separated credits in one horizontal row.

**Enrichment:** None (typography + CSS art only) — waveform bars, transcript block, SVG thread diagram, document preview lines; no Lottie, no stock images, no embedded video.

**Typography:** Sentient 700 (display), Switzer 400/350/500 (body), Geist Mono 400 (mono outlier, ≤2 slots).

---

## Deliverables

| File | Role |
|---|---|
| `tokens.css` | Complete token system — type scale, OKLCH palette, 4pt spacing, motion, z-index, layout |
| `styles.css` | All component styles — N9 nav, hook, narrative workflow stages, CSS art, capture form, Ft2 footer, responsive breakpoints, reduced-motion |
| `index.html` | Semantic HTML5 — ARIA labels, IntersectionObserver scroll reveals, optimistic form JS |
| `screenshot.png` | Full-page render at 1440×900, deviceScaleFactor 2, all stages force-revealed |

---

## Slop Test

**Result: 58 / 58 gates passed.**

Notable gates and resolutions:

| Gate | Check | Resolution |
|---|---|---|
| 24 | No inline style attributes | `.stage__sep-line` class extracted for separator line |
| 38 | Geist Mono in ≤ 2 slots | Waveform label moved to `var(--font-body)`; Mono retained only in transcript time + text |
| 39 | Touch targets ≥ 44px | `min-height: 44px` added to input and button |
| 44 | Hook padding-block ratio ≥ 1.3 | Start changed to `var(--space-2xl)` (64px); end `var(--space-3xl)` (96px) → 96 ≥ 83.2 ✓ |

Pre-emit self-critique scores: P4 H4 E4 S4 R5 V4 (stamped in styles.css line 2).

---

## Limitations

- **No real form backend** — the email form fires an optimistic client-side update only; no data is persisted.
- **IntersectionObserver fallback** — browsers without IntersectionObserver receive all sections immediately visible (no reveal animation), which is acceptable.
- **Web fonts** — Fontshare (Sentient, Switzer) and Google Fonts (Geist Mono) are external dependencies; offline or CDN-blocked environments will fall back to system fonts defined in the font stacks.
- **OKLCH color** — supported in all modern browsers (Chrome 111+, Firefox 113+, Safari 15.4+); older environments receive uncolored fallback.
