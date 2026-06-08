# Cloudflare Durable Objects — spec → production DO

Describe a Durable Object in plain language. The agent implements it in **production-ready
TypeScript** on Cloudflare Workers, writes the matching `wrangler.jsonc`, and **self-reviews
the code against Cloudflare's documented gotchas** — the sharp edges that make most DO
implementations subtly wrong:

- **Hibernation clears in-memory state** → persist in `ctx.storage`, never in fields.
- **`setTimeout` doesn't survive eviction** → schedule with `ctx.storage.setAlarm()`.
- **Only one alarm per DO** → multiplex multiple timers into one alarm (`Math.min` of next-due).
- **`await` is a yield point** → a single-threaded DO can still race; use atomic updates.

Converted, with attribution, from **Cloudflare's own Durable Objects reference**
([cloudflare/skills](https://github.com/cloudflare/skills/tree/main/skills/cloudflare/references/durable-objects),
Apache-2.0). The Rules, API notes, patterns, configuration, and gotchas are Cloudflare's;
this runbook turns them into an executable *spec → production DO* build with a self-review.

## Input

| Input | Required | Description |
|-------|----------|-------------|
| **Spec** | yes | The Durable Object to build, in plain language — behavior, persisted state, scheduling, and the HTTP/WebSocket surface. |

## Outputs

| File | Role | What |
|------|------|------|
| `durable_object.ts` | primary | The Durable Object + Worker entry point. |
| `wrangler.jsonc` | secondary | Worker config — `compatibility_date` + the SQLite-class migration. |
| `self_review.md` | secondary | The generated code reviewed against each documented gotcha (Risk / Fix). |
| `validation_report.json` | eval | Programmatic structural validation. |

## Examples (real runs)

**[scheduler-multi-timer](examples/scheduler-multi-timer/)** — the non-obvious case. A DO has
exactly one alarm, but this Scheduler runs two independent recurring jobs (5-min heartbeat +
30-min session expiry). It multiplexes them: store each job's next-due time, arm the single
alarm to `Math.min(...)`, and recompute drift-free in `alarm()`. State persists, so it
survives eviction. → [`durable_object.ts`](examples/scheduler-multi-timer/expected/durable_object.ts)

**[chatroom-websockets](examples/chatroom-websockets/)** — a multi-room chat DO. WebSocket
Hibernation API for broadcast, a SQLite-backed counter incremented with an atomic
`INSERT … ON CONFLICT DO UPDATE` upsert, and a `setAlarm()`-debounced 30-minute idle purge
that rebuilds its schema on reconnect. The self-review guards 9 gotchas. →
[`durable_object.ts`](examples/chatroom-websockets/expected/durable_object.ts)

Both runs passed structural validation (`overall_passed: true`).

## About these examples — an A/B experiment

The two shipped examples are the **WITH-gotchas** arm of an experiment:

> **Do Cloudflare's documented gotchas actually make the agent write better code?**

Same spec, two arms — **WITH** the gotchas injected vs **WITHOUT** — 3 runs each across 2
tasks (**12 runs total**); the gotchas section was the only variable. The result was a
**tie on correctness**: every run, in both arms, avoided every gotcha — including the
non-obvious single-alarm pattern the control arm invented on its own. The gotchas' value
showed up *elsewhere* (traceability, canonical idioms, surfacing subtle config gotchas), and
a naive grep-based scorer was fooled into flagging the WITH arm as *worse* because it cited
the gotchas by name in comments.

📄 **Full write-up with concrete code:** the experiment report is published as a
[secret gist](https://gist.github.com/jlebensold/7db9194a662964b6c4fb02402930ed8a).

## Run it

Fork and run on Jetty's managed sandbox (`claude-code` / `claude-sonnet-4-6`,
`python312-uv` snapshot). No setup; free for your first 10 runs. Or execute `RUNBOOK.md`
locally with any coding agent — pass your DO spec as `{{spec}}`.

## Attribution

Source: **Cloudflare** — [cloudflare/skills, `references/durable-objects`](https://github.com/cloudflare/skills/tree/main/skills/cloudflare/references/durable-objects)
· License: **Apache-2.0**. This runbook re-expresses Cloudflare's reference as an executable
build + self-review; the rules and gotchas are theirs.
