import Link from "next/link";
import OddityArt from "@/components/OddityArt";
import TierBadge from "@/components/TierBadge";
import { collection, search } from "@/lib/collection";
import { tiers, site } from "@/lib/site";

export const metadata = { title: "Collection" };
type SP = Promise<Record<string, string | undefined>>;

export default async function CollectionPage({ searchParams }: { searchParams: SP }) {
  const sp = await searchParams;
  const res = search({ q: sp.q, tier: sp.tier, trait: sp.trait, sort: sp.sort, page: Number(sp.page || 1) });
  const { stats } = collection();
  const link = (patch: Record<string, string | undefined>) => {
    const merged: Record<string, string | undefined> = { ...sp, page: undefined, ...patch };
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries(merged)) if (v) p.set(k, v);
    return `/collection?${p}`;
  };
  return (
    <div className="mx-auto max-w-7xl px-4 py-10">
      <p className="font-hand text-2xl text-tomato">10,000 wonderfully weird</p>
      <h1 className="font-display font-black text-5xl">The Collection</h1>
      {!site.imagesBase && (
        <p className="mt-4 card p-4 bg-butter/40 text-sm">
          <strong>Artwork in progress.</strong> The final hand-drawn artwork is being created. Names, rarities and traits below come from the
          collection plan and are shown so you can explore; images appear once the art is finished and uploaded.
        </p>
      )}

      <form className="mt-6 flex flex-wrap gap-2" action="/collection">
        <input name="q" defaultValue={sp.q} placeholder="Search by #ID, name or trait…" className="input max-w-sm" />
        {sp.tier && <input type="hidden" name="tier" value={sp.tier} />}
        {sp.trait && <input type="hidden" name="trait" value={sp.trait} />}
        <select name="sort" defaultValue={sp.sort || "id"} className="input max-w-44">
          <option value="id">Token ID ↑</option><option value="id-desc">Token ID ↓</option>
          <option value="rarity">Rarest first</option><option value="name">Name A–Z</option>
        </select>
        <button className="btn bg-butter">Search</button>
        {(sp.q || sp.tier || sp.trait) && <Link href="/collection" className="btn bg-white">Clear</Link>}
      </form>

      <div className="mt-4 flex flex-wrap gap-2">
        {tiers.map((t) => (
          <Link key={t.name} href={link({ tier: sp.tier === t.name ? undefined : t.name })}
            className={`px-3 py-1 rounded-full border-2 border-ink text-sm font-bold ${sp.tier === t.name ? "bg-ink text-cream" : "bg-white"}`}>
            {t.name} · {t.count.toLocaleString()}
          </Link>
        ))}
        {sp.trait && <span className="px-3 py-1 rounded-full border-2 border-ink text-sm font-bold bg-lilac">{sp.trait.replace(":", ": ")}</span>}
      </div>

      <div className="mt-8 grid lg:grid-cols-[260px_1fr] gap-8">
        <aside className="card p-4 h-fit max-h-[75vh] overflow-auto">
          <h2 className="font-display font-black text-xl">Traits</h2>
          {Object.entries(stats).map(([cat, vals]) => (
            <details key={cat} className="mt-2">
              <summary className="font-bold cursor-pointer">{cat} <span className="opacity-50 font-normal">({Object.keys(vals).length})</span></summary>
              <ul className="mt-1 text-sm grid gap-0.5">
                {Object.entries(vals).sort((a, b) => b[1].count - a[1].count).map(([name, s]) => (
                  <li key={name}><Link href={link({ trait: `${cat}:${name}` })} className="flex justify-between hover:underline">
                    <span>{name}</span><span className="opacity-60 tabular-nums">{s.count} · {(s.count / 100).toFixed(1)}%</span></Link></li>
                ))}
              </ul>
            </details>
          ))}
        </aside>
        <div>
          <p className="text-sm opacity-70">{res.total.toLocaleString()} results</p>
          <div className="mt-3 grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-4 gap-4">
            {res.items.map((t) => (
              <Link key={t.id} href={`/collection/${t.id}`} className="card overflow-hidden hover:-translate-y-1 transition">
                <OddityArt id={t.id} species={t.traits.Species} tier={t.tier} />
                <div className="p-3 border-t-3 border-ink">
                  <div className="flex justify-between items-center gap-2"><span className="font-bold">#{t.id}</span><TierBadge tier={t.tier} /></div>
                  <div className="text-sm truncate mt-1">{t.name}</div>
                </div>
              </Link>
            ))}
          </div>
          <nav className="mt-8 flex gap-2 items-center justify-center" aria-label="Pages">
            {res.page > 1 && <Link className="btn bg-white" href={`${link({})}&page=${res.page - 1}`}>← Prev</Link>}
            <span className="font-bold">Page {res.page} of {res.pages}</span>
            {res.page < res.pages && <Link className="btn bg-white" href={`${link({})}&page=${res.page + 1}`}>Next →</Link>}
          </nav>
        </div>
      </div>
    </div>
  );
}
