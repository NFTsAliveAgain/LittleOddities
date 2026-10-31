// Builds data/collection.json for the gallery from the art generator's plan.
// Run after:  cd ../art && python generate.py plan
// Before reveal:  entries are planned CHARACTERS (no token numbers known yet).
// After reveal:   STARTING_INDEX=<contract startingIndex> node scripts/sync-collection.mjs
//                 entries become TOKENS: token T shows character ((T-1+N) % 10000) + 1.
import fs from "node:fs";
const plan = JSON.parse(fs.readFileSync(new URL("../../art/output/plan/plan.json", import.meta.url), "utf8"));
const cfg = JSON.parse(fs.readFileSync(new URL("../../art/config/traits.json", import.meta.url), "utf8"));
const labels = Object.fromEntries(cfg.categories.map((c) => [c.key, c.label]));
const N = process.env.STARTING_INDEX ? Number(process.env.STARTING_INDEX) : null;
if (N !== null && !(N > 0 && N < plan.length)) throw new Error("STARTING_INDEX must be 1..9999 (read it from the contract)");
const chars = plan.map((t) => ({ character: t.id, name: t.name, tier: t.tier,
  traits: Object.fromEntries(Object.entries(t.traits).map(([k, v]) => [labels[k], v])) }));
const tokens = N === null
  ? chars.map((c) => ({ id: c.character, ...c }))
  : chars.map((_, i) => { const c = chars[((i + N) % chars.length)]; return { id: i + 1, ...c }; });
const stats = {};
for (const c of cfg.categories) {
  stats[c.label] = {};
  for (const v of c.values) stats[c.label][v.name] = { tier: v.tier, count: 0 };
}
for (const t of tokens) for (const [k, v] of Object.entries(t.traits)) stats[k][v].count++;
fs.mkdirSync(new URL("../data/", import.meta.url), { recursive: true });
fs.writeFileSync(new URL("../data/collection.json", import.meta.url), JSON.stringify({ engine: cfg.engine, revealed: N !== null, startingIndex: N, tokens, stats }));
console.log(`collection.json (${N === null ? "pre-reveal character preview" : "revealed, startingIndex " + N}): ${tokens.length} entries, ${Object.keys(stats).length} trait categories`);
