# -*- coding: utf-8 -*-
"""SCG 이름 구역 해독(읽기 전용): 배열 앞을 (개수 + [길이+일본어, 길이+영문]…) 로 해석.  python tools/scg_names.py"""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
from scg_audit2 import tail
sys.stdout.reconfigure(encoding='utf-8')

def walk(d, p, n, stop):
    """n 쌍을 읽고 끝 위치·목록"""
    out = []
    for i in range(n):
        v = []
        for k in range(2):
            if p >= stop: return None
            L = d[p]; p += 1
            if p + L > stop: return None
            v.append((p, L)); p += L
        out.append(v)
    return p, out

def find(d, a):
    """배열 시작 a 에 정확히 닿는 (위치, 개수, 쌍) — 뒤쪽 후보부터 여러 구역을 이어서 찾는다."""
    secs = []; stop = a
    while True:
        hit = None
        for p in range(stop - 2, max(0, stop - 30000), -1):
            n = struct.unpack_from('<H', d, p)[0]
            if not 1 <= n <= 3000: continue
            r = walk(d, p + 2, n, stop)
            if r and r[0] == stop:
                hit = (p, n, r[1]); break
        if not hit: break
        secs.insert(0, hit); stop = hit[0]
    return secs, stop

def main():
    D = Disc(1); ie.D = D
    w = {x[0]: x for x in ie.walk() if not x[3] & 2}
    tot = 0; uq = collections.Counter(); ns = collections.Counter(); bad = 0
    for f, x in sorted(w.items()):
        if not f.startswith('/SCENARIO/') or f.endswith('MAPEDIT.SCG'): continue
        d = D.read(x[1], x[2]); a = tail(d)[0]
        secs, st = find(d, a)
        ns[len(secs)] += 1
        if f.endswith(('000EXERC.SCG', '09DENMAR.SCG')):
            print(f, '배열', hex(a), '구역', [(hex(p), n) for p, n, _ in secs], '남은 앞', hex(st), d[st - 12:st].hex(' '))
            for p, n, v in secs:
                print('  ', [(d[q:q + l].decode('cp932', 'replace')) for pr in v[:3] for q, l in pr])
        for p, n, v in secs:
            for pr in v:
                t = d[pr[0][0]:pr[0][0] + pr[0][1]]; uq[t] += 1; tot += 1
    print('구역 수 분포', sorted(ns.items())); print('쌍', tot, '고유', len(uq))
    s = []; b = 0
    for k in uq:
        try: s.append(k.decode('cp932'))
        except Exception: b += 1
    print('복호 실패', b, '글자', sum(len(x) for x in s), '최대 바이트', max(len(k) for k in uq)); print(s[:30])

if __name__ == '__main__':
    main()
