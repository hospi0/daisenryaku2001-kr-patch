# -*- coding: utf-8 -*-
"""UI 그림 글자 덩어리 좌표(읽기 전용). 투명 그림은 알파, 판 그림은 지정 격자.  python tools/ui_blocks.py
→ work/gfx/blocks/<이름>.png(번호 표시), work/gfx/blocks.tsv"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
N = 'DC2LUNITP0 DW2EVOP0 DW2SPECP0 DW2SPECP1 DW2SPECP3 GWL2STATP0 GWL2STATP1 GWL2STATP2 GX2MENUP1 MC2SELP1 SWND2P3'.split()
OUT = 'work/gfx/blocks'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    os.makedirs(OUT, exist_ok=True)
    tsv = open('work/gfx/blocks.tsv', 'w', encoding='utf-8', newline=chr(10))
    f = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 13)
    for n in N:
        im = Image.open('work/gfx/orig/%s.png' % n).convert('RGBA'); a = np.asarray(im)
        al = a[:, :, 3]; solid = (al > 40)
        print(n, im.size, '알파 값', np.unique(al)[:8], '투명 비율', round(float((al < 40).mean()), 2))
        m = cv2.dilate(solid.astype(np.uint8), np.ones((1, 7), np.uint8))
        c, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
        sl = [(st[i, 1], st[i, 1] + st[i, 3], st[i, 0], st[i, 0] + st[i, 2]) for i in range(1, c)]
        S = 4 if im.width <= 128 else 3
        big = im.resize((im.width * S, im.height * S), Image.NEAREST)
        pg = Image.new('RGB', big.size, (60, 90, 70)); pg.paste(big, (0, 0), big); d = ImageDraw.Draw(pg)
        for i, s in enumerate(sl):
            y0, y1, x0, x1 = [int(v) for v in s]
            if (y1 - y0) * (x1 - x0) < 24: continue
            d.rectangle((x0 * S, y0 * S, x1 * S - 1, y1 * S - 1), outline=(255, 60, 60))
            d.text((x0 * S + 2, y0 * S + 1), str(i), fill=(255, 255, 0), font=f, stroke_width=2, stroke_fill=(0, 0, 0))
            tsv.write('%s\t%d\t%d\t%d\t%d\t%d\n' % (n, i, x0, y0, x1, y1))
        pg.save(os.path.join(OUT, n + '.png'))


if __name__ == '__main__':
    main()
