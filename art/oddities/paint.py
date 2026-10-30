"""Low-level drawing engine for Little Oddities.

All artwork is drawn in a 1000 x 1000 "unit" coordinate space and rendered
at a supersampled resolution, then downsampled for smooth anti-aliased edges.
Every shape can get a bold ink outline, which is what gives the collection
its consistent cartoon look.
"""
from __future__ import annotations

import math
from PIL import Image, ImageChops, ImageDraw, ImageFilter

INK = (42, 30, 58)          # deep plum ink used for every outline
WHITE = (255, 253, 247)
OUTLINE = 13                # default outline width in units
FEATURE_OUTLINE = 10


# --------------------------------------------------------------------------
# colour helpers
# --------------------------------------------------------------------------
def hex_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def shade(c, f=0.8):
    """Darken towards the ink colour (keeps shadows warm, never grey)."""
    return mix(c, INK, 1 - f)


def tint(c, f=0.5):
    return mix(c, WHITE, f)


# --------------------------------------------------------------------------
# geometry helpers (unit space)
# --------------------------------------------------------------------------
def ellipse_pts(cx, cy, rx, ry, rot=0.0, n=96):
    r = math.radians(rot)
    cr, sr = math.cos(r), math.sin(r)
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out


def superellipse_pts(cx, cy, rx, ry, n=4.0, rot=0.0, steps=96):
    r = math.radians(rot)
    cr, sr = math.cos(r), math.sin(r)
    out = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        c, s = math.cos(t), math.sin(t)
        x = rx * math.copysign(abs(c) ** (2 / n), c)
        y = ry * math.copysign(abs(s) ** (2 / n), s)
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out


def star_pts(cx, cy, r_out, r_in, points=5, rot=-90.0):
    out = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180.0 / points)
        out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def soft_star_pts(cx, cy, r, points=5, depth=0.22, rot=-90.0, steps=180):
    out = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        f = 1 - depth + depth * math.cos(points * (t - math.radians(rot)))
        out.append((cx + r * f * math.cos(t), cy + r * f * math.sin(t)))
    return out


def heart_pts(cx, cy, s, steps=80):
    out = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        out.append((cx + x * s / 16, cy + y * s / 16))
    return out


def cubic(p0, p1, p2, p3, n=28):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((
            u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1],
        ))
    return out


def quad(p0, p1, p2, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return out


def rotate(pts, cx, cy, deg):
    r = math.radians(deg)
    cr, sr = math.cos(r), math.sin(r)
    return [(cx + (x - cx) * cr - (y - cy) * sr, cy + (x - cx) * sr + (y - cy) * cr) for x, y in pts]


def width_at(poly, y):
    """Return (xmin, xmax) of a closed polygon at height y (unit space)."""
    xs = []
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 <= y < y2) or (y2 <= y < y1):
            xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    if not xs:
        return (500.0, 500.0)
    return (min(xs), max(xs))


# --------------------------------------------------------------------------
# painter
# --------------------------------------------------------------------------
class Painter:
    """A supersampled RGBA canvas that understands unit coordinates."""

    def __init__(self, size: int = 2048):
        self.size = size
        self.s = size / 1000.0
        self.img = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # -- canvases ------------------------------------------------------
    def layer(self) -> "Painter":
        return Painter(self.size)

    def new_mask(self) -> Image.Image:
        return Image.new("L", (self.size, self.size), 0)

    def px(self, v: float) -> float:
        return v * self.s

    def P(self, pts):
        return [(x * self.s, y * self.s) for x, y in pts]

    # -- masks ---------------------------------------------------------
    def m_poly(self, pts, m=None, value=255):
        m = self.new_mask() if m is None else m
        ImageDraw.Draw(m).polygon(self.P(pts), fill=value)
        return m

    def m_ellipse(self, cx, cy, rx, ry=None, rot=0.0, m=None, value=255):
        ry = rx if ry is None else ry
        if rot == 0.0:
            m = self.new_mask() if m is None else m
            s = self.s
            ImageDraw.Draw(m).ellipse([(cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s], fill=value)
            return m
        return self.m_poly(ellipse_pts(cx, cy, rx, ry, rot), m, value)

    def m_rect(self, x0, y0, x1, y1, radius=0, m=None, value=255):
        m = self.new_mask() if m is None else m
        s = self.s
        ImageDraw.Draw(m).rounded_rectangle([x0 * s, y0 * s, x1 * s, y1 * s], radius=radius * s, fill=value)
        return m

    def m_stroke(self, pts, w, m=None, value=255):
        m = self.new_mask() if m is None else m
        d = ImageDraw.Draw(m)
        P = self.P(pts)
        wpx = max(1, int(round(w * self.s)))
        d.line(P, fill=value, width=wpx, joint="curve")
        r = wpx / 2
        for x, y in (P[0], P[-1]):
            d.ellipse([x - r, y - r, x + r, y + r], fill=value)
        return m

    @staticmethod
    def union(*masks):
        out = masks[0]
        for m in masks[1:]:
            out = ImageChops.lighter(out, m)
        return out

    @staticmethod
    def intersect(a, b):
        return ImageChops.multiply(a, b)

    @staticmethod
    def subtract(a, b):
        return ImageChops.subtract(a, b)

    def shift(self, m, dx, dy):
        out = self.new_mask()
        out.paste(m, (int(round(dx * self.s)), int(round(dy * self.s))))
        return out

    def dilate(self, m, w_units):
        """Grow a mask outward by roughly w units (blur + threshold)."""
        r = w_units * self.s
        bbox = m.getbbox()
        if bbox is None:
            return m.copy()
        pad = int(r * 2 + 4)
        box = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
               min(self.size, bbox[2] + pad), min(self.size, bbox[3] + pad))
        crop = m.crop(box).filter(ImageFilter.GaussianBlur(r / 1.76))
        crop = crop.point(lambda v: 255 if v > 10 else 0)
        out = self.new_mask()
        out.paste(crop, box[:2])
        return out

    # -- painting ------------------------------------------------------
    def _paint(self, mask, fill, alpha=255, target=None):
        target = self.img if target is None else target
        bbox = mask.getbbox()
        if bbox is None:
            return
        mc = mask.crop(bbox)
        if isinstance(fill, Image.Image):
            tile = fill.crop(bbox).convert("RGBA")
            a = ImageChops.multiply(tile.getchannel("A"), mc)
        else:
            tile = Image.new("RGBA", mc.size, tuple(fill[:3]) + (255,))
            a = mc
        if alpha < 255:
            a = a.point(lambda v: v * alpha // 255)
        tile.putalpha(a)
        target.alpha_composite(tile, dest=bbox[:2])

    def shape(self, mask, fill, outline=OUTLINE, ink=INK, alpha=255):
        """Fill a mask, with an optional bold ink outline around it."""
        if outline:
            self._paint(self.dilate(mask, outline), ink)
        self._paint(mask, fill, alpha)
        return mask

    def poly(self, pts, fill, outline=OUTLINE, alpha=255):
        return self.shape(self.m_poly(pts), fill, outline, alpha=alpha)

    def ellipse(self, cx, cy, rx, ry=None, fill=WHITE, outline=OUTLINE, rot=0.0, alpha=255):
        return self.shape(self.m_ellipse(cx, cy, rx, ry, rot), fill, outline, alpha=alpha)

    def rect(self, x0, y0, x1, y1, fill, radius=0, outline=OUTLINE, alpha=255):
        return self.shape(self.m_rect(x0, y0, x1, y1, radius), fill, outline, alpha=alpha)

    def stroke(self, pts, w=FEATURE_OUTLINE, color=INK, alpha=255):
        m = self.m_stroke(pts, w)
        self._paint(m, color, alpha)
        return m

    def fill_mask(self, mask, fill, alpha=255):
        self._paint(mask, fill, alpha)

    def glow(self, mask, color, radius_units, alpha=160):
        g = mask.filter(ImageFilter.GaussianBlur(radius_units * self.s))
        self._paint(g, color, alpha)

    def compose(self, layer: "Painter", clip=None):
        img = layer.img
        if clip is not None:
            img = img.copy()
            img.putalpha(ImageChops.multiply(img.getchannel("A"), clip))
        self.img.alpha_composite(img)

    # -- gradients -----------------------------------------------------
    def gradient(self, stops, angle=90.0):
        """Full-canvas gradient image. stops = [(pos 0..1, rgb), ...]."""
        strip = Image.new("RGB", (256, 1))
        px = strip.load()
        for i in range(256):
            t = i / 255
            for j in range(len(stops) - 1):
                p0, c0 = stops[j]
                p1, c1 = stops[j + 1]
                if p0 <= t <= p1:
                    px[i, 0] = mix(c0, c1, (t - p0) / max(1e-6, p1 - p0))
                    break
            else:
                px[i, 0] = stops[-1][1] if t > stops[-1][0] else stops[0][1]
        big = int(self.size * 1.5)
        g = strip.resize((big, big), Image.BILINEAR).rotate(-angle + 0, resample=Image.BILINEAR)
        off = (big - self.size) // 2
        g = g.crop((off, off, off + self.size, off + self.size))
        return g.convert("RGBA")

    def final(self, out_size=1024) -> Image.Image:
        return self.img.resize((out_size, out_size), Image.LANCZOS)
