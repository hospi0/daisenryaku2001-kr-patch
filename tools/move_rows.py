# -*- coding: utf-8 -*-
"""이동 방식 문구(읽기 전용)."""
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
for l in open('work/text/fix_ko.tsv', encoding='utf-8'):
    if l[0] != '#': k, v = l.rstrip('\n').split('\t'); ko[k] = v
for k in sorted(master):
    if '00545' <= k <= '00582':
        print(k, master[k][2], master[k][4], '→', ko[k], nbytes(Bd.tidy(Bd.unesc(ko[k]))))
print([(k, ko[k][:20]) for k in ko if '장궤' in ko[k] or '장륜' in ko[k]][:30])
