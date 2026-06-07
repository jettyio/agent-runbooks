# Deck Spec: Zod — Developer Pitch Deck

## Through-line
One schema definition is all you need — Zod bridges the gap between TypeScript's compile-time safety and what actually runs in production.

## Meta
- **Style preset**: terminal-green
- **Target slide count**: 13
- **Density mode**: speaker-led (1–3 bullets per content slide)
- **Audience**: TypeScript developers — intermediate to senior — evaluating schema validation libraries

## Slide List

### Slide 1
- **number**: 1
- **kind**: cover
- **headline**: Zod — TypeScript-first schema validation with static type inference
- **notes**: Open with the tagline. The deck makes the case that Zod is the definitive answer to the "types don't help me at runtime" problem every TypeScript dev faces. Let the title breathe.
- **sources**: colinhacks/zod README.md — tagline: "TypeScript-first schema validation with static type inference"

---

### Slide 2
- **number**: 2
- **kind**: statement
- **headline**: TypeScript types disappear at runtime
- **notes**: The core problem. TypeScript compiles away to JavaScript. Any data crossing a boundary — API response, env var, form input — arrives as `unknown` or `any` at runtime. Types don't protect you there.
- **sources**: General TypeScript behavior; sets up Zod's value proposition

---

### Slide 3
- **number**: 3
- **kind**: two-column
- **headline**: Define once. Get types and validation together.
- **notes**: Left column shows the tedious "manual validation" pattern — writing runtime checks, then re-declaring TypeScript types separately. Right side shows Zod collapsing both into one schema. The cognitive burden drops to zero.
- **sources**: colinhacks/zod README.md — Basic usage section

---

### Slide 4
- **number**: 4
- **kind**: code
- **headline**: Parse untrusted data — get a typed, validated result
- **notes**: Walk through the core API: define schema, call `.parse()`, get back a strongly-typed deep clone. If invalid, throws a structured `ZodError`. This is the happy path.
- **sources**: colinhacks/zod README.md — "Basic usage" and "Handling errors" sections

---

### Slide 5
- **number**: 5
- **kind**: code
- **headline**: Infer static types from your schema — no duplication
- **notes**: `z.infer<>` is the killer feature for TypeScript devs. The schema IS the type. Change one, the other follows automatically. Show the `Player` example from the README.
- **sources**: colinhacks/zod README.md — "Inferring types" section

---

### Slide 6
- **number**: 6
- **kind**: code
- **headline**: `safeParse` returns a discriminated union — no try/catch required
- **notes**: Alternative to `.parse()` for control-flow-friendly code. The result is `{ success: true; data: T } | { success: false; error: ZodError }`. Narrowing works naturally.
- **sources**: colinhacks/zod README.md — "Handling errors" / safeParse section

---

### Slide 7
- **number**: 7
- **kind**: fact
- **headline**: 14× faster string parsing in Zod 4
- **notes**: Lead with the headline number. Then mention the full set: 7× faster arrays, 6.5× faster objects, 100× fewer tsc instantiations. v4 was a year in the making; Clerk funded the fellowship. Released stable after 24 Zod 3 minor versions.
- **sources**: packages/docs/content/v4/index.mdx — Benchmarks section (node v22.13.0, arm64-darwin)

---

### Slide 8
- **number**: 8
- **kind**: two-column-header
- **headline**: Zod 4 ships a smaller bundle and a faster compiler
- **notes**: Header: "Zod 3 → Zod 4". Left: bundle size comparison table (12.47kb → 5.36kb → 1.88kb mini). Right: tsc instantiations (>25000 → ~175). These are not micro-optimizations; they meaningfully affect CI times and cold-start latency.
- **sources**: packages/docs/content/v4/index.mdx — "2x reduction in core bundle size" and "100x reduction in tsc instantiations"

---

### Slide 9
- **number**: 9
- **kind**: fact
- **headline**: 185 million downloads per week
- **notes**: Scale puts Zod in the foundational-library tier. Compare to where it started: 600k weekly downloads at v3 launch in May 2021. Now 42.8K GitHub stars. Context: this is not a niche utility.
- **sources**: npm API (June 2026): 185,357,947 weekly downloads; GitHub API: 42,878 stars; packages/docs/content/v4/index.mdx — v3 baseline of 600k weekly

---

### Slide 10
- **number**: 10
- **kind**: content
- **headline**: An ecosystem built on top of Zod
- **notes**: Zod is the runtime validation substrate for a large chunk of the TypeScript ecosystem. Mention tRPC (end-to-end type safety), react-hook-form+zodResolver, Drizzle ORM, Hono validator middleware, and AI SDK tool schemas. Frame as: "libraries you already use speak Zod natively."
- **sources**: packages/docs/content/ecosystem.mdx — API Libraries, Form Integrations, Powered by Zod sections

---

### Slide 11
- **number**: 11
- **kind**: code
- **headline**: `zod/mini` — 1.88 kb when every byte counts
- **notes**: For edge/serverless with strict bundle budgets. Functional-style API (`z.optional(z.string())` instead of method chaining). Same parse/safeParse/parseAsync behavior. 6.6× smaller than Zod 3's full bundle.
- **sources**: packages/docs/content/v4/index.mdx — "zod/mini" and "6.6x reduction in core bundle size" sections

---

### Slide 12
- **number**: 12
- **kind**: code
- **headline**: Install in 30 seconds — zero configuration required
- **notes**: One npm install. No setup. Show the import and a minimal schema that validates an API response shape. Emphasize zero dependencies — Zod ships nothing but itself.
- **sources**: colinhacks/zod README.md — "Installation" and "Features: Zero external dependencies"

---

### Slide 13
- **number**: 13
- **kind**: closing
- **headline**: One schema. TypeScript types that hold — in development and in production.
- **notes**: Call back to the through-line. Final CTA: `npm install zod`, link to zod.dev, star the repo. The ask for the audience: try it on one API boundary this week.
- **sources**: colinhacks/zod README.md; zod.dev
