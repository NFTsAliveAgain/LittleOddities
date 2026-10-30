# Launch Checklist

Tick every box before Nov 1, 2027. Any unticked **critical** item = recommend delay.

## Art & metadata (critical)
- [ ] All 138 artist layer files delivered (`python generate.py assets` → 138 / 138)
- [ ] Rights assignment signed; AI-use disclosure received
- [ ] Founder approved final samples in writing
- [ ] `python generate.py collection --approved-art` completed with 0 placeholders
- [ ] `python generate.py validate` → 0 problems; rarity exactly 5,000 / 3,000 / 1,500 / 400 / 100
- [ ] Images + metadata uploaded; `python ipfs_upload.py verify --all` → 0 problems
- [ ] Pinned on at least two services (Pinata + one backup)

## Contract (critical)
- [ ] 27/27 tests pass on the final commit
- [ ] Independent review complete; critical/high findings fixed
- [ ] Sepolia rehearsal complete (below)
- [ ] Founder written approval for mainnet; costs explained
- [ ] Deployed, verified on Etherscan, owner = founder's owner wallet
- [ ] `mintPrice` = 0.005 ETH, `MAX_PER_TX` = 4, wallet limit = agreed value
- [ ] `tokenURI(1)` resolves to correct metadata and image
- [ ] 500 reserve minted to owner wallet
- [ ] Allowlist root set and spot-checked with `allowlist.js check`
- [ ] Public mint **closed** until the founder opens it

## Sepolia rehearsal
- [ ] Allowlist mint (eligible ✓, ineligible ✗, over-allocation ✗)
- [ ] Public mint 1, 2, 3, 4 ✓; 5 ✗; wrong payment ✗; wallet limit ✗ when exceeded
- [ ] Success screen shows token IDs + Etherscan link; OpenSea testnet link works
- [ ] Withdraw works; ownership transfer rehearsal on a throwaway deploy
- [ ] MetaMask desktop, MetaMask mobile, Rainbow, Coinbase Wallet tested

## Website
- [ ] Production env vars set; contract address correct; `NEXT_PUBLIC_CHAIN=mainnet`
- [ ] Countdown shows Nov 1, 2027 12:00 PM EDT (or agreed time)
- [ ] Mobile + desktop check of every page; no console errors
- [ ] Legal pages reviewed by a lawyer (DRAFT banners removed only after review)
- [ ] Social links set in admin; roadmap statuses accurate

## OpenSea & community
- [ ] OpenSea collection page set up (OPENSEA_GUIDE) and metadata refresh tested
- [ ] Discord + X live; moderators briefed; anti-scam message pinned
- [ ] Launch posts scheduled (SOCIAL_LAUNCH_KIT)
