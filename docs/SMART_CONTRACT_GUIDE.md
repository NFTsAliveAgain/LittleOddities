# Smart Contract Guide

File: `contracts/contracts/LittleOddities.sol` · Standard: ERC-721 + ERC-2981 · Libraries: OpenZeppelin Contracts 5.7.0
Solidity 0.8.28 · Tests: `contracts/test/LittleOddities.test.js` (27 passing)

> Not audited. An independent review is required before mainnet (planned Sep 2027).

## Fixed rules (cannot be changed by anyone, ever)
| Rule | Value |
|---|---|
| Maximum supply | 10,000 |
| Reserved giveaway allocation | 500 (part of the 10,000), mintable **once** |
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
| `mintReserve()` | Mint the 500 reserved NFTs to the owner wallet (once) | — |
| `setBaseURI(uri)` | Metadata location (`ipfs://CID/`) | from deploy |
| `freezeMetadata()` | Permanently lock metadata (irreversible) | not frozen |
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

## Measured gas (local test chain)
| Action | Gas | Cost at 5 gwei | Cost at 20 gwei |
|---|---|---|---|
| Deploy | 2,377,382 | ~0.012 ETH | ~0.048 ETH |
| Mint 1 (first mint of a wallet) | ~125,400 | ~0.0006 ETH | ~0.0025 ETH |
| Mint 4 | ~150,000 | ~0.00075 ETH | ~0.003 ETH |
| Reserve 500 (once) | 12,568,085 | ~0.063 ETH | ~0.25 ETH |
| Withdraw | ~34,600 | tiny | tiny |
Cost = gas × gas price. Check https://etherscan.io/gastracker before any mainnet action.

## Known trade-offs (please read)
1. **Instant reveal + sequential IDs = predictable next token.** Because metadata is public, someone
   can see which token ID mints next and time a mint for a Legendary. Limits (4/tx, wallet limit)
   reduce but don't eliminate this. Options: (a) accept and disclose; (b) shuffle which planned
   character gets which ID only at final generation (already random, still visible once uploaded);
   (c) commit-reveal randomized start index (this is a delayed reveal — conflicts with the brief).
   **Recommendation:** (a) with clear disclosure. Founder decides.
2. **Royalties are not enforced** by marketplaces; ERC-2981 is only a signal.
3. **Reserve mint is one big transaction** (~12.6M gas). Do it when gas is low, before public mint.

## Running tests
```bash
cd contracts && npm install && npx hardhat test
```
