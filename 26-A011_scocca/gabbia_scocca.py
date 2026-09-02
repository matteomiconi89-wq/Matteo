#!/usr/bin/env python3
"""Gabbia in pixel per il brief a Manus — vista madre dell'interno scocca 26A011 aperta.

Prospettiva centrale reale (pinhole) calcolata dalla geometria DXF:
camera a X=1.000, Y=2.420 (asse corridoio), occhio a +1.600 dal pavimento (Z 2.995),
FOV orizzontale 72° (~24 mm FF), frame 2400×1350, punto di fuga al centro esatto.
Il disegno resta pulito: l'elenco completo delle quote sta nel brief, non sull'immagine.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import math

FW, FH = 2400, 1350
CAM = (1000.0, 2420.0, 2995.0)          # X, Y, Z camera (Z = pav.1395 + occhio 1600)
F = (FW / 2) / math.tan(math.radians(72) / 2)   # 1651.6 px

def P(x, y, z):
    d = x - CAM[0]
    return (FW / 2 + F * (y - CAM[1]) / d, FH / 2 - F * (z - CAM[2]) / d)

fig = plt.figure(figsize=(16, 9), dpi=150)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, FW); ax.set_ylim(FH, 0); ax.set_aspect("equal")
ax.set_facecolor("#fcfbf9")
ax.add_patch(plt.Rectangle((0, 0), FW, FH, fill=False, ec="#222", lw=2.5))

BLU = "#1f3a5f"; OCRA = "#a2701c"; GRIGIO = "#8d8779"; TEAL = "#2c6e63"

def linea(p1, p2, color=BLU, lw=1.6, ls="-", z=3):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, lw=lw, ls=ls,
            solid_capstyle="round", zorder=z)

def spigolo_x(x0, x1, y, z, **kw):
    linea(P(x0, y, z), P(x1, y, z), **kw)

NEAR = 1601.0          # piano di clip vicino (subito oltre la camera)
DIV = 10199.0          # divisorio che chiude il corridoio in questa vista
FINE = 13510.0         # fine baie (testata estrattori)
PAV, SOFF = 1395.0, 3646.0
BAIA_SX, BAIA_DX = 61.0, 4779.0            # fili esterni baie
COR_SX, COR_DX = 1213.0, 3603.0            # fili corridoio
SOF_BAIA_INT, SOF_BAIA_EST = 3546.0, 3498.0
DAV, TESTA = 2395.0, 3042.0                # fascia vetrata

# --- pavimento: fughe guida ogni metro (ritmo di profondità) ---
for x in range(2000, 13001, 1000):
    linea(P(x, BAIA_SX, PAV), P(x, BAIA_DX, PAV), color="#dcd7cb", lw=.9, z=1)

# --- corridoio centrale ---
for y in (COR_SX, COR_DX):
    spigolo_x(NEAR, DIV, y, PAV, lw=2.2)                   # attacco pavimento
    spigolo_x(NEAR, DIV, y, SOFF, lw=2.2)                  # attacco controsoffitto
    for x0 in (3915.0,):                                   # pilastri fissi 3915-4302
        for xx in (x0, 4302.0):
            linea(P(xx, y, PAV), P(xx, y, SOFF), color=GRIGIO, lw=1.2, z=2)
# divisorio di fondo (X 10.199): parete piena del corridoio
c1, c2 = P(DIV, COR_SX, PAV), P(DIV, COR_DX, PAV)
c3, c4 = P(DIV, COR_DX, SOFF), P(DIV, COR_SX, SOFF)
ax.add_patch(plt.Polygon([c1, c2, c3, c4], fc="#eeeae1", ec=BLU, lw=2, zorder=2))

# --- baie: soffitti inclinati e pareti esterne ---
for y_est, y_int in ((BAIA_SX, COR_SX), (BAIA_DX, COR_DX)):
    spigolo_x(NEAR, FINE, y_est, PAV, lw=2.2)              # attacco pavimento parete esterna
    spigolo_x(NEAR, FINE, y_est, SOF_BAIA_EST, lw=1.8)     # soffitto baia al filo esterno
    spigolo_x(NEAR, FINE, y_int, SOF_BAIA_INT, lw=1.4)     # gradino di soffitto al filo corridoio
    spigolo_x(NEAR, FINE, y_est, DAV, color=OCRA, lw=2.2)  # davanzale +1.000
    spigolo_x(NEAR, FINE, y_est, TESTA, color=OCRA, lw=1.6)  # testa vetro +1.647
# testate di fondo baie
for y_est, y_int in ((BAIA_SX, COR_SX), (BAIA_DX, COR_DX)):
    linea(P(FINE, y_est, PAV), P(FINE, y_est, SOF_BAIA_EST), color=GRIGIO, lw=1.2)
# divisori nelle baie (ingresso X 9.401, cucina X 8.323)
for x, ya, yb in ((9421.0, BAIA_SX, COR_SX), (8323.0, COR_DX, BAIA_DX)):
    p1, p2 = P(x, ya, PAV), P(x, yb, PAV)
    p3, p4 = P(x, yb, SOF_BAIA_INT), P(x, ya, SOF_BAIA_EST)
    ax.add_patch(plt.Polygon([p1, p2, p3, p4], fc="none", ec=TEAL, lw=1.6,
                             ls=(0, (5, 3)), zorder=3))

# --- oblò sul controsoffitto (5, corsia centrale) ---
for x0, x1, y0, y1 in ((1318,1968,2120,2720),(4921,5701,2120,2720),
                       (6303,7595,2095,2745),(8287,9027,2120,2720)):
    if x0 < NEAR + 60: continue
    pts = [P(x0, y0, SOFF), P(x1, y0, SOFF), P(x1, y1, SOFF), P(x0, y1, SOFF)]
    ax.add_patch(plt.Polygon(pts, fc="#f5efdd", ec=OCRA, lw=1.3, zorder=2))

# --- sagoma persona 1.750 a metà scocca (solo scala, nel brief: NON renderizzarla) ---
hx, hw = 7000.0, 210.0
corpo = [P(hx, 2420 - hw, PAV), P(hx, 2420 + hw, PAV),
         P(hx, 2420 + hw, PAV + 1440), P(hx, 2420 - hw, PAV + 1440)]
ax.add_patch(plt.Polygon(corpo, fc="#c9c1b0", ec=GRIGIO, lw=1.2, zorder=4))
p_testa = P(hx, 2420, PAV + 1630)
r_testa = F * 115 / (hx - CAM[0])
ax.add_patch(plt.Circle(p_testa, r_testa, fc="#c9c1b0", ec=GRIGIO, lw=1.2, zorder=4))

# --- punto di fuga + terzi ---
ax.plot(FW/2, FH/2, marker="+", color=OCRA, ms=18, mew=2.2, zorder=6)
for f in (1/3, 2/3):
    ax.axvline(FW*f, color="#e0dcd4", lw=1, ls="--", zorder=0)
    ax.axhline(FH*f, color="#e0dcd4", lw=1, ls="--", zorder=0)

# --- annotazioni (poche: il resto sta nel brief) ---
def nota(txt, xy, xytext, color=BLU):
    ax.annotate(txt, xy=xy, xytext=xytext, fontsize=10, color=color, va="center",
                weight="bold", arrowprops=dict(arrowstyle="->", color=color, lw=1.5),
                zorder=7)

m = P(5200, BAIA_SX, DAV)
nota("DAVANZALE VETRINE +1.000\n(testa vetro +1.647)", m, (m[0]+130, m[1]+240), OCRA)
m = P(6500, COR_SX, SOF_BAIA_INT)
nota("GRADINO DI SOFFITTO\ncorridoio 2.251 → baia 2.151→2.103", m, (m[0]-560, m[1]-190))
m = ((c1[0]+c2[0])/2, (c2[1]+c3[1])/2 - 60)
nota("DIVISORIO a 9,2 m\n(fondo vista)", m, (m[0]+300, m[1]-150))
m = P(5311, 2420, SOFF)
nota("OBLÒ in corsia centrale\n(4 in vista, il 5° oltre il divisorio)", m, (m[0]+430, m[1]-130), OCRA)
m = P(7000, 2420 + 190, PAV + 700)
nota("persona 1.750 = 481 px\n(solo scala: NON renderizzare)", m, (m[0]+300, m[1]+190), GRIGIO)

# quote pixel del varco corridoio a X = 6.000 (5 m dalla camera)
xg = 6000.0
g_sx, g_dx = P(xg, COR_SX, PAV), P(xg, COR_DX, PAV)
g_su = P(xg, COR_SX, SOFF)
yq = g_sx[1] + 36
ax.annotate("", xy=(g_sx[0], yq), xytext=(g_dx[0], yq),
            arrowprops=dict(arrowstyle="<->", color=BLU, lw=1.6))
ax.text((g_sx[0]+g_dx[0])/2, yq + 34, "corridoio 2.390 = %d px  (a X=6.000)" % round(g_dx[0]-g_sx[0]),
        ha="center", fontsize=11, color=BLU, weight="bold")
xq = g_sx[0] - 40
ax.annotate("", xy=(xq, g_su[1]), xytext=(xq, g_sx[1]),
            arrowprops=dict(arrowstyle="<->", color=BLU, lw=1.6))
ax.text(xq - 16, (g_su[1]+g_sx[1])/2, "soffitto 2.251 = %d px" % round(g_sx[1]-g_su[1]),
        ha="right", fontsize=10, color=BLU, va="center")

ax.text(28, 44, "GABBIA DI INQUADRATURA — interno scocca 26A011 aperta (vista madre)",
        fontsize=15, weight="bold", color=BLU, va="top")
ax.text(28, 88, "frame 2400×1350 · camera X 1.000 / Y 2.420 / occhio +1.600 · FOV orizz. 72° (~24 mm FF) · "
                "punto di fuga ESATTO al centro (1200, 675) · rapporto soffitto/corridoio 0,94",
        fontsize=9.5, color="#5a5348", va="top")
ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values():
    s.set_visible(False)
fig.savefig("gabbia_pixel_scocca.png", facecolor="white")
print("scritto gabbia_pixel_scocca.png")
