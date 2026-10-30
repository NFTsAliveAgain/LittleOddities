"""Species = body silhouettes. Each species defines its outline polygon and
derives 'anchors' (where the face, hat, arms, feet and clothing go) so that
every other trait layer fits every body automatically."""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .paint import INK, OUTLINE, Painter, ellipse_pts, shade, tint, width_at


def superblob(cx, cy, a, b, n_top=2.0, n_bot=2.0, wmod=None, radial=None, notch=None, steps=280):
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        c, s = math.cos(t), math.sin(t)
        n = n_bot if s > 0 else n_top
        x = a * math.copysign(abs(c) ** (2 / n), c)
        y = b * math.copysign(abs(s) ** (2 / n), s)
        if radial:
            f = radial(t)
            x, y = x * f, y * f
        if wmod:
            x *= wmod((y + b) / (2 * b))
        if notch and s > 0:
            depth, sig = notch
            y -= depth * math.exp(-(x / sig) ** 2) * s ** 4
        pts.append((cx + x, cy + y))
    return pts


def ghost_poly():
    pts = []
    cx, cy, r = 500, 505, 238
    for i in range(61):
        t = math.pi + math.pi * i / 60
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    for i in range(1, 16):
        pts.append((cx + r + 6 * math.sin(i / 15 * math.pi), cy + 320 * i / 15))
    for i in range(61):
        u = i / 60
        pts.append((cx + r - 2 * r * u, cy + 320 + 48 * abs(math.sin(3 * math.pi * u))))
    for i in range(15, 0, -1):
        pts.append((cx - r - 6 * math.sin(i / 15 * math.pi), cy + 320 * i / 15))
    return pts


def _smooth(t):
    return t * t * (3 - 2 * t)


SPECIES_SHAPES = {
    "Beanling": lambda: superblob(500, 605, 252, 300, 2.0, 2.5),
    "Puffkin": lambda: superblob(500, 615, 272, 272, radial=lambda t: 0.9 + 0.1 * abs(math.cos(4.5 * t))),
    "Sockling": lambda: superblob(500, 590, 188, 335, 3.0, 4.2, wmod=lambda u: 0.94 + 0.08 * u),
    "Gumdrop": lambda: superblob(500, 650, 292, 255, 2.0, 6.0, wmod=lambda u: 0.86 + 0.16 * u),
    "Blockle": lambda: superblob(500, 615, 258, 262, 5.0, 5.0),
    "Pearbo": lambda: superblob(500, 625, 272, 292, 2.2, 2.4, wmod=lambda u: 0.6 + 0.42 * _smooth(u)),
    "Molarbit": lambda: superblob(500, 600, 255, 285, 3.2, 3.0, notch=(70, 70)),
    "Wisplet": ghost_poly,
    "Twinklet": lambda: superblob(500, 618, 292, 292, radial=lambda t: 0.8 + 0.2 * math.cos(5 * (t + math.pi / 2))),
    "Prismling": lambda: superblob(500, 600, 262, 322, 1.45, 1.6),
}

NO_FEET = {"Wisplet"}
NO_ARMS = {"Twinklet"}


@dataclass
class Body:
    species: str
    poly: list
    top: float
    bottom: float
    face: tuple
    fs: float
    face_w: float
    head_x: float
    cloth_y: float
    arm_y: float
    arm_l: tuple
    arm_r: tuple
    feet: list
    has_feet: bool
    has_arms: bool
    extras: dict = field(default_factory=dict)

    def width_at(self, y):
        return width_at(self.poly, y)

    def w(self, y):
        a, b = width_at(self.poly, y)
        return b - a


def build_body(species: str) -> Body:
    poly = SPECIES_SHAPES[species]()
    ys = [p[1] for p in poly]
    top, bottom = min(ys), max(ys)
    H = bottom - top
    face_frac = {"Sockling": 0.34, "Twinklet": 0.47, "Gumdrop": 0.42, "Wisplet": 0.33, "Prismling": 0.42}.get(species, 0.40)
    fy = top + face_frac * H
    a, b = width_at(poly, fy)
    face_w = b - a
    fs = max(0.72, min(1.06, face_w / 470))
    arm_y = top + 0.63 * H
    al, ar = width_at(poly, arm_y)
    foot_y = bottom - 4
    fw = width_at(poly, bottom - 50)
    foot_dx = max(70.0, min(150.0, (fw[1] - fw[0]) * 0.32))
    return Body(
        species=species, poly=poly, top=top, bottom=bottom,
        face=(500.0, fy), fs=fs, face_w=face_w, head_x=500.0,
        cloth_y=top + 0.665 * H, arm_y=arm_y,
        arm_l=(al + 10, arm_y), arm_r=(ar - 10, arm_y),
        feet=[(500 - foot_dx, foot_y), (500 + foot_dx, foot_y)],
        has_feet=species not in NO_FEET, has_arms=species not in NO_ARMS,
    )


def draw_feet(P: Painter, body: Body, skin_base):
    if not body.has_feet:
        return
    for (x, y) in body.feet:
        P.ellipse(x, y, 64, 36, fill=shade(skin_base, 0.86))


def draw_arm(P: Painter, body: Body, side: str, skin_base):
    if not body.has_arms:
        return
    x, y = body.arm_l if side == "l" else body.arm_r
    rot = 28 if side == "l" else -28
    dx = -14 if side == "l" else 14
    P.ellipse(x + dx, y + 18, 34, 56, fill=skin_base, rot=rot)


def draw_body(P: Painter, body: Body, skin_fill, skin_base):
    """Main silhouette with cel shading. Returns the interior mask."""
    m = P.m_poly(body.poly)
    P.shape(m, skin_fill, outline=OUTLINE + 1)
    # cel shadow on lower-right rim
    shadow = P.subtract(m, P.shift(m, -34, -26))
    P.fill_mask(shadow, shade(skin_base, 0.78), alpha=150)
    # soft highlight upper-left
    hx = 500 - body.face_w * 0.28
    hy = body.top + (body.bottom - body.top) * 0.16
    hl = P.intersect(P.m_ellipse(hx, hy, 46, 28, rot=-30), m)
    P.fill_mask(hl, (255, 255, 255), alpha=120)
    hl2 = P.intersect(P.m_ellipse(hx + 58, hy - 22, 13, 10), m)
    P.fill_mask(hl2, (255, 255, 255), alpha=120)
    if body.species == "Prismling":
        cx, top, bot = 500, body.top, body.bottom
        mid = top + (bot - top) * 0.42
        for pts in ([(cx, top + 18), (cx - 130, mid)], [(cx, top + 18), (cx + 130, mid)],
                    [(cx - 130, mid), (cx + 130, mid)], [(cx - 130, mid), (cx, bot - 20)],
                    [(cx + 130, mid), (cx, bot - 20)]):
            lm = P.intersect(P.m_stroke(pts, 7), m)
            P.fill_mask(lm, (255, 255, 255), alpha=70)
    return m


def draw_ground_shadow(P: Painter, body: Body):
    if body.has_feet:
        m = P.m_ellipse(500, body.bottom + 26, max(150, body.w(body.bottom - 60) * 0.5 + 40), 24)
        alpha = 55
    else:
        m = P.m_ellipse(500, 935, 150, 18)
        alpha = 35
    P.glow(m, INK, 4, alpha=alpha)
