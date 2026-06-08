# Scheduler DO — Self Review

## Pitfalls Guarded Against

### 1. "Only One Alarm Allowed"
**Problem:** The spec requires two independent recurring schedules (5 min heartbeat, 30 min expiry), but each DO instance supports exactly one alarm slot.

**Solution:** Event-queue pattern. Two `next_*` timestamps are persisted in KV storage. The alarm is always set to `min(next_heartbeat, next_expiry)`. On each `alarm()` call, whichever jobs are due run, their next times are advanced with `nextOccurrence()`, and the alarm is re-armed to the new minimum. This multiplexes N schedules over one alarm slot indefinitely.

---

### 2. "setTimeout Didn't Fire After Restart" / In-Memory State Lost
**Problem:** `setTimeout` and plain instance variables are cleared on eviction and after hibernation.

**Solution:** All persistent state — `heartbeat_last`, `next_heartbeat`, `next_expiry`, and the `sessions` table — lives exclusively in `ctx.storage`. No mutable in-memory state is relied upon between wake cycles. The `initGuard` flag is intentionally ephemeral (lifecycle-scoped) and is set fresh on every constructor run.

---

### 3. "Constructor Runs on Every Wake" / Expensive Initialization
**Problem:** The constructor runs on every cold start and hibernation wake, making expensive work multiply.

**Solution:** The constructor only runs the idempotent `CREATE TABLE IF NOT EXISTS` DDL (cheap). All scheduling bootstrap logic is deferred to `ensureScheduled()`, which is called lazily on the first `fetch()`. The alarm handler (`alarm()`) reads directly from storage and never calls `ensureScheduled()`.

---

### 4. "Race Condition Despite Single-Threading"
**Problem:** Concurrent requests can interleave at `await` points inside `ensureScheduled()`, causing double-initialization.

**Solution:** `initGuard = true` is set **before** the first `await` call. Because the DO is single-threaded, any concurrent request that arrives during the `getAlarm()` await will see `initGuard === true` and return immediately. This follows the Cloudflare-recommended pattern of setting guard state prior to yield points.

---

### 5. Alarm Drift and Tight-Loop After Outage
**Problem:** If the DO is evicted for a long time (e.g., 2 hours), naively setting `next = now + interval` causes drift; naively using `base + interval` can produce a next-time already in the past, triggering an immediate re-fire loop.

**Solution:** `nextOccurrence(base, interval, now)` uses `floor((now - base) / interval) + 1` to compute the first occurrence strictly after `now`, skipping missed intervals without catching up on them. This gives accurate drift-corrected scheduling and guarantees the alarm always advances.

---

### 6. "Migration Failed" / SQLite vs KV DO Class
**Problem:** Using `new_classes` in the migration for a DO that calls `ctx.storage.sql` causes a runtime error — `new_classes` provisions a KV-storage DO.

**Solution:** `wrangler.jsonc` uses `new_sqlite_classes` in the migration, which provisions the correct SQLite-backed storage backend.

---

### 7. Race-Free Session Deletion
**Problem:** A read-then-delete pattern for session expiry would have a TOCTOU window at every `await` point.

**Solution:** `DELETE FROM sessions WHERE last_seen < ?` is a single atomic SQL statement. No read step, no interleaving possible.

---

### 8. Atomicity of Schedule Writes Before Alarm Re-arm
**Problem:** If the DO crashes between persisting `next_*` values and calling `setAlarm()`, the next alarm time may be inconsistent.

**Solution:** `next_heartbeat` and `next_expiry` are written to storage **before** `setAlarm()` is called. Because both puts are batched at the same microtask checkpoint, they commit atomically before the alarm is set. A crash after the puts but before `setAlarm()` means the alarm simply does not re-arm — a safe failure mode, as the next `fetch()` call will call `ensureScheduled()` which checks `getAlarm()` and re-arms if null.
