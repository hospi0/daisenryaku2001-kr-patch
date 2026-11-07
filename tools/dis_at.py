# -*- coding: utf-8 -*-
"""python tools/dis_at.py 오프셋 개수 … (1ST_READ 파일 오프셋, 16진)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, sh4dis
from gdi import Disc
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3])
a = sys.argv[1:]
for i in range(0, len(a), 2):
    print('==', a[i])
    for l in sh4dis.dis(int(a[i], 16), int(a[i + 1]), e):
        if '0009  NOP' not in l: print(l[:56])
