# -*- coding: utf-8 -*-
"""SCG 적재 코드 찾기(읽기 전용).  python tools/scg_loader.py"""
import sys, os, re, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, sh4dis
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3]); B = 0x8C010000

def refs(addr):
    out = []
    for m in re.finditer(re.escape(struct.pack('<I', addr)), e[:0xB0000]):
        L = m.start()
        if L % 4: continue
        for pc in range(max(0, L - 1024), L, 2):
            op = struct.unpack_from('<H', e, pc)[0]
            if op >> 12 == 0xD and ((pc + 4) & ~3) + (op & 255) * 4 == L: out.append(pc)
    return out

for pat in (b'.SCG', b'.scg', b'SCENARIO', b'%s.SCG'):
    for m in re.finditer(re.escape(pat), e):
        s = m.start()
        while e[s - 1] >= 0x20 and m.start() - s < 24: s -= 1
        print(pat, hex(m.start()), e[s:m.start() + 12], '참조', [hex(B + x) for x in refs(B + s)])
print('---F2CC 쓰는 곳')
for L in (0x1A0C6, 0x8D44C, 0x9A33A, 0x9A53E):
    for pc in range(max(0, L - 512), L, 2):
        op = struct.unpack_from('<H', e, pc)[0]
        if op >> 12 == 0x9 and pc + 4 + (op & 255) * 2 == L:
            print('MOV.W', hex(B + pc), 'R%d' % (op >> 8 & 15))
            for l in sh4dis.dis(pc - 0x30, 44, e): print(l[:54])
print('---길이 표 0x8C3B1914')
for pc in refs(0x8C3B1914)[:30]: print(hex(B + pc), end=' ')
print()
