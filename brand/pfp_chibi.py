#!/usr/bin/env python3
"""Chibi-style X/Twitter profile picture options, in the direction of the artist's concept sheets
(cute critters, big glossy eyes, thick ink outlines, soft painted shading, dreamy backgrounds).
Original drawings made in code with the art engine — placeholders until the artist draws the final PFP.

  python3 brand/pfp_chibi.py      -> brand/social/x-pfp-chibi-*.png + preview
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "art"))
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402
from oddities.paint import INK, WHITE, Painter, cubic, ellipse_pts, hex_rgb as H, quad, shade, star_pts, tint  # noqa: E402

OUT = HERE / "social"


def sky(P, top, bottom, sparkle=WHITE):
    P.fill_mask(P.m_rect(0, 0, 1000, 1000), P.gradient([(0, H(top)), (1, H(bottom))], 90))
    for x, y, r, a in ((150, 200, 90, 70), (860, 260, 120, 55), (800, 820, 140, 45), (120, 760, 110, 50)):
        P.glow(P.m_ellipse(x, y, r), WHITE, 40, alpha=a)
    for x, y, s in ((210, 150, 18), (820, 140, 14), (900, 520, 12), (90, 470, 13), (760, 700, 10)):
        P.poly(star_pts(x, y, s, s * 0.35, 4), H(sparkle) if isinstance(sparkle, str) else sparkle, outline=0, alpha=230)


def body_paint(P, mask, base, light_dx=-40):
    """Soft painted volume: base fill, gentle form shadow, rim light, big soft highlight."""
    P.shape(mask, P.gradient([(0, tint(base, 0.18)), (1, shade(base, 0.86))], 90), outline=16)
    P.fill_mask(P.subtract(mask, P.shift(mask, -46, -38)).filter(ImageFilter.GaussianBlur(14 * P.s)), shade(base, 0.7), alpha=120)
    P.fill_mask(P.subtract(mask, P.shift(mask, -8, -6)), tint(base, 0.45), alpha=120)


def big_eye(P, x, y, sleepy=0.0, lid=None, r=1.0):
    rx, ry = 64 * r, 80 * r
    m = P.m_ellipse(x, y, rx, ry)
    P.shape(m, P.gradient([(0, H("#2a2140")), (0.7, H("#3b2f63")), (1, H("#6a4fb0"))], 90), outline=10)
    P.fill_mask(P.intersect(P.m_ellipse(x, y + ry * 0.55, rx * 0.8, ry * 0.35), m), H("#8a6fe0"), alpha=110)
    P.ellipse(x - rx * 0.32, y - ry * 0.34, rx * 0.36, ry * 0.32, fill=WHITE, outline=0)
    P.ellipse(x + rx * 0.36, y + ry * 0.3, rx * 0.15, fill=WHITE, outline=0, alpha=230)
    if sleepy:
        cut = y - ry + 2 * ry * sleepy
        lm = P.intersect(P.m_ellipse(x, y, rx + 2, ry + 2), P.m_rect(x - 200, y - 200, x + 200, cut))
        P.fill_mask(lm, lid)
        P.stroke(quad((x - rx - 6, cut + 4), (x, cut - 6), (x + rx + 6, cut + 4)), 12)


def face(P, cx, cy, sleepy, lid, mouth="w", spacing=118, r=1.0):
    for d in (-1, 1):
        big_eye(P, cx + d * spacing, cy, sleepy, lid, r)
        P.ellipse(cx + d * (spacing + 62), cy + 92, 40, 22, fill=H("#ff8fb1"), outline=0, alpha=170)
    my = cy + 112
    if mouth == "w":
        P.stroke([(cx - 30, my), (cx - 15, my + 16), (cx, my + 2), (cx + 15, my + 16), (cx + 30, my)], 9)
    elif mouth == "smile":
        P.stroke(quad((cx - 26, my), (cx, my + 22), (cx + 26, my)), 9)
    elif mouth == "o":
        P.ellipse(cx, my + 8, 14, 17, fill=H("#7a2a4a"), outline=8)


def fuzzy(P):
    """Fuzzy blue critter with little horns, sleepy eyes, black hoodie."""
    sky(P, "#ffb6d5", "#b8a6ff", "#fff3b0")
    P.poly([(250, 1000), (290, 800), (500, 760), (710, 800), (750, 1000)], H("#2a2633"))
    P.ellipse(500, 790, 190, 60, fill=H("#3a3546"), outline=10)  # hood, behind the head
    P.stroke(quad((420, 820), (500, 870), (580, 820)), 10, color=H("#e8e4dc"))
    for d in (-1, 1):
        P.poly(cubic((500 + d * 150, 300), (500 + d * 170, 220), (500 + d * 230, 190), (500 + d * 250, 200)) +
               cubic((500 + d * 250, 200), (500 + d * 230, 250), (500 + d * 215, 300), (500 + d * 205, 330)), H("#ffa24d"), outline=12)
    pts = []
    for i in range(360):
        t = 2 * math.pi * i / 360
        f = 1 + 0.055 * abs(math.sin(13 * t)) ** 0.6
        pts.append((500 + 290 * f * math.cos(t), 540 + 265 * f * math.sin(t)))
    m = P.m_poly(pts)
    body_paint(P, m, H("#6f86ff"))
    for i in range(22):  # soft fur tufts just inside the edge
        a = i * 2 * math.pi / 22 + 0.1
        x, y = 500 + 245 * math.cos(a), 540 + 222 * math.sin(a)
        P.fill_mask(P.intersect(P.m_stroke(quad((x, y), (x + 10 * math.cos(a + 1.2), y + 10 * math.sin(a + 1.2)),
                                                 (x + 30 * math.cos(a), y + 30 * math.sin(a))), 6), m), H("#4f63e0"), alpha=130)
    face(P, 500, 520, 0.38, H("#5a6fe6"), "w")


def mushroom(P):
    """Cream mushroom critter with a red spotted cap and a little flower."""
    sky(P, "#bfe8ff", "#d9f5c9", WHITE)
    P.ellipse(500, 1060, 560, 220, fill=H("#8fd27a"), outline=0)
    stem = P.m_poly(ellipse_pts(500, 660, 250, 270))
    body_paint(P, stem, H("#f7e2c2"))
    cap = [(500 + 390 * math.cos(t), 470 + 320 * math.sin(t)) for t in [math.pi + math.pi * i / 120 for i in range(121)]]
    cap += cubic((890, 470), (800, 545), (200, 545), (110, 470))[1:]
    cm = P.m_poly(cap)
    P.shape(cm, P.gradient([(0, H("#ff6b5a")), (1, H("#d63c3c"))], 90), outline=16)
    P.fill_mask(P.subtract(cm, P.shift(cm, -40, -30)).filter(ImageFilter.GaussianBlur(10 * P.s)), H("#a8242e"), alpha=120)
    for x, y, rx, ry in ((330, 300, 50, 40), (520, 210, 62, 46), (690, 320, 46, 38), (420, 420, 34, 26), (800, 420, 30, 24), (230, 420, 28, 22)):
        lay = P.layer()
        lay.ellipse(x, y, rx, ry, fill=H("#fff6ea"), outline=0)
        P.compose(lay, clip=cm)
    P.fill_mask(P.intersect(P.m_ellipse(360, 230, 90, 40, rot=-25), cm), WHITE, alpha=90)
    face(P, 500, 650, 0.4, H("#ecd0a8"), "o", spacing=110, r=0.92)
    for i in range(5):
        a = math.radians(i * 72 - 90)
        P.ellipse(760 + 30 * math.cos(a), 760 + 30 * math.sin(a), 24, 18, fill=WHITE, rot=i * 72 - 90, outline=8)
    P.ellipse(760, 760, 18, fill=H("#ffd86b"), outline=8)


def ghost(P):
    """Pastel holographic ghost with a tiny crown."""
    sky(P, "#2b2160", "#6b4fb8", "#fff3b0")
    for x, y in ((160, 300), (850, 420), (240, 820), (780, 840)):
        P.ellipse(x, y, 5, fill=WHITE, outline=0, alpha=220)
    pts = [(500 + 270 * math.cos(t), 470 + 270 * math.sin(t)) for t in [math.pi + math.pi * i / 80 for i in range(81)]]
    pts += [(770, 900)] + [(770 - 540 * u, 900 + 40 * math.sin(u * 4 * math.pi)) for u in [i / 60 for i in range(61)]] + [(230, 470)]
    m = P.m_poly(pts)
    P.glow(m, H("#d9c8ff"), 40, alpha=150)
    P.shape(m, P.gradient([(0, H("#c9f4ff")), (0.35, H("#e6d1ff")), (0.7, H("#ffd1ec")), (1, H("#fff3c4"))], 60), outline=16)
    P.fill_mask(P.subtract(m, P.shift(m, -40, -30)).filter(ImageFilter.GaussianBlur(14 * P.s)), H("#b79cff"), alpha=110)
    P.fill_mask(P.intersect(P.m_ellipse(370, 330, 70, 34, rot=-30), m), WHITE, alpha=140)
    face(P, 500, 520, 0.0, None, "smile")
    crown = [(420, 230), (405, 150), (455, 190), (500, 130), (545, 190), (595, 150), (580, 230)]
    P.glow(P.m_poly(crown), H("#ffd86b"), 18, alpha=170)
    P.poly(crown, P.gradient([(0, H("#fff0a8")), (1, H("#e0a21c"))], 90), outline=11)
    for x, y in ((405, 150), (500, 130), (595, 150)):
        P.ellipse(x, y, 11, fill=H("#ff8fb1"), outline=6)


def sprout(P):
    """Pink fuzzy sprout critter with round glasses and a green scarf."""
    sky(P, "#fff1c9", "#ffc9de", WHITE)
    P.poly([(260, 1000), (300, 820), (500, 790), (700, 820), (740, 1000)], H("#f4a6c2"))
    pts = []
    for i in range(360):
        t = 2 * math.pi * i / 360
        f = 1 + 0.035 * abs(math.sin(16 * t)) ** 0.7
        pts.append((500 + 280 * f * math.cos(t), 560 + 255 * f * math.sin(t)))
    m = P.m_poly(pts)
    stem = quad((500, 320), (480, 240), (515, 180))
    P.stroke(stem, 28)
    P.stroke(stem, 14, color=H("#5dbb4a"))
    for d, col in ((-1, "#5dbb4a"), (1, "#8ee3b0")):
        tip = (515 + d * 130, 150)
        P.poly(cubic((515, 180), (515 + d * 30, 110), (tip[0] - d * 20, 100), tip) +
               cubic(tip, (tip[0] - d * 20, 180), (515 + d * 50, 200), (515, 180)), H(col), outline=12)
    body_paint(P, m, H("#ffb3cf"))
    scarf = P.intersect(m, P.m_rect(0, 700, 1000, 790))
    P.fill_mask(scarf, H("#5dbb4a"))
    for x in range(200, 820, 70):
        P.fill_mask(P.intersect(scarf, P.m_rect(x, 700, x + 30, 790)), H("#8ee3b0"))
    P.poly([(600, 760), (680, 760), (700, 930), (620, 930)], H("#5dbb4a"), outline=12)
    face(P, 500, 540, 0.0, None, "w", spacing=120, r=0.9)
    for d in (-1, 1):
        ring = P.subtract(P.m_ellipse(500 + d * 120, 540, 96), P.m_ellipse(500 + d * 120, 540, 84))
        P.shape(ring, H("#2a2140"), outline=0)
        P.fill_mask(P.m_ellipse(500 + d * 120, 540, 84), WHITE, alpha=40)
    P.stroke(quad((416, 520), (500, 500), (584, 520)), 12, color=H("#2a2140"))


def main():
    OUT.mkdir(exist_ok=True)
    made = []
    for i, (name, fn) in enumerate((("fuzzy", fuzzy), ("mushroom", mushroom), ("ghost", ghost), ("sprout", sprout))):
        Painter.set_style(1000 + i, warp=1.4)
        P = Painter(2048)
        fn(P)
        img = P.final(1000).convert("RGB")
        p = OUT / f"x-pfp-chibi-{name}.png"
        img.save(p, optimize=True)
        made.append((name, img))
    sheet = Image.new("RGB", (4 * 330 + 50, 400), "black")
    for i, (name, img) in enumerate(made):
        circ = Image.new("L", (300, 300), 0)
        ImageDraw.Draw(circ).ellipse([0, 0, 299, 299], fill=255)
        sheet.paste(img.resize((300, 300), Image.LANCZOS), (25 + i * 330, 30), circ)
        ImageDraw.Draw(sheet).text((25 + i * 330 + 120, 345), name, fill=(170, 170, 170))
    sheet.save(OUT / "x-pfp-chibi-preview.png")
    print("wrote", [m[0] for m in made])


if __name__ == "__main__":
    main()
