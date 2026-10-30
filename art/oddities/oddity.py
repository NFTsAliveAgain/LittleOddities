"""The Oddity: one signature character, many traits.

Every Little Oddity is the same creature (big round head, pointed ears, a
curled antenna, neck and shoulders) shown as a portrait bust. What changes —
and what makes one rarer than another — is skin, markings, eyes, eyewear,
mouth, headwear, clothing, accessories and background.
"""
from __future__ import annotations

import math

from PIL import ImageFilter

from .paint import (FEATURE_OUTLINE as FO, INK, OUTLINE, WHITE, Painter, cubic, ellipse_pts, hex_rgb, mix, quad,
                    rotate, shade, star_pts, tint, width_at)

H = hex_rgb
GOLD = [(0, H("#FFF1A8")), (0.45, H("#F2C14E")), (1, H("#B07A12"))]
SILVER = [(0, H("#FFFFFF")), (0.5, H("#C7CDD8")), (1, H("#7D8597"))]


def superblob(cx, cy, a, b, n_top, n_bot, steps=240):
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        c, s = math.cos(t), math.sin(t)
        n = n_bot if s > 0 else n_top
        pts.append((cx + a * math.copysign(abs(c) ** (2 / n), c), cy + b * math.copysign(abs(s) ** (2 / n), s)))
    return pts


HEAD = superblob(500, 445, 258, 238, 2.25, 2.9)
HEAD_TOP = min(p[1] for p in HEAD)
NECK_Y = 735
TORSO = ([(428, 640), (428, 725)] + cubic((428, 725), (410, 800), (250, 805), (175, 868))[1:] +
         [(118, 1020), (882, 1020)] + cubic((825, 868), (750, 805), (590, 800), (572, 725)) + [(572, 640)])
EYE_L, EYE_R, EYE_R_ = (392, 452), (608, 452), 60
MOUTH = (500, 590)
EARS = {"l": (262, 440), "r": (738, 440)}


def hw(y):
    a, b = width_at(HEAD, y)
    return a, b


class Ctx:
    def __init__(self, P, bg, skin, traits, rng):
        self.P, self.bg, self.skin, self.t, self.rng = P, bg, skin, traits, rng
        self.base = H(skin["color"])
        self.head_mask = None
        self.torso_mask = None
        self.eyes = [(EYE_L[0], EYE_L[1], EYE_R_), (EYE_R[0], EYE_R[1], EYE_R_)]


# ================================================================== skin
def skin_fill(ctx, P):
    s = ctx.skin
    if s["name"] == "Cosmic":
        return P.gradient([(0, H("#1B1240")), (0.5, H("#3B1F7A")), (1, H("#0E2350"))], 70)
    if s.get("gradient"):
        st = s["gradient"]
        return P.gradient([(i / (len(st) - 1), H(c)) for i, c in enumerate(st)], 65)
    return ctx.base


def paint_skin(ctx, mask, outline=OUTLINE + 2, light=True):
    P, base = ctx.P, ctx.base
    P.shape(mask, skin_fill(ctx, P), outline=outline)
    if ctx.skin["name"] == "Cosmic":
        lay = P.layer()
        for _ in range(70):
            lay.ellipse(ctx.rng.uniform(150, 850), ctx.rng.uniform(150, 1000), ctx.rng.uniform(1.5, 4), fill=WHITE, outline=0,
                        alpha=int(ctx.rng.uniform(120, 255)))
        lay.glow(lay.m_ellipse(400, 380, 120), H("#FF5FA2"), 50, alpha=90)
        lay.glow(lay.m_ellipse(620, 560, 110), H("#2EC4B6"), 50, alpha=80)
        P.compose(lay, clip=mask)
    tex = P.intersect(P.pressure().point(lambda v: max(0, v - 140) * 2), mask)
    P.fill_mask(tex, shade(base, 0.88), alpha=60)
    form = P.subtract(mask, P.shift(mask, -80, -60)).filter(ImageFilter.GaussianBlur(30 * P.s))
    P.fill_mask(P.intersect(form, mask), shade(base, 0.8), alpha=120)
    P.fill_mask(P.subtract(mask, P.shift(mask, -36, -28)), shade(base, 0.72), alpha=150)
    P.halftone(P.subtract(mask, P.shift(mask, -24, -18)), spacing=10, max_r=3.2, alpha=80, color=shade(base, 0.45))
    P.fill_mask(P.subtract(mask, P.shift(mask, -7, -5)), tint(base, 0.35), alpha=140)
    if light:
        P.fill_mask(P.subtract(mask, P.shift(mask, 26, 22)).filter(ImageFilter.GaussianBlur(10 * P.s)), WHITE, alpha=70)


def draw_ear(ctx, side, kind):
    P = ctx.P
    bx, by = EARS[side]
    d = -1 if side == "l" else 1
    if kind == "Pointy":
        tip = (bx + d * 150, by - 120)
        pts = cubic((bx, by - 70), (bx + d * 60, by - 110), (tip[0] - d * 30, tip[1] + 10), tip) + \
            cubic(tip, (tip[0] - d * 10, tip[1] + 60), (bx + d * 60, by + 60), (bx, by + 55))[1:]
    elif kind == "Droopy":
        tip = (bx + d * 120, by + 150)
        pts = cubic((bx, by - 60), (bx + d * 110, by - 70), (tip[0] + d * 30, tip[1] - 60), tip) + \
            cubic(tip, (tip[0] - d * 40, tip[1] + 10), (bx + d * 10, by + 90), (bx, by + 60))[1:]
    elif kind == "Notched":
        tip = (bx + d * 150, by - 110)
        pts = cubic((bx, by - 70), (bx + d * 60, by - 110), (tip[0] - d * 30, tip[1] + 10), tip) + \
            [(tip[0] - d * 18, tip[1] + 40), (tip[0] - d * 45, tip[1] + 38), (tip[0] - d * 38, tip[1] + 70)] + \
            cubic((tip[0] - d * 38, tip[1] + 70), (tip[0] - d * 50, tip[1] + 110), (bx + d * 60, by + 60), (bx, by + 55))[1:]
    elif kind == "Fins":
        pts = [(bx, by - 80)]
        for i in range(4):
            a = math.radians(-60 + i * 35)
            pts += [(bx + d * 150 * math.cos(a), by + 150 * math.sin(a)),
                    (bx + d * 95 * math.cos(a + 0.3), by + 95 * math.sin(a + 0.3))]
        pts += [(bx, by + 70)]
    else:  # Round
        pts = ellipse_pts(bx + d * 55, by - 30, 78, 82)
    m = P.m_poly(pts)
    paint_skin(ctx, m, outline=OUTLINE + 1, light=False)
    inner = P.intersect(P.m_poly(pts), P.shift(P.m_poly(pts), -d * 22, 14))
    inner = P.intersect(inner, P.shift(m, d * 18, 0))
    P.fill_mask(inner, mix(ctx.base, H("#FF8FA8"), 0.45), alpha=170)
    if kind == "Fins":
        for i in range(4):
            a = math.radians(-60 + i * 35)
            P.fill_mask(P.intersect(P.m_stroke([(bx, by), (bx + d * 120 * math.cos(a), by + 120 * math.sin(a))], 4), m), INK, alpha=90)


def draw_antenna(ctx):
    P = ctx.P
    curl = [(500, HEAD_TOP + 12)] + cubic((500, HEAD_TOP + 12), (505, HEAD_TOP - 70), (575, HEAD_TOP - 110), (590, HEAD_TOP - 70))[1:]
    P.stroke(curl, 20, color=INK)
    P.stroke(curl, 10, color=ctx.base)
    tip = curl[-1]
    glow = ctx.t["skin"] in ("Gold", "Cosmic", "Holo")
    if glow:
        P.glow(P.m_ellipse(*tip, 30), H("#FFF2B0"), 16, alpha=200)
    P.ellipse(tip[0], tip[1], 20, fill=tint(ctx.base, 0.35) if not glow else H("#FFF2B0"))


def draw_base(ctx):
    P = ctx.P
    ctx.torso_mask = P.m_poly(TORSO)
    paint_skin(ctx, ctx.torso_mask)
    # neck shadow under the chin
    P.fill_mask(P.intersect(ctx.torso_mask, P.m_ellipse(500, 690, 120, 60)).filter(ImageFilter.GaussianBlur(12 * P.s)),
                shade(ctx.base, 0.6), alpha=150)
    for side in ("l", "r"):
        draw_ear(ctx, side, ctx.t["ears"])


def draw_head(ctx):
    P = ctx.P
    ctx.head_mask = P.m_poly(HEAD)
    paint_skin(ctx, ctx.head_mask)
    # nose + cheek planes
    for dx in (-16, 16):
        P.stroke(quad((500 + dx * 0.6, 528), (500 + dx * 1.3, 538), (500 + dx * 1.5, 532)), 6)
    P.fill_mask(P.intersect(P.m_ellipse(500, 515, 40, 30), ctx.head_mask).filter(ImageFilter.GaussianBlur(10 * P.s)), WHITE, alpha=60)
    for x in (320, 680):
        P.fill_mask(P.m_ellipse(x, 560, 46, 26).filter(ImageFilter.GaussianBlur(14 * P.s)), shade(ctx.base, 0.75), alpha=60)


# ============================================================== markings
def markings(ctx, kind):
    P = ctx.P
    dark = shade(ctx.base, 0.55)
    if kind == "None":
        return
    lay = P.layer()
    if kind == "Freckles":
        for cx in (330, 670):
            for dx, dy in ((-22, -6), (4, -14), (24, 2), (-8, 14), (14, 22), (-30, 18)):
                lay.ellipse(cx + dx, 545 + dy, 5, fill=dark, outline=0, alpha=200)
    elif kind == "Cheek Stripes":
        for d in (-1, 1):
            for i in range(3):
                y = 540 + i * 24
                x0 = 500 + d * 250
                lay.stroke([(x0, y), (x0 - d * 70, y + 6)], 11, color=dark, alpha=220)
    elif kind == "Spots":
        for x, y, r in ((300, 330, 26), (690, 300, 20), (720, 590, 30), (290, 600, 16), (560, 250, 14)):
            lay.ellipse(x, y, r, fill=dark, outline=0, alpha=150)
    elif kind == "Scar":
        pts = [(610, 340), (625, 410), (640, 520)]
        lay.stroke(pts, 9, color=shade(ctx.base, 0.5))
        for i in range(4):
            x, y = 612 + i * 8.5, 360 + i * 45
            lay.stroke([(x - 16, y + 2), (x + 16, y - 4)], 5, color=shade(ctx.base, 0.45))
    elif kind == "Star Tattoo":
        lay.poly(star_pts(395, 545, 18, 7), INK, outline=0)
    elif kind == "Face Paint":
        for d in (-1, 1):
            lay.poly([(500 + d * 130, 515), (500 + d * 230, 505), (500 + d * 228, 530), (500 + d * 135, 535)], WHITE, outline=0, alpha=230)
    elif kind == "Stitches":
        lay.stroke([(310, 260), (340, 330), (330, 400)], 6, color=INK)
        for i in range(5):
            t = i / 4
            x, y = 310 + 25 * t, 270 + 120 * t
            lay.stroke([(x - 16, y), (x + 16, y - 6)], 5, color=INK)
        lay.ellipse(690, 600, 16, fill=WHITE, outline=FO)
    elif kind == "Glow Runes":
        rune = H("#7DF9E7")
        for path in ([(300, 300), (330, 350), (300, 400)], [(700, 300), (670, 350), (700, 400)], [(470, 245), (500, 275), (530, 245)]):
            lay.glow(lay.m_stroke(path, 14), rune, 10, alpha=200)
            lay.stroke(path, 7, color=tint(rune, 0.4))
    else:
        raise KeyError(kind)
    P.compose(lay, clip=ctx.head_mask)


# ================================================================== eyes
def _sclera(P, x, y, r, color=WHITE):
    m = P.ellipse(x, y, r * 0.95, r * 0.9, fill=color, outline=FO)
    P.fill_mask(P.subtract(m, P.shift(m, 0, -r * 0.35)), (150, 140, 175), alpha=90)
    return m


def _iris(P, x, y, r, col, pupil=0.42, glint=True):
    iris = P.gradient([(0, tint(col, 0.3)), (1, shade(col, 0.6))], 90)
    P.shape(P.m_ellipse(x, y, r * 0.86, r * 0.9), iris, outline=4)
    for k in range(12):
        a = k * 0.5236
        P.stroke([(x + r * 0.4 * math.cos(a), y + r * 0.4 * math.sin(a)), (x + r * 0.78 * math.cos(a), y + r * 0.78 * math.sin(a))],
                 2.5, color=shade(col, 0.5), alpha=130)
    P.ellipse(x, y, r * pupil, fill=INK, outline=0)
    if glint:
        P.ellipse(x - r * 0.32, y - r * 0.36, r * 0.2, fill=WHITE, outline=0)
        P.ellipse(x + r * 0.3, y + r * 0.3, r * 0.08, fill=WHITE, outline=0, alpha=220)


def _lid(ctx, x, y, r, cover, tilt=0.0):
    P = ctx.P
    m = P.m_ellipse(x, y, r * 0.95, r * 0.9)
    ly = y - r * 0.9 + 1.8 * r * cover
    lidpoly = [(x - r * 1.3, y - r * 1.4), (x + r * 1.3, y - r * 1.4), (x + r * 1.3, ly - tilt * r), (x - r * 1.3, ly + tilt * r)]
    lm = P.intersect(m, P.m_poly(lidpoly))
    P.fill_mask(lm, shade(ctx.base, 0.86))
    P.fill_mask(P.subtract(lm, P.shift(lm, 0, 8)), WHITE, alpha=50)
    P.stroke([(x - r * 1.02, ly + tilt * r * 1.02), (x + r * 1.02, ly - tilt * r * 1.02)], FO + 2)


def _bags(ctx, x, y, r):
    ctx.P.stroke(quad((x - r * 0.6, y + r * 1.12), (x, y + r * 1.3), (x + r * 0.62, y + r * 1.1)), 5, color=shade(ctx.base, 0.55))


IRIS_COLORS = ["#6B4428", "#2F7D6B", "#3E56B8", "#7A3FA8", "#A65A1E", "#3C3C46"]


def eyes(ctx, kind):
    P = ctx.P
    r = EYE_R_
    col = H(IRIS_COLORS[sum(map(ord, ctx.t["skin"] + ctx.t["clothing"])) % len(IRIS_COLORS)])
    pts = [EYE_L, EYE_R]
    if kind in ("Bored", "Unimpressed", "Side-Eye", "Sleepy", "Wide Awake", "Focused"):
        cover = {"Bored": 0.5, "Unimpressed": 0.4, "Side-Eye": 0.36, "Sleepy": 0.62, "Wide Awake": 0.0, "Focused": 0.3}[kind]
        look = {"Bored": (0, 0.22), "Unimpressed": (0.0, 0.12), "Side-Eye": (0.38, 0.1), "Sleepy": (0, 0.3),
                "Wide Awake": (0, 0), "Focused": (0, 0.05)}[kind]
        for (x, y) in pts:
            _sclera(P, x, y, r)
            _iris(P, x + look[0] * r, y + look[1] * r, r * (0.58 if kind != "Wide Awake" else 0.48), col)
            if cover:
                _lid(ctx, x, y, r, cover)
            if kind == "Focused":
                lower = P.intersect(P.m_ellipse(x, y, r * 0.95, r * 0.9), P.m_rect(x - 90, y + r * 0.45, x + 90, y + 90))
                P.fill_mask(lower, shade(ctx.base, 0.86))
                P.stroke([(x - r * 0.9, y + r * 0.45), (x + r * 0.9, y + r * 0.45)], FO)
            if kind in ("Bored", "Sleepy", "Unimpressed"):
                _bags(ctx, x, y, r)
    elif kind == "Angry":
        for (x, y), d in ((EYE_L, 1), (EYE_R, -1)):
            _sclera(P, x, y, r)
            _iris(P, x, y + r * 0.1, r * 0.52, col)
            _lid(ctx, x, y, r, 0.38, tilt=0.28 * -d)
            P.stroke([(x - d * r * 1.05, y - r * 1.15), (x + d * r * 0.9, y - r * 0.72)], FO + 6)
    elif kind == "Wink":
        _sclera(P, *EYE_L, r)
        _iris(P, EYE_L[0], EYE_L[1] + 6, r * 0.56, col)
        _lid(ctx, *EYE_L, r, 0.38)
        P.stroke(quad((EYE_R[0] - r, EYE_R[1] + 4), (EYE_R[0], EYE_R[1] - r * 0.45), (EYE_R[0] + r, EYE_R[1] + 4)), FO + 3)
        ctx.eyes = ctx.eyes[:1]
    elif kind == "Cyclops":
        x, y, rr = 500, 445, r * 1.65
        _sclera(P, x, y, rr)
        _iris(P, x, y + 8, rr * 0.55, col)
        _lid(ctx, x, y, rr, 0.32)
        ctx.eyes = [(x, y, rr)]
    elif kind == "Hypno":
        for (x, y) in pts:
            _sclera(P, x, y, r)
            sp = [(x + r * 0.78 * i / 70 * math.cos(i / 70 * 3 * 6.283), y + r * 0.74 * i / 70 * math.sin(i / 70 * 3 * 6.283)) for i in range(71)]
            P.stroke(sp, 6, color=H("#8E3FD1"))
            _lid(ctx, x, y, r, 0.25)
    elif kind == "Glowing":
        for (x, y) in pts:
            m = P.m_ellipse(x, y, r * 0.95, r * 0.9)
            P.glow(m, H("#7DF9E7"), 30, alpha=230)
            P.shape(m, P.gradient([(0, WHITE), (1, H("#7DF9E7"))], 90), outline=FO)
            _lid(ctx, x, y, r, 0.36)
    elif kind == "Gold":
        for (x, y) in pts:
            _sclera(P, x, y, r, color=H("#2A1E3A"))
            P.glow(P.m_ellipse(x, y + 8, r * 0.5), H("#FFD86B"), 18, alpha=220)
            P.shape(P.m_ellipse(x, y + 8, r * 0.5, r * 0.52), P.gradient(GOLD, 90), outline=4)
            P.ellipse(x, y + 8, r * 0.14, r * 0.34, fill=INK, outline=0)
            _lid(ctx, x, y, r, 0.36)
    else:
        raise KeyError(kind)


# ================================================================ eyewear
def eyewear(ctx, kind):
    P = ctx.P
    if kind == "None":
        return
    (lx, ly), (rx, ry) = EYE_L, EYE_R
    if kind == "Shades":
        for x in (lx, rx):
            m = P.m_poly([(x - 92, ly - 50), (x + 86, ly - 50), (x + 70, ly + 44), (x - 80, ly + 48)])
            P.shape(m, P.gradient([(0, H("#3A2E52")), (1, H("#120C1E"))], 90), outline=FO + 2)
            P.fill_mask(P.intersect(m, P.m_stroke([(x - 70, ly + 20), (x - 20, ly - 45)], 16)), WHITE, alpha=90)
            P.fill_mask(P.intersect(m, P.m_stroke([(x - 30, ly + 30), (x + 0, ly - 10)], 6)), WHITE, alpha=70)
        P.stroke([(lx + 86, ly - 42), (rx - 92, ry - 42)], 16)
        for x, d in ((lx - 92, -1), (rx + 86, 1)):
            P.stroke([(x, ly - 44), (x + d * 70, ly - 50)], 12)
    elif kind == "Round Specs":
        for x in (lx, rx):
            P.fill_mask(P.m_ellipse(x, ly, 84), WHITE, alpha=45)
            ring = P.subtract(P.m_ellipse(x, ly, 90), P.m_ellipse(x, ly, 78))
            P.shape(ring, P.gradient(GOLD, 90), outline=4)
        P.stroke(quad((lx + 88, ly - 8), (500, ly - 30), (rx - 88, ry - 8)), 9)
    elif kind == "Aviators":
        for x, d in ((lx, -1), (rx, 1)):
            m = P.m_poly(cubic((x - d * 10, ly - 50), (x + d * 100, ly - 60), (x + d * 100, ly + 60), (x + d * 20, ly + 70)) +
                         cubic((x + d * 20, ly + 70), (x - d * 80, ly + 72), (x - d * 95, ly - 30), (x - d * 10, ly - 50))[1:])
            P.shape(m, P.gradient([(0, H("#FFB36B")), (0.5, H("#E0568A")), (1, H("#5B3FB8"))], 90), outline=7, alpha=235)
            P.fill_mask(P.intersect(m, P.m_stroke([(x - 60, ly + 10), (x - 20, ly - 40)], 14)), WHITE, alpha=110)
        P.stroke([(lx + 95, ly - 44), (rx - 95, ry - 44)], 8)
        P.stroke([(lx + 80, ly - 30), (rx - 80, ry - 30)], 5)
    elif kind == "3D Glasses":
        P.rect(lx - 105, ly - 58, rx + 105, ly + 52, WHITE, radius=18, outline=FO + 2)
        P.rect(lx - 82, ly - 40, lx + 82, ly + 36, H("#FF4D5E"), radius=10, outline=6, alpha=225)
        P.rect(rx - 82, ry - 40, rx + 82, ry + 36, H("#3FB6FF"), radius=10, outline=6, alpha=225)
    elif kind == "Eyepatch":
        P.stroke([(250, 330), (rx + 110, ry - 110)], 12)
        P.stroke([(lx - 60, ly - 30), (240, 470)], 12)
        P.poly(superblob(lx, ly + 6, 82, 74, 2.4, 2.0, 80), H("#1E1828"), outline=FO + 2)
    elif kind == "Visor":
        m = P.m_poly(cubic((lx - 140, ly - 40), (450, ly - 90), (550, ly - 90), (rx + 140, ly - 40)) +
                     cubic((rx + 140, ly + 40), (550, ly + 70), (450, ly + 70), (lx - 140, ly + 40)))
        P.glow(m, H("#7DF9E7"), 22, alpha=170)
        P.shape(m, P.gradient([(0, H("#2EF2D6")), (0.5, H("#3E8BFF")), (1, H("#B05BFF"))], 0), outline=FO + 2, alpha=240)
        lay = P.layer()
        for i in range(8):
            lay.stroke([(lx - 140, ly - 30 + i * 11), (rx + 140, ly - 30 + i * 11)], 2.5, color=WHITE, alpha=90)
        P.compose(lay, clip=m)
        P.fill_mask(P.intersect(m, P.m_stroke([(lx - 90, ly + 20), (lx - 30, ly - 50)], 22)), WHITE, alpha=120)
    elif kind == "Monocle":
        x, y = rx, ry
        P.fill_mask(P.m_ellipse(x, y, 88), WHITE, alpha=55)
        P.shape(P.subtract(P.m_ellipse(x, y, 96), P.m_ellipse(x, y, 82)), P.gradient(GOLD, 90), outline=5)
        for (cx, cy) in quad((x + 60, y + 72), (x + 110, y + 220), (x + 40, 780))[::2]:
            P.ellipse(cx, cy, 5.5, fill=H("#F2C14E"), outline=3)
    else:
        raise KeyError(kind)


# ================================================================= mouth
def mouth(ctx, kind):
    P = ctx.P
    x, y = MOUTH
    if kind == "Flat":
        P.stroke(quad((x - 62, y), (x, y + 6), (x + 58, y - 2)), FO + 2)
    elif kind == "Smirk":
        P.stroke(cubic((x - 70, y + 4), (x - 10, y + 16), (x + 40, y + 8), (x + 78, y - 22)), FO + 2)
        P.stroke([(x + 72, y - 30), (x + 86, y - 14)], 6)
    elif kind == "Frown":
        P.stroke(quad((x - 60, y + 14), (x, y - 14), (x + 60, y + 14)), FO + 2)
    elif kind in ("Smug Grin", "Gold Grill", "Diamond Grill", "Fangs"):
        m = P.m_poly(quad((x - 92, y - 18), (x, y + 2), (x + 92, y - 26)) + quad((x + 92, y - 26), (x + 10, y + 70), (x - 92, y - 18))[1:])
        P.shape(m, H("#4A1830"), outline=FO + 1)
        lay = P.layer()
        tooth = {"Gold Grill": P.gradient(GOLD, 90), "Diamond Grill": P.gradient([(0, WHITE), (0.5, H("#BFF4FF")), (1, H("#8FC8FF"))], 45)}.get(kind, WHITE)
        lay.shape(lay.m_rect(x - 100, y - 40, x + 100, y + 18), tooth, outline=0)
        for i in range(-3, 4):
            lay.stroke([(x + i * 26, y - 30), (x + i * 26, y + 18)], 4, color=(120, 100, 120) if kind != "Gold Grill" else H("#8A5A0A"))
        if kind == "Diamond Grill":
            for i in range(-3, 3):
                lay.poly(star_pts(x + i * 26 + 13, y - 6, 9, 3, 4), WHITE, outline=0)
        lay.ellipse(x + 8, y + 50, 46, 26, fill=H("#E8607A"), outline=0)
        P.compose(lay, clip=m)
        P.fill_mask(P.subtract(P.ink_line(m, FO + 1), m), INK)
        if kind == "Fangs":
            for dx in (-48, 40):
                P.poly([(x + dx - 13, y - 10), (x + dx + 13, y - 12), (x + dx + 1, y + 34)], WHITE, outline=5)
    elif kind == "Toothpick":
        P.stroke(cubic((x - 64, y + 2), (x - 10, y + 14), (x + 30, y + 8), (x + 66, y - 12)), FO + 2)
        P.stroke([(x + 30, y + 4), (x + 150, y - 30)], 14, color=INK)
        P.stroke([(x + 30, y + 4), (x + 150, y - 30)], 7, color=H("#E8C48A"))
    elif kind == "Bubblegum":
        P.stroke(quad((x - 50, y), (x, y + 8), (x + 50, y)), FO)
        P.ellipse(x + 10, y + 6, 74, 70, fill=H("#FF8FC7"))
        P.ellipse(x - 18, y - 22, 16, 11, fill=WHITE, outline=0, rot=-30, alpha=220)
    elif kind == "Tongue Out":
        P.stroke(quad((x - 66, y - 4), (x, y + 14), (x + 66, y - 6)), FO + 2)
        m = P.subtract(P.m_ellipse(x + 24, y + 26, 30, 38), P.m_rect(0, 0, 1000, y + 6))
        P.shape(m, H("#E8607A"), outline=7)
        P.stroke([(x + 24, y + 14), (x + 24, y + 44)], 4, color=H("#B53A55"))
    elif kind == "Shout":
        m = P.m_ellipse(x, y + 16, 52, 44)
        P.shape(m, H("#4A1830"), outline=FO + 1)
        lay = P.layer()
        lay.ellipse(x, y + 52, 34, 20, fill=H("#E8607A"), outline=0)
        lay.rect(x - 60, y - 40, x + 60, y - 10, WHITE, outline=0)
        P.compose(lay, clip=m)
    else:
        raise KeyError(kind)


# ============================================================== clothing
def _garment_region(ctx, y0):
    return ctx.P.intersect(ctx.torso_mask, ctx.P.m_rect(0, y0, 1000, 1000))


def _finish(ctx, reg, col):
    P = ctx.P
    P.form_shade(reg, 1.3)
    P.halftone(P.subtract(reg, P.shift(reg, -26, -20)), spacing=10, max_r=3, alpha=70, color=shade(col, 0.45))
    for x, y in ((300, 900), (690, 905), (420, 960)):
        P.fill_mask(P.intersect(P.m_stroke(quad((x, y), (x + 18, y + 30), (x + 6, y + 70)), 5), reg), INK, alpha=60)
    P.fill_mask(P.intersect(P.subtract(P.ink_line(reg, FO), reg), ctx.torso_mask), INK)


def clothing(ctx, kind):
    P = ctx.P
    if kind == "None":
        return
    C = {"Tee": "#F4F1EA", "Hoodie": "#5B4BD6", "Bomber Jacket": "#4F5B3A", "Denim Jacket": "#4C78C8", "Puffer": "#FF6B3D",
         "Turtleneck": "#2A2A36", "Tracksuit": "#1F8A70", "Varsity Jacket": "#8C1D2F", "Leather Jacket": "#26222E",
         "Suit": "#2C3350", "Space Suit": "#F2F2F5", "Royal Cape": "#9E1B3B"}
    col = H(C[kind])
    y0 = 742 if kind != "Turtleneck" else 655
    reg = _garment_region(ctx, y0)
    P.fill_mask(reg, col)
    if kind == "Tee":
        P.fill_mask(P.intersect(reg, P.m_ellipse(500, 742, 82, 40)), ctx.base)
        _finish(ctx, reg, col)
        P.stroke(quad((418, 744), (500, 790), (582, 744)), 9)
        # brand graphic: the sprout mark
        P.stroke(quad((500, 960), (494, 915), (504, 880)), 10, color=H("#3E9B4F"))
        for d in (-1, 1):
            P.poly(cubic((504, 880), (504 + d * 30, 850), (504 + d * 60, 860), (504 + d * 64, 872)) +
                   cubic((504 + d * 64, 872), (504 + d * 40, 890), (504 + d * 20, 890), (504, 880))[1:], H("#5DBB4A"), outline=6)
    elif kind == "Hoodie":
        _finish(ctx, reg, col)
        hood = superblob(500, 752, 175, 50, 2.0, 2.0, 120)
        hm = P.subtract(P.intersect(P.m_poly(hood), ctx.torso_mask), P.m_ellipse(500, 740, 95, 34))
        P.shape(hm, shade(col, 0.85), outline=FO)
        for d in (-1, 1):
            P.stroke(quad((500 + d * 40, 790), (500 + d * 52, 860), (500 + d * 44, 920)), 8, color=H("#F4F1EA"))
            P.rect(500 + d * 44 - 7, 918, 500 + d * 44 + 7, 945, H("#C8C2B8"), radius=3, outline=5)
    elif kind in ("Bomber Jacket", "Varsity Jacket", "Tracksuit", "Puffer"):
        if kind == "Varsity Jacket":
            for d in (-1, 1):
                sl = P.intersect(reg, P.m_poly([(500 + d * 250, 760), (500 + d * 420, 820), (500 + d * 420, 1020), (500 + d * 300, 1020)]))
                P.fill_mask(sl, H("#F1E6CF"))
                P.stroke([(500 + d * 260, 780), (500 + d * 312, 1020)], 7)
        if kind == "Puffer":
            for i in range(5):
                band = P.intersect(reg, P.m_rect(0, 750 + i * 58, 1000, 750 + i * 58 + 58))
                P.form_shade(band, 1.4)
                P.fill_mask(P.intersect(P.m_stroke([(100, 808 + i * 58), (900, 808 + i * 58)], 5), reg), INK, alpha=160)
        if kind == "Tracksuit":
            for d in (-1, 1):
                for k in (0, 22):
                    P.fill_mask(P.intersect(P.m_stroke([(500 + d * (230 + k), 790), (500 + d * (330 + k), 1020)], 11), reg), WHITE)
        _finish(ctx, reg, col)
        collar = P.intersect(P.subtract(P.m_ellipse(500, 748, 112, 44), P.m_ellipse(500, 740, 82, 28)), ctx.torso_mask)
        rib = {"Bomber Jacket": H("#2B2B2B"), "Varsity Jacket": col, "Tracksuit": col, "Puffer": shade(col, 0.85)}[kind]
        P.shape(collar, rib, outline=FO)
        if kind in ("Bomber Jacket", "Varsity Jacket"):
            lay = P.layer()
            for i in range(-10, 11):
                lay.stroke([(500 + i * 11, 700), (500 + i * 11, 800)], 3, color=H("#E8B04A") if kind == "Bomber Jacket" else WHITE, alpha=160)
            P.compose(lay, clip=collar)
        P.stroke([(500, 790), (500, 1020)], 7)
        P.stroke([(506, 790), (506, 1020)], 3, color=(200, 200, 210), alpha=200)
        P.rect(492, 800, 516, 836, P.gradient(SILVER, 90), radius=4, outline=4)
    elif kind in ("Denim Jacket", "Leather Jacket", "Suit"):
        if kind == "Suit":
            P.fill_mask(P.intersect(reg, P.m_poly([(430, 742), (570, 742), (500, 1020)])), WHITE)
            P.poly([(486, 770), (514, 770), (522, 960), (500, 990), (478, 960)], H("#C2283E"), outline=6)
            P.poly([(482, 752), (518, 752), (514, 778), (486, 778)], H("#A01F33"), outline=6)
        _finish(ctx, reg, col)
        for d in (-1, 1):
            lapel = [(500 + d * 70, 740), (500 + d * 150, 770), (500 + d * 110, 830), (500 + d * 150, 860), (500 + d * 26, 1000)]
            P.shape(P.intersect(P.m_poly(lapel), ctx.torso_mask), shade(col, 0.85) if kind != "Leather Jacket" else H("#3A3444"), outline=FO)
        if kind == "Denim Jacket":
            for d in (-1, 1):
                P.rect(500 + d * 160 - 50, 880, 500 + d * 160 + 50, 940, shade(col, 0.9), radius=6, outline=6)
                P.ellipse(500 + d * 160, 892, 8, fill=H("#D9A441"), outline=4)
            lay = P.layer()
            for xx in range(130, 880, 60):
                for yy in range(760, 1020, 18):
                    lay.stroke([(xx, yy), (xx, yy + 8)], 3, color=H("#E8B04A"), alpha=170)
            P.compose(lay, clip=P.subtract(reg, P.m_rect(200, 750, 800, 1020)))
        if kind == "Leather Jacket":
            P.stroke([(560, 780), (470, 1020)], 7)
            P.stroke([(565, 780), (475, 1020)], 3, color=(200, 200, 210))
            for x, y in ((380, 800), (620, 800), (330, 840), (670, 840)):
                P.ellipse(x, y, 9, fill=P.gradient(SILVER, 90), outline=4)
    elif kind == "Turtleneck":
        _finish(ctx, reg, col)
        for i in range(-6, 7):
            P.fill_mask(P.intersect(P.m_stroke([(500 + i * 13, 660), (500 + i * 13, 735)], 3), reg), WHITE, alpha=60)
        P.stroke([(410, 740), (590, 740)], 7)
    elif kind == "Space Suit":
        _finish(ctx, reg, col)
        ring = P.intersect(P.subtract(P.m_ellipse(500, 752, 160, 60), P.m_ellipse(500, 742, 100, 32)), ctx.torso_mask)
        P.shape(ring, P.gradient(SILVER, 90), outline=FO)
        P.rect(410, 860, 590, 960, H("#D8DCE6"), radius=12, outline=7)
        for i, c in enumerate(("#FF4D5E", "#FFC23C", "#3FB6FF")):
            P.ellipse(445 + i * 45, 890, 11, fill=H(c), outline=5)
        P.rect(440, 920, 560, 940, H("#2A1E3A"), radius=4, outline=0)
        P.ellipse(260, 880, 34, fill=H("#3E56B8"), outline=6)
        P.poly(star_pts(260, 880, 20, 8), WHITE, outline=0)
    elif kind == "Royal Cape":
        lay = P.layer()
        lay.fill_mask(P.m_rect(0, 742, 1000, 1000), P.gradient([(0, H("#C4244A")), (1, H("#6E0F2A"))], 90))
        P.compose(lay, clip=reg)
        _finish(ctx, reg, col)
        trim = P.intersect(P.subtract(P.m_ellipse(500, 760, 230, 80), P.m_ellipse(500, 735, 100, 34)), ctx.torso_mask)
        P.shape(trim, H("#F6F1E6"), outline=FO)
        lay = P.layer()
        for x in range(260, 760, 38):
            lay.poly([(x, 760), (x + 5, 770), (x, 780), (x - 5, 770)], INK, outline=0)
        P.compose(lay, clip=trim)
        for cx in (380, 620):
            P.ellipse(cx, 830, 24, fill=P.gradient(GOLD, 90), outline=6)
        P.stroke(quad((380, 840), (500, 900), (620, 840)), 8, color=H("#F2C14E"))
    else:
        raise KeyError(kind)


# =========================================================== accessories
def accessory(ctx, kind):
    P = ctx.P
    if kind == "None":
        return
    if kind in ("Silver Chain", "Gold Chain"):
        g = P.gradient(GOLD if kind == "Gold Chain" else SILVER, 90)
        pts = quad((400, 742), (500, 860), (600, 742), n=26)
        for i, (x, y) in enumerate(pts):
            P.ellipse(x, y, 13 if i % 2 else 10, 9 if i % 2 else 12, fill=g, outline=4)
        if kind == "Gold Chain":
            P.poly(star_pts(500, 832, 34, 15), g, outline=6)
    elif kind in ("Hoop Earring", "Stud Earring"):
        x, y = EARS["r"][0] + 40, EARS["r"][1] + 50
        if kind == "Hoop Earring":
            P.shape(P.subtract(P.m_ellipse(x, y + 30, 30), P.m_ellipse(x, y + 30, 21)), P.gradient(GOLD, 90), outline=5)
        else:
            P.ellipse(x, y + 4, 11, fill=P.gradient([(0, WHITE), (1, H("#9FE6FF"))], 45), outline=4)
            P.poly(star_pts(x - 3, y, 6, 2, 4), WHITE, outline=0)
    elif kind == "Nose Ring":
        P.shape(P.subtract(P.m_ellipse(500, 548, 22, 18), P.m_ellipse(500, 543, 15, 11)), P.gradient(SILVER, 90), outline=4)
    elif kind == "Sprout Pin":
        x, y = 660, 860
        P.ellipse(x, y, 34, fill=H("#F4F1EA"), outline=6)
        P.stroke([(x, y + 18), (x, y - 6)], 6, color=H("#3E9B4F"))
        for d in (-1, 1):
            P.ellipse(x + d * 12, y - 10, 12, 7, fill=H("#5DBB4A"), rot=d * -30, outline=4)
    elif kind == "Cheek Bandage":
        P.poly(superblob(680, 545, 56, 20, 6, 6, 60), H("#F2C9A0"), outline=6)
        for dx in (-24, 24):
            for dy in (-6, 6):
                P.ellipse(680 + dx * 0.4 + dy, 545 + dy, 2.5, fill=H("#C99A6A"), outline=0)
    elif kind == "Headset Mic":
        x, y = EARS["l"]
        P.ellipse(x + 20, y + 10, 30, fill=H("#2A2A36"))
        P.stroke(quad((x + 30, y + 30), (x + 60, y + 150), (430, 600)), 9)
        P.ellipse(430, 600, 16, fill=H("#2A2A36"))
    else:
        raise KeyError(kind)


# ============================================================== headwear
HIDES_ANTENNA = {"Beanie", "Backwards Cap", "Bucket Hat", "Bandana", "Beret", "Captain Hat", "Crown"}


def headwear(ctx, kind):
    P = ctx.P
    if kind in ("None", "Halo", "Headband", "Headphones", "Horns"):
        if kind == "None":
            return
    top = HEAD_TOP
    a, b = hw(top + 95)
    rx = (b - a) / 2 + 14
    if kind == "Beanie":
        cy = top + 112
        col = H("#2B2B36") if ctx.t["skin"] not in ("Midnight",) else H("#C2283E")
        dome = sorted([p for p in ellipse_pts(500, cy, rx, 120, n=140) if p[1] <= cy] + [(500 - rx, cy)], key=lambda p: math.atan2(p[1] - cy, p[0] - 500))
        m = P.m_poly(dome)
        P.shape(m, col)
        for i in range(-8, 9):
            P.fill_mask(P.intersect(P.m_stroke([(500 + i * 26, cy), (500 + i * 20, cy - 130)], 5), m), WHITE, alpha=40)
        P.rect(500 - rx - 12, cy - 40, 500 + rx + 12, cy + 30, shade(col, 0.85), radius=26)
        P.rect(470, cy - 26, 530, cy + 12, H("#F4F1EA"), radius=4, outline=5)
    elif kind == "Backwards Cap":
        cy = top + 100
        col = H("#C2283E")
        P.ellipse(500 - rx * 0.7, cy - 2, rx * 0.55, 22, fill=shade(col, 0.75), rot=8)
        dome = sorted([p for p in ellipse_pts(500, cy, rx, 112, n=140) if p[1] <= cy] + [(500 - rx, cy)], key=lambda p: math.atan2(p[1] - cy, p[0] - 500))
        m = P.m_poly(dome)
        P.shape(m, col)
        strap = P.intersect(m, P.m_rect(500 + rx * 0.12, cy - 52, 500 + rx * 0.55, cy + 4, radius=14))
        P.shape(strap, H("#F4F1EA"), outline=5)
        P.ellipse(500, cy - 108, 14, fill=shade(col, 0.8), outline=5)
        for i in (-1, 1):
            P.fill_mask(P.intersect(P.m_stroke(quad((500 + i * rx * 0.45, cy), (500 + i * rx * 0.3, cy - 80), (500, cy - 110)), 4), m), INK, alpha=110)
    elif kind == "Bucket Hat":
        by = top + 110
        col = H("#E8DCC0")
        P.poly([(500 - rx * 0.95, by), (500 - rx * 0.7, by - 125), (500 + rx * 0.7, by - 125), (500 + rx * 0.95, by)], col)
        P.fill_mask(P.m_rect(500 - rx * 0.86, by - 40, 500 + rx * 0.86, by - 18), shade(col, 0.75))
        brim = quad((500 - rx * 1.32, by + 36), (500, by - 40), (500 + rx * 1.32, by + 36)) + quad((500 + rx * 1.32, by + 36), (500, by + 20), (500 - rx * 1.32, by + 36))[1:]
        P.poly(brim, tint(col, 0.2))
        lay = P.layer()
        for i in range(6):
            lay.stroke(quad((500 - rx * 1.2, by + 30 - i * 3 + 0), (500, by - 30 + i * 6), (500 + rx * 1.2, by + 30)), 2.5, color=INK, alpha=70)
        P.compose(lay, clip=P.m_poly(brim))
    elif kind == "Bandana":
        cy = top + 120
        col = H("#2D4FA8")
        dome = sorted([p for p in ellipse_pts(500, cy, rx - 4, 118, n=140) if p[1] <= cy] + [(500 - rx, cy)], key=lambda p: math.atan2(p[1] - cy, p[0] - 500))
        m = P.m_poly(dome)
        P.shape(m, col)
        lay = P.layer()
        for (x, y) in ((420, cy - 60), (520, cy - 80), (600, cy - 40), (470, cy - 20), (360, cy - 20)):
            lay.ellipse(x, y, 12, 7, fill=WHITE, outline=0, rot=30)
            lay.ellipse(x + 10, y - 8, 4, fill=WHITE, outline=0)
        P.compose(lay, clip=m)
        P.poly([(500 + rx - 20, cy - 20), (500 + rx + 70, cy + 30), (500 + rx + 40, cy + 70), (500 + rx - 10, cy + 10)], col, outline=FO)
    elif kind == "Headband":
        y = top + 105
        a, b = hw(y)
        band = P.intersect(ctx.head_mask, P.m_rect(0, y - 26, 1000, y + 26))
        P.fill_mask(band, WHITE)
        P.fill_mask(P.intersect(band, P.m_rect(0, y - 8, 1000, y + 8)), H("#C2283E"))
        P.form_shade(band)
        P.fill_mask(P.subtract(P.intersect(P.ink_line(band, FO), ctx.head_mask), band), INK)
    elif kind == "Headphones":
        P.stroke([p for p in ellipse_pts(500, 440, 300, 270, n=100) if p[1] < 360], 26, color=INK)
        P.stroke([p for p in ellipse_pts(500, 440, 300, 270, n=100) if p[1] < 360], 14, color=H("#E8E4DC"))
        for x in (220, 780):
            P.rect(x - 40, 380, x + 40, 520, H("#2A2A36"), radius=34)
            P.rect(x - 22, 400, x + 22, 500, H("#FF6B3D"), radius=18, outline=5)
    elif kind == "Beret":
        cy = top + 60
        P.ellipse(470, cy, rx * 0.95, 70, fill=H("#1E1828"), rot=-8)
        P.stroke([(480, cy - 66), (488, cy - 92)], 10)
    elif kind == "Captain Hat":
        by = top + 105
        col = H("#F4F1EA")
        P.poly(quad((500 - rx * 0.95, by), (500, by - 230), (500 + rx * 0.95, by)) + [(500 + rx * 0.9, by + 6), (500 - rx * 0.9, by + 6)], col)
        P.rect(500 - rx * 0.9, by - 46, 500 + rx * 0.9, by + 6, H("#1E2A55"), radius=10)
        P.poly(quad((500 - rx * 0.75, by), (500, by + 60), (500 + rx * 0.75, by)), H("#141826"))
        P.shape(P.m_poly(star_pts(500, by - 20, 28, 12)), P.gradient(GOLD, 90), outline=5)
        P.stroke(quad((500 - rx * 0.7, by + 2), (500, by + 20), (500 + rx * 0.7, by + 2)), 6, color=H("#F2C14E"))
    elif kind == "Halo":
        cy = top - 50
        ring = P.subtract(P.m_ellipse(500, cy, 150, 36), P.m_ellipse(500, cy + 3, 112, 19))
        P.glow(ring, H("#FFE38A"), 18, alpha=220)
        P.shape(ring, P.gradient(GOLD, 90), outline=7)
    elif kind == "Horns":
        for d in (-1, 1):
            base = (500 + d * 150, top + 70)
            pts = cubic((base[0] - d * 40, base[1] + 20), (base[0] - d * 30, base[1] - 120), (base[0] + d * 90, base[1] - 150), (base[0] + d * 110, base[1] - 210)) + \
                cubic((base[0] + d * 110, base[1] - 210), (base[0] + d * 50, base[1] - 120), (base[0] + d * 40, base[1] - 40), (base[0] + d * 50, base[1] + 10))[1:]
            P.poly(pts, P.gradient([(0, H("#F4EAD8")), (1, H("#8C6A4E"))], 90))
            for k in range(4):
                p = pts[6 + k * 5]
                P.stroke([(p[0] - 14, p[1] + 4), (p[0] + 18, p[1] + 10)], 4, alpha=120)
    elif kind == "Crown":
        by = top + 70
        r2 = 150
        pts = [(500 - r2, by), (500 - r2 * 1.1, by - 130), (500 - r2 * 0.5, by - 70), (500, by - 165), (500 + r2 * 0.5, by - 70),
               (500 + r2 * 1.1, by - 130), (500 + r2, by)]
        P.glow(P.m_poly(pts), H("#FFD86B"), 24, alpha=170)
        P.poly(pts, P.gradient(GOLD, 80))
        P.rect(500 - r2 * 1.05, by - 34, 500 + r2 * 1.05, by + 10, P.gradient(GOLD, 90), radius=8)
        for x, c in ((500 - r2 * 0.55, "#C2283E"), (500, "#2EC4B6"), (500 + r2 * 0.55, "#7B5CFF")):
            P.ellipse(x, by - 12, 15, fill=H(c), outline=5)
            P.ellipse(x - 5, by - 17, 4, fill=WHITE, outline=0)
        for x, y in ((500 - r2 * 1.1, by - 130), (500, by - 165), (500 + r2 * 1.1, by - 130)):
            P.ellipse(x, y, 13, fill=H("#F6F1E6"), outline=5)
    else:
        raise KeyError(kind)


# ============================================================ background
FLATS = {"Tangerine": "#F2994A", "Bubblegum": "#F7A1C4", "Seafoam": "#79D2BE", "Butter": "#F6D365", "Periwinkle": "#94A3F5",
         "Clay": "#D9785B", "Sage": "#A3BE8C", "Slate": "#6C7A96"}
DUOS = {"Duotone Dusk": ("#F7A072", "#8E5CC4"), "Duotone Lagoon": ("#7DE2D1", "#3B6FD9"), "Duotone Peach": ("#FFD6A5", "#FF8FAB")}


def background(ctx, kind):
    P = ctx.bg
    full = P.m_rect(0, 0, 1000, 1000)
    if kind in FLATS:
        P.fill_mask(full, H(FLATS[kind]))
    elif kind in DUOS:
        a, b = DUOS[kind]
        P.fill_mask(full, P.gradient([(0, H(a)), (1, H(b))], 70))
    elif kind == "Halftone Burst":
        P.fill_mask(full, H("#FFD23F"))
        P.halftone(P.m_ellipse(500, 450, 640).filter(ImageFilter.GaussianBlur(120 * P.s)), spacing=22, max_r=9, alpha=255, color=H("#FF7A3D"))
    elif kind == "Comic Rays":
        P.fill_mask(full, H("#3FA7F5"))
        for i in range(0, 40, 2):
            a0, a1 = math.radians(i * 9), math.radians((i + 1) * 9)
            P.poly([(500, 450), (500 + 1500 * math.cos(a0), 450 + 1500 * math.sin(a0)), (500 + 1500 * math.cos(a1), 450 + 1500 * math.sin(a1))],
                   H("#6EC1FF"), outline=0)
    elif kind == "Brick Wall":
        P.fill_mask(full, H("#B5533C"))
        for r in range(0, 22):
            y = r * 48
            P.stroke([(0, y), (1000, y)], 6, color=H("#E8C9B0"), alpha=200)
            for c in range(0, 9):
                x = c * 130 + (65 if r % 2 else 0)
                P.stroke([(x, y), (x, y + 48)], 6, color=H("#E8C9B0"), alpha=200)
        P.fill_mask(P.pressure().point(lambda v: max(0, v - 120) * 2), H("#7A2E22"), alpha=90)
    elif kind == "Holographic":
        P.fill_mask(full, P.gradient([(0, H("#B5F3FF")), (0.33, H("#E3C6FF")), (0.66, H("#FFC9E8")), (1, H("#FFF1B8"))], 35))
        for i in range(-6, 12):
            P.stroke([(i * 110, 0), (i * 110 + 600, 1000)], 40, color=WHITE, alpha=55)
    elif kind == "Gold Leaf":
        P.fill_mask(full, P.gradient([(0, H("#FFE9A3")), (0.5, H("#E9B949")), (1, H("#B88316"))], 60))
        P.fill_mask(P.pressure().point(lambda v: max(0, v - 130) * 2), H("#FFF6D0"), alpha=120)
    elif kind == "Cosmos":
        P.fill_mask(full, P.gradient([(0, H("#0D0A26")), (1, H("#2B1658"))], 120))
        for x, y, r, c in ((250, 280, 260, "#7B5CFF"), (780, 720, 300, "#FF5FA2"), (760, 200, 160, "#2EC4B6")):
            P.glow(P.m_ellipse(x, y, r), H(c), 80, alpha=120)
        for _ in range(110):
            P.ellipse(ctx.rng.uniform(0, 1000), ctx.rng.uniform(0, 1000), ctx.rng.uniform(1.5, 4.5), fill=WHITE, outline=0,
                      alpha=int(ctx.rng.uniform(120, 255)))
    else:
        raise KeyError(kind)
