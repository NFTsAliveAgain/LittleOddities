# Project Overview

## The project in one paragraph
**NFTs Alive Again** is a brand and community whose mission is to make NFTs fun again. Its first
collection, **Little Oddities**, is 10,000 original cartoon characters on Ethereum. Minting costs
**0.005 ETH** (plus gas), up to **4 per transaction**, with **500 reserved** for community
giveaways. Tokens are revealed together after the mint using provable on-chain randomness. The official target launch is **November 3, 2027**.

## How the pieces fit together
```
 Artist layers ──► art/ generator ──► 10,000 PNG + 10,000 JSON ──► IPFS (Pinata)
                                                                     │  CIDs
                                                                     ▼
                         contracts/ LittleOddities.sol  ◄── baseURI = ipfs://<METADATA_CID>/
                                   ▲        │
                 mint (wallet)     │        │ read: supply, price, status
                                   │        ▼
                         web/ website (mint, gallery, roadmap, community, admin)
                                   │
                               OpenSea reads the same contract + metadata
```

## Where things stand (updated by Claude, Oct 30, 2026)
| Area | Status | Notes |
|---|---|---|
| Brand identity | In progress | Logos, palette, typography, banners, favicon created. Name availability not yet verified. |
| Artwork | In progress | Art direction chosen (artist concept sheets). Production layers **not yet delivered** (0 / 138 files). |
| Generator & rarity | Done (code) | Exact 5,000/3,000/1,500/400/100 rarity, uniqueness, rules, metadata, validation. 6 automated tests. |
| Smart contract | Written + tested | 27 automated tests pass. Not audited. Not deployed to Sepolia yet. |
| Website | Built (pre-launch) | All pages + owner dashboard. 22-step local end-to-end test passes. Not hosted yet. |
| IPFS | Tool built | Nothing uploaded (no final art yet). |
| Community channels | Not started | Discord/X handles not yet secured. |

## Documentation index
- Getting started: [README](../README.md), this file
- Brand: [BRAND_GUIDE](BRAND_GUIDE.md), [NAME_AVAILABILITY_CHECKLIST](NAME_AVAILABILITY_CHECKLIST.md), [SOCIAL_LAUNCH_KIT](SOCIAL_LAUNCH_KIT.md)
- Art: [ARTWORK_GUIDE](ARTWORK_GUIDE.md), [ARTIST_LAYER_SPEC](ARTIST_LAYER_SPEC.md), [COLLECTION_METADATA_GUIDE](COLLECTION_METADATA_GUIDE.md)
- Contract: [SMART_CONTRACT_GUIDE](SMART_CONTRACT_GUIDE.md), [DEPLOYMENT_GUIDE](DEPLOYMENT_GUIDE.md)
- Website & admin: [WEBSITE_GUIDE](WEBSITE_GUIDE.md), [ADMIN_GUIDE](ADMIN_GUIDE.md), [COMMUNITY_GUIDE](COMMUNITY_GUIDE.md)
- Storage & marketplaces: [IPFS_GUIDE](IPFS_GUIDE.md), [OPENSEA_GUIDE](OPENSEA_GUIDE.md)
- Launch: [ROADMAP](ROADMAP.md), [NOVEMBER_3_2027_LAUNCH_PLAN](NOVEMBER_3_2027_LAUNCH_PLAN.md), [LAUNCH_CHECKLIST](LAUNCH_CHECKLIST.md)
- Safety & ownership: [SECURITY_CHECKLIST](SECURITY_CHECKLIST.md), [OWNERSHIP_AND_RIGHTS](OWNERSHIP_AND_RIGHTS.md), [MAINTENANCE_GUIDE](MAINTENANCE_GUIDE.md)

## Founder decisions (Oct 31, 2026)
- Lifetime wallet limit: **10** · Royalty: **5%** · 500 reserve → **founder's own wallet**
- Owner wallet (public): `0xC49f8eb7460246769Adb3a9C0304F000aE7aFD1f` — recorded in `contracts/founder-wallet.json`; contract owner, mint proceeds, 500 reserve, admin login
- Launch: **Wednesday Nov 3, 2027, 12:00 PM New York time (EDT)**
- **Delayed reveal** with provenance + on-chain randomness (replaces instant reveal)

## Still waiting on the founder
1. **Artist:** rights + AI-use answers, quote for production layers (ARTIST_LAYER_SPEC).
2. **Reveal timing:** proposed at sell-out or 48h after public mint opens, whichever first.
3. **Allowlist criteria and size.**
