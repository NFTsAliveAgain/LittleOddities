// Builds data/collection.json for the gallery from the art generator's plan.
// Run after:  cd ../art && python generate.py plan
import fs from "node:fs";
const plan = JSON.parse(fs.readFileSync(new URL("../../art/output/plan/plan.json", import.meta.url), "utf8"));
const cfg = JSON.parse(fs.readFileSync(new URL("../../art/config/traits.json", import.meta.url), "utf8"));
const labels = Object.fromEntries(cfg.categories.map((c) => [c.key, c.label]));
const tokens = plan.map((t) => ({ id: t.id, name: t.name, tier: t.tier,
  traits: Object.fromEntries(Object.entries(t.traits).map(([k, v]) => [labels[k], v])) }));
const stats = {};
for (const c of cfg.categories) {
  stats[c.label] = {};
  for (const v of c.values) stats[c.label][v.name] = { tier: v.tier, count: 0 };
}
for (const t of tokens) for (const [k, v] of Object.entries(t.traits)) stats[k][v].count++;
fs.mkdirSync(new URL("../data/", import.meta.url), { recursive: true });
fs.writeFileSync(new URL("../data/collection.json", import.meta.url), JSON.stringify({ engine: cfg.engine, tokens, stats }));
console.log(`collection.json: ${tokens.length} tokens, ${Object.keys(stats).length} trait categories`);
