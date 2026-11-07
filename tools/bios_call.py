# -*- coding: utf-8 -*-
"""BIOS 글꼴 주소 함수 호출부(읽기 전용)."""
import sys, os, re, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, sh4dis
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3]); B = 0x8C010000
for a in (0x8C30C8D0, 0x8C30C8E4, 0x8C30C8F8):
    for m in re.finditer(re.escape(struct.pack('<I', a)), e):
        L = m.start()
        if L % 4: continue
        for pc in range(max(0, L - 1024), L, 2):
            op = struct.unpack_from('<H', e, pc)[0]
            if op >> 12 == 0xD and ((pc + 4) & ~3) + (op & 255) * 4 == L:
                print('호출', hex(a), '리터럴', hex(L), '읽는 곳', hex(B + pc))

for a in (0x8C30C914, 0x8C30CBCC, 0x8C015220):
    for m in re.finditer(re.escape(struct.pack('<I', a)), e):
        L = m.start()
        if L % 4: continue
        rd = [pc for pc in range(max(0, L - 1024), L, 2) if struct.unpack_from('<H', e, pc)[0] >> 12 == 0xD and ((pc + 4) & ~3) + (struct.unpack_from('<H', e, pc)[0] & 255) * 4 == L]
        print(hex(a), '리터럴', hex(L), [hex(B + x) for x in rd])
