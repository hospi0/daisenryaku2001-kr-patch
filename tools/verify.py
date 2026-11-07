# -*- coding: utf-8 -*-
"""빌드 결과 검산(읽기 전용): SCG 체크섬 전수, 바뀐 파일 수, 실행 파일 포인터가 문자열 시작을 가리키는지.  python tools/verify.py"""
import sys, os, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, scg_sum, extract as X
from gdi import Disc
from discwrite import TrackWriter
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
t3 = [t for t in D.tracks if t.num == 3][0]
r = TrackWriter(glob.glob('work/disc/*(Track 3).bin')[0], t3.start_lba, t3.skip)
old = D.read(*w['/1ST_READ.BIN'][1:3]); new = r.read_user(w['/1ST_READ.BIN'][1], 0, len(old))
T = scg_sum.table(new); ok = n = 0
for f, x in w.items():
    if f.startswith('/SCENARIO/'):
        d = r.read_user(x[1], 0, 0xE2D0); n += 1
        ok += scg_sum.crc(d[8:8 + scg_sum.SPAN], T) == struct.unpack_from('<I', d, 4)[0]
print('SCG 체크섬', ok, '/', n)
assert ok == n
# 포인터: 원본에서 M 문자열을 가리키던 자리의 새 값은 0 이 아닌 글자 시작이고 앞 바이트가 0 이어야 한다
rows, _ = X.exe_rows(old); starts = {o for k, o, b, t in rows}
bad = chg = tot = 0; diff_out = 0
for o in range(0, len(old) - 3, 4):
    v = struct.unpack_from('<I', old, o)[0]
    if v - X.B in starts:
        tot += 1; u = struct.unpack_from('<I', new, o)[0] - X.B
        if u != v - X.B: chg += 1
        if not (0 <= u < len(new)) or new[u] == 0 or new[u - 1] != 0: bad += 1
print('포인터', tot, '바뀜', chg, '이상', bad)
assert bad == 0
# 문자열 구역 밖 변경
lo, hi = 0xB0000, 0xF0000
out = [i for i in range(len(old)) if old[i] != new[i] and not lo <= i < hi and not 0x20EBFE <= i < 0x21D3FE]
print('글자 구역 밖 바뀐 바이트', len(out), [hex(x) for x in out[:6]])
ptrs = sum(1 for i in out if True)
chgf = []
for f, x in w.items():
    if x[2] > 1 << 26: continue
    if r.read_user(x[1], 0, x[2]) != D.read(x[1], x[2]): chgf.append(f)
r.f.close()
print('바뀐 파일(64MB 이하)', len(chgf), collections.Counter(f.split('/')[1] if f.count('/') > 1 else 'root' for f in chgf).most_common())
ps = set(o for o in range(0, len(old) - 3, 4) if struct.unpack_from('<I', old, o)[0] - X.B in starts)
stray = [i for i in out if (i & ~3) not in ps]
print('포인터 칸이 아닌 변경', len(stray), [hex(x) for x in stray[:8]])
