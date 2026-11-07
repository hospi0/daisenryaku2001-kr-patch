# -*- coding: utf-8 -*-
"""제목 칸 크기 측정(읽기 전용)."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
c = collections.Counter(); nx = collections.Counter(); ex = []
for f, x in sorted(w.items()):
    if not f.startswith('/SCENARIO/'): continue
    d = D.read(x[1], x[2]); t = d[8:0x78].split(b'\0')[0]; c[len(t)] += 1
    ex.append((len(t), f.split('/')[-1], d[8:0x30].hex(' ')))
print(sorted(c.items()))
for e in sorted(ex, reverse=True)[:5]: print(e)
for e in sorted(ex)[:3]: print(e)
col = collections.Counter()
for off in range(8, 0x40):
    col[off] = len({D.read(x[1], x[2])[off] for f, x in w.items() if f.startswith('/SCENARIO/')})
print('칸별 값 종류', [(hex(k), v) for k, v in sorted(col.items())])
