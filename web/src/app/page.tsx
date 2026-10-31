import Link from "next/link";
import Countdown from "@/components/Countdown";
import OddityArt from "@/components/OddityArt";
import Section from "@/components/Section";
import StatusBadge from "@/components/StatusBadge";
import TierBadge from "@/components/TierBadge";
import SocialLinks from "@/components/SocialLinks";
import { getRoadmap, getSettings, giveawayTotals } from "@/lib/content";
import { collection, label } from "@/lib/collection";
import { site, tiers } from "@/lib/site";
import { contractReady } from "@/lib/contract";

export const dynamic = "force-dynamic";

export default async function Home() {
  const [roadmap, settings, gw] = await Promise.all([getRoadmap(), getSettings(), giveawayTotals()]);
  const showcase = ["Legendary", "Epic", "Rare", "Uncommon", "Common"].map((t) => collection().tokens.find((x) => x.tier === t)!);
  const phases = [1, 2, 3, 4].map((p) => ({ p, items: roadmap.filter((r) => r.phase === p) }));
  const names = ["The Revival", "The Community", "The Oddities Universe", "What Comes Next"];
  return (
    <>
      <section className="bg-night text-cream border-b-4 border-ink overflow-hidden">
        <div className="mx-auto max-w-7xl px-4 py-14 lg:py-20 grid lg:grid-cols-2 gap-10 items-center">
          <div>
            <p className="font-hand text-3xl text-butter wobble inline-block">{site.message}</p>
            <h1 className="font-display font-black text-6xl sm:text-7xl leading-[0.95] mt-2">
              Little<br /><span className="text-pink">Odd</span><span className="text-mint">ities</span>
            </h1>
            <p className="font-hand text-3xl mt-3">{site.slogan}</p>
            <p className="mt-4 text-cream/80 max-w-lg text-lg">
              10,000 original, wonderfully weird characters from one strange little universe — the first collection from {site.brand}.
              Collecting should be fun again. Community should matter. This is where it starts.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/mint" className="btn bg-tomato text-white text-lg">Mint</Link>
              <Link href="/collection" className="btn bg-butter text-ink text-lg">Explore the collection</Link>
              <Link href="/roadmap" className="btn bg-cream text-ink text-lg">Roadmap</Link>
            </div>
            <div className="mt-10 text-ink"><Countdown /></div>
          </div>
          <div className="grid grid-cols-3 gap-3 rotate-1">
            {showcase.map((t, i) => (
              <Link key={t.id} href={`/collection/${t.id}`} className={`card overflow-hidden text-ink ${i === 0 ? "col-span-2 row-span-2" : ""}`}>
                <OddityArt character={t.character} species={t.traits.Species} tier={t.tier} />
                <div className="p-2 flex items-center justify-between gap-2 text-sm"><span className="font-bold truncate">{label(t.id)}</span><TierBadge tier={t.tier} /></div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 -mt-8 relative z-10">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[["Total supply", "10,000"], ["Mint price", `${site.mintPriceEth} ETH`], ["Per transaction", "Max 4"],
            ["Mint status", contractReady ? "See mint page" : "Not open yet"]].map(([k, v]) => (
            <div key={k} className="card p-4"><div className="text-xs font-bold uppercase opacity-60">{k}</div><div className="font-display font-black text-2xl">{v}</div></div>
          ))}
        </div>
        <p className="text-sm opacity-70 mt-2">{settings.mint_status_note} Ethereum gas fees are extra.</p>
      </section>

      <Section kicker="Same world. Different stories." title="Rarity tiers">
        <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {tiers.map((t) => (
            <div key={t.name} className="card p-4" style={{ background: `color-mix(in srgb, ${t.color} 18%, white)` }}>
              <div className="flex justify-between items-center"><TierBadge tier={t.name} /><span className="font-bold">{t.pct}%</span></div>
              <div className="font-display font-black text-3xl mt-3">{t.count.toLocaleString()}</div>
              <p className="text-sm mt-1">{t.blurb}</p>
            </div>
          ))}
        </div>
      </Section>

      <Section kicker="For the community" title="500 Oddities reserved for giveaways">
        <div className="card p-6 grid md:grid-cols-3 gap-6 items-center">
          <p className="md:col-span-2 text-lg">
            500 of the 10,000 Little Oddities are set aside — not extra, part of the 10,000 — for community giveaways, contests,
            holder rewards and special events. Every distribution is recorded publicly with the winner&apos;s wallet and the
            on-chain transaction, so anyone can check it.
          </p>
          <div className="text-center">
            <div className="font-display font-black text-5xl">{gw.distributed} <span className="text-2xl opacity-50">/ 500</span></div>
            <p className="text-sm">given away so far (recorded on-chain)</p>
            <Link href="/community#giveaways" className="btn bg-butter mt-3">Giveaway records</Link>
          </div>
        </div>
      </Section>

      <Section kicker="Honest progress, always" title="Roadmap preview">
        <div className="grid md:grid-cols-4 gap-3">
          {phases.map(({ p, items }) => (
            <div key={p} className="card p-4">
              <p className="text-xs font-bold uppercase opacity-60">Phase {p}</p>
              <h3 className="font-display font-black text-xl">{names[p - 1]}</h3>
              <ul className="mt-3 grid gap-2 text-sm">
                {items.slice(0, 4).map((i) => (<li key={i.id} className="flex justify-between gap-2"><span>{i.title}</span><StatusBadge status={i.status} /></li>))}
              </ul>
            </div>
          ))}
        </div>
        <Link href="/roadmap" className="btn bg-cream mt-6">See the full roadmap</Link>
      </Section>

      <Section kicker="Join the movement" title="Community">
        <div className="card p-6 flex flex-wrap gap-6 items-center justify-between">
          <p className="max-w-xl">{settings.welcome_message}</p>
          <div className="flex flex-col gap-3"><Link href="/community" className="btn bg-mint">Visit the community</Link><SocialLinks /></div>
        </div>
      </Section>
    </>
  );
}
