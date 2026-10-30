# Website Guide

Tech: Next.js 15 · TypeScript · Tailwind CSS 4 · RainbowKit · wagmi · viem · libSQL (Turso) database.

## Pages
| URL | What it does |
|---|---|
| `/` | Hero, showcase, stats, rarity tiers, giveaway counter (real records only), roadmap preview, countdown |
| `/collection` | All 10,000: search (#ID, name, trait), sort, filter by rarity/trait, trait statistics |
| `/collection/[id]` | One Oddity: traits with % rarity, OpenSea link |
| `/mint` | Wallet connect, network check, allowlist check, price, 1–4 selector, total, status, tx + token IDs |
| `/roadmap` | Interactive 4-phase roadmap with honest statuses (edited in admin) |
| `/community` | Announcements, events, polls/character voting, giveaways + winners, suggestions |
| `/about`, `/faq` | Story and questions |
| `/license`, `/terms`, `/privacy` | DRAFT legal pages (lawyer review needed) |
| `/admin` | Owner-only dashboard (ADMIN_GUIDE) |

Images: until `NEXT_PUBLIC_IMAGES_BASE` is set, cards say "Artwork in progress" (no fake art).

## Run locally
```bash
cd web
npm install
cp .env.example .env.local     # then edit values
npm run dev                    # http://localhost:3000
```
After changing the contract: `cd contracts && npx hardhat compile` then `cd web && npm run abi:sync`.
After re-planning the collection: `cd art && python3 generate.py plan` then `cd web && npm run collection:sync`.

## Environment variables (`web/.env.example` explains each)
Public: chain, contract address, WalletConnect project id (free at cloud.reown.com), launch date/timezone, images base, RPC URL.
Server-only: `ADMIN_ADDRESSES`, `SESSION_SECRET`, `DATABASE_URL`, `DATABASE_AUTH_TOKEN`.

## Launch timezone
`NEXT_PUBLIC_LAUNCH_ISO=2027-11-01T12:00:00-04:00` and `NEXT_PUBLIC_LAUNCH_TZ=America/New_York`.
Visitors see the countdown in real time and the launch moment written in New York time.

## Tests
- `npm run typecheck` and `npm run build`
- `node scripts/e2e-local.mjs` — 22-step end-to-end test against a local Hardhat chain (see the script header)
