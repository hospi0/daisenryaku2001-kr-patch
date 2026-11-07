# -*- coding: utf-8 -*-
"""공용 어미가 붙는 문장 끝 검토(읽기 전용)."""
import sys, os, re, glob, collections
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
for k in sorted(master):
    if '03228' <= k <= '03250': print(k, master[k][4][:30], '→', ko[k][:40])
print('--- 조언 문장(03840~03960)·행동(02855~02885) 끝 낱말')
c = collections.Counter(); ex = {}
for k in sorted(master):
    if '03840' <= k <= '03960' or '02855' <= k <= '02885':
        v = re.sub(r'[.!?…]+$', '', ko[k].replace(chr(92) + 'l', ' ').strip()); e = v.split(' ')[-1][-5:]
        c[e] += 1; ex.setdefault(e, (k, master[k][4][-12:], v[-24:]))
print(c.most_common(60))
for e, x in ex.items():
    if e not in ('주의', '확인', '주목'): print(e, x)
