# -*- coding: utf-8 -*-
"""번역 세부 검토(읽기 전용).  python tools/ko_review.py"""
import sys, os, re, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_extract as ie, extract as X, build as Bd
from ko_audit import nbytes
from gdi import Disc
sys.stdout.reconfigure(encoding='utf-8')
D = Disc(1); ie.D = D
w = {x[0]: x for x in ie.walk() if not x[3] & 2}
e = D.read(*w['/1ST_READ.BIN'][1:3])
master = {}; pos = {}
for l in open('work/text/master.tsv', encoding='utf-8'):
    if l[0] != '#': c = l.rstrip('\n').split('\t'); master[c[0]] = c
for l in open('work/text/master_pos.tsv', encoding='utf-8'):
    c = l.rstrip('\n').split('\t'); pos[c[0]] = c[2].split()
ko = {}
for fn in glob.glob('my files/번역/*.tsv'):
    for l in open(fn, encoding='utf-8'):
        if l[0] == '#' or not l.strip(): continue
        c = l.rstrip('\r\n').split('\t'); ko[c[0]] = c[5]
ptr = collections.defaultdict(list)
for o in range(0, len(e) - 3):
    if e[o + 3] == 0x8C:
        v = struct.unpack_from('<I', e, o)[0]
        if X.B <= v < X.B + len(e): ptr[v - X.B].append(o)
slots = {}
for k, m in master.items():
    if m[1] == 'M':
        for p in pos[k]: slots[int(p, 16)] = (int(m[2]), k)
S = sorted(slots)
print('== 위험: 문자열 뒤에 다른 자료가 붙은 자리(옮기면 표 전체가 어긋날 수 있음)')
glue = []
for i, p in enumerate(S):
    L, k = slots[p]; nx = S[i + 1] if i + 1 < len(S) else p + L + 1
    g = e[p + L:nx]
    if g.strip(b'\0'): glue.append((hex(p), k, master[k][4][:16], ko[k][:14], g[:20].hex()))
print(len(glue)); print(glue[:12])
print('== 속 포인터·비정렬')
for i, p in enumerate(S):
    L, k = slots[p]
    for q in range(p + 1, p + L):
        if q in ptr: print(hex(p), k, master[k][4][:30], '속', q - p, [hex(x) for x in ptr[q]])
    for o in ptr[p]:
        if o % 4: print('비정렬', hex(p), k, master[k][4][:24], hex(o))
print('== 이상해 보이는 M(원문과 번역이 같거나 반각·기호 위주)')
sus = [(k, m[4][:20], ko[k][:20]) for k, m in master.items() if m[1] == 'M' and (ko[k] == m[4] or not re.search('[가-힣]', ko[k]))]
print(len(sus), sus[:50])
print('== 한자·가나 남음')
K = re.compile('[ぁ-んァ-ヶｦ-ﾟ一-龥々]')
print([(k, master[k][1], ko[k][:30]) for k in ko if K.search(ko[k])])
print('== 줄 폭 초과 M, 괄호')
a = open('work/text/audit.txt', encoding='utf-8').read().split('== ')
for s in a:
    if s.startswith(('줄 폭 초과', '원문 괄호')): print(s[:1600])
T = {'司令部': '사령부', '首都': '수도', '歩兵': '보병', '軍事費': '군사비', '索敵': '색적', '機数': '기수', '燃料': '연료', '経験値': '경험치', '補給': '보급', '占領': '점령', '爆撃': '폭격', '戦闘機': '전투기',
     'ヘックス': '헥스', 'ユニット': '유닛', '師団': '사단', '軍団': '군단', '小隊': '소대', '中隊': '중대', '大隊': '대대', '進化': '진화', '改良': '개량', '生産': '생산', '開発': '개발', '参謀': '참모', '換装': '환장',
     '視認': '시야', '射程': '사정', '揚陸': '양륙', '搭載': '탑재', '空港': '공항', '都市': '도시', '戦車': '전차', '軍事演習': '군사 연습', 'キャンペーン': '캠페인', 'シナリオ': '시나리오', '東部戦線': '동부 전선',
     'ヴェルサイユ': '베르사유', 'ヒンデンブルク': '힌덴부르크', 'スターリン': '스탈린', 'チャーチル': '처칠', 'ルーズベルト': '루스벨트', 'ヒトラー': '히틀러', 'ソ連': '소련', '首相': '총리', '大統領': '대통령', '枢軸': '추축'}
print('== 용어')
for j, t in T.items():
    use = [k for k, m in master.items() if j in m[4]]
    miss = [k for k in use if t not in ko[k].replace(' ', '') and t.replace(' ', '') not in ko[k].replace(' ', '')]
    if miss: print(j, t, len(use), '다름', len(miss), [(k, ko[k][:18]) for k in miss[:5]])
