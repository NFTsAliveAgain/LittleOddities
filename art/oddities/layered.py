"""Layer compositor for the artist's hand-drawn trait files.

Files live in art/layers/<category>/ and are named after the trait:

  layers/background/Forest.png
  layers/species/Cat.png            line art + details, drawn ON TOP of the tinted fill
  layers/species/Cat.fill.png       flat light-grey body fill, tinted by the Color trait
  layers/special/Wings.back.png     optional ".back" part, drawn behind the body
  layers/pattern/Spots.png          clipped to the body fill automatically

All files: 2048 x 2048 PNG with transparency, aligned to the shared template.
If a file is missing the token renders as a clearly-labelled PLACEHOLDER card,
so development can continue without ever passing placeholder art off as final.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

LAYERS = Path(__file__).resolve().parent.parent / "layers"
FONTS = Path(__file__).resolve().parent.parent.parent / "brand" / "fonts"
SIZE = 2048


def layer_path(key: str, name: str, part: str = "") -> Path:
    return LAYERS / key / f"{name}{'.' + part if part else ''}.png"


@lru_cache(maxsize=512)
def _load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    im = Image.open(p).convert("RGBA")
    if im.size != (SIZE, SIZE):
        raise ValueError(f"{p} is {im.size}, expected {SIZE}x{SIZE}")
    return im


def required_files(cfg: dict) -> list:
    """Every file the artist must deliver (optional .back parts are not required)."""
    out = []
    for c in cfg["categories"]:
        for v in c["values"]:
            if v["name"] == "None" or (c["key"] == "pattern" and v["name"] == "Solid") or c["key"] == "color":
                continue
            out.append(layer_path(c["key"], v["name"]))
            if c["key"] in cfg.get("colorable", []):
                out.append(layer_path(c["key"], v["name"], "fill"))
    return out


def asset_status(cfg: dict) -> dict:
    files = required_files(cfg)
    have = [f for f in files if f.exists()]
    return {"required": len(files), "delivered": len(have),
            "missing": [str(f.relative_to(LAYERS)) for f in files if not f.exists()]}


def _tint(fill: Image.Image, hexcolor: str, rainbow: bool) -> Image.Image:
    """Multiply the grey fill by the body colour, keeping the artist's shading."""
    if rainbow:
        from .paint import Painter
        color = Painter(SIZE).gradient([(0, (255, 140, 170)), (0.25, (255, 214, 110)), (0.5, (140, 230, 160)),
                                        (0.75, (120, 190, 255)), (1, (190, 150, 255))], 35)
    else:
        h = hexcolor.lstrip("#")
        color = Image.new("RGBA", fill.size, tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    rgb = ImageChops.multiply(fill.convert("RGB"), color.convert("RGB")).convert("RGBA")
    rgb.putalpha(fill.getchannel("A"))
    return rgb


def render_layered(traits: dict, cfg: dict, out_size: int = 1024):
    """Returns (image, qa). qa['placeholder'] is True when any layer is missing."""
    missing = []
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    body_mask = None
    color = cfg["value"][("color", traits["color"])]
    for step in cfg["layer_order"]:
        key, _, part = step.partition(":")
        name = traits.get(key)
        if name is None or name == "None" or (key == "pattern" and name == "Solid") or part == "overlay":
            continue
        if part == "back":
            im = _load(str(layer_path(key, name, "back")))
            if im is not None:
                canvas.alpha_composite(im)
            continue
        if key in cfg.get("colorable", []):
            fill = _load(str(layer_path(key, name, "fill")))
            if fill is None:
                missing.append(str(layer_path(key, name, "fill").relative_to(LAYERS)))
            else:
                canvas.alpha_composite(_tint(fill, color["hex"], traits["color"] == "Rainbow"))
                body_mask = fill.getchannel("A")
        im = _load(str(layer_path(key, name)))
        if im is None:
            missing.append(str(layer_path(key, name).relative_to(LAYERS)))
            continue
        if key == "pattern" and body_mask is not None:
            im = im.copy()
            im.putalpha(ImageChops.multiply(im.getchannel("A"), body_mask))
        canvas.alpha_composite(im)
    if missing:
        return placeholder(traits, cfg, out_size), {"ok": False, "placeholder": True, "issues": [f"missing layer {m}" for m in missing]}
    img = canvas.resize((out_size, out_size), Image.LANCZOS).convert("RGB")
    return img, {"ok": True, "placeholder": False, "issues": []}


def placeholder(traits: dict, cfg: dict, out_size: int = 1024) -> Image.Image:
    """An honest stand-in: plainly says it is not the final artwork."""
    bg = cfg["value"][("color", traits["color"])]["hex"]
    img = Image.new("RGB", (out_size, out_size), "#FFF6E6")
    d = ImageDraw.Draw(img)
    s = out_size / 1024

    def f(size, bold=True):
        try:
            return ImageFont.truetype(str(FONTS / ("Fraunces_900Black.ttf" if bold else "DMSans_500Medium.ttf")), int(size * s))
        except OSError:
            return ImageFont.load_default()

    d.rounded_rectangle([40 * s, 40 * s, 984 * s, 984 * s], radius=48 * s, outline="#2A1E3A", width=int(8 * s))
    sw = bg if traits["color"] != "Rainbow" else "#C9B8F2"
    d.ellipse([382 * s, 110 * s, 642 * s, 370 * s], fill=sw, outline="#2A1E3A", width=int(8 * s))
    d.text((512 * s, 420 * s), traits["species"], font=f(72), fill="#2A1E3A", anchor="mm")
    d.text((512 * s, 480 * s), "PLACEHOLDER - artist layers pending", font=f(26, False), fill="#C2283E", anchor="mm")
    y = 540
    for c in cfg["categories"]:
        if c["key"] == "species":
            continue
        d.text((180 * s, y * s), c["label"], font=f(28, False), fill="#7A6F86")
        d.text((470 * s, y * s), traits[c["key"]], font=f(30), fill="#2A1E3A")
        y += 44
    return img
