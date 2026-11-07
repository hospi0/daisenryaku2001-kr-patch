# -*- coding: utf-8 -*-
"""루트·UI 쪽 PVR 목록(읽기 전용)."""
import sys, os, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
r = [f for f in w if f.count('/') == 1 and f.endswith('.PVR')]
print('루트 PVR', len(r))
fm = collections.Counter(); rows = []
for f in sorted(r):
    d = D.read(*w[f][1:3]); o = d.find(b'PVRT')
    if o < 0: rows.append((f, 'noPVRT')); continue
    px, dt = d[o + 8], d[o + 9]; W, H = struct.unpack_from('<HH', d, o + 12)
    fm[(px, dt)] += 1; rows.append((f[1:], len(d), px, dt, W, H))
print(fm.most_common())
print(' '.join('%s:%dx%d' % (x[0][:-4], x[4], x[5]) for x in rows if len(x) > 2))
print([f for f in w if f.count('/') == 2 and f.endswith('.PVR') and f.split('/')[1] in ('SCENE', 'WEATHER', 'REALETC')][:12])
