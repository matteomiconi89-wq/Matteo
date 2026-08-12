#!/usr/bin/env python3
"""Gabbia in pixel per il brief a Manus: dove deve stare ogni cosa nel frame 16:9.

Render richiesto 2400x1350. Qui si fissa l'inquadratura e si traducono le quote CAD
in pixel, cosi' il collaudo dopo e' una misura e non un parere.
Il disegno resta pulito: l'elenco completo delle quote va nel brief, non sull'immagine.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

FW, FH = 2400, 1350
MOB_L = 1173.0

SCALA = (FW * 0.48) / MOB_L
X0 = (FW - MOB_L * SCALA) / 2.0
Y_PAV = FH * 0.92

px_x = lambda mm: X0 + mm * SCALA
px_y = lambda z: Y_PAV - z * SCALA
box = lambda x0, x1, z0, z1, **kw: Rectangle(
    (px_x(x0), px_y(z1)), (x1 - x0) * SCALA, (z1 - z0) * SCALA, **kw)

fig, ax = plt.subplots(figsize=(16, 9), dpi=150)
ax.set_xlim(0, FW); ax.set_ylim(FH, 0)
ax.set_aspect("equal"); ax.set_facecolor("#fcfbf9")
ax.add_patch(Rectangle((0, 0), FW, FH, fill=False, ec="#222", lw=2.5))
for f in (1 / 3, 2 / 3):
    ax.axvline(FW * f, color="#e0dcd4", lw=1, ls="--")
    ax.axhline(FH * f, color="#e0dcd4", lw=1, ls="--")

# pavimento + parete di fondo (contesto)
ax.add_patch(Rectangle((0, 0), FW, Y_PAV, fc="#f2efe9", ec="none", zorder=0))
ax.axhline(Y_PAV, color="#8d8779", lw=1.5, zorder=1)

# corpo mobile
ax.add_patch(box(0, 1173, 100, 670, fc="#ded9cd", ec="#1f3a5f", lw=2, zorder=2))
ax.add_patch(box(0, 1173, 2, 100, fc="#63676b", ec="#1f3a5f", lw=1.2, zorder=3))   # zoccolo
# nicchia a giorno
ax.add_patch(box(18, 450, 118, 557, fc="#c9c1b0", ec="#1f3a5f", lw=1.2, zorder=4))
ax.add_patch(box(18, 450, 328.5, 346.5, fc="#b0a894", ec="#1f3a5f", lw=1, zorder=5))
# ante
for a, b, lab in [(453, 810, "ANTA SX 357"), (813, 1170, "ANTA DX 357")]:
    ax.add_patch(box(a, b, 92, 580, fc="#4a4a4e", ec="#1f3a5f", lw=1.2, zorder=4))
    ax.text(px_x((a + b) / 2), px_y(336), lab, ha="center", va="center",
            fontsize=10, color="white", weight="bold", zorder=6)
ax.text(px_x(234), px_y(430), "NICCHIA\nA GIORNO\n432 mm", ha="center", va="center",
        fontsize=10, color="#3a3a3a", weight="bold", zorder=6)
ax.text(px_x(234), px_y(215), "1 ripiano\na quota 329", ha="center", va="center",
        fontsize=8.5, color="#5a5348", zorder=6)
# gola + piano
ax.add_patch(box(0, 1173, 580, 610, fc="#1c1c1c", ec="#a2701c", lw=2, zorder=5))
ax.add_patch(box(0, 1173, 610, 670, fc="#4a4a4e", ec="#1f3a5f", lw=1.2, zorder=5))
# lavabo + miscelatore
ax.add_patch(box(499, 1102, 670, 920, fc="#f7f7f4", ec="#1f3a5f", lw=1.8, zorder=6))
ax.add_patch(box(430, 470, 670, 1100, fc="#3f3f3d", ec="#1f3a5f", lw=1, zorder=6))
ax.add_patch(box(470, 577, 1060, 1100, fc="#3f3f3d", ec="#1f3a5f", lw=1, zorder=6))
ax.text(px_x(800), px_y(800), "LAVABO\nGalassia MEG 11 PRO", ha="center", va="center",
        fontsize=9, color="#4a4a4e", zorder=7)

# richiami
ax.annotate("GOLA APERTA 30 mm\nfondo a specchio, LED sotto il piano",
            xy=(px_x(1173) + 6, px_y(595)), xytext=(px_x(1173) + 150, px_y(700)),
            fontsize=9.5, color="#a2701c", weight="bold", va="center",
            arrowprops=dict(arrowstyle="->", color="#a2701c", lw=1.6))
ax.annotate("zoccolo arretrato 98, fessura d'ombra\nLED che lava il pavimento",
            xy=(px_x(0) - 6, px_y(50)), xytext=(px_x(0) - 470, px_y(150)),
            fontsize=9.5, color="#1f3a5f", va="center",
            arrowprops=dict(arrowstyle="->", color="#1f3a5f", lw=1.4))
ax.annotate("NESSUNA MANIGLIA a vista:\napertura a gola",
            xy=(px_x(990), px_y(560)), xytext=(px_x(1230), px_y(1010)),
            fontsize=9.5, color="#1f3a5f", va="center",
            arrowprops=dict(arrowstyle="->", color="#1f3a5f", lw=1.4))

# quote principali
yq = px_y(0) + 55
ax.annotate("", xy=(px_x(0), yq), xytext=(px_x(1173), yq),
            arrowprops=dict(arrowstyle="<->", color="#1f3a5f", lw=1.6))
ax.text(px_x(586), yq - 14, "MOBILE 1173 mm = 1152 px  (48% del frame)", ha="center",
        fontsize=11, color="#1f3a5f", weight="bold")
xq = px_x(1173) + 95
ax.annotate("", xy=(xq, px_y(0)), xytext=(xq, px_y(670)),
            arrowprops=dict(arrowstyle="<->", color="#1f3a5f", lw=1.6))
ax.text(xq + 12, px_y(335), "piano finito\n670 mm\n= 658 px", fontsize=9, color="#1f3a5f", va="center")

ax.text(28, 44, "GABBIA DI INQUADRATURA — mobile lavabo lavanderia 26-A011",
        fontsize=15, weight="bold", color="#1f3a5f", va="top")
ax.text(28, 88, "frame 2400×1350 · scala 0,9821 px/mm · base mobile a y 1242 px · "
                "rapporti da rispettare: nicchia/anta 1,21 · L/H-piano 1,75",
        fontsize=9.5, color="#5a5348", va="top")
ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values():
    s.set_visible(False)
fig.tight_layout()
fig.savefig("gabbia_pixel.png", facecolor="white", bbox_inches="tight")
print("scritto gabbia_pixel.png")
