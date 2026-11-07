# -*- coding: utf-8 -*-
r"""빌더. 원본 → 글꼴·1ST_READ·SCG 적용 → work/disc/ (원본 롬은 읽기만).
  python tools/build.py              예행(디스크 안 씀)
  python tools/build.py --write      work/disc/ 에 씀
  --test work/ko_test.tsv            시험 표(구분 \t JP \t KO)만 쓰고, 한글을 2수준 한자 칸에 넣는다
번역 입력 = work/ko/*.tsv (dai_NNN.tsv 형식: 번호 구분 예산 쓰임 JP KO). KO 빈 줄은 원문 유지.
쓰는 순간 검사: 바이트 예산, 서식(%d 등) 개수, 글꼴에 없는 글자 → 하나라도 있으면 빌드 안 함."""
import sys, os, re, glob, shutil, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, fontlib as F, extract as X
from gdi import Disc, disc_dir, USER
from scg_audit2 import tail
import scg_sum
from discwrite import TrackWriter
import numpy as np
from PIL import Image, ImageDraw, ImageFont

TTF = 'C:/claude/utils/font/nanum-gothic/NanumGothicBold.ttf'
OUT = 'work/disc'
FONT = '/DPFONT/S18RM04P.DAT'
EXE = '/1ST_READ.BIN'
WIDTH = 44                                   # SCG 문장 한 줄 = 전각 22칸
PUNCT = r"""[,.!?:;)\]}'"~，．！？：；）］｝’”～、。…]"""
FMT = re.compile(r'%[-+0 #]*\d*(?:\.\d+)?[a-zA-Z%]')


def unesc(t):
    out = []; i = 0
    while i < len(t):
        if t[i] == '\\' and i + 1 < len(t):
            c = t[i + 1]; out.append({'n': '\r\n', 'l': '\n', 'r': '\r', 't': '\t', '\\': '\\'}.get(c, '\\' + c)); i += 2
        else:
            out.append(t[i]); i += 1
    return ''.join(out)


def tidy(t):
    t = t.replace('·', '・').replace('–', '－').replace('—', '―')     # 글꼴에 있는 부호로
    t = re.sub(r'\.{3,}|…+', '…', t)                       # 한국식 말줄임표 한 칸
    return re.sub('(' + PUNCT + ')[ 　]+', r'\1', t)        # 문장부호 뒤 공백은 빌더가 지운다


def load(test):
    """(구분, 원문) → 번역"""
    tr = {}; err = []
    if test:
        for l in open(test, encoding='utf-8'):
            c = l.rstrip('\n').split('\t')
            if len(c) == 3 and c[0][0] != '#': tr[(c[0], unesc(c[1]))] = tidy(unesc(c[2]))
        return tr, err
    master = {}
    for l in open('work/text/master.tsv', encoding='utf-8'):
        c = l.rstrip('\n').split('\t')
        if l[0] != '#': master[c[0]] = c
    for fn in sorted(glob.glob(os.path.join('my files', '번역', '*.tsv'))):
        for l in open(fn, encoding='utf-8'):
            c = l.rstrip('\r\n').split('\t')
            if l[0] == '#' or len(c) < 6 or not c[5]: continue
            m = master.get(c[0])
            if not m or m[4] != c[4]:
                err.append('%s %s 원문이 추출표와 다름' % (os.path.basename(fn), c[0])); continue
            tr[(m[1], unesc(m[4]))] = tidy(unesc(c[5]))
    for l in open('work/text/fix_ko.tsv', encoding='utf-8'):
        if l[0] == '#': continue
        k, v = l.rstrip('\n').split('\t'); m = master[k]
        tr[(m[1], unesc(m[4]))] = tidy(unesc(v))
    # 원문이 한 줄인 M 은 게임이 칸 폭으로 알아서 접는다(2줄 상자). 번역의 줄바꿈은 3번째 줄로 밀려 사라지므로 공백으로
    for (k, jp), v in list(tr.items()):
        if k == 'M' and '\n' not in jp and '\n' in v:
            tr[(k, jp)] = v.replace('\r\n', ' ').replace('\n', ' ')
    return tr, err


def check(tr, bud, err):
    for (k, jp), ko in tr.items():
        if sorted(FMT.findall(jp)) != sorted(FMT.findall(ko)):
            err.append('서식 다름 [%s] %s → %s' % (k, jp[:24], ko[:24]))


def render(ch, font):
    S = 8
    im = Image.new('L', (18 * S, 18 * S), 0)
    ImageDraw.Draw(im).text((9 * S, 9 * S), ch, 255, font=font, anchor='mm')
    a = np.asarray(im.resize((18, 18), Image.BOX), float) / 255
    p = np.zeros((18, 20), np.uint8); p[:, :18] = np.digitize(a, [0.2, 0.45, 0.7])
    return p


def pack(p):
    v = p.reshape(-1, 4)
    return (v[:, 0] << 6 | v[:, 1] << 4 | v[:, 2] << 2 | v[:, 3]).astype(np.uint8).tobytes()


def make_font(font, ko, base, keep=()):
    tf = ImageFont.truetype(TTF, 17 * 8); cmap = {}
    j1, j2 = base >> 8, base & 255
    for c in ko:
        while (j1, j2) in keep:
            j2 += 1
            if j2 > 0x7E: j1, j2 = j1 + 1, 0x21
        i = (j1 - 0x21) * 94 + (j2 - 0x21)
        font[i * F.CELL:(i + 1) * F.CELL] = pack(render(c, tf))
        cmap[c] = bytes((j1 + 0x80, j2 + 0x80)).decode('euc_jp').encode('cp932')
        j2 += 1
        if j2 > 0x7E: j1, j2 = j1 + 1, 0x21
        assert j1 <= 0x74, '글꼴 칸 부족'
    p = np.zeros((18, 20), np.uint8)                       # … = 바닥선 점 셋
    for x in (2, 8, 14): p[14:16, x:x + 2] = 3
    i = F.idx('…'); font[i * F.CELL:(i + 1) * F.CELL] = pack(p)
    return cmap


def enc(t, cmap):
    out = bytearray()
    for c in t:
        if c in cmap: out += cmap[c]
        else:
            b = c.encode('cp932')                          # 없으면 예외 = 빌드 실패
            out += b
    return bytes(out)


def wrap(t, cmap):
    """문단을 44 B 줄로. 띄어쓰기 자리에서만 끊고, 낱말이 44 B 를 넘을 때만 쪼갠다."""
    lines = []
    for para in t.split('\r\n'):
        cur = b''
        for w in re.split('( )', para):
            b = enc(w, cmap)
            if len(cur) + len(b) > WIDTH:
                if w == ' ': lines.append(cur); cur = b''; continue
                if cur.strip(): lines.append(cur.rstrip()); cur = b''
                while len(b) > WIDTH:
                    k = WIDTH
                    if len(b[:k].decode('cp932', 'ignore').encode('cp932')) != k: k -= 1
                    lines.append(b[:k]); b = b[k:]
            cur += b
        lines.append(cur)
    return b'\r\n'.join(lines)


def scg(d, tr, cmap, st):
    """새 SCG 바이트. 번역이 없으면 원본과 바이트까지 같아야 한다."""
    a, ls, s, _ = tail(d)
    out = bytearray(d[:X.NAME_AT - 3])
    tt = d[8:0x78].split(b'\0')[0]
    if tt:
        ko = tr.get(('T', tt.decode('cp932')))
        if ko is not None:
            b = enc(ko, cmap)                    # 제목 칸 = 0x08~0x20(24 B + 끝 0), 0x21 부터 다른 값
            if len(b) > 24: raise SystemExit('제목 예산 초과: %s %d/24' % (ko, len(b)))
            out[8:0x21] = b + b'\0' * (0x19 - len(b)); st['T'] += 1
    for k in range(12):
        r = X.ARMY0 + k * X.ARMYS
        if r >= X.NAME_AT: break
        t = d[r:r + 40].split(b'\0')[0]
        if not t: break
        try: ko = tr.get(('A', t.decode('cp932')))
        except UnicodeDecodeError: ko = None
        if ko is not None:
            b = enc(ko, cmap)
            if len(b) > 23: raise SystemExit('군 이름 예산 초과: %s %d/23' % (ko, len(b)))        # 칸 뒤 +32 까지 0(원본 최대 20)
            out[r:r + max(len(t), len(b) + 1)] = b + b'\0' * (max(len(t), len(b) + 1) - len(b)); st['A'] += 1
    n = d[X.NAME_AT - 1]; q = X.NAME_AT; body = bytearray([n])
    for i in range(n):
        L = d[q]; t = d[q + 1:q + 1 + L]; q += 1 + L; M = d[q]; e = d[q + 1:q + 1 + M]; q += 1 + M
        ko = tr.get(('P', t.decode('cp932')))
        if ko is not None:
            t = enc(ko, cmap); st['P'] += 1      # 게임이 24 B 칸의 +2 에 복사(0x8C0132FE) → 21 B + 끝 0
            if len(t) > 21: raise SystemExit('이름 예산 초과: %s %d/21' % (ko, len(t)))
        body += bytes([len(t)]) + t + bytes([M]) + e
    out += struct.pack('<H', len(body)) + body
    if len(out) & 1: out.append(d[q] if len(out) == q else 0)
    assert s - a == 40
    slots = list(struct.unpack_from('<20H', d, a)); o = s; blocks = []
    for i, L in enumerate(slots):
        if not L: continue
        raw = d[o:o + L]; o += L
        ko = tr.get(('S', X.para(raw)))
        if ko is not None:
            raw = wrap(ko, cmap); st['S'] += 1
            assert len(raw) < 65536
        slots[i] = len(raw); blocks.append(raw)
    assert o == len(d)
    out += struct.pack('<20H', *slots)
    for b in blocks: out += b
    struct.pack_into('<I', out, 4, scg_sum.crc(bytes(out[8:8 + scg_sum.SPAN]), CRC_T))   # 게임이 적재 때 검사(오류 0x19)
    return bytes(out)


def relocate(exe, rows, tr, cmap, err):
    """번역이 제자리에 들어가면 그대로, 넘치면 빈 자리로 옮기고 정렬된 포인터를 전부 고친다.
    빈 자리 = 옮긴 문자열의 원래 칸 + 줄어든 문자열의 남은 칸(4 B 정렬 범위만, 0 구역은 안 씀)."""
    B = X.B; ptr = collections.defaultdict(list)
    for o in range(0, len(exe) - 3, 4):
        v = struct.unpack_from('<I', exe, o)[0]
        if B <= v < B + len(exe): ptr[v - B].append(o)
    free = []; todo = []
    for k, o, bud, t in rows:
        L = bud; end = (o + L + 1 + 3) & ~3
        v = tr.get((k, t))
        if v is None: continue
        b = enc(v, cmap) + b'\0'
        if len(b) <= L + 1:
            exe[o:o + L + 1] = b + b'\0' * (L + 1 - len(b))
            q = (o + len(b) + 3) & ~3
            if q < end: free.append((q, end))
        else:
            exe[o:end] = b'\0' * (end - o); free.append((o, end)); todo.append((o, b, v))
    free.sort(); mg = []
    for a, b in free:
        if mg and a <= mg[-1][1]: mg[-1][1] = max(mg[-1][1], b)
        else: mg.append([a, b])
    print('빈 자리', sum(b - a for a, b in mg), '조각', len(mg), '옮길 양', sum(len(x[1]) for x in todo))
    for o, b, v in sorted(todo, key=lambda x: -len(x[1])):
        need = (len(b) + 3) & ~3; best = None
        for f in mg:
            if f[1] - f[0] >= need and (best is None or f[1] - f[0] < best[1] - best[0]): best = f
        if best is None:
            err.append('옮길 자리 없음 %d %s' % (len(b), v[:20])); continue
        q = best[0]; best[0] += need
        exe[q:q + len(b)] = b
        if not ptr[o]: err.append('포인터 없음 %X %s' % (o, v[:20]))
        for r in ptr[o]: struct.pack_into('<I', exe, r, B + q)
    return len(todo), mg


BIOS_OFS_FN = 0x8C30C914      # (r4=4, r5=SJIS) → BIOS 글꼴 오프셋. 0x8C015220 이 24×24 1bpp 를 읽을 때 부른다
BIOS_LIT = 0x52E8             # 그 함수 주소 리터럴(파일 위치)
BIOS_KANJI0 = 0xE190          # JIS 0x3021 오프셋 = 0xE190 + 칸 번호 × 72 (0x8C30CAF6 실측)
FONT_VAR = 0x8C6B37D0         # S18 글꼴 주소 변수
TBL_CELL = (0x42 - 0x21) * 94 # 24×24 표를 둘 자리: 번역 뒤 안 쓰는 한자 칸(S18 파일 안)


def bios_table(font, ko):
    """한글 칸 순서대로 24×24 1bpp(72 B) 를 안 쓰는 글꼴 칸 자리에 쓴다."""
    f = ImageFont.truetype(TTF, 22); o = TBL_CELL * F.CELL
    for n, c in enumerate(ko):
        im = Image.new('1', (24, 24), 0); d = ImageDraw.Draw(im); d.fontmode = '1'
        d.text((12, 12), c, 1, font=f, anchor='mm')
        a = np.asarray(im, np.uint8)
        font[o + n * 72:o + n * 72 + 72] = np.packbits(a, axis=1).tobytes()
    assert o + len(ko) * 72 <= len(font)
    return o


def bios_hook(exe, font, ko, free, err):
    """전투 3D 이름표는 BIOS 글꼴을 쓴다. 오프셋 함수 호출만 작은 함수로 돌려 한글 칸이면 표를 읽게 한다.
    반환값 r0 만 바뀌고 호출부는 r11(BIOS 시작)+r0 으로 읽으므로 r0 = 표 주소 − r11."""
    if struct.unpack_from('<I', exe, BIOS_LIT)[0] != BIOS_OFS_FN:
        err.append('BIOS 리터럴 다름'); return
    T = bios_table(font, ko)
    w = [0x4F22, 0xD009, 0x400B, 0x0009, 0x4F26, 0xD108, 0x6203, 0x3218, 0xD107, 0x3212, 0x8906, 0xD107,
         0x6112, 0xD307, 0x313C, 0x312C, 0x31B8, 0x6013, 0x000B, 0x0009]
    code = b''.join(struct.pack('<H', x) for x in w) + struct.pack('<5I', BIOS_OFS_FN, BIOS_KANJI0, len(ko) * 72, FONT_VAR, T)
    assert len(code) == 60
    best = next((f for f in free if f[1] - f[0] >= 64 and f[0] % 4 == 0), None)
    if best is None: err.append('훅 자리 없음'); return
    q = best[0]; exe[q:q + 60] = code
    struct.pack_into('<I', exe, BIOS_LIT, X.B + q)
    print('BIOS 훅', hex(X.B + q), '표', hex(T), '글자', len(ko))


def dir_entry(D, path):
    """ISO 디렉터리 레코드의 (섹터 LBA, 섹터 안 위치)"""
    pvd = D.read(ie.PVD_LBA, USER)
    lba = struct.unpack_from('<I', pvd, 158)[0]; size = struct.unpack_from('<I', pvd, 166)[0]
    parts = path.strip('/').split('/')
    for pi, name in enumerate(parts):
        hit = None
        for s in range((size + USER - 1) // USER):
            sec = D.read(lba + s, USER); i = 0
            while i < USER and sec[i]:
                ln = sec[i]; nm = sec[i + 33:i + 33 + sec[i + 32]].split(b';')[0].decode('ascii', 'replace')
                if nm.upper() == name.upper(): hit = (lba + s, i, sec); break
                i += ln
            if hit: break
        assert hit, path
        ls, off, sec = hit
        lba = struct.unpack_from('<I', sec, off + 2)[0]; size = struct.unpack_from('<I', sec, off + 10)[0]
    return ls, off


def gfx_files(D, w, err):
    """승인된 그림 → (디스크 경로, 새 바이트). 원본과 형식·크기가 다르면 빌드 안 함."""
    out = {}
    items = [('/SCENE/SCENE%02d.PVR' % i, 'work/gfx/scene_new/SCENE%02d.pvrnew' % i) for i in range(29)]
    items += [('/%s.PVR' % n, 'work/gfx/ui_new/%s.pvrnew' % n) for n in
              'LOGOMSG DC2LUNITP0 DW2EVOP0 DW2SPECP0 DW2SPECP1 DW2SPECP3 GWL2STATP0 GWL2STATP1 GWL2STATP2 GX2MENUP1 MC2SELP1 SWND2P3'.split()]
    for f, src in items:
        o = D.read(*w[f][1:3]); n = open(src, 'rb').read()
        a, b = o.find(b'PVRT'), n.find(b'PVRT')
        new = o[:a] + n[b:]
        if o[a + 8:a + 10] != n[b + 8:b + 10] or o[a + 12:a + 16] != n[b + 12:b + 16]:
            err.append('그림 형식 다름 %s %s %s' % (f, o[a + 8:a + 16].hex(), n[b + 8:b + 16].hex()))
        if len(new) != len(o): err.append('그림 크기 다름 %s %d %d' % (f, len(new), len(o)))
        out[f] = new
    return out


def movie_files(w, err):
    out = {}
    for fn in glob.glob('work/movie/kr/*.SFD'):
        f = '/MOVIE/' + os.path.basename(fn)
        if os.path.getsize(fn) != w[f][2]: err.append('동영상 크기 다름 ' + f)
        out[f] = fn
    return out


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    test = sys.argv[sys.argv.index('--test') + 1] if '--test' in sys.argv else None
    D = Disc(1); ie.D = D
    w = {x[0]: x for x in ie.walk() if not x[3] & 2}
    tr, err = load(test); check(tr, None, err)
    print('번역', len(tr), collections.Counter(k for k, _ in tr).most_common())
    font = bytearray(D.read(*w[FONT][1:3])); exe = bytearray(D.read(*w[EXE][1:3]))
    global CRC_T
    CRC_T = scg_sum.table(bytes(exe))
    freq = collections.Counter(c for v in tr.values() for c in v if '가' <= c <= '힣')
    ko = [c for c, _ in freq.most_common()]
    ko += [c for c in '새시나리오제국' if c not in ko]
    keep = set()
    for v in tr.values():
        for c in v:
            if not ('가' <= c <= '힣') and ord(c) >= 0x3000:
                try: b = c.encode('euc_jp')
                except UnicodeEncodeError: continue
                if len(b) == 2 and b[0] >= 0xB0: keep.add((b[0] - 0x80, b[1] - 0x80))
    print('번역에 남은 한자 칸', len(keep))
    cmap = make_font(font, ko, 0x5021 if test else 0x3021, keep)
    print('한글', len(ko), '자')
    # 1ST_READ 제자리
    m, _ = X.exe_rows(bytes(exe)); nw, _, _ = X.news_rows(bytes(exe)); n = 0
    moved, free = relocate(exe, m, tr, cmap, err)
    if not test: bios_hook(exe, font, ko, free, err)
    for k, o, bud, t in nw:
        v = tr.get((k, t))
        if v is None: continue
        b = enc(v, cmap)
        if len(b) > bud:
            err.append('예산 초과 [%s] %d/%d %s' % (k, len(b), bud, v[:24])); continue
        exe[o:o + bud] = b + b'\0' * (bud - len(b)); n += 1
    n += len(m); print('옮긴 문자열', moved)
    print('실행 파일 자리', n)
    # SCG
    st = collections.Counter(); new = {}
    for f, x in sorted(w.items()):
        if not f.startswith('/SCENARIO/') or f.endswith('MAPEDIT.SCG'): continue
        d = D.read(x[1], x[2]); b = scg(d, tr, cmap, st)
        if b != d: new[f] = b
        else: st['같음'] += 1
    # MAPEDIT.SCG: 문장 구역이 없고 제목과 기본 나라 이름만 있다
    x = w['/SCENARIO/MAPEDIT.SCG']; d = bytearray(D.read(x[1], x[2]))
    if not test:
        t = d[8:0x21].split(b'\0')[0]; print('MAPEDIT 제목', t.decode('cp932'))
        b = enc('새 시나리오', cmap); d[8:0x21] = b + b'\0' * (0x19 - len(b)); k = 0
        while X.ARMY0 + k * X.ARMYS < X.NAME_AT:
            r = X.ARMY0 + k * X.ARMYS; t = bytes(d[r:r + 24]).split(b'\0')[0]
            if not t: break
            u = t.decode('cp932'); assert u[0] == '第' and u[-1] == '国', u
            b = enc('제' + u[1:-1] + '국', cmap); assert len(b) <= len(t), u
            d[r:r + len(t)] = b + b'\0' * (len(t) - len(b)); k += 1
        print('MAPEDIT 나라', k)
        struct.pack_into('<I', d, 4, scg_sum.crc(bytes(d[8:8 + scg_sum.SPAN]), CRC_T)); new['/SCENARIO/MAPEDIT.SCG'] = bytes(d)
    print('SCG', st.most_common(), '바뀐 파일', len(new))
    grow = []
    for f, b in new.items():
        x = w[f]; cap = (x[2] + USER - 1) // USER * USER
        if len(b) > cap: err.append('섹터 여유 초과 %s %d > %d' % (f, len(b), cap))
        if len(b) != x[2]: grow.append((f.split('/')[-1], x[2], len(b)))
    print('크기 바뀜', grow[:8])
    gfx = gfx_files(D, w, err); mov = movie_files(w, err)
    print('그림', len(gfx), '동영상', len(mov))
    for e in err[:40]: print('⛔', e)
    if err: raise SystemExit('오류 %d — 빌드 안 함' % len(err))
    if '--write' not in sys.argv:
        print('예행 끝(디스크 안 씀)'); return
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(disc_dir(1), '*.*')):
        o = os.path.join(OUT, os.path.basename(f))
        if '(Track 3)' in f or not os.path.exists(o): shutil.copyfile(f, o)
    t3 = [t for t in D.tracks if t.num == 3][0]
    path = glob.glob(OUT + '/*(Track 3).bin')[0]
    tw = TrackWriter(path, t3.start_lba, t3.skip)
    tw.write_user(w[FONT][1], 0, bytes(font)); tw.write_user(w[EXE][1], 0, bytes(exe))
    for f, b in new.items():
        x = w[f]; cap = (x[2] + USER - 1) // USER * USER
        tw.write_user(x[1], 0, b + b'\0' * (cap - len(b)))
        if len(b) != x[2]:
            ls, off = dir_entry(D, f)
            tw.write_user(ls, off + 10, struct.pack('<I', len(b)) + struct.pack('>I', len(b)))
    for f, b in gfx.items(): tw.write_user(w[f][1], 0, b)
    for f, fn in mov.items():
        tw.write_user(w[f][1], 0, open(fn, 'rb').read()); print('동영상', f, flush=True)
    print('섹터 고침', tw.close())
    r = TrackWriter(path, t3.start_lba, t3.skip)
    assert r.read_user(w[FONT][1], 0, len(font)) == bytes(font) and r.read_user(w[EXE][1], 0, len(exe)) == bytes(exe)
    for f, b in list(new.items()) + list(gfx.items()): assert r.read_user(w[f][1], 0, len(b)) == b
    for f, fn in mov.items(): assert r.read_user(w[f][1], 0, w[f][2]) == open(fn, 'rb').read()
    r.f.close(); print('다시 읽기 일치')


if __name__ == '__main__':
    main()
