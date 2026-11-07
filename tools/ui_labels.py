# -*- coding: utf-8 -*-
"""UI 그림 라벨 한글화(디스크 안 씀). 칸 좌표표대로 원본 글자 범위 안에만 그린다.
  python tools/ui_labels.py → work/gfx/ui_new/*.png, *_vq.png, work/gfx/ui_preview/*.png(원본|새것, 재압축본)"""
import os, sys, struct, subprocess, tempfile, shutil
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
PY = r'C:\claude\utils\dreamcast\PyPVR\pypvr.py'
FONT = 'C:/claude/utils/font/nanum-gothic/NanumGothicBold.ttf'
OUT = 'work/gfx/ui_new'; PV = 'work/gfx/ui_v9'
LB = (200, 232, 248); WT = (246, 246, 246); BK = (0, 0, 0); CY = (150, 225, 235); WH = (240, 240, 240); DK = (8, 12, 16)
# 이름: (형식, [(x0,y0,x1,y1,글, 글자색, 테두리색, 방식)…])  방식 c=투명으로 지움, p=판 무늬로 메움
T = {
 'DC2LUNITP0': ('1555', [(0, 0, 35, 19, '번호', CY, DK, 'c'), (35, 0, 61, 19, '종류', CY, DK, 'c'), (69, 0, 111, 19, '기수', CY, DK, 'c'),
                         (0, 21, 93, 39, '유닛 이름', CY, DK, 'c'), (0, 40, 31, 59, '연료', CY, DK, 'c'), (31, 40, 63, 59, '경험', CY, DK, 'c'),
                         (69, 40, 112, 59, '상태', CY, DK, 'c'), (0, 60, 40, 79, '좌표', CY, DK, 'c'), (0, 80, 74, 100, '탑재 정보', CY, DK, 'c')]),
 'DW2EVOP0': ('4444', [(0, 0, 128, 30, '예산 보고', (205, 205, 205), None, 'c'), (0, 32, 96, 62, '개량 전', (205, 205, 205), None, 'c'), (0, 64, 96, 95, '진화 후', (205, 205, 205), None, 'c')]),
 'DW2SPECP0': ('1555', [(74, 0, 128, 18, '환장비', LB, BK, 'c'),
                        (0, 20, 32, 35, '대공', WT, None, 'c'), (32, 20, 64, 35, '대지', WT, None, 'c'), (64, 20, 96, 35, '대갑', WT, None, 'c'), (96, 20, 128, 35, '비갑', WT, None, 'c'),
                        (0, 36, 33, 50, '대함', WT, None, 'c'), (33, 36, 67, 50, '대잠', WT, None, 'c'), (85, 36, 120, 50, '특수', WT, None, 'c'),
                        (0, 51, 53, 66, '공격력', LB, BK, 'c'), (53, 51, 86, 66, '사정', LB, BK, 'c'),
                        (0, 67, 36, 83, '우선', LB, BK, 'c'), (36, 67, 71, 83, '명중', LB, BK, 'c'), (71, 67, 104, 83, '가격', LB, BK, 'c')]),
 'DW2SPECP1': ('1555', [(0, 36, 34, 51, '공격', WH, None, 'f'), (34, 36, 68, 51, '격파', WH, None, 'f'), (68, 36, 102, 51, '탄수', WH, None, 'f'),
                        (0, 52, 34, 68, '명중', WH, None, 'f'), (34, 52, 68, 68, '우선', WH, None, 'f')]),
 'DW2SPECP3': ('1555', [(3, 3, 55, 25, '색적', (28, 56, 120), None, 'p'), (61, 3, 113, 25, '이동', (28, 56, 120), None, 'p'), (3, 33, 103, 55, '특수 장비', (28, 56, 120), None, 'p'),
                        (3, 63, 55, 85, '방어', (28, 56, 120), None, 'p'), (3, 93, 55, 115, '전적', (28, 56, 120), None, 'p'), (61, 93, 113, 115, '탑재', (28, 56, 120), None, 'p')]),
 'GWL2STATP2': ('1555', [(0, 0, 60, 19, '일출', (170, 60, 150), DK, 'c'), (0, 20, 60, 39, '일몰', (220, 70, 30), DK, 'c'), (0, 40, 60, 59, '강우율', (80, 190, 215), DK, 'c'),
                         (80, 32, 120, 50, '날씨', (50, 150, 70), DK, 'c'), (80, 52, 120, 71, '달', (200, 190, 160), DK, 'c'),
                         (0, 60, 80, 79, '최고 기온', (190, 0, 0), DK, 'c'), (0, 80, 80, 100, '최저 기온', (20, 50, 190), DK, 'c')]),
 'GX2MENUP1': ('1555', [(0, 0, 40, 20, '설정', (35, 200, 205), DK, 'c'), (42, 0, 84, 20, '전략', (35, 200, 205), DK, 'c'), (0, 22, 40, 42, '도표', (35, 200, 205), DK, 'c'), (42, 22, 123, 42, '시스템', (35, 200, 205), DK, 'c'),
                        (0, 44, 64, 64, '전자동', (35, 200, 205), DK, 'c'), (0, 66, 65, 84, '규칙', (35, 200, 205), DK, 'c'), (0, 86, 81, 106, '사운드', (35, 200, 205), DK, 'c')]),
 'MC2SELP1': ('1555', []),
 'GWL2STATP1': ('1555', [(x * 60 + 4, y * 24 + 4, x * 60 + 56, y * 24 + 21, t, (10, 12, 14), None, 'p') for y, r in enumerate(['전투기 공격기 폭격기 초계기', '수송기 - 전차 대공포', '견인포 병력 수송차 요새', '전투함 보조함 잠수함 총병력'])
                         for x, t in enumerate(r.split()) if t != '-']),
 'SWND2P3': ('4444', [(97, 2, 128, 22, '지형', (10, 10, 10), None, 'p'), (97, 26, 128, 46, '고도', (10, 10, 10), None, 'p'), (97, 50, 128, 70, '노선', (10, 10, 10), None, 'p'),
                      (97, 74, 128, 94, '제한', (10, 10, 10), None, 'p'), (97, 98, 128, 118, '점령', (10, 10, 10), None, 'p'), (65, 106, 96, 126, '지명', (10, 10, 10), None, 'p')]),
 'GWL2STATP0': ('4444', [(0, 2, 80, 16, '글라이더', DK, None, 'c'), (81, 2, 112, 16, '공수', DK, None, 'c'), (112, 2, 144, 16, '강하', DK, None, 'c'), (144, 2, 176, 16, '발진', DK, None, 'c'), (176, 2, 208, 16, '폭격', DK, None, 'c'),
                         (0, 17, 80, 32, '어뢰·폭뢰', DK, None, 'c'), (81, 17, 128, 32, '소나', DK, None, 'c'), (129, 17, 192, 32, '수상 하차', DK, None, 'c'),
                         (0, 34, 64, 48, '수상 보급', DK, None, 'c'), (81, 34, 128, 48, '명중률', DK, None, 'c'), (129, 34, 175, 48, '공격력', DK, None, 'c'), (176, 34, 208, 48, '시인', DK, None, 'c'), (208, 34, 240, 48, '속도', DK, None, 'c'),
                         (0, 50, 32, 64, '하차', DK, None, 'c'), (32, 50, 80, 64, '스노클', DK, None, 'c'), (81, 50, 128, 64, '대공', DK, None, 'c'), (129, 50, 175, 64, '레이더', DK, None, 'c'), (176, 50, 250, 64, '간접 사격', DK, None, 'c'),
                         (143, 66, 176, 81, '불가', (10, 10, 170), None, 'c'), (218, 66, 248, 81, '점령', DK, None, 'c'), (143, 82, 176, 97, '불가', WH, None, 'c'), (218, 82, 248, 97, '대지', DK, None, 'c'),
                         (0, 114, 80, 129, '수납 시 손해', DK, None, 'c'), (0, 130, 80, 145, '착함 시 손해', DK, None, 'c')]),
}


CLR = {
 'GWL2STATP0': [(0, 0, 222, 16), (0, 16, 222, 33), (0, 33, 256, 49), (0, 49, 256, 65), (143, 65, 178, 98), (216, 65, 256, 98), (0, 112, 90, 147)],
 'GWL2STATP2': [(0, 0, 62, 62), (0, 59, 80, 102), (78, 30, 124, 72)],     # 회색 원은 x 81~ · y 72~
 'GX2MENUP1': [(0, 0, 128, 108)],
 'DC2LUNITP0': [(0, 0, 114, 80), (0, 80, 75, 102)],
 'DW2SPECP0': [(72, 0, 128, 19), (0, 19, 128, 84)],
 'DW2EVOP0': [(0, 0, 128, 31), (0, 31, 96, 64), (0, 64, 96, 95)],
 'MC2SELP1': [(0, 0, 114, 38)],
}


SMOOTH = ('GWL2STATP2',)   # 글자·테두리 사이를 섞어 그리는 그림
ALPHA = ('DW2EVOP0',)                       # 4444 + 테두리 없음: 알파로 부드럽게


G14 = ('bdf', 'C:/claude/utils/font/Galmuri-v2.40.3/Galmuri14.bdf')     # TTF 는 재계산으로 획이 어긋난다, BDF 화소 그대로
NB18 = ('C:/claude/utils/font/nanum-gothic/NanumGothicBold.ttf', 18)
PIX = {'DC2LUNITP0': G14, 'DW2SPECP0': G14, 'GWL2STATP0': G14, 'GX2MENUP1': NB18}     # 보간 없이 또렷하게


_BDF = {}


def draw_bdf(w, h, t, path):
    """BDF 글자 화소 그대로. 칸이 좁으면 글자 사이만 최대 2 줄인다(글자 자체는 안 건드림)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import bdf
    f = _BDF.setdefault(path, bdf.Font(path))
    gl = [f.draw(c) for c in t]
    tot = sum(g[1] for g in gl); cut = 0
    while cut < 2 and tot - cut * sum(1 for c in t[:-1] if ord(c) > 127) > w: cut += 1
    a = np.zeros((40, w + 40), np.float32); x = 0
    for c, (pts, dw) in zip(t, gl):
        for px, py in pts:
            if 0 <= py < 40 and x + px < a.shape[1]: a[py, x + px] = 1
        x += dw - (cut if ord(c) > 127 else 0)
    a = a[:, :w]
    ys = np.nonzero(a.sum(1))[0]; a = a[ys[0]:ys[-1] + 1]
    out = np.zeros((h, w), np.float32); y = max((h - a.shape[0]) // 2, 0); out[y:y + a.shape[0]] = a[:h - y]
    return out


def draw_pix(w, h, t, spec):
    """픽셀 글꼴을 원래 크기 그대로(늘리지 않음). 칸이 좁으면 글자 간격만 1 줄인다."""
    if spec[0] == 'bdf':
        return draw_bdf(w, h, t, spec[1])
    path, size = spec
    f = ImageFont.truetype(path, size)
    full = int(round(f.getlength('가'))); adv = full; half = int(round(f.getlength(' ')))
    while adv > full - 3 and sum(adv if ord(c) > 127 else half for c in t) > w: adv -= 1
    im = Image.new('1', (w + 24, h + 24), 0); d = ImageDraw.Draw(im); d.fontmode = '1'
    x = 0
    for c in t:
        d.text((x, 2), c, 1, font=f); x += adv if ord(c) > 127 else half
    a = np.asarray(im, np.float32)[:, :w]
    ys = np.nonzero(a.sum(1))[0]; a = a[ys[0]:ys[-1] + 1]
    out = np.zeros((h, w), np.float32); y = max((h - a.shape[0]) // 2, 0); out[y:y + a.shape[0]] = a[:h - y]
    return out


def draw(w, h, t, left=False):
    """글자 가림막: 칸 크기 w×h 안에 맞춘 알파"""
    f = ImageFont.truetype(FONT, 100)
    bb = f.getbbox(t); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    im = Image.new('L', (tw + 8, th + 8), 0); ImageDraw.Draw(im).text((4 - bb[0], 4 - bb[1]), t, 255, font=f)
    hh = h; ww = int(tw * hh / th)
    if ww > w: ww = w
    pad = 1
    r = im.resize((max(1, ww - 2 * pad), max(1, hh - 2 * pad)), Image.LANCZOS)
    out = Image.new('L', (w, h), 0); out.paste(r, (0 if left else (w - r.width) // 2, (h - r.height) // 2))
    return np.asarray(out, np.float32) / 255


def erase(a, x0, y0, x1, y1, n):
    """판 위 글자 화소만 판 무늬로 메운다. 판 색 = 밝은 쪽 표본(글자가 칸의 절반을 넘어도 안 속게)"""
    H, W = a.shape[:2]; e = 3 if n == 'DW2SPECP3' else 0
    x0, y0, x1, y1 = max(x0 - e, 0), max(y0 - e, 0), min(x1 + e, W), min(y1 + e, H)
    reg = np.ascontiguousarray(a[y0:y1, x0:x1, :3]); lum = reg.astype(np.float32).mean(2)
    if n == 'DW2SPECP3':
        m = reg[:, :, 2].astype(int) > reg[:, :, 0].astype(int) + 8       # 글자만 파랗다(판·턱은 노랑·갈색)
    else:
        m = lum < np.percentile(lum, 80) - 40
    m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8))
    a[y0:y1, x0:x1, :3] = cv2.inpaint(reg, m, 3, cv2.INPAINT_TELEA)


def apply(a, box, n):
    x0, y0, x1, y1, t, fg, ol, mode = box
    if mode == 'p':
        erase(a, x0, y0, x1, y1, n)
    elif mode == 'f':
        reg = a[y0:y1, x0:x1, :3].reshape(-1, 3)
        a[y0:y1, x0:x1, :3] = np.percentile(reg, 10, axis=0).astype(np.uint8)   # 어두운 판 + 흰 글자
    else:
        a[y0:y1, x0:x1] = 0
    k = draw_pix(x1 - x0, y1 - y0, t, PIX[n]) if n in PIX else draw(x1 - x0, y1 - y0, t, left=mode == 'c')
    if n in SMOOTH and ol is not None:
        sol = cv2.dilate((k > 0.15).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        c = np.array(ol, np.float32) * (1 - k[..., None]) + np.array(fg, np.float32) * k[..., None]
        v = a[y0:y1, x0:x1]; v[sol, :3] = c[sol].astype(np.uint8); v[sol, 3] = 255
        return
    if n in ALPHA and mode == 'c':
        v = a[y0:y1, x0:x1]; sol = k > 0.04
        v[sol, :3] = fg; v[sol, 3] = (np.clip(k[sol] * 1.25, 0, 1) * 255).astype(np.uint8)
        return
    on = k > 0.45
    if ol is not None:
        o = cv2.dilate(on.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~on
        a[y0:y1, x0:x1][o] = (*ol, 255)
    if mode == 'c':
        a[y0:y1, x0:x1][on] = (*fg, 255)
    else:
        v = a[y0:y1, x0:x1, :3].astype(np.float32); al = np.clip(k * 1.4, 0, 1)[..., None]
        a[y0:y1, x0:x1, :3] = (v * (1 - al) + np.array(fg, np.float32) * al).astype(np.uint8)


def shadow_label(a):
    """未対応 자리: 늘리지 않은 큰 글자 + 오른쪽 아래 검은 그림자(원본 방식)"""
    f = ImageFont.truetype('C:/claude/utils/font/nanum-gothic/NanumGothicExtraBold.ttf', 33)
    im = Image.new('L', (160, 60), 0); ImageDraw.Draw(im).text((2, 2), '미대응', 255, font=f)
    k = np.asarray(im, np.float32) / 255
    ys, xs = np.nonzero(k > 0.3); k = k[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = k.shape; w = min(w, 110); k = k[:, :w]; y0, x0 = max((35 - h) // 2, 0), 1
    sh = np.zeros((38, 114), np.float32); sh[y0 + 3:y0 + 3 + h, x0 + 3:x0 + 3 + w] = np.maximum(sh[y0 + 3:y0 + 3 + h, x0 + 3:x0 + 3 + w], k[:35 - y0, :])
    v = a[0:38, 0:114]; m = sh > 0.4; v[m] = (0, 0, 0, 255)
    t = np.zeros((38, 114), np.float32); t[y0:y0 + h, x0:x0 + w] = k
    on = t > 0.12
    c = np.where(m[..., None], 0, 150) * (1 - t[..., None]) + 246 * t[..., None]
    v[on, :3] = c[on].astype(np.uint8); v[on, 3] = 255


def exp_label(a):
    """経験値: 넘친 끝 조각까지 한 줄로 그려 (58,60)~ 와 (115,30)~ 로 나눈다"""
    fg = (28, 56, 120)
    W = 83; H = 22
    erase(a, 61, 63, 128, 85, 'DW2SPECP3'); erase(a, 115, 33, 128, 55, 'DW2SPECP3')
    k = draw(W - 3, H, '경험치'); al = np.clip(k * 1.4, 0, 1)[..., None]
    v = a[63:85, 61:128, :3].astype(np.float32)
    a[63:85, 61:128, :3] = (v * (1 - al[:, :67]) + np.array(fg, np.float32) * al[:, :67]).astype(np.uint8)
    v = a[33:55, 115:128, :3].astype(np.float32); w2 = al[:, 67:80]
    a[33:55, 115:115 + w2.shape[1], :3] = (v[:, :w2.shape[1]] * (1 - w2) + np.array(fg, np.float32) * w2).astype(np.uint8)


def logo():
    """LOGOMSG: 검은 판 가운데 두 줄. 640×480 기준으로 그려 512×512 로"""
    src = Image.open('work/gfx/orig/LOGOMSG.png').convert('RGB'); a = np.asarray(src).copy()
    a[140:330] = 0
    f = ImageFont.truetype('C:/claude/utils/font/nanum-myeongjo/NanumMyeongjoExtraBold.ttf', 36)
    ov = Image.new('RGB', (640, 480), (0, 0, 0)); d = ImageDraw.Draw(ov)
    for y, t in ((185, '이 비극이 두 번 다시'), (235, '되풀이되지 않기를 바라며')):
        d.text((320, y), t, (70, 90, 235), font=f, anchor='ma', stroke_width=3, stroke_fill=(30, 40, 160))
    for y, t in ((185, '이 비극이 두 번 다시'), (235, '되풀이되지 않기를 바라며')):
        d.text((320, y), t, (235, 240, 255), font=f, anchor='ma')
    b = np.asarray(ov.resize((512, 512), Image.LANCZOS))
    a[140:330] = b[140:330]
    return Image.fromarray(a)


def vq(im, fmt, n, tmp):
    p = os.path.join(tmp, 'u%s.png' % n); im.save(p)
    arg = {'1555': ['-1555', '-vq', '-vqa1'], '4444': ['-4444', '-vq', '-vqa1'], '565': ['-565', '-vq', '-vqa1'], '4444tw': ['-4444', '-tw']}[fmt]
    subprocess.run([sys.executable, PY, 'u%s.png' % n] + arg + ['-nopvp', '-silent'], cwd=tmp, capture_output=True)
    q = os.path.join(tmp, 'u%s.PVR' % n)
    os.makedirs(os.path.join(tmp, 'd'), exist_ok=True); shutil.copyfile(q, os.path.join(tmp, 'd', 'x%s.PVR' % n))
    subprocess.run([sys.executable, PY, 'x%s.PVR' % n], cwd=os.path.join(tmp, 'd'), capture_output=True)
    return q, Image.open(os.path.join(tmp, 'd', 'x%s.png' % n)).convert('RGBA')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    os.makedirs(OUT, exist_ok=True); os.makedirs(PV, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='ui')
    for n, (fmt, boxes) in T.items():
        a = np.asarray(Image.open('work/gfx/orig/%s.png' % n).convert('RGBA')).copy()
        for x0, y0, x1, y1 in CLR.get(n, []): a[y0:y1, x0:x1] = 0
        if n == 'DW2SPECP1':
            for x0, y0, x1, y1 in ((0, 36, 102, 52), (0, 52, 68, 68)):
                v = a[y0:y1, x0:x1]; solid = v[:, :, 3] > 0
                dark = solid & (v[:, :, :3].astype(int).sum(2) < 200) & (v[:, :, :3].astype(int).sum(2) > 20)
                col = np.median(v[dark][:, :3], 0).astype(np.uint8)
                v[solid, :3] = col
        if n == 'SWND2P3':
            erase(a, 96, 48, 128, 96, n)
        for b in boxes: apply(a, b, n)
        if n == 'MC2SELP1': shadow_label(a)
        if n == 'DW2SPECP3': exp_label(a)
        im = Image.fromarray(a); im.save(os.path.join(OUT, n + '.png'))
        q, dec = vq(im, '4444tw' if n == 'SWND2P3' else fmt, n, tmp)
        shutil.copyfile(q, os.path.join(OUT, n + '.pvrnew')); dec.save(os.path.join(OUT, n + '_vq.png'))
        o = Image.open('work/gfx/orig/%s.png' % n).convert('RGBA'); S = 3 if o.width <= 128 else 2
        pg = Image.new('RGB', (o.width * S * 2 + 12, o.height * S), (60, 90, 70))
        for i, g in enumerate((o, dec)):
            r = g.resize((o.width * S, o.height * S), Image.NEAREST); pg.paste(r, (i * (o.width * S + 12), 0), r)
        pg.save(os.path.join(PV, n + '.png')); print(n, os.path.getsize(q), flush=True)
    im = logo(); im.save(os.path.join(OUT, 'LOGOMSG.png'))
    q, dec = vq(im, '565', 'LOGOMSG', tmp); shutil.copyfile(q, os.path.join(OUT, 'LOGOMSG.pvrnew')); dec.convert('RGB').resize((640, 480), Image.LANCZOS).save(os.path.join(PV, 'LOGOMSG.png'))
    shutil.rmtree(tmp, ignore_errors=True)
    for k, ns in enumerate((('DC2LUNITP0', 'DW2SPECP0', 'DW2SPECP1'), ('DW2SPECP3', 'GWL2STATP2', 'GX2MENUP1'), ('DW2EVOP0', 'MC2SELP1', 'SWND2P3'))):
        ims = [Image.open(os.path.join(PV, n + '.png')) for n in ns]
        pg = Image.new('RGB', (max(i.width for i in ims), sum(i.height + 6 for i in ims)), (0, 0, 0)); y = 0
        for i in ims: pg.paste(i, (0, y)); y += i.height + 6
        pg.save(os.path.join(PV, '_s%d.png' % k))


if __name__ == '__main__':
    main()
