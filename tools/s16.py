# -*- coding: utf-8 -*-
"""16번 전투 화면 글자 출처(읽기 전용)."""
import sys, os, re, struct, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, rzip
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3])
s = rzip.unrzip(open(glob.glob('work/states/16.state*')[0], 'rb').read())
rb = s.find(e[0x1000:0x1100]) - 0x1000 - 0x10000; ram = s[rb:rb + 0x1000000]
print('RAM', rb, '글꼴 변수', hex(struct.unpack_from('<I', ram, 0x6B37D0)[0]))
for n in ('S18RM04P', 'S20RM04P', 'S24RM04P', 'S26RM04P'):
    d = D.read(*w['/DPFONT/%s.DAT' % n][1:3]); print(n, s.find(d[300000:300256]))
b = '狙撃小隊 1935'.encode('cp932')
hits = [m.start() for m in re.finditer(re.escape(b), s)]
print('문자열 위치(스테이트)', [hex(x) for x in hits][:6], '실행 파일 안', e.find(b), [hex(0x8C000000 + x - rb) for x in hits if rb <= x < rb + 0x1000000][:6])
for x in hits[:4]:
    print(hex(x), s[x - 16:x + 24].hex(' '))
for pat in (b'SCG', b'REAL.OSB'):
    pass
print([f for f in w if 'REALFONT' in f or f.startswith('/REALINF')][:6], len([f for f in w if f.startswith('/REALINF')]))
