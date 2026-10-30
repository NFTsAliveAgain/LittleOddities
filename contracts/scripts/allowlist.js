#!/usr/bin/env node
/*
 Little Oddities allowlist tool.

   node scripts/allowlist.js build  allowlist/allowlist.csv   # validate CSV, write root + proofs
   node scripts/allowlist.js check  0xWALLET                   # is this wallet eligible? how many?
   node scripts/allowlist.js export allowlist/export.csv       # export the current list as CSV

 CSV format (header required):  address,allocation
 Output: allowlist/allowlist.json (root + every wallet's proof). The website reads
 web/public/allowlist.json, so build copies it there. The root goes into the
 contract with setMerkleRoot(root) — an owner action, done from the admin guide.
*/
const fs = require("fs");
const path = require("path");
const { StandardMerkleTree } = require("@openzeppelin/merkle-tree");
const { getAddress, isAddress } = require("ethers");

const OUT = path.join(__dirname, "..", "allowlist", "allowlist.json");
const WEB = path.join(__dirname, "..", "..", "web", "public", "allowlist.json");

function readCsv(file) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
  const header = lines.shift().toLowerCase().replace(/\s/g, "");
  if (header !== "address,allocation") throw new Error(`First line must be "address,allocation" (found "${header}")`);
  const seen = new Map();
  const errors = [];
  lines.forEach((line, i) => {
    const [addr, alloc] = line.split(",").map((s) => s.trim());
    const row = i + 2;
    if (!isAddress(addr)) return errors.push(`row ${row}: invalid address "${addr}"`);
    const n = Number(alloc);
    if (!Number.isInteger(n) || n < 1 || n > 1000) return errors.push(`row ${row}: allocation must be a whole number 1-1000`);
    const a = getAddress(addr);
    if (seen.has(a)) return errors.push(`row ${row}: duplicate address ${a} (first on row ${seen.get(a).row})`);
    seen.set(a, { n, row });
  });
  if (errors.length) throw new Error("CSV problems:\n  " + errors.join("\n  "));
  return [...seen.entries()].map(([a, { n }]) => [a, String(n)]);
}

function build(file) {
  const values = readCsv(file);
  if (!values.length) throw new Error("allowlist is empty");
  const tree = StandardMerkleTree.of(values, ["address", "uint256"]);
  const entries = {};
  for (const [i, v] of tree.entries()) entries[v[0].toLowerCase()] = { allocation: Number(v[1]), proof: tree.getProof(i) };
  const out = { root: tree.root, count: values.length, total: values.reduce((s, v) => s + Number(v[1]), 0),
                generatedAt: new Date().toISOString(), entries };
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify(out, null, 2));
  if (fs.existsSync(path.dirname(WEB))) fs.writeFileSync(WEB, JSON.stringify(out));
  // self-check every proof before reporting success
  for (const [addr, e] of Object.entries(entries)) {
    if (!StandardMerkleTree.verify(tree.root, ["address", "uint256"], [getAddress(addr), String(e.allocation)], e.proof))
      throw new Error(`proof self-check failed for ${addr}`);
  }
  console.log(`Allowlist built: ${out.count} wallets, ${out.total} total allowlist mints.`);
  console.log(`Merkle root: ${out.root}`);
  console.log(`Wrote ${OUT}${fs.existsSync(path.dirname(WEB)) ? " and " + WEB : ""}`);
  console.log("Next: owner calls setMerkleRoot(root) on the contract (see docs/ADMIN_GUIDE.md).");
}

function check(addr) {
  const data = JSON.parse(fs.readFileSync(OUT, "utf8"));
  const e = isAddress(addr) && data.entries[addr.toLowerCase()];
  console.log(e ? `ELIGIBLE: ${getAddress(addr)} may mint up to ${e.allocation} on the allowlist.` : `NOT on the allowlist: ${addr}`);
}

function exportCsv(file) {
  const data = JSON.parse(fs.readFileSync(OUT, "utf8"));
  const rows = ["address,allocation", ...Object.entries(data.entries).map(([a, e]) => `${getAddress(a)},${e.allocation}`)];
  fs.writeFileSync(file, rows.join("\n") + "\n");
  console.log(`Exported ${rows.length - 1} wallets to ${file}`);
}

const [cmd, arg] = process.argv.slice(2);
try {
  if (cmd === "build") build(arg || path.join(__dirname, "..", "allowlist", "allowlist.csv"));
  else if (cmd === "check") check(arg);
  else if (cmd === "export") exportCsv(arg || path.join(__dirname, "..", "allowlist", "export.csv"));
  else console.log("usage: node scripts/allowlist.js build <csv> | check <address> | export <csv>");
} catch (e) {
  console.error("ERROR:", e.message);
  process.exit(1);
}
