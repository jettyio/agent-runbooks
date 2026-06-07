# Hallmark — build — Results

## Overview
- **Date**: 2026-06-07T00:00:00Z
- **Operation**: build
- **Brief**: Single-page site for Marginalia, an independent print quarterly about the future of cities (housing, transit, public space, and the people who shape them). One action: subscribe to the next issue.

## Inferred design context

- **Audience**: Urbanists, architects, and curious city-dwellers — educated, text-comfortable readers who appreciate editorial craft and long-form writing
- **Use case**: Subscribe to the next issue of a print quarterly
- **Tone**: Editorial, warm, literary, print-rooted — text-forward, not a tech product
- **Genre**: Editorial (explicit in brief; default Hallmark genre; no other signal fired)
- **Macrostructure**: Letter (12) — first-person, intimate, no-button-in-fold opening that reads as a personal note from the editors; suits a donor/subscriber appeal for an indie quarterly
- **Theme**: Almanac — warm cream paper (oklch 95% 0.014 80), warm near-black ink (oklch 18% 0.014 55), terracotta accent (oklch 48% 0.19 30°); archival, periodic-publication energy
- **Nav archetype**: N6 Newspaper masthead — full-width, large centred wordmark ("Marginalia"), double hairline rule, issue line above wordmark, nav links below the rule in small caps
- **Footer archetype**: Ft4 Dense typographic colophon — serif family, paragraph layout, includes publication date, ISSN note, back-issues info, and copyright; reads as a print colophon
- **Enrichment**: None (typography only) — the brief is explicitly text-forward; no hero image or illustration needed or appropriate

## What was produced

- **index.html** — Complete standalone letter-form editorial page for Marginalia; links tokens.css and styles.css by relative href; N6 masthead, Letter body, subscribe form, letter close, Ft4 colophon footer
- **styles.css** — All page styles; Hallmark stamp on line 1; pre-emit critique stamped; no inline colour values
- **tokens.css** — Full Hallmark token system: 9 colour tokens (paper, paper-2, paper-3, rule, neutral, muted, ink, accent, focus, success, accent-ink, error-glow, error-bg), 2 font tokens, 12 type-scale tokens, 9 spacing tokens, 6 motion tokens, 2 misc tokens
- **screenshot.png** — Full-page render at 1440×900 @2× devicePixelRatio; fonts loaded from Google Fonts; warm cream paper visible; terracotta accent on subscribe button
- **summary.md** — This file

## Slop test

- **58/58 ✓** — All 58 gates passed after one revision pass (fixes to gates 24, 26, 27, 39, 41)
- Pre-emit critique: **P5 H5 E4 S5 R5 V4**
- Gate fixes applied:
  - Gate 24 (spacing scale): removed `calc(var(--space-sm) + 2px)` from input padding → `var(--space-sm) var(--space-md)`
  - Gate 26 (interactive states): added `:active` to `.footer-link`
  - Gate 27 (reduced-motion): added explicit `transform: none` for `.form-submit:active` under `prefers-reduced-motion: reduce`
  - Gate 39 (input focus ring): replaced `box-shadow` focus with `outline: 2px solid transparent` at rest / `outline-color: var(--color-focus)` on focus-visible — no border width shift
  - Gate 41 (accent-ink token): added `--color-accent-ink` token; used on hover text of accent-filled submit button

## Limitations / notes

- **Google Fonts dependency**: Fraunces and Newsreader load from fonts.googleapis.com. System fallback stack is `Georgia, 'Times New Roman', serif` — legible but visually different. Screenshot was captured with network access (fonts loaded).
- **Subscribe form**: wired to `action="#"` — a back-end handler would need to be connected for production use.
- **Edition data**: Issue numbers, dates, and article summaries are editorial placeholders appropriate for this brief. No quantitative metrics were invented (gate 46 — honest copy).
- **First Hallmark run**: No `.hallmark/log.json` existed; this is the inaugural entry for this project. No diversification constraint applied on macrostructure or theme.
