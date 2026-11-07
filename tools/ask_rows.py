# -*- coding: utf-8 -*-
"""M 구역 한 줄 문장 중 38 B 를 넘는 줄(자동 줄바꿈으로 3째 줄로 떨어짐) 목록, 읽기 전용."""
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
    if k not in m or not k < '04000': continue
    s = Bd.tidy(Bd.unesc(ko[k])); o = m[k][4]
    if '\n' in o or '\l' in o or '\n' in s: continue
    b = nbytes(s)
    if b > 38 and int(m[k][2]) <= 38:
        n += 1; print(k, m[k][2], b, o, '→', ko[k])
print(n)
