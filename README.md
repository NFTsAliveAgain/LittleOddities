# NFTs Alive Again — Little Oddities

**A World of Wonderfully Weird.** · *Bringing NFTs Alive Again.*

This repository contains everything for the Little Oddities NFT project: the art generator, the
Ethereum smart contract, the website + community platform, the brand kit and all documentation.

> **Status (honest):** in development. Target public launch: **November 3, 2027**.
> Final artwork is being commissioned (placeholders are used for testing and are labelled as such).
> The smart contract is written and tested but **not independently audited** and **not deployed** anywhere public.

## What's in here

| Folder | What it is | Start with |
|---|---|---|
| `art/` | Collection planner, artist-layer compositor, metadata, validation, IPFS upload | `docs/ARTWORK_GUIDE.md` |
| `contracts/` | `LittleOddities.sol` (ERC-721), tests, allowlist tool, deploy script | `docs/SMART_CONTRACT_GUIDE.md` |
| `web/` | Next.js website: home, collection, mint, roadmap, community, admin | `docs/WEBSITE_GUIDE.md` |
| `brand/` | Logos, banners, social images, favicon, palette, fonts | `docs/BRAND_GUIDE.md` |
| `docs/` | All guides, checklists and the launch plan | `docs/PROJECT_OVERVIEW.md` |

## Quick commands

```bash
# Art: plan all 10,000, check which artist files have arrived, render samples
cd art && python3 generate.py plan && python3 generate.py assets && python3 generate.py samples

# Contract: run the 27 automated tests
cd contracts && npm install && npx hardhat test

# Website: run locally at http://localhost:3000
cd web && npm install && cp .env.example .env.local && npm run dev
```

## Golden rules
1. Never share or commit a private key, seed phrase or `.env` file.
2. Nothing goes to Ethereum mainnet without the founder's explicit written approval.
3. No invented transaction hashes, contract addresses, IPFS CIDs, winners, votes or stats — ever.

Full documentation index: [`docs/PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md).
