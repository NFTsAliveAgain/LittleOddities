"use client";
import { useCallback, useEffect, useState } from "react";
import { useAccount } from "wagmi";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { ADMIN_TABLES } from "@/lib/admin-tables";
import { useWalletSignature } from "./useWalletSignature";
import ContractControls from "./ContractControls";

type Row = Record<string, string | number | null>;
const BOOL = new Set(["published", "holders_only", "open"]);
const LONG = new Set(["body", "detail", "description", "value", "note"]);
const ENUMS: Record<string, string[]> = {
  status: ["planned", "in_progress", "completed"],
};
const ENUMS_BY_TABLE: Record<string, Record<string, string[]>> = {
  suggestions: { status: ["pending", "approved", "rejected", "done"] },
  giveaways: { status: ["planned", "open", "closed", "distributed"] },
  events: { kind: ["event", "contest", "giveaway", "space", "other"] },
  polls: { kind: ["poll", "character"] },
};

export default function AdminApp() {
  const { isConnected } = useAccount();
  const sign = useWalletSignature();
  const [authed, setAuthed] = useState<boolean | null>(null);
  const [tab, setTab] = useState("roadmap_items");
  const [err, setErr] = useState("");

  useEffect(() => { fetch("/api/admin/settings").then((r) => setAuthed(r.ok)); }, []);

  async function signIn() {
    setErr("");
    try {
      const { address, signature } = await sign("admin sign-in");
      const r = await fetch("/api/auth/verify", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ address, signature }) });
      const j = await r.json();
      if (!r.ok) throw new Error(j.error);
      setAuthed(true);
    } catch (e) { setErr((e as Error).message); }
  }

  if (authed === null) return <div className="mx-auto max-w-5xl px-4 py-12">Loading…</div>;
  if (!authed) {
    return (
      <div className="mx-auto max-w-lg px-4 py-16">
        <div className="card p-6">
          <h1 className="font-display font-black text-3xl">Owner dashboard</h1>
          <p className="mt-2 text-sm">Sign in by connecting the owner wallet and signing a free message. No password, no transaction, no gas.</p>
          <div className="mt-4">{isConnected ? <button className="btn bg-butter" onClick={signIn}>Sign in with wallet</button> : <ConnectButton />}</div>
          {err && <p className="mt-3 text-sm text-tomato" role="alert">{err}</p>}
        </div>
      </div>
    );
  }
  return (
    <div className="mx-auto max-w-7xl px-4 py-10">
      <div className="flex justify-between items-center flex-wrap gap-3">
        <h1 className="font-display font-black text-4xl">Owner dashboard</h1>
        <button className="btn bg-white" onClick={() => fetch("/api/auth/logout", { method: "POST" }).then(() => setAuthed(false))}>Sign out</button>
      </div>
      <div className="mt-6 flex flex-wrap gap-2">
        {[...Object.entries(ADMIN_TABLES).map(([k, v]) => [k, v.label]), ["contract", "Mint settings (on-chain)"]].map(([k, label]) => (
          <button key={k} className={`btn py-1 text-sm ${tab === k ? "bg-ink text-cream" : "bg-white"}`} onClick={() => setTab(k)}>{label}</button>
        ))}
      </div>
      <div className="mt-6">{tab === "contract" ? <ContractControls /> : <TableEditor key={tab} table={tab} />}</div>
    </div>
  );
}

function TableEditor({ table }: { table: string }) {
  const spec = ADMIN_TABLES[table];
  const [rows, setRows] = useState<Row[]>([]);
  const [draft, setDraft] = useState<Row>({});
  const [msg, setMsg] = useState("");
  const load = useCallback(() => fetch(`/api/admin/${table}`).then((r) => r.json()).then((j) => setRows(j.rows || [])), [table]);
  useEffect(() => { load(); }, [load]);

  async function call(method: string, body: Row) {
    const r = await fetch(`/api/admin/${table}`, { method, headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
    const j = await r.json();
    setMsg(r.ok ? "Saved ✓" : j.error);
    if (r.ok) load();
    return r.ok;
  }
  const idKey = table === "settings" ? "key" : "id";
  const readOnly = spec.columns.length === 0;

  return (
    <div className="grid gap-4">
      {table === "giveaway_winners" && <p className="card p-4 text-sm bg-butter/40">Record a winner only after the NFT transfer has really happened. Paste the real transaction hash from Etherscan — the public page links to it as proof.</p>}
      {table === "roadmap_items" && <p className="card p-4 text-sm bg-butter/40">Only mark an item &ldquo;completed&rdquo; when it is genuinely done. Visitors see these statuses exactly as set here.</p>}
      {!readOnly && table !== "suggestions" && (
        <div className="card p-4">
          <h2 className="font-display font-black text-xl">Add new</h2>
          <Fields table={table} cols={spec.columns} row={draft} onChange={setDraft} />
          <button className="btn bg-mint mt-3" onClick={async () => { if (await call("POST", draft)) setDraft({}); }}>Add</button>
        </div>
      )}
      {msg && <p className="text-sm font-bold" role="status">{msg}</p>}
      {rows.map((r) => <RowEditor key={String(r[idKey])} table={table} row={r} idKey={idKey} cols={spec.columns} onSave={(b) => call("PATCH", b)} onDelete={() => confirm("Delete this item?") && call("DELETE", { id: r[idKey] })} readOnly={readOnly} />)}
      {!rows.length && <p className="opacity-60">Nothing here yet.</p>}
    </div>
  );
}

function RowEditor({ table, row, idKey, cols, onSave, onDelete, readOnly }: { table: string; row: Row; idKey: string; cols: string[]; onSave: (b: Row) => void; onDelete: () => void; readOnly: boolean }) {
  const [r, setR] = useState(row);
  if (readOnly) return <pre className="card p-3 text-xs overflow-auto">{JSON.stringify(row)}</pre>;
  return (
    <div className="card p-4">
      <div className="text-xs opacity-60 mb-2">{idKey} {String(row[idKey])}{table === "suggestions" ? ` · from ${row.author} · ${row.created_at}` : ""}</div>
      {table === "suggestions" && <p className="mb-2">{String(row.body)}</p>}
      <Fields table={table} cols={cols.filter((c) => !(table === "settings" && c === "key"))} row={r} onChange={setR} />
      <div className="mt-3 flex gap-2">
        <button className="btn bg-butter py-1" onClick={() => onSave({ ...Object.fromEntries(cols.map((c) => [c, r[c]])), id: row[idKey] })}>Save</button>
        <button className="btn bg-white py-1" onClick={onDelete}>Delete</button>
      </div>
    </div>
  );
}

function Fields({ table, cols, row, onChange }: { table: string; cols: string[]; row: Row; onChange: (r: Row) => void }) {
  return (
    <div className="grid sm:grid-cols-2 gap-3">
      {cols.map((c) => {
        const opts = ENUMS_BY_TABLE[table]?.[c] || (table === "roadmap_items" ? ENUMS[c] : undefined);
        const v = row[c] ?? "";
        const set = (val: string | number) => onChange({ ...row, [c]: val });
        return (
          <label key={c} className={`text-sm font-bold ${LONG.has(c) ? "sm:col-span-2" : ""}`}>{c.replace(/_/g, " ")}
            {BOOL.has(c) ? <input type="checkbox" className="ml-2 scale-125" checked={Number(v) === 1} onChange={(e) => set(e.target.checked ? 1 : 0)} />
              : opts ? <select className="input mt-1 font-normal" value={String(v)} onChange={(e) => set(e.target.value)}><option value="">—</option>{opts.map((o) => <option key={o}>{o}</option>)}</select>
              : LONG.has(c) ? <textarea className="input mt-1 font-normal min-h-20" value={String(v)} onChange={(e) => set(e.target.value)} />
              : <input className="input mt-1 font-normal" value={String(v)} onChange={(e) => set(e.target.value)} />}
          </label>
        );
      })}
    </div>
  );
}
