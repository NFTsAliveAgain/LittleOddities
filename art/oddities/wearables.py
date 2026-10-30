"""Headwear, Clothing and Accessories."""
from __future__ import annotations

import math

from .bodies import draw_arm
from .paint import (FEATURE_OUTLINE as FO, INK, OUTLINE, WHITE, cubic, ellipse_pts, heart_pts, hex_rgb, quad,
                    rotate, shade, star_pts, superellipse_pts, tint)

C = {k: hex_rgb(v) for k, v in {
    "tomato": "#FF5A3C", "mustard": "#FFC23C", "teal": "#1FB5A8", "pink": "#FF8FC7", "grape": "#7B5CFF",
    "mint": "#8EE3B0", "sky": "#6BB8FF", "cream": "#FFF1D6", "navy": "#2D3A7A", "leaf": "#5DBB4A",
    "orange": "#FF8A1F", "denim": "#4C7BD9", "red": "#E8384F", "purple": "#7A3FA0", "gold": "#F6C445",
    "brown": "#9A6440", "charcoal": "#33304A", "lilac": "#C7B3FF",
}.items()}


FAM = {"tomato": {"red", "orange"}, "mustard": {"yellow", "orange"}, "teal": {"teal", "green"}, "pink": {"pink", "red"},
       "mint": {"green", "teal"}, "sky": {"blue"}, "red": {"red", "pink", "orange"}, "navy": {"blue", "dark"},
       "grape": {"purple"}, "orange": {"orange", "yellow"}, "denim": {"blue"}, "purple": {"purple", "dark"}}


def pick(ctx, *names):
    """First colour whose family doesn't clash with the skin (keeps garments visible)."""
    for n in names:
        if not FAM.get(n, set()) & set(ctx.skin_families):
            return C[n]
    return C[names[-1]]


def gold_fill(P):
    return P.gradient([(0, hex_rgb("#FFF0A8")), (0.45, hex_rgb("#F6C445")), (1, hex_rgb("#C98A12"))], 70)


# ---------------------------------------------------------------- headwear
def headwear(ctx, kind):
    P, b = ctx.P, ctx.body
    hx, hy = b.head_x, b.top
    hw = b.w(hy + 50)
    k = max(0.62, min(1.12, hw / 300))
    if kind == "None":
        return
    if kind == "Beanie":
        cy = hy + 78
        rx = b.w(cy) / 2 + 12
        ry = min(rx * 0.78, 135)
        dome = [p for p in ellipse_pts(hx, cy, rx, ry, n=120) if p[1] <= cy] + [(hx - rx, cy)]
        dome.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - hx))
        col = pick(ctx, "tomato", "teal", "grape")
        m = P.m_poly(dome)
        P.shape(m, col)
        for i in range(-3, 4):
            P.fill_mask(P.intersect(P.m_stroke([(hx + i * rx / 4, cy), (hx + i * rx / 5.5, cy - ry)], 6), m), shade(col, 0.8))
        P.rect(hx - rx - 10, cy - 30, hx + rx + 10, cy + 22, shade(col, 0.85), radius=22)
        P.ellipse(hx, cy - ry - 18, 34 * k, fill=C["cream"])
    elif kind == "Party Hat":
        base = (hx + 12, hy + 34)
        pts = [(base[0] - 82 * k, base[1]), (base[0], base[1] - 215 * k), (base[0] + 82 * k, base[1])]
        pts = rotate(pts, *base, 12)
        m = P.m_poly(pts)
        P.shape(m, pick(ctx, "pink", "sky"))
        lay = P.layer()
        for i in range(5):
            y = base[1] - 40 * k * i - 10
            lay.poly(rotate(star_pts(base[0] + (i % 2 * 2 - 1) * 26 * k, y, 14 * k, 6 * k), *base, 12), C["mustard"], outline=0)
        P.compose(lay, clip=m)
        tip = pts[1]
        P.ellipse(tip[0], tip[1] - 6, 22 * k, fill=C["mustard"])
    elif kind == "Bucket Hat":
        by = hy + 62
        rx = b.w(by) / 2 + 4
        crown = [(hx - rx * 0.92, by), (hx - rx * 0.66, by - 112 * k), (hx + rx * 0.66, by - 112 * k), (hx + rx * 0.92, by)]
        hat = pick(ctx, "mint", "pink", "sky")
        P.poly(crown + [(hx, by + 6)], hat)
        P.fill_mask(P.m_rect(hx - rx * 0.86, by - 36 * k, hx + rx * 0.86, by - 16 * k), shade(hat, 0.8))
        brim = quad((hx - rx * 1.38, by + 30), (hx, by - 34), (hx + rx * 1.38, by + 30)) + \
            quad((hx + rx * 1.38, by + 30), (hx, by + 18), (hx - rx * 1.38, by + 30))[1:]
        P.poly(brim, tint(hat, 0.25))
    elif kind == "Sprout":
        base = (hx + 4, hy + 14)
        topp = (hx + 18, hy - 92 * k)
        P.stroke(quad(base, (hx - 18, hy - 40), topp), 16, color=INK)
        P.stroke(quad(base, (hx - 18, hy - 40), topp), 8, color=C["leaf"])
        for d in (-1, 1):
            tip = (topp[0] + d * 92 * k, topp[1] - 34 * k)
            leaf = cubic(topp, (topp[0] + d * 20 * k, topp[1] - 60 * k), (tip[0] - d * 10, tip[1] - 30 * k), tip) + \
                cubic(tip, (tip[0] - d * 20 * k, tip[1] + 34 * k), (topp[0] + d * 40 * k, topp[1] + 18 * k), topp)[1:]
            P.poly(leaf, C["leaf"] if d < 0 else tint(C["leaf"], 0.2), outline=FO)
            P.stroke([topp, ((topp[0] + tip[0]) / 2, (topp[1] + tip[1]) / 2 - 6)], 4, color=shade(C["leaf"], 0.7))
    elif kind == "Antenna Bobbles":
        for d in (-1, 1):
            base = (hx + d * 52 * k, hy + 30)
            end = (hx + d * 112 * k, hy - 112 * k)
            P.stroke(quad(base, (hx + d * 40 * k, hy - 60 * k), end), 9)
            P.ellipse(end[0], end[1], 26 * k, fill=C["mustard"] if d < 0 else C["teal"])
    elif kind == "Flower":
        cx, cy = hx + hw * 0.34, hy + 40
        for i in range(5):
            a = math.radians(i * 72 - 90)
            P.ellipse(cx + 34 * k * math.cos(a), cy + 34 * k * math.sin(a), 30 * k, 22 * k, fill=WHITE, rot=i * 72 - 90)
        P.ellipse(cx, cy, 22 * k, fill=C["mustard"])
    elif kind == "Propeller Cap":
        cy = hy + 70
        rx = b.w(cy) / 2 + 10
        ry = min(rx * 0.62, 118)
        dome = sorted([p for p in ellipse_pts(hx, cy, rx, ry, n=120) if p[1] <= cy] + [(hx - rx, cy)],
                      key=lambda p: math.atan2(p[1] - cy, p[0] - hx))
        P.ellipse(hx + rx * 0.62, cy - 4, rx * 0.62, 22, fill=C["red"])
        m = P.m_poly(dome)
        P.shape(m, C["red"])
        lay = P.layer()
        cols = [C["mustard"], C["sky"], C["mustard"], C["sky"]]
        for i in range(4):
            a0, a1 = math.pi + i * math.pi / 4, math.pi + (i + 0.5) * math.pi / 4
            lay.poly([(hx, cy), (hx + 400 * math.cos(a0), cy + 400 * math.sin(a0)), (hx + 400 * math.cos(a1), cy + 400 * math.sin(a1))],
                     cols[i], outline=0)
        P.compose(lay, clip=m)
        P.shape(P.subtract(P.dilate(m, OUTLINE), m), INK, outline=0)
        st = (hx, cy - ry - 34)
        P.stroke([(hx, cy - ry + 4), st], 10)
        P.ellipse(st[0] - 54 * k, st[1], 54 * k, 15 * k, fill=C["teal"], rot=-6)
        P.ellipse(st[0] + 54 * k, st[1], 54 * k, 15 * k, fill=C["tomato"], rot=-6)
        P.ellipse(*st, 11, fill=C["mustard"])
    elif kind == "Tiny Top Hat":
        bx, by = hx + hw * 0.16, hy + 30
        crown = [(bx - 46 * k, by), (bx - 42 * k, by - 120 * k), (bx + 42 * k, by - 120 * k), (bx + 46 * k, by)]
        P.ellipse(*rotate([(bx, by)], bx, by, 0)[0], 82 * k, 18 * k, fill=C["charcoal"], rot=10)
        P.poly(rotate(crown, bx, by, 10), C["charcoal"])
        P.poly(rotate([(bx - 45 * k, by - 22 * k), (bx + 45 * k, by - 22 * k), (bx + 44 * k, by - 44 * k), (bx - 44 * k, by - 44 * k)], bx, by, 10),
               C["red"], outline=5)
    elif kind == "Chef Hat":
        by = hy + 52
        rx = min(b.w(by) / 2, 170)
        puffs = [P.m_ellipse(hx + dx * rx, by - 70 * k + dy * k, r * k) for dx, dy, r in
                 ((-0.62, 0, 62), (0.62, 0, 62), (-0.3, -60, 66), (0.3, -60, 66), (0, -10, 70))]
        P.shape(P.union(*puffs), WHITE)
        P.rect(hx - rx * 0.86, by - 52 * k, hx + rx * 0.86, by + 10, WHITE, radius=14)
        for i in (-1, 0, 1):
            P.stroke([(hx + i * rx * 0.4, by - 44 * k), (hx + i * rx * 0.4, by - 4)], 4, color=(205, 200, 210))
    elif kind == "Paper Boat":
        by = hy + 38
        hull = [(hx - 140 * k, by - 48 * k), (hx + 140 * k, by - 48 * k), (hx + 92 * k, by + 10), (hx - 92 * k, by + 10)]
        sail = [(hx - 70 * k, by - 48 * k), (hx + 8 * k, by - 170 * k), (hx + 70 * k, by - 48 * k)]
        P.poly(sail, tint(C["sky"], 0.55))
        P.poly(hull, C["cream"])
        P.stroke([(hx + 8 * k, by - 160 * k), (hx + 4 * k, by - 52 * k)], 4, color=shade(C["sky"], 0.7))
    elif kind == "Traffic Cone":
        base = (hx, hy + 40)
        cone = rotate([(base[0] - 78 * k, base[1]), (base[0] - 20 * k, base[1] - 205 * k), (base[0] + 20 * k, base[1] - 205 * k),
                       (base[0] + 78 * k, base[1])], *base, -8)
        P.rect(base[0] - 112 * k, base[1] - 14, base[0] + 112 * k, base[1] + 14, C["orange"], radius=8)
        m = P.m_poly(cone)
        P.shape(m, C["orange"])
        lay = P.layer()
        for y0 in (70, 140):
            lay.rect(0, base[1] - y0 * k - 18 * k, 1000, base[1] - y0 * k + 10 * k, WHITE, outline=0)
        P.compose(lay, clip=P.intersect(m, P.m_poly(rotate([(0, 0), (1000, 0), (1000, 1000), (0, 1000)], *base, -8))))
    elif kind == "Birthday Candle":
        bx, by = hx + 6, hy + 30
        m = P.m_rect(bx - 22 * k, by - 136 * k, bx + 22 * k, by + 6, radius=8)
        P.shape(m, C["pink"])
        lay = P.layer()
        for i in range(-2, 8):
            y = by - i * 30 * k
            lay.poly([(bx - 40, y), (bx + 40, y - 30 * k), (bx + 40, y - 18 * k), (bx - 40, y + 12 * k)], WHITE, outline=0)
        P.compose(lay, clip=m)
        fy = by - 136 * k - 46 * k
        flame = cubic((bx, fy - 46 * k), (bx + 44 * k, fy + 10 * k), (bx + 26 * k, fy + 40 * k), (bx, fy + 40 * k)) + \
            cubic((bx, fy + 40 * k), (bx - 26 * k, fy + 40 * k), (bx - 44 * k, fy + 10 * k), (bx, fy - 46 * k))[1:]
        P.glow(P.m_ellipse(bx, fy + 6, 60 * k), C["mustard"], 18, alpha=170)
        P.poly(flame, C["mustard"], outline=FO)
        P.ellipse(bx, fy + 18 * k, 12 * k, 18 * k, fill=C["orange"], outline=0)
        P.stroke([(bx, fy + 38 * k), (bx, by - 136 * k)], 5)
    elif kind == "Wizard Hat":
        by = hy + 48
        rx = b.w(by) / 2 + 30
        cone = cubic((hx - rx * 0.7, by), (hx - rx * 0.4, by - 140 * k), (hx - 10, by - 240 * k), (hx + 120 * k, by - 250 * k)) + \
            cubic((hx + 120 * k, by - 250 * k), (hx + 40 * k, by - 200 * k), (hx + rx * 0.5, by - 130 * k), (hx + rx * 0.7, by))[1:]
        P.ellipse(hx, by, rx * 1.2, 30, fill=C["navy"])
        m = P.poly(cone, C["navy"])
        lay = P.layer()
        for (dx, dy, s) in ((-0.3, -60, 16), (0.15, -120, 12), (0.3, -40, 10), (-0.05, -170, 9)):
            lay.poly(star_pts(hx + dx * rx, by + dy * k, s * k * 1.4, s * k * 0.6), C["mustard"], outline=0)
        P.compose(lay, clip=m)
        P.ellipse(hx + 120 * k, by - 250 * k, 14 * k, fill=C["mustard"])
    elif kind == "Halo":
        cy = hy - 46
        outer = P.m_ellipse(hx, cy, 120 * k, 30 * k)
        inner = P.m_ellipse(hx, cy + 2, 88 * k, 15 * k)
        ring = P.subtract(outer, inner)
        P.glow(ring, C["gold"], 14, alpha=200)
        P.shape(ring, gold_fill(P), outline=7)
    elif kind == "Crown":
        by = hy + 40
        rx = min(b.w(by) / 2 - 6, 150) * 0.85
        pts = [(hx - rx, by), (hx - rx * 1.08, by - 120 * k), (hx - rx * 0.55, by - 60 * k), (hx, by - 150 * k),
               (hx + rx * 0.55, by - 60 * k), (hx + rx * 1.08, by - 120 * k), (hx + rx, by)]
        P.glow(P.m_poly(pts), C["gold"], 20, alpha=150)
        P.poly(pts, gold_fill(P))
        P.rect(hx - rx * 1.04, by - 28 * k, hx + rx * 1.04, by + 8, gold_fill(P), radius=8)
        for x, col in ((hx - rx * 0.55, C["red"]), (hx, C["teal"]), (hx + rx * 0.55, C["grape"])):
            P.ellipse(x, by - 10 * k, 13 * k, fill=col, outline=5)
        for x, y in ((hx - rx * 1.08, by - 120 * k), (hx, by - 150 * k), (hx + rx * 1.08, by - 120 * k)):
            P.ellipse(x, y, 12 * k, fill=C["cream"], outline=5)
    elif kind == "Backwards Cap":
        cy = hy + 70
        rx = b.w(cy) / 2 + 12
        ry = min(rx * 0.62, 112)
        col = pick(ctx, "navy", "tomato")
        P.ellipse(hx - rx * 0.75, cy - 2, rx * 0.6, 20, fill=shade(col, 0.8), rot=8)
        dome = sorted([p for p in ellipse_pts(hx, cy, rx, ry, n=120) if p[1] <= cy] + [(hx - rx, cy)],
                      key=lambda p: math.atan2(p[1] - cy, p[0] - hx))
        m = P.m_poly(dome)
        P.shape(m, col)
        P.fill_mask(P.intersect(m, P.m_rect(hx + rx * 0.05, cy - 46, hx + rx * 0.55, cy + 2, radius=12)), C["cream"])
        P.ellipse(hx, cy - ry + 6, 12, fill=shade(col, 0.8), outline=6)
    else:
        raise KeyError(kind)


# ---------------------------------------------------------------- clothing
def _region(ctx, y0):
    P, b = ctx.P, ctx.body
    return P.intersect(ctx.body_mask, P.m_rect(0, y0, 1000, 1000))


def _edge(ctx, region):
    P = ctx.P
    P.fill_mask(P.intersect(P.subtract(P.dilate(region, FO), region), ctx.body_mask), INK)


def clothing_back(ctx, kind):
    P, b = ctx.P, ctx.body
    if kind not in ("Hero Cape", "Royal Robe"):
        return
    col = C["red"] if kind == "Hero Cape" else C["purple"]
    y0 = b.cloth_y - 30
    l, r = b.width_at(y0)
    bot = min(960, b.bottom + 20)
    cape = [(l + 20, y0), (r - 20, y0), (r + 90, bot - 30), (500 + 60, bot), (500 - 60, bot), (l - 90, bot - 30)]
    cape = quad(cape[0], ((l + r) / 2, y0 - 30), cape[1]) + cubic(cape[1], (r + 30, y0 + 120), (r + 100, bot - 120), cape[2])[1:] + \
        quad(cape[2], (500, bot + 30), cape[5])[1:] + cubic(cape[5], (l - 100, bot - 120), (l - 30, y0 + 120), cape[0])[1:]
    P.poly(cape, col)


def clothing(ctx, kind):
    P, b = ctx.P, ctx.body
    fx = b.face[0]
    y0 = b.cloth_y
    if kind == "None":
        return
    if kind == "Snug Shorts":
        col = pick(ctx, "mustard", "teal", "grape")
        reg = _region(ctx, y0)
        P.fill_mask(reg, col)
        P.fill_mask(P.intersect(reg, P.m_rect(0, y0, 1000, y0 + 24)), shade(col, 0.82))
        _edge(ctx, reg)
        P.stroke([(fx, b.bottom - 70), (fx, b.bottom - 12)], 6)
    elif kind == "Striped Sweater":
        col = pick(ctx, "teal", "tomato", "grape")
        reg = _region(ctx, y0)
        P.fill_mask(reg, col)
        lay = P.layer()
        for i in range(8):
            lay.rect(0, y0 + 30 + i * 52, 1000, y0 + 52 + i * 52, C["cream"], outline=0)
        P.compose(lay, clip=reg)
        _edge(ctx, reg)
        P.fill_mask(P.intersect(reg, P.m_rect(0, y0, 1000, y0 + 22)), shade(col, 0.8))
    elif kind == "Raincoat":
        coat = pick(ctx, "mustard", "sky", "red")
        reg = _region(ctx, y0)
        P.fill_mask(reg, coat)
        _edge(ctx, reg)
        P.stroke([(fx, y0 + 4), (fx, b.bottom - 10)], 6, color=shade(coat, 0.7))
        for i in range(3):
            P.ellipse(fx + 22, y0 + 50 + i * 60, 10, fill=C["navy"], outline=5)
        for d in (-1, 1):
            P.poly([(fx, y0 + 2), (fx + d * 90, y0 - 4), (fx + d * 60, y0 + 50)], shade(coat, 0.9), outline=FO)
    elif kind == "Overalls":
        denim = pick(ctx, "denim", "mustard")
        reg = _region(ctx, y0 + 50)
        P.fill_mask(reg, denim)
        _edge(ctx, reg)
        bib = P.intersect(ctx.body_mask, P.m_rect(fx - 90, y0 - 18, fx + 90, y0 + 60, radius=10))
        P.shape(bib, denim, outline=FO)
        P.rect(fx - 34, y0 + 4, fx + 34, y0 + 42, shade(denim, 0.85), radius=8, outline=5)
        l, r = b.width_at(y0 - 120)
        for d, edge in ((-1, l), (1, r)):
            strap = [(fx + d * 70, y0 - 12), (fx + d * 90, y0 - 12), (edge - d * 10, y0 - 130), (edge - d * 40, y0 - 130)]
            P.shape(P.intersect(P.m_poly(strap), ctx.body_mask), denim, outline=6)
            P.ellipse(fx + d * 80, y0 - 6, 11, fill=C["mustard"], outline=5)
    elif kind == "Sailor Collar":
        reg = _region(ctx, y0 + 10)
        P.fill_mask(reg, WHITE)
        _edge(ctx, reg)
        l, r = b.width_at(y0)
        for d in (-1, 1):
            col = [(fx, y0 + 70), (fx + d * 20, y0 - 6), (fx + d * (r - l) * 0.46, y0 - 14), (fx + d * (r - l) * 0.42, y0 + 30)]
            P.shape(P.intersect(P.m_poly(col), ctx.body_mask), C["navy"], outline=FO)
        for d in (-1, 1):
            P.poly([(fx, y0 + 40), (fx + d * 44, y0 + 18), (fx + d * 40, y0 + 66)], C["red"], outline=6)
        P.ellipse(fx, y0 + 42, 12, fill=C["red"], outline=6)
    elif kind == "Tuxedo":
        reg = _region(ctx, y0)
        P.fill_mask(reg, C["charcoal"])
        _edge(ctx, reg)
        shirt = P.intersect(reg, P.m_poly([(fx - 58, y0 - 10), (fx + 58, y0 - 10), (fx, y0 + 140)]))
        P.fill_mask(shirt, WHITE)
        P.stroke([(fx - 58, y0 - 10), (fx, y0 + 140), (fx + 58, y0 - 10)], 6)
        for d in (-1, 1):
            P.poly([(fx, y0 + 14), (fx + d * 40, y0), (fx + d * 40, y0 + 30)], INK, outline=4)
        P.ellipse(fx, y0 + 74, 6, fill=INK, outline=0)
        P.ellipse(fx, y0 + 104, 6, fill=INK, outline=0)
    elif kind == "Hero Cape":
        l, r = b.width_at(y0 - 30)
        P.poly([(l + 6, y0 - 46), (r - 6, y0 - 46), (r - 14, y0 - 20), (l + 14, y0 - 20)], C["red"], outline=FO)
        P.ellipse(fx, y0 - 33, 20, fill=gold_fill(P), outline=6)
        P.poly(star_pts(fx, y0 - 33, 12, 5), C["red"], outline=0)
    elif kind == "Royal Robe":
        reg = _region(ctx, y0 - 10)
        P.fill_mask(reg, C["purple"])
        trim = P.intersect(ctx.body_mask, P.m_rect(0, y0 - 40, 1000, y0 - 4))
        P.fill_mask(trim, C["cream"])
        mid = P.intersect(reg, P.m_rect(fx - 26, y0, fx + 26, 1000))
        P.fill_mask(mid, C["cream"])
        lay = P.layer()
        for x in range(0, 1000, 46):
            for y in (y0 - 22,):
                lay.poly([(x, y - 9), (x + 5, y), (x, y + 9), (x - 5, y)], INK, outline=0)
        for y in range(int(y0 + 40), 1000, 56):
            lay.poly([(fx, y - 9), (fx + 5, y), (fx, y + 9), (fx - 5, y)], INK, outline=0)
        P.compose(lay, clip=P.union(trim, mid))
        _edge(ctx, P.intersect(ctx.body_mask, P.m_rect(0, y0 - 40, 1000, 1000)))
    elif kind == "Hoodie":
        col = pick(ctx, "grape", "mustard", "tomato")
        reg = _region(ctx, y0 + 12)
        P.fill_mask(reg, col)
        _edge(ctx, reg)
        l, r = b.width_at(y0 + 12)
        hood = quad((l + 10, y0 + 8), (fx, y0 + 96), (r - 10, y0 + 8))
        P.shape(P.intersect(P.m_poly(hood + [(r, y0 - 20), (l, y0 - 20)]), ctx.body_mask), shade(col, 0.82), outline=0)
        P.stroke([(p[0], p[1]) for p in hood], FO)
        for d in (-1, 1):
            P.stroke([(fx + d * 30, y0 + 70), (fx + d * 34, y0 + 150)], 7, color=C["cream"])
            P.ellipse(fx + d * 34, y0 + 156, 9, fill=C["cream"], outline=5)
        P.stroke(quad((fx - 110, b.bottom - 110), (fx, b.bottom - 90), (fx + 110, b.bottom - 110)), 7)
    else:
        raise KeyError(kind)


# ------------------------------------------------------------- accessories
def accessory(ctx, kind):
    P, b = ctx.P, ctx.body
    fx, fy = b.face
    fs = b.fs
    y0 = b.cloth_y
    if kind == "None":
        return
    if kind == "Bow Tie":
        y = y0 - 6
        bow = pick(ctx, "red", "navy")
        for d in (-1, 1):
            P.poly([(fx, y), (fx + d * 58, y - 30), (fx + d * 64, y + 4), (fx + d * 56, y + 34)], bow, outline=FO)
            for (dx, dy) in ((34, -6), (44, 14)):
                P.ellipse(fx + d * dx, y + dy, 6, fill=C["cream"], outline=0)
        P.ellipse(fx, y + 2, 17, 19, fill=shade(bow, 0.85))
    elif kind == "Scarf":
        sc = pick(ctx, "tomato", "teal")
        band = P.intersect(ctx.body_mask, P.m_rect(0, y0 - 46, 1000, y0 + 10))
        P.fill_mask(band, sc)
        lay = P.layer()
        for x in range(0, 1000, 60):
            lay.rect(x, y0 - 50, x + 26, y0 + 14, C["cream"], outline=0)
        P.compose(lay, clip=band)
        _edge(ctx, band)
        tail = superellipse_pts(fx + 70, y0 + 70, 30, 82, 5, rot=-14)
        tm = P.m_poly(tail)
        P.shape(tm, sc)
        lay = P.layer()
        for i in range(4):
            lay.rect(0, y0 + 20 + i * 40, 1000, y0 + 38 + i * 40, C["cream"], outline=0)
        P.compose(lay, clip=tm)
    elif kind == "Bandage":
        x, y = fx + b.face_w * 0.3, fy - 112 * fs
        for rot in (38, -38):
            P.poly(superellipse_pts(x, y, 58 * fs, 18 * fs, 4, rot=rot), hex_rgb("#F2C9A0"), outline=6)
        P.rect(x - 14 * fs, y - 14 * fs, x + 14 * fs, y + 14 * fs, hex_rgb("#E3AE7C"), radius=4, outline=0)
    elif kind == "Round Glasses":
        eyes = ctx.eyes[:2]
        for (x, y, r) in eyes:
            ring = P.m_ellipse(x, y, r * 1.28 + 6)
            P.fill_mask(ring, WHITE, alpha=55)
            P.stroke(ellipse_pts(x, y, r * 1.28 + 6, r * 1.28 + 6) + [ellipse_pts(x, y, r * 1.28 + 6, r * 1.28 + 6)[0]], 9)
        (x1, y1, r1), (x2, y2, r2) = eyes
        P.stroke(quad((x1 + r1 * 1.28 + 6, y1), ((x1 + x2) / 2, min(y1, y2) - 18), (x2 - r2 * 1.28 - 6, y2)), 8)
    elif kind == "Monocle":
        x, y, r = ctx.eyes[-1] if len(ctx.eyes) < 3 else ctx.eyes[1]
        rr = r * 1.3 + 6
        P.fill_mask(P.m_ellipse(x, y, rr), WHITE, alpha=60)
        ring = P.subtract(P.m_ellipse(x, y, rr + 6), P.m_ellipse(x, y, rr - 4))
        P.shape(ring, gold_fill(P), outline=5)
        chain = quad((x + rr * 0.6, y + rr * 0.8), (x + rr * 1.6, y + 160), (x + 30, y0 + 20))
        for i, (cx, cy) in enumerate(chain[::2]):
            P.ellipse(cx, cy, 4.5, fill=C["gold"], outline=3)
    elif kind == "Lollipop":
        x, y = b.arm_r
        top = (x + 70, y - 170)
        P.stroke([(x + 10, y + 14), top], 18, color=INK)
        P.stroke([(x + 10, y + 14), top], 10, color=WHITE)
        P.ellipse(*top, 62, fill=pick(ctx, "pink", "sky"))
        sp = [(top[0] + 52 * i / 80 * math.cos(i / 80 * 6 * math.pi), top[1] + 52 * i / 80 * math.sin(i / 80 * 6 * math.pi)) for i in range(81)]
        P.stroke(sp, 9, color=WHITE)
        draw_arm(P, b, "r", ctx.skin_base)
    elif kind == "Balloon":
        x, y = b.arm_r
        bc = (min(870, x + 120), 250)
        string = [(x + 14, y + 4)] + [(x + 14 + (bc[0] - x - 14) * t + 14 * math.sin(t * 9), y + 4 + (bc[1] + 92 - y - 4) * t)
                                      for t in [i / 30 for i in range(1, 31)]]
        P.stroke(string, 4)
        bl = pick(ctx, "red", "sky")
        P.poly([(bc[0] - 12, bc[1] + 96), (bc[0] + 12, bc[1] + 96), (bc[0], bc[1] + 80)], bl, outline=5)
        P.ellipse(bc[0], bc[1], 72, 86, fill=bl)
        P.ellipse(bc[0] - 26, bc[1] - 34, 14, 22, fill=WHITE, outline=0, rot=30, alpha=180)
        draw_arm(P, b, "r", ctx.skin_base)
    elif kind == "Star Wand":
        x, y = b.arm_l
        tip = (max(130, x - 95), y - 190)
        P.stroke([(x - 8, y + 12), tip], 16, color=INK)
        P.stroke([(x - 8, y + 12), tip], 8, color=C["lilac"])
        P.glow(P.m_poly(star_pts(*tip, 66, 30)), C["gold"], 16, alpha=190)
        P.poly(star_pts(*tip, 60, 27), gold_fill(P))
        for (dx, dy, s) in ((70, -40, 14), (-50, -70, 10), (40, 60, 9)):
            P.poly(star_pts(tip[0] + dx, tip[1] + dy, s, s * 0.35, 4), WHITE, outline=4)
        draw_arm(P, b, "l", ctx.skin_base)
    else:
        raise KeyError(kind)
