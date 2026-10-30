"use client";
import { useAccount, useSignMessage } from "wagmi";

// Asks the wallet to sign a free, gasless message (same text the server verifies).
export function useWalletSignature() {
  const { address } = useAccount();
  const { signMessageAsync } = useSignMessage();
  return async (purpose: string) => {
    if (!address) throw new Error("Connect your wallet first.");
    const { nonce } = await fetch("/api/auth/nonce").then((r) => r.json());
    const message = `NFTs Alive Again ${purpose}\n\nThis signature proves you control this wallet. It costs nothing and sends no transaction.\n\nAddress: ${address}\nNonce: ${nonce}`;
    const signature = await signMessageAsync({ message });
    return { address, signature };
  };
}
