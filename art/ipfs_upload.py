#!/usr/bin/env python3
"""IPFS upload + verification for Little Oddities (Pinata).

Reproducible, three-step workflow. Each step records results in output/ipfs/ipfs_record.json.

  0) python ipfs_upload.py hidden      uploads the mystery image + hidden.json -> UNREVEALED_URI (before deploy)
  1) python ipfs_upload.py images      uploads output/collection/images/ as ONE folder -> IMAGES_CID
     (images are named by planned character number; which token gets which is unknown until reveal)
  2) python ipfs_upload.py metadata --starting-index N
                                       AFTER the on-chain reveal: token T gets character ((T-1+N) % 10000)+1;
                                       writes per-token metadata with the real IMAGES_CID, uploads -> METADATA_CID
  3) python ipfs_upload.py verify      fetches a sample (or --all) from a gateway and checks every file

  python ipfs_upload.py check          offline: validates folders & metadata before spending anything

Needs PINATA_JWT in your environment (Pinata dashboard -> API Keys). Never commit it.
Nothing here invents CIDs: a CID is only recorded after Pinata returns it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COL = ROOT / "output" / "collection"
IPFS_DIR = ROOT / "output" / "ipfs"
RECORD = IPFS_DIR / "ipfs_record.json"
PIN_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"
GATEWAY = os.environ.get("IPFS_GATEWAY", "https://gateway.pinata.cloud/ipfs/")
SUPPLY = 10_000
PLACEHOLDER = "__IMAGES_CID__"


def load_record() -> dict:
    return json.loads(RECORD.read_text()) if RECORD.exists() else {}


def save_record(rec: dict):
    IPFS_DIR.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(rec, indent=2))


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check(require_placeholder=True) -> list:
    """Offline pre-flight checks. Returns a list of problems (empty = ready)."""
    problems = []
    imgs, metas = COL / "images", COL / "metadata"
    for i in range(1, SUPPLY + 1):
        if not (imgs / f"{i}.png").exists():
            problems.append(f"missing image {i}.png")
        mp = metas / f"{i}.json"
        if not mp.exists():
            problems.append(f"missing metadata {i}.json")
            continue
        m = json.loads(mp.read_text())
        if require_placeholder and m.get("image") != f"ipfs://{PLACEHOLDER}/{i}.png":
            problems.append(f"{i}.json image field unexpected: {m.get('image')}")
        if len(problems) > 50:
            problems.append("... stopping after 50 problems")
            break
    extra = [p.name for p in imgs.glob("*") if p.suffix == ".png" and not p.stem.isdigit()] if imgs.exists() else []
    problems += [f"unexpected file in images folder: {n}" for n in extra]
    report = COL / "validation_report.json"
    if not report.exists() or not json.loads(report.read_text()).get("ok"):
        problems.append("collection validation has not passed (run: python generate.py validate)")
    qa = COL / "qa_report.json"
    if qa.exists() and any(v.get("placeholder") for v in json.loads(qa.read_text()).values()):
        problems.append("collection contains PLACEHOLDER images — real artist layers are required before upload")
    return problems


def pin_folder(folder: Path, name: str, jwt: str) -> str:
    """Upload a whole folder so files are addressable as <CID>/<file>."""
    import requests

    files = sorted(p for p in folder.iterdir() if p.is_file() and not p.name.startswith("."))
    handles = [("file", (f"{name}/{p.name}", open(p, "rb"))) for p in files]
    try:
        r = requests.post(PIN_URL, headers={"Authorization": f"Bearer {jwt}"}, files=handles,
                          data={"pinataMetadata": json.dumps({"name": name}),
                                "pinataOptions": json.dumps({"cidVersion": 1, "wrapWithDirectory": False})},
                          timeout=3600)
    finally:
        for _, (_, fh) in handles:
            fh.close()
    if r.status_code != 200:
        raise RuntimeError(f"Pinata error {r.status_code}: {r.text[:500]}")
    cid = r.json()["IpfsHash"]
    return cid


def character_for(token_id: int, starting_index: int) -> int:
    """Same formula as the contract's characterOf()."""
    return ((token_id - 1 + starting_index) % SUPPLY) + 1


def write_final_metadata(images_cid: str, starting_index: int) -> Path:
    if not 0 < starting_index < SUPPLY:
        raise ValueError("starting index must come from the contract (1..9999)")
    out = IPFS_DIR / "metadata"
    out.mkdir(parents=True, exist_ok=True)
    for t in range(1, SUPPLY + 1):
        c = character_for(t, starting_index)
        m = json.loads((COL / "metadata" / f"{c}.json").read_text())
        m["name"] = m["name"].replace(f"#{c}:", f"#{t}:", 1)
        m["image"] = f"ipfs://{images_cid}/{c}.png"
        if "external_url" in m:
            m["external_url"] = m["external_url"].rsplit("/", 1)[0] + f"/{t}"
        m["attributes"] = m["attributes"] + [{"trait_type": "Character No.", "value": c, "display_type": "number"}]
        # contract tokenURI = baseURI + tokenId + ".json"
        (out / f"{t}.json").write_text(json.dumps(m, ensure_ascii=False))
    return out


def cmd_images(args):
    jwt = os.environ.get("PINATA_JWT") or sys.exit("Set PINATA_JWT first (see docs/IPFS_GUIDE.md).")
    probs = check()
    if probs and not args.force_test:
        sys.exit("Pre-flight failed:\n  " + "\n  ".join(probs[:30]))
    cid = pin_folder(COL / "images", "little-oddities-images", jwt)
    rec = load_record()
    rec["images"] = {"cid": cid, "uploaded_at": datetime.now(timezone.utc).isoformat(), "count": SUPPLY,
                     "sample_sha256": {str(i): sha256(COL / "images" / f"{i}.png") for i in (1, 500, 5000, 10000)}}
    save_record(rec)
    print(f"Images pinned. IMAGES_CID = {cid}\nNext: python ipfs_upload.py metadata")


def cmd_metadata(args):
    jwt = os.environ.get("PINATA_JWT") or sys.exit("Set PINATA_JWT first.")
    rec = load_record()
    if "images" not in rec:
        sys.exit("Upload images first (python ipfs_upload.py images).")
    if args.starting_index is None:
        sys.exit("Pass --starting-index N, read from the contract after finalizeReveal (startingIndex()).")
    folder = write_final_metadata(rec["images"]["cid"], args.starting_index)
    cid = pin_folder(folder, "little-oddities-metadata", jwt)
    rec["metadata"] = {"cid": cid, "uploaded_at": datetime.now(timezone.utc).isoformat(), "base_uri": f"ipfs://{cid}/",
                       "starting_index": args.starting_index}
    save_record(rec)
    print(f"Metadata pinned. METADATA_CID = {cid}\nOwner then calls reveal(\"ipfs://{cid}/\")\nNext: python ipfs_upload.py verify")


def cmd_hidden(args):
    """Mystery image + metadata shown for every token until reveal."""
    jwt = os.environ.get("PINATA_JWT") or sys.exit("Set PINATA_JWT first.")
    src = ROOT.parent / "brand" / "reveal" / "hidden.png"
    if not src.exists():
        sys.exit("brand/reveal/hidden.png missing (run: node brand/build_graphics.js)")
    img_dir = IPFS_DIR / "hidden_image"
    img_dir.mkdir(parents=True, exist_ok=True)
    (img_dir / "hidden.png").write_bytes(src.read_bytes())
    img_cid = pin_folder(img_dir, "little-oddities-hidden-image", jwt)
    meta_dir = IPFS_DIR / "hidden_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    (meta_dir / "hidden.json").write_text(json.dumps({
        "name": "Little Oddities (unrevealed)",
        "description": "A Little Oddity is waiting to wake up. Every token is revealed together after the mint, using on-chain "
                       "randomness, so no one (not even the team) knows in advance which character each token becomes.",
        "image": f"ipfs://{img_cid}/hidden.png",
        "attributes": [{"trait_type": "Status", "value": "Unrevealed"}]}, indent=2))
    meta_cid = pin_folder(meta_dir, "little-oddities-hidden-metadata", jwt)
    rec = load_record()
    rec["hidden"] = {"image_cid": img_cid, "metadata_cid": meta_cid, "unrevealed_uri": f"ipfs://{meta_cid}/hidden.json",
                     "uploaded_at": datetime.now(timezone.utc).isoformat()}
    save_record(rec)
    print(f"UNREVEALED_URI = ipfs://{meta_cid}/hidden.json  (put this in contracts/.env before deploying)")


def cmd_verify(args):
    import requests

    rec = load_record()
    if "metadata" not in rec:
        sys.exit("Nothing uploaded yet.")
    ids = list(range(1, SUPPLY + 1)) if args.all else sorted({1, 2, SUPPLY, *random.sample(range(1, SUPPLY + 1), 40)})
    bad = []
    for i in ids:
        try:
            c = character_for(i, rec["metadata"]["starting_index"])
            m = requests.get(f"{GATEWAY}{rec['metadata']['cid']}/{i}.json", timeout=60).json()
            if m["image"] != f"ipfs://{rec['images']['cid']}/{c}.png" or f"#{i}:" not in m["name"]:
                bad.append(f"{i}: metadata image link or name wrong")
            img = requests.get(f"{GATEWAY}{rec['images']['cid']}/{c}.png", timeout=120)
            if img.status_code != 200 or hashlib.sha256(img.content).hexdigest() != sha256(COL / "images" / f"{c}.png"):
                bad.append(f"{i}: image missing or differs from local file")
        except Exception as e:  # noqa: BLE001 - report every failure honestly
            bad.append(f"{i}: {e}")
        time.sleep(0.2)
    rec["verification"] = {"checked": len(ids), "problems": bad, "at": datetime.now(timezone.utc).isoformat(), "ok": not bad}
    save_record(rec)
    print(f"Verified {len(ids)} tokens via {GATEWAY}. Problems: {len(bad)}")
    for b in bad[:30]:
        print("  -", b)
    sys.exit(0 if not bad else 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["check", "hidden", "images", "metadata", "verify"])
    ap.add_argument("--starting-index", type=int, default=None, help="from the contract after finalizeReveal")
    ap.add_argument("--all", action="store_true", help="verify every token (slow)")
    ap.add_argument("--force-test", action="store_true", help="TEST uploads only: skip pre-flight")
    args = ap.parse_args()
    if args.command == "check":
        probs = check()
        print("Ready to upload." if not probs else "Not ready:\n  " + "\n  ".join(probs[:40]))
        sys.exit(1 if probs else 0)
    {"hidden": cmd_hidden, "images": cmd_images, "metadata": cmd_metadata, "verify": cmd_verify}[args.command](args)


if __name__ == "__main__":
    main()
