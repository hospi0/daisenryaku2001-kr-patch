# -*- coding: utf-8 -*-
"""이름 구역 앞에서 읽기: 머리 u16 크기 + u8 개수 검산(읽기 전용)."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
from scg_audit2 import tail
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
ok = 0
for f, x in sorted(w.items()):
    if not f.startswith('/SCENARIO/') or f.endswith('MAPEDIT.SCG'): continue
    d = D.read(x[1], x[2]); a = tail(d)[0]; size = struct.unpack_from('<H', d, 0xF2C8)[0]; n = d[0xF2CA]; q = 0xF2CB; c = 0
    while q < a - 1 and c < 400:
        L = d[q]; q += 1 + L; M = d[q]; q += 1 + M; c += 1
    good = q == 0xF2CA + size and ((q + 1) & ~1) == a
    if good and c == n: ok += 1
    else:
        print(f, 'a', hex(a), 'size', hex(size), '끝', hex(0xF2CB + size), 'n', n, '읽은 쌍', c, 'q', hex(q))
        # 실패 지점 부근
        q = 0xF2CB
        for i in range(n):
            L = d[q]; t = d[q + 1:q + 1 + L]; r = q + 1 + L; M = d[r]; u = d[r + 1:r + 1 + M]
            bad = any(b >= 0x7f or b < 0x20 for b in u)
            try: t.decode('cp932')
            except Exception: bad = True
            if bad: print('  ', i, hex(q), t.decode('cp932', 'replace'), u)
            q = r + 1 + M
print('맞음', ok)
