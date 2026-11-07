# -*- coding: utf-8 -*-
"""S18RM04P.DAT 칸 구조: 15,616자 × 45 B = 18행 × 20비트 가설.  python tools/font_view2.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
import numpy as np
from PIL import Image

def bits(b):
    return np.unpackbits(np.frombuffer(b, np.uint8))

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    D = Disc(1); ie.D = D
    w = {x[0]: x for x in ie.walk() if not x[3] & 2}
    d = D.read(*w['/DPFONT/S18RM04P.DAT'][1:3]); print(len(d), len(d) / 45)
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 700
    cols, rows = 40, 20
    for name, ww, hh in (('a', 20, 18), ('b', 18, 20)):
        pg = Image.new('L', (cols * (ww + 3), rows * (hh + 3)), 50)
        for k in range(cols * rows):
            i = start + k; b = bits(d[i * 45:(i + 1) * 45])[:ww * hh].reshape(hh, ww) * 255
            pg.paste(Image.fromarray(b.astype(np.uint8)), ((k % cols) * (ww + 3) + 1, (k // cols) * (hh + 3) + 1))
        pg.save('work/font18%s.png' % name)

if __name__ == '__main__':
    main()
