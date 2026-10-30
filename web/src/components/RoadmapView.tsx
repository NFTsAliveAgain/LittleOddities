"use client";
import { useState } from "react";
import StatusBadge from "./StatusBadge";
import type { RoadmapItem } from "@/lib/content";

const PHASES = [
  { n: 1, name: "The Revival", color: "bg-butter", blurb: "Building the foundations: brand, art, contract, website." },
  { n: 2, name: "The Community", color: "bg-mint", blurb: "Giveaways, contests, polls and a real say for holders." },
  { n: 3, name: "The Oddities Universe", color: "bg-lilac", blurb: "Stories, lore and new creative work." },
  { n: 4, name: "What Comes Next", color: "bg-pink", blurb: "Directions we hope to explore — shaped by the community." },
];

export default function RoadmapView({ items }: { items: RoadmapItem[] }) {
  const [phase, setPhase] = useState<number | null>(null);
  const [status, setStatus] = useState<string>("all");
  const shown = PHASES.filter((p) => phase === null || p.n === phase);
  return (
    <div>
      <div className="flex flex-wrap gap-2">
        <button className={`btn py-1 ${phase === null ? "bg-ink text-cream" : "bg-white"}`} onClick={() => setPhase(null)}>All phases</button>
        {PHASES.map((p) => (
          <button key={p.n} className={`btn py-1 ${phase === p.n ? "bg-ink text-cream" : "bg-white"}`} onClick={() => setPhase(p.n)}>Phase {p.n}</button>
        ))}
        <select className="input max-w-44" value={status} onChange={(e) => setStatus(e.target.value)} aria-label="Filter by status">
          <option value="all">All statuses</option><option value="completed">Completed</option>
          <option value="in_progress">In progress</option><option value="planned">Planned</option>
        </select>
      </div>
      <ol className="mt-8 relative border-l-4 border-ink ml-3 grid gap-10">
        {shown.map((p) => {
          const list = items.filter((i) => i.phase === p.n && (status === "all" || i.status === status));
          const done = items.filter((i) => i.phase === p.n && i.status === "completed").length;
          const total = items.filter((i) => i.phase === p.n).length;
          return (
            <li key={p.n} className="pl-8 relative">
              <span className={`absolute -left-[22px] top-1 w-10 h-10 rounded-full border-4 border-ink ${p.color} grid place-items-center font-display font-black`}>{p.n}</span>
              <h2 className="font-display font-black text-3xl">Phase {p.n} — {p.name}</h2>
              <p className="opacity-70">{p.blurb}</p>
              <div className="mt-2 h-3 max-w-md rounded-full border-2 border-ink bg-white overflow-hidden" aria-label={`${done} of ${total} completed`}>
                <div className="h-full bg-moss" style={{ width: `${total ? (100 * done) / total : 0}%` }} />
              </div>
              <p className="text-xs mt-1 opacity-60">{done} of {total} completed</p>
              <ul className="mt-4 grid sm:grid-cols-2 gap-3">
                {list.map((i) => (
                  <li key={i.id} className="card p-4">
                    <div className="flex justify-between gap-3 items-start"><span className="font-bold">{i.title}</span><StatusBadge status={i.status} /></div>
                    {i.detail && <p className="text-sm mt-2 opacity-80">{i.detail}</p>}
                  </li>
                ))}
                {!list.length && <li className="text-sm opacity-60">No items with this status.</li>}
              </ul>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
