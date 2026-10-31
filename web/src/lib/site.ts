// Central site settings. Values that change per environment come from .env (see .env.example).
export const site = {
  brand: "NFTs Alive Again",
  collection: "Little Oddities",
  slogan: "A World of Wonderfully Weird.",
  message: "Bringing NFTs Alive Again.",
  url: process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000",
  totalSupply: 10_000,
  reserved: 500,
  maxPerTx: 4,
  mintPriceEth: "0.005", // display only — the contract is the source of truth
  launchIso: process.env.NEXT_PUBLIC_LAUNCH_ISO || "2027-11-03T12:00:00-04:00",
  launchTz: process.env.NEXT_PUBLIC_LAUNCH_TZ || "America/New_York",
  chain: (process.env.NEXT_PUBLIC_CHAIN || "sepolia") as "sepolia" | "mainnet" | "localhost",
  contractAddress: (process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || "") as `0x${string}` | "",
  imagesBase: process.env.NEXT_PUBLIC_IMAGES_BASE || "",
};

export const tiers = [
  { name: "Common", count: 5000, pct: 50, color: "var(--color-common)", blurb: "Everyday Oddities, still special." },
  { name: "Uncommon", count: 3000, pct: 30, color: "var(--color-uncommon)", blurb: "More unique traits and details." },
  { name: "Rare", count: 1500, pct: 15, color: "var(--color-rare)", blurb: "Stand out with rare features." },
  { name: "Epic", count: 400, pct: 4, color: "var(--color-epic)", blurb: "Truly unusual combinations." },
  { name: "Legendary", count: 100, pct: 1, color: "var(--color-legendary)", blurb: "The rarest of the rare." },
] as const;

export const explorer = site.chain === "mainnet" ? "https://etherscan.io" : site.chain === "localhost" ? "http://localhost-no-explorer" : "https://sepolia.etherscan.io";
export const openseaItem = (id: number | string) =>
  site.chain === "mainnet" && site.contractAddress
    ? `https://opensea.io/assets/ethereum/${site.contractAddress}/${id}`
    : site.contractAddress
      ? `https://testnets.opensea.io/assets/sepolia/${site.contractAddress}/${id}`
      : "";
