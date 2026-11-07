# -*- coding: utf-8 -*-
"""DPFONT 판독(읽기 전용): 크기별 칸 나눔 확인, 시트, 스테이트 안에 글꼴이 있는지.  python tools/font_view.py"""
import sys, os, re, struct, zlib, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
import numpy as np
from PIL import Image

def glyph(d, i, w, h, row):
    o = i * row * h; a = np.zeros((h, w), np.uint8)
    for y in range(h):
        r = d[o + y * row:o + (y + 1) * row]; v = int.from_bytes(r, 'big')
        for x in range(w):
            if v >> (row * 8 - 1 - x) & 1: a[y, x] = 255
    return a

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    D = Disc(1); ie.D = D
    w = {x[0]: x for x in ie.walk() if not x[3] & 2}
    d = D.read(*w['/DPFONT/S24RM04P.DAT'][1:3]); print(len(d), d[:32].hex(' '))
    cols = 48; rows = 24; start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    pg = Image.new('L', (cols * 26, rows * 26), 40)
    for k in range(cols * rows):
        g = glyph(d, start + k, 24, 24, 3); pg.paste(Image.fromarray(g), ((k % cols) * 26 + 1, (k // cols) * 26 + 1))
    pg.save('work/font24.png')
    for f in ('1.state', '11.state'):
        s = open('work/states/' + f, 'rb').read(); print(f, len(s), s[:24].hex(' '), s[:8])
        for off in (0, 4, 8, 12, 16, 32):
            try:
                z = zlib.decompress(s[off:]); print(' zlib', off, len(z)); break
            except Exception: pass

if __name__ == '__main__':
    main()
