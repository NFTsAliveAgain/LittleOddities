import "server-only";
import fs from "node:fs";
import path from "node:path";

export type Token = { id: number; name: string; tier: string; traits: Record<string, string> };
type Data = { engine: string; tokens: Token[]; stats: Record<string, Record<string, { tier: string; count: number }>> };

let cache: Data | null = null;
export function collection(): Data {
  if (!cache) cache = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "collection.json"), "utf8")) as Data;
  return cache;
}

const TIER_RANK: Record<string, number> = { Legendary: 0, Epic: 1, Rare: 2, Uncommon: 3, Common: 4 };

export function search(opts: { q?: string; tier?: string; trait?: string; sort?: string; page?: number; per?: number }) {
  const { tokens } = collection();
  const ql = (opts.q || "").trim().toLowerCase();
  let list = tokens.filter((t) => {
    if (opts.tier && t.tier !== opts.tier) return false;
    if (opts.trait) {
      const [k, v] = opts.trait.split(":");
      if (t.traits[k] !== v) return false;
    }
    if (!ql) return true;
    return String(t.id) === ql.replace("#", "") || t.name.toLowerCase().includes(ql) ||
      Object.values(t.traits).some((v) => v.toLowerCase().includes(ql));
  });
  if (opts.sort === "rarity") list = [...list].sort((a, b) => TIER_RANK[a.tier] - TIER_RANK[b.tier] || a.id - b.id);
  else if (opts.sort === "name") list = [...list].sort((a, b) => a.name.localeCompare(b.name));
  else if (opts.sort === "id-desc") list = [...list].sort((a, b) => b.id - a.id);
  const per = opts.per || 24;
  const page = Math.max(1, opts.page || 1);
  return { total: list.length, page, pages: Math.max(1, Math.ceil(list.length / per)), items: list.slice((page - 1) * per, page * per) };
}

export function token(id: number) {
  return collection().tokens.find((t) => t.id === id) || null;
}
