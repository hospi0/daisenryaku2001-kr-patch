# -*- coding: utf-8 -*-
"""SCG 끝 구역 전수 검사 2: 문장 시작 = 마지막 0 바이트 다음.  python tools/scg_audit2.py"""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
RE = re.compile(rb'(?:[\x81-\x9f\xe0-\xfc][\x40-\x7e\x80-\xfc]|[\x20-\x7e\x0d\x0a]){2,}')
JP = re.compile('[ぁ-んァ-ヶ一-龥]')

def tail(d):
    n = len(d); s = d.rfind(b'\0') + 1; want = n - s
    for end in range(s - 2, max(0, s - 400), -1):        # 배열 끝 위치 후보(0 채움 포함)
        acc = 0; ls = []; p = end
        while p > s - 900 and acc < want:
            v = struct.unpack_from('<H', d, p)[0]
            ls.insert(0, v); acc += v; p -= 2
        if acc == want and ls and ls[-1] and ls[0]:
            return p + 2, ls, s, end + 2
    return None

def main():
    D = Disc(1); ie.D = D
    w = {x[0]: x for x in ie.walk() if not x[3] & 2}
    ok = 0; bad = []; nb = collections.Counter(); slots = collections.Counter(); uq = set(); tot = 0; uo = set(); no = 0; ex = []; lens = collections.Counter(); ws = collections.Counter()
    for f, x in sorted(w.items()):
        if not f.startswith('/SCENARIO/'): continue
        d = D.read(x[1], x[2]); t = tail(d)
        if not t: bad.append((f, len(d), len(d) - d.rfind(b'\0') - 1)); continue
        ok += 1; a, ls, s, e = t; nb[sum(1 for v in ls if v)] += 1; slots[s - a] += 1
        o = s
        for L in ls:
            if L:
                b = d[o:o + L]; tx = b.decode('cp932', 'replace'); uq.add(tx); tot += len(tx); o += L
                for l in b.split(b'\r\n'): lens[len(l)] += 1
        for m in RE.finditer(d[:a]):
            try: u = m.group(0).decode('cp932')
            except Exception: continue
            if len(JP.findall(u)) >= 2: no += 1; uo.add(u.strip())
    print('구조 맞음', ok, '안 맞음', len(bad), bad[:8])
    print('블록 수', sorted(nb.items())); print('배열 시작~문장', slots.most_common(6))
    print('블록 글자', tot, '고유 블록', len(uq), '고유 글자', sum(len(x) for x in uq))
    print('줄 길이 최대', max(lens), sorted(lens.items())[-5:])
    print('구역 밖 일본어 줄', no, '고유', len(uo), '글자', sum(len(x) for x in uo))
    print(sorted(uo, key=len)[-14:]); print(sorted(uo)[:14])

if __name__ == '__main__':
    main()
