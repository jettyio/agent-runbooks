# Self-Review: ChatRoom Durable Object

## Pitfalls guarded against

### 1. Hibernation clears in-memory state
**Risk:** Message count stored as a class property would be lost whenever the DO
hibernates between messages—making the count silently wrong.  
**Fix:** The count lives exclusively in SQLite (`counters` table), never in a field.
Every increment uses `ctx.storage.sql.exec()`, which persists across hibernation and
eviction.

---

### 2. `setTimeout` lost on eviction
**Risk:** A 30-minute `setTimeout` for inactivity cleanup disappears the moment the
runtime evicts the DO, so cleanup never fires.  
**Fix:** Every message calls `await this.ctx.storage.setAlarm(Date.now() + INACTIVITY_MS)`,
replacing any previously scheduled alarm. `setAlarm` is durable—it survives eviction 
and hibernation, and the runtime wakes the DO to execute `alarm()` even after a cold start.

---

### 3. Constructor runs on every wake (cold start + hibernate wake)
**Risk:** Expensive initialization in the constructor re-runs on every wake, blocking
the first request after hibernation.  
**Fix:** The constructor only calls `ensureSchema()`, which executes a single cheap
`CREATE TABLE IF NOT EXISTS` and sets an in-memory `schemaReady` flag. Subsequent calls
are no-ops. No blocking network I/O or expensive computation occurs in the constructor.

---

### 4. Race condition from read-modify-write on the counter
**Risk:** Two concurrent `webSocketMessage` invocations could both read `count = 5`,
both compute `6`, and both write `6`—losing one increment. Even though the DO is
single-threaded, `await` creates a yield point where another request can interleave.  
**Fix:** The counter is updated with a single atomic SQL upsert:
```sql
INSERT INTO counters (id, count) VALUES (1, 1)
ON CONFLICT(id) DO UPDATE SET count = count + 1
```
There is no separate read; the database engine performs the increment atomically.

---

### 5. Not using the WebSocket Hibernation API
**Risk:** Without `acceptWebSocket()` + the hibernation handlers, the DO cannot sleep
between messages, keeping it alive—and billing—at all times. Eviction without the API
also drops all live connections silently.  
**Fix:** `ctx.acceptWebSocket(server)` enrolls every connection in the Hibernation API.
The DO handlers `webSocketMessage`, `webSocketClose`, and `webSocketError` are class
methods, so the runtime can wake the DO for each event without keeping it permanently
resident. `ctx.getWebSockets()` is used for broadcast because it rehydrates the
connection set correctly after a wake.

---

### 6. Schema disappears after `deleteAll()`
**Risk:** `ctx.storage.deleteAll()` drops all SQLite tables. If the DO stays alive
after the alarm fires (e.g., a client reconnects immediately), subsequent SQL calls
fail because the `counters` table no longer exists.  
**Fix:** The `alarm()` handler sets `this.schemaReady = false` *before* calling
`deleteAll()`. The next call to `ensureSchema()` (in `webSocketMessage` or `fetch`)
then recreates the table. The constructor also calls `ensureSchema()` on every wake,
covering the case where the DO was evicted and restarted after the purge.

---

### 7. Compatibility date too old (RPC / hibernation features unavailable)
**Risk:** `compatibility_date` older than `2024-04-03` silently disables Durable Object
RPC. Older dates may also affect WebSocket Hibernation API behavior.  
**Fix:** `wrangler.jsonc` sets `"compatibility_date": "2024-04-03"`.

---

### 8. Wrong migration type (KV vs SQLite)
**Risk:** Using `new_classes` provisions a KV-backed DO; `ctx.storage.sql` is only
available on SQLite-backed instances. Deploying with the wrong migration type causes
runtime errors.  
**Fix:** The migration uses `"new_sqlite_classes": ["ChatRoom"]`, which provisions the
correct SQLite storage backend.

---

### 9. Only one alarm slot per DO
**Risk:** Trying to maintain multiple independent timers fails silently; each `setAlarm`
call replaces the previous one.  
**Acknowledgement:** This is intentional here. We only need one timer (inactivity
deadline), and replacing it on every message is exactly the desired behavior—the clock
restarts from the *last* message, not the first.
