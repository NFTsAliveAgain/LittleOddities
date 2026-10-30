"""ERC-721 / OpenSea-compatible metadata.

The image link uses the placeholder __IMAGES_CID__ until the images have
really been uploaded to IPFS. The IPFS upload tool (Phase 5) replaces it with
the real CID it receives. We never invent CIDs.
"""
from __future__ import annotations

CID_PLACEHOLDER = "__IMAGES_CID__"


def token_metadata(token: dict, cfg: dict, images_cid: str = CID_PLACEHOLDER) -> dict:
    col = cfg["collection"]
    attrs = [{"trait_type": "Rarity", "value": token["tier"]}]
    for c in cfg["categories"]:
        attrs.append({"trait_type": c["label"], "value": token["traits"][c["key"]]})
    return {
        "name": f"Little Oddities #{token['id']}: {token['name']}",
        "description": f"Meet {token['name']}, a {token['tier'].lower()} Oddity from Little Oddities, "
                       f"the first collection from NFTs Alive Again. A World of Wonderfully Weird.",
        "image": f"ipfs://{images_cid}/{token['id']}.png",
        "external_url": f"{col['external_url_base']}{token['id']}",
        "attributes": attrs,
    }


def collection_metadata(cfg: dict, image_uri: str = "", external_link: str = "") -> dict:
    """contractURI() JSON used by marketplaces for collection-level info."""
    return {
        "name": cfg["collection"]["name"],
        "description": cfg["collection"]["description"],
        "image": image_uri,
        "external_link": external_link,
    }
