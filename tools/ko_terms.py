# -*- coding: utf-8 -*-
"""그림·동영상 표기와 번역본 대조(읽기 전용)."""
import sys, os, glob, re
sys.stdout.reconfigure(encoding='utf-8')
master = {}
for l in open('work/text/master.tsv', encoding='utf-8'):
    if l[0] != '#': c = l.rstrip('\n').split('\t'); master[c[0]] = c
ko = {}
for fn in glob.glob('my files/번역/*.tsv'):
    for l in open(fn, encoding='utf-8'):
        if l[0] == '#' or not l.strip(): continue
        c = l.rstrip('\r\n').split('\t'); ko[c[0]] = c[5]
J = '軍事演習 スペイン内乱 ポーランド電撃戦 北欧侵攻 西方電撃戦 バトル・オブ・ブリテン バルカン半島 東部戦線 東部戦線　開幕 モスクワ戦 東部戦線　第二幕 スターリングラード救出作戦 東部戦線　第三幕 クルスク大戦車戦 東部戦線の崩壊 第三帝国の滅亡 北アフリカ戦線 エル・アラメインの死闘 アメリカ参戦 イタリア戦線 史上最大の作戦 西部戦線 バルジの戦い アシカ作戦 中東 ウラル アメリカ戦線 ボルシェビキの終焉 プロレタリア革命 機数 索敵 換装費 視認 射数 兵員 未対応 表類 戦績 特殊装備 月齢 降雨率 全自動 ルール 地形 高度 路線 制限 占領 地名 予算報告 改良前 進化後 哨戒機 牽引砲 総兵力 輸送車 対空砲 要塞 非甲 対甲'.split()
for j in J:
    h = [ko[k] for k, m in master.items() if m[4] == j or m[4] == '【%s】' % j]
    print(j, '→', sorted(set(h))[:4])
for t in ('처칠', '수상', '총리'):
    pass
print([ (k, ko[k][:30]) for k,m in master.items() if 'ヨードル' in m[4] or 'ジューコフ' in m[4] or 'ホー・チ' in m[4] or 'フリーデブルク' in m[4]][:6])
print([ (k, ko[k][:30]) for k,m in master.items() if m[4] in ('毛沢東','蒋介石') or 'チャーチル首相' in m[4]][:6])
