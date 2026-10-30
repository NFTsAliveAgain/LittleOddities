"""Face traits: Eyes, Mouths and Expressions."""
from __future__ import annotations

import math

from .paint import FEATURE_OUTLINE as FO, INK, WHITE, Painter, cubic, hex_rgb, quad, shade, star_pts, tint

MOUTH_DARK = (92, 32, 58)
TONGUE = hex_rgb("#FF7A93")
BLUSH = hex_rgb("#FF7E9D")
GOLD = hex_rgb("#F6C445")


def eye_metrics(ctx):
    fx, fy = ctx.body.face
    fs = ctx.body.fs
    return fx, fy, 60 * fs, 104 * fs


# ---------------------------------------------------------------- eye parts
IRIS = [hex_rgb("#7A4E2D")]


def sclera(P, x, y, r, color=WHITE):
    m = P.ellipse(x, y, r * 0.9, r, fill=color, outline=FO)
    # lid shadow across the top of the eyeball + crease line above
    P.fill_mask(P.subtract(m, P.shift(m, 0, -r * 0.35)), (150, 140, 175), alpha=90)
    P.stroke(quad((x - r * 0.7, y - r * 1.18), (x, y - r * 1.42), (x + r * 0.75, y - r * 1.15)), 4, alpha=110)


def pupil(P, x, y, r, size=0.52, look=(0.0, 0.14), color=INK, glint=True):
    px, py = x + look[0] * r, y + look[1] * r
    if color == INK and size < 0.62:
        ir = r * min(0.82, size * 1.55)
        iris = P.gradient([(0, tint(IRIS[0], 0.25)), (1, shade(IRIS[0], 0.7))], 90)
        P.shape(P.m_ellipse(px, py, ir * 0.9, ir), iris, outline=4)
        for k in range(10):
            a = k * 0.628
            P.stroke([(px + ir * 0.45 * math.cos(a), py + ir * 0.45 * math.sin(a)),
                      (px + ir * 0.82 * math.cos(a), py + ir * 0.82 * math.sin(a))], 2.5, color=shade(IRIS[0], 0.55), alpha=140)
    P.ellipse(px, py, r * size * 0.88 * 0.75, r * size * 0.75, fill=color, outline=0)
    if glint:
        P.ellipse(px - r * size * 0.38, py - r * size * 0.42, r * size * 0.3, fill=WHITE, outline=0)
        P.ellipse(px + r * size * 0.36, py + r * size * 0.34, r * size * 0.12, fill=WHITE, outline=0, alpha=220)


def classic(P, x, y, r, inward=1, **kw):
    sclera(P, x, y, r)
    pupil(P, x, y, r, look=(0.1 * inward, 0.14), **kw)


def lid(ctx, x, y, r, cover):
    P = ctx.P
    m = P.m_ellipse(x, y, r * 0.9, r)
    cut = P.m_rect(x - r * 1.2, y - r * 1.2, x + r * 1.2, y - r + 2 * r * cover)
    P.fill_mask(P.intersect(m, cut), shade(ctx.skin_base, 0.9))
    ly = y - r + 2 * r * cover
    hw = r * 0.9 * math.sqrt(max(0.0, 1 - ((ly - y) / r) ** 2))
    P.stroke([(x - hw - 4, ly), (x + hw + 4, ly)], FO)


def closed_arc(P, x, y, r, up=True):
    pts = []
    for i in range(21):
        t = math.pi + math.pi * i / 20 if up else math.pi * i / 20
        pts.append((x + r * 0.78 * math.cos(t), y + (0.15 * r if up else -0.25 * r) + r * 0.62 * math.sin(t)))
    P.stroke(pts, FO + 1)


def eyes(ctx, kind):
    P = ctx.P
    fx, fy, r, sp = eye_metrics(ctx)
    IRIS[0] = [hex_rgb(c) for c in ("#7A4E2D", "#2F7D6B", "#4A5FC1", "#8A4FB8", "#B5652A")][sum(map(ord, ctx.body.species + kind)) % 5]
    L, R = (fx - sp, fy), (fx + sp, fy)
    ctx.eyes = [(L[0], L[1], r), (R[0], R[1], r)]
    if kind == "Classic":
        classic(P, *L, r, 1); classic(P, *R, r, -1)
    elif kind == "Dot Eyes":
        for (x, y), _ in ((L, 0), (R, 0)):
            P.ellipse(x, y, r * 0.36, r * 0.48, fill=INK, outline=0)
            P.ellipse(x - r * 0.12, y - r * 0.17, r * 0.13, fill=WHITE, outline=0)
        ctx.eyes = [(L[0], L[1], r * 0.7), (R[0], R[1], r * 0.7)]
    elif kind == "Sleepy":
        for (x, y), inw in ((L, 1), (R, -1)):
            classic(P, x, y, r, inw)
            lid(ctx, x, y, r, 0.5)
    elif kind == "Side Glance":
        for (x, y) in (L, R):
            sclera(P, x, y, r)
            pupil(P, x, y, r, look=(0.4, 0.12), size=0.5)
            lid(ctx, x, y, r, 0.3)
    elif kind == "Wide":
        rr = r * 1.22
        for (x, y) in (L, R):
            sclera(P, x, y, rr)
            pupil(P, x, y, rr, size=0.3, look=(0, 0.0))
        ctx.eyes = [(L[0], L[1], rr), (R[0], R[1], rr)]
    elif kind == "Mismatched":
        classic(P, L[0] - 6, L[1] - 4, r * 1.26, 1, size=0.46)
        classic(P, R[0] + 4, R[1] + 6, r * 0.78, -1, size=0.6)
        ctx.eyes = [(L[0] - 6, L[1] - 4, r * 1.26), (R[0] + 4, R[1] + 6, r * 0.78)]
    elif kind == "Happy Arcs":
        closed_arc(P, *L, r); closed_arc(P, *R, r)
    elif kind == "Wink":
        classic(P, *L, r, 1)
        closed_arc(P, *R, r)
    elif kind == "Cyclops":
        rr = r * 1.6
        sclera(P, fx, fy, rr)
        P.ellipse(fx, fy + rr * 0.1, rr * 0.5, rr * 0.55, fill=hex_rgb("#2EC4B6"), outline=0)
        pupil(P, fx, fy, rr, size=0.3, look=(0, 0.1))
        ctx.eyes = [(fx, fy, rr)]
    elif kind == "Dizzy":
        for (x, y) in (L, R):
            sclera(P, x, y, r)
            pts = []
            for i in range(60):
                t = i / 59 * 2.4 * 2 * math.pi
                rad = r * 0.72 * i / 59
                pts.append((x + rad * math.cos(t), y + rad * math.sin(t)))
            P.stroke(pts, 5)
    elif kind == "Triple":
        rr = r * 0.84
        L2, R2 = (fx - sp * 1.02, fy + 10), (fx + sp * 1.02, fy + 10)
        T = (fx, fy - rr * 1.55)
        classic(P, *L2, rr, 1); classic(P, *R2, rr, -1); classic(P, *T, rr * 0.86, 0)
        ctx.eyes = [(L2[0], L2[1], rr), (R2[0], R2[1], rr), (T[0], T[1], rr * 0.86)]
    elif kind == "Star Eyes":
        for (x, y) in (L, R):
            sclera(P, x, y, r)
            P.poly(star_pts(x, y + r * 0.08, r * 0.62, r * 0.28), GOLD, outline=5)
    elif kind == "Sparkle Eyes":
        rr = r * 1.1
        for (x, y), inw in ((L, 1), (R, -1)):
            sclera(P, x, y, rr)
            iris = P.gradient([(0, hex_rgb("#7B5CFF")), (1, hex_rgb("#FF8FC7"))], 90)
            px = x + 0.06 * inw * rr
            P.shape(P.m_ellipse(px, y + rr * 0.1, rr * 0.62, rr * 0.7), iris, outline=0)
            P.ellipse(px, y + rr * 0.14, rr * 0.3, rr * 0.34, fill=INK, outline=0)
            P.ellipse(px - rr * 0.22, y - rr * 0.18, rr * 0.2, fill=WHITE, outline=0)
            P.ellipse(px + rr * 0.24, y + rr * 0.34, rr * 0.1, fill=WHITE, outline=0)
        ctx.eyes = [(L[0], L[1], rr), (R[0], R[1], rr)]
    elif kind == "Cosmic Eyes":
        for (x, y) in (L, R):
            sclera(P, x, y, r, color=hex_rgb("#1E1B4B"))
            for (dx, dy, s) in ((-0.3, -0.3, 0.1), (0.25, -0.1, 0.07), (-0.1, 0.35, 0.06), (0.35, 0.3, 0.08), (0.0, -0.05, 0.05)):
                P.poly(star_pts(x + dx * r, y + dy * r, r * s * 1.6, r * s * 0.6, 4), WHITE, outline=0)
            P.ellipse(x - r * 0.35, y - r * 0.45, r * 0.15, fill=WHITE, outline=0)
    elif kind == "Golden Gaze":
        for (x, y), inw in ((L, 1), (R, -1)):
            sclera(P, x, y, r)
            gold = P.gradient([(0, hex_rgb("#FFE48A")), (1, hex_rgb("#D89A1E"))], 90)
            P.shape(P.m_ellipse(x + 0.08 * inw * r, y + r * 0.12, r * 0.6, r * 0.64), gold, outline=4)
            pupil(P, x + 0.08 * inw * r, y, r, size=0.3, look=(0, 0.12))
            for k in (-1, 0, 1):
                a = math.radians(-90 + k * 32 - 8 * inw)
                P.stroke([(x + r * 0.95 * math.cos(a), y + r * 1.02 * math.sin(a)),
                          (x + r * 1.32 * math.cos(a), y + r * 1.38 * math.sin(a))], 6)
    elif kind in ("Bored", "Unimpressed"):
        cover = 0.52 if kind == "Bored" else 0.42
        for (x, y), inw in ((L, 1), (R, -1)):
            sclera(P, x, y, r)
            look = (0.0, 0.3) if kind == "Bored" else (0.42 * -inw if inw < 0 else 0.42, 0.18)
            pupil(P, x, y, r, size=0.46, look=look)
            lid(ctx, x, y, r, cover)
            P.stroke(quad((x - r * 0.55, y + r * 1.15), (x, y + r * 1.32), (x + r * 0.55, y + r * 1.15)), 5,
                     color=shade(ctx.skin_base, 0.62))
    elif kind == "Shades":
        for (x, y) in (L, R):
            m = P.m_poly([(x - r * 1.25, y - r * 0.55), (x + r * 1.15, y - r * 0.55), (x + r * 0.95, y + r * 0.6), (x - r * 1.05, y + r * 0.6)])
            P.shape(m, INK, outline=FO)
            P.fill_mask(P.intersect(m, P.m_stroke([(x - r * 0.9, y + r * 0.2), (x - r * 0.2, y - r * 0.5)], 14)), (255, 255, 255), alpha=110)
        P.stroke([(L[0] + r * 1.1, L[1] - r * 0.4), (R[0] - r * 1.2, R[1] - r * 0.4)], FO + 4)
        ctx.eyes = []
    else:
        raise KeyError(kind)


# ------------------------------------------------------------------ mouths
def mouth(ctx, kind):
    P = ctx.P
    fx, fy = ctx.body.face
    fs = ctx.body.fs
    my = fy + 122 * fs
    w = 60 * fs
    if kind in ("Smile", "Single Fang", "Tongue Out"):
        curve = quad((fx - w, my - 8), (fx, my + 0.8 * w), (fx + w, my - 8))
        if kind == "Single Fang":
            x, y = curve[16]
            P.poly([(x - 11, y - 4), (x + 11, y - 4), (x + 1, y + 22)], WHITE, outline=5)
        if kind == "Tongue Out":
            x, y = curve[12]
            m = P.m_ellipse(x + 4, y + 16, 22 * fs, 26 * fs)
            m = P.subtract(m, P.m_rect(x - 40, y - 40, x + 40, y))
            P.shape(m, TONGUE, outline=6)
            P.stroke([(x + 4, y + 4), (x + 4, y + 22 * fs)], 4, color=shade(TONGUE, 0.75))
        P.stroke(curve, FO + 1)
    elif kind in ("Big Grin", "Gold Tooth", "Laugh"):
        ww = w * (1.15 if kind != "Laugh" else 0.95)
        depth = 1.15 if kind != "Laugh" else 1.55
        top = my - 14
        pts = [(fx - ww, top)] + quad((fx - ww, top), (fx, top + depth * ww * 1.6), (fx + ww, top))[1:]
        m = P.m_poly(pts)
        P.shape(m, MOUTH_DARK, outline=FO)
        inner = P.layer()
        if kind != "Laugh":
            inner.rect(fx - ww, top - 10, fx + ww, top + 19 * fs, WHITE, outline=0)
            for i in (-1, 1):
                inner.stroke([(fx + i * ww * 0.33, top), (fx + i * ww * 0.33, top + 19 * fs)], 4, color=(220, 210, 215))
            if kind == "Gold Tooth":
                gold = inner.gradient([(0, hex_rgb("#FFE48A")), (1, hex_rgb("#D89A1E"))], 90)
                inner.shape(inner.m_rect(fx + ww * 0.36, top - 10, fx + ww * 0.72, top + 19 * fs), gold, outline=0)
                inner.ellipse(fx + ww * 0.48, top + 6, 3, fill=WHITE, outline=0)
        inner.ellipse(fx + 6, top + depth * ww * 0.85, ww * 0.6, ww * 0.42, fill=TONGUE, outline=0)
        P.compose(inner, clip=m)
        P.shape(P.subtract(P.dilate(m, FO), m), INK, outline=0)
    elif kind == "Tiny O":
        P.ellipse(fx, my + 4, 16 * fs, 21 * fs, fill=MOUTH_DARK, outline=FO)
    elif kind == "Wobbly":
        pts = [(fx - w + 2 * w * i / 30, my + 7 * math.sin(i / 30 * 3 * math.pi)) for i in range(31)]
        P.stroke(pts, FO + 1)
    elif kind == "Buck Teeth":
        ww = w * 0.7
        for d in (-1, 1):
            P.rect(fx + (d - 1) * 10 * fs + (2 if d > 0 else -2), my - 6, fx + (d + 1) * 10 * fs + (2 if d > 0 else -2), my + 24 * fs,
                   WHITE, radius=4, outline=5)
        P.stroke(quad((fx - ww, my - 10), (fx, my + 6), (fx + ww, my - 10)), FO + 1)
    elif kind == "Pout":
        P.stroke(quad((fx - w * 0.45, my + 10), (fx, my - 14), (fx + w * 0.45, my + 10)), FO + 1)
        P.stroke(quad((fx - w * 0.2, my + 16), (fx, my + 24), (fx + w * 0.2, my + 16)), 5)
    elif kind == "Chomper":
        ww = w * 1.3
        m = P.m_ellipse(fx, my + 8, ww, 0.55 * ww)
        P.shape(m, MOUTH_DARK, outline=FO)
        inner = P.layer()
        n = 6
        top = [(fx - ww + 2 * ww * i / n + (ww / n if j else 0), my + 8 - 0.55 * ww + (24 if j else -4) * fs)
               for i in range(n) for j in (0, 1)]
        inner.poly([(fx - ww, my - 40)] + top + [(fx + ww, my - 40)], WHITE, outline=0)
        bot = [(fx - ww + 2 * ww * i / n + (ww / n if j else 0), my + 8 + 0.55 * ww - (22 if j else -4) * fs)
               for i in range(n) for j in (0, 1)]
        inner.poly([(fx - ww, my + 80)] + bot + [(fx + ww, my + 80)], WHITE, outline=0)
        P.compose(inner, clip=m)
        P.shape(P.subtract(P.dilate(m, FO), m), INK, outline=0)
    elif kind == "Smirk":
        P.stroke(cubic((fx - w * 0.7, my + 4), (fx - w * 0.1, my + 14), (fx + w * 0.5, my + 6), (fx + w * 0.85, my - 18)), FO + 1)
        P.stroke([(fx + w * 0.78, my - 26), (fx + w * 0.95, my - 10)], 5)
    elif kind == "Bubblegum":
        P.stroke(quad((fx - w * 0.5, my + 2), (fx, my + 10), (fx + w * 0.5, my + 2)), FO)
        P.ellipse(fx + w * 0.2, my + 4, 66 * fs, 62 * fs, fill=hex_rgb("#FF8FC7"))
        P.ellipse(fx + w * 0.2 - 26 * fs, my - 22 * fs, 14 * fs, 10 * fs, fill=WHITE, outline=0, rot=-30, alpha=200)
    elif kind == "Flat":
        P.stroke([(fx - w * 0.55, my + 2), (fx + w * 0.55, my + 2)], FO + 1)
    else:
        raise KeyError(kind)


# ------------------------------------------------------------- expressions
def expression(ctx, kind):
    P = ctx.P
    fx, fy = ctx.body.face
    fs = ctx.body.fs
    cheek_y = fy + 84 * fs
    cheek_dx = 168 * fs

    def blush():
        for d in (-1, 1):
            P.ellipse(fx + d * cheek_dx, cheek_y, 32 * fs, 18 * fs, fill=BLUSH, outline=0, alpha=150)

    def brow(x, y, r, tilt, arch=0.0):
        # tilt > 0 raises the inner end (towards face centre)
        inner = 1 if x < fx else -1
        if len(ctx.eyes) == 1:
            inner = 0
        y0 = y - r * 1.38
        a = (x - r * 0.7 * inner if inner else x - r * 0.7, y0 + tilt * 12 * inner if inner else y0)
        b = (x + r * 0.6 * inner if inner else x + r * 0.7, y0 - tilt * 14 * inner if inner else y0)
        if inner == 0:
            a, b = (x - r * 0.7, y0), (x + r * 0.7, y0)
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - arch * 16)
        P.stroke(quad(a, mid, b), FO + 1)

    if kind == "Content":
        return
    if kind == "Blushing":
        blush()
    elif kind == "Freckled":
        for d in (-1, 1):
            for (dx, dy) in ((-14, -6), (8, -10), (-2, 10), (18, 8)):
                P.ellipse(fx + d * cheek_dx + dx * fs, cheek_y + dy * fs, 5.5 * fs, fill=shade(ctx.skin_base, 0.6), outline=0)
    elif kind in ("Grumpy", "Worried", "Proud", "Raised Brow"):
        for i, (x, y, r) in enumerate(ctx.eyes[:2]):
            if kind == "Grumpy":
                brow(x, y, r, -1.2)
            elif kind == "Worried":
                brow(x, y, r, 1.3, arch=0.3)
            elif kind == "Proud":
                brow(x, y - 8, r, 0, arch=1.0)
            else:
                brow(x, y - (14 if i == 1 else 0), r, 0, arch=1.2 if i == 1 else 0)
        if kind == "Proud":
            blush()
    else:
        raise KeyError(kind)
