# -*- coding: utf-8 -*-
"""디스크 전 파일에서 화면 문구를 인코딩별로 찾는다(읽기 전용). 동영상 제외.  python tools/scan_text.py"""
import sys, os, collections, re, gzip
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie
from gdi import Disc

WORDS = ['どの項目を聞きたいですか', '勝利条件を教えてください', '難易度を調整しますか', '軍事費', '騎兵小隊', '参謀に作戦行動案を立案させます',
         'ゲーム再開ファイルをロードします', '本演習は敵首都占領による', '生産', '開発表で生産廃止可能なユニットを確認だ', '経験値', '特殊装備', '司令部', '首都']

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    D = Disc(1); ie.D = D
    w = [x for x in ie.walk() if not x[3] & 2]
    pats = {}
    for t in WORDS:
        for enc in ('shift_jis', 'euc_jp', 'utf-16-le', 'utf-16-be'):
            pats[t.encode(enc)] = (t, enc)
    hit = collections.defaultdict(collections.Counter); head = collections.Counter(); ex = {}
    for f, l, s, fl in w:
        if f.endswith('.SFD'): continue
        d = D.read(l, s)
        head[(f.rsplit('.', 1)[-1], d[:4])] += 1
        for b, (t, enc) in pats.items():
            n = d.count(b)
            if n: hit[(t, enc)][f] += n
    for k, v in hit.items(): print(k, sum(v.values()), v.most_common(5))
    print(sorted(((str(k), n) for k, n in head.items()), key=lambda x: -x[1])[:30])

if __name__ == '__main__':
    main()
