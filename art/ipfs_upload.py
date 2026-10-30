#!/usr/bin/env python3
"""IPFS upload + verification for Little Oddities (Pinata).

Reproducible, three-step workflow. Each step records results in output/ipfs/ipfs_record.json.

  1) python ipfs_upload.py images      uploads output/collection/images/ as ONE folder -> IMAGES_CID
  2) python ipfs_upload.py metadata    writes metadata with the real IMAGES_CID, uploads it -> METADATA_CID
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


def write_final_metadata(images_cid: str) -> Path:
    out = IPFS_DIR / "metadata"
    out.mkdir(parents=True, exist_ok=True)
    for i in range(1, SUPPLY + 1):
        m = json.loads((COL / "metadata" / f"{i}.json").read_text())
        m["image"] = m["image"].replace(PLACEHOLDER, images_cid)
        # contract tokenURI = baseURI + id + ".json"
        (out / f"{i}.json").write_text(json.dumps(m, ensure_ascii=False))
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
    folder = write_final_metadata(rec["images"]["cid"])
    cid = pin_folder(folder, "little-oddities-metadata", jwt)
    rec["metadata"] = {"cid": cid, "uploaded_at": datetime.now(timezone.utc).isoformat(), "base_uri": f"ipfs://{cid}/"}
    save_record(rec)
    print(f"Metadata pinned. METADATA_CID = {cid}\nContract BASE_URI = ipfs://{cid}/\nNext: python ipfs_upload.py verify")


def cmd_verify(args):
    import requests

    rec = load_record()
    if "metadata" not in rec:
        sys.exit("Nothing uploaded yet.")
    ids = list(range(1, SUPPLY + 1)) if args.all else sorted({1, 2, SUPPLY, *random.sample(range(1, SUPPLY + 1), 40)})
    bad = []
    for i in ids:
        try:
            m = requests.get(f"{GATEWAY}{rec['metadata']['cid']}/{i}.json", timeout=60).json()
            if m["image"] != f"ipfs://{rec['images']['cid']}/{i}.png":
                bad.append(f"{i}: metadata image link wrong")
            img = requests.get(f"{GATEWAY}{rec['images']['cid']}/{i}.png", timeout=120)
            if img.status_code != 200 or hashlib.sha256(img.content).hexdigest() != sha256(COL / "images" / f"{i}.png"):
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
    ap.add_argument("command", choices=["check", "images", "metadata", "verify"])
    ap.add_argument("--all", action="store_true", help="verify every token (slow)")
    ap.add_argument("--force-test", action="store_true", help="TEST uploads only: skip pre-flight")
    args = ap.parse_args()
    if args.command == "check":
        probs = check()
        print("Ready to upload." if not probs else "Not ready:\n  " + "\n  ".join(probs[:40]))
        sys.exit(1 if probs else 0)
    {"images": cmd_images, "metadata": cmd_metadata, "verify": cmd_verify}[args.command](args)


if __name__ == "__main__":
    main()
