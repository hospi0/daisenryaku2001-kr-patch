# -*- coding: utf-8 -*-
"""고정 칸으로 잘라 쓰는 이어붙인 문자열 후보(읽기 전용)."""
import sys, os, re, glob
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
    if '00126' <= k <= '00136': print(k, master[k][2], master[k][4], '→', ko[k])
print('--- 후보: 원문에 띄어쓰기·문장부호·가나 조사 없이 12 B 이상')
for k, m in master.items():
    j = m[4]
    if m[1] == 'M' and int(m[2]) >= 12 and not re.search('[ぁ-ん、。 　%\\/()]', j) and len(j) % 2 == 0 and not re.search('[A-Za-z0-9ｦ-ﾟＡ-Ｚ０-９]', j) and re.fullmatch('[一-龥ァ-ヶー]+', j) and ' ' not in ko[k]:
        print(k, m[2], j, '→', ko[k])
for w in ('編成', 'サイズ', '積載', '牽引可', '搭載重量'):
    print(w, [(k, m[2], m[4][:24], ko[k][:24]) for k, m in master.items() if w in m[4] and len(m[4]) < 16][:6])
