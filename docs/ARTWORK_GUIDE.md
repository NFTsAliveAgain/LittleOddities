# Artwork Guide

## Art direction
Based on the artist's concept sheets: original, cute-but-cool 2D cartoon characters with bold clean
outlines, expressive faces, many species (Fuzzy, Slime, Cat, Mushroom, Ghost, Robot, Alien…),
streetwear and quirky accessories, painted scenic backgrounds.

## How the 10,000 are made
1. The **artist** draws every trait once as a transparent layer (spec: ARTIST_LAYER_SPEC.md).
2. `art/config/traits.json` lists every trait, its rarity tier, weight and compatibility rules.
3. The **planner** decides all 10,000 combinations before drawing anything:
   - exact tiers 5,000 / 3,000 / 1,500 / 400 / 100, shuffled across token IDs with a fixed seed (20271101)
   - every non-Common token gets exactly one "signature" trait of its tier, allocated in exact quotas
   - no token contains a trait rarer than its tier → **Rarity = rarest trait**
   - compatibility rules (e.g. no glasses over goggles, ghosts don't skateboard)
   - unique trait combinations and unique names
4. The **compositor** stacks the layers, tints each species with its Color, clips patterns to the body.
5. **Validation** checks every image (size, blank, exact + near duplicates) and every metadata file.

## Commands (run inside `art/`)
| Command | What it does |
|---|---|
| `python3 generate.py plan` | Plan all 10,000 + trait statistics (`output/plan/`) |
| `python3 generate.py assets` | Which artist files are delivered / missing |
| `python3 generate.py samples --count 30` | Render samples + contact sheet for approval |
| `python3 generate.py collection --approved-art` | Render all 10,000 (refuses if layers missing) |
| `python3 generate.py validate` | Validate the full collection |
| `python3 -m unittest discover -s tests` | Pipeline tests |

## Asset status (honest)
| Item | Status |
|---|---|
| Artist concept sheets | Received (mockups — not production files; AI-use + rights questions pending) |
| Production layers | **0 / 138 delivered** |
| Placeholder cards | Used for development only; labelled "PLACEHOLDER – artist layers pending"; upload tool refuses them |
| Earlier code-drawn prototype (v4 "Oddity") | Archived in `art/config/procedural_traits.json` + `art/oddities/oddity.py`; usable for testing with `--config config/procedural_traits.json` |

## Approval log
| Date | What was approved | By |
|---|---|---|
| | Sample characters from real artist layers | Founder |
