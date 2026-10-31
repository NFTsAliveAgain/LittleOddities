import Link from "next/link";
import { Mark } from "./Logo";
import { site } from "@/lib/site";
import SocialLinks from "./SocialLinks";

export default function Footer() {
  return (
    <footer className="bg-night text-cream border-t-4 border-ink mt-16">
      <div className="mx-auto max-w-7xl px-4 py-10 grid gap-8 md:grid-cols-4">
        <div className="md:col-span-2">
          <div className="flex items-center gap-3"><Mark size={44} /><span className="font-display font-black text-xl">{site.brand}</span></div>
          <p className="mt-3 text-cream/70 max-w-md">{site.collection} · {site.slogan} 10,000 total supply · {site.mintPriceEth} ETH + gas · Target launch Nov 3, 2027.</p>
          <p className="mt-3 text-xs text-cream/50 max-w-md">NFTs are digital collectibles, not investments. Nothing on this site is a promise of value, profit or future deliverables.</p>
        </div>
        <div className="grid gap-1 text-sm">
          <Link href="/collection">Collection</Link><Link href="/mint">Mint</Link><Link href="/roadmap">Roadmap</Link>
          <Link href="/community">Community</Link><Link href="/faq">FAQ</Link>
        </div>
        <div className="grid gap-1 text-sm content-start">
          <Link href="/license">NFT holder license</Link><Link href="/terms">Terms of service</Link><Link href="/privacy">Privacy policy</Link>
          <div className="mt-3"><SocialLinks /></div>
        </div>
      </div>
      <p className="text-center text-xs text-cream/40 pb-6">© {new Date().getFullYear()} {site.brand}. Drafts of legal pages pending legal review.</p>
    </footer>
  );
}
