# November 3, 2027 Launch Plan

Target: **public launch Wednesday, November 3, 2027, 12:00 PM America/New_York (EDT, UTC−4)**.
(Daylight saving ends Nov 7, 2027, so Nov 3 is still EDT.) The time is configurable in
`web/.env` → `NEXT_PUBLIC_LAUNCH_ISO` / `NEXT_PUBLIC_LAUNCH_TZ`.

**The calendar never overrides safety.** If any critical security, metadata, payment or ownership
issue is open, we recommend delaying launch and announcing the delay honestly.

## Critical path
The **artwork** is the longest pole. Everything else is built and waiting for it.
Production layers must be delivered by **end of March 2027** to keep the schedule comfortable.

## Schedule (working backward from launch)

| When | Milestone | Owner | Done when |
|---|---|---|---|
| **Nov 2026** | Brand foundation, project architecture, website foundation, contract + tests, generator | Claude | ✅ built (this repo) |
| Nov 2026 | Founder decisions: artist, wallet limit, royalty, launch time | Founder | Written answers |
| Nov 2026 | Secure names: domain, X, Discord, Instagram; trademark search | Founder | Checklist complete |
| Dec 2026 | Artist contract signed (rights assignment, AI disclosure); template + 2 species delivered | Founder + artist | Files pass `generate.py assets` |
| Dec 2026 | Character style approval (first real samples) | Founder | Written approval |
| Jan–Mar 2027 | All 138 layer files delivered and reviewed | Artist | 138 / 138 delivered |
| Mar 2027 | Generate + validate 10,000; rarity & trait reports | Claude | `generate.py validate` passes |
| Apr 2027 | Sepolia deployment, wallet + mint testing, gallery integration | Claude + founder | Sepolia checklist complete |
| Apr–May 2027 | IPFS test upload to Sepolia build; metadata verification | Claude | `ipfs_upload.py verify --all` passes |
| May–Jun 2027 | Website hosted (staging); admin dashboard in use; legal review of license/terms/privacy | Founder + lawyer | Staging URL live |
| Jul–Aug 2027 | Open community channels; publish story; character introductions; roadmap announcement; allowlist criteria | Founder | Channels live |
| Sep 2027 | **Independent contract review**; fix findings; final art QA; verify supply + metadata | Reviewer + Claude | Review report, all critical/high fixed |
| Oct 1–15, 2027 | Final IPFS upload of real art; verify all 10,000; final contract review | Claude | Verified |
| Oct 15–25, 2027 | **Mainnet deployment (only with explicit founder approval)**; Etherscan verification; **provenance hash set + published**; OpenSea setup; reserve mint to founder wallet; allowlist root set | Founder signs | Contract verified |
| Oct 25–31, 2027 | Mint simulation on Sepolia with the final build; mobile + desktop wallet tests; countdown posts | All | Launch checklist green |
| **Nov 3, 2027** | Allowlist window opens (proposed), then public mint (when authorized by founder) | Founder | Mint live |
| Sell-out or Nov 5, 2027 (proposed) | **Reveal**: commit → finalize → per-token metadata upload → reveal; gallery switches to token numbers | Founder + Claude | Tokens revealed, spot-checked |

## Testing calendar
| Date | Test |
|---|---|
| Every change | Contract tests (27), art tests (6), website type-check + build |
| Apr 2027 | Sepolia: deploy, verify, allowlist mint, public mint, limits, reserve, withdraw, ownership transfer |
| May 2027 | Mobile wallets (MetaMask mobile, Rainbow, Coinbase Wallet) via WalletConnect |
| Sep 2027 | Independent review; re-test after every fix |
| Oct 2027 | Full rehearsal on Sepolia with final metadata; load test of website |

## Launch-day run sheet (Nov 3, 2027, New York time)
| Time | Action |
|---|---|
| 08:00 | Final go/no-go meeting using LAUNCH_CHECKLIST.md |
| 09:00 | Post "Today's the day" (Social kit) |
| 11:45 | Founder opens allowlist mint from admin dashboard (owner wallet signs) |
| 12:00 | Countdown hits zero; announcement posted |
| As planned | Founder opens public mint when ready |
| All day | Monitor: Etherscan, website errors, Discord questions; never DM first |
| Evening | Thank-you post; honest stats only |
