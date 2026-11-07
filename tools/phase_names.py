# -*- coding: utf-8 -*-
"""前期·後期 이름의 전기형·후기형 바꿈 예산 표(읽기 전용)."""
import sys, os, glob, re
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
fit = over = 0; rest = []
for k in sorted(ko):
    if k not in m: continue
    o = m[k][4]; v = ko[k]
    if re.search('[前後]期$', o) and re.search('[전후]기$', v):
        n = nbytes(Bd.tidy(v)) + 2; b = int(m[k][2])
        if n <= b: fit += 1
        else: over += 1; print(k, b, n, o, '→', v + '형')
    elif '前期' in o or '後期' in o:
        rest.append((k, o[:30], v[:30]))
print('들어감', fit, '넘침', over, '끝이 아닌 곳', len(rest)); print(rest[:12])
mx = max(nbytes(Bd.tidy(ko[k])) for k in ko if k in m and '01300' <= k <= '02600' and m[k][1] == 'M')
print('이름 구역 최대 번역 길이', mx)
