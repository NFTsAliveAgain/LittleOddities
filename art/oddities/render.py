"""Composes all trait layers into one finished Little Oddity portrait."""
from __future__ import annotations

import hashlib
import random

from PIL import Image, ImageChops, ImageFilter, ImageStat

from . import oddity as O
from .paint import Painter

LAYER_ORDER = ["background", "studio light", "antenna", "shoulders + ears", "clothing", "head", "markings", "eyes",
               "eyewear", "mouth", "accessory", "headwear", "grain"]


def dna_of(traits: dict, order) -> str:
    return "|".join(f"{k}={traits[k]}" for k in order)


def _seed(dna: str, salt: str) -> int:
    return int(hashlib.sha256((salt + dna).encode()).hexdigest()[:16], 16)


def render(traits: dict, skin_info: dict, order, size: int = 2048, out_size: int = 1024):
    """Render one character. The image is a pure function of its traits:
    identical traits always give an identical image (including the hand-drawn
    line wobble, which is seeded from the traits)."""
    dna = dna_of(traits, order)
    Painter.set_style(_seed(dna, "pen"))
    bg, ch = Painter(size), Painter(size)
    ctx = O.Ctx(ch, bg, skin_info, traits, random.Random(_seed(dna, "detail")))

    O.background(ctx, traits["background"])
    light_background(bg)
    if traits["headwear"] not in O.HIDES_ANTENNA:
        O.draw_antenna(ctx)
    O.draw_base(ctx)
    O.clothing(ctx, traits["clothing"])
    O.draw_head(ctx)
    O.markings(ctx, traits["markings"])
    O.eyes(ctx, traits["eyes"])
    O.eyewear(ctx, traits["eyewear"])
    O.mouth(ctx, traits["mouth"])
    O.accessory(ctx, traits["accessory"])
    O.headwear(ctx, traits["headwear"])

    qa = quality_check(bg, ch, ctx)
    bg.img.alpha_composite(ch.img)
    img = grain(bg.final(out_size).convert("RGB"), _seed(dna, "grain"))
    return img, qa


def light_background(bg: Painter):
    """Studio lighting: glow behind the head, darker corners, paper texture."""
    glow = bg.m_ellipse(500, 470, 420).filter(ImageFilter.GaussianBlur(120 * bg.s))
    bg.fill_mask(glow, (255, 250, 235), alpha=90)
    vign = ImageChops.invert(bg.m_ellipse(500, 520, 700).filter(ImageFilter.GaussianBlur(160 * bg.s)))
    bg.fill_mask(vign, (42, 30, 58), alpha=85)
    bg.fill_mask(bg.pressure().point(lambda v: max(0, v - 150) * 2), (255, 255, 255), alpha=35)


def grain(img: Image.Image, seed: int) -> Image.Image:
    """Subtle print-style grain so the art feels less digital-flat."""
    random.seed(seed)
    noise = Image.effect_noise(img.size, 22).convert("RGB")
    return Image.blend(img, ImageChops.soft_light(img, noise), 0.5)


def quality_check(bg: Painter, ch: Painter, ctx) -> dict:
    """Automatic visual checks. Problems are reported, never hidden."""
    issues = []
    solid = ch.img.getchannel("A").point(lambda v: 255 if v > 200 else 0)
    bbox = solid.getbbox()
    if bbox is None:
        return {"ok": False, "issues": ["character layer is empty"]}
    if bbox[1] < int(ch.size * 0.012):
        issues.append(f"headwear/character touches the top edge (bbox {bbox})")
    body_rgb = ImageStat.Stat(ch.img.convert("RGB"), ctx.head_mask).mean
    bg_rgb = ImageStat.Stat(bg.img.convert("RGB"), ctx.head_mask).mean
    dist = sum((a - b) ** 2 for a, b in zip(body_rgb, bg_rgb)) ** 0.5
    if dist < 45:
        issues.append(f"low skin/background contrast ({dist:.0f})")
    return {"ok": not issues, "issues": issues, "contrast": round(dist, 1)}
