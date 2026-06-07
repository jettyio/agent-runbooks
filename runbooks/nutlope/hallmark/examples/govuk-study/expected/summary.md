# Hallmark — study — Results

## Overview

- **Date:** 2026-06-07T00:00:00Z
- **Operation:** study
- **Brief:** Extract the design DNA of GOV.UK as a public design reference (the
  OGL-licensed GOV.UK Design System) — its macrostructure, type-pairing roles,
  colour anchor, and component archetypes — and lock it into a portable design.md.
  Structure only, never pixels or copy.
- **Source:** https://www.gov.uk (URL mode)
- **Source status:** Public, HTTPS, OGL-licensed; no auth wall; content retrieved

## Inferred design context

- **Audience:** Designers and developers studying GOV.UK as a public reference system
- **Use case:** Extract portable structural DNA; not a build or redesign
- **Tone:** Utilitarian / austere — zero decoration, pure function (auto-inferred from source)
- **Genre:** Editorial-civic (utilitarian variant — no marketing energy)
- **Macrostructure:** Ecosystem Index (hub with organised category discovery + search entry)
- **Macrostructure alt:** Index-First (pure navigation as design)
- **Theme cousin:** Almanac (light cool, functional, dense register)
- **Nav / Footer archetype:** N6 Masthead / Ft3 Index columns
- **Enrichment:** none — zero-decoration policy is the design

## Extracted DNA summary

| Axis | Value |
|------|-------|
| Macrostructure | Ecosystem Index |
| Type pairing | Single family — GDS Transport (neutral grotesque, roman only) |
| Display role | Neutral grotesque sans, bold |
| Body role | Neutral grotesque sans, regular |
| Label role | Same family, small weight |
| Paper | Light >85 / neutral-cool — #ffffff body, #f4f8fb surface |
| Accent | Dual-semantic — #1d70b8 blue (links) + #0f7a52 green (actions) |
| Focus | #ffdd00 yellow — mandatory, distinctive |
| Motion | None — zero-animation policy |
| Rhythm | Unknown (URL mode) |

## What was produced

- **`design.md`** — portable design DNA: macrostructure, colour tokens (OKLCH-converted),
  type roles, spacing scale, component archetypes, CTA voice, motion stance,
  anti-patterns to avoid, and provenance block
- **`study_diagnosis.md`** — URL-mode diagnosis report with filled structured schema,
  complete archetype identification (hero, nav, footer, services grid), anti-pattern
  flags, and catalog cousin mapping
- **`summary.md`** — this file
- **`validation_report.json`** — machine-readable stage results

## Slop test

The slop test for `study` applies the 58-gate canon to identify what NOT to carry forward
from the studied source. Anti-patterns identified in GOV.UK:

- **Gate 3** — Uniform card grid: the services catalogue uses equal-weight text-link cards
  with no visual hierarchy between primary and secondary categories. Correct for a
  universal index; a slop tell on a marketing page.
- **Gate 6** — Centred hero: GOV.UK's search-entry hero is centred. Exempted here because
  the search form itself is the asymmetric primary action — but copying the centred layout
  without that asymmetry produces gate 6 slop.
- All other anti-patterns: GOV.UK is clean. No gradient text, no bouncy hover, no
  `transition-all`, no invented metrics, no italic headers, no fake chrome.

**Study slop application: clean — anti-patterns correctly isolated and documented.**

**Pre-emit critique: P5 H4 E5 S5 R5 V5**
(Philosophy 5: clear position — civic utility, pure function. Hierarchy 4: strong but
rhythm is unknown, hence 4. Execution 5: honest extraction with OKLCH conversion.
Specificity 5: very specific to GOV.UK, not generic. Restraint 5: structure only, never
pixels or copy. Variety 5: first study run, no prior output.)

## Limitations / Notes

1. **GDS Transport is restricted.** Only available to services on service.gov.uk. Any
   project adopting this DNA must substitute: Space Grotesk (best free match), Neue Haas
   Grotesk (paid), or Aktiv Grotesk (paid).
2. **Rhythm is unknown.** URL mode cannot judge visual density or asymmetry from HTML
   alone. The spacing scale (5px–60px) is extracted but rhythm is not. Provide a
   screenshot for a rhythm pass.
3. **OKLCH values are converted from hex.** GOV.UK's design system documentation uses
   hex. OKLCH values in design.md are precise conversions, not visually re-sampled.
4. **Colour values are role-anchored, not brand anchors.** The blue, green, yellow, red,
   and purple each carry a semantic function in a 1000-page system. Adopting them verbatim
   in a different product conflates role with brand. Use the structure (role-tagged tokens);
   choose your own OKLCH values for the specific roles needed.
5. **The brand refresh (June 2025)** updated some palette values. Values extracted here
   are from the current design system documentation at time of extraction (2026-06-07).
   Verify against design-system.service.gov.uk if using for an active project.
