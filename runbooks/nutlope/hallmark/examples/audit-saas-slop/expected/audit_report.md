# Hallmark Audit — `a45a609c.00.html`

> Audited against Hallmark v1.1.0 anti-pattern list and 58-gate slop test.
> Operation: **audit**. No edits made. Ranked punch list, grouped by severity.

---

## Structural Fingerprint Check

**CRITICAL — AI template confirmed.**

The page is the canonical AI landing-page template with zero deviation:

```
Nav (wordmark-left · links-right · CTA-button)
  └─ Hero (centered, purple gradient, h1 + lede + CTA + fake browser mockup)
       └─ Stats row (3 equal numbers, centered)
            └─ Features (3 equal cards, emoji icon above heading above body)
                 └─ CTA band (centered, purple gradient)
                      └─ Footer (4 columns · social row · copyright)
```

No asymmetry. No structural surprise. No asymmetric span, lateral bias, or section rhythm that deviates from the template. The page would pass a vibes-check as "professional" and a Hallmark audit as a demonstration piece of every major AI tell stacked in one file.

---

## Critical — Ships as Slop (7 findings)

---

**[CRITICAL] Structural fingerprint: AI template — entire page (lines 1–101)**
The page IS the AI template: centered hero → 3-equal-stat numbers → 3-equal-feature cards → centered CTA band → 4-column footer. No structural surprise at any layer.
→ Pick a non-centred macrostructure (Bento Grid, Stat-Led, Workbench, Marquee Hero with left-biased content) and break the symmetry at the section level.

---

**[CRITICAL] The 3-column feature grid — CSS lines 30–35 / HTML lines 78–82**
`grid-template-columns: 1fr 1fr 1fr; gap: 28px` with three `text-align: center` cards, each: emoji icon above heading above body copy. Every LLM emits this shape.
→ Break the grid. Vary column widths. Remove one card and use the freed space as negative space. Move icons inline with headings or drop them.

---

**[CRITICAL] Purple-gradient hero (and CTA band) — CSS lines 14, 26, 37**
Three purple-to-white / purple-to-light-purple gradients: `.hero { background: linear-gradient(135deg, #a78bfa 0%, #ffffff 100%) }`, `.browser .screen { background: linear-gradient(135deg, #ede9fe, #fff) }`, `.cta-band { background: linear-gradient(135deg, #6d28d9, #a78bfa) }`. The purple-gradient hero is the single most-recognised AI aesthetic.
→ Pick one anchor hue. Flat tinted surface or single-stop tint at ≤ 4 % opacity. No gradient backgrounds on hero or CTA band.

---

**[CRITICAL] The AI nav — CSS lines 10–12 / HTML lines 49–55**
Wordmark-left (`<strong>Nimbus</strong>`), four inline text links (`Product · Pricing · Docs · Blog`) grouped right, CTA button hard-right, full viewport width. Matches N1a exactly — the most-recognised AI nav fingerprint.
→ Route to N5 (floating pill), N1b (canonical three-section SaaS), or N13 (inline ⌘K-pill). Reach for N1a only when the page has two destinations.

---

**[CRITICAL] The AI footer — CSS lines 41–45 / HTML lines 89–99**
`grid-template-columns: 2fr 1fr 1fr 1fr` with columns labelled Nimbus / Product / Company / Resources, emoji social row, copyright line spanning the grid. Genre-blind; identical across thousands of pages.
→ Default to Ft1 (masthead), Ft2 (inline single line), Ft5 (statement), or Ft6 (letter close). Reserve the 4-column index only on genuine hub or docs roots.

---

**[CRITICAL] Full-viewport centered hero — CSS line 13 / HTML lines 57–70**
`text-align: center` with h1, p, and primary CTA all stacked on the same centred vertical axis. Gate 6 auto-fails: all four elements (eyebrow, title, lede, CTA) share the centred axis with no off-axis element.
→ Left-bias the text column. Put at least the eyebrow or CTA off the central axis. Let content height determine hero height — remove the symmetric `120px / 96px` symmetric padding.

---

**[CRITICAL] Inter-everywhere — CSS line 9**
`font-family: -apple-system, "Segoe UI", Roboto, Inter, sans-serif` used for every element from the 56 px hero headline (`.hero h1`) to the 12 px copyright. One-font page = template page.
→ Pair a distinctive display face (Fraunces, Instrument Serif, Clash Display, Neue Haas Grotesk) with a refined body face (Inter, DM Sans, Libre Baskerville). Display face for headings; body face for prose.

---

## Major — Looks AI-Generated (9 findings)

---

**[MAJOR] Re-drawn UI chrome — CSS lines 20–26 / HTML lines 61–69**
Hand-built `.browser` div: `.bar` with three coloured `.dot` circles mimicking macOS traffic lights, a `.url` pill with placeholder text `app.nimbus.ai/dashboard`, `.screen` as an empty gradient box. The exact pattern slop-test gate 47 names: "fake browser bar (URL pill + traffic-light dots)".
→ Cut it. If a product screenshot is needed, use a real `<figure>` with a screenshot and a hairline border. The re-drawn chrome communicates "AI invented a UI that already exists".

---

**[MAJOR] Italic header — CSS line 16 / HTML line 58**
`.hero h1 em { font-style: italic; color: #6d28d9 }` inside `<h1>The platform built to <em>think</em> with your team</h1>`. The single-italicised-word-in-heading is among the most reliable AI tells; it appears in anti-patterns.md as the primary example. Gate 38a: auto-fail.
→ Headers are roman (`font-style: normal`). Carry emphasis with weight, accent colour, or a drawn underline beneath the word.

---

**[MAJOR] Invented metrics — CSS lines 27–29 / HTML lines 72–76**
Three fabricated statistics: `+47%` "Conversion uplift", `50,000+` "Teams trust Nimbus", `10×` "Faster than before". These are literally the three canonical invented-metric examples given in anti-patterns.md — the model reached for placeholder stats to fill a stat slot.
→ Replace with real numbers, a labelled placeholder block ("metric to confirm"), or rebuild the section without the proof slot. A stat-led layout with invented stats is worse than no stats: it signals fabrication.

---

**[MAJOR] Generic emoji as feature icons — CSS line 33 / HTML lines 79–81**
`🚀`, `🔒`, `✨` in `.card .ico { font-size: 40px }`. The `✨` and `🚀` glyphs are explicitly listed in anti-patterns.md as generic-emoji tells. Emoji are OS-rendered, break the stroke voice of any icon library, and are the AI-default shortcut. Gate 30: fail.
→ Pick one icon library (Lucide for SaaS, Phosphor for weight variants) and use SVG icons consistently. Or drop icons and lead with typography.

---

**[MAJOR] Mid-render token improvisation — CSS lines 7–46 (entire stylesheet)**
Zero CSS custom properties in the stylesheet. Eighteen distinct inline hex values are scattered through the rules: `#1f2937`, `#4b5563`, `#6b7280`, `#9ca3af`, `#e5e7eb`, `#f3f4f6`, `#6d28d9`, `#a78bfa`, `#374151`, `#111827`, `#ede9fe`, `#10b981`, `#ef4444`, `#f59e0b`, etc. Every colour is improvised inline. Gate 48: fail.
→ Lift every colour into a `:root { --color-* }` token block and replace all hex values with `var(--token-name)`. This is prerequisite to any design-system coherence.

---

**[MAJOR] Centred everything — CSS lines 13, 27, 32, 36**
`text-align: center` on hero, `text-align: center` on stats, `text-align: center` on every feature card, `text-align: center` on CTA band. Every section shares the same layout axis. No lateral bias anywhere on the page.
→ Bias the layout. Left-heavy hero with a right-offset CTA, or an asymmetric split on the feature section, breaks the "generated" read.

---

**[MAJOR] No interactive states — CSS lines 7–46 (entire stylesheet)**
Zero `:hover`, `:focus-visible`, `:active`, or `:disabled` declarations. The `.cta` button element and all `<a>` links provide no visual feedback on interaction. Gate 26: fail (interactive elements must have default + hover + focus-visible + active + disabled).
→ Add at least `button:hover { background: ... }`, `button:focus-visible { outline: 2px solid ...; outline-offset: 2px }`, `button:active { transform: translateY(1px) }` for every interactive element.

---

**[MAJOR] No responsive layout — CSS lines 7–46 (entire stylesheet)**
Zero `@media` queries. `grid-template-columns: 1fr 1fr 1fr` on the features section and `grid-template-columns: 2fr 1fr 1fr 1fr` on the footer produce horizontal scroll on any viewport below ~900 px. No `overflow-x: clip` on `html` or `body`. Gates 34, 49, 50, 51: fail.
→ Add `overflow-x: clip` to both `html` and `body`. Add `@media (max-width: 48rem)` rules to collapse all multi-column grids to `1fr`. Change feature grid tracks to `minmax(0, 1fr)`.

---

**[MAJOR] Contrast failure: CTA band — CSS lines 36–40 / HTML lines 84–87**
`.cta-band { background: linear-gradient(135deg, #6d28d9, #a78bfa); color: #fff }`. At the light end of the gradient (#a78bfa, OKLCH ≈ L 72%), white text (L 100%) achieves approximately 2.0:1 contrast ratio — failing WCAG 3:1 for large text and 4.5:1 for body text. Gate 41: fail.
→ Use the dark end of the anchor hue (#6d28d9 or darker) as a flat surface colour. White text on flat dark purple clears 4.5:1 easily. Drop the gradient.

---

## Minor — Small Taste Issues (4 findings)

---

**[MINOR] Startup-cliché copy — HTML lines 59, 79–81**
Body copy: "Powerful, **seamless**, and cutting-edge. Nimbus **supercharges** your workflow with **revolutionary** AI that just works." Feature cards: "**blazing-fast** performance", "**effortlessly** scales", "unlock **powerful insights**". "Seamless" and "Supercharge" are on Hallmark's cliché list; the surrounding copy reads identically to thousands of AI-generated SaaS landing pages.
→ Name a concrete claim the product actually makes. Abstract superlatives ("blazing-fast", "revolutionary") are unfalsifiable and untrustworthy. Replace with a specific differentiator or a real user-facing benefit.

---

**[MINOR] Emoji social icons — HTML line 93**
`🐦 💼 📷 ▶️` used as Twitter/LinkedIn/Instagram/YouTube links in the footer. Same emoji-as-icon problem as the feature section; OS-rendered, inconsistent stroke voice.
→ Use SVG social icons from a single library (Primer Octicons, Lucide, Simple Icons) or use text links ("Twitter · LinkedIn · YouTube") — text links are more accessible and honest.

---

**[MINOR] Tabular data without tabular-nums — CSS line 28 / HTML lines 72–76**
`.stats .n { font-size: 44px; font-weight: 800 }` renders `+47%`, `50,000+`, `10×` in proportional figures. On a row that invites numeric comparison, vertical digit alignment matters.
→ Add `font-variant-numeric: tabular-nums` to `.stats .n` (and any future numeric container).

---

**[MINOR] Prose max-width in px — CSS line 17**
`.hero p { max-width: 600px }` constrains copy width in pixels. At 20 px body size, 600 px resolves to ~83 characters — exceeding the 45–75 ch optimal reading measure.
→ Use `max-width: 60ch` (or 62–65ch for a comfortable measure at this size) to enforce typographic line-length regardless of viewport zoom or font scaling.

---

## Slop-Test Gate Summary (applied as audit rubric)

Gates evaluated against the 58-gate canon:

| Gate | Description | Result |
|------|-------------|--------|
| 1 | Display font is Inter/Roboto/system default | **FAIL** |
| 2 | Purple-to-blue gradient anywhere | **FAIL** (hero + screen + CTA band) |
| 3 | 3-equal-column card grid with icon-above-heading | **FAIL** |
| 6 | All elements centred on same axis (gate 6 auto-fail) | **FAIL** |
| 7 | Pure `#fff` as base colour | **FAIL** (hero gradient endpoint; body default) |
| 8 | AI template structure | **FAIL** |
| 23 | Accent covers > 5% of viewport | **FAIL** (nav button + stats + h1 em + CTA band) |
| 25 | Prose max-width outside 45–75 ch | **FAIL** (600px ≈ 83ch at 20px) |
| 26 | Interactive element lacks focus-visible/active/disabled | **FAIL** (all buttons and links) |
| 29 | Abstract gradient covers > 5% with > 1 accent colour | **FAIL** (hero, CTA band) |
| 30 | Emoji glyph as feature-card icon | **FAIL** (🚀 🔒 ✨) |
| 34 | Horizontal scroll on any viewport 320–1920px | **FAIL** (no responsive layout) |
| 38a | Heading or display type italic | **FAIL** (em inside h1) |
| 40–41 | Contrast thresholds | **FAIL** (white on #a78bfa ≈ 2:1) |
| 42 | AI nav fingerprint | **FAIL** |
| 43 | AI footer fingerprint | **FAIL** |
| 44 | Hero content exceeds fold at 1280×800 | **FAIL** (browser mockup pushes below fold) |
| 45 | Decorative element without semantic anchor | **FAIL** (re-drawn browser chrome) |
| 46 | Invented metric | **FAIL** (+47%, 50000+, 10×) |
| 47 | Re-drawn browser chrome | **FAIL** |
| 48 | Mid-render token improvisation | **FAIL** (18 inline hex values, no custom properties) |
| 49 | Two-line clickable text possible on mobile | **FAIL** (no responsive layout) |
| 50 | Image-bearing grid without `minmax(0, 1fr)` | **FAIL** |
| 51 | Display headers without `overflow-wrap: anywhere` | **FAIL** |

**24 / 58 gates fail.** Remaining 34 gates pass (mostly by absence — no animations, no forms, no Lottie, no Three.js, no eyebrow patterns, no sticky elements).

---

## Summary

**7 critical · 9 major · 4 minor**

**Verdict — ships as slop.**

This page is a near-perfect specimen of the AI-generated landing page: every structural, typographic, and motion choice lands on the highest-probability training-data default. The three invented metrics (+47% / 50,000+ / 10×) are textbook fabrications. The fake browser mockup is one of the strongest AI tells in the wild. The purple gradient appears three times. The three-equal-card feature grid, the AI nav, the AI footer, the centred hero, and the single system font make this unmistakably generated.

No single fix resolves this page. It requires a structural rebuild with a non-default macrostructure, a real token system, a display/body font pairing, replaced emoji icons, removed chrome, and verified real-world metrics.
