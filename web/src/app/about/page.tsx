import Link from "next/link";
export const metadata = { title: "About" };

export default function About() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <p className="font-hand text-3xl text-tomato">Bringing NFTs Alive Again</p>
      <h1 className="font-display font-black text-5xl">Why we&apos;re here</h1>
      <div className="mt-8 grid gap-5 text-lg leading-relaxed">
        <p>Remember when collecting was <em>fun</em>? When you&apos;d stay up for a drop because the art made you smile, not because of a chart?
          When a community felt like a group of friends who all liked the same weird thing?</p>
        <p><strong>NFTs Alive Again</strong> exists to bring that feeling back. Not with promises or hype — with characters worth caring about,
          a community that actually gets a say, and a project that shows its work in the open.</p>
        <p><strong>Little Oddities</strong> is where it starts: 10,000 original characters from one wonderfully weird universe. Fuzzy ones, slimy ones,
          a few mushrooms, the occasional ghost. Each one is a little different. All of them belong.</p>
        <h2 className="font-display font-black text-3xl mt-4">What we believe</h2>
        <ul className="grid gap-2 list-none">
          {["NFTs should be fun again.", "Collecting should feel exciting.", "Community should matter — and holders should have a voice.",
            "The journey should be transparent, including when things change or take longer.", "The project should grow with its community."].map((t) => (
            <li key={t} className="card p-4 font-bold">{t}</li>))}
        </ul>
        <h2 className="font-display font-black text-3xl mt-4">How we&apos;ll keep it honest</h2>
        <p>Our roadmap shows the real status of every item. Giveaways are recorded with on-chain proof. The smart contract&apos;s rules — price,
          limits, the 500 reserved NFTs — are public and enforced by code. And we&apos;ll never promise you profits: Little Oddities are collectibles,
          made to be enjoyed.</p>
        <div className="flex flex-wrap gap-3 mt-4"><Link href="/roadmap" className="btn bg-butter">Read the roadmap</Link><Link href="/community" className="btn bg-mint">Join the community</Link></div>
      </div>
    </div>
  );
}
