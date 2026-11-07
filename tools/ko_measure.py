# -*- coding: utf-8 -*-
"""재배치 가능성 측정(읽기 전용).  python tools/ko_measure.py"""
import sys, os, re, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, extract as X, build as Bd
from ko_audit import nbytes, _ok
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3])
master = {}; pos = {}
for l in open('work/text/master.tsv', encoding='utf-8'):
    if l[0] != '#': c = l.rstrip('\n').split('\t'); master[c[0]] = c
for l in open('work/text/master_pos.tsv', encoding='utf-8'):
    c = l.rstrip('\n').split('\t'); pos[c[0]] = c[2].split()
ko = {}
for fn in glob.glob('my files/번역/*.tsv'):
    for l in open(fn, encoding='utf-8'):
        if l[0] == '#' or not l.strip(): continue
        c = l.rstrip('\r\n').split('\t'); ko[c[0]] = c[5]
bad = collections.Counter(ch for v in ko.values() for ch in Bd.tidy(Bd.unesc(v)) if not ('가' <= ch <= '힣') and ord(ch) >= 128 and not _ok(ch))
print('글꼴 밖 글자', bad.most_common(20))
# 포인터 전수(정렬 무관)
ptr = collections.defaultdict(list)
for o in range(0, len(e) - 3):
    if e[o + 3] == 0x8C:
        v = struct.unpack_from('<I', e, o)[0]
        if X.B <= v < X.B + len(e): ptr[v - X.B].append(o)
# 문자열 자리: 위치 → (길이, 번호)
slots = {}
for k, m in master.items():
    if m[1] != 'M': continue
    for p in pos[k]:
        slots[int(p, 16)] = (int(m[2]), k)
S = sorted(slots)
print('M 자리', len(S), '구역', hex(S[0]), hex(S[-1]))
# 칸 크기 = 다음 문자열까지(사이가 0 만일 때)
heap = 0; need = 0; over = 0; inner = 0; unal = 0; nptr = 0
for i, p in enumerate(S):
    L, k = slots[p]
    nx = S[i + 1] if i + 1 < len(S) else p + L + 1
    gap = e[p + L:nx]
    size = (nx - p) if not gap.strip(b'\0') else L + 1
    heap += size
    n = nbytes(Bd.tidy(Bd.unesc(ko[k]))) + 1
    need += n
    if n > L + 1: over += 1
    for q in range(p + 1, p + L):
        if q in ptr: inner += 1
    for o in ptr[p]:
        nptr += 1
        if o % 4: unal += 1
print('칸 합', heap, '번역 합(같은 글 중복 포함)', need, '넘침 자리', over, '문자열 속을 가리키는 포인터', inner, '포인터', nptr, '비정렬', unal)
uni = {}
for p in S: uni[slots[p][1]] = nbytes(Bd.tidy(Bd.unesc(ko[slots[p][1]]))) + 1
print('같은 글 합친 번역 합', sum(uni.values()))
# 짧은 줄 표본
sh = [(k, m[2], m[4], ko[k]) for k, m in master.items() if m[1] == 'M' and int(m[2]) <= 8]
print('8 B 이하', len(sh)); print(sh[:40])
c = collections.Counter(int(m[2]) for k, m in master.items() if m[1] == 'M' and nbytes(Bd.tidy(Bd.unesc(ko[k]))) > int(m[2])); print('초과 줄 예산 분포', sorted(c.items())[:24])
ov = collections.Counter(int(p, 16) >> 12 for k, m in master.items() if m[1] == 'M' and nbytes(Bd.tidy(Bd.unesc(ko[k]))) > int(m[2]) for p in pos[k]); print('초과 줄 위치', sorted((hex(a << 12), b) for a, b in ov.items())[:30])
# 군 이름 칸
lens = collections.Counter(); after = collections.Counter()
for f, x in w.items():
    if f.startswith('/SCENARIO/') and not f.endswith('MAPEDIT.SCG'):
        d = D.read(x[1], x[2])
        for kx in range(12):
            r = X.ARMY0 + kx * X.ARMYS
            if r >= X.NAME_AT: break
            t = d[r:r + 64].split(b'\0')[0]
            if not t: break
            lens[len(t)] += 1
print('군 이름 길이', sorted(lens.items())[-6:])
d = D.read(*w['/SCENARIO/26STLNGD.SCG'][1:3]); print(d[0x78:0x78 + 64].hex(' '))
for lim, kind in ((21, 'P'), (41, 'H'), (15, 'C'), (24, 'T')):
    ovr = [(k, m[4], ko[k]) for k, m in master.items() if m[1] == kind and nbytes(Bd.tidy(Bd.unesc(ko[k]))) > lim]
    fit = [x for x in ovr if nbytes(Bd.tidy(Bd.unesc(x[2])).replace(' ', '')) <= lim]
    print(kind, '초과', len(ovr), '공백 빼면 맞음', len(fit))
