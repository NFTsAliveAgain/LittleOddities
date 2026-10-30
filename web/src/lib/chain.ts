"use client";
import { getDefaultConfig } from "@rainbow-me/rainbowkit";
import { http } from "wagmi";
import { hardhat, mainnet, sepolia } from "wagmi/chains";
import { site } from "./site";

// "localhost" is only for automated local testing against a private Hardhat chain.
export const activeChain = site.chain === "mainnet" ? mainnet : site.chain === "localhost" ? hardhat : sepolia;

export const wagmiConfig = getDefaultConfig({
  appName: "NFTs Alive Again",
  // A WalletConnect project id is required for mobile wallets (free at cloud.reown.com).
  projectId: process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID || "MISSING_WALLETCONNECT_PROJECT_ID",
  chains: [activeChain],
  transports: { [activeChain.id]: http(process.env.NEXT_PUBLIC_RPC_URL || undefined) } as never,
  ssr: true,
});
