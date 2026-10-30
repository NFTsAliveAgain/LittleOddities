import { NextResponse } from "next/server";
import { adminAddresses, startAdminSession, verifyWalletSignature } from "@/lib/auth";
import { q } from "@/lib/db";

export async function POST(req: Request) {
  const { address, signature } = await req.json();
  const addr = await verifyWalletSignature(address, signature, "admin sign-in");
  if (!addr) return NextResponse.json({ error: "Signature could not be verified. Please try again." }, { status: 401 });
  if (!adminAddresses().includes(addr)) return NextResponse.json({ error: "This wallet is not an admin." }, { status: 403 });
  await startAdminSession(addr);
  await q("INSERT INTO audit_log (actor, action) VALUES (?, 'sign-in')", [addr]);
  return NextResponse.json({ ok: true, address: addr });
}
