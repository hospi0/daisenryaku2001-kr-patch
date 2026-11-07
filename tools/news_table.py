# -*- coding: utf-8 -*-
"""역사 사건 표 구조 측정(읽기 전용).  python tools/news_table.py"""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3])
p = e.find('抗日救国'.encode('cp932'))
s = p
while e[s - 1]: s -= 1
print('본문 시작', hex(s))
# 나라 칸 앞뒤로 간격 측정: 표 안 문장 시작 위치들
rows = [int(l.split('\t')[0], 16) for l in open('work/text/exe_scan.tsv', encoding='utf-8') if l[0] != '#' and 0x200000 <= int(l.split('\t')[0], 16) < 0x230000]
g = collections.Counter(b - a for a, b in zip(rows, rows[1:])); print('간격', g.most_common(10))
print(e[s - 28:s + 90].hex(' '))
for pos in (s - 0x60, s, s + 0x60):
    print(hex(pos), e[pos:pos + 0x60].decode('cp932', 'replace').replace('\0', '·')[:60])
