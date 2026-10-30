#!/usr/bin/env python3
"""Little Oddities generator — command line.

  python generate.py plan                 # plan all 10,000 (no images) + stats
  python generate.py samples --count 30   # render sample characters for review
  python generate.py catalog              # render every trait on a reference character
  python generate.py collection --approved-art   # render all 10,000 (after art approval)
  python generate.py validate             # validate a rendered collection

Everything is reproducible: the same config + seed always gives the same collection.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from oddities.metadata import token_metadata  # noqa: E402
from oddities.planner import load_config, plan_collection, statistics, verify_plan  # noqa: E402
from oddities.layered import asset_status, render_layered  # noqa: E402
from oddities.planner import CONFIG  # noqa: E402
from oddities.validate import validate_folder  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
FONTS = ROOT.parent / "brand" / "fonts"
INK = (42, 30, 58)
CREAM = (255, 246, 230)
TIER_COLORS = {"Common": (120, 130, 150), "Uncommon": (46, 170, 120), "Rare": (60, 120, 230),
               "Epic": (150, 80, 220), "Legendary": (230, 150, 20)}


def font(size, bold=True):
    name = "Fraunces_900Black.ttf" if bold else "DMSans_500Medium.ttf"
    try:
        return ImageFont.truetype(str(FONTS / name), size)
    except OSError:
        return ImageFont.load_default()


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def render_token(traits, cfg, out_size=1024):
    """Artist layers (default) or the archived procedural engine (config 'engine')."""
    if cfg.get("engine") == "layered":
        return render_layered(traits, cfg, out_size)
    from oddities.render import render
    return render(traits, cfg["value"][("skin", traits["skin"])], cfg["order"], out_size=out_size)


def _render_one(args):
    token, cfg, out_dir = args
    img, qa = render_token(token["traits"], cfg)
    img.save(Path(out_dir) / "images" / f"{token['id']}.png", optimize=True)
    return token["id"], qa


def contact_sheet(items, path: Path, cols=5, cell=360, title="Little Oddities"):
    """items = [(PIL image, line1, line2, tier)]"""
    rows = (len(items) + cols - 1) // cols
    pad, label = 24, 70
    W = cols * (cell + pad) + pad
    Hh = 120 + rows * (cell + label + pad) + pad
    sheet = Image.new("RGB", (W, Hh), CREAM)
    d = ImageDraw.Draw(sheet)
    d.text((pad, 34), title, font=font(52), fill=INK)
    for i, (img, l1, l2, tier) in enumerate(items):
        x = pad + (i % cols) * (cell + pad)
        y = 120 + (i // cols) * (cell + label + pad)
        d.rounded_rectangle([x - 4, y - 4, x + cell + 4, y + cell + label], 18, fill=(255, 255, 255), outline=INK, width=4)
        sheet.paste(img.resize((cell, cell), Image.LANCZOS), (x, y))
        d.text((x + 12, y + cell + 8), l1, font=font(22), fill=INK)
        d.text((x + 12, y + cell + 38), l2, font=font(17, bold=False), fill=TIER_COLORS.get(tier, INK))
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, optimize=True)


def cmd_plan(cfg, args):
    t = time.time()
    tokens = plan_collection(cfg, args.seed)
    problems = verify_plan(tokens, cfg)
    stats = statistics(tokens, cfg)
    write_json(OUT / "plan" / "plan.json", tokens)
    write_json(OUT / "plan" / "trait_statistics.json", stats)
    print(f"Planned {len(tokens)} tokens in {time.time() - t:.1f}s")
    print("Tier counts:", stats["tiers"])
    print("Plan problems:", problems or "none")
    return tokens, problems


def cmd_samples(cfg, args):
    tokens = plan_collection(cfg, args.seed)
    want = {"Common": 0.34, "Uncommon": 0.24, "Rare": 0.2, "Epic": 0.12, "Legendary": 0.1}
    picks = []
    for tier, frac in want.items():
        picks += [t for t in tokens if t["tier"] == tier][: max(1, round(args.count * frac))]
    picks = picks[: args.count]
    out = OUT / "samples"
    (out / "images").mkdir(parents=True, exist_ok=True)
    items, report = [], []
    for t in picks:
        img, qa = render_token(t["traits"], cfg)
        img.save(out / "images" / f"{t['id']}.png", optimize=True)
        write_json(out / "metadata" / f"{t['id']}.json", token_metadata(t, cfg))
        items.append((img, f"#{t['id']} {t['name']}", f"{t['tier']}", t["tier"]))
        report.append({"id": t["id"], "tier": t["tier"], "qa": qa})
        print(f"  #{t['id']:>5} {t['tier']:<9} {t['name']:<28} QA: {'ok' if qa['ok'] else qa['issues']}")
    contact_sheet(items, out / "sample_sheet.png", title="Little Oddities - Sample Characters (for approval)")
    write_json(out / "qa_report.json", report)
    print(f"Wrote {len(picks)} samples to {out}")


REFERENCE = {"background": "Periwinkle", "skin": "Moss", "ears": "Pointy", "markings": "None", "clothing": "Hoodie",
             "eyes": "Bored", "eyewear": "None", "mouth": "Smirk", "accessory": "None", "headwear": "None"}


def cmd_catalog(cfg, args):
    """One sheet per category showing every trait value on a reference character (procedural engine)."""
    if cfg.get("engine") == "layered":
        sys.exit("Catalog sheets for artist layers come from the artist. Use --config config/procedural_traits.json for the code-drawn set.")
    out = OUT / "catalog"
    for c in cfg["categories"]:
        items = []
        for v in c["values"]:
            traits = dict(REFERENCE)
            traits[c["key"]] = v["name"]
            if c["key"] == "background":
                fams = set(v.get("families", []))
                traits["skin"] = next(k for k in ("Moss", "Rose", "Sand", "Sky") if not fams & set(cfg["value"][("skin", k)]["families"]))
            if c["key"] == "skin" and set(v["families"]) & set(cfg["value"][("background", "Periwinkle")]["families"]):
                traits["background"] = "Butter"
            if c["key"] == "eyewear" and v["name"] != "None":
                traits["eyes"] = "Unimpressed"
            img, qa = render(traits, cfg["value"][("skin", traits["skin"])], cfg["order"], size=1400, out_size=700)
            items.append((img, v["name"], v["tier"], v["tier"]))
        contact_sheet(items, out / f"{c['key']}.png", cols=6, cell=260, title=f"Trait catalog - {c['label']} ({len(items)})")
        print(f"  catalog: {c['label']} ({len(items)} values)")
    print(f"Wrote catalog sheets to {out}")


def cmd_collection(cfg, args):
    if not args.approved_art:
        sys.exit("Refusing to render the full collection until the founder has approved the sample art.\n"
                 "Re-run with --approved-art once approval is recorded in docs/ARTWORK_GUIDE.md.")
    tokens, problems = cmd_plan(cfg, args)
    if problems:
        sys.exit("Plan has problems; fix them before rendering.")
    out = OUT / "collection"
    (out / "images").mkdir(parents=True, exist_ok=True)
    for t in tokens:
        write_json(out / "metadata" / f"{t['id']}.json", token_metadata(t, cfg))
    if cfg.get("engine") == "layered" and asset_status(cfg)["missing"] and not args.allow_placeholders:
        sys.exit("Artist layers are missing (run: python generate.py assets). Use --allow-placeholders only for TEST builds.")
    jobs = [(t, cfg, str(out)) for t in tokens
            if args.force or not (out / "images" / f"{t['id']}.png").exists()]
    qa = {}
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for i, (tid, q) in enumerate(ex.map(_render_one, jobs, chunksize=8), 1):
            qa[tid] = q
            if i % 250 == 0:
                print(f"  rendered {i}/{len(jobs)}  ({time.time() - t0:.0f}s)")
    write_json(out / "qa_report.json", {str(k): v for k, v in sorted(qa.items())})
    write_json(out / "trait_statistics.json", statistics(tokens, cfg))
    print(f"Rendered {len(jobs)} images. QA flags: {sum(1 for q in qa.values() if not q['ok'])}")


def cmd_assets(cfg, args):
    st = asset_status(cfg)
    write_json(OUT / "asset_status.json", st)
    print(f"Artist layer files delivered: {st['delivered']} / {st['required']}")
    for m in st["missing"][:40]:
        print("  missing:", m)
    if len(st["missing"]) > 40:
        print(f"  ... and {len(st['missing']) - 40} more (full list in output/asset_status.json)")


def cmd_validate(cfg, args):
    out = OUT / args.folder
    ids = list(range(1, cfg["collection"]["supply"] + 1)) if args.folder == "collection" else \
        sorted(int(p.stem) for p in (out / "images").glob("*.png"))
    res = validate_folder(out, ids, cfg)
    write_json(out / "validation_report.json", res)
    print(f"Checked {res['checked']} tokens. Problems: {len(res['problems'])}")
    for p in res["problems"][:30]:
        print("  -", p)
    print("Rarity counts:", res["tier_counts"])
    sys.exit(0 if res["ok"] else 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["plan", "samples", "catalog", "collection", "validate", "assets"])
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--count", type=int, default=30)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--approved-art", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--folder", default="collection")
    ap.add_argument("--allow-placeholders", action="store_true", help="TEST builds only")
    ap.add_argument("--config", default=str(CONFIG))
    args = ap.parse_args()
    cfg = load_config(args.config)
    {"plan": cmd_plan, "samples": cmd_samples, "catalog": cmd_catalog,
     "collection": cmd_collection, "validate": cmd_validate, "assets": cmd_assets}[args.command](cfg, args)


if __name__ == "__main__":
    main()
