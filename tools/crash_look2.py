# -*- coding: utf-8 -*-
"""크래시 PC 후보·레지스터 영역·SCG 파서 찾기(읽기 전용)."""
import sys, os, re, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, rzip, sh4dis
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3]); B = 0x8C010000
s = rzip.unrzip(open('work/states_crash/crash1.state', 'rb').read())
rb = s.find(e[0x1000:0x1100]) - 0x1000 - 0x10000
ram = s[rb:rb + 0x1000000]
t = rb + 0x1000000
print('뒤 구역 0x1C0~0x2C0')
for o in range(0x1C0, 0x2C0, 16):
    print(hex(o), ' '.join('%08x' % v for v in struct.unpack_from('<4I', s, t + o)))
print('앞 0x8c0~0x930')
for o in range(0x8C0, 0x930, 16):
    print(hex(o), ' '.join('%08x' % v for v in struct.unpack_from('<4I', s, o)))
for pc in (0x8C31C656,):
    o = pc - B
    print('코드 일치', ram[pc - 0x8C000000:pc - 0x8C000000 + 16] == e[o:o + 16])
    for l in sh4dis.dis(o - 0x40, 48, ram[0x10000:]): print(l[:58])
for v in (0xF2C8, 0xF2CA, 0xF2CB, 0xF2CC):
    hs = [m.start() for m in re.finditer(re.escape(struct.pack('<I', v)), e) if m.start() % 4 == 0 and m.start() < 0xB0000]
    hw = [m.start() for m in re.finditer(re.escape(struct.pack('<H', v)), e) if m.start() % 2 == 0 and m.start() < 0xB0000]
    print(hex(v), '리터럴32', [hex(x) for x in hs][:6], '16', [hex(x) for x in hw][:10])
print('버퍼 주소 담은 곳', [hex(0x8C000000 + m.start()) for m in re.finditer(re.escape(struct.pack('<I', 0x8CD30240)), ram)][:10])
