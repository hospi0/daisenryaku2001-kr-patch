# -*- coding: utf-8 -*-
"""BIOS 훅 기계어 검산: 역어셈 + 작은 시뮬레이터로 한글·비한글 입력 확인(읽기 전용).  python tools/hook_check.py"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sh4dis, build as Bd
sys.stdout.reconfigure(encoding='utf-8')
N = 1120; T = 0x4428C
w = [0x4F22, 0xD009, 0x400B, 0x0009, 0x4F26, 0xD108, 0x6203, 0x3218, 0xD107, 0x3212, 0x8906, 0xD107, 0x6112, 0xD307, 0x313C, 0x312C, 0x31B8, 0x6013, 0x000B, 0x0009]
code = b''.join(struct.pack('<H', x) for x in w) + struct.pack('<5I', Bd.BIOS_OFS_FN, Bd.BIOS_KANJI0, N * 72, Bd.FONT_VAR, T)
for l in sh4dis.dis(0, 20, code): print(l[:60])
S = 0x8C0C77CC; FONT = 0x8CD418C0; BIOS = 0xA0100020


def run(off):
    r = [0] * 16; r[11] = BIOS; pc = 0; t = 0; delay = None; steps = 0
    mem = {Bd.FONT_VAR: FONT}
    while steps < 60:
        steps += 1
        op = struct.unpack_from('<H', code, pc)[0]; nx = pc + 2
        a, n, m, d = op >> 12, op >> 8 & 15, op >> 4 & 15, op & 15
        if op == 0x4F22 or op == 0x4F26 or op == 0x0009: pass
        elif a == 0xD:
            r[n] = struct.unpack_from('<I', code, ((pc & ~3) + 4) + (op & 255) * 4)[0]
        elif op == 0x400B:
            assert r[0] == Bd.BIOS_OFS_FN; r[0] = off; nx = pc + 4      # 지연 슬롯 NOP 건너뜀
        elif a == 6 and d == 3: r[n] = r[m]
        elif a == 6 and d == 2: r[n] = mem[r[m]]
        elif a == 3 and d == 8: r[n] = (r[n] - r[m]) & 0xFFFFFFFF
        elif a == 3 and d == 12: r[n] = (r[n] + r[m]) & 0xFFFFFFFF
        elif a == 3 and d == 2: t = r[n] >= r[m]
        elif op >> 8 == 0x89:
            if t: nx = pc + 4 + (op & 255) * 2
        elif op == 0x000B: return r[0]
        else: raise SystemExit('모르는 명령 %04X' % op)
        pc = nx
    raise SystemExit('무한 반복')


for name, off in (('한글 첫 칸', 0xE190), ('한글 끝 칸', 0xE190 + (N - 1) * 72), ('한글 바로 뒤', 0xE190 + N * 72), ('기호(앞)', 0x2880), ('반각', 0x24)):
    r0 = run(off); read = (BIOS + r0) & 0xFFFFFFFF
    print(name, hex(off), '→ 읽는 주소', hex(read), '표' if FONT + T <= read < FONT + T + N * 72 else 'BIOS 그대로' if r0 == off else '⛔')
print('마지막 표 끝', hex(T + N * 72), '글꼴 크기', hex(702720))
