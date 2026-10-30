import "server-only";
import { createClient, type Client } from "@libsql/client";
import { SCHEMA, SEED } from "./schema";

let client: Client | null = null;
let ready: Promise<void> | null = null;

/** Database: a local file in development, a hosted Turso (libSQL) database in production. */
export function db(): Client {
  if (!client) {
    client = createClient({
      url: process.env.DATABASE_URL || "file:data/local.db",
      authToken: process.env.DATABASE_AUTH_TOKEN || undefined,
    });
  }
  return client;
}

export async function ensureDb() {
  if (!ready) {
    ready = (async () => {
      const c = db();
      await c.batch(SCHEMA.map((sql) => ({ sql, args: [] })), "write");
      const r = await c.execute("SELECT COUNT(*) AS n FROM roadmap_items");
      if (Number(r.rows[0].n) === 0) await c.batch(SEED, "write");
    })();
  }
  return ready;
}

export async function q<T = Record<string, unknown>>(sql: string, args: (string | number | null)[] = []): Promise<T[]> {
  await ensureDb();
  const r = await db().execute({ sql, args });
  return r.rows.map((row) => ({ ...row }) as T);
}
