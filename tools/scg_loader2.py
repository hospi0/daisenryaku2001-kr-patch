# -*- coding: utf-8 -*-
"""시나리오 표 레코드와 적재 함수 역어셈(읽기 전용)."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, sh4dis
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3]); B = 0x8C010000
for o in (0x207020 - 0x60, 0x207020 + 0x8C - 0x60):
    print(hex(o), e[o:o + 0x90].hex(' '))
for f in ('000EXERC', '001EXERC'):
    d = D.read(*w['/SCENARIO/%s.SCG' % f][1:3]); print(f, len(d), hex(len(d)), d[:8].hex(' '))
for l in sh4dis.dis(0x3500, 150, e): print(l[:54])
