import { NextResponse } from "next/server";
import { verifyWalletSignature } from "@/lib/auth";
import { holderBalance } from "@/lib/contract";
import { q } from "@/lib/db";

// Real participation only: every vote and suggestion is signed by a real wallet.
export async function POST(req: Request) {
  const { action, address, signature, pollId, optionId, body } = await req.json();
  const purpose = action === "vote" ? "vote" : "suggestion";
  const addr = await verifyWalletSignature(address, signature, purpose);
  if (!addr) return NextResponse.json({ error: "Signature could not be verified." }, { status: 401 });

  if (action === "vote") {
    const [poll] = await q<{ id: number; open: number; holders_only: number; closes_at: string | null }>(
      "SELECT id, open, holders_only, closes_at FROM polls WHERE id = ?", [Number(pollId)]);
    if (!poll || !poll.open || (poll.closes_at && new Date(poll.closes_at) < new Date()))
      return NextResponse.json({ error: "This poll is not open." }, { status: 400 });
    const [opt] = await q("SELECT id FROM poll_options WHERE id = ? AND poll_id = ?", [Number(optionId), poll.id]);
    if (!opt) return NextResponse.json({ error: "Unknown option." }, { status: 400 });
    if (poll.holders_only) {
      const bal = await holderBalance(addr as `0x${string}`).catch(() => 0n);
      if (bal === 0n) return NextResponse.json({ error: "This poll is for Little Oddities holders." }, { status: 403 });
    }
    const existing = await q("SELECT 1 FROM poll_votes WHERE poll_id = ? AND voter = ?", [poll.id, addr]);
    if (existing.length) return NextResponse.json({ error: "This wallet already voted." }, { status: 409 });
    await q("INSERT INTO poll_votes (poll_id, option_id, voter) VALUES (?, ?, ?)", [poll.id, Number(optionId), addr]);
    return NextResponse.json({ ok: true });
  }

  if (action === "suggest") {
    const text = String(body || "").trim();
    if (text.length < 10 || text.length > 1000) return NextResponse.json({ error: "Suggestions must be 10-1000 characters." }, { status: 400 });
    const recent = await q("SELECT 1 FROM suggestions WHERE author = ? AND created_at > datetime('now','-1 day')", [addr]);
    if (recent.length >= 3) return NextResponse.json({ error: "Limit: 3 suggestions per wallet per day." }, { status: 429 });
    await q("INSERT INTO suggestions (author, body) VALUES (?, ?)", [addr, text]);
    return NextResponse.json({ ok: true, note: "Thanks! Suggestions appear publicly after review." });
  }
  return NextResponse.json({ error: "Unknown action" }, { status: 400 });
}
