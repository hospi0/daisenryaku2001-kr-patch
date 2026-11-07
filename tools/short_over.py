# -*- coding: utf-8 -*-
"""원문 8 B 이하인데 번역이 넘치는 짧은 칸 목록(읽기 전용)."""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as Bd
from ko_audit import nbytes
sys.stdout.reconfigure(encoding='utf-8')
m = {}
for l in open('work/text/master.tsv', encoding='utf-8'):
    if l[0] != '#': c = l.rstrip('\n').split('\t'); m[c[0]] = c
ko = {}
for fn in glob.glob('my files/번역/*.tsv'):
    for l in open(fn, encoding='utf-8'):
        if l[0] == '#' or not l.strip(): continue
        c = l.rstrip('\r\n').split('\t'); ko[c[0]] = c[5]
for l in open('work/text/fix_ko.tsv', encoding='utf-8'):
    if l[0] != '#': k, v = l.rstrip('\n').split('\t', 1); ko[k] = v
r = []
for k in sorted(ko):
    if k in m and k < '04000' and int(m[k][2]) <= 8:
        n = nbytes(Bd.tidy(Bd.unesc(ko[k])))
        if n > int(m[k][2]): r.append('%s %s→%d %s → %s' % (k, m[k][2], n, m[k][4], ko[k]))
print(len(r)); print('\n'.join(r))
