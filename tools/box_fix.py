# -*- coding: utf-8 -*-
"""원문에 없는 줄바꿈이 든 M 줄 + 조사 괄호 줄 전수(읽기 전용).  python tools/box_fix.py"""
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
NL = chr(10)
more = [];
for k, m in master.items():
    if m[1] != 'M': continue
    j = Bd.unesc(m[4]); v = Bd.tidy(Bd.unesc(ko[k]))
    if v.count(NL) > j.count(NL): more.append((k, j.count(NL), v.count(NL), nbytes(v.replace(NL, ' ')), v.replace(NL, '/')[:60]))
print('원문보다 줄바꿈 많은 M', len(more), '원문 0줄', sum(1 for x in more if x[1] == 0))
print('줄바꿈 빼면 76 B 초과', [x for x in more if x[1] == 0 and x[3] > 76])
print(more[:6])
J = re.compile(r'(?:은\(는\)|는\(은\)|이\(가\)|가\(이\)|을\(를\)|를\(을\)|과\(와\)|와\(과\)|\(으\)로|\(이\)|\(을\)|\(를\))')
h = [(k, master[k][1], ko[k][:50]) for k in ko if J.search(ko[k])]
print('조사 괄호', len(h), collections.Counter(x for k in ko for x in J.findall(ko[k])).most_common())
for x in h[:40]: print(x)
