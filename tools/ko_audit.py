# -*- coding: utf-8 -*-
"""번역 TSV 전수 검사(읽기 전용, 고치지 않음).  python tools/ko_audit.py [폴더] → work/text/audit.txt"""
import sys, os, re, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as Bd
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join('my files', '번역')
LIM = {'T': 24, 'P': 21}
KANA = re.compile('[ぁ-んァ-ヶｦ-ﾟ一-龥々]')
TOK = re.compile(r'%[-+0 #]*\d*(?:\.\d+)?[a-zA-Z%]')


def nbytes(t):
    n = 0
    for c in t:
        if '가' <= c <= '힣': n += 2
        else:
            try: n += len(c.encode('cp932'))
            except UnicodeEncodeError: n += 2
    return n


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    master = {}
    for l in open('work/text/master.tsv', encoding='utf-8'):
        if l[0] != '#':
            c = l.rstrip('\n').split('\t'); master[c[0]] = c
    rows = {}; P = collections.defaultdict(list)
    for fn in sorted(glob.glob(os.path.join(SRC, '*.tsv'))):
        b = open(fn, 'rb').read()
        if b[:3] == b'\xef\xbb\xbf': P['BOM'].append(os.path.basename(fn))
        for ln, l in enumerate(b.decode('utf-8', 'replace').splitlines(), 1):
            if not l or l[0] == '#': continue
            c = l.split('\t'); k = c[0].strip()
            if len(c) != 6: P['열 수'].append((os.path.basename(fn), ln, len(c), l[:50]));
            if k in rows: P['번호 겹침'].append((k, os.path.basename(fn)))
            rows[k] = (os.path.basename(fn), c)
    miss = [k for k in master if k not in rows]; extra = [k for k in rows if k not in master]
    print('원본', len(master), '받음', len(rows), '빠진 번호', len(miss), miss[:10], '없는 번호', extra[:10])
    stat = collections.Counter(); kos = {}
    for k, (fn, c) in rows.items():
        if k not in master: continue
        m = master[k]; kind = m[1]; jp = m[4]; ko = c[5] if len(c) > 5 else ''
        if len(c) > 4 and c[4] != jp: P['원문 바뀜'].append((k, fn, jp[:30], c[4][:30]))
        if not ko.strip(): P['빈칸'].append((k, kind, jp[:30])); continue
        stat[kind] += 1; kos[k] = ko
        v = Bd.tidy(Bd.unesc(ko)); j = Bd.unesc(jp)
        if sorted(TOK.findall(j)) != sorted(TOK.findall(v)): P['서식'].append((k, kind, jp[:34], ko[:34]))
        if KANA.search(v): P['일본어·한자 남음'].append((k, kind, ko[:44]))
        bad = sorted({ch for ch in v if not ('가' <= ch <= '힣') and ord(ch) >= 128 and not _ok(ch)})
        if bad: P['글꼴에 없는 글자'].append((k, kind, ''.join(bad), ko[:30]))
        if any(0x3131 <= ord(ch) <= 0x318E for ch in v): P['낱자모'].append((k, ko[:30]))
        if kind != 'S':
            if j.count('\n') != v.count('\n'): P['줄바꿈 수'].append((k, kind, j.count('\n'), v.count('\n'), ko[:40]))
        bud = LIM.get(kind) or int(m[2])
        n = nbytes(v)
        if bud and n > bud: P['예산 초과 ' + kind].append((k, n, bud, jp[:22], ko[:30]))
        if kind == 'M' and '\n' in j:
            wj = max(nbytes(x) for x in re.split('\r?\n', j)); wv = max(nbytes(x) for x in re.split('\r?\n', v))
            if wv > wj: P['줄 폭 초과 M'].append((k, wv, wj, ko[:40]))
        if kind == 'S':
            cm = {}
            lines = wrapped(v)
            if n > 1000: P['S 1000 B 초과'].append((k, n))
            P['_S줄'].append(len(lines))
        for a, b in (('「', '」'), ('『', '』')):
            if v.count(a) != v.count(b): P['괄호 짝'].append((k, ko[:40]))
            if j.count(a) != v.count(a): P['원문 괄호 수 다름'].append((k, jp[:24], ko[:24]))
    print('구분별', stat.most_common())
    out = open('work/text/audit.txt', 'w', encoding='utf-8')
    for k, v in sorted(P.items()):
        if k == '_S줄':
            print('S 줄 수 분포', sorted(collections.Counter(v).items())[-8:]); continue
        print(k, len(v), v[:5]); out.write('== %s %d\n' % (k, len(v)))
        for x in v: out.write(repr(x) + '\n')
    return master, kos


def wrapped(v):
    ls = []
    for p in v.split('\r\n'):
        cur = 0; n = 1
        for w in re.split('( )', p):
            b = nbytes(w)
            if cur + b > 44: n += 1; cur = 0
            cur += b
        ls += [0] * n
    return ls


def _ok(ch):
    try: ch.encode('cp932'); return True
    except UnicodeEncodeError: return False


if __name__ == '__main__':
    main()
