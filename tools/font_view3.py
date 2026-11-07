# -*- coding: utf-8 -*-
"""S18 비트 폭 측정: 비트열을 폭 w 로 접었을 때 위아래 줄 일치율.  python tools/font_view3.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
import numpy as np
from PIL import Image

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    D = Disc(1); ie.D = D
    w = {x[0]: x for x in ie.walk() if not x[3] & 2}
    d = D.read(*w['/DPFONT/S18RM04P.DAT'][1:3])
    b = np.unpackbits(np.frombuffer(d[200000:320000], np.uint8))
    on = b.mean(); print('켜진 비율', round(float(on), 3))
    r = []
    for k in range(8, 80):
        m = (b[:-k] & b[k:]).sum() / max(1, b.sum()); r.append((round(float(m), 3), k))
    print(sorted(r, reverse=True)[:12])
    best = sorted(r, reverse=True)[0][1]
    for ww in sorted({x[1] for x in sorted(r, reverse=True)[:3]}):
        hh = 360 // ww if 360 % ww == 0 else 18
        st = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
        cols, rows = 36, 12
        pg = Image.new('L', (cols * (ww + 3), rows * (hh + 3)), 50)
        al = np.unpackbits(np.frombuffer(d, np.uint8))
        for k in range(cols * rows):
            o = (st + k) * 360; g = al[o:o + ww * hh].reshape(hh, ww) * 255
            pg.paste(Image.fromarray(g.astype(np.uint8)), ((k % cols) * (ww + 3) + 1, (k // cols) * (hh + 3) + 1))
        pg.save('work/font18_w%d.png' % ww); print(ww, hh)

if __name__ == '__main__':
    main()
