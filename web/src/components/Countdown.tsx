"use client";
import { useEffect, useState } from "react";
import { site } from "@/lib/site";

export default function Countdown() {
  const target = new Date(site.launchIso).getTime();
  const [now, setNow] = useState<number | null>(null);
  useEffect(() => {
    setNow(Date.now());
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, []);
  const left = Math.max(0, target - (now ?? target));
  const parts = [["Days", Math.floor(left / 864e5)], ["Hours", Math.floor(left / 36e5) % 24], ["Min", Math.floor(left / 6e4) % 60], ["Sec", Math.floor(left / 1e3) % 60]];
  const local = new Intl.DateTimeFormat("en-US", { year: "numeric", month: "long", day: "numeric", hour: "numeric", minute: "2-digit", timeZone: site.launchTz, timeZoneName: "short" }).format(target);
  return (
    <div>
      <div className="flex gap-2 sm:gap-3" aria-live="off">
        {parts.map(([label, v]) => (
          <div key={label} className="card px-3 py-2 sm:px-4 text-center min-w-16">
            <div className="font-display font-black text-2xl sm:text-4xl tabular-nums">{now === null ? "–" : String(v).padStart(2, "0")}</div>
            <div className="text-xs font-bold uppercase tracking-wide opacity-60">{label}</div>
          </div>
        ))}
      </div>
      <p className="mt-2 text-sm opacity-70">Target launch: <strong>{local}</strong>{now !== null && left === 0 ? " — launch time reached (minting opens only when announced)" : ""}</p>
    </div>
  );
}
