# -*- coding: utf-8 -*-
"""초기 분량·글꼴 조사(읽기 전용). python tools/survey.py"""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
RE = re.compile(rb'(?:[\x81-\x9f\xe0-\xfc][\x40-\x7e\x80-\xfc]|[\x20-\x7e]){3,}')

def strs(d):
    out = []
    for m in RE.finditer(d):
        b = m.group(0)
        try: t = b.decode('cp932')
        except Exception: continue
        j = len(re.findall('[ぁ-んァ-ヶ一-龥]', t))
        if j >= 2: out.append((m.start(), t))
    return out

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    D = Disc(1); ie.D = D
    w = {x[0]: x for x in ie.walk() if not x[3] & 2}
    tot = collections.Counter(); uniq = collections.defaultdict(set)
    allchars = set()
    for f, (n, l, s, fl) in sorted(w.items()):
        if f.endswith(('.SFD', '.PVR', '.PVM', '.NJ', '.NJM', '.MLT', '.MPB')): continue
        d = D.read(l, s); v = strs(d)
        if not v: continue
        e = f.rsplit('.', 1)[-1] if '.' in f else ''; k = f if e == 'BIN' else e
        tot[k] += len(v); uniq[k] |= {t for o, t in v}
        for o, t in v: allchars |= set(re.findall('[一-龥ぁ-んァ-ヶ]', t))
    for k, c in tot.most_common(14):
        print(k, '문자열', c, '고유', len(uniq[k]), '글자수', sum(len(x) for x in uniq[k]))
    print('글자 종류', len(allchars))
    u = set().union(*uniq.values()); print('전체 고유', len(u), '글자수', sum(len(x) for x in u))
    v = strs(D.read(*w['/SCENARIO/000EXERC.SCG'][1:3])); print([t[:40] for o, t in v[:14]])
    for f in ('/ALL.FOB', '/ALL.FPB'):
        n, l, s, fl = w[f]; d = D.read(l, s); print(f, s, d[:32].hex(' '))
    print([f for f in w if re.search(r'FONT|FON|\.FOB|\.FPB|\.OSB|\.MSB|\.TXB|\.DAT$', f)][:40])
    d1 = D.read(*w['/1ST_READ.BIN'][1:3]); d2 = D.read(*w['/2_DP.BIN'][1:3]); print('1ST', len(d1), '2_DP', len(d2), sum(a == b for a, b in zip(d1[:400000], d2[:400000])))
    print(D.read(45000, 256)[:96])

if __name__ == '__main__':
    main()
