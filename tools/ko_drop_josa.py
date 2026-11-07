# -*- coding: utf-8 -*-
"""괄호 조사(을(를) 등)를 없앤 줄을 fix_ko.tsv 에 더한다. 번역 원본은 안 건드림.  python tools/ko_drop_josa.py"""
import glob, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ko = {}
for fn in glob.glob('my files/번역/*.tsv'):
    for l in open(fn, encoding='utf-8'):
        if l[0] == '#' or not l.strip(): continue
        c = l.rstrip('\r\n').split('\t'); ko[c[0]] = c[5]
L = open('work/text/fix_ko.tsv', encoding='utf-8').read().split('\n')
head = [l for l in L if l and l[0] == '#']; fx = dict(l.split('\t', 1) for l in L if l and l[0] != '#')
J = re.compile(r'(?:은\(는\)|는\(은\)|이\(가\)|가\(이\)|을\(를\)|를\(을\)|과\(와\)|와\(과\)|\(으\)로|\(이\)|\(을\)|\(를\))')


def clean(v):
    def rp(m):
        e = m.end(); nx = v[e:e + 1]
        return '' if nx in (' ', '') else ' '          # 뒤에 띄어쓰기가 없으면 한 칸 둔다
    return J.sub(rp, v)


n = 0
for k in sorted(ko):
    v = fx.get(k, ko[k])
    if J.search(v):
        w = clean(v); print(k, v[:44], '→', w[:44]); fx[k] = w; n += 1
open('work/text/fix_ko.tsv', 'w', encoding='utf-8', newline='\n').write('\n'.join(head + ['%s\t%s' % (k, fx[k]) for k in sorted(fx)]) + '\n')
print('고침', n)
