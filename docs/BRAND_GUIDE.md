# Brand Guide

## Names
- Brand: **NFTs Alive Again** (always written exactly so; "NFTs" with lowercase s)
- Collection: **Little Oddities** · one character = "a Little Oddity" / "an Oddity"
- Slogan: **A World of Wonderfully Weird.** · Message: **Bringing NFTs Alive Again.**

## Personality
Playful, nostalgic, a bit weird, warm and honest. Think Saturday-morning cartoons meets indie
sticker shop. **Not:** neon cyberpunk, "to the moon", fake urgency, financial promises.

## Logo system (`brand/logos/`)
| File | Use |
|---|---|
| `mark.svg` | The Oddity-with-a-sprout mark. The sprout = things coming back to life. Avatars, favicon, stamps |
| `nfts-alive-again-dark.svg` | Wordmark lockup for dark backgrounds |
| `nfts-alive-again-light.svg` | Wordmark lockup for light backgrounds |
| `little-oddities.svg` | Collection logo: chunky "Little" + multicolour outlined "Oddities" + handwritten slogan |
Clear space: at least the height of the mark's eye around the logo. Don't stretch, recolour or add effects.
Text in the SVGs is converted to outlines, so they display correctly anywhere.

## Colours (`brand/palette/palette.png`)
| Name | Hex | Role |
|---|---|---|
| Ink | #1E1A2E | Outlines, text, offset shadows |
| Night | #141A2E | Dark sections, header/footer |
| Cream | #FBF5EA | Page background |
| Pink | #F59AC5 | Accent |
| Mint | #8EE3B0 | Accent, success |
| Lilac | #C9B8F2 | Accent |
| Sky | #7CC8FF | Accent, links on dark |
| Butter | #FFD86B | Primary highlight, "Alive" |
| Tomato | #FF6B4A | Primary action (Mint button), warnings |
| Moss | #5DBB4A | Sprout, "completed" |
Rarity colours: Common #8A93A6 · Uncommon #3FBF7F · Rare #3E8BFF · Epic #A35CF0 · Legendary #F2A516

## Typography (all SIL Open Font License — free for commercial use, licences in `brand/fonts/`)
- **Fraunces Black** — headlines and logo
- **DM Sans** — body text, UI
- **Caveat Bold** — handwritten accents ("Join the movement"), use sparingly

## Signature components
Thick 3px ink outlines, rounded corners, chunky offset "sticker" shadows (4–6px), slight rotations
(−2°), handwritten kickers above headlines, paper-dot texture. Defined in `web/src/app/globals.css`
(`.card`, `.btn`, `.wobble`, `.paper-grain`).

## Graphics (`brand/`)
X banner 1500×500 · OpenSea banner 1400×350 · Discord banner 960×540 · OG/share image 1200×630 ·
profile images 400×400 (butter + night) · favicons 32/180/512 + SVG. Rebuild after edits:
`python3 brand/build_logos.py` then `node brand/build_graphics.js`.

## Voice examples
✅ "Something weird is waking up." ✅ "500 Oddities are set aside for you, the community."
❌ "Don't miss out, floor will 10x!" ❌ "Partnered with [anyone we're not actually partnered with]."
