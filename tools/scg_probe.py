# -*- coding: utf-8 -*-
"""SCG 문자열 배치·메뉴 라벨 출처·동영상 추출(읽기 전용).  python tools/scg_probe.py"""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
RE = re.compile(rb'(?:[\x81-\x9f\xe0-\xfc][\x40-\x7e\x80-\xfc]|[\x20-\x7e\x0a]){2,}')
JP = re.compile('[ぁ-んァ-ヶ一-龥]')

def strs(d):
    for m in RE.finditer(d):
        try: t = m.group(0).decode('cp932')
        except Exception: continue
        if JP.search(t): yield m.start(), len(m.group(0)), t

d = D.read(*w['/SCENARIO/000EXERC.SCG'][1:3])
v = list(strs(d)); print('줄', len(v))
for (o, n, t), nx in list(zip(v, v[1:] + [(len(d), 0, '')]))[:60]:
    print('%05X %3d 칸%4d %s' % (o, n, nx[0] - o, t[:30]))
print('...')
for o, n, t in v[-12:]: print('%05X %3d %s' % (o, n, t[:30]))
# 파일별 첫 문자열 위치 분포
c = collections.Counter(); sizes = collections.Counter()
for f, x in w.items():
    if f.startswith('/SCENARIO/'):
        q = D.read(x[1], x[2]); s = list(strs(q)); sizes[x[2] // 1000 * 1000] += 1
        c[len(s) // 20 * 20] += 1
print('줄 수 분포', sorted(c.items())); print('크기 분포', sorted(sizes.items())[:12])
e = D.read(*w['/1ST_READ.BIN'][1:3])
for t in ('作　戦', '作戦', '助　言', '雑　談', '情　勢', '難易度調整', 'ゲーム開始', '青軍司令部', '青軍', '生　産', '索敵', '移動'):
    print(t, e.count(t.encode('cp932')), end=' | ')
print()
E_ = [f for f in w if f.endswith('.SFD')]
os.makedirs('work/movie', exist_ok=True)
for f in E_:
    o = 'work/movie/' + f.split('/')[-1]
    if not os.path.exists(o):
        with open(o, 'wb') as h:
            lba, size = w[f][1], w[f][2]; p = 0
            while p < size:
                n = min(1 << 24, size - p); h.write(D.read(lba + p // 2048, n)); p += n
    print(f, os.path.getsize(o))
