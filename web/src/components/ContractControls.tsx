"use client";
import { useState } from "react";
import { formatEther, parseEther } from "viem";
import { useAccount, useReadContracts, useWriteContract } from "wagmi";
import { contractAddress, oddityAbi } from "@/lib/contract";
import { explorer } from "@/lib/site";

// On-chain owner actions. These are real transactions signed by the OWNER wallet; each asks for confirmation first.
export default function ContractControls() {
  const { address } = useAccount();
  const c = { address: contractAddress as `0x${string}`, abi: oddityAbi } as const;
  const { data, refetch } = useReadContracts({ contracts: ["owner", "mintPrice", "walletLimit", "publicActive", "allowlistActive", "merkleRoot", "reserveMinted", "totalSupply", "metadataFrozen"]
    .map((f) => ({ ...c, functionName: f })), query: { enabled: Boolean(contractAddress) } });
  const [owner, price, limit, pub, al, root, reserved, supply, frozen] = (data || []).map((d) => d.result) as [string, bigint, bigint, boolean, boolean, string, boolean, bigint, boolean];
  const { writeContractAsync } = useWriteContract();
  const [msg, setMsg] = useState("");
  const [inputs, setInputs] = useState({ price: "", limit: "", root: "" });

  if (!contractAddress) return <p className="card p-5">No contract configured yet. After deploying to Sepolia, set NEXT_PUBLIC_CONTRACT_ADDRESS (see docs/DEPLOYMENT_GUIDE.md).</p>;
  const isOwner = owner && address && owner.toLowerCase() === address.toLowerCase();

  async function act(label: string, functionName: string, args: unknown[] = []) {
    if (!confirm(`${label}\n\nThis sends a real transaction from your owner wallet and costs gas. Continue?`)) return;
    setMsg("Confirm in your wallet…");
    try {
      const hash = await writeContractAsync({ ...c, functionName, args });
      setMsg(`Sent: ${explorer}/tx/${hash}`);
      setTimeout(() => refetch(), 15000);
    } catch (e) { setMsg((e as { shortMessage?: string }).shortMessage || String(e)); }
  }

  return (
    <div className="grid gap-4">
      {!isOwner && <p className="card p-4 bg-tomato/15">The connected wallet is not the contract owner ({owner}). On-chain actions will fail.</p>}
      <div className="card p-5 grid sm:grid-cols-3 gap-3 text-sm">
        <div>Price: <b>{price !== undefined ? formatEther(price) : "…"} ETH</b></div>
        <div>Wallet limit: <b>{limit?.toString()}</b></div>
        <div>Minted: <b>{supply?.toString()}</b></div>
        <div>Public mint: <b>{pub ? "OPEN" : "closed"}</b></div>
        <div>Allowlist mint: <b>{al ? "OPEN" : "closed"}</b></div>
        <div>Reserve (500) minted: <b>{reserved ? "yes" : "no"}</b></div>
        <div className="sm:col-span-3 break-all">Merkle root: <b>{root}</b></div>
        <div>Metadata frozen: <b>{frozen ? "yes" : "no"}</b></div>
      </div>
      <div className="card p-5 grid gap-3">
        <div className="flex flex-wrap gap-2">
          <button className="btn bg-mint" onClick={() => act(`${al ? "CLOSE" : "OPEN"} allowlist minting`, "setAllowlistActive", [!al])}>{al ? "Close" : "Open"} allowlist mint</button>
          <button className="btn bg-mint" onClick={() => act(`${pub ? "CLOSE" : "OPEN"} PUBLIC minting`, "setPublicActive", [!pub])}>{pub ? "Close" : "Open"} public mint</button>
          {!reserved && <button className="btn bg-butter" onClick={() => act("Mint the 500 reserved giveaway NFTs to the owner wallet (one time only, large gas cost)", "mintReserve")}>Mint 500 reserve</button>}
          <button className="btn bg-white" onClick={() => act("Withdraw all mint proceeds to the owner wallet", "withdraw")}>Withdraw funds</button>
        </div>
        <div className="flex flex-wrap gap-2 items-end">
          <label className="text-sm font-bold">New price (ETH)<input className="input mt-1" value={inputs.price} onChange={(e) => setInputs({ ...inputs, price: e.target.value })} placeholder="0.005" /></label>
          <button className="btn bg-white" onClick={() => act(`Change mint price to ${inputs.price} ETH`, "setMintPrice", [parseEther(inputs.price || "0")])} disabled={!inputs.price}>Set price</button>
          <label className="text-sm font-bold">Wallet limit<input className="input mt-1" value={inputs.limit} onChange={(e) => setInputs({ ...inputs, limit: e.target.value })} placeholder="10" /></label>
          <button className="btn bg-white" onClick={() => act(`Change lifetime wallet limit to ${inputs.limit}`, "setWalletLimit", [BigInt(inputs.limit || "0")])} disabled={!inputs.limit}>Set limit</button>
        </div>
        <div className="flex flex-wrap gap-2 items-end">
          <label className="text-sm font-bold grow">Allowlist Merkle root (from the allowlist tool)<input className="input mt-1" value={inputs.root} onChange={(e) => setInputs({ ...inputs, root: e.target.value })} placeholder="0x…" /></label>
          <button className="btn bg-white" onClick={() => act("Set allowlist Merkle root", "setMerkleRoot", [inputs.root])} disabled={!/^0x[0-9a-fA-F]{64}$/.test(inputs.root)}>Set root</button>
        </div>
        {msg && <p className="text-sm break-all" role="status">{msg}</p>}
      </div>
    </div>
  );
}
