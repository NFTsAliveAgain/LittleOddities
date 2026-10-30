# OpenSea Guide

The website is the primary mint. OpenSea reads **the same contract** — never deploy a second one.

## What happens automatically
OpenSea usually indexes standard ERC-721 contracts on Ethereum after the first mint and reads
`tokenURI` metadata. It does **not** automatically verify, feature or promote a collection.

## Manual setup (after mainnet deployment)
1. Go to opensea.io, connect the **owner wallet** (the contract owner can edit the collection).
2. Find the collection (search the contract address) → "Edit collection".
3. Upload: logo `brand/social/profile-400x400.png`, banner `brand/banners/opensea-banner-1400x350.png`, featured image.
4. Description (from SOCIAL_LAUNCH_KIT), website URL, Discord, X links. Category: PFPs / Art.
5. Creator earnings: set the payout address and percentage if desired (enforcement depends on OpenSea's policies).
6. Slug: request `little-oddities` if free.

## Testing on Sepolia
Use https://testnets.opensea.io with the Sepolia contract to check images and traits display properly.

## Metadata refresh
If an image or traits look stale: open the item → "⋯" → **Refresh metadata**. For the whole
collection, contact OpenSea support or use their API refresh endpoint.

## Verification badge
OpenSea's blue checkmark is decided by OpenSea, based on their criteria — it cannot be requested as a right.

## Contract source verification (Etherscan)
Run the `npx hardhat verify` command printed by the deploy script. Verified source builds trust and lets
OpenSea/wallets display contract info.
