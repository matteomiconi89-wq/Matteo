# -*- coding: utf-8 -*-
"""Diagnostico: misura in pixel gli spani delle quote per calibrare la scala
di ciascuna vista. Le linee di estensione delle quote sono tratti lunghi
(verticali per quote orizzontali, orizzontali per quote verticali): si
individuano come 'picchi' nelle proiezioni dell'inchiostro su bande mirate."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
img = Image.open(os.path.join(HERE, "foto_divanoletto.png")).convert("L")
W, H = img.size
d = list(img.getdata())
INK = 160
def ink(x, y): return d[y * W + x] < INK

# proiezione colonne (totale) per trovare il vuoto tra le due viste
col = [sum(1 for y in range(H) if ink(x, y)) for x in range(W)]
# vuoto centrale
mid_lo, mid_hi = int(W * 0.33), int(W * 0.66)
best = None; run = None
for x in range(mid_lo, mid_hi):
    if col[x] == 0:
        if run is None: run = [x, x]
        else: run[1] = x
    else:
        if run and (best is None or (run[1]-run[0]) > (best[1]-best[0])): best = run
        run = None
if run and (best is None or (run[1]-run[0]) > (best[1]-best[0])): best = run
gap = (best[0]+best[1])//2 if best else W//2
print("Gap tra viste ~ x=%d (vuoto %s)" % (gap, best))

def band_cols(x0, x1, y0, y1, thr):
    """colonne in [x0,x1) con conteggio inchiostro >= thr nella banda righe [y0,y1)"""
    res = []
    for x in range(x0, x1):
        c = sum(1 for y in range(y0, y1) if ink(x, y))
        if c >= thr: res.append((x, c))
    return res

def band_rows(x0, x1, y0, y1, thr):
    res = []
    for y in range(y0, y1):
        c = sum(1 for x in range(x0, x1) if ink(x, y))
        if c >= thr: res.append((y, c))
    return res

def span(items):
    if not items: return None
    xs = [a for a, _ in items]
    return min(xs), max(xs), max(xs) - min(xs)

topH = int(H * 0.32)        # banda alta (linee di quota orizzontali in cima)
botY0 = int(H * 0.78)       # banda bassa (quota 86)

print("\n== VISTA SX (divano chiuso) [0,%d) ==" % gap)
ext = band_cols(0, gap, 0, topH, 6)
print(" estens. orizz. '57' (top): ", span(ext), "colonne:", [x for x, _ in ext][:40])
rcol = band_cols(int(gap*0.72), gap, 0, H, 12)
print(" possibili vert. dx (quota 35) col-spike:", [x for x, _ in rcol])

print("\n== VISTA DX (letto aperto) [%d,%d) ==" % (gap, W))
ext2 = band_cols(gap, W, 0, topH, 6)
print(" estens. orizz. '200' (top): ", span(ext2), "colonne:", [x for x, _ in ext2][:60])
bot = band_cols(gap, W, botY0, H, 5)
print(" estens. orizz. '86' (bottom):", span(bot), "colonne:", [x for x, _ in bot][:60])

# righe estreme inchiostro (per pavimento / altezza)
for name, x0, x1 in [("SX", 0, gap), ("DX", gap, W)]:
    rows = [y for y in range(H) if any(ink(x, y) for x in range(x0, x1))]
    print(" %s: y_inchiostro min=%d max=%d" % (name, min(rows), max(rows)))
