# -*- coding: utf-8 -*-
"""원문·번역 찾기(읽기 전용).  python tools/ko_find.py 낱말 …"""
import sys, glob
sys.stdout.reconfigure(encoding='utf-8')
ko = {}
for fn in glob.glob('my files/번역/*.tsv'):
    for l in open(fn, encoding='utf-8'):
        if l[0] == '#' or not l.strip(): continue
        c = l.rstrip('\r\n').split('\t'); ko[c[0]] = c
for l in open('work/text/fix_ko.tsv', encoding='utf-8'):
    if l[0] != '#':
        k, v = l.rstrip('\n').split('\t'); ko[k][5] = v
for w in sys.argv[1:]:
    h = [(c[0], c[1], c[2], c[4][:26], c[5][:26]) for c in ko.values() if (w == c[4] or w == c[5] or (len(w) > 1 and (w in c[4] or w in c[5]) and len(c[4]) < 12))]
    print(w, len(h), h[:9])
