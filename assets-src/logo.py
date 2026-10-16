"""Köy Fırını logosu ve uygulama ikonları.

Yazı, Baloo 2 ExtraBold glif çizgilerinden SVG yoluna çevrilir (sistemde font
kurulu olmasa da aynı görünür). Inkscape SVG'leri PNG'ye çevirir.
Kullanım: python assets-src/logo.py <baloo2-800.ttf yolu>
"""
import os
import subprocess
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets-src', 'logo')
INKSCAPE = r'C:\Program Files\Inkscape\bin\inkscape.com'
OL = '#2a160b'


def text_path(font, text, size, cx, baseline, spacing=0):
    """Metni ortalanmış tek bir SVG yolu olarak döndürür."""
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font['head'].unitsPerEm
    sc = size / upm
    names = [cmap[ord(ch)] for ch in text]
    widths = [font['hmtx'][n][0] for n in names]
    total = sum(widths) * sc + spacing * (len(text) - 1)
    x = cx - total / 2
    pen = SVGPathPen(gs)
    for n, w in zip(names, widths):
        tp = TransformPen(pen, (sc, 0, 0, -sc, x, baseline))
        gs[n].draw(tp)
        x += w * sc + spacing
    return pen.getCommands()


def oven(cx, by, s):
    """Tuğla kubbeli taş fırın, ağzında ateş. cx: orta, by: taban, s: ölçek."""
    r = 60 * s
    bricks = ''.join(
        f'<path d="M{cx - (r - k * 13 * s):.1f} {by:.1f} A{r - k * 13 * s:.1f} {(r - k * 13 * s) * .92:.1f} 0 0 1 {cx + r - k * 13 * s:.1f} {by:.1f}" fill="none" stroke="#5a2414" stroke-width="{2.2 * s:.1f}" opacity=".55"/>'
        for k in range(1, 4))
    return (
        f'<path d="M{cx - r:.1f} {by:.1f} A{r:.1f} {r * .92:.1f} 0 0 1 {cx + r:.1f} {by:.1f}Z" fill="url(#dome)" stroke="{OL}" stroke-width="{5 * s:.1f}"/>'
        + bricks
        + f'<rect x="{cx + r * .35:.1f}" y="{by - r * 1.25:.1f}" width="{14 * s:.1f}" height="{r * .5:.1f}" fill="#6a3a24" stroke="{OL}" stroke-width="{4 * s:.1f}"/>'
        + f'<path d="M{cx - r * .42:.1f} {by:.1f} A{r * .42:.1f} {r * .5:.1f} 0 0 1 {cx + r * .42:.1f} {by:.1f}Z" fill="#1a0b05" stroke="{OL}" stroke-width="{4 * s:.1f}"/>'
        + f'<path d="M{cx - r * .32:.1f} {by:.1f} Q{cx - r * .2:.1f} {by - r * .34:.1f} {cx - r * .08:.1f} {by - r * .12:.1f} Q{cx:.1f} {by - r * .46:.1f} {cx + r * .1:.1f} {by - r * .14:.1f} Q{cx + r * .22:.1f} {by - r * .3:.1f} {cx + r * .32:.1f} {by:.1f}Z" fill="url(#fire)"/>'
        + f'<ellipse cx="{cx:.1f}" cy="{by:.1f}" rx="{r * .55:.1f}" ry="{r * .12:.1f}" fill="#ffb347" opacity=".35"/>'
    )


def loaf(cx, cy, s):
    cuts = ''.join(
        f'<path d="M{cx + (dx - 12) * s:.1f} {cy - 6 * s:.1f} q{12 * s:.1f} {-14 * s:.1f} {26 * s:.1f} {-4 * s:.1f}" fill="none" stroke="#f7d79a" stroke-width="{7 * s:.1f}" stroke-linecap="round"/>'
        for dx in (-26, 0, 26))
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{54 * s:.1f}" ry="{32 * s:.1f}" fill="url(#crust)" stroke="{OL}" stroke-width="{4.5 * s:.1f}"/>'
            f'<ellipse cx="{cx:.1f}" cy="{cy + 12 * s:.1f}" rx="{46 * s:.1f}" ry="{14 * s:.1f}" fill="#8f4a16" opacity=".35"/>'
            + cuts +
            f'<ellipse cx="{cx - 18 * s:.1f}" cy="{cy - 18 * s:.1f}" rx="{15 * s:.1f}" ry="{5 * s:.1f}" fill="#fff" opacity=".45" transform="rotate(-18 {cx - 18 * s:.1f} {cy - 18 * s:.1f})"/>')


def wheat(x, y, s, flip=1):
    out = f'<path d="M{x:.1f} {y:.1f} Q{x + flip * 10 * s:.1f} {y - 60 * s:.1f} {x + flip * 28 * s:.1f} {y - 110 * s:.1f}" stroke="#c99a3e" stroke-width="{4 * s:.1f}" fill="none" stroke-linecap="round"/>'
    for k in range(6):
        t = k / 6
        px = x + flip * (6 + 22 * t) * s
        py = y - (40 + 70 * t) * s
        for side in (-1, 1):
            out += (f'<ellipse cx="{px + side * 7 * s:.1f}" cy="{py:.1f}" rx="{4.5 * s:.1f}" ry="{9 * s:.1f}" fill="url(#grain)" stroke="#7a5a1a" stroke-width="{1.6 * s:.1f}" '
                    f'transform="rotate({side * 28 + flip * 14} {px + side * 7 * s:.1f} {py:.1f})"/>')
    return out


DEFS = '''
<radialGradient id="bg" cx=".5" cy=".38" r=".75"><stop offset="0" stop-color="#7a3a1c"/><stop offset=".55" stop-color="#3d1c0e"/><stop offset="1" stop-color="#1c0d06"/></radialGradient>
<radialGradient id="dome" cx=".38" cy=".25" r=".9"><stop offset="0" stop-color="#e08a5c"/><stop offset=".55" stop-color="#a8502e"/><stop offset="1" stop-color="#6a2a16"/></radialGradient>
<linearGradient id="fire" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#ff7a1a"/><stop offset=".6" stop-color="#ffc23a"/><stop offset="1" stop-color="#fff2a0"/></linearGradient>
<linearGradient id="crust" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6bd64"/><stop offset=".55" stop-color="#d48a36"/><stop offset="1" stop-color="#9a5218"/></linearGradient>
<linearGradient id="grain" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe390"/><stop offset="1" stop-color="#d39b2a"/></linearGradient>
<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff1b0"/><stop offset=".45" stop-color="#ffcf4a"/><stop offset="1" stop-color="#e08a12"/></linearGradient>
<linearGradient id="ribbon" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d4503a"/><stop offset="1" stop-color="#8e2818"/></linearGradient>
<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffb04a" stop-opacity=".55"/><stop offset="1" stop-color="#ffb04a" stop-opacity="0"/></radialGradient>
'''


def icon_svg(full_bleed=True, pad=1.0):
    """Kare uygulama ikonu: fırın, önünde ekmek, iki yanda başak."""
    s = pad
    c = 256
    bg = '<rect width="512" height="512" fill="url(#bg)"/>' if full_bleed else '<rect x="16" y="16" width="480" height="480" rx="110" fill="url(#bg)"/>'
    body = (bg
            + f'<circle cx="{c}" cy="{c + 10}" r="{210 * s:.1f}" fill="url(#glow)"/>'
            + f'<g transform="translate({c} {c}) scale({s}) translate(-{c} -{c})">'
            + f'<ellipse cx="{c}" cy="420" rx="200" ry="34" fill="#140904" opacity=".55"/>'
            + oven(c, 340, 2.6)
            + wheat(96, 470, 2.1, 1) + wheat(416, 470, 2.1, -1)
            + loaf(c, 408, 1.75)
            + '</g>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512"><defs>{DEFS}</defs>{body}</svg>'


def logo_svg(font):
    title = text_path(font, 'Köy Fırını', 128, 400, 300, 2)
    sub = text_path(font, 'TOPLA · PİŞİR · SAT · BÜYÜ', 26, 400, 371, 2)
    body = (
        '<ellipse cx="400" cy="160" rx="250" ry="130" fill="url(#glow)"/>'
        + wheat(170, 250, 1.3, 1) + wheat(630, 250, 1.3, -1)
        + oven(400, 205, 1.9)
        + loaf(400, 220, 1.35)
        # yazı: gölge, kalın dış çizgi, altın dolgu, üst parıltı
        + f'<path d="{title}" fill="#140904" transform="translate(5 7)" opacity=".6"/>'
        + f'<path d="{title}" fill="none" stroke="{OL}" stroke-width="16" stroke-linejoin="round"/>'
        + f'<path d="{title}" fill="url(#gold)"/>'
        + '<path d="M150 338 L650 338 L626 362 L650 386 L150 386 L174 362Z" fill="url(#ribbon)" stroke="#2a160b" stroke-width="5" stroke-linejoin="round"/>'
        + f'<path d="{sub}" fill="#fff1d2"/>'
    )
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="420" viewBox="0 0 800 420"><defs>{DEFS}</defs>{body}</svg>'


def export(svg_text, name, w, h, out_path):
    p = os.path.join(SRC, name + '.svg')
    with open(p, 'w', encoding='utf-8') as f:
        f.write(svg_text)
    subprocess.run([INKSCAPE, '--export-type=png', f'--export-width={w}', f'--export-height={h}', f'--export-filename={out_path}', p],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == '__main__':
    os.makedirs(SRC, exist_ok=True)
    font = TTFont(sys.argv[1])
    export(logo_svg(font), 'logo', 800, 420, os.path.join(ROOT, 'assets', 'logo.png'))
    full = icon_svg(True, 1.0)
    export(full, 'icon', 512, 512, os.path.join(ROOT, 'icon-512.png'))
    export(full, 'icon', 192, 192, os.path.join(ROOT, 'icon-192.png'))
    export(full, 'icon', 180, 180, os.path.join(ROOT, 'apple-touch-icon.png'))
    export(icon_svg(True, .78), 'maskable', 512, 512, os.path.join(ROOT, 'maskable-512.png'))
    print('logo ve ikonlar hazır')
