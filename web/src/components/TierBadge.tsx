const C: Record<string, string> = { Common: "bg-common", Uncommon: "bg-uncommon", Rare: "bg-rare", Epic: "bg-epic", Legendary: "bg-legendary" };
export default function TierBadge({ tier }: { tier: string }) {
  return <span className={`${C[tier] || "bg-common"} text-white text-xs font-bold px-2.5 py-1 rounded-full border-2 border-ink`}>{tier}</span>;
}
