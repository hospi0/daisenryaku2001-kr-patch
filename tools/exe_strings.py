# -*- coding: utf-8 -*-
"""1ST_READ.BIN 문자열을 NUL 경계 + 포인터 참조로 뽑는다(읽기 전용). → work/text/exe_scan.tsv
python tools/exe_strings.py"""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc

B = 0x8C010000
JP = re.compile('[ぁ-んァ-ヶ一-龥々ー]')

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    D = Disc(1); ie.D = D
    w = {x[0]: x for x in ie.walk() if not x[3] & 2}
    e = D.read(*w['/1ST_READ.BIN'][1:3])
    # 실행 파일 안 포인터 전수(4바이트 정렬)
    ptr = collections.Counter()
    for o in range(0, len(e) - 3, 4):
        v = struct.unpack_from('<I', e, o)[0]
        if B <= v < B + len(e): ptr[v - B] += 1
    rows = []; bad = 0
    for m in re.finditer(rb'[^\x00]+', e):
        b = m.group(0); o = m.start()
        if len(b) < 2: continue
        try: t = b.decode('cp932')
        except Exception: bad += 1; continue
        if not JP.search(t): continue
        if any(ord(c) < 0x20 and c not in '\n\r\t' for c in t): continue
        rows.append((o, len(b), ptr.get(o, 0), t))
    ref = [r for r in rows if r[2]]; un = [r for r in rows if not r[2]]
    print('후보', len(rows), '참조 있음', len(ref), '없음', len(un), '복호 실패 조각', bad)
    print('참조 있음 글자 수', sum(len(r[3]) for r in ref), '고유', len({r[3] for r in ref}))
    # 구역별 분포(64KB)
    c = collections.Counter(r[0] >> 16 for r in ref); print('참조 분포', sorted((hex(k << 16), v) for k, v in c.items()))
    c = collections.Counter(r[0] >> 16 for r in un); print('무참조 분포', sorted((hex(k << 16), v) for k, v in c.items()))
    print('무참조 표본', [r[3][:24] for r in un[:: max(1, len(un) // 24)]][:24])
    print('참조 표본', [r[3][:24] for r in ref[:: max(1, len(ref) // 24)]][:24])
    os.makedirs('work/text', exist_ok=True)
    with open('work/text/exe_scan.tsv', 'w', encoding='utf-8') as f:
        f.write('#위치\t바이트\t참조\tJP\n')
        for o, n, p, t in rows:
            f.write('%06X\t%d\t%d\t%s\n' % (o, n, p, t.replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')))
    # SCG 구조
    d = D.read(*w['/SCENARIO/000EXERC.SCG'][1:3]); print('SCG', len(d), d[:64].hex(' '))
    p = d.find('本演習は'.encode('cp932')); print('브리핑 위치', hex(p), d[p - 48:p + 8].hex(' '))
    tot = 0; uq = set()
    for f, x in w.items():
        if f.startswith('/SCENARIO/'):
            q = D.read(x[1], x[2])
            for m in re.finditer(rb'(?:[\x81-\x9f\xe0-\xfc][\x40-\x7e\x80-\xfc]|[\x20-\x7e\x0a]){4,}', q):
                try: t = m.group(0).decode('cp932')
                except Exception: continue
                if len(JP.findall(t)) >= 2: tot += 1; uq.add(t)
    print('SCG 줄', tot, '고유', len(uq), '글자', sum(len(x) for x in uq))

if __name__ == '__main__':
    main()
