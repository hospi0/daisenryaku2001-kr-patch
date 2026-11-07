# -*- coding: utf-8 -*-
"""글상자 문구 폭 측정(읽기 전용)."""
import sys, os, re, glob, collections
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
for l in open('work/text/fix_ko.tsv', encoding='utf-8'):
    if l[0] != '#': k, v = l.rstrip('\n').split('\t'); ko[k] = v
h = [k for k in ko if '이외는 고도' in ko[k]]
print(h, [(master[k][2], master[k][4], ko[k]) for k in h])
k0 = int(h[0])
for k in range(k0 - 6, k0 + 7):
    k = '%05d' % k; print(k, master[k][2], master[k][4][:40], '|', ko[k][:46])
# M 한 줄(줄바꿈 없음) 원문 길이 벼랑
c = collections.Counter(int(m[2]) for k, m in master.items() if m[1] == 'M' and '\l' not in m[4] and '\n' not in m[4])
print('한 줄 원문 길이 분포', sorted(c.items())[-30:])
L = [(nbytes(Bd.tidy(Bd.unesc(ko[k]))), int(m[2]), k) for k, m in master.items() if m[1] == 'M' and '\l' not in m[4] and '\n' not in m[4] and int(m[2]) >= 30]
for lim in (36, 38, 40, 44, 76): print('번역 ', lim, '초과', sum(1 for a, b, k in L if a > lim))
