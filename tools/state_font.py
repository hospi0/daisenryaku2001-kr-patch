# -*- coding: utf-8 -*-
"""스테이트 메모리에 글꼴 파일·문자열이 있는지(읽기 전용)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, rzip
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
f = [n for n in dir(rzip) if not n.startswith('_')]; print(f)
fn = getattr(rzip, 'load', None) or getattr(rzip, 'read', None) or getattr(rzip, 'decompress', None) or getattr(rzip, 'unrzip', None)
s = fn(open('work/states/11.state', 'rb').read()) if fn.__name__ in ('decompress', 'unrzip') else fn('work/states/11.state')
print(len(s)); open('work/state11.bin', 'wb').write(s)
for n in ('S18RM04P', 'S20RM04P', 'S24RM04P', 'S26RM04P'):
    d = D.read(*w['/DPFONT/%s.DAT' % n][1:3])
    hits = []
    for o in (20000, 100000, 300000, 600000):
        c = d[o:o + 512]
        if c.strip(b'\0'): hits.append((o, s.find(c)))
    print(n, hits)
for t in ('「ゲーム」のどの項目を？', '勝利条件を教えてください'):
    print(t, s.find(t.encode('cp932')))
e = D.read(*w['/1ST_READ.BIN'][1:3]); print('exe 위치', s.find(e[0x1000:0x1100]))
