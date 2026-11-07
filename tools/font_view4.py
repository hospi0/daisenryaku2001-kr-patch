# -*- coding: utf-8 -*-
"""S18 칸 풀기: 40비트 줄 = 두 줄 교차(가설 A) / 20비트 앞뒤(가설 B).  python tools/font_view4.py [시작 칸]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
import numpy as np
from PIL import Image

def dec(d, i, mode):
    b = np.unpackbits(np.frombuffer(d[i * 45:(i + 1) * 45], np.uint8)).reshape(9, 2, 20)
    return np.concatenate([b[:, 0, :], b[:, 1, :]], 0)      # 40비트 줄 = 위쪽 반 + 아래쪽 반

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    D = Disc(1); ie.D = D
    w = {x[0]: x for x in ie.walk() if not x[3] & 2}
    d = D.read(*w['/DPFONT/S18RM04P.DAT'][1:3])
    st = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    cols, rows = 30, 14
    pg = Image.new('L', (cols * 23 * 2, rows * 21 * 2), 50)
    for k in range(cols * rows):
        g = (dec(d, st + k, 'A') * 255).astype(np.uint8); I = Image.fromarray(g).resize((40, 36), 0)
        pg.paste(I, ((k % cols) * 46 + 2, (k // cols) * 42 + 2))
    pg.save('work/font18_A.png'); print(pg.size)

if __name__ == '__main__':
    main()
