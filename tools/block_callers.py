# -*- coding: utf-8 -*-
"""블록 복사 함수의 호출부와 버퍼 크기, 원본 블록 길이 분포(읽기 전용)."""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, sh4dis
from gdi import Disc
from scg_audit2 import tail
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3]); B = 0x8C010000
# 함수 시작: 0x19E0 앞으로 푸시 열
for l in sh4dis.dis(0x19C0, 16, e): print(l[:50])
slot = collections.Counter(); mx = collections.Counter(); big = []
for f, x in sorted(w.items()):
    if not f.startswith('/SCENARIO/') or f.endswith('MAPEDIT.SCG'): continue
    d = D.read(x[1], x[2]); a, ls, s, _ = tail(d)
    sl = struct.unpack_from('<20H', d, a)
    for i, L in enumerate(sl):
        if L:
            mx[i] = max(mx[i], L); big.append((L, f.split('/')[-1], i))
print('칸별 최대', sorted(mx.items())); print('최대 블록', sorted(big, reverse=True)[:6])
for fn in range(0x19C0, 0x19E2, 2):
    a = B + fn
    lit = [m.start() for m in re.finditer(re.escape(struct.pack('<I', a)), e) if m.start() % 4 == 0 and m.start() < 0xB0000]
    bsr = []
    for pc in range(0, 0xB0000, 2):
        op = struct.unpack_from('<H', e, pc)[0]
        if op >> 12 == 0xB:
            dsp = op & 0xFFF
            if dsp & 0x800: dsp -= 0x1000
            if pc + 4 + dsp * 2 == fn: bsr.append(pc)
    if lit or bsr: print(hex(a), '리터럴', [hex(x) for x in lit], 'BSR', [hex(x) for x in bsr])
    for L in lit:
        for pc in range(max(0, L - 1024), L, 2):
            op = struct.unpack_from('<H', e, pc)[0]
            if op >> 12 == 0xD and ((pc + 4) & ~3) + (op & 255) * 4 == L:
                print('--- 호출', hex(B + pc))
                for l in sh4dis.dis(max(0, pc - 0x18), 26, e): print(l[:52])
    for pc in bsr:
        print('--- BSR', hex(B + pc))
        for l in sh4dis.dis(max(0, pc - 0x18), 18, e): print(l[:52])
