# -*- coding: utf-8 -*-
"""추가 추출(읽기 전용): 정렬 무관 포인터가 가리키는 일본어 문자열 중 master 에 없는 것.
python tools/extract_extra.py          측정만
python tools/extract_extra.py --write  work/text/master_x.tsv + my files/tsv/dai_042.tsv"""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, extract as X
from gdi import Disc

BAD = lambda t: any((ord(c) < 0x20 and c not in '\r\n\t') or 0x7f <= ord(c) < 0xa0 or 0xe000 <= ord(c) <= 0xf8ff for c in t)

def rows(e):
    ptr = collections.Counter(); src = collections.defaultdict(list)
    for o in range(0, len(e) - 3):
        if e[o + 3] != 0x8C: continue
        v = struct.unpack_from('<I', e, o)[0]
        if X.B <= v < X.B + len(e):
            ptr[v - X.B] += 1; src[v - X.B].append(o)
    known = {o for k, o, b, t in X.exe_rows(e)[0]}
    nw, a, z = X.news_rows(e)
    out = []
    for p, n in ptr.items():
        if p in known or a <= p < z or e[p - 1] != 0 or e[p] == 0: continue
        q = e.find(b'\0', p); b = e[p:q]
        if len(b) < 2 or len(b) > 600: continue
        try: t = b.decode('cp932')
        except Exception: continue
        if BAD(t) or not X.JP.search(t): continue
        out.append(('X', p, len(b), t, n, src[p][0]))
    return sorted(out, key=lambda r: r[1])

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    D = Disc(1); ie.D = D
    w = {x[0]: x for x in ie.walk() if not x[3] & 2}
    e = D.read(*w['/1ST_READ.BIN'][1:3])
    r = rows(e)
    print('후보', len(r), '고유', len({x[3] for x in r}), '글자', sum(len(t) for t in {x[3] for x in r}))
    print('구역', sorted(collections.Counter(x[1] >> 12 for x in r).items())[:40])
    for x in r[:: max(1, len(r) // 40)]: print(hex(x[1]), x[2], x[4], hex(x[5]), x[3][:34].replace('\n', '|').replace('\r', ''))
    if '--write' in sys.argv:
        uni = collections.OrderedDict()
        for k, p, n, t, c, s in r:
            v = uni.setdefault(t, [n, 0, []]); v[1] += 1; v[2].append(p)
        n0 = sum(1 for l in open('work/text/master.tsv', encoding='utf-8') if l[0] != '#')
        head = '#번호\t구분\t예산\t쓰임\tJP\tKO\n'
        with open('work/text/master_x.tsv', 'w', encoding='utf-8', newline=chr(10)) as f, open(os.path.join(X.OUT, 'dai_042.tsv'), 'w', encoding='utf-8', newline=chr(10)) as g:
            f.write(head); g.write(head)
            for i, (t, v) in enumerate(uni.items(), n0 + 1):
                l = '%05d\tX\t%d\t%d\t%s\t\n' % (i, v[0], v[1], X.esc(t)); f.write(l); g.write(l)
        print('dai_042', len(uni), '줄', os.path.getsize(os.path.join(X.OUT, 'dai_042.tsv')))

if __name__ == '__main__':
    main()
