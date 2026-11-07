# -*- coding: utf-8 -*-
"""딱딱한 명사형 어미 줄 전수(읽기 전용)."""
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
c = collections.Counter(); rows = collections.defaultdict(list)
for k, m in master.items():
    if m[1] != 'M': continue
    v = re.sub(r'[.!?…]+$', '', ko[k].replace('\l', ' ').strip())
    w = re.search(r'([가-힣]+)$', v)
    j = m[4]
    if w and re.search('(確認|注意|注目|だ|です?$|せよ|べし)[。！]?$', j) or (w and re.search('[가-힣](이다|다)$', v) and re.search('(だ|である)[。！]?$', j)):
        e = w.group(1)[-4:]; c[e] += 1; rows[e].append((k, j[-14:], v[-26:]))
print(sum(c.values()), c.most_common(40))
for e, n in c.most_common(14):
    print(e, n, rows[e][:3])
