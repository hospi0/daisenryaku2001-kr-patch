# -*- coding: utf-8 -*-
"""한글 글꼴 렌더 방식 비교(읽기 전용, 2비트 4단계로 게임과 같게).  python tools/font_cmp.py → work/gfx/font_cmp.png"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import bdf
sys.stdout.reconfigure(encoding='utf-8')
NB = 'C:/claude/utils/font/nanum-gothic/NanumGothicBold.ttf'
NR = 'C:/claude/utils/font/nanum-gothic/NanumGothic.ttf'
T = '군굳곤곧근귿제1군사령부전투공격기수도'


def cur(ch):
    f = ImageFont.truetype(NB, 17 * 8); S = 8
    im = Image.new('L', (18 * S, 18 * S), 0); ImageDraw.Draw(im).text((9 * S, 9 * S), ch, 255, font=f, anchor='mm')
    a = np.asarray(im.resize((18, 18), Image.BOX), float) / 255
    return np.digitize(a, [0.2, 0.45, 0.7])


def direct(path, size, mono):
    def g(ch):
        f = ImageFont.truetype(path, size)
        im = Image.new('1' if mono else 'L', (18, 18), 0); d = ImageDraw.Draw(im)
        if mono: d.fontmode = '1'
        d.text((9, 9), ch, 1 if mono else 255, font=f, anchor='mm')
        a = np.asarray(im, float)
        if mono: return (a > 0) * 3
        return np.digitize(a / 255, [0.2, 0.45, 0.7])
    return g


_f = bdf.Font('C:/claude/utils/font/Galmuri-v2.40.3/Galmuri14.bdf')


def gal(ch):
    pts, dw = _f.draw(ch); a = np.zeros((24, 24), int)
    for x, y in pts:
        if 0 <= y < 24 and 0 <= x < 24: a[y, x] = 3
    ys, xs = np.nonzero(a); a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    o = np.zeros((18, 18), int); y = (18 - a.shape[0]) // 2; x = (18 - a.shape[1]) // 2; o[y:y + a.shape[0], x:x + a.shape[1]] = a
    return o


M = [('A 지금(나눔고딕 볼드 축소)', cur), ('B 볼드 17 직접', direct(NB, 17, False)), ('C 볼드 16 직접', direct(NB, 16, False)), ('D 볼드 17 1비트', direct(NB, 17, True)),
     ('E 볼드 16 1비트', direct(NB, 16, True)), ('F 보통 17 직접', direct(NR, 17, False)), ('G 갈무리14 화소', gal)]
S = 3; W = len(T) * 19 * S + 240
pg = Image.new('RGB', (W, len(M) * (18 * S + 10) + 6), (200, 210, 205)); d = ImageDraw.Draw(pg); lab = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 13)
for r, (n, g) in enumerate(M):
    y = r * (18 * S + 10) + 6; d.text((4, y + 16), n, (0, 0, 0), font=lab)
    for i, c in enumerate(T):
        a = g(c); col = (np.array([205, 215, 210])[None, None] * (1 - a[..., None] / 3) + np.array([10, 10, 10])[None, None] * (a[..., None] / 3)).astype(np.uint8)
        pg.paste(Image.fromarray(col).resize((18 * S, 18 * S), 0), (230 + i * 19 * S, y))
pg.save('work/gfx/font_cmp.png'); print(pg.size)
