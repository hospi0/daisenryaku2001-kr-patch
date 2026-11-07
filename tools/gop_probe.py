# -*- coding: utf-8 -*-
"""SFD 그림 종류·GOP 구조·타임스탬프 규칙 측정(읽기 전용)."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'moviesub.py'), encoding='utf-8').read().split('def main')[0]
exec(src.replace("__file__", repr(os.path.abspath('tools/moviesub.py'))))
sys.stdout.reconfigure(encoding='utf-8')
for mv in sys.argv[1:]:
    b = open('work/movie/%s.SFD' % mv, 'rb').read(); P = packets(b)
    es = b''.join(b[p:e] for _, s, _, p, e in P if s == 0xE0)
    G = gops(es); pics = pictures(es)
    seq = ''.join(' IPBD'[t] for k, t, r in pics[:52])
    cnt = [sum(1 for k, _, _ in pics if k < g) for g in G]
    print(mv, 'GOP', len(G), '그림', len(pics), 'ES', len(es), seq)
    print(' 시간참조', [r for k, t, r in pics[:30]])
    print(' GOP 간격', collections.Counter(b2 - a for a, b2 in zip(cnt, cnt[1:])).most_common(4))
    for per in (3003, 3000):
        print(' per', per, check_rule(b, P, es, per))
    from_ = [(hex(b[st]) ) for i, s, st, p, e in P[:0]]
    tw = ts_walk(b, P)[:6]; print(' 패킷', [(pos, kind, get_ts(b, q) if kind else None) for pos, q, kind, ln in tw])
    pics2, gs = gop_first(es, len(es)); starts = [k for k, _, _ in pics2]
    import bisect as bs
    n = 0; rows = []
    for pos, q, kind, ln in ts_walk(b, P):
        if kind not in (0x20, 0x30): continue
        j = bs.bisect_left(starts, pos)
        hit = j < len(pics2) and starts[j] < pos + ln
        pts = get_ts(b, q); dts = get_ts(b, q + 5) if kind == 0x30 else None
        rows.append((j, hit, pics2[j][1] if hit else 0, gs[j] + pics2[j][2] if hit else 0, pts, dts))
    print(' 표시번호·PTS', [(j, h, t, d, p, dd) for j, h, t, d, p, dd in rows[:14]])
    c = collections.Counter(); c2 = collections.Counter()
    for j, h, t, d, p, dd in rows:
        if h:
            c[p - d * 3003] += 1
            if dd is not None: c2[dd - j * 3003] += 1
    print(' PTS-표시*3003', c.most_common(5), 'DTS-j*3003', c2.most_common(5), '찍힌', len(rows), '그림 시작 없음', sum(1 for r in rows if not r[1]))
    print(' 뒤쪽', [(j, t, d, p, dd, round(p / d, 3) if d else 0) for j, h, t, d, p, dd in rows[40:400:45]])
    c = collections.Counter(p - d * 3006 for j, h, t, d, p, dd in rows if h); print(' p-d*3006', c.most_common(8))
    c = collections.Counter(dd - j * 3006 for j, h, t, d, p, dd in rows if h and dd is not None); print(' dts-j*3006', c.most_common(8))
    dl = [b2[4] - a2[4] for a2, b2 in zip(rows, rows[1:]) if b2[3] - a2[3] == 1]; print(' 인접 표시 PTS 차', collections.Counter(dl).most_common(6))
