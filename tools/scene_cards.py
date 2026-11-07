# -*- coding: utf-8 -*-
"""시나리오 제목 카드: 원본 위 빈 곳에 작은 한글 뜻풀이(디스크 안 씀).
게임이 512×512 를 4:3 으로 늘려 보이므로 640×480 에 그린 뒤 512×512 로 줄여 얹는다.
  python tools/scene_cards.py [번호 …] → work/gfx/scene_new/*.png · *.pvr(VQ) · work/gfx/scene_preview_N.png(원본|새것, 재압축본)"""
import os, sys, subprocess, tempfile, shutil, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
PY = r'C:\claude\utils\dreamcast\PyPVR\pypvr.py'
FONT = 'C:/claude/utils/font/nanum-myeongjo/NanumMyeongjoExtraBold.ttf'
SIZE = 30
KO = ['군사 연습', '스페인 내전', '폴란드 전격전', '북유럽 침공', '서방 전격전', '브리튼 전투', '발칸 반도', '동부전선 개막', '동부전선', '모스크바 전투',
      '동부전선 제2막', '스탈린그라드 구출 작전', '동부전선 제3막', '쿠르스크 대전차전', '동부전선의 붕괴', '제3제국의 멸망', '북아프리카 전선', '엘알라메인의 사투',
      '미국 참전', '이탈리아 전선', '사상 최대의 작전', '서부전선', '벌지 전투', '바다사자 작전', '중동', '우랄', '미국 전선', '볼셰비키의 종언', '프롤레타리아 혁명']
FIX = {9: 'tr', 12: 'br', 15: 'bl', 16: 'br', 28: 'br'}                                     # 번호 → 'bl','br','tl','tr','bc','tc' (자동 선택을 사람이 바꿀 때)
OUT = 'work/gfx/scene_new'


def font():
    f = FONT
    if not os.path.exists(f):
        f = glob.glob('C:/claude/utils/font/nanum-myeongjo/*Bold*.ttf')[0]
    return ImageFont.truetype(f, SIZE)


def spots(w, h):
    m = 26
    return {'bl': (m, 480 - h - m), 'br': (640 - w - m, 480 - h - m), 'tl': (m, m), 'tr': (640 - w - m, m),
            'bc': ((640 - w) // 2, 480 - h - m), 'tc': ((640 - w) // 2, m)}


def pick(card, w, h):
    """글자 자리 후보 중 가장 잔잔한 곳(색 있는 큰 제목은 채도·경계가 높다)"""
    a = np.asarray(card.convert('RGB').resize((640, 480), Image.BILINEAR), np.float32)
    g = a.mean(2); e = np.abs(np.diff(g, axis=1))[:-1] + np.abs(np.diff(g, axis=0))[:, :-1]
    sat = a.max(2) - a.min(2)
    best = None
    for k, (x, y) in spots(w, h).items():
        s = e[y:y + h, x:x + w].mean() + 0.6 * sat[y:y + h, x:x + w].mean() + (3 if k[1] == 'c' else 0)
        if best is None or s < best[0]: best = (s, k)
    return best[1]


def card(i):
    src = Image.open('work/gfx/scene/SCENE%02d.png' % i).convert('RGB')
    f = font(); t = KO[i]
    bb = f.getbbox(t); w, h = bb[2] - bb[0] + 12, bb[3] - bb[1] + 12
    k = FIX.get(i) or pick(src, w, h); x, y = spots(w, h)[k]
    ov = Image.new('RGBA', (640, 480), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    sh = Image.new('RGBA', (640, 480), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((x + 6 - bb[0], y + 6 - bb[1]), t, font=f, fill=(0, 0, 0, 255), stroke_width=4, stroke_fill=(0, 0, 0, 255))
    sh = sh.filter(ImageFilter.GaussianBlur(2))
    ov = Image.alpha_composite(ov, sh); d = ImageDraw.Draw(ov)
    d.text((x + 6 - bb[0], y + 6 - bb[1]), t, font=f, fill=(250, 244, 226, 255), stroke_width=2, stroke_fill=(16, 16, 16, 255))
    ov = ov.resize((512, 512), Image.LANCZOS)
    out = src.convert('RGBA'); out.alpha_composite(ov)
    return out.convert('RGB'), k


def vq(im, n, tmp):
    p = os.path.join(tmp, 'c%s.png' % n); im.save(p)
    subprocess.run([sys.executable, PY, 'c%s.png' % n, '-565', '-vq', '-vqa1', '-nopvp', '-silent'], cwd=tmp, capture_output=True)
    q = os.path.join(tmp, 'c%s.pvr' % n)
    if not os.path.exists(q): q = os.path.join(tmp, 'c%s.PVR' % n)
    os.makedirs(os.path.join(tmp, 'd'), exist_ok=True)
    shutil.copyfile(q, os.path.join(tmp, 'd', 'x%s.PVR' % n))
    subprocess.run([sys.executable, PY, 'x%s.PVR' % n], cwd=os.path.join(tmp, 'd'), capture_output=True)
    return q, Image.open(os.path.join(tmp, 'd', 'x%s.png' % n)).convert('RGB')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    os.makedirs(OUT, exist_ok=True)
    want = [int(x) for x in sys.argv[1:]] or list(range(29))
    tmp = tempfile.mkdtemp(prefix='scn'); rows = []
    for i in want:
        im, k = card(i); n = '%02d' % i
        im.save(os.path.join(OUT, 'SCENE%s.png' % n))
        q, dec = vq(im, n, tmp)
        shutil.copyfile(q, os.path.join(OUT, 'SCENE%s.pvrnew' % n)); dec.save(os.path.join(OUT, 'SCENE%s_vq.png' % n))
        rows.append((i, k)); print(i, KO[i], k, os.path.getsize(q), flush=True)
    shutil.rmtree(tmp, ignore_errors=True)
    fs = sorted(glob.glob(OUT + '/SCENE*_vq.png')); C = 4; W, H = 400, 300; f = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 13)
    for s in range(0, len(fs), 12):
        part = fs[s:s + 12]; pg = Image.new('RGB', (C * W, ((len(part) + C - 1) // C) * (H + 18)), (34, 34, 40)); d = ImageDraw.Draw(pg)
        for j, p in enumerate(part):
            im = Image.open(p).resize((W - 4, H), Image.LANCZOS); x = (j % C) * W; y = (j // C) * (H + 18)
            pg.paste(im, (x + 2, y + 18)); d.text((x + 4, y + 1), os.path.basename(p)[:7], fill=(255, 230, 120), font=f)
        pg.save('work/gfx/scene_v2_%d.png' % (s // 12))


if __name__ == '__main__':
    main()
