"""Builds the vector logo files (text converted to outlines, so no font is needed to display them)."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = Path(__file__).parent
INK, CREAM, BUTTER, PINK, MINT, LILAC = "#1e1a2e", "#fbf5ea", "#ffd86b", "#f59ac5", "#8ee3b0", "#c9b8f2"
MARK = (HERE.parent / "web/src/components/Logo.tsx").read_text().split("<svg")[1].split("</svg>")[0]
MARK_BODY = MARK.split(">", 1)[1].replace("strokeWidth", "stroke-width").replace("strokeLinecap", "stroke-linecap").replace("strokeLinejoin", "stroke-linejoin")


def text_paths(text, font_file, size, x, y, colors, tracking=0.0):
    font = TTFont(HERE / "fonts" / font_file)
    gs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
    scale = size / font["head"].unitsPerEm
    out, cx = [], x
    for i, ch in enumerate(text):
        g = cmap.get(ord(ch))
        if g is None:
            continue
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (scale, 0, 0, -scale, cx, y)))
        d = pen.getCommands()
        if d:
            out.append(f'<path d="{d}" fill="{colors[i % len(colors)] if isinstance(colors, list) else colors}"/>')
        cx += hmtx[g][0] * scale + tracking
    return "\n".join(out), cx - x


def svg(w, h, body, bg=None):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{rect}{body}</svg>\n'


out = HERE / "logos"
out.mkdir(exist_ok=True)
(out / "mark.svg").write_text(svg(64, 64, MARK_BODY))
for name, fg, accent in (("nfts-alive-again-dark.svg", CREAM, BUTTER), ("nfts-alive-again-light.svg", INK, "#e08a00")):
    a, w1 = text_paths("NFTs ", "Fraunces_900Black.ttf", 56, 84, 52, fg)
    b, w2 = text_paths("Alive", "Fraunces_900Black.ttf", 56, 84 + w1, 52, accent)
    c, w3 = text_paths(" Again", "Fraunces_900Black.ttf", 56, 84 + w1 + w2, 52, fg)
    body = f'<g transform="translate(0,2) scale(1.1)">{MARK_BODY}</g>{a}{b}{c}'
    (out / name).write_text(svg(int(84 + w1 + w2 + w3 + 8), 76, body))
lo, wl = text_paths("Little", "Fraunces_900Black.ttf", 120, 10, 112, INK)
od, wo = text_paths("Oddities", "Fraunces_900Black.ttf", 120, 10, 236, [PINK, LILAC, MINT, BUTTER, PINK, LILAC, MINT, BUTTER])
outline = od.replace('"/>', f'" stroke="{INK}" stroke-width="7" paint-order="stroke"/>')
tag, wt = text_paths("A World of Wonderfully Weird.", "Caveat_700Bold.ttf", 46, 20, 300, INK)
W = int(max(wl, wo, wt) + 30)
(out / "little-oddities.svg").write_text(svg(W, 320, lo + outline + tag))
fav = svg(64, 64, f'<rect width="64" height="64" rx="14" fill="{INK}"/><g transform="translate(4,4) scale(0.875)">{MARK_BODY}</g>')
(HERE / "favicon").mkdir(exist_ok=True)
(HERE / "favicon" / "favicon.svg").write_text(fav)
print("logos:", sorted(p.name for p in out.iterdir()))
