# -*- coding: utf-8 -*-
"""원문이 2줄인 짧은 M 중 한 줄이라도 넘치는 번역(읽기 전용)."""
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
n = 0
for k in sorted(ko):
    if k not in m or m[k][1] != 'M' or m[k][4].count('\l') != 1 or int(m[k][2]) > 90: continue
    ls = ko[k].split('\l')
    b = [nbytes(Bd.tidy(x)) for x in ls]
    if max(b) > 36 or len(ls) != 2:
        n += 1; print(k, m[k][2], b, m[k][4], '→', ko[k])
print(n)
