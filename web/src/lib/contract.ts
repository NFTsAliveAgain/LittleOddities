import abiJson from "./abi.json";
import { createPublicClient, http, type Abi } from "viem";
import { hardhat, mainnet, sepolia } from "viem/chains";
import { site } from "./site";

export const oddityAbi = abiJson as Abi;
export const contractAddress = site.contractAddress || undefined;
export const contractReady = Boolean(site.contractAddress);

// Server-side reads (holder checks for votes). No keys involved.
export const publicClient = createPublicClient({
  chain: site.chain === "mainnet" ? mainnet : site.chain === "localhost" ? hardhat : sepolia,
  transport: http(process.env.NEXT_PUBLIC_RPC_URL || undefined),
});

export async function holderBalance(address: `0x${string}`): Promise<bigint> {
  if (!contractAddress) return 0n;
  return (await publicClient.readContract({ address: contractAddress, abi: oddityAbi, functionName: "balanceOf", args: [address] })) as bigint;
}
