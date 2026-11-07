# -*- coding: utf-8 -*-
"""짧은 칸 위험 목록과 빠진 한 글자 문자열(읽기 전용)."""
import sys, os, re, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, build as Bd, extract as X
from ko_audit import nbytes
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3])
master = {}
for l in open('work/text/master.tsv', encoding='utf-8'):
    if l[0] != '#': c = l.rstrip('\n').split('\t'); master[c[0]] = c
ko = {}
for fn in glob.glob('my files/번역/*.tsv'):
    for l in open(fn, encoding='utf-8'):
        if l[0] == '#' or not l.strip(): continue
        c = l.rstrip('\r\n').split('\t'); ko[c[0]] = c[5]
for l in open('work/text/fix_ko.tsv', encoding='utf-8'):
    if l[0] != '#': k, v = l.rstrip('\n').split('\t'); ko[k] = v
for k in sorted(master):
    if '03284' <= k <= '03298': print(k, master[k][2], master[k][4], '→', ko[k])
over = [(k, int(master[k][2]), nbytes(Bd.tidy(Bd.unesc(ko[k]))), master[k][4], ko[k]) for k in master if master[k][1] == 'M' and int(master[k][2]) <= 8 and nbytes(Bd.tidy(Bd.unesc(ko[k]))) > int(master[k][2])]
print('8 B 이하 초과', len(over))
for x in over: print(x)
ptr = collections.Counter()
for o in range(0, len(e) - 3, 4):
    v = struct.unpack_from('<I', e, o)[0]
    if X.B <= v < X.B + len(e): ptr[v - X.B] += 1
for m in re.finditer(b'\x91\xe6', e[0xB0000:0xF0000]):
    p = 0xB0000 + m.start()
    if e[p - 1] == 0: print(hex(p), ptr.get(p, 0), e[p:p + 14])
