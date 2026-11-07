# -*- coding: utf-8 -*-
"""S18RM04P.DAT: JIS 순서 (구-0x21)*94+(점-0x21), 칸 90 B, 2bpp(바이트 위 비트부터 4화소). 코드 0x8C014BA2 실측."""
import numpy as np
CELL = 90
def idx(ch):
    b = ch.encode('euc_jp'); return (b[0] - 0xA1) * 94 + (b[1] - 0xA1)
def dec(d, i, w=20, h=18):
    r = np.frombuffer(d[i * CELL:(i + 1) * CELL], np.uint8)
    p = np.stack([r >> 6 & 3, r >> 4 & 3, r >> 2 & 3, r & 3], 1).reshape(-1)
    return p[:w * h].reshape(h, w)
