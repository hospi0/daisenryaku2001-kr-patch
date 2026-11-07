# -*- coding: utf-8 -*-
"""SCG 이름 구역: 쌍(길이+일본어, 길이+영문)을 따라가 배열에 닿는 가장 이른 시작.  python tools/scg_names2.py"""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
from scg_audit2 import tail
sys.stdout.reconfigure(encoding='utf-8')

def okjp(b):
    try: t = b.decode('cp932')
    except Exception: return False
    return all(ord(c) >= 0x20 for c in t)

def oken(b):
    return all(0x20 <= c < 0x7f for c in b)

def chain(d, stop):
    """stop 까지 이어지는 시작점 집합을 뒤에서부터 동적으로 계산 → 가장 이른 시작, 쌍 수"""
    good = {stop: 0, stop - 1: 0} if d[stop - 1] == 0 else {stop: 0}
    lo = max(0, stop - 40000)
    for p in range(stop - 2, lo, -1):
        L = d[p]
        if p + 1 + L >= stop or not okjp(d[p + 1:p + 1 + L]): continue
        q = p + 1 + L; M = d[q]
        if not oken(d[q + 1:q + 1 + M]): continue
        r = q + 1 + M
        if r in good: good[p] = good[r] + 1
    return good

def main():
    D = Disc(1); ie.D = D
    w = {x[0]: x for x in ie.walk() if not x[3] & 2}
    heads = collections.Counter(); uq = {}; tot = 0; res = []; cnt_match = 0
    for f, x in sorted(w.items()):
        if not f.startswith('/SCENARIO/') or f.endswith('MAPEDIT.SCG'): continue
        d = D.read(x[1], x[2]); a = tail(d)[0]
        g = chain(d, a)
        p = max(g, key=lambda k: (g[k], -k)); n = g[p]
        h = d[p - 6:p]
        res.append((f.split('/')[-1], hex(a), hex(p), n, h.hex(' ')))
        if struct.unpack_from('<H', d, p - 2)[0] == n: cnt_match += 1
        if d[p - 1] == n & 255: heads['u8'] += 1
        q = p
        for i in range(n):
            L = d[q]; t = d[q + 1:q + 1 + L]; q += 1 + L; M = d[q]; e = d[q + 1:q + 1 + M]; q += 1 + M
            uq.setdefault(t.decode('cp932'), e.decode('ascii')); tot += 1
    for r in res[:10] + res[-6:]: print(r)
    print('개수 일치 u16', cnt_match, 'u8', heads['u8'], '/', len(res))
    print('쌍', tot, '고유', len(uq), '글자', sum(len(k) for k in uq), '최대', max(len(k.encode('cp932')) for k in uq))
    print('영문 빈 칸', sum(1 for v in uq.values() if not v))
    print(list(uq.items())[:14]); print(list(uq.items())[-8:])
    jp = [k for k in uq if re.search('[ぁ-んァ-ヶ一-龥]', k)]; print('일본어 포함', len(jp), '글자', sum(len(k) for k in jp))

if __name__ == '__main__':
    main()
