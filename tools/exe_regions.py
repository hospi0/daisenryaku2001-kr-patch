# -*- coding: utf-8 -*-
"""무참조 문자열 구역 판독(읽기 전용).  python tools/exe_regions.py"""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3])
rows = []
for l in open('work/text/exe_scan.tsv', encoding='utf-8'):
    c = l.rstrip('\n').split('\t')
    if c[0][0] != '#' and len(c) >= 4: rows.append((int(c[0], 16), int(c[1]), int(c[2]), c[3]))
good = re.compile(r'^[ぁ-んァ-ヶ一-龥々ー、。！？「」『』（）・…―－　0-9A-Za-z０-９Ａ-Ｚ%\ .,:/\-]+$')
un = [r for r in rows if not r[2] and good.match(r[3]) and len(r[3]) >= 6 and re.search('[ぁ-ん一-龥]', r[3])]
c = collections.Counter(r[0] >> 16 for r in un); print('깨끗한 무참조', len(un), sorted((hex(k << 16), v) for k, v in c.items()))
for t in ('王党派カグラール団', '中国で', '抗日救国'):
    b = t.encode('cp932'); p = e.find(b); print(t, hex(p))
    if p > 0:
        s = e[p - 64:p + 96]; print(' ', s.hex(' ')[:200]); print(' ', s.decode('cp932', 'replace').replace('\0', '·').replace('\r', '|')[:80])
for k in (0x100000, 0x130000, 0x210000, 0x260000, 0x2b0000):
    print(hex(k), [r[3][:18] for r in un if r[0] >> 16 == k >> 16][:10])
s = open('work/state11.bin', 'rb').read()
