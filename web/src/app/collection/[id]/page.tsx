import Link from "next/link";
import { notFound } from "next/navigation";
import OddityArt from "@/components/OddityArt";
import TierBadge from "@/components/TierBadge";
import { collection, isRevealed, label, token } from "@/lib/collection";
import { openseaItem, site } from "@/lib/site";

type P = Promise<{ id: string }>;
export async function generateMetadata({ params }: { params: P }) {
  const t = token(Number((await params).id));
  return { title: t ? `${label(t.id)} ${t.name}` : "Not found" };
}

export default async function TokenPage({ params }: { params: P }) {
  const id = Number((await params).id);
  const t = token(id);
  if (!t) notFound();
  const { stats } = collection();
  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <Link href="/collection" className="text-sm underline">← Back to collection</Link>
      <div className="mt-4 grid md:grid-cols-2 gap-8">
        <div className="card overflow-hidden"><OddityArt character={t.character} species={t.traits.Species} tier={t.tier} /></div>
        <div>
          <p className="font-bold opacity-60">{isRevealed() ? `Little Oddities #${t.id} · character ${t.character}` : `Planned character ${t.id} · token number decided at reveal`}</p>
          <h1 className="font-display font-black text-5xl">{t.name}</h1>
          <div className="mt-3"><TierBadge tier={t.tier} /></div>
          <table className="mt-6 w-full card overflow-hidden">
            <tbody>
              {Object.entries(t.traits).map(([k, v]) => {
                const s = stats[k]?.[v];
                return (
                  <tr key={k} className="border-b-2 border-ink/10 last:border-0">
                    <td className="p-3 text-sm opacity-60">{k}</td>
                    <td className="p-3 font-bold"><Link className="hover:underline" href={`/collection?trait=${encodeURIComponent(`${k}:${v}`)}`}>{v}</Link></td>
                    <td className="p-3 text-sm text-right tabular-nums">{s ? `${s.count.toLocaleString()} have this (${(s.count / 100).toFixed(1)}%)` : ""}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <div className="mt-6 flex flex-wrap gap-3">
            {isRevealed() && openseaItem(t.id) && <a className="btn bg-sky" href={openseaItem(t.id)} target="_blank" rel="noopener noreferrer">View on OpenSea</a>}
            <Link className="btn bg-butter" href="/mint">Mint</Link>
          </div>
          {!site.imagesBase && <p className="mt-4 text-sm opacity-70">Artwork in progress — the final image will appear here once the art is complete and uploaded.</p>}
        </div>
      </div>
      <div className="mt-8 flex justify-between">
        {id > 1 ? <Link className="btn bg-white" href={`/collection/${id - 1}`}>← {label(id - 1)}</Link> : <span />}
        {id < 10000 && <Link className="btn bg-white" href={`/collection/${id + 1}`}>{label(id + 1)} →</Link>}
      </div>
    </div>
  );
}
