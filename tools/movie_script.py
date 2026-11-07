# -*- coding: utf-8 -*-
"""해설 자막 대본 + 시각 → work/text/movie.tsv, my files/tsv/dai_movie.tsv(읽기 전용 측정).
시각: 그림 x 의 글자가 화면 오른쪽에 들어오는 때 = t0+(x-320)/v/30, 왼쪽으로 나가는 때 = t0+x/v/30.
python tools/movie_script.py"""
import os, sys
import numpy as np
from PIL import Image
FPS = 30
S = {
 'CAMPAIGN0': [
  '第1次世界大戦敗戦国のドイツは大幅な軍縮と多額の賠償金を課せられ、仏との国境に幅50キロの非武装中立地帯が設けられた。',
  'ナチスによる一揆が発生。だが、軍及びバイエルン州政府の支持を得られず即日鎮圧され、ヒトラーは逮捕、投獄された。',
  'ニューヨーク証券取引所の株価暴落から史上最大の経済恐慌が発生。この大恐慌によってドイツでは600万人が失業した。',
  'ヒンデンブルク大統領の任命を受け、ヒトラー首相に就任。ナチスと保守派による連立政権が成立する。',
  'ヒンデンブルク大統領が死亡。その前日に制定された国家元首法によりヒトラーの大統領・首相兼任が決定する。',
  'ヒトラーは国民徴兵制復活、空軍保有を明らかにし、ヴェルサイユ条約軍備制限条項破棄を宣言した。',
  '前年からの国境紛争を口実として、イタリア軍がアビシニアへの武力侵攻を開始した。',
  '仏ソ相互援助条約締結を理由として、独軍はヴェルサイユ及びロカルノ条約を破棄、ラインラント非武装地域に進駐、再占領した。',
  '人民戦線政府に対しフランコ将軍らが反乱、内戦となる。ヒトラーはフランコ軍への援助として空軍「コンドル軍団」を派遣した。'],
 'ENDINGFAIL': [
  'ヨードル将軍、フリーデブルク提督とが、アイゼンハワー将軍の司令部でドイツの無条件降伏文書に調印した。',
  'カイテル将軍、フリーデブルク提督、シュトゥンプフ将軍がジューコフ将軍の司令部でドイツの無条件降伏文書に調印した。',
  'トルーマン、スターリン、チャーチルの三者が参集し、ドイツの戦後処理、対日処置について協議した。',
  'この日正午、日本で国民に対する終戦詔書が放送された。また、翌日には日本陸海軍全部隊への停戦命令が発せられた。',
  'ドイツの主要戦争犯罪人の裁判がニュルンベルクで始まり、ナチス党幹部や将軍など24名が裁かれた。',
  '日本の敗戦により、領土の回復と平和の訪れた中国であったが、毛沢東の共産党と蒋介石の国民党の間での内戦が激化する。',
  'フランスはインドシナの再植民地化を試み軍事占領を強行、ホー・チミンのベトミン軍との武力衝突に発展した。',
  'ユダヤ国民評議会の樹立宣言と同時にアラブ諸国がイスラエルを攻撃。この結果、百万のパレスチナ人が故郷を追われた。',
  'ソ連占領区から西ベルリンの境界が全て封鎖された。西側は食料や燃料の大規模な空輸を行い、危機を回避した。',
  '第一次連邦議会選挙が行われ、大統領が選出された。新しい大統領、首相のもとに政府が機能した。',
  '人民議会がドイツ民主共和国樹立を宣言。ソ連は新政権に行政権を委譲。',
  'ドイツは事実上分割された。だがそれは、単に忌まわしい「軍事占領地区に分かれた」というだけに過ぎない。この悲劇については、それはただ永続するものではないと言えるのみである。　W・S・チャーチル'],
 'ENDINGUSAWIN': [
  '7月16日0207時　ニューメキシコ州アラモゴード砂漠',
  '「ハイル・ヒトラー！」「ハイル・ヒトラー！」早朝にも関わらず、独系アメリカ人団体「ブント」の会員約2万人が集まり、ナチス式の敬礼と共に総統を出迎えた。'],
 'ENDINGUSAFAIL': ['ドイツ・アメリカ軍は力つき、兵士は続々と降伏・投降していった。独米両国は大西洋を挟んで膠着状態におちいったが、やがて…'],
 'ENDINGEUROPEEWIN': ['「同志諸君、革命は達成された。ヨーロッパは我々労働者のものである。全ての労働者達の、偉大な祖国となったのである」「祖国のために！　スターリンのために！」'],
 'ENDINGEUROPEFAIL': ['我々はドイツ主権維持のため、2つに分かれてまで戦った。しかし我々の選択はより悲惨な結果を招いただけではないか？　本当にこれでよかったのだろうか…。'],
 'ENDINGEUROPEWWIN': ['「今やソビエトはウラル山脈に引かれた、強く冷たい鉄のカーテンの向こうへ消えていった。我々は赤どもに勝ったのだ！」チャーチル首相の声が、朗々と赤の広場に響いた。'],
}


def groups(im, gap):
    a = im[6:30].astype(np.float32)
    hp = np.abs(a - np.median(a, 0, keepdims=True))             # 세로 대비 = 글자
    e = (a > np.median(a) + 45).sum(0).astype(np.float32)
    e = np.convolve(e, np.ones(5) / 5, 'same')
    on = np.nonzero(e > 1.2)[0]
    if not len(on): return []
    out = []; s = p = on[0]
    for x in on[1:]:
        if x - p > gap: out.append((int(s), int(p))); s = x
        p = x
    out.append((int(s), int(p)))
    return [g for g in out if g[1] - g[0] >= 500]       # 짧은 묶음은 밝은 배경 잡음


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    segs = {}
    for l in open('work/movie/ticker/segs.tsv', encoding='utf-8'):
        n, k, a, b, v, w = l.rstrip('\n').split('\t'); segs.setdefault(n, []).append((int(k), float(a), float(b), float(v)))
    rows = []
    for n, ss in S.items():
        got = []
        for k, a, b, v in segs[n]:
            if v < 2: continue
            im = np.asarray(Image.open('work/movie/ticker/%s_%02d.png' % (n, k)))
            for x0, x1 in groups(im, 75):
                got.append((a + (x0 - 320) / v / FPS, a + x1 / v / FPS, k, x1 - x0))
        print(n, '문장', len(ss), '글자 묶음', len(got), [(round(g[0], 1), round(g[1], 1), g[3]) for g in got])
        assert len(got) == len(ss), n
        for i, (s, g) in enumerate(zip(ss, got), 1): rows.append((n, i, max(g[0], 0), g[1], s))
    head = '#번호\t영상\t시작\t끝\tJP\tKO\n'
    for fn in ('work/text/movie.tsv', os.path.join('my files', 'tsv', 'dai_movie.tsv')):
        with open(fn, 'w', encoding='utf-8', newline=chr(10)) as f:
            f.write(head)
            for j, (n, i, a, b, t) in enumerate(rows, 1):
                f.write('V%02d\t%s\t%.1f\t%.1f\t%s\t\n' % (j, n, a, b, t))
    print('대본', len(rows), '줄', sum(len(r[4]) for r in rows), '자')
    return rows


if __name__ == '__main__':
    main()
