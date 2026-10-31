import { site } from "@/lib/site";
export const metadata = { title: "FAQ" };

const FAQ: [string, string][] = [
  ["What is NFTs Alive Again?", "NFTs Alive Again is a creative brand and community on a mission to make NFTs fun again — with original art, transparent progress and a community that has a real voice."],
  ["What are Little Oddities?", "Little Oddities is the first NFT collection from NFTs Alive Again: 10,000 original, wonderfully weird cartoon characters. Each has its own combination of species, colors, outfits and quirks."],
  ["How many NFTs exist?", "Exactly 10,000 — no more can ever be created. The limit is written into the smart contract. 500 of the 10,000 are reserved for community giveaways."],
  ["How much does minting cost?", "0.005 ETH per NFT (2 = 0.010, 3 = 0.015, 4 = 0.020 ETH). Ethereum network (gas) fees are extra and go to the network, not to us. Your wallet shows the gas fee before you confirm."],
  ["What is the 4 NFT transaction limit?", "You can mint up to 4 Oddities in a single transaction. The smart contract enforces this. There is also a separate lifetime limit per wallet (set before launch and shown on the mint page) to keep distribution fair."],
  ["What is the allowlist?", "The allowlist is a list of wallets that can mint during an early allowlist window. The contract checks eligibility itself using a cryptographic proof, so only listed wallets can use it. Allowlist criteria will be announced in our official channels — be wary of anyone selling 'allowlist spots'."],
  ["What are the 500 reserved NFTs?", "500 of the 10,000 Oddities are minted once to the project's owner wallet and used only for community giveaways, contests, holder rewards and special events. They are part of the 10,000, not extra."],
  ["How do giveaways work?", "Giveaways are announced on the Community page and our official channels with their rules. Winners are recorded publicly with their wallet and the on-chain transaction that delivered the NFT, so anyone can verify it."],
  ["Which blockchain is used?", "Ethereum. Testing happens first on the Sepolia test network; the public collection will be on Ethereum mainnet."],
  ["How do I view my NFT on OpenSea?", "After minting, the success screen links to your Oddity on OpenSea. You can also visit OpenSea, connect the same wallet and look under your profile. It can take a few minutes for new mints to appear."],
  ["What is the roadmap?", "The roadmap lists what we're working on and plan to explore, with an honest status for each item: Planned, In progress or Completed. Later phases are intentions, not guarantees, and will be shaped by community feedback."],
  ["What happens after minting?", "Your Oddity arrives in your wallet straight away as a mystery Oddity. Every token is revealed together after the mint. Holders can take part in polls, character voting, contests and holder-only announcements."],
  ["How does the reveal work — and why is it fair?", "Before minting starts we publish a 'provenance hash': a fingerprint of all 10,000 images in their planned order, locked into the smart contract. After the mint, the contract picks a random starting point from a future Ethereum block, which nobody (not even the team) can predict or choose. That decides which character each token number becomes. Anyone can re-check the fingerprint and the starting point afterwards, so no one can grab the rare ones early or swap art later."],
  ["Is this an investment?", "No. Little Oddities are digital collectibles. We make no promises about price, value or returns. Please only spend what you're comfortable spending on a collectible."],
  ["Do I own the copyright to my Oddity's art?", "Buying an NFT does not transfer copyright. You get the rights described in our NFT holder license — read it on the License page."],
];

export default function FaqPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <p className="font-hand text-2xl text-tomato">Good questions</p>
      <h1 className="font-display font-black text-5xl">FAQ</h1>
      <div className="mt-8 grid gap-3">
        {FAQ.map(([q, a]) => (
          <details key={q} className="card p-5 group">
            <summary className="font-display font-black text-xl cursor-pointer list-none flex justify-between gap-4">{q}<span className="group-open:rotate-45 transition">+</span></summary>
            <p className="mt-3 leading-relaxed">{a}</p>
          </details>
        ))}
      </div>
      <p className="mt-8 text-sm opacity-70">Official launch target: November 3, 2027 ({site.launchTz}). Dates may change if anything isn&apos;t ready — we&apos;ll always say so publicly.</p>
    </div>
  );
}
