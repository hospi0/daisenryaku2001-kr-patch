# -*- coding: utf-8 -*-
"""크래시 스테이트: 한글 블록 위치, 길이 표(읽기 전용)."""
import sys, os, re, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, rzip
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3])
for fn in sys.argv[1:]:
    s = rzip.unrzip(open(fn, 'rb').read()); rb = s.find(e[0x1000:0x1100]) - 0x1000 - 0x10000; ram = s[rb:rb + 0x1000000]
    print(fn, '길이 표', ram[0x3B1914:0x3B1914 + 40].hex(' '))
    h = 0xD30240
    print(' 버퍼 끝쪽', ram[h + 0xF2CA + 0x46:h + 0xF2CA + 0x46 + 16].hex(' '))
    sig = bytes.fromhex('98 b1 98 c0')[:0]
    # 시험 브리핑 첫 줄의 한글 코드열을 버퍼에서 뽑아 메모리 전수 검색
    s0 = h + 0xF2CA + 0x46 + 40
    key = ram[s0:s0 + 12]; print(' 키', key.hex(' '))
    print(' 위치', [hex(0x8C000000 + m.start()) for m in re.finditer(re.escape(key), ram)][:8])
    q = ram.find('難易度'.encode('cp932')); print(' 일본어 難易度', hex(q))
