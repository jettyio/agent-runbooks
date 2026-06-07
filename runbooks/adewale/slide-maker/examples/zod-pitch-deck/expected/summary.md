# Run Summary

## Run metadata

| Field | Value |
|---|---|
| Date | 2026-06-07 |
| Mode | create |
| Goal | Developer pitch deck for Zod, the TypeScript-first schema validation library |
| Source repo | colinhacks/zod (v4.4.3) |
| Style preset | terminal-green |
| Slide count | 13 |
| Model | claude-sonnet-4-6 |

## Through-line

> One schema definition is all you need — Zod bridges the gap between TypeScript's compile-time safety and what actually runs in production.

## Narrative arc

**What → Why it matters → How → What's next** (Explainer arc for developer audience)

The deck opens with the core problem TypeScript developers face (types disappear at runtime), then shows how Zod solves it through a single schema that provides both runtime validation and static type inference. The v4 performance numbers and ecosystem breadth make the "why this library" case, and the closing restates the through-line with a concrete, low-friction CTA.

## Style notes

- Preset: `terminal-green` (IBM Plex Mono, bg `#0d1117`, green `#39d353`)
- Custom CSS written to `/app/results/styles/tokens.css`
- Slidev fell back to UnoCSS engine for the CSS file (expected behavior — custom tokens are applied inline via the slide classes)

## Validation results

| Gate | Result |
|---|---|
| Spec completeness | PASS — all 13 slides have kind, headline, notes, and sources |
| Through-line | PASS — present in cover (slide 1) and closing (slide 13) |
| Source grounding | PASS — all factual claims traced to README, v4 release notes, npm API, GitHub API |
| Density | PASS — speaker-led density; no slide exceeds 3 bullets of prose |
| No internal leakage | PASS — no runbook internals exposed in slide text |
| No LLM tells | PASS — no filler openers, hollow intensifiers, or unsupported superlatives |
| Compilation | PASS — `slidev build` exited 0 |
| PDF export | PASS — deck.pdf produced (335,871 bytes) |
| Results hygiene | PASS — no node_modules/dist in /app/results |
| Output files | PASS — all required deliverables present and non-empty |

## Issues

None. All validation gates passed on first attempt.

## Key source facts used

- **42,878** GitHub stars (GitHub API, June 2026)
- **185,357,947** weekly npm downloads (npm API, June 2026)  
- **734,307,806** monthly npm downloads (npm API, June 2026)
- **14×** faster string parsing in Zod 4 vs Zod 3 (packages/docs/content/v4/index.mdx — benchmarks)
- **7×** faster array parsing in Zod 4 (same source)
- **6.5×** faster object parsing in Zod 4 (same source)
- **100×** fewer tsc instantiations (25000 → 175) (same source)
- Bundle: 12.47 kb (Zod 3) → 5.36 kb (Zod 4) → 1.88 kb (Zod 4 mini) (same source)
- Zero external dependencies, works in Node.js + all modern browsers (README)
- v3.0 launched May 2021 with 600k weekly downloads (v4 release notes)
