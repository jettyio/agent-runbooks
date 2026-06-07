---
theme: default
title: "Zod — TypeScript-first schema validation"
transition: slide-left
highlighter: shiki
colorSchema: dark
css: styles/tokens.css
---

---
layout: cover
class: 'text-left pl-16'
---

# Zod

<div class="text-2xl mt-2" style="color: #39d353; font-family: 'IBM Plex Mono', monospace;">
TypeScript-first schema validation<br/>with static type inference
</div>

<div class="mt-8 text-sm" style="color: #8b949e;">
colinhacks/zod &nbsp;·&nbsp; v4.4.3 &nbsp;·&nbsp; MIT
</div>

<!-- Open with the tagline. The deck makes the case that Zod is the definitive answer to
the "types don't help me at runtime" problem every TypeScript dev faces. Let the title breathe. -->

---
layout: statement
---

# TypeScript types vanish<br/>at runtime

<div class="mt-6 text-center" style="color: #8b949e; font-size: 0.95em;">
Any data crossing a boundary — API response, env var, form input —<br/>
arrives as <code>unknown</code> at runtime. Your types aren't there to help.
</div>

<!-- The core problem. TypeScript compiles away to JavaScript. Types that look airtight
in your editor provide zero protection against a malformed API payload at midnight on Friday. -->

---
layout: two-cols
---

## Without Zod

```ts
// Types declared separately from runtime checks
type User = {
  id: number;
  email: string;
};

// Guards written by hand — and they drift
function isUser(data: unknown): data is User {
  return (
    typeof data === 'object' && data !== null &&
    typeof (data as any).id === 'number' &&
    typeof (data as any).email === 'string'
  );
}

const raw = await fetch('/api/user').then(r => r.json());
if (!isUser(raw)) throw new Error('unexpected shape');
const user: User = raw; // still "trust me" territory
```

::right::

## With Zod

```ts
import * as z from "zod";

// One schema. Types AND validation together.
const User = z.object({
  id: z.number(),
  email: z.string().email(),
});

type User = z.infer<typeof User>;

const raw = await fetch('/api/user').then(r => r.json());

// Validated. Typed. No manual guard.
const user = User.parse(raw);
console.log(user.email); // string — guaranteed
```

<!-- Left shows the tedious "manual guards + separate types" pattern that every TypeScript dev
has written. Right shows Zod collapsing both concerns into one schema. Change the schema,
the type follows automatically. -->

---
layout: default
---

## Parse untrusted data — get a typed result

```ts {all|1|4-11|14-17|19-26}
import * as z from "zod";

// Define a schema
const Player = z.object({
  username: z.string(),
  xp: z.number().nonnegative(),
  role: z.enum(["admin", "player", "spectator"]),
});

type Player = z.infer<typeof Player>;
// { username: string; xp: number; role: "admin"|"player"|"spectator" }

// Valid input → typed deep clone
const player = Player.parse({
  username: "billie", xp: 100, role: "player"
});
// => { username: "billie", xp: 100, role: "player" }

// Invalid input → structured ZodError
try {
  Player.parse({ username: 42, xp: -5 });
} catch (err) {
  if (err instanceof z.ZodError) {
    err.issues;
    // [{ code: "invalid_type", path: ["username"], ... },
    //  { code: "too_small",    path: ["xp"], ... }]
  }
}
```

<!-- Walk through the core API: define schema, call `.parse()`, get back a strongly-typed
clone. If invalid, throws a structured ZodError with per-field granularity. -->

---
layout: default
---

## Infer static types — no duplication

```ts {all|1-7|9-11|13-16}
import * as z from "zod";

const Player = z.object({
  username: z.string(),
  xp: z.number(),
});

// Extract the TypeScript type — schema IS the source of truth
type Player = z.infer<typeof Player>;
// => { username: string; xp: number }

// Transforms give you distinct input and output types
const WithTimestamp = z.string().transform(s => new Date(s));
type In  = z.input<typeof WithTimestamp>;   // string
type Out = z.output<typeof WithTimestamp>;  // Date
```

<div class="mt-4 text-sm" style="color: #8b949e;">
Change the schema once. The TypeScript type updates everywhere automatically.
</div>

<!-- z.infer<> is the killer feature for TypeScript devs. The schema IS the type.
Change one field in the schema, the type follows. No more keeping them in sync by hand. -->

---
layout: default
---

## `safeParse` — no try/catch required

```ts {all|1-9|11-18}
import * as z from "zod";

const Config = z.object({
  port:    z.number().int().min(1).max(65535),
  host:    z.string(),
  debug:   z.boolean().default(false),
});

// Result is a discriminated union — narrowing is native
const result = Config.safeParse(process.env);

if (!result.success) {
  // result.error is a ZodError
  console.error(result.error.flatten());
  process.exit(1);
}

// result.data is fully typed: { port: number; host: string; debug: boolean }
startServer(result.data);
```

<div class="mt-3 text-sm" style="color: #8b949e;">
`safeParseAsync` handles async refinements and transforms.
</div>

<!-- safeParse returns { success: true; data: T } | { success: false; error: ZodError }.
The discriminated union makes narrowing work naturally — no try/catch, no type assertions. -->

---
layout: fact
---

# 14×

<div class="text-xl mt-2" style="color: #e6edf3;">faster string parsing in Zod 4</div>

<div class="mt-8 text-base" style="color: #8b949e; text-align: center;">
7× faster arrays &nbsp;·&nbsp; 6.5× faster objects &nbsp;·&nbsp; 100× fewer <code>tsc</code> instantiations
</div>

<div class="mt-4 text-xs" style="color: #8b949e; text-align: center;">
Benchmarked against Zod 3 · node v22.13.0 · arm64-darwin
</div>

<!-- Lead with the headline number. v4 was a year in the making — Clerk funded the OSS
fellowship. After 24 Zod 3 minor versions, a rewrite was the only path to these gains.
Released stable; closes 9 of 10 most-upvoted issues. -->

---
layout: two-cols-header
---

## Zod 3 → Zod 4: smaller and faster to compile

::left::

### Bundle size (gzipped)

| Package | Size |
|---|---|
| Zod 3 | 12.47 kb |
| Zod 4 | 5.36 kb |
| Zod 4 / mini | **1.88 kb** |

<div class="mt-3 text-sm" style="color: #8b949e;">
<code>zod/mini</code> uses a functional API that tree-shakes to only what you import.
</div>

::right::

### TypeScript compilation

| | Instantiations |
|---|---|
| Zod 3 | > 25,000 |
| Zod 4 | ~ 175 |

<div class="mt-3 text-sm" style="color: #8b949e;">
Simple <code>z.object().extend()</code> no longer blows up <code>tsc</code> on large codebases.
</div>

<!-- These numbers come from the v4 benchmarking playground in packages/tsc.
Bundle: measured with rollup on a minimal validation script. tsc: extendedDiagnostics
on a 5-field object with extend(). Neither is synthetic — both reflect real-world usage. -->

---
layout: fact
---

# 185M

<div class="text-xl mt-2" style="color: #e6edf3;">weekly npm downloads</div>

<div class="mt-6 text-base" style="color: #39d353; text-align: center;">
42,878 GitHub stars &nbsp;·&nbsp; 734M monthly downloads
</div>

<div class="mt-4 text-sm" style="color: #8b949e; text-align: center;">
Started at 600k/week when v3 launched in May 2021.<br/>
Now in the same download tier as foundational infrastructure libraries.
</div>

<!-- Scale context: 185M weekly puts Zod alongside tools like axios and lodash in download
volume. This isn't a niche utility — it's the default runtime validation layer for TypeScript.
Sources: npm API and GitHub API, June 2026. -->

---
layout: default
---

## An ecosystem built on Zod

<div class="grid grid-cols-2 gap-8 mt-4">
<div>

**API & RPC**
- tRPC — end-to-end type-safe APIs
- Hono `@hono/zod-validator` middleware
- OpenAPI / JSON Schema generation

**Forms**
- react-hook-form `zodResolver`
- Valibot (Zod-compatible API surface)

</div>
<div>

**Data & ORM**
- Drizzle ORM `drizzle-zod`
- Prisma schema generation

**AI / LLM tooling**
- Vercel AI SDK structured outputs
- LangChain tool schemas

</div>
</div>

<div class="mt-6 text-sm" style="color: #8b949e;">
Libraries you already use speak Zod natively — schema definitions travel across your stack.
</div>

<!-- Zod is the runtime validation substrate for a large chunk of the TypeScript ecosystem.
The point: Zod isn't just "useful for validation" — it's the lingua franca that lets a
schema written once be consumed by your API layer, your form library, and your ORM. -->

---
layout: default
---

## `zod/mini` — 1.88 kb when every byte counts

```ts {all|1|3-10|12-17}
import * as z from "zod/mini";

// Functional API — same parse/safeParse/parseAsync behavior
const User = z.object({
  name:  z.string(),
  age:   z.optional(z.number()),
  roles: z.array(z.enum(["admin", "viewer"])),
});

type User = z.infer<typeof User>;

// Checks are composable — bundlers tree-shake what you don't import
const PositiveArray = z.array(z.number()).check(
  z.minLength(1),
  z.refine(arr => arr.every(n => n > 0), "all values must be positive"),
);
```

<div class="mt-3 text-sm" style="color: #8b949e;">
6.6× smaller than Zod 3 · ideal for edge functions, service workers, and tight Lambda budgets
</div>

<!-- zod/mini is a tree-shakable subpackage introduced in v4.
Functional-style API instead of method chaining — z.optional(z.string()) rather than z.string().optional().
Same runtime semantics; just a different API surface that bundlers can prune aggressively. -->

---
layout: default
---

## Get started in 30 seconds

```bash
npm install zod
```

```ts
import * as z from "zod";

// Validate an API response
const Repo = z.object({
  id:          z.number(),
  name:        z.string(),
  stargazers:  z.number(),
  archived:    z.boolean().default(false),
});

type Repo = z.infer<typeof Repo>;

const raw = await fetch("https://api.github.com/repos/colinhacks/zod")
              .then(r => r.json());

const repo = Repo.parse(raw);
console.log(`${repo.name}: ${repo.stargazers} stars`);
// => "zod: 42878 stars"
```

<div class="mt-3 text-sm" style="color: #8b949e;">Zero dependencies. Works in Node.js, Deno, Bun, and every modern browser.</div>

<!-- One npm install. No setup, no config, no peer dependencies.
The example uses the Zod repo itself as the data source — developer audience will appreciate the meta. -->

---
layout: end
class: 'text-center'
---

# One schema. Types that hold<br/>in development **and** production.

<div class="mt-8 text-lg" style="color: #39d353;">
<code>npm install zod</code>
</div>

<div class="mt-6 grid grid-cols-3 gap-4 text-sm" style="color: #8b949e; max-width: 600px; margin: 0 auto;">
<div>📖<br/><a href="https://zod.dev" style="color: #58a6ff;">zod.dev</a></div>
<div>⭐<br/><a href="https://github.com/colinhacks/zod" style="color: #58a6ff;">colinhacks/zod</a></div>
<div>💬<br/><a href="https://discord.gg/KaSRdyX2vc" style="color: #58a6ff;">Discord</a></div>
</div>

<div class="mt-8 text-sm" style="color: #8b949e;">
Try it on one API boundary this week.
</div>

<!-- Callback to the through-line: "One schema definition bridges compile-time and runtime."
The ask is concrete and low-friction: one boundary, this week. Don't oversell. -->
