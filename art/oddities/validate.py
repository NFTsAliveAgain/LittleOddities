"""Validates generated images + metadata files. Reports problems honestly."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageStat


def dhash(img: Image.Image, size: int = 16) -> int:
    g = img.convert("L").resize((size + 1, size), Image.LANCZOS)
    px = list(g.getdata())
    bits = 0
    for r in range(size):
        for c in range(size):
            bits = (bits << 1) | (px[r * (size + 1) + c] > px[r * (size + 1) + c + 1])
    return bits


def validate_folder(out_dir: Path, expected_ids, cfg: dict, expected_size=1024) -> dict:
    img_dir, meta_dir = out_dir / "images", out_dir / "metadata"
    problems, sha_seen, dh_seen = [], {}, {}
    tier_counts = {}
    for tid in expected_ids:
        ip, mp = img_dir / f"{tid}.png", meta_dir / f"{tid}.json"
        if not ip.exists():
            problems.append(f"{tid}: image missing"); continue
        if not mp.exists():
            problems.append(f"{tid}: metadata missing"); continue
        raw = ip.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if sha in sha_seen:
            problems.append(f"{tid}: identical image to token {sha_seen[sha]}")
        sha_seen[sha] = tid
        with Image.open(ip) as im:
            if im.size != (expected_size, expected_size):
                problems.append(f"{tid}: size {im.size}")
            if im.mode not in ("RGB", "RGBA"):
                problems.append(f"{tid}: mode {im.mode}")
            if max(ImageStat.Stat(im.convert("L")).stddev) < 8:
                problems.append(f"{tid}: image looks blank")
            h = dhash(im)
        if h in dh_seen:
            problems.append(f"{tid}: perceptual near-duplicate of token {dh_seen[h]} (review)")
        dh_seen[h] = tid
        try:
            meta = json.loads(mp.read_text())
        except json.JSONDecodeError as e:
            problems.append(f"{tid}: invalid JSON ({e})"); continue
        for key in ("name", "description", "image", "attributes"):
            if key not in meta:
                problems.append(f"{tid}: metadata missing '{key}'")
        if not str(meta.get("image", "")).endswith(f"/{tid}.png"):
            problems.append(f"{tid}: image URI does not point at {tid}.png")
        types = [a.get("trait_type") for a in meta.get("attributes", [])]
        need = ["Rarity"] + [c["label"] for c in cfg["categories"]]
        if types != need:
            problems.append(f"{tid}: attributes {types} != {need}")
        rar = next((a["value"] for a in meta.get("attributes", []) if a.get("trait_type") == "Rarity"), None)
        tier_counts[rar] = tier_counts.get(rar, 0) + 1
    return {"checked": len(list(expected_ids)), "problems": problems, "tier_counts": tier_counts, "ok": not problems}
