# Deployment Guide (Sepolia first, mainnet only with approval)

## Accounts you need
| Account | Why | Cost |
|---|---|---|
| **Owner wallet** (hardware wallet strongly recommended, e.g. Ledger/Trezor) | Owns the contract, receives funds and the 500 reserve | — |
| **Deployer wallet** (a fresh, separate wallet) | Pays deploy gas; holds only what's needed | Sepolia: free test ETH; mainnet: ~0.02–0.06 ETH |
| Alchemy or Infura account | RPC URL to talk to Ethereum | Free tier |
| Etherscan account | API key for source-code verification | Free |
| Pinata account | IPFS pinning | Free tier may not fit 10k images — check plan limits |

**Never** paste your owner wallet's seed phrase or private key anywhere. The deploy script only
needs the *deployer* key, kept in `contracts/.env` on your own computer.

## Step 1 — Sepolia (test network, no real money)
1. Get Sepolia ETH for the deployer from a faucet (e.g. the Alchemy or Google Cloud Sepolia faucet).
2. `cd contracts && cp .env.example .env` and fill in:
   `SEPOLIA_RPC_URL`, `DEPLOYER_PRIVATE_KEY` (deployer only!), `ETHERSCAN_API_KEY`, `OWNER_ADDRESS` (your public owner address),
   `UNREVEALED_URI` (mystery metadata — can stay a placeholder on Sepolia; on mainnet use `python3 art/ipfs_upload.py hidden`), `CONTRACT_URI`, `WALLET_LIMIT`=10, `ROYALTY_BPS`=500.
3. `npx hardhat test` → must show 27 passing.
4. `npm run deploy:sepolia` → prints the address and saves `deployments/sepolia.json`.
5. Verify the source: copy the `npx hardhat verify ...` command it prints and run it.
6. In `web/.env.local` set `NEXT_PUBLIC_CHAIN=sepolia` and `NEXT_PUBLIC_CONTRACT_ADDRESS=<address>`.
7. Work through the Sepolia section of LAUNCH_CHECKLIST.md.

## Step 2 — Mainnet (REAL money — founder approval required)
Before anything: the independent review is complete, every critical/high finding is fixed and re-tested,
real artwork + metadata are uploaded and verified (`ipfs_upload.py verify --all`), and the founder has
approved in writing. The deploy script refuses mainnet unless you run:
```bash
CONFIRM_MAINNET_DEPLOY=I_APPROVE_MAINNET npm run deploy:mainnet
```
It also refuses if `UNREVEALED_URI` still contains a placeholder CID.
Expected cost: deploy ≈ 2.38M gas (≈ 0.012 ETH at 5 gwei, 0.048 ETH at 20 gwei).

## Step 3 — After deployment (owner wallet, from the admin dashboard)
1. Verify on Etherscan. 2. **Set the provenance hash** (before ANY mint — it locks at the first mint).
3. Mint the 500 reserve to your wallet (when gas is low; ≈12.6M gas). 4. Set allowlist root. 5. Set up OpenSea (OPENSEA_GUIDE).
6. Open allowlist / public mint only at the announced time.
7. Reveal (admin → Mint settings → Delayed reveal): Commit → Finalize → build metadata with the starting index → Reveal.
8. Freeze metadata once you are 100% sure it's final (optional, irreversible).

## Website hosting (Vercel recommended)
1. Push the repo to *your* GitHub. 2. On vercel.com, "Add New Project" → import repo → Root Directory `web`.
3. Add the environment variables from `web/.env.example` (production values). 4. Create a free Turso database
(turso.tech), set `DATABASE_URL` + `DATABASE_AUTH_TOKEN`. 5. Add your domain in Vercel → Domains.
