# -*- coding: utf-8 -*-
"""UI 그림이 어느 스테이트 메모리(VRAM 포함)에 올라와 있는지 + 실행 파일 안 이름 옆 문자열(읽기 전용)."""
import sys, os, glob, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, rzip
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
N = 'DC2LUNITP0 DW2EVOP0 DW2SPECP0 DW2SPECP1 DW2SPECP3 GWL2STATP0 GWL2STATP1 GWL2STATP2 GX2MENUP1 MC2SELP1 SWND2P3'.split()
keys = {}
for n in N:
    d = D.read(*w['/%s.PVR' % n][1:3]); o = d.find(b'PVRT') + 16
    keys[n] = d[o + 2048 + 512:o + 2048 + 576] if len(d) > 4000 else d[o + 256:o + 320]    # 코드북 뒤 색인
    keys[n + '#cb'] = d[o + 64:o + 128]
fs = sorted(glob.glob('work/states/*.state*'), key=lambda p: int(re.search(r'(\d+)\.state', p).group(1)))
res = {n: [] for n in N}
for p in fs:
    s = rzip.unrzip(open(p, 'rb').read()); k = os.path.basename(p).split('.')[0]
    for n in N:
        if keys[n] in s or keys[n + '#cb'] in s: res[n].append(k)
for n in N: print(n, res[n])
e = D.read(*w['/1ST_READ.BIN'][1:3])
for m in re.finditer(rb'(?i)dc2lunitp0', e):
    print(hex(m.start()), e[m.start() - 60:m.start() + 60])
