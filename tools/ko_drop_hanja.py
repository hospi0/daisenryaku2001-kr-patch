# -*- coding: utf-8 -*-
"""괄호 속 한자를 뺀 줄을 fix_ko.tsv 에 더한다(번역 원본은 안 건드림).  python tools/ko_drop_hanja.py"""
import glob, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ko = {}
for fn in glob.glob('my files/번역/*.tsv'):
    for l in open(fn, encoding='utf-8'):
        if l[0] == '#' or not l.strip(): continue
        c = l.rstrip('\r\n').split('\t'); ko[c[0]] = c[5]
fx = {}
lines = open('work/text/fix_ko.tsv', encoding='utf-8').read().split('\n')
for l in lines:
    if l and l[0] != '#':
        k, v = l.split('\t'); fx[k] = v
R = re.compile(r'[(（][^()（）]*[一-龥ぁ-ん][^()（）]*[)）]')
new = 0
for k in sorted(ko):
    v = fx.get(k, ko[k]); n = R.sub('', v)
    if n != v:
        print(k, v[:40], '→', n[:40]); fx[k] = n; new += 1
head = [l for l in lines if l and l[0] == '#']
open('work/text/fix_ko.tsv', 'w', encoding='utf-8', newline='\n').write('\n'.join(head + ['%s\t%s' % (k, fx[k]) for k in sorted(fx)]) + '\n')
print('고침', new, '남은 한자·가나 줄', [(k, fx.get(k, ko[k])[:24]) for k in sorted(ko) if re.search('[一-龥ぁ-んァ-ヶ]', fx.get(k, ko[k]))])
