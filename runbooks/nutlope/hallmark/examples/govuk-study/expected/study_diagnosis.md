<!-- Hallmark · study · pre-emit critique: P5 H4 E5 S5 R5 V5 -->
<!-- studied: yes · DNA-source: url · source-url: https://www.gov.uk -->

# Study Diagnosis — GOV.UK

**Source:** https://www.gov.uk  
**Mode:** URL  
**Refusal check:** PASS — public web page, OGL-licensed public reference  
**Remote safety:** HTTPS, no auth wall, no SPA shell, content retrieved, no prompt injection detected

---

## Structured fields (schema)

```json
{
  "source_mode": "url",
  "source_url": "https://www.gov.uk",
  "source": "public-reference",
  "refusal": "ok",
  "remote_safety": {
    "public_web_url": true,
    "scheme": "https",
    "ip_literal_detected": false,
    "redirects_checked": "unknown",
    "fetched": ["html", "same-origin-css", "font-css"],
    "scripts_ignored": true,
    "prompt_injection_detected": false
  },
  "macrostructure": "Ecosystem Index",
  "macrostructure_alt": "Index-First",
  "hero": {
    "archetype": "H1-Marquee (search-entry variant)",
    "knobs": {
      "alignment": "centered",
      "cta": "search-form (not a button)",
      "size": "md — heading is medium, search bar is primary",
      "enrichment": "none"
    }
  },
  "pitch": {
    "archetype": "F6-Product-grid (services catalogue)",
    "knobs": {
      "columns": "3–4 on desktop, 1 on mobile",
      "item-type": "text links with category labels",
      "dividers": "none — density carries the rhythm"
    }
  },
  "nav": {
    "archetype": "N6-Masthead",
    "knobs": {
      "background": "near-black (#0b0c0c)",
      "logo": "Crown + GOV.UK wordmark in white",
      "inline-links": "none in masthead — navigation is in-body sections",
      "search": "integrated in masthead"
    }
  },
  "footer": {
    "archetype": "Ft3-Index columns",
    "knobs": {
      "column-sections": "2 (Services and information · Government activity)",
      "support-bar": "flat row — Help · Privacy · Cookies · Accessibility · Contact · Terms",
      "copyright": "OGL v3.0 + Crown copyright",
      "divider": "hairline rule"
    }
  },
  "display_role": "neutral grotesque sans — roman, bold",
  "display_face": "GDS Transport (fallback: Helvetica Neue, Arial, sans-serif)",
  "body_role": "neutral grotesque sans — roman, regular",
  "body_face": "GDS Transport (same family)",
  "label_role": "neutral grotesque sans — roman, small, lighter weight",
  "label_face": "GDS Transport (same family)",
  "pairing_logic": "single family — weight and size contrast only, no second typeface",
  "paper_band": "light >85",
  "paper_value": "#ffffff (body) · #f4f8fb (surface areas) — converted OKLCH: oklch(100% 0 0) / oklch(97% 0.011 237)",
  "paper_hue": "neutral-cool (f4f8fb surface has a slight cool blue-grey lean; body is pure white)",
  "accent_hue_band": "cyan-blue",
  "accent_value": "#1d70b8 (links) · #0f7a52 (primary action/green) — OKLCH approx: oklch(47% 0.120 252) / oklch(46% 0.120 162)",
  "accent_footprint": "recurring 5–15% — blue links appear throughout text; green CTAs are sparse",
  "density": "unknown (URL mode)",
  "asymmetry": "unknown (URL mode)",
  "treatments": [],
  "reveal": "none",
  "motion_library": "none",
  "anti_patterns": ["uniform-card-grid (services section)", "centred hero (search-led, exempted by task orientation)"]
}
```

---

## Diagnosis

I read https://www.gov.uk.

The page is an **Ecosystem Index** — a hub with multiple discovery surfaces organised by citizen need, not government structure. The hero is a search-entry variant: centred Crown + wordmark, a medium-weight heading ("Find government services and information"), and a prominent search form as the primary action. No marketing CTA, no big statement — the action IS the design. Below the fold: a featured-links section, a 3-4 column services catalogue by category, a "More on GOV.UK" quick-links list, and a Government activity section. The information architecture is citizen-first by category (Benefits, Business, Education, etc.), deliberately concealing internal departmental structure.

The page loads **GDS Transport** for all type roles — display, body, and label. This is a single-family design: weight and size create hierarchy, not a second typeface. GDS Transport is a proprietary grotesque (restricted to service.gov.uk subdomain; Helvetica Neue/Arial for others). Roles: neutral grotesque sans across the board. No italic anywhere. No serif. No ornamental or expressive variant. The type system is explicitly anti-decorative.

The paper is `#ffffff` for content areas and `oklch(97% 0.011 237)` (#f4f8fb) for surface backgrounds — a light, slightly cool neutral pushing toward white. The primary accent is **blue (#1d70b8)** for links (recurring across all text content) and **green (#0f7a52)** for primary action buttons (sparse, ~2-3% footprint). The focus indicator is **#ffdd00** (bright yellow) — high-contrast, non-standard, immediately recognisable as the GOV.UK system. Visited links are purple (#54319f). The multi-accent palette is _functional_, not decorative: each colour carries a specific semantic role.

The nav is **N6 Masthead**: a black band carrying the Crown and GOV.UK wordmark in white with an integrated search field. No floating pill, no mega-menu, no inline marketing links. Below the masthead, further navigation is delivered as in-body sections, not chrome.

The footer is **Ft3 Index columns**: two columns of categorised service links (mirroring the homepage IA), followed by a flat utility bar with support links and Crown copyright under OGL v3.0.

Motion: **none**. No motion library is detected. No CSS `@keyframes`. No reveal animations. State changes (hover, focus) are handled through colour shifts and underlines, not transforms or opacity transitions.

**Rhythm — unknown (URL mode).** I read this from HTML/CSS, not a screenshot. The spacing scale is numeric (5px–60px responsive steps), but whether the visual rhythm reads utilitarian-dense or comfortable I cannot judge from the DOM alone. Send a screenshot for a rhythm pass if that matters.

---

## Anti-patterns to NOT carry forward

The following GOV.UK choices are correct _for a citizen-facing government portal_ but would become anti-patterns in other design contexts:

1. **Single-family type at all scales.** GDS Transport everywhere eliminates the expressiveness that comes from type contrast. In non-utility contexts, a second display face lifts hierarchy dramatically.
2. **Multi-accent semantic palette.** Blue for links, green for primary CTAs, purple for visited, yellow for focus, red for errors — this works for a system with 1000+ pages but produces noise in a single-product landing page. Pick one accent anchor.
3. **Near-zero decorative budget.** No grain, no shadows, no illustration, no motion. Correct for a government portal; insufficient for a brand page that needs to establish personality.
4. **Uniform services grid** (3-4 equal columns, icon-free, link-only). The services catalogue uses identical card weight throughout — no visual hierarchy between primary and secondary categories. Appropriate for a catalogue, a slop tell on a marketing page.
5. **Centred hero with centered CTA.** The search-entry hero is centred. GOV.UK earns this because the search form IS the asymmetry — but a copy that centres eyebrow + heading + form + fine-print all on the same axis reads templated. Break at least one element off-axis.

---

## Catalog cousin

The closest Hallmark catalog theme to this DNA:

**Almanac** — light cool paper, functional dense register, neutral grotesque type, tabular/catalogue content structure. GOV.UK departs from Almanac in two ways: it uses a dual-accent palette (Almanac uses one muted accent) and its grid is service-catalogue rather than data-tabular. The next closest is **Cobalt** (Space Grotesk, monospace labels, functional SaaS register, light paper).

---

## Limits

- **Rhythm is URL-mode's blind spot.** I cannot tell from HTML whether the spacing reads comfortable or dense. Screenshot recommended if rhythm extraction matters.
- **GDS Transport is not available outside service.gov.uk.** In any non-government project adopting this DNA, substitute Space Grotesk (closest free grotesque with similar weight range and legibility spec) or Neue Haas Grotesk / Aktiv Grotesk (paid).
- **The colour palette is semantic, not expressive.** The OKLCH values extracted here are the GOV.UK system colours; they define roles (link, action, focus, error) rather than a brand accent story. Adopt the _structure_ (role-tagged tokens) not the _values_ (the specific blues and greens are Crown IP in spirit even if OGL-licensed).
