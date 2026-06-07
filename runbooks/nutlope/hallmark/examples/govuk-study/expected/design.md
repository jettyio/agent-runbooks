# Design — GOV.UK DNA (Public Reference Extract)

<!-- Hallmark · study · pre-emit critique: P5 H4 E5 S5 R5 V5 -->
<!-- studied: yes · DNA-source: url · source-url: https://www.gov.uk -->

Portable design DNA extracted from https://www.gov.uk — the OGL-licensed GOV.UK Design
System. This file encodes structural and typographic patterns only. Token values are
derived from official design system documentation (design-system.service.gov.uk).
Do not adopt colour values verbatim; they carry semantic roles defined by a 1000-page
system. Adopt the token _structure_ and the role logic.

## Provenance

- **Source mode:** URL — https://www.gov.uk
- **Extraction date:** 2026-06-07
- **Attestation:** Public reference — OGL v3.0 licensed; operator context asserts
  entitlement to study as a public design reference.
- **Confidence:** Tokens are exact (extracted from design-system.service.gov.uk colour
  documentation). Fonts are exact (GDS Transport confirmed from typeface page). Rhythm
  is unknown — URL mode cannot judge density from HTML alone.

## System

- **Genre** · Editorial (civic utilitarian — purely functional, zero decorative budget)
- **Macrostructure** · Ecosystem Index — hub with multiple discovery surfaces organised
  by citizen need (category catalogue + featured content + search entry)
- **Macrostructure alt** · Index-First — pure navigation as design; no narrative flow
- **Theme cousin** · Almanac (light cool, functional, dense register)
- **Axes** · light >85 / neutral grotesque sans / cyan-blue + green (semantic dual-accent)

## Type

```
Display role:  neutral grotesque sans — roman, bold (700+)
               → GDS Transport (restricted); substitute: Space Grotesk Bold
                 or Neue Haas Grotesk Display
Body role:     neutral grotesque sans — roman, regular (400)
               → GDS Transport (same family); substitute: Space Grotesk Regular
Label role:    neutral grotesque sans — roman, small (400 / 500)
               → GDS Transport (same family)

Pairing logic: SINGLE FAMILY — weight and size alone create hierarchy.
               No second display face. No italic anywhere. All roman.
               The zero-italic discipline is structural, not incidental.

Fallback stack: "GDS Transport", "Helvetica Neue", "Arial", sans-serif
```

## Tokens (extracted from GOV.UK Design System — hex source, OKLCH approximate)

```css
:root {
  /* Paper */
  --color-paper:           oklch(100% 0 0);        /* #ffffff — body background */
  --color-paper-surface:   oklch(97% 0.011 237);   /* #f4f8fb — surface, template bg */
  --color-paper-2:         oklch(96% 0 0);          /* #f3f3f3 — subtle alternate */

  /* Ink */
  --color-ink:             oklch(4.5% 0.005 0);    /* #0b0c0c — primary text */
  --color-ink-2:           oklch(33% 0.003 0);     /* #484949 — secondary text */
  --color-rule:            oklch(83% 0 0);          /* #cecece — borders */
  --color-input-border:    oklch(4.5% 0.005 0);    /* #0b0c0c — form input borders */

  /* Accent — semantic dual-accent system (do not merge) */
  --color-accent-link:     oklch(47% 0.120 252);   /* #1d70b8 — links (blue) */
  --color-accent-link-hover: oklch(34% 0.100 243); /* #0f385c — link hover (dark blue) */
  --color-accent-visited:  oklch(36% 0.175 298);   /* #54319f — visited links (purple) */
  --color-accent-action:   oklch(46% 0.120 162);   /* #0f7a52 — primary button (green) */
  --color-accent-brand:    oklch(47% 0.120 252);   /* #1d70b8 — brand / wayfinding */

  /* Focus — distinctive, non-optional */
  --color-focus:           oklch(90% 0.190 100);   /* #ffdd00 — focus ring (yellow) */
  --color-focus-text:      oklch(4.5% 0.005 0);    /* #0b0c0c — text on focus */

  /* Feedback */
  --color-error:           oklch(47% 0.140 22);    /* #ca3535 — error */
  --color-success:         oklch(46% 0.120 162);   /* #0f7a52 — success (= action) */

  /* Typography */
  --font-display:  "GDS Transport", "Helvetica Neue", Arial, sans-serif;
  --font-body:     "GDS Transport", "Helvetica Neue", Arial, sans-serif;
  --font-mono:     "Courier New", Courier, monospace; /* fallback only; not a design choice */

  /* Spacing — 5px base unit (not 4pt); GOV.UK uses a 5px grid */
  --space-1:  5px;
  --space-2:  10px;
  --space-3:  15px;   /* —mobile */
  --space-4:  20px;   /* 15px mobile */
  --space-5:  25px;   /* 15px mobile */
  --space-6:  30px;   /* 20px mobile */
  --space-7:  40px;   /* 25px mobile */
  --space-8:  50px;   /* 30px mobile */
  --space-9:  60px;   /* 40px mobile */

  /* Grid */
  --grid-max-width: 1020px;
  --grid-columns:   12;

  /* Motion — none is a design choice, not an omission */
  --dur-fast: 0ms;   /* GOV.UK uses no transitions on most elements */
  --dur-base: 100ms; /* state changes only (hover underlines) */
  --ease-out: ease;  /* no custom easing; functional state only */
}
```

## Component archetypes

```
Nav:    N6 Masthead
        — Near-black band (#0b0c0c), Crown symbol + GOV.UK wordmark in white.
        — Integrated search. No floating pill. No inline marketing links.
        — Below masthead: in-body section navigation (not chrome).

Hero:   H1 search-entry variant
        — Centered: Crown + heading (medium, not display-sized) + search form.
        — The search form IS the CTA. No button-only CTA. No subheading superlative.
        — Enrichment: none. Typography only.

Body:   F6 catalogue grid
        — Services by category, 3–4 columns desktop, 1 mobile.
        — Text-link cards, no icons, no card borders, no hover shadows.
        — Title-only cards: category name as the entire information unit.

Footer: Ft3 Index columns
        — 2 column sections (Services / Government activity) + utility bar row.
        — Support links: flat, small, hairline-separated.
        — OGL v3.0 copyright notice.
```

## CTA voice

```
Primary: green (#0f7a52 → var(--color-accent-action)) · no radius or minimal (2–4px)
         · bold weight · white text · no icon
         → "Search" / "Start now" / "Continue" — verb-led, no superlatives
Secondary: white bg · black border · same radius · same weight
           → used for alternative or destructive actions
Focus state: 3px solid var(--color-focus) (#ffdd00) offset 0 — instant, non-animated
```

## Motion stance

```
Stance: motion-cut — deliberate zero-animation policy.
        No entrance reveals, no scroll animations, no hover transforms.
        State changes only: link underlines appear on hover (colour shift only).
        No motion library. No @keyframes.
Reduced-motion: no special rule needed — the baseline is already motion-cut.
```

## Type scale (GOV.UK responsive type)

```
Heading XL: 48px desktop / 32px mobile — bold — govuk-heading-xl
Heading L:  36px desktop / 24px mobile — bold — govuk-heading-l
Heading M:  24px desktop / 18px mobile — bold — govuk-heading-m
Heading S:  19px desktop             — bold — govuk-heading-s
Body:       19px desktop / 16px mobile — regular
Small:      16px desktop / 14px mobile — regular
Caption:    14px — regular
```

## IA and structural DNA

```
Information architecture:  citizen-first by need category,
                           NOT by government department.
Section rhythm:            category → featured → catalogue → activity → footer.
Negative-space discipline: functional (not generous, not dense — exactly enough).
Asymmetry:                 none at page level; centred-container approach.
                           Asymmetry appears at content level (two-thirds + one-third
                           layout for longform service pages, NOT homepage).
Link treatment:            underline on ALL links in body copy — accessibility-mandatory.
Wayfinding:                colour-coded by role (blue=link, green=go, red=stop, yellow=focus).
```

## Notes — anti-patterns NOT to carry forward

These GOV.UK choices are correct for a universal citizen-facing portal.
They become anti-patterns in other design contexts:

1. **Single-family across all scales** — eliminates expressive type contrast. In
   non-utility contexts, add a second display face for hierarchy.

2. **Semantic multi-accent palette** (blue + green + purple + yellow + red) — correct
   for a system with 1000+ templates; produces noise on a single-product page. Collapse
   to one anchor accent + one focus colour.

3. **Zero-decoration budget** — no illustration, no texture, no animation. Extract the
   structural restraint; don't extract the sensory blankness.

4. **Uniform catalogue grid** (equal-weight text-link cards, no title hierarchy) —
   correct for a services index; reads as slop on a marketing page where hierarchy matters.

5. **Centred full-axis hero** — GOV.UK earns it because the search form is the
   asymmetric element. Elsewhere, break at least one element off-centre.

6. **Breadcrumb-heavy navigation** — GOV.UK uses breadcrumbs as primary spatial
   orientation on interior pages. For single-page or shallow IA, omit.
