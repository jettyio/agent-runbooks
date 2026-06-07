# Zod — Developer Pitch Deck

**Through-line:** One schema definition is all you need — Zod bridges the gap between TypeScript's compile-time safety and what actually runs in production.

**Style:** terminal-green (IBM Plex Mono, GitHub dark bg `#0d1117`, terminal green `#39d353`)

**Slides:** 13  
**Mode:** create  
**Audience:** TypeScript developers (intermediate to senior) evaluating schema validation libraries

---

## How to run

### Prerequisites

- Node.js 18+
- `@slidev/cli` — installed globally or via the project

### Install

```bash
npm install
```

### Preview in browser

```bash
npx slidev slides.md
```

### Export to PDF

```bash
npx slidev export slides.md --output deck.pdf --timeout 60000
```

### Build static site

```bash
npx slidev build slides.md
```

---

## Slide outline

| # | Kind | Headline |
|---|------|---------|
| 1 | cover | Zod — TypeScript-first schema validation |
| 2 | statement | TypeScript types vanish at runtime |
| 3 | two-cols | Define once. Get types and validation together. |
| 4 | default | Parse untrusted data — get a typed result |
| 5 | default | Infer static types — no duplication |
| 6 | default | `safeParse` — no try/catch required |
| 7 | fact | 14× faster string parsing in Zod 4 |
| 8 | two-cols-header | Zod 4 ships smaller and compiles faster |
| 9 | fact | 185M weekly downloads |
| 10 | default | An ecosystem built on Zod |
| 11 | default | `zod/mini` — 1.88 kb |
| 12 | default | Get started in 30 seconds |
| 13 | end | One schema. Types that hold in dev and production. |

---

## Source material

- `colinhacks/zod` README.md — v4.4.3
- `packages/docs/content/v4/index.mdx` — v4 release notes and benchmarks
- `packages/docs/content/ecosystem.mdx` — ecosystem listing
- npm API (June 2026): weekly and monthly download counts
- GitHub API (June 2026): star count, fork count
