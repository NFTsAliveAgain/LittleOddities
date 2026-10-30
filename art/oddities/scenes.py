"""Backgrounds, body Patterns and Special Features."""
from __future__ import annotations

import math

from .paint import (FEATURE_OUTLINE as FO, INK, WHITE, cubic, ellipse_pts, heart_pts, hex_rgb, quad, shade,
                    soft_star_pts, star_pts, tint)

H = hex_rgb


# ------------------------------------------------------------- backgrounds
def _cloud(P, cx, cy, s, fill, outline=0, alpha=255):
    m = P.union(*[P.m_ellipse(cx + dx * s, cy + dy * s, r * s) for dx, dy, r in
                  ((-1.0, 0.2, 0.7), (0, -0.3, 1.0), (1.0, 0.15, 0.75), (0.45, 0.4, 0.6), (-0.45, 0.45, 0.6))])
    P.shape(m, fill, outline=outline, alpha=alpha)
    return m


FLAT = {"Flat Tangerine": "#FF9F43", "Flat Bubblegum": "#FF9EC8", "Flat Seafoam": "#7EDCC6", "Flat Butter": "#FFE27A",
        "Flat Periwinkle": "#9AA8FF", "Flat Ink": "#2A1E3A", "Flat Clay": "#E07A5F", "Flat Sage": "#A8C69F"}


def background(ctx, kind):
    P, rng = ctx.P, ctx.rng
    full = P.m_rect(0, 0, 1000, 1000)
    if kind in FLAT:
        P.fill_mask(full, H(FLAT[kind]))
        return

    def base(c):
        P.fill_mask(full, H(c))

    if kind == "Cream Dots":
        base("#FFF1D6")
        for row in range(11):
            for col in range(11):
                x = col * 100 + (50 if row % 2 else 0)
                P.ellipse(x, row * 100, 14, fill=H("#F6DDAE"), outline=0)
    elif kind == "Peach Sunburst":
        base("#FFD2B8")
        for i in range(0, 24, 2):
            a0, a1 = math.radians(i * 15), math.radians((i + 1) * 15)
            P.poly([(500, 620), (500 + 1500 * math.cos(a0), 620 + 1500 * math.sin(a0)),
                    (500 + 1500 * math.cos(a1), 620 + 1500 * math.sin(a1))], H("#FFC2A0"), outline=0)
    elif kind == "Mint Waves":
        base("#CFF5DF")
        for i in range(-1, 12):
            pts = [(x, i * 95 + 26 * math.sin(x / 1000 * 4 * math.pi)) for x in range(-20, 1040, 20)]
            P.stroke(pts, 30, color=H("#B6EBCD"))
    elif kind == "Sky Clouds":
        base("#CFE9FF")
        for (x, y, s) in ((150, 170, 70), (820, 120, 55), (870, 560, 60), (120, 640, 50), (480, 70, 40)):
            _cloud(P, x, y, s, WHITE, alpha=230)
    elif kind == "Lilac Checker":
        base("#E6DCFF")
        for r in range(8):
            for c in range(8):
                if (r + c) % 2:
                    P.rect(c * 125, r * 125, c * 125 + 125, r * 125 + 125, H("#D8CBFA"), outline=0)
    elif kind == "Butter Confetti":
        base("#FFF3B8")
        cols = [H(c) for c in ("#FF8FC7", "#6BB8FF", "#8EE3B0", "#FF8A5C", "#B79CFF")]
        for i in range(46):
            x, y = rng.uniform(20, 980), rng.uniform(20, 980)
            P.poly(_rot_rect(x, y, 15, 5, rng.uniform(0, 180)), rng.choice(cols), outline=0, alpha=210)
    elif kind == "Rose Stripes":
        base("#FFD9E6")
        for i in range(-10, 20):
            x = i * 90
            P.poly([(x, 0), (x + 45, 0), (x + 45 - 1000, 1000), (x - 1000, 1000)], H("#FFC9DB"), outline=0)
    elif kind == "Sage Spotlight":
        base("#DCE8D2")
        P.ellipse(500, 590, 400, fill=H("#E9F1E1"), outline=0)
    elif kind == "Tangerine Rays":
        base("#FFB766")
        for i in range(0, 36, 2):
            a0, a1 = math.radians(i * 10), math.radians((i + 1) * 10)
            P.poly([(500, 600), (500 + 1500 * math.cos(a0), 600 + 1500 * math.sin(a0)),
                    (500 + 1500 * math.cos(a1), 600 + 1500 * math.sin(a1))], H("#FFA44D"), outline=0)
        P.ellipse(500, 600, 330, fill=H("#FFC57F"), outline=0, alpha=150)
    elif kind == "Seafoam Scallops":
        base("#C9F1EA")
        for r in range(13):
            for c in range(12):
                x, y = c * 90 + (45 if r % 2 else 0), r * 80
                P.ellipse(x, y, 45, fill=H("#B3E8DE") if (r % 2) else H("#BFEDE4"), outline=0)
                P.stroke([(x + 40 * math.cos(t), y + 40 * math.sin(t)) for t in [math.pi * k / 16 for k in range(17)]], 4, color=H("#A6DFD4"))
    elif kind == "Periwinkle Hills":
        P.fill_mask(full, P.gradient([(0, H("#C7D2FF")), (1, H("#E8ECFF"))], 90))
        P.ellipse(820, 180, 60, fill=H("#FFF4C2"), outline=0)
        P.ellipse(200, 1150, 520, 330, fill=H("#A7E3A1"), outline=0)
        P.ellipse(850, 1120, 520, 300, fill=H("#8FD68A"), outline=0)
    elif kind == "Twilight Stars":
        P.fill_mask(full, P.gradient([(0, H("#1D2257")), (1, H("#4B3D8F"))], 90))
        for i in range(60):
            x, y, s = rng.uniform(0, 1000), rng.uniform(0, 1000), rng.uniform(2, 5)
            P.ellipse(x, y, s, fill=WHITE, outline=0, alpha=int(rng.uniform(120, 255)))
        for (x, y, s) in ((140, 160, 22), (860, 260, 16), (110, 760, 14)):
            P.poly(star_pts(x, y, s, s * 0.4, 4), H("#FFE9A8"), outline=0)
        moon = P.subtract(P.m_ellipse(820, 150, 62), P.m_ellipse(848, 130, 56))
        P.fill_mask(moon, H("#FFE9A8"))
    elif kind == "Sunset Gradient":
        P.fill_mask(full, P.gradient([(0, H("#FF9E6B")), (0.55, H("#FF7FA8")), (1, H("#8C6BD6"))], 90))
        P.ellipse(500, 700, 330, fill=H("#FFD27A"), outline=0, alpha=170)
    elif kind == "Dream Clouds":
        P.fill_mask(full, P.gradient([(0, H("#FFD6F0")), (0.5, H("#E3D4FF")), (1, H("#C8E7FF"))], 60))
        for (x, y, s) in ((140, 230, 80), (860, 180, 70), (900, 700, 75), (110, 760, 70)):
            _cloud(P, x, y, s, WHITE, alpha=200)
        for i in range(20):
            x, y, s = rng.uniform(40, 960), rng.uniform(40, 960), rng.uniform(6, 12)
            P.poly(star_pts(x, y, s, s * 0.4, 4), WHITE, outline=0, alpha=200)
    elif kind == "Rainbow Arc":
        base("#FFF6E5")
        cols = ["#FF6B6B", "#FFA94D", "#FFD43B", "#69DB7C", "#4DABF7", "#9775FA"]
        for i, c in enumerate(cols):
            P.ellipse(500, 760, 470 - i * 42, fill=H(c), outline=0)
        P.ellipse(500, 760, 470 - 6 * 42, fill=H("#FFF6E5"), outline=0)
        _cloud(P, 90, 760, 60, WHITE)
        _cloud(P, 910, 760, 60, WHITE)
    elif kind == "Golden Hour":
        P.fill_mask(full, P.gradient([(0, H("#FFE7A3")), (1, H("#F4B23E"))], 90))
        for i in range(0, 32, 2):
            a0, a1 = math.radians(i * 11.25), math.radians((i + 1) * 11.25)
            P.poly([(500, 600), (500 + 1500 * math.cos(a0), 600 + 1500 * math.sin(a0)),
                    (500 + 1500 * math.cos(a1), 600 + 1500 * math.sin(a1))], H("#FFF2C4"), outline=0, alpha=110)
        for i in range(24):
            x, y, s = rng.uniform(40, 960), rng.uniform(40, 960), rng.uniform(5, 11)
            P.poly(star_pts(x, y, s, s * 0.35, 4), WHITE, outline=0, alpha=220)
    elif kind == "Cosmic Void":
        P.fill_mask(full, P.gradient([(0, H("#120C2E")), (1, H("#2B1658"))], 120))
        for (x, y, r, c) in ((250, 300, 260, "#7B5CFF"), (780, 700, 300, "#FF5FA2"), (700, 220, 160, "#2EC4B6")):
            P.glow(P.m_ellipse(x, y, r), H(c), 80, alpha=120)
        for i in range(90):
            x, y, s = rng.uniform(0, 1000), rng.uniform(0, 1000), rng.uniform(1.5, 4.5)
            P.ellipse(x, y, s, fill=WHITE, outline=0, alpha=int(rng.uniform(140, 255)))
        P.ellipse(150, 830, 44, fill=H("#FFB86B"))
        P.shape(P.subtract(P.m_ellipse(150, 830, 82, 16, rot=-18), P.m_ellipse(150, 822, 46, 10, rot=-18)), H("#FFE0B0"), outline=5)
    else:
        raise KeyError(kind)


def _rot_rect(x, y, hw, hh, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(x + dx * c - dy * s, y + dx * s + dy * c) for dx, dy in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]


# ---------------------------------------------------------------- patterns
def pattern(ctx, kind):
    """Drawn on a separate layer, clipped to the body interior."""
    if kind == "None":
        return
    P, b, rng = ctx.P, ctx.body, ctx.prng
    lay = P.layer()
    dark = shade(ctx.skin_base, 0.8)
    light = tint(ctx.skin_base, 0.45)
    top, bot = b.top, b.bottom
    if kind == "Spots":
        for (dx, dy, r) in ((-0.32, 0.18, 34), (0.3, 0.1, 24), (0.36, 0.55, 40), (-0.25, 0.68, 28), (0.05, 0.86, 22),
                            (-0.42, 0.42, 18), (0.12, 0.02, 16)):
            lay.ellipse(500 + dx * 520, top + dy * (bot - top), r, fill=dark, outline=0, alpha=170)
    elif kind == "Stripes":
        for i in range(10):
            y = top + 40 + i * 70
            pts = [(x, y + 10 * math.sin(x / 70)) for x in range(150, 860, 15)]
            lay.stroke(pts, 26, color=dark, alpha=150)
    elif kind == "Belly Patch":
        lay.ellipse(500, b.cloth_y + 40, b.w(b.cloth_y) * 0.3, (bot - b.cloth_y) * 0.62, fill=light, outline=0)
    elif kind == "Zigzag":
        y = b.top + (bot - top) * 0.52
        pts = [(x, y + (24 if (x // 40) % 2 else -24)) for x in range(140, 880, 40)]
        lay.stroke(pts, 34, color=dark, alpha=170)
        lay.stroke([(x, yy + 70) for x, yy in pts], 18, color=light, alpha=220)
    elif kind == "Patchwork":
        for (cx, cy, s, rot) in ((0.3, 0.3, 50, 12), (-0.28, 0.7, 42, -8)):
            x, y = 500 + cx * b.face_w, top + cy * (bot - top)
            pts = _rot_rect(x, y, s, s * 0.85, rot)
            lay.poly(pts, light, outline=0)
            for i in range(4):
                p0, p1 = pts[i], pts[(i + 1) % 4]
                for t in range(1, 6):
                    u = t / 6
                    px, py = p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u
                    nx, ny = (x - px) * 0.12, (y - py) * 0.12
                    lay.stroke([(px - nx * 0.6, py - ny * 0.6), (px + nx * 0.6, py + ny * 0.6)], 4, color=INK)
    elif kind == "Star Speckles":
        for i in range(14):
            x, y = rng.uniform(220, 780), rng.uniform(top + 40, bot - 30)
            s = rng.uniform(9, 17)
            lay.poly(star_pts(x, y, s, s * 0.45), light, outline=0, alpha=230)
    elif kind == "Swirl":
        cx, cy = 500 + b.face_w * 0.2, top + (bot - top) * 0.7
        pts = [(cx + 6 * t * math.cos(t), cy + 6 * t * math.sin(t)) for t in [i / 10 for i in range(0, 190)]]
        lay.stroke(pts, 16, color=dark, alpha=150)
    elif kind == "Constellation":
        g = lay.gradient([(0, H("#2A1E6E")), (1, H("#5B3FB8"))], 90)
        lay.fill_mask(ctx.body_mask, g)
        pts = [(rng.uniform(250, 750), rng.uniform(top + 60, bot - 40)) for _ in range(6)]
        pts.sort()
        lay.stroke(pts, 3, color=WHITE, alpha=150)
        for x, y in pts:
            lay.poly(star_pts(x, y, 12, 5, 4), WHITE, outline=0)
        for i in range(40):
            lay.ellipse(rng.uniform(150, 850), rng.uniform(top, bot), rng.uniform(1.5, 3.5), fill=WHITE, outline=0, alpha=200)
    else:
        raise KeyError(kind)
    P.compose(lay, clip=ctx.body_mask)


# ---------------------------------------------------------------- specials
def special_back(ctx, kind):
    P, b = ctx.P, ctx.body
    if kind == "Glow Aura":
        P.glow(P.m_poly(b.poly), H("#FFF6C8"), 45, alpha=255)
        P.glow(P.m_poly(b.poly), H("#FFFFFF"), 20, alpha=200)
    elif kind == "Stardust Orbit":
        _orbit(ctx, back=True)


def _orbit_pts(b):
    cy = b.top + (b.bottom - b.top) * 0.55
    return ellipse_pts(500, cy, 400, 92, rot=-12, n=160)


def _orbit(ctx, back):
    P, b = ctx.P, ctx.body
    pts = _orbit_pts(b)
    seg = pts[80:] + [pts[0]] if back else pts[:81]
    P.stroke(seg, 9, color=WHITE, alpha=230)
    P.stroke(seg, 3, color=H("#F6C445"), alpha=255)
    if not back:
        for idx, (r, c) in ((20, (24, "#7B5CFF")), (52, (16, "#2EC4B6")), (70, (12, "#FF8FC7"))):
            P.ellipse(*pts[idx], r, fill=H(c), outline=6)
        P.poly(star_pts(*pts[38], 22, 9), H("#F6C445"), outline=5)


def special(ctx, kind):
    P, b = ctx.P, ctx.body
    fx, fy = b.face
    fs = b.fs
    if kind in ("None", "Glow Aura"):
        return
    if kind == "Sweat Drop":
        x, y = fx + b.face_w * 0.43, fy - 70 * fs
        drop = cubic((x, y - 34), (x + 28, y + 2), (x + 22, y + 26), (x, y + 26)) + \
            cubic((x, y + 26), (x - 22, y + 26), (x - 28, y + 2), (x, y - 34))[1:]
        P.poly(drop, H("#9ED8FF"), outline=6)
        P.ellipse(x - 7, y + 8, 5, 8, fill=WHITE, outline=0)
    elif kind == "Sparkles":
        for (x, y, s) in ((170, 300, 34), (840, 400, 26), (150, 620, 20), (860, 700, 30)):
            P.poly(star_pts(x, y, s, s * 0.32, 4), H("#FFF7D1"), outline=6)
    elif kind == "Heart Bubbles":
        for (x, y, s) in ((800, 300, 40), (860, 200, 28), (790, 130, 20)):
            P.poly(heart_pts(x, y, s), H("#FF6F91"), outline=6)
            P.ellipse(x - s * 0.4, y - s * 0.35, s * 0.15, fill=WHITE, outline=0)
    elif kind == "Bubbles":
        for (x, y, r) in ((820, 520, 34), (860, 420, 22), (800, 330, 16), (170, 470, 26), (140, 380, 14)):
            P.ellipse(x, y, r, fill=H("#DFF6FF"), outline=5, alpha=200)
            P.ellipse(x - r * 0.35, y - r * 0.35, r * 0.25, fill=WHITE, outline=0)
    elif kind == "Rain Cloud":
        x, y = 215, 205
        for i, dx in enumerate((-50, 0, 50)):
            P.poly(_drop(x + dx, y + 90 + (i % 2) * 30, 14), H("#6BB8FF"), outline=5)
        _cloud(P, x, y, 58, H("#C9CFE0"), outline=FO)
    elif kind == "Little Buddy":
        x, y = 830, 880
        m = P.m_poly(soft_star_pts(x, y, 56, points=7, depth=0.04))
        P.shape(m, H("#B5A6FF"))
        P.ellipse(x - 16, y - 8, 7, 9, fill=INK, outline=0)
        P.ellipse(x + 16, y - 8, 7, 9, fill=INK, outline=0)
        P.stroke(quad((x - 14, y + 14), (x, y + 26), (x + 14, y + 14)), 5)
        P.ellipse(x - 8, y - 66, 12, fill=H("#FFC23C"))
        P.stroke([(x - 2, y - 52), (x - 6, y - 56)], 5)
    elif kind == "Stardust Orbit":
        _orbit(ctx, back=False)
    else:
        raise KeyError(kind)


def _drop(x, y, s):
    return cubic((x, y - 2 * s), (x + 1.6 * s, y), (x + 1.2 * s, y + 1.5 * s), (x, y + 1.5 * s)) + \
        cubic((x, y + 1.5 * s), (x - 1.2 * s, y + 1.5 * s), (x - 1.6 * s, y), (x, y - 2 * s))[1:]
