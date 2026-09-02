#!/usr/bin/env python3
# Assonometrie dei volumi scocca 26A011 (aperto/chiuso) — àncora geometrica per Manus.
import json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

BASE = pathlib.Path(__file__).parent
DATA = json.loads((BASE / "geometry.json").read_text())

COL = {
    "VOL_TELAIO": "#454c54", "VOL_CASSONE": "#8593a0", "VOL_PAVIMENTO": "#a5793f",
    "VOL_TETTO": "#aab4bc", "VOL_CONTROSOFFITTO": "#d8d2c4", "VOL_OBLO": "#63c3dc",
    "VOL_IMPIANTO_CLIMA": "#5b83ad", "VOL_DIVISORI": "#c07b3c", "VOL_VETRO": "#4fc3de",
    "VOL_ESTRATTORE_INGRESSO": "#3f9e94", "VOL_ESTRATTORE_CUCINA": "#76a565",
    "VOL_TETTO_ESTR_INCLINATO": "#caa15e",
}
ALPHA = {"VOL_VETRO": .4, "VOL_OBLO": .55}

def draw(cfg, title, out, elev=20, azim=-63):
    polys, fcs = [], []
    xs, ys, zs = [], [], []
    for m in DATA[cfg]:
        fc = to_rgba(COL.get(m["l"], "#999"), ALPHA.get(m["l"], 1.0))
        for f in m["f"]:
            polys.append([tuple(m["v"][i]) for i in f])
            fcs.append(fc)
        for v in m["v"]:
            xs.append(v[0]); ys.append(v[1]); zs.append(v[2])
    fig = plt.figure(figsize=(15, 8.6), dpi=140)
    ax = fig.add_axes([0.0, 0.0, 1.0, 0.94], projection="3d")
    ax.set_proj_type("ortho")
    pc = Poly3DCollection(polys, facecolors=fcs, edgecolor=(0.14, 0.18, 0.22, .9),
                          linewidths=.3)
    ax.add_collection3d(pc)
    mx = 250
    rx = (min(xs)-mx, max(xs)+mx); ry = (min(ys)-mx, max(ys)+mx); rz = (min(zs), max(zs)+mx)
    ax.set_xlim(*rx); ax.set_ylim(*ry); ax.set_zlim(*rz)
    ax.set_box_aspect((rx[1]-rx[0], ry[1]-ry[0], rz[1]-rz[0]), zoom=1.24)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    fig.text(.5, .965, title, ha="center", fontsize=16, fontweight="bold", color="#232e38")
    fig.text(.5, .928, "26A011 rev.06 — volumi reali dal DXF · quote in millimetri", ha="center",
             fontsize=10.5, color="#67727e")
    fig.text(.985, .022,
             "L 13.989 · larg. 2.540 (chiuso) / 4.840 (aperto) · H 4.000\n"
             "pavimento interno +1.395 da terra · h utile 2.251 (centro) / 2.103-2.151 (baie)",
             ha="right", fontsize=10, family="monospace", color="#232e38")
    fig.savefig(BASE / out, facecolor="white")
    plt.close(fig)
    print(out)

draw("aperto", "SCOCCA 26A011 — CONFIGURAZIONE APERTA (esercizio)", "scocca_assonometria_aperto.png")
draw("chiuso", "SCOCCA 26A011 — CONFIGURAZIONE CHIUSA (marcia)", "scocca_assonometria_chiuso.png")
draw("aperto", "SCOCCA 26A011 — APERTA, VISTA LATO CUCINA / RETRO", "scocca_assonometria_aperto_retro.png", elev=24, azim=118)
