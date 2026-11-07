# -*- coding: utf-8 -*-
"""JIS 번호로 글자 찍어 보기 + 칸 안 잉크 범위 측정.  python tools/font_view5.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, fontlib as F
from gdi import Disc
import numpy as np
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
d = D.read(*w['/DPFONT/S18RM04P.DAT'][1:3]); print(len(d), len(d) / F.CELL)
T = '敵になるはずの国の様子が丸見えなのは何故？勝利条件を教えてください。軍事演習アイウ「」１２ＡＢ'
pg = Image.new('L', (24 * 22 * 2, 2 * 22 * 2 + 6), 60)
for k, c in enumerate(T):
    a = F.dec(d, F.idx(c)); I = Image.fromarray((a * 85).astype(np.uint8)).resize((40, 36), 0)
    pg.paste(I, ((k % 24) * 44 + 2, (k // 24) * 44 + 2))
pg.save('work/font_jis.png')
vals = np.zeros(4, int); x0 = 99; x1 = 0; y0 = 99; y1 = 0
for c in T:
    a = F.dec(d, F.idx(c)); vals += np.bincount(a.ravel(), minlength=4)
    ys, xs = np.nonzero(a)
    if len(xs): x0 = min(x0, xs.min()); x1 = max(x1, xs.max()); y0 = min(y0, ys.min()); y1 = max(y1, ys.max())
print('값 분포', vals, '잉크 x', x0, x1, 'y', y0, y1)
used = sum(1 for i in range(len(d) // F.CELL) if d[i * 90:(i + 1) * 90].strip(b'\0')); print('채워진 칸', used)
