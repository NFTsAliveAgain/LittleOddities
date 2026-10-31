import { site } from "@/lib/site";

const TIER_BG: Record<string, string> = { Common: "#e8ecf3", Uncommon: "#d6f5e4", Rare: "#dbe8ff", Epic: "#eadcff", Legendary: "#fff0c2" };

// Shows the real IPFS image once uploaded (files are named by CHARACTER number). Until then: an honest card.
export default function OddityArt({ character, species, tier, className = "" }: { character: number; species: string; tier: string; className?: string }) {
  if (site.imagesBase) {
    // eslint-disable-next-line @next/next/no-img-element
    return <img src={`${site.imagesBase}${character}.png`} alt={`Little Oddities character ${character}`} loading="lazy" className={`w-full aspect-square object-cover ${className}`} />;
  }
  return (
    <div className={`w-full aspect-square grid place-items-center paper-grain ${className}`} style={{ background: TIER_BG[tier] || "#eee" }}>
      <div className="text-center px-3">
        <div className="font-display font-black text-2xl">{species}</div>
        <div className="text-[11px] font-bold uppercase tracking-wider opacity-60 mt-1">Artwork in progress</div>
      </div>
    </div>
  );
}
