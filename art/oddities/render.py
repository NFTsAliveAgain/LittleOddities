"""Composes all trait layers into one finished Little Oddity image."""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field

from PIL import Image, ImageChops, ImageFilter, ImageStat

from . import features, scenes, wearables
from .bodies import Body, build_body, draw_arm, draw_body, draw_feet, draw_ground_shadow
from .paint import Painter, hex_rgb

LAYER_ORDER = [
    "background", "ground shadow", "special (behind)", "clothing (behind)", "feet", "species + skin",
    "pattern", "clothing", "arms", "expression", "eyes", "mouth", "accessory", "headwear", "special",
]


@dataclass
class Ctx:
    P: Painter
    body: Body
    skin_base: tuple
    skin_fill: object
    body_mask: object
    rng: random.Random
    prng: random.Random
    skin_families: tuple = ()
    eyes: list = field(default_factory=list)


def dna_of(traits: dict, order) -> str:
    return "|".join(f"{k}={traits[k]}" for k in order)


def _seed(dna: str, salt: str) -> int:
    return int(hashlib.sha256((salt + dna).encode()).hexdigest()[:16], 16)


def render(traits: dict, skin_info: dict, order, size: int = 2048, out_size: int = 1024, framing: str = "portrait"):
    """Render one character. The image is a pure function of its traits,
    so identical traits always produce an identical image."""
    dna = dna_of(traits, order)
    Painter.set_style(_seed(dna, "pen"))
    bg = Painter(size)
    ch = Painter(size)
    body = build_body(traits["species"])

    base = hex_rgb(skin_info["color"])
    if skin_info.get("gradient"):
        stops = skin_info["gradient"]
        fill = ch.gradient([(i / (len(stops) - 1), hex_rgb(c)) for i, c in enumerate(stops)], 65)
    else:
        fill = base
    ctx = Ctx(bg, body, base, fill, None, random.Random(_seed(dna, "bg")), random.Random(_seed(dna, "pattern")),
              tuple(skin_info.get("families", ())))

    scenes.background(ctx, traits["background"])
    light_background(bg, body)
    if framing == "full":
        draw_ground_shadow(bg, body)

    ctx.P = ch
    scenes.special_back(ctx, traits["special"])
    wearables.clothing_back(ctx, traits["clothing"])
    draw_feet(ch, body, base)
    ctx.body_mask = draw_body(ch, body, fill, base)
    scenes.pattern(ctx, traits["pattern"])
    wearables.clothing(ctx, traits["clothing"])
    draw_arm(ch, body, "l", base)
    draw_arm(ch, body, "r", base)
    features.eyes(ctx, traits["eyes"])  # sets ctx.eyes (needed by brows / glasses)
    features.expression(ctx, traits["expression"])
    features.mouth(ctx, traits["mouth"])
    wearables.accessory(ctx, traits["accessory"])
    wearables.headwear(ctx, traits["headwear"])
    scenes.special(ctx, traits["special"])

    qa = quality_check(bg, ch, ctx, framing)
    if framing == "portrait":
        ch.img = portrait_camera(ch, body)
    bg.img.alpha_composite(ch.img)
    img = bg.final(out_size).convert("RGB")
    img = grain(img, _seed(dna, "grain"))
    return img, qa


def light_background(bg: Painter, body: Body):
    """Studio lighting: warm glow behind the head, darker vignette corners, paper texture."""
    glow = bg.m_ellipse(500, body.face[1] + 40, 420, 420).filter(ImageFilter.GaussianBlur(120 * bg.s))
    bg.fill_mask(glow, (255, 250, 235), alpha=95)
    vign = ImageChops.invert(bg.m_ellipse(500, 520, 700, 700).filter(ImageFilter.GaussianBlur(160 * bg.s)))
    bg.fill_mask(vign, (42, 30, 58), alpha=80)
    bg.fill_mask(bg.pressure().point(lambda v: max(0, v - 150) * 2), (255, 255, 255), alpha=40)


def portrait_camera(ch: Painter, body: Body) -> Image.Image:
    """PFP framing: zoom in so head + shoulders fill the frame, body cropped at the bottom."""
    size = ch.size
    solid = ch.img.getchannel("A").point(lambda v: 255 if v > 200 else 0)
    top_px = solid.getbbox()[1]
    face_px = body.face[1] * ch.s
    target = 0.52 * size
    k = min(1.65, (target - 0.06 * size) / max(1.0, face_px - top_px))
    big = ch.img.resize((int(size * k), int(size * k)), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.alpha_composite(big, dest=(0, 0), source=(int(500 * ch.s * k - size / 2), int(face_px * k - target)))
    return out


def grain(img: Image.Image, seed: int) -> Image.Image:
    """Subtle print-style grain so the art feels less digital-flat."""
    random.seed(seed)
    noise = Image.effect_noise(img.size, 22).convert("RGB")
    return Image.blend(img, ImageChops.soft_light(img, noise), 0.55)


def quality_check(bg: Painter, ch: Painter, ctx: Ctx, framing: str = "portrait") -> dict:
    """Automatic visual checks. Problems are reported, never hidden."""
    issues = []
    alpha = ch.img.getchannel("A")
    bbox = alpha.point(lambda v: 255 if v > 200 else 0).getbbox()  # ignore soft glows
    size = ch.size
    margin = int(size * 0.012)
    if bbox is None:
        issues.append("character layer is empty")
        return {"ok": False, "issues": issues}
    if framing == "full" and (bbox[0] < margin or bbox[2] > size - margin or bbox[3] > size - margin) or bbox[1] < margin:
        issues.append(f"character touches canvas edge (bbox {bbox})")
    coverage = ImageStat.Stat(alpha.point(lambda v: 255 if v > 127 else 0)).mean[0] / 255
    if not 0.10 <= coverage <= 0.72:
        issues.append(f"character coverage {coverage:.2f} outside 0.10-0.72")
    # contrast between skin and the background behind the body
    body_rgb = ImageStat.Stat(ch.img.convert("RGB"), ctx.body_mask).mean
    bg_rgb = ImageStat.Stat(bg.img.convert("RGB"), ctx.body_mask).mean
    dist = sum((a - b) ** 2 for a, b in zip(body_rgb, bg_rgb)) ** 0.5
    if dist < 45:
        issues.append(f"low skin/background contrast ({dist:.0f})")
    return {"ok": not issues, "issues": issues, "coverage": round(coverage, 3), "contrast": round(dist, 1)}
