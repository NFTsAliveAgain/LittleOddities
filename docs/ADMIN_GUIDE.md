# Admin Guide (for the founder)

## Signing in
1. Open `https://<your-site>/admin`.
2. Click **Connect Wallet** and choose the wallet whose address is in `ADMIN_ADDRESSES` (set in Vercel → Settings → Environment Variables).
3. Click **Sign in with wallet** and approve the signature. It is free (no gas, no transaction).
4. You stay signed in for 8 hours. **Sign out** on shared computers.
No passwords exist. To add a helper admin, add their public address to `ADMIN_ADDRESSES` (comma-separated) and redeploy.

## Tabs
| Tab | Use it to |
|---|---|
| Roadmap | Edit titles/details, set **Planned / In progress / Completed**. Only mark completed when truly done |
| Announcements | Write posts; tick *published* to show them; *holders_only* labels holder posts |
| Events & contests | Add events, contests, spaces with dates and links |
| Polls & voting | Create a poll (tick *open*; *holders_only* = only NFT holders may vote), then add options in **Poll options** with the poll's id |
| Suggestions | Review community ideas: set *approved* to show publicly, *rejected* to hide, *done* when implemented |
| Giveaways | Create giveaway campaigns (quantity, status, dates) |
| Giveaway winners | **After** sending the NFT, record wallet, token id and the real transaction hash (validated) |
| Site settings & links | Discord / X / Instagram / YouTube URLs, welcome message, mint status note |
| Audit log | Read-only record of every admin action |
| Mint settings (on-chain) | Open/close allowlist + public mint, set price, wallet limit, allowlist root, mint the 500 reserve, withdraw, **delayed reveal** (provenance → commit → finalize → reveal) |

## The 500 giveaway NFTs — workflow
1. After deployment, Mint settings → **Mint next 100 of reserve** — press it 5 times (one transaction each) until it shows 500 / 500. Do it when gas is low. It can never go above 500.
2. Create a giveaway (Giveaways tab), publish it, and announce rules publicly.
3. Pick winners fairly and transparently (e.g. announced criteria or a public random draw).
4. Send each NFT from the owner wallet (OpenSea "Transfer" or your wallet's NFT send).
5. Record each winner with the transaction hash. The public page links to Etherscan as proof.
Never record a winner before the transfer has happened.

## The reveal (after the mint)
1. Before minting opens: Mint settings → paste the provenance hash → **Set provenance**.
2. When it's reveal time: **1 · Commit reveal**. Wait about a minute. **2 · Finalize** (must be within ~50 minutes).
3. Note the starting index shown. Ask Claude/your developer to run `ipfs_upload.py metadata --starting-index N` and give you the `ipfs://…/` address.
4. Paste it and press **3 · Reveal**. Then in `web`, run `STARTING_INDEX=N npm run collection:sync` and redeploy the site so the gallery switches to token numbers.

## On-chain actions
Each button sends a real transaction from the connected owner wallet; a confirmation dialog explains it first,
then your wallet shows the gas cost. If the connected wallet isn't the owner, a red warning appears.
