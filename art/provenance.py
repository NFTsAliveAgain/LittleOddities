#!/usr/bin/env python3
"""Provenance fingerprint for the delayed reveal.

  python provenance.py            # computes it from output/collection/images/1..10000.png

provenance hash = SHA-256 of the concatenated SHA-256 hashes of every image, in planned
character order 1..10,000. Publish it (owner: setProvenanceHash) BEFORE any mint. After the
reveal anyone can recompute it from the IPFS images and confirm nothing was swapped.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMGS = ROOT / "output" / "collection" / "images"
OUT = ROOT / "output" / "provenance.json"


def compute(folder: Path = IMGS, supply: int = 10_000) -> dict:
    hashes = []
    for i in range(1, supply + 1):
        p = folder / f"{i}.png"
        if not p.exists():
            raise FileNotFoundError(f"missing {p}")
        hashes.append(hashlib.sha256(p.read_bytes()).hexdigest())
    return {"provenance_hash": hashlib.sha256("".join(hashes).encode()).hexdigest(),
            "method": "sha256(concat(sha256(image_1..image_N)))", "image_hashes": hashes}


if __name__ == "__main__":
    try:
        res = compute()
    except FileNotFoundError as e:
        sys.exit(f"Cannot compute provenance yet: {e}. Generate the final collection first.")
    OUT.write_text(json.dumps(res, indent=1))
    print(f"Provenance hash: {res['provenance_hash']}\nSaved {OUT}\nOwner sets it on-chain with setProvenanceHash BEFORE minting opens.")
