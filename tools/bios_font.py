# -*- coding: utf-8 -*-
"""BIOS 글꼴 벡터 사용 코드(읽기 전용)."""
import sys, os, re, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, sh4dis
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3]); B = 0x8C010000
for v in (0x8C0000B4, 0x8C0000B0):
    for m in re.finditer(re.escape(struct.pack('<I', v)), e):
        L = m.start()
        if L % 4: continue
        print(hex(v), '리터럴', hex(L))
        for pc in range(max(0, L - 1024), L, 2):
            op = struct.unpack_from('<H', e, pc)[0]
            if op >> 12 == 0xD and ((pc + 4) & ~3) + (op & 255) * 4 == L:
                print('--- 읽는 곳', hex(B + pc))
                for l in sh4dis.dis(pc - 0x10, 22, e):
                    if '0009  NOP' not in l: print(l[:54])
