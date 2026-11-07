# -*- coding: utf-8 -*-
"""글꼴 포인터 변수(0x8C6B37D0)를 읽는 코드 찾기(읽기 전용).  python tools/font_code2.py"""
import sys, os, re, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, sh4dis
from gdi import Disc

B = 0x8C010000
VAR = 0x8C6B37D0

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    D = Disc(1); ie.D = D
    w = {x[0]: x for x in ie.walk() if not x[3] & 2}
    e = D.read(*w['/1ST_READ.BIN'][1:3])
    s = open('work/state11.bin', 'rb').read()
    rb = s.find(e[0x1000:0x1100]) - 0x1000 - 0x10000
    ram = s[rb:rb + 0x1000000]
    print('변수 값', hex(struct.unpack_from('<I', ram, VAR - 0x8C000000)[0]))
    d = D.read(*w['/DPFONT/S18RM04P.DAT'][1:3])
    fo = ram.find(d[20000:20512]) - 20000; print('글꼴 RAM', hex(0x8C000000 + fo))
    print('글꼴 주소 담은 곳', [hex(0x8C000000 + m.start()) for m in re.finditer(re.escape(struct.pack('<I', 0x8C000000 + fo)), ram)][:12])
    lits = [m.start() for m in re.finditer(re.escape(struct.pack('<I', VAR)), e) if m.start() % 4 == 0]
    print('변수 리터럴', [hex(x) for x in lits])
    # 리터럴을 읽는 MOV.L @(disp,PC),Rn 찾기
    for lit in lits:
        for pc in range(max(0, lit - 1024), lit, 2):
            op = struct.unpack_from('<H', e, pc)[0]
            if op >> 12 == 0xD and ((pc + 4) & ~3) + (op & 255) * 4 == lit:
                print('--- 읽는 곳', hex(B + pc), 'R%d' % (op >> 8 & 15))
                for l in sh4dis.dis(max(0, pc - 0x30), 90, e): print(l[:60])

if __name__ == '__main__':
    main()
