# -*- coding: utf-8 -*-
"""Misura mirata: linee di quota orizzontali (run orizzontale piu' alto) e
verticali (run verticale piu' a destra) per ciascuna vista, per ricavare le
scale e capire se le due viste sono alla stessa scala."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
img = Image.open(os.path.join(HERE, "foto_divanoletto.png")).convert("L")
W, H = img.size
d = list(img.getdata())
INK = 160
def ink(x, y): return d[y * W + x] < INK
GAP = 464

def hrun(y, x0, x1):
    best = 0; cur = 0; bs = be = 0; cs = x0
    for x in range(x0, x1):
        if ink(x, y):
            if cur == 0: cs = x
            cur += 1
            if cur > best: best = cur; bs = cs; be = x
        else:
            cur = 0
    return best, bs, be

def vrun(x, y0, y1):
    best = 0; cur = 0; bs = be = 0; cs = y0
    for y in range(y0, y1):
        if ink(x, y):
            if cur == 0: cs = y
            cur += 1
            if cur > best: best = cur; bs = cs; be = y
        else:
            cur = 0
    return best, bs, be

def top_hline(x0, x1):
    for y in range(H):
        b, s, e = hrun(y, x0, x1)
        if b > 60:
            return y, s, e, b
    return None

def rightmost_vline(x0, x1, minlen):
    for x in range(x1 - 1, x0 - 1, -1):
        b, s, e = vrun(x, 0, H)
        if b > minlen:
            return x, s, e, b
    return None

def floor_row(x0, x1):
    bestrow = None; bestlen = 0
    for y in range(int(H * 0.5), H):
        b, _, _ = hrun(y, x0, x1)
        if b > bestlen: bestlen = b; bestrow = y
    return bestrow, bestlen

print("== VISTA SX (divano) ==")
t = top_hline(0, GAP)
print(" linea quota top (57): row=%d  x=%d..%d  span=%d px -> 57/span=%.4f cm/px" %
      (t[0], t[1], t[2], t[2]-t[1], 57.0/(t[2]-t[1])))
v = rightmost_vline(int(GAP*0.6), GAP, 75)
print(" linea quota vert. dx (35): x=%d  y=%d..%d  span=%d px -> 35/span=%.4f cm/px" %
      (v[0], v[1], v[2], v[2]-v[1], 35.0/(v[2]-v[1])))
fr = floor_row(0, GAP)
print(" pavimento ~ row=%d (run %d px)" % fr)

print("\n== VISTA DX (letto) ==")
t2 = top_hline(GAP, W)
print(" linea quota top (200): row=%d  x=%d..%d  span=%d px -> 200/span=%.4f cm/px" %
      (t2[0], t2[1], t2[2], t2[2]-t2[1], 200.0/(t2[2]-t2[1])))
v2 = rightmost_vline(int(GAP + (W-GAP)*0.6), W, 75)
print(" linea quota vert. dx (41): x=%d  y=%d..%d  span=%d px -> 41/span=%.4f cm/px" %
      (v2[0], v2[1], v2[2], v2[2]-v2[1], 41.0/(v2[2]-v2[1])))
fr2 = floor_row(GAP, W)
print(" pavimento ~ row=%d (run %d px)" % fr2)
