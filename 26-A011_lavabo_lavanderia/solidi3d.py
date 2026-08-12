#!/usr/bin/env python3
"""Volumi JSON -> DXF 3D (mesh) + script AutoCAD (BOX nativi) + assonometrie.

X = larghezza, Y = profondità, Z = altezza (mm, come nel CAD).
Le assonometrie usano proiezione ortografica + algoritmo del pittore:
niente librerie 3D, risultato deterministico e ripetibile.
"""
import json
import math
import sys

import ezdxf
from ezdxf.render import forms
import matplotlib
matplotlib.use("Agg")
import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection


def crea_dxf(boxes, out_dxf):
    doc = ezdxf.new("R2018", setup=True)
    doc.header["$INSUNITS"] = 4  # millimetri
    msp = doc.modelspace()
    for b in boxes:
        layer = b.get("layer", "VOLUMI")
        if layer not in doc.layers:
            doc.layers.add(layer, color=b.get("colore", 8))
        dx, dy, dz = b["x1"] - b["x0"], b["y1"] - b["y0"], b["z1"] - b["z0"]
        mesh = forms.cube(center=False).scale(dx, dy, dz).translate(b["x0"], b["y0"], b["z0"])
        mesh.render_mesh(msp, dxfattribs={"layer": layer})
    doc.saveas(out_dxf)


def crea_scr(boxes, out_scr):
    """Script AutoCAD: un layer per gruppo, BOX nativo per ogni pezzo."""
    righe = ["._UCS", "_W", ""]
    layer_corrente = None
    for b in boxes:
        lay = b.get("layer", "VOLUMI")
        if lay != layer_corrente:
            righe += ["._-LAYER", "_M", lay, "_C", str(b.get("colore", 8)), "", ""]
            layer_corrente = lay
        dx, dy, dz = b["x1"] - b["x0"], b["y1"] - b["y0"], b["z1"] - b["z0"]
        righe += ["._BOX", f"{b['x0']},{b['y0']},{b['z0']}", f"@{dx},{dy}", f"{dz}"]
    righe += ["._-VIEW", "_SWISO", "._ZOOM", "_E", "._VSCURRENT", "_S", ""]
    open(out_scr, "w", encoding="ascii").write("\n".join(righe))


def proietta(boxes, az_deg, el_deg, esploso=0.0):
    """Ritorna le facce visibili ordinate dal fondo (algoritmo del pittore)."""
    az, el = math.radians(az_deg), math.radians(el_deg)
    cam = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    f = -cam / np.linalg.norm(cam)
    # destra schermo = Z x avanti  → X del mobile cresce verso destra, come nel prospetto CAD
    r = np.cross(np.array([0.0, 0.0, 1.0]), f); r /= np.linalg.norm(r)
    u = np.cross(f, r)
    luce = np.array([-0.3, -0.8, 0.6]); luce /= np.linalg.norm(luce)

    facce = []
    for b in boxes:
        off = np.array([0.0, esploso * b.get("esplodi", 0.0), 0.0])
        x0, y0, z0 = b["x0"] + off[0], b["y0"] + off[1], b["z0"] + off[2]
        x1, y1, z1 = b["x1"] + off[0], b["y1"] + off[1], b["z1"] + off[2]
        v = np.array([
            (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
            (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
        ], dtype=float)
        quads = [
            ([0, 1, 5, 4], (0, -1, 0)), ([3, 2, 6, 7], (0, 1, 0)),
            ([0, 3, 7, 4], (-1, 0, 0)), ([1, 2, 6, 5], (1, 0, 0)),
            ([4, 5, 6, 7], (0, 0, 1)), ([0, 1, 2, 3], (0, 0, -1)),
        ]
        base = np.array(matplotlib.colors.to_rgb(b.get("tinta", "#d7d2c8")))
        for idx, n in quads:
            n = np.array(n, dtype=float)
            if np.dot(n, f) > 0:
                continue
            pts = v[idx]
            depth = float(np.mean(pts @ f))
            poly = [(float(p @ r), float(p @ u)) for p in pts]
            lum = 0.58 + 0.42 * max(0.0, float(np.dot(n, luce)))
            facce.append((depth, poly, tuple(np.clip(base * lum, 0, 1))))
    facce.sort(key=lambda t: -t[0])
    return facce


def disegna(boxes, titolo, out_png, az=118, el=20, quote=None):
    facce = proietta(boxes, az, el)
    fig, ax = plt.subplots(figsize=(11, 9), dpi=150)
    ax.add_collection(PolyCollection([p for _, p, _ in facce],
                                     facecolors=[c for _, _, c in facce],
                                     edgecolors="#2b2b2b", linewidths=0.55))
    ax.autoscale()
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title(titolo, fontsize=11)
    if quote:
        ax.text(0.5, -0.02, quote, transform=ax.transAxes, ha="center", va="top",
                fontsize=8.5, family="monospace", color="#333333")
    fig.tight_layout()
    fig.savefig(out_png, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    src, out = sys.argv[1], sys.argv[2]
    data = json.load(open(src, encoding="utf-8"))
    boxes, titolo = data["box"], data.get("titolo", "VOLUMI")

    crea_dxf(boxes, out + ".dxf")
    crea_scr(boxes, out + ".scr")

    mobile = [b for b in boxes if not b["nome"].startswith(("PAR_", "VETRO_"))]
    senza_ante = [b for b in boxes if not b["nome"].startswith("ANTA_")]
    solo_carcassa = [b for b in mobile if not b["nome"].startswith(("ANTA_", "LAVABO", "MISCEL", "TOP_"))]

    tot = (max(b["x1"] for b in boxes), max(b["y1"] for b in boxes), max(b["z1"] for b in boxes))
    q = (f"parete+mobile: L {tot[0]:.0f} x P {tot[1]:.0f} x H {tot[2]:.0f} mm   |   "
         f"mobile: 1173 x 400 x H 670 (piano finito)   |   lavabo fino a H 920")

    disegna(boxes, titolo + "\ncomplessivo (parete + mobile)", out + "_1_complessivo.png", quote=q)
    disegna(mobile, titolo + "\nmobile con ante chiuse — gola di presa 30 mm sopra le ante",
            out + "_2_mobile_chiuso.png", az=118, el=14)
    disegna(senza_ante, titolo + "\nSENZA ANTE: nicchia a giorno + vano interno con ripiani",
            out + "_3_senza_ante.png", az=118, el=14)
    disegna(solo_carcassa, titolo + "\nSOLA CARCASSA: fianchi, divisorio, schienale, ripiani, traversi",
            out + "_4_carcassa.png", az=125, el=22)
    disegna(mobile, titolo + "\nvista di fianco (sezione ottica): profondità e sbalzi",
            out + "_5_fianco.png", az=180, el=2)

    print(f"{len(boxes)} solidi -> {out}.dxf / .scr + 5 viste")
    print(f"Ingombro totale: {tot[0]:.0f} x {tot[1]:.0f} x {tot[2]:.0f} mm")


if __name__ == "__main__":
    main()
