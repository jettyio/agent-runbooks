# Jetty Investor Pitch Deck

**Through-line:** Jetty turns unreliable AI agents into production-grade workflows by making evaluation a first-class primitive — not an afterthought.

## Deck overview

| Property | Value |
|----------|-------|
| Slide count | 16 |
| Style preset | Bold Signal (`bold-signal`) |
| Density mode | Speaker-led |
| Audience | Seed/Series A investors |
| Source | jettyio/jettyio-skills · jetty.io |

## Files

| File | Description |
|------|-------------|
| `slides.md` | Slidev source — the deck in Markdown |
| `deck.pdf` | Rendered PDF (176 KB, 16 pages) |
| `deck.spec.md` | Full slide specification and source mapping |
| `styles/tokens.css` | Bold Signal color/font token overrides |
| `summary.md` | Run metadata and validation results |
| `validation_report.json` | Machine-readable validation output |

## Running the deck

```bash
# Install dependencies (Node.js 18+ required)
npm install @slidev/cli @slidev/theme-default

# Start dev server (live preview)
npx slidev slides.md

# Export to PDF
npx slidev export slides.md --output deck.pdf --timeout 60000
```

## Narrative arc

Problem → Insight → Solution → Proof → CTA

1. **Cover** — Jetty: AI/ML workflows that check their own work
2. **Problem** — AI agents fail silently in production
3. **Market gap** — The missing evaluation/orchestration layer
4. **Insight** — Evaluation is infrastructure, not a feature
5. **Solution** — Jetty platform overview
6. **Architecture** — The dual feedback loop (inner + outer)
7. **Distribution** — MCP-native, 16 tools, every major agent
8. **Product** — Runbooks with built-in quality gates
9. **Observability** — Full trajectory recording
10. **Traction** — AWS, Google, TU/e, and 6 more customers
11. **Revenue** — 5-tier SaaS from Free to Enterprise
12. **Market** — Category being defined now
13. **GTM** — Developer-led, MCP as distribution channel
14. **Backing** — Hidden Layers, AQC Capital, Mila Ventures
15. **Why now** — The MCP moment
16. **CTA** — Through-line callback + ask
