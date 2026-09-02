#!/usr/bin/env python3
"""Zoom quotato sulla pendenza del tetto estrattore (vista frontale, lato ingresso)."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

d = json.load(open("volumi_scocca.json", encoding="utf-8"))

fig, ax = plt.subplots(figsize=(12, 6.5), dpi=150)

# sezione trasversale (piano YZ) dei pezzi utili, lato ingresso + centro
for b in d["box"]:
    if b.get("tipo") == "prisma_x" and "ING" in b["nome"] and b["x0"] == 4322:
        poly = Polygon(b["profilo"], closed=True, facecolor="#e0b070",
                       edgecolor="#7a5510", linewidth=1.6, zorder=5, label="tetto estrattore (inclinato)")
        ax.add_patch(poly)
    elif b.get("tipo") in ("cilindro_y",) or "profilo" in b:
        continue
    elif b["nome"] in ("EST_ING_G_parete_sopra_finestra", "CASS_architrave_baiaG_ING",
                       "TETTO_cassone_sp315", "CTRSOF_campata_2_living"):
        y0, z0, y1, z1 = b["y0"], b["z0"], b["y1"], b["z1"]
        col = {"EST_ING_G_parete_sopra_finestra": "#b7cfe0",
               "CASS_architrave_baiaG_ING": "#d7d2c8",
               "TETTO_cassone_sp315": "#eae8e2",
               "CTRSOF_campata_2_living": "#f2efe8"}[b["nome"]]
        ax.add_patch(Polygon([(y0, z0), (y1, z0), (y1, z1), (y0, z1)], closed=True,
                             facecolor=col, edgecolor="#555", linewidth=0.8, zorder=3))

# quote
def quota_v(y, z, testo, dy=60):
    ax.annotate(testo, xy=(y, z), xytext=(y + dy, z + 55),
                fontsize=10, color="#a33", family="monospace",
                arrowprops=dict(arrowstyle="->", color="#a33", lw=1.2), zorder=10)

ax.annotate("intradosso 3498\n(la linea del tuo 2D)", xy=(75, 3500), xytext=(120, 3380),
            fontsize=10, color="#a33", family="monospace",
            arrowprops=dict(arrowstyle="->", color="#a33", lw=1.2), zorder=10)
ax.annotate("estradosso 3624 al colmo", xy=(1295, 3624), xytext=(700, 3700),
            fontsize=10, color="#a33", family="monospace",
            arrowprops=dict(arrowstyle="->", color="#a33", lw=1.2), zorder=10)
ax.annotate("estradosso 3576 (filo pelle parete 3580)", xy=(200, 3580),
            xytext=(430, 3450), fontsize=10, color="#a33", family="monospace",
            arrowprops=dict(arrowstyle="->", color="#a33", lw=1.2), zorder=10)
ax.annotate("", xy=(1301, 3430), xytext=(61, 3430),
            arrowprops=dict(arrowstyle="<->", color="#333", lw=1))
ax.text(660, 3408, "pendenza: +46 mm su 1176 (~2,2 gradi) | sp. pacco 78 | soffitto finito 3468 (= pav+2073)", ha="center",
        fontsize=10.5, color="#333", family="monospace")

ax.annotate("parete estrattore\n(cima a 3610)", xy=(45, 3600), xytext=(-120, 3790),
            fontsize=9, color="#456",
            arrowprops=dict(arrowstyle="->", color="#456", lw=1))
ax.text(1420, 3900, "TETTO CASSONE (3685-4000)", fontsize=9, color="#666")
ax.text(1500, 3660, "controsoffitto 3646-3685", fontsize=8.5, color="#888")
ax.text(1181, 3610, "architrave", fontsize=8, color="#888", rotation=90, va="bottom")

ax.set_xlim(-150, 2200)
ax.set_ylim(3350, 4080)
ax.set_aspect("equal")
ax.set_xlabel("Y locale (mm) - 0 = faccia esterna estrattore ingresso aperto")
ax.set_ylabel("Z (mm da terra)")
ax.set_title("SCOCCA 26-A011 rev.06 - zoom sezione: pendenza tetto estrattore (lato ingresso)\n"
             "in AutoCAD: vista FRONTE + zoom sul colmo, oppure clic sul solido arancio (layer VOL_TETTO_ESTR_INCLINATO)")
ax.grid(True, linewidth=0.3, alpha=0.5)
fig.tight_layout()
fig.savefig("scocca_zoom_tetto_inclinato.png", facecolor="white")
print("saved scocca_zoom_tetto_inclinato.png")
