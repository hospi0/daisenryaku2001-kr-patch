# -*- coding: utf-8 -*-
"""크래시 스테이트 판독(읽기 전용): RAM 위치, SCG 적재 여부, 화면 문자열, SH4 레지스터 후보."""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, rzip
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3]); scg = D.read(*w['/SCENARIO/000EXERC.SCG'][1:3])
for fn in sys.argv[1:]:
    s = rzip.unrzip(open(fn, 'rb').read()); print(fn, len(s))
    p = s.find(e[0x1000:0x1100]); rb = p - 0x1000 - 0x10000; print(' RAM 시작', rb)
    ram = s[rb:rb + 0x1000000]
    q = ram.find(scg[0x4000:0x4100]); print(' SCG 몸통', hex(0x8C000000 + q - 0x4000) if q >= 0 else None)
    for t in ('청군',): pass
    h = ram.find(b'\x52\x53\x10\x01'); print(' RS 머리', hex(0x8C000000 + h) if h >= 0 else None)
    if h >= 0:
        print('  제목', ram[h + 8:h + 40].hex(' ')); print('  이름 머리', ram[h + 0xF2C8:h + 0xF2E0].hex(' '))
    print(' 글꼴 변수', hex(struct.unpack_from('<I', ram, 0x6B37D0)[0]))
    # RAM 밖 앞쪽에서 코드 주소처럼 보이는 값 (SH4 문맥 후보)
    c = collections.Counter()
    for base, name in ((0, '앞'), (rb + 0x1000000, '뒤')):
        seg = s[base:base + 0x400000] if name == '뒤' else s[:min(rb, 0x400000)]
        hits = [(o, struct.unpack_from('<I', seg, o)[0]) for o in range(0, len(seg) - 3, 4) if 0x8C010000 <= struct.unpack_from('<I', seg, o)[0] < 0x8C3A0000]
        print(' ', name, '코드 주소 값', len(hits), [(hex(o), hex(v)) for o, v in hits[:12]])
