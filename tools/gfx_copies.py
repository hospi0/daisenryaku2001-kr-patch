# -*- coding: utf-8 -*-
"""교체할 그림의 같은 바이트 사본이 다른 파일에 있는지(읽기 전용).  python tools/gfx_copies.py"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
N = ['/SCENE/SCENE%02d.PVR' % i for i in range(29)] + ['/%s.PVR' % n for n in 'LOGOMSG DC2LUNITP0 DW2EVOP0 DW2SPECP0 DW2SPECP1 DW2SPECP3 GWL2STATP0 GWL2STATP1 GWL2STATP2 GX2MENUP1 MC2SELP1 SWND2P3'.split()]
keys = {}
for f in N:
    d = D.read(*w[f][1:3]); keys[f] = d[0x40:0x80] if len(set(d[len(d) // 2:len(d) // 2 + 64])) < 8 else d[len(d) // 2:len(d) // 2 + 64]
hits = collections.defaultdict(list); n = 0
for f, x in w.items():
    if f.endswith('.SFD') or f in N: continue
    if f.startswith(('/REAL', '/HEXUNIT', '/WEATHER', '/DP')): continue
    d = D.read(x[1], x[2]); n += 1
    for k, v in keys.items():
        if v in d: hits[k].append(f)
print('검사', n, '사본', dict(hits) or '없음')
