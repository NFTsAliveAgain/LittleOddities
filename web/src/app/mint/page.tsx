import MintPanel, { PriceTable } from "@/components/MintPanel";
import { site } from "@/lib/site";

export const metadata = { title: "Mint" };

export default function MintPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-10 grid lg:grid-cols-[1fr_380px] gap-8">
      <div>
        <p className="font-hand text-2xl text-tomato">Bring one home</p>
        <h1 className="font-display font-black text-5xl">Mint a Little Oddity</h1>
        <div className="mt-6"><MintPanel /></div>
      </div>
      <aside className="grid gap-4 content-start">
        <div className="card p-5">
          <h2 className="font-display font-black text-xl">How minting works</h2>
          <ol className="mt-2 list-decimal pl-5 text-sm grid gap-1">
            <li>Connect your wallet (MetaMask, Rainbow, Coinbase Wallet, WalletConnect…).</li>
            <li>Make sure you&apos;re on {site.chain === "mainnet" ? "Ethereum" : "the Sepolia test network"}.</li>
            <li>Pick 1–4. The exact total is shown before you confirm.</li>
            <li>Confirm in your wallet. Your wallet shows the gas fee too.</li>
            <li>Your Oddities are revealed instantly — no waiting.</li>
          </ol>
        </div>
        <div className="card p-5">
          <h2 className="font-display font-black text-xl">Price</h2>
          <PriceTable />
          <p className="text-xs mt-3 opacity-70">Price, the 4-per-transaction limit, your wallet&apos;s lifetime limit and the allowlist are all enforced by the smart contract itself — not just this website.</p>
        </div>
        <div className="card p-5 text-sm">
          <h2 className="font-display font-black text-xl">Please remember</h2>
          <p className="mt-2">NFTs are collectibles, not investments. We will never DM you first, never ask for your seed phrase, and the only official mint is on this website.</p>
        </div>
      </aside>
    </div>
  );
}
