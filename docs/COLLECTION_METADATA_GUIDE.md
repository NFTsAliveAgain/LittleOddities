# Collection Metadata Guide

Each token has `<id>.json` (ERC-721 / OpenSea format), e.g.:
```json
{
  "name": "Little Oddities #2: Jojo Muddlewood",
  "description": "Meet Jojo Muddlewood, a uncommon Oddity from Little Oddities, the first collection from NFTs Alive Again. A World of Wonderfully Weird.",
  "image": "ipfs://__IMAGES_CID__/2.png",
  "external_url": "https://example.com/collection/2",
  "attributes": [
    {"trait_type": "Rarity", "value": "Uncommon"},
    {"trait_type": "Background", "value": "Sunset"},
    {"trait_type": "Species", "value": "Cat"}
  ]
}
```
- `__IMAGES_CID__` is a **placeholder**; `ipfs_upload.py metadata` replaces it with the real CID returned by Pinata.
- Before launch, set `collection.external_url_base` in `art/config/traits.json` to your real domain (currently `https://example.com/collection/`).
- Contract `tokenURI(id)` = `baseURI + id + ".json"` → baseURI must be `ipfs://<METADATA_CID>/`.
- Collection-level info for marketplaces: `contractURI()` → a JSON with name, description, image, external_link.
- Attribute order: Rarity, then every category in `traits.json`. "None" values are included so collectors can filter "no headwear".
- Instant reveal: there is no hidden/placeholder metadata on-chain; metadata is final when uploaded.

Reports generated: `output/plan/trait_statistics.json`, `output/collection/qa_report.json`, `output/collection/validation_report.json`.
