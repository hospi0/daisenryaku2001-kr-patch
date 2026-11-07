# -*- coding: utf-8 -*-
"""PoC 시험 빌드: 글꼴 2수준 한자 칸에 한글을 넣고 화면 문구 5줄을 제자리로 바꾼다.
출력 work/disc/ (원본 롬은 읽기만).  python tools/poc_build.py"""
import sys, os, shutil, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, fontlib as F
from gdi import Disc, disc_dir
from discwrite import TrackWriter
import numpy as np
from PIL import Image, ImageDraw, ImageFont

TTF = 'C:/claude/utils/font/nanum-gothic/NanumGothicBold.ttf'
OUT = 'work/disc'
BASE = 0x5021                     # 2수준 한자 첫 구역(시험용)
# (원문, 번역) — 번역의 반각 공백·부호는 반각 경로 시험을 겸한다
LINES = [
    ('勝利条件を教えてください。', '승리 조건을 알려 주세요.'),
    ('空港を味方に使われてしまいます。', '공항을 아군이 쓰고 있습니다.'),
    ('どの項目を聞きたいですか？', '어느 항목을 듣고 싶습니까?'),
    ('難易度を調整しますか？', '난이도를 조정합니까?'),
    ('参謀に作戦行動案を立案させます', '참모에게 작전을 세우게 합니다'),
]

def cell_code(n):
    return ((BASE >> 8) + n // 94, 0x21 + n % 94)

def sjis(j1, j2):
    return bytes((j1 + 0x80, j2 + 0x80)).decode('euc_jp').encode('cp932')

def render(ch, font):
    S = 8
    im = Image.new('L', (18 * S, 18 * S), 0)
    ImageDraw.Draw(im).text((9 * S, 9 * S), ch, 255, font=font, anchor='mm')
    a = np.asarray(im.resize((18, 18), Image.BOX), float) / 255
    q = np.digitize(a, [0.2, 0.45, 0.7]).astype(np.uint8)
    p = np.zeros((18, 20), np.uint8); p[:, :18] = q
    return p

def pack(p):
    v = p.reshape(-1, 4)
    return (v[:, 0] << 6 | v[:, 1] << 4 | v[:, 2] << 2 | v[:, 3]).astype(np.uint8).tobytes()

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    D = Disc(1); ie.D = D
    w = {x[0]: x for x in ie.walk() if not x[3] & 2}
    fname = '/DPFONT/S18RM04P.DAT'
    font = bytearray(D.read(*w[fname][1:3])); exe = bytearray(D.read(*w['/1ST_READ.BIN'][1:3]))
    ko = sorted({c for s, t in LINES for c in t if '가' <= c <= '힣'}); print('한글', len(ko))
    tf = ImageFont.truetype(TTF, 17 * 8)
    cmap = {}
    for n, c in enumerate(ko):
        j1, j2 = cell_code(n); i = (j1 - 0x21) * 94 + (j2 - 0x21)
        g = pack(render(c, tf)); assert len(g) == F.CELL
        font[i * F.CELL:(i + 1) * F.CELL] = g; cmap[c] = sjis(j1, j2)
    assert (F.dec(bytes(font), (cell_code(0)[0] - 0x21) * 94)[:, 18:] == 0).all()
    for s, t in LINES:
        b = s.encode('cp932'); hits = []
        p = exe.find(b)
        while p >= 0:
            hits.append(p); p = exe.find(b, p + 1)
        n = b''.join(cmap[c] if c in cmap else c.encode('ascii') for c in t)
        print(s, [hex(h) for h in hits], '앞뒤', [(exe[h - 1], exe[h + len(b)]) for h in hits], len(n), '/', len(b))
        assert len(n) <= len(b), t
        for h in hits:
            assert exe[h - 1] == 0 and exe[h + len(b)] == 0, '문자열 일부 ' + s
            exe[h:h + len(b)] = n + b'\0' * (len(b) - len(n))
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(disc_dir(1), '*.*')):
        o = os.path.join(OUT, os.path.basename(f))
        print('복사', os.path.basename(f)); shutil.copyfile(f, o)
    t3 = [t for t in D.tracks if t.num == 3][0]
    tw = TrackWriter(glob.glob(OUT + '/*(Track 3).bin')[0], t3.start_lba, t3.skip)
    tw.write_user(w[fname][1], 0, bytes(font)); tw.write_user(w['/1ST_READ.BIN'][1], 0, bytes(exe))
    print('섹터 고침', tw.close())
    # 검산: 새 트랙에서 다시 읽어 기대값 비교
    r = TrackWriter(glob.glob(OUT + '/*(Track 3).bin')[0], t3.start_lba, t3.skip)
    assert r.read_user(w[fname][1], 0, len(font)) == bytes(font)
    assert r.read_user(w['/1ST_READ.BIN'][1], 0, len(exe)) == bytes(exe)
    r.f.close(); print('다시 읽기 일치')
    pg = Image.new('L', (22 * 24, 22 * ((len(ko) + 23) // 24)), 60)
    for k, c in enumerate(ko):
        j1, j2 = cell_code(k); a = F.dec(bytes(font), (j1 - 0x21) * 94 + j2 - 0x21)
        pg.paste(Image.fromarray((a * 85).astype(np.uint8)), ((k % 24) * 22 + 1, (k // 24) * 22 + 1))
    pg.resize((pg.width * 2, pg.height * 2), 0).save('work/poc_glyphs.png')

if __name__ == '__main__':
    main()
