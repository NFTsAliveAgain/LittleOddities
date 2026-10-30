import { NextResponse } from "next/server";
import { currentAdmin } from "@/lib/auth";
import { q } from "@/lib/db";
import { ADMIN_TABLES } from "@/lib/admin-tables";

type Ctx = { params: Promise<{ table: string }> };

async function guard(ctx: Ctx) {
  const admin = await currentAdmin();
  const { table } = await ctx.params;
  const spec = ADMIN_TABLES[table];
  if (!admin) return { error: NextResponse.json({ error: "Not signed in" }, { status: 401 }) };
  if (!spec) return { error: NextResponse.json({ error: "Unknown table" }, { status: 404 }) };
  return { admin, table, spec };
}

function pick(body: Record<string, unknown>, cols: string[]) {
  const keys = cols.filter((c) => c in body);
  return { keys, vals: keys.map((k) => (body[k] === "" ? null : (body[k] as string | number | null))) };
}

const STATUS = new Set(["planned", "in_progress", "completed"]);

function validate(table: string, body: Record<string, unknown>) {
  if (table === "roadmap_items" && "status" in body && !STATUS.has(String(body.status))) return "Status must be planned, in_progress or completed";
  if (table === "giveaway_winners" && body.tx_hash && !/^0x[0-9a-fA-F]{64}$/.test(String(body.tx_hash))) return "Transaction hash must be 0x + 64 hex characters";
  if (table === "giveaway_winners" && body.wallet && !/^0x[0-9a-fA-F]{40}$/.test(String(body.wallet))) return "Wallet must be a 0x address";
  return null;
}

export async function GET(_: Request, ctx: Ctx) {
  const g = await guard(ctx);
  if ("error" in g) return g.error;
  return NextResponse.json({ rows: await q(`SELECT * FROM ${g.table} ORDER BY ${g.spec.order} LIMIT 500`) });
}

export async function POST(req: Request, ctx: Ctx) {
  const g = await guard(ctx);
  if ("error" in g) return g.error;
  const body = await req.json();
  const err = validate(g.table, body);
  if (err) return NextResponse.json({ error: err }, { status: 400 });
  const { keys, vals } = pick(body, g.spec.columns);
  if (!keys.length) return NextResponse.json({ error: "Nothing to save" }, { status: 400 });
  const verb = g.table === "settings" ? "INSERT OR REPLACE" : "INSERT";
  await q(`${verb} INTO ${g.table} (${keys.join(",")}) VALUES (${keys.map(() => "?").join(",")})`, vals);
  await q("INSERT INTO audit_log (actor, action, detail) VALUES (?, ?, ?)", [g.admin, `create ${g.table}`, JSON.stringify(body).slice(0, 500)]);
  return NextResponse.json({ ok: true });
}

export async function PATCH(req: Request, ctx: Ctx) {
  const g = await guard(ctx);
  if ("error" in g) return g.error;
  const { id, ...body } = await req.json();
  const err = validate(g.table, body);
  if (err) return NextResponse.json({ error: err }, { status: 400 });
  const { keys, vals } = pick(body, g.spec.columns);
  if (!keys.length || id === undefined) return NextResponse.json({ error: "Nothing to update" }, { status: 400 });
  const idCol = g.table === "settings" ? "key" : "id";
  const extra = g.table === "roadmap_items" ? ", updated_at = CURRENT_TIMESTAMP" : "";
  await q(`UPDATE ${g.table} SET ${keys.map((k) => `${k} = ?`).join(", ")}${extra} WHERE ${idCol} = ?`, [...vals, id]);
  await q("INSERT INTO audit_log (actor, action, detail) VALUES (?, ?, ?)", [g.admin, `update ${g.table} ${id}`, JSON.stringify(body).slice(0, 500)]);
  return NextResponse.json({ ok: true });
}

export async function DELETE(req: Request, ctx: Ctx) {
  const g = await guard(ctx);
  if ("error" in g) return g.error;
  if (g.table === "audit_log") return NextResponse.json({ error: "Audit log cannot be edited" }, { status: 403 });
  const { id } = await req.json();
  const idCol = g.table === "settings" ? "key" : "id";
  await q(`DELETE FROM ${g.table} WHERE ${idCol} = ?`, [id]);
  await q("INSERT INTO audit_log (actor, action) VALUES (?, ?)", [g.admin, `delete ${g.table} ${id}`]);
  return NextResponse.json({ ok: true });
}
