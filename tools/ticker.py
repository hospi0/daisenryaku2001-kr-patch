# -*- coding: utf-8 -*-
"""흐르는 자막 띠 이어 붙이기(읽기 전용). → work/movie/ticker/<영상>_NN.png + segs.tsv + 읽기용 페이지
python tools/ticker.py [영상 …]"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
FF = r'C:\claude\utils\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe'
MOV = ['CAMPAIGN0', 'ENDINGFAIL', 'ENDINGUSAWIN', 'ENDINGUSAFAIL', 'ENDINGEUROPEEWIN', 'ENDINGEUROPEFAIL', 'ENDINGEUROPEWWIN']
Y0, H, FPS = 192, 34, 30
TH = 175
OUT = 'work/movie/ticker'


def frames(name):
    p = subprocess.run([FF, '-v', 'error', '-i', 'work/movie/%s.SFD' % name, '-vf', 'fps=%d,crop=320:%d:0:%d,format=gray' % (FPS, H, Y0), '-f', 'rawvideo', '-'], capture_output=True)
    return np.frombuffer(p.stdout, np.uint8).reshape(-1, H, 320)


def speed(fr):
    """구간 전체에서 lag 프레임 뒤 글자 일치가 가장 큰 이동량 → 프레임당 화소"""
    m = fr > TH; L = min(12, len(fr) // 3); best = (0, 0)
    if L < 2: return 0.0
    for dx in range(4, 160):
        s = 0
        for i in range(0, len(fr) - L, 3):
            s += (m[i, :, dx:] & m[i + L, :, :320 - dx]).sum()
        if s > best[0]: best = (s, dx)
    return best[1] / L


def segments(fr):
    """글자 있는 프레임 구간(0.4초 넘는 빈틈으로 나눔)"""
    act = (fr > TH).sum((1, 2)) > 120
    out = []; i = 0; n = len(fr)
    while i < n:
        if not act[i]: i += 1; continue
        j = i; gap = 0; last = i
        while j < n and gap < FPS * 0.4:
            if act[j]: gap = 0; last = j
            else: gap += 1
            j += 1
        if last - i > FPS * 0.7: out.append((i, last))
        i = j
    return out


def stitch(fr, v):
    n = len(fr); W = int(v * n) + 320 + 4
    acc = np.zeros((H, W), np.float32); cnt = np.zeros((H, W), np.float32)
    for i in range(n):
        x = int(round(v * i)); acc[:, x:x + 320] += fr[i]; cnt[:, x:x + 320] += 1
    return (acc / np.maximum(cnt, 1)).astype(np.uint8)


def main():
    os.makedirs(OUT, exist_ok=True)
    names = sys.argv[1:] or MOV
    tsv = open(os.path.join(OUT, 'segs.tsv'), 'a', encoding='utf-8', newline=chr(10))
    f = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 14)
    for nm in names:
        fr = frames(nm); seg = segments(fr); rows = []
        print(nm, '프레임', len(fr), '구간', len(seg))
        for k, (a, b) in enumerate(seg):
            s = fr[a:b + 1]; v = speed(s); im = stitch(s, v) if v > 0 else s[len(s) // 2]
            I = Image.fromarray(im); I.save(os.path.join(OUT, '%s_%02d.png' % (nm, k)))
            tsv.write('%s\t%d\t%.2f\t%.2f\t%.2f\t%d\n' % (nm, k, a / FPS, b / FPS, v, im.shape[1]))
            rows.append((k, a / FPS, b / FPS, v, I))
            print(' ', k, round(a / FPS, 2), round(b / FPS, 2), 'v', round(v, 2), '폭', im.shape[1])
        # 읽기용 페이지: 구간을 폭 1500 줄로 접어 쌓는다
        Wd = 1500; lines = []
        for k, a, b, v, I in rows:
            lines.append(('#%02d  %.1f~%.1f초  v=%.2f' % (k, a, b, v), None))
            I2 = I.resize((I.width * 2, I.height * 2), Image.LANCZOS)
            for x in range(0, I2.width, Wd - 60):
                lines.append((None, I2.crop((x, 0, min(x + Wd, I2.width), I2.height))))
        hgt = sum(20 if t else 70 for t, _ in lines)
        pg = Image.new('L', (Wd, hgt), 30); d = ImageDraw.Draw(pg); y = 0
        for t, c in lines:
            if t: d.text((4, y + 1), t, 255, font=f); y += 20
            else: pg.paste(c, (0, y)); y += 70
        for i, y0 in enumerate(range(0, hgt, 1200)):
            pg.crop((0, y0, Wd, min(y0 + 1200, hgt))).save(os.path.join(OUT, '_%s_p%d.png' % (nm, i)))
    tsv.close()


if __name__ == '__main__':
    main()
