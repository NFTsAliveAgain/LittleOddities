# Smart Contract Guide

File: `contracts/contracts/LittleOddities.sol` · Standard: ERC-721 + ERC-2981 · Libraries: OpenZeppelin Contracts 5.7.0
Solidity 0.8.28 · Tests: `contracts/test/LittleOddities.test.js` (27 passing)

> Not audited. An independent review is required before mainnet (planned Sep 2027).

## Fixed rules (cannot be changed by anyone, ever)
| Rule | Value |
|---|---|
| Maximum supply | 10,000 |
| Reserved giveaway allocation | 500 (part of the 10,000), **500 total ever**, minted to the owner in batches |
| Max per paid transaction | 4 |
| Token IDs | Sequential, starting at 1 |
| Max royalty | 10% |
| Paid mints can use reserved slots? | No — paid mints stop at 9,500 until the reserve is minted |

## Owner-controlled settings (all emit events)
| Function | What it does | Default |
|---|---|---|
| `setMintPrice(wei)` | Change price per NFT | 0.005 ETH |
| `setWalletLimit(n)` | Lifetime paid mints per wallet (allowlist + public combined) | **10 (proposed — confirm)** |
| `setMerkleRoot(root)` | Publish allowlist | empty |
| `setAllowlistActive(bool)` | Open/close allowlist mint | closed |
| `setPublicActive(bool)` | Open/close public mint | closed |
| `mintReserve(quantity)` | Mint reserved NFTs to the owner wallet; batches add up to exactly 500, never more | — |
| `setProvenanceHash(hash)` | Publish the image fingerprint — **only before the first mint** | empty |
| `setUnrevealedURI(uri)` | Mystery metadata shown before reveal | from deploy |
| `commitReveal()` | Reveal step 1: choose the next block as randomness source | — |
| `finalizeReveal()` | Reveal step 2 — **anyone** may call; sets `startingIndex` | — |
| `reveal(baseURI)` | Reveal step 3: point tokens at final metadata (once) | — |
| `setBaseURI(uri)` | Fix final metadata location — only after reveal, until frozen | — |
| `freezeMetadata()` | Permanently lock metadata (irreversible; after reveal) | not frozen |
| `setContractURI(uri)` | Collection-level info for marketplaces | from deploy |
| `setRoyalty(addr, bps)` | ERC-2981 royalty (≤ 10%) | 5% to owner (proposed) |
| `withdraw()` | Send all mint ETH to the owner wallet | — |
| `transferOwnership(addr)` then `acceptOwnership()` | Two-step owner change | — |

**What the owner can NOT do:** mint beyond the single 500 reserve, exceed 10,000, mint for free
outside the reserve (price is charged to everyone, including the owner), take NFTs from holders,
change metadata after freezing, or renounce ownership by accident (`renounceOwnership` is disabled).
There are no other roles, admins or hidden functions.

## Minting rules
- `publicMint(quantity)` — public sale must be open; 1–4; `msg.value` must **exactly** equal price × quantity (under- and over-payment both rejected); wallet limit enforced.
- `allowlistMint(quantity, allocation, proof)` — allowlist must be open; Merkle proof of (wallet, allocation); total allowlist mints ≤ allocation; same price and limits.
- Reentrancy guarded; `_safeMint` for buyers (contract wallets must accept NFTs).

## Allowlist tool
```bash
cd contracts
node scripts/allowlist.js build allowlist/allowlist.csv   # CSV: address,allocation
node scripts/allowlist.js check 0xWallet
node scripts/allowlist.js export allowlist/export.csv
```
Build prints the Merkle root (paste into the admin dashboard → Mint settings → Set root) and writes
`web/public/allowlist.json` so the website can show eligibility and supply proofs.

## Measured gas
**Important:** Sepolia (Oct 31, 2026) charges far more for storing new data than the local simulator — deploying
cost ~6.8× more and the 500 reserve ~4.6× more. Mainnet pricing in 2027 may match either; **re-measure before mainnet.**

| Action | Local simulator | Sepolia (measured / estimated) |
|---|---|---|
| Deploy | 2,886,083 | 19,840,635 (measured) |
| Mint 1 (first mint of a wallet) | ~125,400 | not yet measured |
| Reserve, batch of 100 | 2,598,894 | 11,757,732 (estimated by the network) |
| Reserve, all 500 at once | ~12.6M | fails: needs > 50,000,000 — **too large for one transaction** |
| Withdraw | ~34,600 | not yet measured |
Cost = gas × gas price (e.g. 20M gas at 1 gwei = 0.02 ETH; at 10 gwei = 0.2 ETH). Check https://etherscan.io/gastracker before any mainnet action.
**Why the reserve is batched:** a single 500-token mint can exceed Ethereum's per-transaction gas limit (~16.7M).
Batches of **100** stay under it. The 500 total cap is enforced on-chain regardless of batch size.

## Delayed reveal (founder decision, Oct 31, 2026)
Chosen to stop "rarity sniping" (the original brief asked for instant reveal; the founder changed this).
1. **Provenance** — `python3 art/provenance.py` → SHA-256 of all image hashes in planned order. Owner
   publishes it with `setProvenanceHash` before minting; it locks automatically at the first mint.
2. **Mint** — every token's `tokenURI` returns the mystery metadata (`brand/reveal/hidden.png`).
3. **Randomness** — owner `commitReveal()` fixes a *future* block; ~12 s later anyone calls
   `finalizeReveal()`, which hashes that block's hash + `prevrandao` → `startingIndex` (1–9,999).
   Must be finalized within 256 blocks (~50 min) or the owner simply commits again.
4. **Mapping** — token N shows planned character `((N − 1 + startingIndex) % 10000) + 1` (`characterOf(N)` on-chain).
5. **Reveal** — `python3 art/ipfs_upload.py metadata --starting-index N` builds per-token metadata; owner calls `reveal("ipfs://<CID>/")`.
**When to reveal:** proposed at sell-out or 48 hours after public mint opens, whichever comes first — announce it in advance.
**Randomness strength:** a block proposer could in theory withhold a block to re-roll; for an NFT reveal this is
considered acceptable and is widely used. Chainlink VRF is the stronger (paid) alternative if ever needed.
**Verification for collectors:** recompute the provenance hash from the IPFS images, read `startingIndex`, apply the formula.

## Known trade-offs (please read)
1. **Unrevealed period:** holders see a mystery image until the reveal; be clear about the reveal timing.
2. **Royalties are not enforced** by marketplaces; ERC-2981 is only a signal.
3. **Reserve mint takes ~5 transactions** (batches of 100). Do them when gas is low, before public mint.
4. **Gas cost uncertainty:** see "Measured gas" — a gas-saving ERC721A implementation can be evaluated before launch.

## Running tests
```bash
cd contracts && npm install && npx hardhat test
```
