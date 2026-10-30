# Little Oddities — Artist Layer Specification

This is what the artist delivers so the generator can build all 10,000 Little Oddities
with exact rarity. **Send this whole document to the artist.**

## The big idea
The artist does **not** draw 10,000 pictures. They draw each trait **once** as a separate
transparent layer. The generator stacks the layers (background → body → clothes → face → hat …)
in thousands of unique combinations. This is how most well-known PFP collections are made.

## Non-negotiable file rules
1. **Canvas:** every file is **2048 × 2048 px**, PNG, **transparent background** (except backgrounds), sRGB.
2. **Same template:** every layer is drawn on the **same shared character template** (one pose,
   one camera position). A hat must sit correctly on *every* species without moving it.
   The artist should first deliver the template (body pose + head position) for approval.
3. **One pose for all species.** Species differ by head, ears, face shape, texture and tail —
   not by pose — so every clothing item fits every species. If a species truly needs a
   different fit, tell us early: each extra fit multiplies the work.
4. **Body colour is applied by the generator.** For each species deliver two files:
   - `Name.fill.png` — the body **fill only**, painted in **light neutral grey** with the artist's
     shading (light areas near white, shadows darker grey). The generator multiplies this by the
     Color trait, so shading is preserved.
   - `Name.png` — line art, eyes-sockets, fur detail, highlights: everything that should NOT be tinted.
5. **Parts that go behind the body** (wings, tail, cape back, backpack straps behind) use an extra
   file with `.back` in the name, e.g. `Wings.back.png`. Optional — only where needed.
6. **Patterns** (`layers/pattern/`) are drawn over the whole body area; the generator clips them to
   the body automatically. Use transparency so the body colour shows through.
7. **File names must match the trait names below exactly** (case and spaces included).
8. **Deliver the editable source files** too (PSD / Procreate / CLIP), with layers named.
9. **No text, signatures or watermarks** in the layers.

## Originality and rights (required before payment in full)
- All work must be **original**. No copying or close imitation of other NFT collections, brands,
  characters or artists' styles; no traced or stock material.
- **AI tools:** tell us in writing whether any AI tools were used, which ones, and for which files.
  Undisclosed AI use is a breach (AI-generated material may not be protectable by copyright and
  can cause community backlash).
- A **signed agreement assigning all rights** in the delivered artwork to the project owner
  (Deven Dauphinais) is required — template in docs/OWNERSHIP_AND_RIGHTS.md, to be reviewed by
  a lawyer.

## Body colours (applied by the generator — nothing to draw)
Blue (#5BA8F5), Pink (#F59AC5), Purple (#A07BE8), Green (#7CCB6A), Yellow (#F6D45A), Orange (#F5A04F), Teal (#3FC1B0), Beige (#E8D2B0), Red (#E8574F), Mint (#A6E8C8), Lavender (#C9B8F2), Brown (#9C6B4A), Gray (#9AA0AA), White (#F4F2EE), Black (#2E2A36), Rainbow (#FFFFFF). "Rainbow" uses a soft multicolour gradient.

## Complete file list (120 traits)
Rarity tiers are proposals and do not change what is drawn.

### Background — folder `layers/background/` (10 traits)

| Trait | Proposed rarity | File(s) |
|---|---|---|
| Forest | Common | `Forest.png` |
| Beach | Common | `Beach.png` |
| City | Common | `City.png` |
| Pastel | Common | `Pastel.png` |
| Desert | Common | `Desert.png` |
| Sunset | Uncommon | `Sunset.png` |
| Snow | Uncommon | `Snow.png` |
| Night | Rare | `Night.png` |
| Rainbow | Rare | `Rainbow.png` |
| Space | Epic | `Space.png` |

### Species — folder `layers/species/` (18 traits)

| Trait | Proposed rarity | File(s) |
|---|---|---|
| Fuzzy | Common | `Fuzzy.png` + `Fuzzy.fill.png` |
| Slime | Common | `Slime.png` + `Slime.fill.png` |
| Bear | Common | `Bear.png` + `Bear.fill.png` |
| Cat | Common | `Cat.png` + `Cat.fill.png` |
| Dog | Common | `Dog.png` + `Dog.fill.png` |
| Bunny | Common | `Bunny.png` + `Bunny.fill.png` |
| Plant | Uncommon | `Plant.png` + `Plant.fill.png` |
| Bird | Uncommon | `Bird.png` + `Bird.fill.png` |
| Fox | Uncommon | `Fox.png` + `Fox.fill.png` |
| Bug | Uncommon | `Bug.png` + `Bug.fill.png` |
| Axolotl | Uncommon | `Axolotl.png` + `Axolotl.fill.png` |
| Mushroom | Rare | `Mushroom.png` + `Mushroom.fill.png` |
| Rock | Rare | `Rock.png` + `Rock.fill.png` |
| Reptile | Rare | `Reptile.png` + `Reptile.fill.png` |
| Monster | Rare | `Monster.png` + `Monster.fill.png` |
| Ghost | Epic | `Ghost.png` + `Ghost.fill.png` |
| Robot | Epic | `Robot.png` + `Robot.fill.png` |
| Alien | Legendary | `Alien.png` + `Alien.fill.png` |

### Pattern — folder `layers/pattern/` (11 traits)

| Trait | Proposed rarity | File(s) |
|---|---|---|
| Spots | Common | `Spots.png` |
| Stripes | Common | `Stripes.png` |
| Swirls | Uncommon | `Swirls.png` |
| Checks | Uncommon | `Checks.png` |
| Leaves | Uncommon | `Leaves.png` |
| Stars | Rare | `Stars.png` |
| Camouflage | Rare | `Camouflage.png` |
| Geo | Rare | `Geo.png` |
| Tie-dye | Epic | `Tie-dye.png` |
| Hearts | Epic | `Hearts.png` |
| Flames | Legendary | `Flames.png` |

### Eyes — folder `layers/eyes/` (13 traits)

| Trait | Proposed rarity | File(s) |
|---|---|---|
| Normal | Common | `Normal.png` |
| Sleepy | Common | `Sleepy.png` |
| Bored | Common | `Bored.png` |
| Side-Eye | Common | `Side-Eye.png` |
| Wink | Common | `Wink.png` |
| Angry | Uncommon | `Angry.png` |
| Teary | Uncommon | `Teary.png` |
| Spiral | Uncommon | `Spiral.png` |
| X Eyes | Rare | `X Eyes.png` |
| Heart | Rare | `Heart.png` |
| Star | Epic | `Star.png` |
| Goggles | Epic | `Goggles.png` |
| Galaxy | Legendary | `Galaxy.png` |

### Mouth — folder `layers/mouth/` (10 traits)

| Trait | Proposed rarity | File(s) |
|---|---|---|
| Smile | Common | `Smile.png` |
| Grin | Common | `Grin.png` |
| Sad | Common | `Sad.png` |
| Open | Common | `Open.png` |
| Tongue | Uncommon | `Tongue.png` |
| Surprised | Uncommon | `Surprised.png` |
| Toothy | Uncommon | `Toothy.png` |
| Fangs | Rare | `Fangs.png` |
| Gold Tooth | Epic | `Gold Tooth.png` |
| Diamond Grin | Legendary | `Diamond Grin.png` |

### Clothing — folder `layers/clothing/` (16 traits)

| Trait | Proposed rarity | File(s) |
|---|---|---|
| T-shirt | Common | `T-shirt.png` |
| Hoodie | Common | `Hoodie.png` |
| Sweater | Common | `Sweater.png` |
| Shirt | Common | `Shirt.png` |
| Overalls | Uncommon | `Overalls.png` |
| Jacket | Uncommon | `Jacket.png` |
| Denim Jacket | Uncommon | `Denim Jacket.png` |
| Raincoat | Uncommon | `Raincoat.png` |
| Tracksuit | Uncommon | `Tracksuit.png` |
| Coat | Rare | `Coat.png` |
| Varsity Jacket | Rare | `Varsity Jacket.png` |
| Puffer Vest | Rare | `Puffer Vest.png` |
| Suit | Rare | `Suit.png` |
| Robe | Epic | `Robe.png` |
| Astronaut Suit | Epic | `Astronaut Suit.png` |
| Cape | Legendary | `Cape.png` |

### Accessory — folder `layers/accessory/` (16 traits)

| Trait | Proposed rarity | File(s) |
|---|---|---|
| Bag | Common | `Bag.png` |
| Scarf | Common | `Scarf.png` |
| Glasses | Common | `Glasses.png` |
| Bandage | Common | `Bandage.png` |
| Backpack | Uncommon | `Backpack.png` |
| Headphones | Uncommon | `Headphones.png` |
| Drink | Uncommon | `Drink.png` |
| Flower | Uncommon | `Flower.png` |
| Watch | Rare | `Watch.png` |
| Necklace | Rare | `Necklace.png` |
| Camera | Rare | `Camera.png` |
| Skateboard | Rare | `Skateboard.png` |
| Earring | Rare | `Earring.png` |
| Ring | Epic | `Ring.png` |
| Gold Chain | Epic | `Gold Chain.png` |
| Treasure Map | Legendary | `Treasure Map.png` |

### Headwear — folder `layers/headwear/` (14 traits)

| Trait | Proposed rarity | File(s) |
|---|---|---|
| Beanie | Common | `Beanie.png` |
| Cap | Common | `Cap.png` |
| Bucket | Common | `Bucket.png` |
| Headband | Common | `Headband.png` |
| Hat | Uncommon | `Hat.png` |
| Hood | Uncommon | `Hood.png` |
| Cowboy | Uncommon | `Cowboy.png` |
| Flower Crown | Uncommon | `Flower Crown.png` |
| Helmet | Rare | `Helmet.png` |
| Wizard | Rare | `Wizard.png` |
| Chef Hat | Rare | `Chef Hat.png` |
| Pilot Cap | Rare | `Pilot Cap.png` |
| Space Helmet | Epic | `Space Helmet.png` |
| Crown | Legendary | `Crown.png` |

### Special — folder `layers/special/` (12 traits)

| Trait | Proposed rarity | File(s) |
|---|---|---|
| Antenna | Common | `Antenna.png` |
| Sparkles | Common | `Sparkles.png` |
| Tail | Uncommon | `Tail.png` |
| Little Buddy | Uncommon | `Little Buddy.png` |
| Rain Cloud | Uncommon | `Rain Cloud.png` |
| Horns | Rare | `Horns.png` |
| Third Eye | Rare | `Third Eye.png` |
| Wings | Epic | `Wings.png` |
| Fire Aura | Epic | `Fire Aura.png` |
| Ice Aura | Epic | `Ice Aura.png` |
| Glow | Legendary | `Glow.png` |
| Halo | Legendary | `Halo.png` |

## How we check delivery
Run `python generate.py assets` in the `art` folder. It lists every delivered and missing file.
Wrong sizes are rejected automatically. Then `python generate.py samples` renders real samples for
the founder's approval **before** the full 10,000 are generated.

## Suggested delivery order
1. Template + 2 species (fill + lines) + 3 backgrounds → we test end-to-end.
2. All species → 3. Eyes and mouths → 4. Clothing, headwear, accessories → 5. Specials and patterns.
