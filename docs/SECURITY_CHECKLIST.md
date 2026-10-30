# Security Checklist

## Wallets & secrets
- [ ] Owner wallet is a hardware wallet (or a multisig such as Safe with 2-of-3 signers)
- [ ] Deployer wallet is separate and holds only deployment funds
- [ ] Seed phrases stored offline on paper/metal, never photographed, never typed into a website
- [ ] `.env` files are never committed (`.gitignore` covers them) — check `git status` before every commit
- [ ] `SESSION_SECRET` is a long random string, different in production
- [ ] 2FA on GitHub, Vercel, Turso, Pinata, Alchemy, Etherscan, domain registrar, X, Discord, email

## Contract
- [x] OpenZeppelin audited building blocks (ERC721, ERC2981, Ownable2Step, ReentrancyGuard, MerkleProof)
- [x] Exact payment, 4/tx, wallet limit, supply cap, reserve-once all enforced on-chain and tested
- [x] Reentrancy attack test passes
- [x] Every admin function owner-only and tested against non-owners
- [x] `renounceOwnership` disabled; two-step ownership transfer
- [ ] Independent review by a reputable reviewer — **required before mainnet**
- [ ] All review findings fixed and re-tested
- [ ] Source verified on Etherscan

## Website
- [x] Admin access via wallet signature; admin list on the server only; HTTP-only, SameSite=strict session cookie, 8h expiry
- [x] Single-use sign-in nonces (replay rejected — tested)
- [x] Admin API only edits allow-listed tables/columns; every admin action audit-logged
- [x] Community votes/suggestions require wallet signatures; suggestions moderated before display
- [ ] Hosted over HTTPS only (Vercel default)
- [ ] Dependencies updated and `npm audit` reviewed before launch
- [ ] Rate limiting / bot protection reviewed at launch scale (e.g. Vercel firewall)

## Launch-day scams to warn the community about
- Fake mint sites and fake "support" DMs. We never DM first. The only mint is on the official website.
- Nobody from the team will ever ask for a seed phrase.
