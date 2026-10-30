"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import Logo from "./Logo";

const NAV = [["Collection", "/collection"], ["Mint", "/mint"], ["Roadmap", "/roadmap"], ["Community", "/community"], ["About", "/about"], ["FAQ", "/faq"]];

export default function Header() {
  const path = usePathname();
  const [open, setOpen] = useState(false);
  return (
    <header className="bg-night text-cream sticky top-0 z-40 border-b-4 border-ink">
      <div className="mx-auto max-w-7xl px-3 sm:px-4 h-16 flex items-center gap-2 sm:gap-4">
        <Link href="/" className="shrink-0" aria-label="NFTs Alive Again home"><Logo small /></Link>
        <nav className="hidden lg:flex gap-1 ml-4">
          {NAV.map(([label, href]) => (
            <Link key={href} href={href}
              className={`px-3 py-1.5 rounded-full font-bold text-sm transition ${path.startsWith(href) ? "bg-butter text-ink" : "hover:bg-white/10"}`}>
              {label}
            </Link>
          ))}
        </nav>
        <div className="ml-auto flex items-center gap-2 min-w-0">
          <ConnectButton chainStatus="icon" showBalance={false} accountStatus={{ smallScreen: "avatar", largeScreen: "address" }} />
          <button className="lg:hidden rounded-lg border-2 border-cream/40 px-3 py-1.5 font-bold" onClick={() => setOpen(!open)} aria-expanded={open} aria-label="Menu">
            {open ? "Close" : "Menu"}
          </button>
        </div>
      </div>
      {open && (
        <nav className="lg:hidden border-t border-white/10 px-4 pb-4 grid gap-1">
          {NAV.map(([label, href]) => (
            <Link key={href} href={href} onClick={() => setOpen(false)} className="py-2 font-bold">{label}</Link>
          ))}
        </nav>
      )}
    </header>
  );
}
