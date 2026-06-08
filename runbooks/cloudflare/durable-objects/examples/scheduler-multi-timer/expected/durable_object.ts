import { DurableObject } from "cloudflare:workers";

export interface Env {
  SCHEDULER: DurableObjectNamespace;
}

const HEARTBEAT_INTERVAL_MS = 5 * 60 * 1000;   // 5 minutes
const EXPIRY_INTERVAL_MS    = 30 * 60 * 1000;  // 30 minutes
const SESSION_TTL_MS        = 60 * 60 * 1000;  // 1 hour

/**
 * Returns the next future occurrence of a recurring event.
 * Uses floor+1 instead of ceil so that an alarm firing exactly on-schedule
 * still advances to the NEXT interval (avoids immediate re-fire).
 */
function nextOccurrence(base: number, interval: number, now: number): number {
  if (base > now) return base;
  const skipped = Math.floor((now - base) / interval) + 1;
  return base + skipped * interval;
}

export class Scheduler extends DurableObject<Env> {
  // Set before the first await in ensureScheduled — prevents concurrent
  // requests from racing into initialization during the same wake cycle.
  private initGuard = false;

  constructor(ctx: DurableObjectState, env: Env) {
    super(ctx, env);
    // Idempotent DDL — safe to run on every constructor call (cold start or
    // wake from hibernation). No expensive work here; scheduling bootstrap
    // is deferred to ensureScheduled() to keep cold starts fast.
    this.ctx.storage.sql.exec(`
      CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        last_seen  INTEGER NOT NULL
      )
    `);
  }

  /**
   * Called on the first fetch() of each wake cycle.
   * If no alarm is already persisted, writes initial schedule state and arms
   * the first alarm. Guard flag is set before the first await so concurrent
   * requests that arrive mid-await see it and skip — DO single-threading
   * guarantees the flag is visible across the yield point.
   */
  private async ensureScheduled(): Promise<void> {
    if (this.initGuard) return;
    this.initGuard = true; // must be set before first await

    const existingAlarm = await this.ctx.storage.getAlarm();
    if (existingAlarm !== null) return; // already running, nothing to do

    const now = Date.now();
    const nextHeartbeat = now + HEARTBEAT_INTERVAL_MS;
    const nextExpiry    = now + EXPIRY_INTERVAL_MS;

    // Batch these puts — they're written atomically at the checkpoint boundary.
    await this.ctx.storage.put("next_heartbeat", nextHeartbeat);
    await this.ctx.storage.put("next_expiry",    nextExpiry);
    await this.ctx.storage.setAlarm(Math.min(nextHeartbeat, nextExpiry));
  }

  async fetch(request: Request): Promise<Response> {
    await this.ensureScheduled();

    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/status") {
      return this.handleStatus();
    }

    // Convenience endpoint for testing: upsert a session record.
    if (request.method === "POST" && url.pathname === "/session") {
      return this.handleUpsertSession(request);
    }

    return new Response("Not Found", { status: 404 });
  }

  private async handleStatus(): Promise<Response> {
    const lastHeartbeat = await this.ctx.storage.get<number>("heartbeat_last");

    const row = this.ctx.storage.sql
      .exec("SELECT COUNT(*) AS count FROM sessions")
      .one() as { count: number };

    return Response.json({
      lastHeartbeat:   lastHeartbeat != null ? new Date(lastHeartbeat).toISOString() : null,
      activeSessions:  row.count,
    });
  }

  private async handleUpsertSession(request: Request): Promise<Response> {
    const body = await request.json<{ sessionId: string }>();
    if (!body?.sessionId) {
      return new Response("sessionId required", { status: 400 });
    }
    const now = Date.now();
    this.ctx.storage.sql.exec(
      `INSERT INTO sessions (session_id, last_seen) VALUES (?, ?)
       ON CONFLICT(session_id) DO UPDATE SET last_seen = excluded.last_seen`,
      body.sessionId,
      now,
    );
    return Response.json({ ok: true });
  }

  /**
   * Single alarm handler that multiplexes two independent recurring jobs.
   *
   * Pattern: persist `next_heartbeat` and `next_expiry` in KV storage and
   * always set the alarm to min(nextHeartbeat, nextExpiry).  On each wake,
   * run whichever jobs are due, advance their schedules with nextOccurrence()
   * to skip any missed intervals (no catch-up backlog), then re-arm.
   *
   * This survives eviction and hibernation because ALL state lives in storage.
   */
  async alarm(): Promise<void> {
    const now = Date.now();

    const [storedNextHb, storedNextEx] = await Promise.all([
      this.ctx.storage.get<number>("next_heartbeat"),
      this.ctx.storage.get<number>("next_expiry"),
    ]);

    // Fallback to now so a corrupted/missing value still runs and reschedules.
    const nextHb = storedNextHb ?? now;
    const nextEx = storedNextEx ?? now;

    if (now >= nextHb) {
      await this.runHeartbeat(now);
    }

    if (now >= nextEx) {
      this.runExpiry(now);
    }

    const newNextHb = nextOccurrence(nextHb, HEARTBEAT_INTERVAL_MS, now);
    const newNextEx = nextOccurrence(nextEx, EXPIRY_INTERVAL_MS, now);

    // Persist updated schedule before setting the alarm so a crash between
    // setAlarm and put doesn't cause a double-run on the next wake.
    await this.ctx.storage.put("next_heartbeat", newNextHb);
    await this.ctx.storage.put("next_expiry",    newNextEx);
    await this.ctx.storage.setAlarm(Math.min(newNextHb, newNextEx));
  }

  private async runHeartbeat(now: number): Promise<void> {
    await this.ctx.storage.put("heartbeat_last", now);
  }

  private runExpiry(now: number): void {
    const cutoff = now - SESSION_TTL_MS;
    // Atomic DELETE — no read-modify-write race possible.
    this.ctx.storage.sql.exec(
      "DELETE FROM sessions WHERE last_seen < ?",
      cutoff,
    );
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Route all traffic to a single named Scheduler instance.
    const id   = env.SCHEDULER.idFromName("global");
    const stub = env.SCHEDULER.get(id);
    return stub.fetch(request);
  },
} satisfies ExportedHandler<Env>;
