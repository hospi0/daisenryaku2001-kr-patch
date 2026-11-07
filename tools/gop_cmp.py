# -*- coding: utf-8 -*-
"""원본과 시험 인코딩의 그림 순서 비교(읽기 전용)."""
import sys, os
src = open('tools/moviesub.py', encoding='utf-8').read().split('def main')[0]
exec(src.replace("__file__", repr(os.path.abspath('tools/moviesub.py'))))
sys.stdout.reconfigure(encoding='utf-8')
mv = sys.argv[1]
b = open('work/movie/%s.SFD' % mv, 'rb').read(); P = packets(b)
es = b''.join(b[p:e] for _, s, _, p, e in P if s == 0xE0)
he = open('work/movie/kr/_head.m1v', 'rb').read()
A = pictures(es); Bq = pictures(he); GA = gops(es); GB = gops(he)
a = [(t, r) for k, t, r in A]; c = [(t, r) for k, t, r in Bq]
print(len(a), len(c), 'GOP', len(GA), len(GB))
d = next((i for i in range(min(len(a), len(c))) if a[i] != c[i]), None); print('첫 차이', d)
if d is not None:
    print(' 원본', ''.join(' IPBD'[t] for t, r in a[max(0, d - 10):d + 30]), [r for t, r in a[max(0, d - 6):d + 8]])
    print(' 새것', ''.join(' IPBD'[t] for t, r in c[max(0, d - 10):d + 30]), [r for t, r in c[max(0, d - 6):d + 8]])
ca = [sum(1 for k, _, _ in A if k < g) for g in GA][:14]; cb = [sum(1 for k, _, _ in Bq if k < g) for g in GB][:14]; print(ca); print(cb)
print('마지막 원본 패턴', ''.join(' IPBD'[t] for t, r in a[-60:]))
