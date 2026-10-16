"""Köy Fırını ürün ve malzeme ikonları.

Her ikon 128x128 bir SVG olarak yazılır, Inkscape ile PNG'ye çevrilir ve
Pillow ile tek bir atlas dosyasında (assets/items.png) birleştirilir.
Nesnelerin tabanı y=118 civarındadır: oyun ikonu alt orta noktasından çizer.

Çalıştırma:  python -I assets-src/icons.py
"""
import json
import os
import subprocess
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets-src', 'icons')
OUT = os.path.join(ROOT, 'assets')
INKSCAPE = r'C:\Program Files\Inkscape\bin\inkscape.com'
CELL = 128
OL = '#3a2212'  # ortak dış çizgi rengi

def svg(body, defs=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">'
            f'<defs>{defs}</defs>{body}</svg>')

def lg(id_, stops, x1=0, y1=0, x2=0, y2=1):
    s = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{id_}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'

def rg(id_, stops, cx=.4, cy=.35, r=.7):
    s = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<radialGradient id="{id_}" cx="{cx}" cy="{cy}" r="{r}">{s}</radialGradient>'

def shine(cx, cy, rx, ry, rot=-20, op=.45):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" transform="rotate({rot} {cx} {cy})" fill="#fff" opacity="{op}"/>'

ICONS = {}

# ---------------------------------------------------------------- ürünler
ICONS['ekmek'] = svg(
    f'<ellipse cx="64" cy="80" rx="54" ry="34" fill="url(#ek)" stroke="{OL}" stroke-width="4"/>'
    '<ellipse cx="64" cy="94" rx="46" ry="16" fill="#8f4a16" opacity=".35"/>'
    + ''.join(f'<path d="M{x-12} {66+abs(x-64)*.1} q 12 -14 26 -4" fill="none" stroke="#f7d79a" stroke-width="7" stroke-linecap="round"/>'
              f'<path d="M{x-12} {66+abs(x-64)*.1} q 12 -14 26 -4" fill="none" stroke="#b86a28" stroke-width="2" stroke-linecap="round" transform="translate(1 4)"/>'
              for x in (36, 62, 88))
    + shine(44, 60, 16, 6),
    lg('ek', [(0, '#f2b65e'), (.55, '#d48a36'), (1, '#9a5218')]))

ICONS['simit'] = svg(
    f'<ellipse cx="64" cy="78" rx="52" ry="36" fill="url(#si)" stroke="{OL}" stroke-width="4"/>'
    f'<ellipse cx="64" cy="76" rx="22" ry="13" fill="#5a3218" stroke="{OL}" stroke-width="3"/>'
    '<ellipse cx="64" cy="74" rx="20" ry="10" fill="#2b190c" opacity=".55"/>'
    + ''.join(f'<ellipse cx="{64+40*__import__("math").cos(a/9*6.283)*1.0:.1f}" cy="{77+25*__import__("math").sin(a/9*6.283):.1f}" rx="3.2" ry="1.9" fill="#fbefcf" stroke="#9a6a3a" stroke-width=".8" transform="rotate({a*40} {64+40*__import__("math").cos(a/9*6.283):.1f} {77+25*__import__("math").sin(a/9*6.283):.1f})"/>' for a in range(9))
    + ''.join(f'<ellipse cx="{64+33*__import__("math").cos(a/7*6.283+.4):.1f}" cy="{77+19*__import__("math").sin(a/7*6.283+.4):.1f}" rx="2.6" ry="1.5" fill="#fbefcf" opacity=".9"/>' for a in range(7))
    + shine(40, 60, 14, 5, -25, .35),
    rg('si', [(0, '#e09050'), (.6, '#b5612a'), (1, '#7a3612')], .45, .3, .75))

ICONS['pogaca'] = svg(
    f'<path d="M14 96 Q14 46 64 42 Q114 46 114 96 Q90 110 64 110 Q38 110 14 96Z" fill="url(#po)" stroke="{OL}" stroke-width="4"/>'
    '<path d="M22 96 Q40 104 64 104 Q88 104 106 96" fill="none" stroke="#9a5a1a" stroke-width="3" opacity=".5"/>'
    + ''.join(f'<ellipse cx="{x}" cy="{y}" rx="2.3" ry="1.6" fill="#24160c"/>' for x, y in [(50, 60), (62, 56), (75, 61), (56, 70), (70, 72), (84, 68), (44, 72), (64, 64)])
    + shine(46, 56, 15, 7, -25, .5),
    rg('po', [(0, '#ffd889'), (.55, '#eaa847'), (1, '#b26e1c')], .42, .3, .8))

ICONS['kurabiye'] = svg(
    f'<ellipse cx="64" cy="92" rx="48" ry="18" fill="#8a5420" stroke="{OL}" stroke-width="4"/>'
    f'<ellipse cx="64" cy="80" rx="48" ry="22" fill="url(#ku)" stroke="{OL}" stroke-width="4"/>'
    '<ellipse cx="64" cy="76" rx="16" ry="7" fill="#c8253a" stroke="#7a1626" stroke-width="2.5"/>'
    '<ellipse cx="60" cy="74" rx="6" ry="2.3" fill="#fff" opacity=".55"/>'
    + ''.join(f'<circle cx="{x}" cy="{y}" r="1.6" fill="#fffaf0" opacity=".9"/>' for x, y in [(30, 78), (40, 70), (90, 72), (98, 82), (82, 90), (46, 88), (64, 92)])
    + shine(38, 72, 10, 4, -15, .35),
    rg('ku', [(0, '#f6d391'), (.6, '#e2ad5c'), (1, '#b97c33')], .45, .3, .8))

ICONS['pasta'] = svg(
    f'<path d="M18 62 L110 62 L110 104 Q64 116 18 104Z" fill="url(#pa)" stroke="{OL}" stroke-width="4"/>'
    '<path d="M18 80 Q64 90 110 80 L110 88 Q64 98 18 88Z" fill="#ff8fb0"/>'
    '<path d="M18 96 Q64 106 110 96" fill="none" stroke="#e9cfa6" stroke-width="3"/>'
    f'<ellipse cx="64" cy="62" rx="46" ry="14" fill="#fffaf4" stroke="{OL}" stroke-width="4"/>'
    + ''.join(f'<circle cx="{x}" cy="{y}" r="6" fill="#fff" stroke="#e8d9c6" stroke-width="1.5"/>' for x, y in [(30, 62), (46, 56), (82, 56), (98, 62), (64, 68)])
    + f'<path d="M64 26 C46 30 48 52 64 56 C80 52 82 30 64 26Z" fill="url(#ci)" stroke="{OL}" stroke-width="3.5"/>'
    '<path d="M56 28 L64 20 L72 28 L64 32Z" fill="#3f8a2a" stroke="#24521a" stroke-width="2"/>'
    + ''.join(f'<ellipse cx="{x}" cy="{y}" rx="1.3" ry="2" fill="#ffe48a"/>' for x, y in [(58, 38), (68, 36), (63, 46), (70, 46), (56, 46)])
    + shine(58, 36, 4, 7, 20, .5),
    lg('pa', [(0, '#f8ead2'), (1, '#e7cfaa')]) + rg('ci', [(0, '#ff6070'), (1, '#c01628')]))

ICONS['borek'] = svg(
    f'<path d="M12 92 Q14 58 52 50 L104 56 Q120 64 116 90 Q98 110 60 108 Q22 106 12 92Z" fill="url(#bo)" stroke="{OL}" stroke-width="4"/>'
    f'<ellipse cx="38" cy="80" rx="24" ry="22" fill="#f1c87a" stroke="{OL}" stroke-width="3.5"/>'
    '<path d="M38 80 m0 -15 a15 15 0 1 1 -1 0 m1 6 a9 9 0 1 0 1 0 m-1 5 a4 4 0 1 1 -1 0" fill="none" stroke="#b9822e" stroke-width="2.5"/>'
    '<path d="M64 60 Q84 62 108 66 M66 72 Q88 74 112 78 M64 86 Q90 88 112 90" stroke="#f9dc9a" stroke-width="3" fill="none" stroke-linecap="round"/>'
    + ''.join(f'<ellipse cx="{x}" cy="{y}" rx="2.2" ry="1.3" fill="#fff6dc"/>' for x, y in [(74, 64), (90, 70), (100, 80), (82, 82), (96, 92), (70, 92)])
    + shine(72, 60, 14, 4, 5, .35),
    lg('bo', [(0, '#f3c46a'), (1, '#b6772a')]))

ICONS['aycoregi'] = svg(
    f'<path d="M22 100 C6 70 30 30 74 34 C52 46 46 70 58 86 C70 100 92 102 108 94 C92 116 42 120 22 100Z" fill="url(#ay)" stroke="{OL}" stroke-width="4"/>'
    '<path d="M30 92 C22 72 38 50 62 44" fill="none" stroke="#f6d38c" stroke-width="5" stroke-linecap="round"/>'
    + ''.join(f'<ellipse cx="{x}" cy="{y}" rx="4" ry="3" fill="#7a4a1e" stroke="#3a2212" stroke-width="1.5"/>' for x, y in [(36, 80), (44, 64), (48, 96), (64, 104), (32, 66)])
    + '<path d="M40 54 q10 -6 22 -8" stroke="#fff" stroke-width="3" opacity=".5" fill="none" stroke-linecap="round"/>',
    lg('ay', [(0, '#e7a85a'), (1, '#9a5a20')], 0, 0, 1, 1))

ICONS['pide'] = svg(
    f'<path d="M6 76 Q30 50 64 50 Q98 50 122 76 Q98 104 64 104 Q30 104 6 76Z" fill="url(#pi)" stroke="{OL}" stroke-width="4"/>'
    f'<path d="M24 76 Q44 62 64 62 Q84 62 104 76 Q84 92 64 92 Q44 92 24 76Z" fill="#f4d34c" stroke="#b07a1a" stroke-width="2.5"/>'
    '<ellipse cx="64" cy="76" rx="12" ry="8" fill="#fff6d0"/><ellipse cx="64" cy="76" rx="6" ry="5" fill="#ffb21e"/>'
    + ''.join(f'<circle cx="{x}" cy="{y}" r="4.2" fill="#2f3418" stroke="#151809" stroke-width="1.2"/><circle cx="{x}" cy="{y}" r="1.4" fill="#7c8a3a"/>' for x, y in [(40, 76), (86, 74), (52, 84), (78, 84)])
    + shine(40, 60, 16, 4, -10, .35),
    lg('pi', [(0, '#efb15a'), (1, '#a8621e')]))

ICONS['baklava'] = svg(
    ''.join(f'<path d="M{x} {y-26} L{x+24} {y} L{x} {y+18} L{x-24} {y}Z" fill="url(#bk)" stroke="{OL}" stroke-width="3.5"/>'
            f'<path d="M{x-14} {y-4} L{x+14} {y-4} M{x-10} {y+6} L{x+10} {y+6}" stroke="#f9df8c" stroke-width="2"/>'
            f'<circle cx="{x}" cy="{y-6}" r="4.5" fill="#6aa83e" stroke="#2f5a1a" stroke-width="1.5"/>'
            for x, y in [(40, 84), (88, 84), (64, 66)])
    + '<path d="M28 100 Q64 112 100 100" stroke="#8a5a14" stroke-width="3" fill="none" opacity=".5"/>'
    + shine(58, 52, 8, 3, 30, .5),
    lg('bk', [(0, '#f6cf5a'), (.6, '#d4a017'), (1, '#8e6210')]))

# ---------------------------------------------------------------- hammaddeler
ICONS['bugday'] = svg(
    ''.join(f'<path d="M64 118 L{64+dx} 40" stroke="#b8913f" stroke-width="4" stroke-linecap="round"/>' for dx in (-26, -10, 8, 24))
    + ''.join(''.join(f'<ellipse cx="{64+dx*(1-k*.06):.1f}" cy="{36+k*9}" rx="6" ry="9" fill="url(#bu)" stroke="#7a5a1a" stroke-width="2" transform="rotate({dx*.8+(-1)**k*18} {64+dx*(1-k*.06):.1f} {36+k*9})"/>' for k in range(4)) for dx in (-26, -10, 8, 24))
    + f'<path d="M46 92 Q64 100 82 92 L80 100 Q64 108 48 100Z" fill="#c0392b" stroke="{OL}" stroke-width="3"/>',
    lg('bu', [(0, '#ffe08a'), (1, '#d39b2a')]))

ICONS['su'] = svg(
    f'<path d="M64 14 C64 14 24 60 24 82 C24 104 42 118 64 118 C86 118 104 104 104 82 C104 60 64 14 64 14Z" fill="url(#su)" stroke="#1d4a6e" stroke-width="4"/>'
    '<path d="M44 80 C44 96 54 104 64 106" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" opacity=".55"/>'
    + shine(52, 62, 6, 12, 25, .6),
    lg('su', [(0, '#a9e2ff'), (.5, '#55aee8'), (1, '#2d7cc2')]))

ICONS['yumurta'] = svg(
    f'<ellipse cx="46" cy="82" rx="26" ry="33" fill="url(#y1)" stroke="{OL}" stroke-width="4"/>'
    f'<ellipse cx="84" cy="86" rx="24" ry="30" fill="url(#y2)" stroke="{OL}" stroke-width="4"/>'
    + shine(38, 68, 6, 11, 15, .7) + shine(78, 74, 5, 10, 15, .5),
    rg('y1', [(0, '#fffdf6'), (1, '#e3d6bd')]) + rg('y2', [(0, '#f2c590'), (1, '#c28752')]))

ICONS['sut'] = svg(
    f'<path d="M44 34 L84 34 L84 46 Q98 58 98 74 L98 108 Q98 118 88 118 L40 118 Q30 118 30 108 L30 74 Q30 58 44 46Z" fill="url(#sb)" stroke="{OL}" stroke-width="4"/>'
    '<path d="M32 78 L96 78 L96 108 Q96 116 88 116 L40 116 Q32 116 32 108Z" fill="#fff"/>'
    f'<rect x="40" y="18" width="48" height="18" rx="5" fill="#3f78d0" stroke="{OL}" stroke-width="4"/>'
    f'<rect x="40" y="86" width="48" height="20" rx="6" fill="#3f78d0" opacity=".9"/>'
    '<path d="M50 96 l6 -5 l5 5 l6 -6 l5 6" fill="none" stroke="#fff" stroke-width="2.5"/>'
    + shine(42, 70, 4, 16, 0, .6),
    lg('sb', [(0, '#e9f2fb'), (1, '#c7d8ea')], 0, 0, 1, 0))

ICONS['cilek'] = svg(
    f'<path d="M64 118 C30 104 18 72 26 56 C34 42 52 44 64 52 C76 44 94 42 102 56 C110 72 98 104 64 118Z" fill="url(#ck)" stroke="{OL}" stroke-width="4"/>'
    + ''.join(f'<ellipse cx="{x}" cy="{y}" rx="2" ry="3" fill="#ffe48a" stroke="#b8862a" stroke-width=".8"/>' for x, y in [(44, 66), (64, 64), (84, 66), (52, 82), (76, 82), (64, 96), (40, 80), (88, 80), (64, 80)])
    + f'<path d="M64 52 L44 40 L58 42 L54 26 L64 38 L74 26 L70 42 L84 40Z" fill="#4c9a30" stroke="#24521a" stroke-width="3" stroke-linejoin="round"/>'
    + shine(42, 62, 6, 12, 25, .45),
    rg('ck', [(0, '#ff7080'), (.6, '#e8323f'), (1, '#a8121e')]))

ICONS['susam'] = svg(
    f'<path d="M26 112 Q20 76 32 54 Q40 42 64 42 Q88 42 96 54 Q108 76 102 112 Q64 122 26 112Z" fill="url(#sc)" stroke="{OL}" stroke-width="4"/>'
    f'<ellipse cx="64" cy="48" rx="30" ry="10" fill="#f6ebc5" stroke="{OL}" stroke-width="3.5"/>'
    + ''.join(f'<ellipse cx="{x}" cy="{y}" rx="2.6" ry="1.5" fill="#d8c18a"/>' for x, y in [(52, 46), (60, 50), (70, 46), (76, 50), (64, 44), (56, 42)])
    + '<path d="M40 60 Q64 66 88 60" stroke="#7a5a2a" stroke-width="4" fill="none"/>'
    + '<path d="M36 80 L92 80 M38 96 L90 96" stroke="#a8875a" stroke-width="2" opacity=".6"/>'
    + ''.join(f'<ellipse cx="{x}" cy="{y}" rx="2.6" ry="1.5" fill="#f6ebc5" stroke="#9a7a4a" stroke-width=".8"/>' for x, y in [(108, 110), (114, 104), (104, 116), (18, 112)]),
    lg('sc', [(0, '#e4cf9c'), (1, '#b5975c')], 0, 0, 1, 0))

ICONS['seker'] = svg(
    f'<path d="M64 120 C52 104 34 90 36 70 C38 56 50 50 64 50 C78 50 90 56 92 70 C94 90 76 104 64 120Z" fill="url(#pn)" stroke="{OL}" stroke-width="4"/>'
    '<path d="M48 72 Q64 78 80 72 M50 88 Q64 92 76 88" stroke="#5e1430" stroke-width="2" fill="none" opacity=".6"/>'
    f'<path d="M60 52 C40 40 34 18 44 10 C58 18 62 34 62 50Z" fill="#4c9a30" stroke="#24521a" stroke-width="3"/>'
    f'<path d="M68 52 C88 40 94 18 84 10 C70 18 66 34 66 50Z" fill="#5fb03a" stroke="#24521a" stroke-width="3"/>'
    '<path d="M44 12 Q56 30 62 48 M84 12 Q72 30 66 48" stroke="#2c6a1c" stroke-width="2" fill="none"/>'
    + shine(52, 66, 5, 10, 20, .35),
    rg('pn', [(0, '#d2506e'), (.6, '#9a2a4a'), (1, '#5e1430')]))

ICONS['bal'] = svg(
    f'<path d="M34 48 L94 48 Q104 56 104 70 L104 106 Q104 118 92 118 L36 118 Q24 118 24 106 L24 70 Q24 56 34 48Z" fill="url(#bj)" stroke="{OL}" stroke-width="4"/>'
    '<path d="M26 66 L102 66 L102 106 Q102 116 92 116 L36 116 Q26 116 26 106Z" fill="url(#hn)"/>'
    f'<rect x="30" y="32" width="68" height="18" rx="5" fill="#a0703c" stroke="{OL}" stroke-width="4"/>'
    '<path d="M30 40 L98 40" stroke="#6b4422" stroke-width="2"/>'
    f'<rect x="40" y="76" width="48" height="28" rx="5" fill="#fff4d6" stroke="#9a6a1a" stroke-width="2"/>'
    + ''.join(f'<path d="M{x} {y} l5 -3 l5 3 l0 6 l-5 3 l-5 -3Z" fill="#f2b544" stroke="#9a6a1a" stroke-width="1.2"/>' for x, y in [(50, 84), (60, 84), (55, 92), (65, 92), (70, 84)])
    + shine(32, 76, 4, 14, 0, .55),
    lg('bj', [(0, '#fff3d8'), (1, '#e9cf9b')], 0, 0, 1, 0) + lg('hn', [(0, '#f8c24e'), (1, '#d68a10')]))

ICONS['findik'] = svg(
    ''.join(f'<path d="M{x} {y-24} C{x+20} {y-20} {x+22} {y+6} {x} {y+14} C{x-22} {y+6} {x-20} {y-20} {x} {y-24}Z" fill="url(#fk)" stroke="{OL}" stroke-width="3.5"/>'
            f'<path d="M{x-14} {y-12} Q{x} {y-22} {x+14} {y-12} L{x+12} {y-8} Q{x} {y-16} {x-12} {y-8}Z" fill="#e3c08a"/>'
            + shine(x-7, y-2, 3, 7, 15, .45)
            for x, y in [(40, 96), (88, 96), (64, 72)])
    + f'<path d="M40 50 C34 34 50 20 64 22 C60 36 52 44 40 50Z" fill="#6aa040" stroke="#2f5a1a" stroke-width="3"/>'
    + f'<path d="M88 50 C94 34 78 20 64 22 C68 36 76 44 88 50Z" fill="#7ab84a" stroke="#2f5a1a" stroke-width="3"/>',
    rg('fk', [(0, '#c08a50'), (.65, '#8a5426'), (1, '#5a3214')]))

ICONS['zeytin'] = svg(
    f'<path d="M14 40 Q60 50 112 96" stroke="#6b5a2a" stroke-width="6" fill="none" stroke-linecap="round"/>'
    + ''.join(f'<path d="M{x} {y} q{dx} {dy} {dx*2} 0 q-{dx} -{dy+6} -{dx*2} 0Z" fill="#7a9a4a" stroke="#3a4a1a" stroke-width="2.5"/>' for x, y, dx, dy in [(30, 44, 10, -14), (60, 56, 10, 12), (84, 72, -10, -12), (98, 86, 8, 12)])
    + ''.join(f'<ellipse cx="{x}" cy="{y}" rx="13" ry="16" fill="url(#zt)" stroke="{OL}" stroke-width="3.5" transform="rotate({r} {x} {y})"/>' + shine(x-4, y-6, 3, 6, r, .5)
              for x, y, r in [(46, 74, -20), (72, 92, 10), (92, 112, -10)]),
    rg('zt', [(0, '#5a6a2c'), (.7, '#2f3a14'), (1, '#1a2008')]))

ICONS['un'] = svg(
    f'<path d="M28 116 Q20 80 30 52 Q34 40 46 36 L82 36 Q94 40 98 52 Q108 80 100 116 Q64 124 28 116Z" fill="url(#us)" stroke="{OL}" stroke-width="4"/>'
    f'<path d="M44 38 Q64 26 84 38 L80 44 Q64 36 48 44Z" fill="#e8dcbc" stroke="{OL}" stroke-width="3"/>'
    '<path d="M50 30 Q56 22 64 26 Q72 22 78 30" stroke="#b08a4a" stroke-width="4" fill="none"/>'
    f'<rect x="38" y="66" width="52" height="34" rx="6" fill="#c84a3a" stroke="#7a2418" stroke-width="2.5"/>'
    '<text x="64" y="92" font-family="Arial Black,Arial,sans-serif" font-weight="900" font-size="22" text-anchor="middle" fill="#fff4dc">UN</text>'
    + shine(40, 56, 5, 12, 10, .5),
    lg('us', [(0, '#fbf3df'), (1, '#dccba4')], 0, 0, 1, 0))

ICONS['hamur'] = svg(
    f'<path d="M14 100 Q12 64 50 56 Q64 50 80 56 Q116 64 114 100 Q90 116 64 116 Q38 116 14 100Z" fill="url(#hm)" stroke="{OL}" stroke-width="4"/>'
    '<path d="M30 96 Q50 108 78 104" stroke="#cdb787" stroke-width="3" fill="none"/>'
    + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity=".85"/>' for x, y, r in [(46, 70, 3), (60, 64, 2), (78, 70, 2.5), (90, 80, 2), (36, 84, 2), (66, 78, 1.6)])
    + shine(44, 70, 14, 6, -15, .6),
    rg('hm', [(0, '#fffaea'), (.7, '#f0dfb4'), (1, '#cdb787')]))

# ---------------------------------------------------------------- arayüz
ICONS['coin'] = svg(
    f'<ellipse cx="64" cy="70" rx="48" ry="46" fill="#9a6a0a" stroke="{OL}" stroke-width="4"/>'
    f'<ellipse cx="64" cy="64" rx="48" ry="46" fill="url(#cn)" stroke="{OL}" stroke-width="4"/>'
    '<ellipse cx="64" cy="64" rx="36" ry="34" fill="none" stroke="#b07c10" stroke-width="3"/>'
    '<path d="M64 38 L64 90" stroke="#a87410" stroke-width="4" stroke-linecap="round"/>'
    + ''.join(f'<ellipse cx="{64+s*7}" cy="{46+k*10}" rx="4" ry="7" fill="#f7d45a" stroke="#a87410" stroke-width="2" transform="rotate({s*-30} {64+s*7} {46+k*10})"/>' for k in range(4) for s in (-1, 1))
    + shine(44, 44, 12, 6, -35, .7),
    rg('cn', [(0, '#fff2a8'), (.5, '#f2c544'), (1, '#c48a12')]))

ICONS['star'] = svg(
    '<path d="M64 8 L76 50 L120 52 L84 76 L98 118 L64 92 L30 118 L44 76 L8 52 L52 50Z" fill="url(#st)" stroke="#8a5a00" stroke-width="5" stroke-linejoin="round"/>'
    + shine(54, 44, 8, 14, 25, .7),
    rg('st', [(0, '#fff7b0'), (.55, '#ffd23a'), (1, '#e09000')]))

ORDER = ['ekmek', 'simit', 'pogaca', 'kurabiye', 'pasta', 'borek', 'aycoregi', 'pide', 'baklava',
         'bugday', 'su', 'yumurta', 'sut', 'cilek', 'susam', 'seker', 'bal', 'findik', 'zeytin',
         'un', 'hamur', 'coin', 'star']


def main():
    os.makedirs(SRC, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    files = []
    for name in ORDER:
        p = os.path.join(SRC, name + '.svg')
        with open(p, 'w', encoding='utf-8') as f:
            f.write(ICONS[name])
        files.append(p)
    subprocess.run([INKSCAPE, '--export-type=png', f'--export-width={CELL}', f'--export-height={CELL}', *files], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cols = 6
    rows = (len(ORDER) + cols - 1) // cols
    atlas = Image.new('RGBA', (cols * CELL, rows * CELL), (0, 0, 0, 0))
    index = {}
    for i, name in enumerate(ORDER):
        im = Image.open(os.path.join(SRC, name + '.png')).convert('RGBA')
        x, y = (i % cols) * CELL, (i // cols) * CELL
        atlas.paste(im, (x, y))
        index[name] = i
    atlas.save(os.path.join(OUT, 'items.png'), optimize=True)
    with open(os.path.join(OUT, 'items.json'), 'w', encoding='utf-8') as f:
        json.dump({'cell': CELL, 'cols': cols, 'index': index}, f)
    print('atlas', atlas.size, len(ORDER), 'ikon')


if __name__ == '__main__':
    sys.exit(main())
