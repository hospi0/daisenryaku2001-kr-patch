# -*- coding: utf-8 -*-
"""스택 복귀 주소 + SCG 파서 역어셈(읽기 전용)."""
import sys, os, re, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, rzip, sh4dis
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3]); B = 0x8C010000
s = rzip.unrzip(open(sys.argv[1], 'rb').read())
rb = s.find(e[0x1000:0x1100]) - 0x1000 - 0x10000
ram = s[rb:rb + 0x1000000]; t = rb + 0x1000000
r = struct.unpack_from('<16I', s, t + 0x1CC); print('R', ['%08x' % v for v in r], 'PC %08x' % struct.unpack_from('<I', s, t + 0x23C)[0])
sp = r[15] - 0x8C000000
st = [(sp + i * 4, struct.unpack_from('<I', ram, sp + i * 4)[0]) for i in range(0, 300)]
ret = []
for a, v in st:
    if B <= v < B + 0xB0000 and v % 2 == 0:
        o = v - B
        op = struct.unpack_from('<H', e, o - 4)[0]
        if (op & 0xF0FF) in (0x400B, 0x0003) or op >> 12 == 0xB:
            ret.append((hex(a + 0x8C000000), hex(v)))
print('복귀 주소', ret[:24])
