# -*- coding: utf-8 -*-
"""글꼴 파일 이름 참조 코드와 메모리 위치 추적(읽기 전용).  python tools/font_code.py"""
import sys, os, re, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, sh4dis
from gdi import Disc

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    D = Disc(1); ie.D = D
    w = {x[0]: x for x in ie.walk() if not x[3] & 2}
    e = D.read(*w['/1ST_READ.BIN'][1:3]); B = 0x8C010000
    a = e.find(b'S18RM04P.DAT'); print('이름', hex(a), e[a - 24:a + 40])
    for m in re.finditer(b'DPFONT|S18RM|S20RM|S24RM', e): print(hex(m.start()), e[m.start() - 2:m.start() + 16])
    refs = [m.start() for m in re.finditer(re.escape(struct.pack('<I', a + B)), e)]; print('참조', [hex(r) for r in refs])
    s = open('work/state11.bin', 'rb').read()
    rb = s.find(e[0x1000:0x1100]) - 0x1000 - 0x10000; print('RAM 시작(스테이트)', rb)
    d = D.read(*w['/DPFONT/S18RM04P.DAT'][1:3]); fo = s.find(d[20000:20512]) - 20000 - rb; print('글꼴 RAM', hex(0x8C000000 + fo))
    v = struct.pack('<I', 0x8C000000 + fo); hits = [m.start() - rb for m in re.finditer(re.escape(v), s[rb:rb + 0x1000000])]; print('글꼴 주소를 담은 곳', [hex(0x8C000000 + h) for h in hits][:12])
    for r in refs[:2]:
        for l in sh4dis.dis(max(0, r - 0x60), 60, e): print(l[:60])

if __name__ == '__main__':
    main()
