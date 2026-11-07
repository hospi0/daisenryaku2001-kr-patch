# -*- coding: utf-8 -*-
"""UI PVR 을 PyPVR 로 풀어 시트로(읽기 전용, 디스크 안 씀). work/gfx/orig/*.png + work/gfx/sheet_N.png"""
import sys, os, subprocess, tempfile, shutil, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
PY = r'C:\claude\utils\dreamcast\PyPVR\pypvr.py'
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
SKIP = ('HU_2D', 'HMTREE', 'SWWT', 'HMEXPLODE', 'HMFLAG')
names = [f for f in sorted(w) if f.count('/') == 1 and f.endswith('.PVR') and not f[1:].startswith(SKIP)]
os.makedirs('work/gfx/orig', exist_ok=True)
tmp = tempfile.mkdtemp(prefix='pvr'); bad = []
for f in names:
    n = f[1:-4]; o = 'work/gfx/orig/%s.png' % n
    if os.path.exists(o): continue
    p = os.path.join(tmp, n + '.PVR'); open(p, 'wb').write(D.read(*w[f][1:3]))
    r = subprocess.run([sys.executable, PY, p, '-o', tmp, '-png'], capture_output=True, text=True, cwd=tmp)
    q = glob.glob(os.path.join(tmp, '**', n + '*.png'), recursive=True)
    if q: shutil.move(q[0], o)
    else: bad.append(n)
shutil.rmtree(tmp, ignore_errors=True)
print('풀림', len(glob.glob('work/gfx/orig/*.png')), '실패', len(bad), bad[:10])
fs = sorted(glob.glob('work/gfx/orig/*.png')); C = 8; T = 190
for s in range(0, len(fs), 48):
    pg = Image.new('RGB', (C * T, 6 * (T + 14)), (70, 70, 90)); d = ImageDraw.Draw(pg)
    for i, f in enumerate(fs[s:s + 48]):
        im = Image.open(f).convert('RGBA'); im.thumbnail((T - 4, T - 4))
        x = (i % C) * T; y = (i // C) * (T + 14)
        pg.paste(im, (x + 2, y + 13), im); d.text((x + 2, y + 1), os.path.basename(f)[:-4][:24], fill=(255, 255, 0))
    pg.save('work/gfx/sheet_%d.png' % (s // 48))
print(len(fs), (len(fs) + 47) // 48)
