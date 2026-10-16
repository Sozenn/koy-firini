"""Baloo 2 (SIL OFL) yazı tipinden oyunun web fontlarını üretir.

Değişken fonttan 600 ve 800 kalınlıkta iki örnek çıkarılır, Türkçe dahil Latin
karakterlere indirgenir ve woff2 olarak assets/fonts altına yazılır.
Kullanım: python assets-src/font.py <Baloo2[wght].ttf yolu>
"""
import os
import sys

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'fonts')
TEXT = ''.join(chr(c) for c in range(0x20, 0x7f)) + 'çÇğĞıİöÖşŞüÜâÂîÎûÛéÉ·•–—‘’“”…×÷→←↑↓★☆✦✓○●◆♥⏸€₺°'


def build(src, weight, name):
    font = TTFont(src)
    inst = instancer.instantiateVariableFont(font, {'wght': weight})
    tmp = os.path.join(OUT, name + '.ttf')
    inst.save(tmp)
    opts = subset.Options()
    opts.flavor = 'woff2'
    opts.layout_features = ['kern', 'liga', 'locl']
    opts.name_IDs = ['*']
    f = subset.load_font(tmp, opts)
    sub = subset.Subsetter(opts)
    sub.populate(text=TEXT)
    sub.subset(f)
    subset.save_font(f, os.path.join(OUT, name + '.woff2'), opts)
    return tmp


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    src = sys.argv[1]
    for w, n in [(600, 'baloo2-600'), (800, 'baloo2-800')]:
        build(src, w, n)
        print('font', n)
