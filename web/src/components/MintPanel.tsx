"use client";
import { useEffect, useMemo, useState } from "react";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { formatEther, parseEventLogs } from "viem";
import { useAccount, useChainId, useReadContracts, useSwitchChain, useWaitForTransactionReceipt, useWriteContract } from "wagmi";
import { activeChain } from "@/lib/chain";
import { contractAddress, oddityAbi } from "@/lib/contract";
import { explorer, openseaItem, site } from "@/lib/site";

type AllowEntry = { allocation: number; proof: `0x${string}`[] };

function friendlyError(e: unknown): string {
  const m = (e as { shortMessage?: string; message?: string })?.shortMessage || (e as Error)?.message || String(e);
  if (/User rejected|denied/i.test(m)) return "You cancelled the transaction in your wallet. Nothing was charged.";
  if (/insufficient funds/i.test(m)) return "Your wallet doesn't have enough ETH for the mint price plus gas.";
  for (const [err, text] of [
    ["SaleNotActive", "Minting is not open right now."],
    ["ExceedsWalletLimit", "This would go over the lifetime mint limit for your wallet."],
    ["ExceedsAllowlistAllocation", "This would go over your allowlist allocation."],
    ["InvalidProof", "This wallet isn't on the allowlist."],
    ["ExceedsSupply", "Not enough NFTs left for that quantity."],
    ["WrongPayment", "The payment amount didn't match the price. Please refresh and try again."],
    ["InvalidQuantity", "You can mint 1 to 4 per transaction."],
  ]) if (m.includes(err)) return text;
  return m.split("\n")[0];
}

export default function MintPanel() {
  const { address, isConnected } = useAccount();
  const chainId = useChainId();
  const { switchChain } = useSwitchChain();
  const wrongNetwork = isConnected && chainId !== activeChain.id;
  const [qty, setQty] = useState(1);
  const [allow, setAllow] = useState<Record<string, AllowEntry> | null>(null);

  useEffect(() => {
    fetch("/allowlist.json").then((r) => (r.ok ? r.json() : null)).then((d) => setAllow(d?.entries || {})).catch(() => setAllow({}));
  }, []);
  const entry = address && allow ? allow[address.toLowerCase()] : undefined;

  const c = { address: contractAddress as `0x${string}`, abi: oddityAbi } as const;
  const reads = useReadContracts({
    contracts: [
      { ...c, functionName: "mintPrice" }, { ...c, functionName: "totalSupply" }, { ...c, functionName: "remainingPaidSupply" },
      { ...c, functionName: "publicActive" }, { ...c, functionName: "allowlistActive" }, { ...c, functionName: "walletLimit" },
      { ...c, functionName: "mintedBy", args: [address ?? "0x0000000000000000000000000000000000000000"] },
      { ...c, functionName: "allowlistMintedBy", args: [address ?? "0x0000000000000000000000000000000000000000"] },
    ],
    query: { enabled: Boolean(contractAddress), refetchInterval: 15000 },
  });
  const v = reads.data?.map((r) => r.result);
  const [price, supply, remaining, publicActive, allowlistActive, walletLimit, minted, alMinted] =
    (v || []) as [bigint?, bigint?, bigint?, boolean?, boolean?, bigint?, bigint?, bigint?];

  const useAllowlist = Boolean(allowlistActive && entry);
  const walletLeft = walletLimit !== undefined && minted !== undefined ? Number(walletLimit - minted) : 4;
  const allowLeft = entry && alMinted !== undefined ? entry.allocation - Number(alMinted) : 4;
  const maxQty = Math.max(0, Math.min(4, walletLeft, useAllowlist ? allowLeft : 4, remaining !== undefined ? Number(remaining) : 4));
  useEffect(() => { if (qty > Math.max(1, maxQty)) setQty(Math.max(1, maxQty)); }, [maxQty, qty]);

  const total = price !== undefined ? price * BigInt(qty) : undefined;
  const saleOpen = Boolean(publicActive || useAllowlist);

  const { writeContractAsync, data: hash, isPending, reset } = useWriteContract();
  const receipt = useWaitForTransactionReceipt({ hash });
  const [error, setError] = useState("");

  const mintedIds = useMemo(() => {
    if (!receipt.data) return [];
    const logs = parseEventLogs({ abi: oddityAbi, logs: receipt.data.logs, eventName: "Minted" }) as unknown as { args: { firstTokenId: bigint; quantity: bigint } }[];
    return logs.flatMap((l) => Array.from({ length: Number(l.args.quantity) }, (_, i) => Number(l.args.firstTokenId) + i));
  }, [receipt.data]);

  async function mint() {
    setError("");
    try {
      if (total === undefined) throw new Error("Price not loaded yet");
      if (useAllowlist && entry) {
        await writeContractAsync({ ...c, functionName: "allowlistMint", args: [BigInt(qty), BigInt(entry.allocation), entry.proof], value: total });
      } else {
        await writeContractAsync({ ...c, functionName: "publicMint", args: [BigInt(qty)], value: total });
      }
    } catch (e) {
      setError(friendlyError(e));
    }
  }

  if (!contractAddress) {
    return (
      <div className="card p-6">
        <h3 className="font-display font-black text-2xl">Minting isn&apos;t open yet</h3>
        <p className="mt-2">The Little Oddities contract has not been deployed. Target launch: <strong>November 1, 2027</strong>.</p>
        <PriceTable />
      </div>
    );
  }

  if (receipt.isSuccess) {
    return (
      <div className="card p-6 bg-mint/40">
        <p className="font-hand text-3xl">Welcome to the weird!</p>
        <h3 className="font-display font-black text-3xl">You minted {mintedIds.length} Little {mintedIds.length === 1 ? "Oddity" : "Oddities"}</h3>
        <ul className="mt-4 grid gap-2">
          {mintedIds.map((id) => (
            <li key={id} className="flex flex-wrap gap-3 items-center">
              <a className="font-bold underline" href={`/collection/${id}`}>#{id}</a>
              {openseaItem(id) && <a className="underline text-sm" href={openseaItem(id)} target="_blank" rel="noopener noreferrer">View on OpenSea (may take a few minutes to appear)</a>}
            </li>
          ))}
        </ul>
        <a className="mt-4 inline-block underline text-sm" href={`${explorer}/tx/${hash}`} target="_blank" rel="noopener noreferrer">View transaction on Etherscan</a>
        <div className="mt-6"><button className="btn bg-butter" onClick={() => { reset(); setQty(1); }}>Mint again</button></div>
      </div>
    );
  }

  return (
    <div className="card p-6">
      <div className="grid sm:grid-cols-3 gap-3 text-center">
        <Stat label="Minted" value={supply !== undefined ? `${supply.toLocaleString()} / ${site.totalSupply.toLocaleString()}` : "…"} />
        <Stat label="Left for mint" value={remaining !== undefined ? remaining.toLocaleString() : "…"} />
        <Stat label="Price each" value={price !== undefined ? `${formatEther(price)} ETH` : "…"} />
      </div>

      <div className="mt-5 flex flex-wrap gap-2 text-sm">
        <Pill on={Boolean(allowlistActive)}>Allowlist {allowlistActive ? "open" : "closed"}</Pill>
        <Pill on={Boolean(publicActive)}>Public {publicActive ? "open" : "closed"}</Pill>
      </div>

      {!isConnected ? (
        <div className="mt-6"><ConnectButton label="Connect wallet to mint" /></div>
      ) : wrongNetwork ? (
        <div className="mt-6">
          <p className="font-bold">Your wallet is on the wrong network.</p>
          <button className="btn bg-butter mt-3" onClick={() => switchChain({ chainId: activeChain.id })}>Switch to {activeChain.name}</button>
        </div>
      ) : (
        <>
          <div className="mt-6 rounded-xl border-2 border-ink p-4 bg-cream">
            <p className="font-bold">Allowlist check</p>
            <p className="text-sm mt-1">
              {allow === null ? "Checking…" : entry ? `This wallet is on the allowlist (up to ${entry.allocation} allowlist mints${alMinted !== undefined ? `, ${Number(alMinted)} used` : ""}).` : "This wallet is not on the allowlist."}
            </p>
            {walletLimit !== undefined && minted !== undefined && (
              <p className="text-sm mt-1">Lifetime mints from this wallet: <strong>{Number(minted)} / {Number(walletLimit)}</strong></p>
            )}
          </div>

          <div className="mt-6 flex items-center gap-4">
            <span className="font-bold">Quantity</span>
            <div className="flex items-center gap-2" role="group" aria-label="Quantity">
              <button className="btn bg-white px-4 py-1" onClick={() => setQty(Math.max(1, qty - 1))} disabled={qty <= 1} aria-label="Fewer">−</button>
              <span className="font-display font-black text-3xl w-10 text-center tabular-nums">{qty}</span>
              <button className="btn bg-white px-4 py-1" onClick={() => setQty(Math.min(maxQty, qty + 1))} disabled={qty >= maxQty} aria-label="More">+</button>
            </div>
            <span className="text-sm opacity-60">max 4 per transaction</span>
          </div>

          <div className="mt-6 rounded-xl bg-night text-cream p-4">
            <div className="flex justify-between"><span>{qty} × {price !== undefined ? formatEther(price) : "…"} ETH</span>
              <span className="font-display font-black text-2xl">{total !== undefined ? `${formatEther(total)} ETH` : "…"}</span></div>
            <p className="text-xs text-cream/70 mt-1">Plus an Ethereum network (gas) fee shown by your wallet before you confirm. Gas goes to the network, not to us.</p>
          </div>

          <button className="btn bg-tomato text-white w-full mt-6 text-lg" onClick={mint}
            disabled={!saleOpen || maxQty === 0 || isPending || receipt.isLoading || total === undefined}>
            {isPending ? "Confirm in your wallet…" : receipt.isLoading ? "Minting… waiting for the network" :
              !saleOpen ? "Minting is closed" : maxQty === 0 ? "Limit reached" : `Mint ${qty} for ${total !== undefined ? formatEther(total) : "…"} ETH`}
          </button>
          {hash && receipt.isLoading && (
            <p className="text-sm mt-2">Transaction sent. <a className="underline" href={`${explorer}/tx/${hash}`} target="_blank" rel="noopener noreferrer">Track it on Etherscan</a></p>
          )}
          {(error || receipt.isError) && <p className="mt-3 rounded-lg bg-tomato/15 border-2 border-tomato p-3 text-sm" role="alert">{error || "The transaction failed on-chain. Nothing was minted; check Etherscan for details."}</p>}
        </>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (<div className="rounded-xl border-2 border-ink p-3 bg-cream"><div className="text-xs font-bold uppercase opacity-60">{label}</div><div className="font-display font-black text-xl">{value}</div></div>);
}
function Pill({ on, children }: { on: boolean; children: React.ReactNode }) {
  return <span className={`px-3 py-1 rounded-full border-2 border-ink font-bold ${on ? "bg-mint" : "bg-white opacity-70"}`}>{children}</span>;
}
export function PriceTable() {
  return (
    <table className="mt-4 w-full text-left border-2 border-ink rounded-xl overflow-hidden">
      <thead className="bg-night text-cream"><tr><th className="p-2">Quantity</th><th className="p-2">Total price</th></tr></thead>
      <tbody>{[1, 2, 3, 4].map((n) => (<tr key={n} className="odd:bg-cream"><td className="p-2">{n} NFT{n > 1 ? "s" : ""}</td><td className="p-2 font-bold">{(0.005 * n).toFixed(3)} ETH + gas</td></tr>))}</tbody>
    </table>
  );
}
