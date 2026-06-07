# Executive Summary — Jetty Investor Pitch Deck

## Run metadata

| Field | Value |
|-------|-------|
| Goal | Investor pitch deck for Jetty (jetty.io), the agentic evaluation platform for AI/ML workflows |
| Mode | create |
| Style preset | bold-signal (explicitly specified) |
| Source repo | jettyio/jettyio-skills (scraped via WebFetch + GitHub raw) |
| Run date | 2026-06-07 |
| Model | claude-sonnet-4-6 |

## Through-line

> Jetty turns unreliable AI agents into production-grade workflows by making evaluation a first-class primitive — not an afterthought.

## Deck overview

- **Slide count:** 16
- **Narrative arc:** Problem → Insight → Solution → Proof → CTA
- **Density mode:** Speaker-led (1–3 bullets per slide)
- **Audience:** Seed/Series A investors, technically fluent

## Style decision

Bold Signal was explicitly specified as the style preset (`bold-signal`). This is the appropriate choice for an investor pitch deck: dark background (`#1a1a1a`), high-contrast white text, and a strong orange accent (`#FF5722`) that signals confidence and urgency. Fonts: Archivo Black (display) / Space Grotesk (body).

## Source material gathered

| Source | Content extracted |
|--------|------------------|
| `https://raw.githubusercontent.com/jettyio/jettyio-skills/main/README.md` | Platform description, MCP tools, runbook system, compatibility |
| `https://github.com/jettyio/jettyio-skills` | Repo structure, topics, tech stack |
| `https://raw.githubusercontent.com/jettyio/jettyio-skills/main/QUICKSTART.md` | Workflow config schema, setup steps, technical concepts |
| `https://jetty.io` | Value proposition, customers, investors, use cases |
| `https://jetty.io/pricing` | 5-tier pricing model (Free → Enterprise) |

## Validation results

| Gate | Status |
|------|--------|
| Spec completeness | PASS — all 16 slides have kind, headline, notes, sources |
| Through-line | PASS — present in cover (slide 1) and closing (slide 16) |
| Source grounding | PASS — every factual claim traced to source URL or file |
| Density | PASS — all slides within 1–3 bullet budget; no overflow |
| No internal leakage | PASS — no runbook/spec internals in slide text |
| No LLM tells | PASS — no hollow intensifiers, generic transitions, or unsupported superlatives |
| Compilation | PASS — `slidev build` exited 0 |
| PDF export | PASS — `deck.pdf` produced (176,494 bytes) |
| Results hygiene | PASS — no `node_modules/`, `dist/`, or `package*.json` in `/app/results` |
| Output files | PASS — all required deliverables present and non-empty |

## Issues and notes

- `slidev build` emitted two `[INVALID_ANNOTATION]` warnings from `@vueuse/core` — these are upstream library warnings unrelated to slide content and did not affect compilation (exited 0).
- `playwright install chromium` ran silently (no output) but export succeeded, confirming Chromium was available.
- No `node_modules/`, `dist/`, or build scaffolding was written to `/app/results`.

## Deliverables

| File | Size |
|------|------|
| `/app/results/deck.spec.md` | ~4 KB |
| `/app/results/slides.md` | ~6 KB |
| `/app/results/deck.pdf` | 176 KB |
| `/app/results/README.md` | ~1.5 KB |
| `/app/results/styles/tokens.css` | ~3 KB |
| `/app/results/summary.md` | this file |
| `/app/results/validation_report.json` | ~0.5 KB |
