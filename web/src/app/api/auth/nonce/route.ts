import { NextResponse } from "next/server";
import { issueNonce } from "@/lib/auth";

export async function GET() {
  return NextResponse.json({ nonce: await issueNonce() });
}
