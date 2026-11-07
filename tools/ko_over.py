# -*- coding: utf-8 -*-
"""고정 칸 초과 목록(읽기 전용) → work/text/over.tsv"""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as Bd
from ko_audit import nbytes
sys.stdout.reconfigure(encoding='utf-8')
master = {}
for l in open('work/text/master.tsv', encoding='utf-8'):
    if l[0] != '#': c = l.rstrip('\n').split('\t'); master[c[0]] = c
ko = {}
for fn in glob.glob('my files/번역/*.tsv'):
    for l in open(fn, encoding='utf-8'):
        if l[0] == '#' or not l.strip(): continue
        c = l.rstrip('\r\n').split('\t'); ko[c[0]] = c[5]
LIM = {'P': 21, 'H': 41, 'C': 15, 'A': 23, 'T': 24}
o = open('work/text/over.tsv', 'w', encoding='utf-8', newline=chr(10)); n = {}
for k, m in master.items():
    if m[1] in LIM:
        b = nbytes(Bd.tidy(Bd.unesc(ko[k])))
        if b > LIM[m[1]]:
            n[m[1]] = n.get(m[1], 0) + 1; o.write('%s\t%s\t%d/%d\t%s\t%s\n' % (k, m[1], b, LIM[m[1]], m[4], ko[k]))
print(n)
