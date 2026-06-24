---
version: "1.0.0"
evaluation: programmatic
agent: claude-code
model: anthropic/claude-sonnet-4.6
model_provider: openrouter
snapshot: python312-uv
# The headline deliverable — the Durable Object implementation.
primary_outputs:
  - durable_object.ts
origin:
  url: "https://github.com/cloudflare/skills/tree/main/skills/cloudflare/references/durable-objects"
  source_host: "github.com"
  source_title: "Cloudflare Durable Objects reference (cloudflare/skills)"
  imported_at: "2026-06-07T00:00:00Z"
  imported_by: "skill-to-runbook-converter@1.0.0"
  attribution:
    collection_or_org: "cloudflare"
    skill_name: "durable-objects"
    author: "Cloudflare (github.com/cloudflare/skills)"
    license: "Apache-2.0"
    confidence: "high"
secrets: {}
---

# Cloudflare Durable Objects — Build a Durable Object — Agent Runbook

> Converted, with attribution, from **Cloudflare's Durable Objects reference**
> (github.com/cloudflare/skills, Apache-2.0). The Rules, API notes, patterns,
> configuration, and gotchas below are Cloudflare's; this runbook turns them into an
> executable "spec → production DO" build with a self-review against the gotchas.

> **EXECUTE THIS RUNBOOK NOW** with tools. Write the deliverables to `{{results_dir}}`. Your
> first action is a tool call. Do not ask questions — implement the spec.

## Inputs (already provided)

- **Spec:** {{spec}} — the Durable Object to build (behavior, persistence, scheduling, API).
- **Language/runtime:** TypeScript on Cloudflare Workers (the only supported target here).

## Objective

Implement a **production-ready** Cloudflare Durable Object in TypeScript from a spec, and
get it right where most implementations get it wrong. Durable Objects combine compute with
strongly-consistent, co-located storage in globally-unique, single-threaded instances. That
model has sharp edges — hibernation clears in-memory state, `setTimeout` doesn't survive
eviction, only one alarm exists per DO, and `await` is a yield point that allows races even
though the object is single-threaded. This runbook bakes Cloudflare's documented rules,
patterns, and **gotchas** into the build and verifies the output against them, so the code is
deployable, not just plausible.

---

## Parameters

| Parameter | Template Variable | Default | Description |
|-----------|------------------|---------|-------------|
| Results directory | `{{results_dir}}` | `/app/results` | Output directory |
| Spec | `{{spec}}` | *(required)* | The Durable Object to build (behavior, persistence, scheduling, public surface) |

## Dependencies

| Dependency | Type | Required | Description |
|------------|------|----------|-------------|
| *(none at build time)* | — | — | Generates + statically reviews TypeScript; deploying needs `wrangler` + a Cloudflare account (out of scope for this sandbox). |

## The Rules of Durable Objects (apply all six)

1. **One alarm per DO** — schedule multiple events via a queue pattern, not multiple alarms.
2. **~1K req/s per DO max** — shard across DOs for higher throughput.
3. **Constructor runs on every wake** — keep init light; use lazy loading.
4. **Hibernation clears memory** — in-memory state is lost; persist critical data.
5. **Use `ctx.waitUntil()` for cleanup** — ensures completion after the response is sent.
6. **No `setTimeout` for persistence** — use `ctx.storage.setAlarm()` for reliable scheduling.

## API essentials

- A DO extends `DurableObject`; the constructor receives `ctx: DurableObjectState` (storage,
  WebSockets, alarms, `blockConcurrencyWhile`, `waitUntil`) and `env: Env` (bindings).
- **Storage:** `ctx.storage` — KV (`get`/`put`/`delete`/`deleteAll`) and SQL (`ctx.storage.sql.exec(...)`),
  strongly consistent and co-located. SQL gives atomic read-modify-write.
- **WebSocket hibernation:** accept with `ctx.acceptWebSocket(ws)` and handle with the async
  `webSocketMessage(ws, msg)` / `webSocketClose(...)` handlers — these survive hibernation.
  `server.accept()` + `ws.addEventListener('message', …)` does **not** hibernate and drops on
  eviction. Per-connection metadata goes in `ws.serializeAttachment()` (small, JSON-serializable).
- **Alarms:** `ctx.storage.setAlarm(timestampMs)` schedules; the `async alarm()` handler runs.
  One alarm per DO — setting a new alarm replaces the old one.
- **Concurrency:** the DO is single-threaded, but `await` yields. Guard read-modify-write with
  `ctx.blockConcurrencyWhile(async () => { … })` or use atomic SQL.

## Patterns to reach for

- **Rate limiting / distributed lock / counters** → atomic SQL (`ON CONFLICT … DO UPDATE`) or
  `blockConcurrencyWhile`.
- **Real-time / chat** → WebSocket hibernation API + reconnection on the client; persist
  per-connection state with `serializeAttachment()`.
- **Multiple scheduled events** → one alarm + an event queue in storage; on `alarm()`, process
  due events and re-arm the alarm for the next one.
- **Graceful cleanup** → `ctx.waitUntil()` for post-response work; `deleteAll()` for purges.
- **High throughput** → shard across `idFromName()` instances.

## Configuration (wrangler)

`wrangler.jsonc` needs the DO binding and a migration:

```jsonc
{
  "durable_objects": { "bindings": [{ "name": "CHAT_ROOM", "class_name": "ChatRoom" }] },
  "migrations": [{ "tag": "v1", "new_sqlite_classes": ["ChatRoom"] }]
}
```

Migration tags must be **unique and sequential**; RPC needs `compatibility_date >= 2024-04-03`;
raise `limits.cpu_ms` (max 300s) for long work. `deleted_classes` destroys data — prefer
`transferred_classes`; migrations cannot be rolled back (test with `--dry-run`).

---

## Durable Objects Gotchas (the heart — guard against every one)

### Hibernation cleared in-memory state
In-memory fields are lost when the DO hibernates/evicts. Persist with `ctx.storage`;
per-connection metadata with `ws.serializeAttachment()`.
```typescript
// ❌ lost on hibernation
private userCount = 0;
async webSocketMessage(ws, msg) { this.userCount++; }
// ✅ persisted
async webSocketMessage(ws, msg) {
  const c = (await this.ctx.storage.get<number>("userCount")) || 0;
  await this.ctx.storage.put("userCount", c + 1);
}
```

### `setTimeout` didn't fire after restart
`setTimeout` is in-memory; eviction clears it. Use an alarm.
```typescript
// ❌ lost on eviction:  setTimeout(() => this.cleanup(), 3600000)
// ✅ survives:          await this.ctx.storage.setAlarm(Date.now() + 3600000)
//                        async alarm() { await this.cleanup() }
```

### Constructor runs on every wake
Runs on cold start AND on wake-from-hibernation. Keep it light; lazy-load heavy data.

### Race condition despite single-threading
`await` is a yield point — a concurrent request can interleave between a `get` and a `put`.
Use atomic SQL or `blockConcurrencyWhile`.
```typescript
// ❌ race:
const n = (await this.ctx.storage.get("count")) || 0;   // another request can run here
await this.ctx.storage.put("count", n + 1);
// ✅ atomic SQL:
this.ctx.storage.sql.exec("INSERT INTO counters(id,value) VALUES(1,1) ON CONFLICT(id) DO UPDATE SET value=value+1 RETURNING value").one().value;
// ✅ or lock:
await this.ctx.blockConcurrencyWhile(async () => { /* read-modify-write */ });
```

### Only one alarm per DO
Need multiple timers? Keep an event queue in storage and re-arm the single alarm for the next due event.

### WebSockets disconnect on eviction
Use the hibernation handlers (`ctx.acceptWebSocket` + `webSocketMessage`) + client reconnection — not `addEventListener`.

Other documented gotchas: **503 under load** → shard (~1K req/s/DO); **storage quota** (10 GB/DO,
5 GB free account-wide) → cleanup via alarms + `deleteAll`; **CPU time exceeded** (30s default,
300s max) → raise `limits.cpu_ms` or chunk; **migration failed** → unique/sequential tags;
**RPC not found** → `compatibility_date >= 2024-04-03`; **`deleted_classes` destroys data** →
use `transferred_classes`; **cold starts slow** → expected; optimize the constructor / warm
critical DOs. Hibernation caveats: memory cleared, constructor reruns, eviction may happen
instead of hibernation (design for both), attachments must be small + JSON-serializable, an
alarm prevents hibernation until its handler completes.

---

## Step 1: Environment Setup

```bash
mkdir -p "{{results_dir}}"
S="{{spec}}"
[ -n "$S" ] && [ "$S" != "{{spec}}" ] || { echo "ERROR: no spec provided"; exit 1; }
echo "Building Durable Object for spec (first 120 chars): ${S:0:120}"
```

## Step 2: Understand the Spec

Identify, from the spec: the DO's state (what must persist), any **scheduling** (→ alarm, not
`setTimeout`), any **concurrency-sensitive** mutations (→ atomic SQL / `blockConcurrencyWhile`),
any **WebSocket** usage (→ hibernation API), and the **public surface** (HTTP routes / RPC).

## Step 3: Implement `durable_object.ts`

Write the full TypeScript implementation. Apply the Rules, the API, and the Gotchas above. In
particular: persist anything that must survive idle; schedule with `setAlarm`; make counters
atomic; use the WebSocket hibernation handlers; keep the constructor light. The code must be
idiomatic and deployable, not pseudo-code.

## Step 4: Configure `wrangler.jsonc`

Write the Workers config: the DO binding and a `new_sqlite_classes` migration (unique,
sequential tag). Set `compatibility_date >= 2024-04-03`.

## Step 5: Self-Review Against the Gotchas

Write `{{results_dir}}/self_review.md`: for each relevant gotcha, state how the implementation
guards against it (or why it does not apply). Be specific — quote the line that handles it. If
you find a violation, fix the code before finishing (max 3 rounds).

## Step 6: Evaluate & Validate

Evaluate the implementation against the gotcha checklist, then write
`{{results_dir}}/validation_report.json`:

```json
{
  "version": "1.0.0", "run_date": "<ISO>",
  "stages": [
    { "name": "implement", "passed": true, "message": "durable_object.ts written" },
    { "name": "configure", "passed": true, "message": "wrangler.jsonc written" },
    { "name": "self_review", "passed": true, "message": "reviewed against N gotchas" }
  ],
  "results": { "gotchas_guarded": 0 },
  "overall_passed": true
}
```

---

## REQUIRED OUTPUT FILES (MANDATORY)

| File | Description |
|------|-------------|
| `{{results_dir}}/durable_object.ts` | The complete, deployable Durable Object implementation. |
| `{{results_dir}}/wrangler.jsonc` | Workers config: DO binding + migration. |
| `{{results_dir}}/self_review.md` | Per-gotcha review of how the code guards against each. |
| `{{results_dir}}/summary.md` | What was built + the key DO decisions. |
| `{{results_dir}}/validation_report.json` | `stages`, `results`, `overall_passed`. |

The task is NOT complete until every file exists and is non-empty.

---

## Final Checklist (MANDATORY — do not skip)

### Verification Script

```bash
echo "=== FINAL OUTPUT VERIFICATION ==="
RESULTS_DIR="{{results_dir}}"
for f in "$RESULTS_DIR/durable_object.ts" "$RESULTS_DIR/wrangler.jsonc" "$RESULTS_DIR/self_review.md" "$RESULTS_DIR/summary.md" "$RESULTS_DIR/validation_report.json"; do
  [ -s "$f" ] && echo "PASS: $f ($(wc -c < "$f") bytes)" || echo "FAIL: $f is missing or empty"
done
TS="$RESULTS_DIR/durable_object.ts"
grep -q "setTimeout" "$TS" && echo "WARN: setTimeout in code — should be setAlarm for persistence" || echo "PASS: no setTimeout"
grep -qE "acceptWebSocket|webSocketMessage" "$TS" && echo "PASS: uses WebSocket hibernation API" || echo "NOTE: no hibernation API (ok if no WebSockets in spec)"
echo "=== VERIFICATION COMPLETE ==="
```

### Checklist

- [ ] `durable_object.ts` is complete, idiomatic, and deployable (extends `DurableObject`)
- [ ] Anything that must survive idle is persisted in `ctx.storage`, not an in-memory field
- [ ] Scheduling uses `ctx.storage.setAlarm()` + `alarm()`, never `setTimeout`
- [ ] Counters / read-modify-write are atomic (SQL `ON CONFLICT` or `blockConcurrencyWhile`)
- [ ] WebSockets use the hibernation handlers (`acceptWebSocket` + `webSocketMessage`)
- [ ] Only one alarm is used (queue pattern if multiple events are needed)
- [ ] Constructor is light (no heavy work on every wake)
- [ ] `wrangler.jsonc` has the DO binding + a unique/sequential migration tag
- [ ] `self_review.md` addresses each relevant gotcha with a specific reference
- [ ] Verification script printed PASS for every line

**If ANY item fails, go back and fix it. Do NOT finish until all items pass.**

---

## Tips

- **The single-threaded DO still has races.** `await` yields; a second request can run between a
  `get` and a `put`. Make read-modify-write atomic — this is the #1 silent DO bug.
- **Persist before you hibernate.** Treat every in-memory field as ephemeral; if it must
  survive idle, it lives in `ctx.storage` (or a small `serializeAttachment`).
- **`setAlarm`, never `setTimeout`.** Timers die on eviction; the single alarm survives. Re-arm
  it on each relevant event (debounce) and keep a queue in storage if you need several timers.
- **WebSockets must hibernate.** `ctx.acceptWebSocket` + `webSocketMessage`, not
  `addEventListener` — otherwise connections drop when the DO is evicted.
- **Keep the constructor cheap.** It runs on every wake; lazy-load anything expensive.
