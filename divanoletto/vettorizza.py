# -*- coding: utf-8 -*-
"""
Vettorializza foto_divanoletto.png in DXF (R12) ricalcando TUTTE le linee,
con contorni LISCI e PRECISI (no scaletta):
  - sovracampionamento bicubico (SUPER x)
  - marching squares con INTERPOLAZIONE sub-pixel sul grigio
  - concatenamento segmenti -> polilinee
  - Douglas-Peucker (semplificazione che mantiene gli spigoli netti)
Solo PIL. Genera anche un'anteprima PNG ad alta risoluzione.
"""
import os, math
from collections import defaultdict
from PIL import Image

HERE   = os.path.dirname(os.path.abspath(__file__))
SRC    = os.path.join(HERE, "foto_divanoletto.png")
DXFOUT = os.path.join(HERE, "divano_letto_ricalco_v3.dxf")
PNGOUT = os.path.join(HERE, "ricalco_anteprima_v3.png")

SUPER  = 4        # fattore di sovracampionamento (bicubico) - linee piu' morbide
ISO    = 160.0    # livello di soglia (grigio) per il contorno
EPS    = 1.5      # tolleranza Douglas-Peucker, in pixel sovracampionati
MINLEN = 6.0      # scarta polilinee piu' corte (px sovracamp.) = puntini
SCALE  = 0.3876   # cm per pixel ORIGINALE - CALIBRATO sulle quote misurate
                  # (57->147px, 200->517px, 86->221px, 41->105px = 0.387-0.390)
LAYER  = "RICALCO"

# ---------------- 1) immagine: grigio + sovracampionamento ----------------
img = Image.open(SRC).convert("L")
W0, H0 = img.size
img = img.resize((W0 * SUPER, H0 * SUPER), Image.BICUBIC)
W, H = img.size
data = list(img.getdata())
print("Sorgente %dx%d -> sovracamp. %dx%d (x%d)" % (W0, H0, W, H, SUPER))

def cross(va, vb):
    d = vb - va
    if d == 0:
        return 0.5
    t = (ISO - va) / d
    return 0.0 if t < 0 else (1.0 if t > 1 else t)

# ---------------- 2) marching squares INTERPOLATO ----------------
segs = []
ap = segs.append
for y in range(H - 1):
    base = y * W; base1 = base + W
    for x in range(W - 1):
        vtl = data[base + x]; vtr = data[base + x + 1]
        vbl = data[base1 + x]; vbr = data[base1 + x + 1]
        itl = vtl < ISO; itr = vtr < ISO; ibl = vbl < ISO; ibr = vbr < ISO
        s = itl + itr + ibl + ibr
        if s == 0 or s == 4:
            continue
        pT = pR = pB = pL = None
        if itl != itr: pT = (x + cross(vtl, vtr), y)
        if itr != ibr: pR = (x + 1.0, y + cross(vtr, vbr))
        if ibl != ibr: pB = (x + cross(vbl, vbr), y + 1.0)
        if itl != ibl: pL = (x, y + cross(vtl, vbl))
        pres = [p for p in (pT, pR, pB, pL) if p is not None]
        if len(pres) == 2:
            ap((pres[0], pres[1]))
        else:  # saddle (4 punti)
            if itl:
                ap((pT, pL)); ap((pR, pB))
            else:
                ap((pT, pR)); ap((pB, pL))
print("Segmenti:", len(segs))

# ---------------- 3) concatenamento in polilinee ----------------
def key(p):
    return (round(p[0], 3), round(p[1], 3))

adj = defaultdict(list)
for i, (a, b) in enumerate(segs):
    adj[key(a)].append((i, b))
    adj[key(b)].append((i, a))

used = bytearray(len(segs))
polys = []
for i0 in range(len(segs)):
    if used[i0]:
        continue
    a, b = segs[i0]; used[i0] = 1
    pts = [a, b]
    cur = b
    while True:
        nxt = None
        for (j, other) in adj[key(cur)]:
            if not used[j]:
                nxt = (j, other); break
        if nxt is None:
            break
        used[nxt[0]] = 1; pts.append(nxt[1]); cur = nxt[1]
    cur = a
    while True:
        nxt = None
        for (j, other) in adj[key(cur)]:
            if not used[j]:
                nxt = (j, other); break
        if nxt is None:
            break
        used[nxt[0]] = 1; pts.insert(0, nxt[1]); cur = nxt[1]
    polys.append(pts)
print("Polilinee grezze:", len(polys))

# ---------------- 4) Douglas-Peucker ----------------
def rdp(P, eps):
    n = len(P)
    if n < 3:
        return P[:]
    keep = bytearray(n); keep[0] = keep[-1] = 1
    st = [(0, n - 1)]
    while st:
        i, j = st.pop()
        ax, ay = P[i]; bx, by = P[j]
        dx = bx - ax; dy = by - ay; d2 = dx * dx + dy * dy
        dmax = 0.0; idx = -1
        for k in range(i + 1, j):
            px, py = P[k]
            if d2 == 0:
                dist = math.hypot(px - ax, py - ay)
            else:
                t = ((px - ax) * dx + (py - ay) * dy) / d2
                dist = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
            if dist > dmax:
                dmax = dist; idx = k
        if idx != -1 and dmax > eps:
            keep[idx] = 1; st.append((i, idx)); st.append((idx, j))
    return [P[k] for k in range(n) if keep[k]]

def plen(P):
    return sum(math.hypot(P[i+1][0]-P[i][0], P[i+1][1]-P[i][1]) for i in range(len(P)-1))

clean = []
for p in polys:
    closed = key(p[0]) == key(p[-1]) and len(p) > 3
    sp = rdp(p, EPS)
    if len(sp) < 2 or plen(sp) < MINLEN:
        continue
    if closed and key(sp[0]) == key(sp[-1]):
        clean.append((sp[:-1], True))
    else:
        clean.append((sp, False))
print("Polilinee finali:", len(clean), " vertici:", sum(len(p) for p, _ in clean))

# ---------------- 5) DXF R12 ----------------
buf = []
def g(c, v): buf.append(str(c)); buf.append(str(v))
def fn(x): return "%.4f" % x
def tx(x, y): return ((x / SUPER) * SCALE, ((H - y) / SUPER) * SCALE)

for pts, closed in clean:
    g(0, "POLYLINE"); g(8, LAYER); g(66, 1); g(70, 1 if closed else 0)
    g(10, "0.0"); g(20, "0.0"); g(30, "0.0")
    for (x, y) in pts:
        X, Y = tx(x, y)
        g(0, "VERTEX"); g(8, LAYER); g(10, fn(X)); g(20, fn(Y)); g(30, "0.0")
    g(0, "SEQEND")

minx, miny = tx(0, H); maxx, maxy = tx(W, 0)
PREFIX = (
    "0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1009\n9\n$INSUNITS\n70\n5\n"
    "9\n$EXTMIN\n10\n%s\n20\n%s\n30\n0.0\n9\n$EXTMAX\n10\n%s\n20\n%s\n30\n0.0\n0\nENDSEC\n"
    "0\nSECTION\n2\nTABLES\n"
    "0\nTABLE\n2\nLTYPE\n70\n1\n0\nLTYPE\n2\nCONTINUOUS\n70\n0\n3\nSolid line\n72\n65\n73\n0\n40\n0.0\n0\nENDTAB\n"
    "0\nTABLE\n2\nLAYER\n70\n2\n0\nLAYER\n2\n0\n70\n0\n62\n7\n6\nCONTINUOUS\n"
    "0\nLAYER\n2\n%s\n70\n0\n62\n7\n6\nCONTINUOUS\n0\nENDTAB\n0\nENDSEC\n"
    "0\nSECTION\n2\nENTITIES\n"
) % (fn(minx), fn(miny), fn(maxx), fn(maxy), LAYER)
with open(DXFOUT, "w", encoding="ascii") as fh:
    fh.write(PREFIX + "\n".join(buf) + "\n0\nENDSEC\n0\nEOF\n")
print("DXF:", DXFOUT)

# ---------------- 6) anteprima PNG ----------------
from PIL import ImageDraw
prev = Image.new("RGB", (W0 * 2, H0 * 2), "white")
d = ImageDraw.Draw(prev)
k = 2.0 / SUPER
for pts, closed in clean:
    seq = pts + [pts[0]] if closed else pts
    d.line([(x * k, y * k) for (x, y) in seq], fill=(0, 0, 0), width=1)
prev.save(PNGOUT)
print("PNG:", PNGOUT)
