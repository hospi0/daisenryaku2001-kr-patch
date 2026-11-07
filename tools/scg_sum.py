# -*- coding: utf-8 -*-
"""SCG 체크섬: 파일 +8 부터 0xE2C0 B, 0x8C046100(MSB 우선 CRC32, 초기 -1, 끝 NOT). 표 = 1ST_READ 0x180214."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SPAN = 0xE2C0

def table(e):
    return struct.unpack_from('<256I', e, 0x180214)

def crc(b, t):
    c = 0xFFFFFFFF
    for x in b:
        c = ((c << 8) & 0xFFFFFFFF) ^ t[(c >> 24) ^ x]
    return c ^ 0xFFFFFFFF

if __name__ == '__main__':
    import iso_extract as ie
    from gdi import Disc
    sys.stdout.reconfigure(encoding='utf-8')
    D = Disc(1); ie.D = D
    w = {x[0]: x for x in ie.walk() if not x[3] & 2}
    t = table(D.read(*w['/1ST_READ.BIN'][1:3])); ok = 0; n = 0; bad = []
    for f, x in sorted(w.items()):
        if not f.startswith('/SCENARIO/'): continue
        d = D.read(x[1], x[2]); n += 1
        if crc(d[8:8 + SPAN], t) == struct.unpack_from('<I', d, 4)[0]: ok += 1
        else: bad.append(f)
    print('일치', ok, '/', n, bad[:5])
