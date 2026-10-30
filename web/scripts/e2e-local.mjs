// LOCAL end-to-end test against a private Hardhat chain + `next dev`.
// Uses Hardhat's PUBLICLY KNOWN test keys (worthless, local only). Run: node scripts/e2e-local.mjs
import { createWalletClient, createPublicClient, http, parseEther, getAddress } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { hardhat } from "viem/chains";
import fs from "node:fs";

const BASE = "http://localhost:3000";
const ADDR = "0x5FbDB2315678afecb367f032d93F642f64180aa3";
const abi = JSON.parse(fs.readFileSync(new URL("../src/lib/abi.json", import.meta.url)));
const owner = privateKeyToAccount("0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80");
const fan = privateKeyToAccount("0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d");
const pub = createPublicClient({ chain: hardhat, transport: http() });
const wallet = (a) => createWalletClient({ account: a, chain: hardhat, transport: http() });
let pass = 0, fail = 0;
const ok = (cond, name) => { cond ? pass++ : fail++; console.log(`${cond ? "PASS" : "FAIL"}  ${name}`); };

class Session {
  constructor() { this.jar = {}; }
  async req(path, opts = {}) {
    const headers = { "content-type": "application/json", cookie: Object.entries(this.jar).map(([k, v]) => `${k}=${v}`).join("; ") };
    const r = await fetch(BASE + path, { ...opts, headers, redirect: "manual" });
    for (const c of r.headers.getSetCookie?.() || []) { const [kv] = c.split(";"); const [k, ...v] = kv.split("="); this.jar[k] = v.join("="); }
    let body = null; try { body = await r.json(); } catch {}
    return { status: r.status, body };
  }
  async signed(account, purpose) {
    const { body } = await this.req("/api/auth/nonce");
    const message = `NFTs Alive Again ${purpose}\n\nThis signature proves you control this wallet. It costs nothing and sends no transaction.\n\nAddress: ${getAddress(account.address)}\nNonce: ${body.nonce}`;
    return { address: account.address, signature: await account.signMessage({ message }) };
  }
}

// --- admin auth
const anon = new Session();
ok((await anon.req("/api/admin/roadmap_items")).status === 401, "admin API rejects visitors without a session");
const intruder = new Session();
const ib = await intruder.signed(fan, "admin sign-in");
ok((await intruder.req("/api/auth/verify", { method: "POST", body: JSON.stringify(ib) })).status === 403, "non-admin wallet cannot sign in");
const forged = new Session();
const fb = await forged.signed(fan, "admin sign-in");
ok((await forged.req("/api/auth/verify", { method: "POST", body: JSON.stringify({ ...fb, address: owner.address }) })).status === 401, "forged signature (fan signs, claims owner) rejected");
const admin = new Session();
const ab = await admin.signed(owner, "admin sign-in");
ok((await admin.req("/api/auth/verify", { method: "POST", body: JSON.stringify(ab) })).status === 200, "owner wallet signs in");
const replay = new Session();
ok((await replay.req("/api/auth/verify", { method: "POST", body: JSON.stringify(ab) })).status === 401, "replayed signature rejected (single-use nonce)");

// --- admin content management
const rm = (await admin.req("/api/admin/roadmap_items")).body.rows;
ok(rm.length === 30 && rm.every((r) => r.status !== "completed"), "roadmap seeded with 30 items, none falsely completed");
ok((await admin.req("/api/admin/roadmap_items", { method: "PATCH", body: JSON.stringify({ id: rm[0].id, status: "done!!" }) })).status === 400, "invalid roadmap status rejected");
ok((await admin.req("/api/admin/roadmap_items", { method: "PATCH", body: JSON.stringify({ id: rm[3].id, detail: "Foundation built; testing in progress." }) })).status === 200, "roadmap item edited");
ok((await admin.req("/api/admin/announcements", { method: "POST", body: JSON.stringify({ title: "E2E test announcement", body: "Hello", published: 1 }) })).status === 200, "announcement created");
ok((await admin.req("/api/admin/settings", { method: "POST", body: JSON.stringify({ key: "discord_url", value: "https://discord.gg/example-test" }) })).status === 200, "social link setting saved");
ok((await admin.req("/api/admin/giveaway_winners", { method: "POST", body: JSON.stringify({ giveaway_id: 1, wallet: fan.address, tx_hash: "0xnotreal" }) })).status === 400, "giveaway winner with fake tx hash rejected");
await admin.req("/api/admin/polls", { method: "POST", body: JSON.stringify({ question: "Which species next?", kind: "character", holders_only: 1, open: 1 }) });
const poll = (await admin.req("/api/admin/polls")).body.rows[0];
await admin.req("/api/admin/poll_options", { method: "POST", body: JSON.stringify({ poll_id: poll.id, label: "Axolotl" }) });
await admin.req("/api/admin/poll_options", { method: "POST", body: JSON.stringify({ poll_id: poll.id, label: "Robot" }) });
const opt = (await admin.req("/api/admin/poll_options")).body.rows.find((o) => o.poll_id === poll.id);

// --- holder-only voting
const voter = new Session();
let v = await voter.req("/api/community", { method: "POST", body: JSON.stringify({ action: "vote", pollId: poll.id, optionId: opt.id, ...(await voter.signed(fan, "vote")) }) });
ok(v.status === 403, "non-holder cannot vote in holder-only poll");

// --- mint on-chain (owner opens public mint; fan mints 2 at exact price)
const C = { address: ADDR, abi };
await pub.waitForTransactionReceipt({ hash: await wallet(owner).writeContract({ ...C, functionName: "setPublicActive", args: [true] }) });
const tx = await wallet(fan).writeContract({ ...C, functionName: "publicMint", args: [2n], value: parseEther("0.01") });
const rc = await pub.waitForTransactionReceipt({ hash: tx });
ok(rc.status === "success", "fan mints 2 for exactly 0.010 ETH");
ok((await pub.readContract({ ...C, functionName: "tokenURI", args: [1n] })) === "ipfs://__METADATA_CID__/1.json", "tokenURI points at metadata file");
try { await wallet(fan).writeContract({ ...C, functionName: "publicMint", args: [1n], value: parseEther("0.006") }); ok(false, "overpayment rejected"); }
catch { ok(true, "overpayment rejected on-chain"); }

v = await voter.req("/api/community", { method: "POST", body: JSON.stringify({ action: "vote", pollId: poll.id, optionId: opt.id, ...(await voter.signed(fan, "vote")) }) });
ok(v.status === 200, "holder votes successfully");
v = await voter.req("/api/community", { method: "POST", body: JSON.stringify({ action: "vote", pollId: poll.id, optionId: opt.id, ...(await voter.signed(fan, "vote")) }) });
ok(v.status === 409, "second vote from same wallet rejected");

// --- suggestions are moderated
const s = await voter.req("/api/community", { method: "POST", body: JSON.stringify({ action: "suggest", body: "Please add a sleepy axolotl!", ...(await voter.signed(fan, "suggestion")) }) });
ok(s.status === 200, "suggestion submitted");
const page = await (await fetch(BASE + "/community")).text();
ok(!page.includes("sleepy axolotl"), "unreviewed suggestion is NOT shown publicly");
ok(page.includes("E2E test announcement") && page.includes("Which species next?"), "published announcement and poll appear publicly");
const sug = (await admin.req("/api/admin/suggestions")).body.rows[0];
await admin.req("/api/admin/suggestions", { method: "PATCH", body: JSON.stringify({ id: sug.id, status: "approved" }) });
ok((await (await fetch(BASE + "/community")).text()).includes("sleepy axolotl"), "approved suggestion appears publicly");
ok((await admin.req("/api/admin/audit_log")).body.rows.length > 5, "admin actions recorded in audit log");

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
