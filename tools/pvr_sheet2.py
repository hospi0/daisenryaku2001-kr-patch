# -*- coding: utf-8 -*-
"""SCENE 폴더 그림 시트와 얼굴 아닌 나머지 이름(읽기 전용)."""
import sys, os, subprocess, tempfile, shutil, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
PY = r'C:\claude\utils\dreamcast\PyPVR\pypvr.py'
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
sc = [f for f in sorted(w) if f.startswith('/SCENE/')]
print(len(sc), sc[:6], {f.rsplit('.', 1)[-1] for f in sc})
os.makedirs('work/gfx/scene', exist_ok=True)
tmp = tempfile.mkdtemp(prefix='pvr')
for f in sc:
    if not f.endswith('.PVR'): continue
    n = f.split('/')[-1][:-4]; p = os.path.join(tmp, n + '.PVR'); open(p, 'wb').write(D.read(*w[f][1:3]))
    subprocess.run([sys.executable, PY, p, '-o', tmp, '-png'], capture_output=True, text=True, cwd=tmp)
    q = glob.glob(os.path.join(tmp, '**', n + '*.png'), recursive=True)
    if q: shutil.move(q[0], 'work/gfx/scene/%s.png' % n)
shutil.rmtree(tmp, ignore_errors=True)
fs = sorted(glob.glob('work/gfx/scene/*.png')); C = 8; T = 190
pg = Image.new('RGB', (C * T, ((len(fs) + C - 1) // C) * (T + 14)), (70, 70, 90)); d = ImageDraw.Draw(pg)
for i, f in enumerate(fs):
    im = Image.open(f).convert('RGBA'); s = im.size; im.thumbnail((T - 4, T - 4))
    x = (i % C) * T; y = (i // C) * (T + 14)
    pg.paste(im, (x + 2, y + 13), im); d.text((x + 2, y + 1), '%s %dx%d' % (os.path.basename(f)[:-4][:14], s[0], s[1]), fill=(255, 255, 0))
pg.save('work/gfx/sheet_scene.png')
rest = [os.path.basename(f)[:-4] for f in sorted(glob.glob('work/gfx/orig/*.png')) if not os.path.basename(f).startswith('Z')]
print(len(rest), rest[-24:])
print('Z', sum(1 for f in glob.glob('work/gfx/orig/Z*.png')))
