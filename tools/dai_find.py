# -*- coding: utf-8 -*-
"""第 이 든 곳 전수(읽기 전용)."""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
d = D.read(*w['/SCENARIO/MAPEDIT.SCG'][1:3])
print('MAPEDIT', len(d), d[:40].hex(' '))
for m in re.finditer(b'\x91\xe6', d): print(hex(m.start()), d[m.start() - 4:m.start() + 16].hex(' '), d[m.start():m.start() + 14].decode('cp932', 'replace'))
for r in (0x78, 0x78 + 0x144C):
    print(hex(r), d[r:r + 24].hex(' '), d[r:r + 24].split(b'\0')[0].decode('cp932', 'replace'))
print('이름 구역', d[0xF2C8:0xF2F0].hex(' '))
for t in ('首都', '第1軍', '第１軍', '第%d軍', '第%2d軍'):
    e = D.read(*w['/1ST_READ.BIN'][1:3]); b = t.encode('cp932')
    print(t, [hex(m.start()) for m in re.finditer(re.escape(b), e)][:6], [hex(m.start()) for m in re.finditer(re.escape(b), d)][:6])
