# Maintenance Guide

## Weekly
- Review suggestions and update roadmap statuses (admin)
- Check site is up; check Discord for scam reports

## Monthly
- `npm outdated` / `npm audit` in `web/` and `contracts/`; update carefully, run tests + build
- Check Pinata pins are still present (`python3 ipfs_upload.py verify`)
- Renewals: domain, Pinata plan, Vercel, Turso

## After launch
- Contract code cannot change. Settings (price, limits, mint open/closed) change via admin.
- If anything looks wrong on-chain, close minting first (admin → Mint settings), then investigate.
- Keep `ipfs_record.json`, `deployments/*.json` and the audit report committed in the repo.

## Backups
- Database: Turso dashboard → backups / or periodic export
- Artwork sources + generated collection: two places (cloud + offline drive)
