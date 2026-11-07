# -*- coding: utf-8 -*-
"""SCG 머리 +4 값이 체크섬인지 시험 + 파일 적재 함수 역어셈(읽기 전용)."""
import sys, os, struct, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, sh4dis
from gdi import Disc
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3])
fs = [f for f in w if f.startswith('/SCENARIO/')][:6]
for f in fs:
    d = D.read(*w[f][1:3]); v = struct.unpack_from('<I', d, 4)[0]; b = d[8:]
    a = np.frombuffer(b, np.uint8).astype(np.uint64)
    n4 = len(b) // 4 * 4
    u32 = np.frombuffer(b[:n4], '<u4').astype(np.uint64)
    n2 = len(b) // 2 * 2
    u16 = np.frombuffer(b[:n2], '<u2').astype(np.uint64)
    c = {'crc': zlib.crc32(b), 'crc_all0': zlib.crc32(d[:4] + b'\0\0\0\0' + b), 'adler': zlib.adler32(b), 'sum8': int(a.sum()) & 0xFFFFFFFF, 'sum16': int(u16.sum()) & 0xFFFFFFFF, 'sum32': int(u32.sum()) & 0xFFFFFFFF}
    print(f.split('/')[-1], hex(v), len(d), {k: hex(x) for k, x in c.items()}, [k for k, x in c.items() if x == v or (~x & 0xFFFFFFFF) == v or (-x & 0xFFFFFFFF) == v])
print('머리', D.read(*w[fs[0]][1:3])[:24].hex(' '))
for l in sh4dis.dis(0xF7C, 90, e): print(l[:52])
import re
for pat in (b'RS\x10\x01', struct.pack('<I', 0x01105352), struct.pack('<I', 0x01105352)[::-1]):
    print(pat, [hex(m.start()) for m in re.finditer(re.escape(pat), e)][:8])
