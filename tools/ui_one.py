# -*- coding: utf-8 -*-
"""UI 그림 «한 장만» 다시 만들어 미리보기 폴더에(ui_new 는 안 건드림). python tools/ui_one.py 이름 폴더"""
import sys, os, tempfile, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import ui_labels as U
n, pv = sys.argv[1:3]
os.makedirs(pv, exist_ok=True); tmp = tempfile.mkdtemp(prefix='ui')
fmt, boxes = U.T[n]
a = np.asarray(Image.open('work/gfx/orig/%s.png' % n).convert('RGBA')).copy()
for x0, y0, x1, y1 in U.CLR.get(n, []): a[y0:y1, x0:x1] = 0
for b in boxes: U.apply(a, b, n)
im = Image.fromarray(a); im.save(os.path.join(pv, n + '.png'))
q, dec = U.vq(im, fmt, n, tmp)
shutil.copyfile(q, os.path.join(pv, n + '.pvrnew')); dec.save(os.path.join(pv, n + '_vq.png'))
old = Image.open('work/gfx/ui_new/%s_vq.png' % n).convert('RGBA'); S = 4
pg = Image.new('RGB', (old.width * S * 2 + 12, old.height * S), (60, 90, 70))
for i, g in enumerate((old, dec)):
    r = g.resize((old.width * S, old.height * S), Image.NEAREST); pg.paste(r, (i * (old.width * S + 12), 0), r)
pg.save(os.path.join(pv, '비교_전_후.png')); shutil.rmtree(tmp, ignore_errors=True)
d = np.abs(np.asarray(Image.open('work/gfx/ui_new/%s.png' % n).convert('RGBA'), int) - np.asarray(im, int)).sum(2)
ys, xs = np.nonzero(d); print('바뀐 화소', len(xs), '범위', xs.min(), ys.min(), xs.max(), ys.max())
