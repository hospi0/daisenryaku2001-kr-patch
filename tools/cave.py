# -*- coding: utf-8 -*-
"""빈 코드 자리(NOP 열) 찾기(읽기 전용)."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3])
r = []; p = 0
while p < 0xB0000:
    if e[p:p + 2] == b'\x09\x00':
        q = p
        while e[q:q + 2] == b'\x09\x00': q += 2
        if q - p >= 56: r.append((q - p, hex(p)))
        p = q
    else: p += 2
print(len(r), sorted(r, reverse=True)[:10]); print([x for x in r if 0x4000 < int(x[1], 16) < 0x7000][:8])
