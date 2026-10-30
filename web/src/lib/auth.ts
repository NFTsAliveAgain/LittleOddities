import "server-only";
import { SignJWT, jwtVerify } from "jose";
import { cookies } from "next/headers";
import { getAddress, isAddress } from "viem";
import { publicClient } from "./contract";

const SESSION = "naa_admin";
const NONCE = "naa_nonce";

function secret() {
  const s = process.env.SESSION_SECRET || "";
  if (s.length < 32) throw new Error("SESSION_SECRET must be set to at least 32 random characters");
  return new TextEncoder().encode(s);
}

export function adminAddresses(): string[] {
  return (process.env.ADMIN_ADDRESSES || "").split(",").map((a) => a.trim()).filter((a) => isAddress(a)).map((a) => getAddress(a));
}

export const signInMessage = (address: string, nonce: string, purpose = "admin sign-in") =>
  `NFTs Alive Again ${purpose}\n\nThis signature proves you control this wallet. It costs nothing and sends no transaction.\n\nAddress: ${address}\nNonce: ${nonce}`;

export async function issueNonce(): Promise<string> {
  const nonce = crypto.randomUUID();
  const token = await new SignJWT({ nonce }).setProtectedHeader({ alg: "HS256" }).setExpirationTime("10m").sign(secret());
  (await cookies()).set(NONCE, token, { httpOnly: true, sameSite: "strict", secure: process.env.NODE_ENV === "production", path: "/", maxAge: 600 });
  return nonce;
}

/** Verifies a signed message for the current nonce. Supports normal wallets and smart wallets (ERC-1271). */
export async function verifyWalletSignature(address: string, signature: `0x${string}`, purpose: string): Promise<string | null> {
  const jar = await cookies();
  const t = jar.get(NONCE)?.value;
  if (!t || !isAddress(address)) return null;
  let nonce: string;
  try {
    nonce = (await jwtVerify(t, secret())).payload.nonce as string;
  } catch {
    return null;
  }
  jar.delete(NONCE); // single use
  const addr = getAddress(address);
  const ok = await publicClient.verifyMessage({ address: addr, message: signInMessage(addr, nonce, purpose), signature }).catch(() => false);
  return ok ? addr : null;
}

export async function startAdminSession(address: string) {
  const token = await new SignJWT({ sub: address, role: "admin" }).setProtectedHeader({ alg: "HS256" }).setExpirationTime("8h").sign(secret());
  (await cookies()).set(SESSION, token, { httpOnly: true, sameSite: "strict", secure: process.env.NODE_ENV === "production", path: "/", maxAge: 8 * 3600 });
}

export async function endAdminSession() {
  (await cookies()).delete(SESSION);
}

/** Returns the admin address if the request has a valid session AND the address is still an admin. */
export async function currentAdmin(): Promise<string | null> {
  const t = (await cookies()).get(SESSION)?.value;
  if (!t) return null;
  try {
    const { payload } = await jwtVerify(t, secret());
    const a = String(payload.sub);
    return adminAddresses().includes(a) ? a : null;
  } catch {
    return null;
  }
}
