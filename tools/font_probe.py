# -*- coding: utf-8 -*-
"""글꼴 후보 조사(읽기 전용). BIOS 글꼴 벡터·큰 비트맵·파일 이름.  python tools/font_probe.py"""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    D = Disc(1); ie.D = D
    w = {x[0]: x for x in ie.walk() if not x[3] & 2}
    e = D.read(*w['/1ST_READ.BIN'][1:3])
    for v in (0x8C0000B4, 0xAC0000B4, 0x8C0000B0, 0xAC0000B0, 0x8C0000BC, 0x8C0000C0):
        print(hex(v), len(re.findall(re.escape(struct.pack('<I', v)), e)))
    # 파일 크기 큰 순(그림·동영상·모델·지도 제외)
    r = [(s, f) for f, (n, l, s, fl) in w.items() if not f.endswith(('.SFD', '.NJ', '.NJM', '.PVM', '.MPB', '.MLT')) and '/REAL' not in f]
    for s, f in sorted(r, reverse=True)[:30]: print(s, f)
    c = collections.Counter(f.rsplit('/', 1)[0] for f in w); print(c.most_common(20))
    print([f for f in w if re.search(r'FONT|FNT|KANJI|MOJI|CHAR|TEXT|MSG|STR', f.split('/')[-1])][:40])
    s = re.findall(rb'[\x20-\x7e]{5,}', e)
    print([x.decode() for x in s if re.search(rb'(?i)font|\.fon|\.pvr|kanji|\.txb|\.osb|\.mrg|\.dat|\.bin', x)][:60])

if __name__ == '__main__':
    main()
