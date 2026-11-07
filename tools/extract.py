# -*- coding: utf-8 -*-
r"""전체 번역 원문 추출(읽기 전용). → work/text/master.tsv + my files/tsv/dai_NNN.tsv(18 KB 단위)
구분: M=1ST_READ 문자열 · C=사건 표 나라 · H=사건 표 본문 · S=SCG 문장 블록 · P=SCG 이름 · T=SCG 제목 · A=SCG 군 이름
같은 원문은 한 줄로 합치고 쓰인 곳 수를 적는다. S 는 전각 22칸으로 끊긴 줄을 이어 문단으로 보여 준다.
python tools/extract.py"""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
from scg_audit2 import tail

B = 0x8C010000
SPLIT = 18 * 1024
OUT = os.path.join('my files', 'tsv')
JP = re.compile('[ぁ-んァ-ヶ一-龥々ｦ-ﾟ]')
CLEAN = re.compile(r'^[ぁ-んァ-ヶ一-龥々ｦ-ﾟ、。！？「」『』（）()・…―－ー〜～　０-９Ａ-Ｚａ-ｚ\x20-\x7e\r\n\t％×＋／：＜＞→←↑↓○●◎△▲▽▼□■☆★※〇，．]+$')
NAME_AT = 0xF2CB
ARMY0, ARMYS = 0x78, 0x144C


def esc(t):
    return t.replace('\\', '\\\\').replace('\r\n', '\\n').replace('\n', '\\l').replace('\r', '\\r').replace('\t', '\\t')


def exe_rows(e):
    ptr = collections.Counter()
    for o in range(0, len(e) - 3, 4):
        v = struct.unpack_from('<I', e, o)[0]
        if B <= v < B + len(e): ptr[v - B] += 1
    lo, hi = 0xB0000, 0xF0000
    rows = []; drop = []
    for m in re.finditer(rb'[^\x00]+', e[lo:hi]):
        b = m.group(0); o = lo + m.start()
        try: t = b.decode('cp932')
        except Exception: continue
        if not JP.search(t): continue
        if any((ord(c) < 0x20 and c not in '\r\n\t') or 0x7f <= ord(c) < 0xa0 or 0xe000 <= ord(c) <= 0xf8ff for c in t):
            drop.append((o, t)); continue
        if not ptr.get(o):
            drop.append((o, t)); continue
        rows.append(('M', o, len(b), t))
    return rows, drop


def news_rows(e):
    p = e.find('抗日救国'.encode('cp932'))
    while e[p - 1]: p -= 1
    r0 = p - 22                                  # 머리 6 + 나라 16 앞

    def valid(r):
        if r < 0 or r + 64 > len(e): return False
        if e[r + 5] != 0 or not 0x10 <= e[r + 4] <= 0x70: return False     # 앞 2 B 는 FF FF 또는 00 00
        if not (1 <= e[r + 2] <= 31 and 1 <= e[r + 3] <= 12): return False
        try:
            c = e[r + 6:r + 22].split(b'\0')[0].decode('cp932'); t = e[r + 22:r + 64].split(b'\0')[0].decode('cp932')
        except Exception: return False
        return bool(t)
    assert valid(r0), hex(r0)
    a = r0
    while valid(a - 64): a -= 64
    z = r0
    while valid(z + 64): z += 64
    rows = []
    for r in range(a, z + 64, 64):
        c = e[r + 6:r + 22].split(b'\0')[0].decode('cp932'); t = e[r + 22:r + 64].split(b'\0')[0].decode('cp932')
        if c: rows.append(('C', r + 6, 15, c))
        rows.append(('H', r + 22, 41, t))
    return rows, a, z + 64


def para(b):
    """전각 22칸(44 B) 으로 꽉 찬 줄은 다음 줄에 이어 붙이고, 짧은 줄 끝의 줄바꿈만 남긴다."""
    ls = b.split(b'\r\n'); out = ''
    for i, l in enumerate(ls):
        out += l.decode('cp932')
        if i < len(ls) - 1 and len(l) < 43: out += '\r\n'
    return out


def scg_rows(D, w):
    rows = []; left = collections.Counter(); ex = []
    for f, x in sorted(w.items()):
        if not f.startswith('/SCENARIO/') or f.endswith('MAPEDIT.SCG'): continue
        n = f.split('/')[-1]; d = D.read(x[1], x[2]); a, ls, s, e_ = tail(d)
        cov = bytearray(len(d))
        o = s
        for i, L in enumerate(ls):
            if L:
                rows.append(('S', (n, i), 0, para(d[o:o + L]))); o += L
        q = NAME_AT; size = struct.unpack_from('<H', d, NAME_AT - 3)[0]     # 크기는 개수 바이트부터, 끝은 짝수로 맞춤
        for i in range(d[NAME_AT - 1]):
            L = d[q]; t = d[q + 1:q + 1 + L]; q += 1 + L; M = d[q]; q += 1 + M
            u = t.decode('cp932')
            if JP.search(u): rows.append(('P', (n, i), 0, u))
        assert q == NAME_AT - 1 + size and ((q + 1) & ~1) == a, f
        tt = d[8:0x78].split(b'\0')[0]
        if tt:
            u = tt.decode('cp932', 'replace'); cov[8:8 + len(tt)] = b'\1' * len(tt)
            rows.append(('T', (n, 0), 0x6F, u))
        for k in range(12):
            r = ARMY0 + k * ARMYS
            if r >= NAME_AT: break
            t = d[r:r + 40].split(b'\0')[0]
            if not t: break                      # 첫 빈 칸 뒤는 군 칸이 아니라 지도 자료
            cov[r:r + len(t) + 24] = b'\1' * (len(t) + 24)     # 이름 뒤 칸의 옛 찌꺼기는 화면에 안 나온다
            try: rows.append(('A', (n, k), len(t), t.decode('cp932')))
            except Exception: left['복호 실패 군 이름'] += 1
        for m in re.finditer(rb'(?:[\x81-\x9f\xe0-\xfc][\x40-\x7e\x80-\xfc]){2,}', d[0x78:NAME_AT - 3]):
            st = 0x78 + m.start()
            if any(cov[st:st + 2]): continue
            try: u = m.group(0).decode('cp932')
            except Exception: continue
            if len(JP.findall(u)) >= 2:
                left[n] += 1
                if len(ex) < 30: ex.append((n, hex(st), hex(st % ARMYS), u[:20]))
    return rows, left, ex


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    D = Disc(1); ie.D = D
    w = {x[0]: x for x in ie.walk() if not x[3] & 2}
    e = D.read(*w['/1ST_READ.BIN'][1:3])
    m, drop = exe_rows(e); nw, na, nz = news_rows(e); sc, left, ex = scg_rows(D, w)
    print('M', len(m), '버림', len(drop), '사건 표', hex(na), hex(nz), (nz - na) // 64, '건')
    print('버린 표본', [t[:18] for o, t in drop[:: max(1, len(drop) // 16)]][:16])
    print('SCG 고정 구역 남은 일본어', sum(left.values()), left.most_common(5)); print(ex[:14])
    # 같은 원문 합치기: (구분군, 원문) → 쓰임
    uni = collections.OrderedDict()
    for k, pos, bud, t in m + nw + sc:
        g = (k, t); v = uni.setdefault(g, [0, 0, []]); v[0] += 1; v[1] = max(v[1], bud) if not v[1] else min(v[1], bud); v[2].append(pos)
    c = collections.Counter(); ch = collections.Counter()
    for (k, t), v in uni.items(): c[k] += 1; ch[k] += len(t)
    print('구분별 고유', c.most_common(), '글자', ch.most_common(), '합', sum(ch.values()))
    os.makedirs('work/text', exist_ok=True); os.makedirs(OUT, exist_ok=True)
    head = '#번호\t구분\t예산\t쓰임\tJP\tKO\n'
    lines = []
    for i, ((k, t), v) in enumerate(uni.items(), 1):
        lines.append('%05d\t%s\t%d\t%d\t%s\t\n' % (i, k, v[1], v[0], esc(t)))
    with open('work/text/master.tsv', 'w', encoding='utf-8', newline=chr(10)) as f:
        f.write(head); f.writelines(lines)
    with open('work/text/master_pos.tsv', 'w', encoding='utf-8', newline=chr(10)) as f:
        for i, ((k, t), v) in enumerate(uni.items(), 1):
            f.write('%05d\t%s\t%s\n' % (i, k, ' '.join(('%X' % p) if isinstance(p, int) else '%s:%d' % p for p in v[2])))
    for fn in os.listdir(OUT):
        if fn.startswith('dai_'): os.remove(os.path.join(OUT, fn))
    chunks = []; cur = []; size = len(head.encode('utf-8'))
    for l in lines:
        n = len(l.encode('utf-8'))
        if size + n > SPLIT and cur:
            chunks.append(cur); cur = []; size = len(head.encode('utf-8'))
        cur.append(l); size += n
    if cur: chunks.append(cur)
    for i, ck in enumerate(chunks, 1):
        with open(os.path.join(OUT, 'dai_%03d.tsv' % i), 'w', encoding='utf-8', newline=chr(10)) as f:
            f.write(head); f.writelines(ck)
    # 번호 연속 검산
    got = []
    for i in range(1, len(chunks) + 1):
        for l in open(os.path.join(OUT, 'dai_%03d.tsv' % i), encoding='utf-8'):
            if l[0] != '#': got.append(int(l[:5]))
    assert got == list(range(1, len(lines) + 1)), '번호 어긋남'
    print('TSV', len(chunks), '개 · 줄', len(lines), '최대', max(os.path.getsize(os.path.join(OUT, 'dai_%03d.tsv' % i)) for i in range(1, len(chunks) + 1)))


if __name__ == '__main__':
    main()
