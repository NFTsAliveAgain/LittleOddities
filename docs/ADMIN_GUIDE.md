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
| Mint settings (on-chain) | Open/close allowlist + public mint, set price, wallet limit, allowlist root, mint the 500 reserve, withdraw |

## The 500 giveaway NFTs — workflow
1. After deployment, Mint settings → **Mint 500 reserve** (one time; costs ≈12.6M gas — do it when gas is low).
2. Create a giveaway (Giveaways tab), publish it, and announce rules publicly.
3. Pick winners fairly and transparently (e.g. announced criteria or a public random draw).
4. Send each NFT from the owner wallet (OpenSea "Transfer" or your wallet's NFT send).
5. Record each winner with the transaction hash. The public page links to Etherscan as proof.
Never record a winner before the transfer has happened.

## On-chain actions
Each button sends a real transaction from the connected owner wallet; a confirmation dialog explains it first,
then your wallet shows the gas cost. If the connected wallet isn't the owner, a red warning appears.
