import { DurableObject } from "cloudflare:workers";

export interface Env {
  CHAT_ROOM: DurableObjectNamespace;
}

const INACTIVITY_MS = 30 * 60 * 1000; // 30 minutes

export class ChatRoom extends DurableObject {
  // In-memory flag so CREATE TABLE IF NOT EXISTS runs at most once per lifetime,
  // but is explicitly reset to false in alarm() before deleteAll() so the next
  // operation recreates the schema after the purge.
  private schemaReady = false;

  constructor(ctx: DurableObjectState, env: Env) {
    super(ctx, env);
    // Runs on every cold start AND every wake from hibernation.
    // ensureSchema() is cheap (no-op when table exists) and guards the case
    // where the DO was just reconstructed after eviction.
    this.ensureSchema();
  }

  // ── Schema ────────────────────────────────────────────────────────────────

  private ensureSchema(): void {
    if (this.schemaReady) return;
    this.ctx.storage.sql.exec(`
      CREATE TABLE IF NOT EXISTS counters (
        id    INTEGER PRIMARY KEY,
        count INTEGER NOT NULL DEFAULT 0
      )
    `);
    this.schemaReady = true;
  }

  private getCount(): number {
    for (const row of this.ctx.storage.sql.exec<{ count: number }>(
      "SELECT count FROM counters WHERE id = 1"
    )) {
      return row.count;
    }
    return 0;
  }

  // ── HTTP handler ──────────────────────────────────────────────────────────

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/count") {
      this.ensureSchema();
      return Response.json({ messageCount: this.getCount() });
    }

    if (
      request.method === "GET" &&
      url.pathname === "/ws" &&
      request.headers.get("Upgrade")?.toLowerCase() === "websocket"
    ) {
      // acceptWebSocket() opts into the Hibernation API so the DO can sleep
      // between messages without dropping live connections.
      const { 0: client, 1: server } = new WebSocketPair();
      this.ctx.acceptWebSocket(server);
      return new Response(null, { status: 101, webSocket: client });
    }

    return new Response(
      JSON.stringify({ error: "Not found" }),
      { status: 404, headers: { "Content-Type": "application/json" } }
    );
  }

  // ── WebSocket Hibernation API handlers ────────────────────────────────────
  // These are called by the runtime when the DO wakes from hibernation for a
  // message, close, or error event. In-memory state is NOT available here
  // unless it was set in the constructor—everything must come from storage.

  async webSocketMessage(ws: WebSocket, message: string | ArrayBuffer): Promise<void> {
    if (typeof message !== "string") return;

    this.ensureSchema();

    // Atomic upsert: INSERT … ON CONFLICT prevents the TOCTOU race that a
    // read-then-write pattern would create at async yield points.
    this.ctx.storage.sql.exec(`
      INSERT INTO counters (id, count) VALUES (1, 1)
      ON CONFLICT(id) DO UPDATE SET count = count + 1
    `);

    // Reschedule the inactivity alarm on every message. A single alarm slot
    // per DO is sufficient because we always want the deadline relative to
    // the *last* message, not the first.
    await this.ctx.storage.setAlarm(Date.now() + INACTIVITY_MS);

    // Broadcast to every connected socket. getWebSockets() works across
    // hibernation — the runtime rehydrates the set from its own bookkeeping.
    const sockets = this.ctx.getWebSockets();
    for (const socket of sockets) {
      try {
        socket.send(message);
      } catch {
        // Socket already in a closed/errored state; skip silently.
      }
    }
  }

  async webSocketClose(ws: WebSocket, code: number, reason: string, _wasClean: boolean): Promise<void> {
    // Complete the closing handshake from the server side.
    ws.close(code, reason);
  }

  async webSocketError(ws: WebSocket, error: unknown): Promise<void> {
    console.error("ChatRoom WebSocket error:", error);
  }

  // ── Alarm ─────────────────────────────────────────────────────────────────

  async alarm(): Promise<void> {
    // Mark schema gone *before* deleteAll() so that, if the DO stays alive
    // after the purge, the next ensureSchema() call recreates the table.
    this.schemaReady = false;
    // deleteAll() removes all KV entries AND drops all SQLite tables,
    // including the alarm itself—no further fires until a new message arrives.
    await this.ctx.storage.deleteAll();
  }
}

// ── Worker entry point ────────────────────────────────────────────────────────

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // Expected routes:
    //   GET /room/:name/ws     — upgrade to WebSocket
    //   GET /room/:name/count  — message total
    const match = url.pathname.match(/^\/room\/([^\/]+)(\/.*)?$/);
    if (!match) {
      return new Response(
        JSON.stringify({ error: "Usage: /room/:name/ws or /room/:name/count" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const [, roomName, subPath = "/count"] = match;
    const id = env.CHAT_ROOM.idFromName(roomName);
    const stub = env.CHAT_ROOM.get(id);

    // Rewrite the pathname to just the sub-path so the DO receives /ws or /count.
    const doUrl = new URL(request.url);
    doUrl.pathname = subPath;

    return stub.fetch(new Request(doUrl.toString(), request));
  },
};
