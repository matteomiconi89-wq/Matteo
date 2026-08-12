#!/usr/bin/env python3
"""Genera il 3D dei soli volumi (protocollo solidi, checkpoint AutoCAD di Matteo).

Input:  JSON con lista di box {nome, layer, x0,y0,z0, x1,y1,z1} in mm
        (X = larghezza fronte, Y = profondità, Z = altezza da terra).
Output: <out>.dxf   — MESH 3D per AutoCAD (orbita/ombreggia, misure esatte)
        <out>.scr   — script AutoCAD che ricrea i volumi come solidi BOX nativi
        <out>_assonometria.png — anteprima assonometrica (poi àncora per Manus)
"""
import json
import os
import sys

import ezdxf
from ezdxf.render import forms
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ACI = {  # colori per gruppo di layer, tenui da tavola
    "default": 8,
}


def leggi_box(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return data["box"], data.get("titolo", "SOLIDI VOLUMI")


def crea_dxf(boxes, titolo, out_dxf):
    doc = ezdxf.new("R2018", setup=True)
    doc.header["$INSUNITS"] = 4  # millimetri
    msp = doc.modelspace()
    for b in boxes:
        layer = b.get("layer", "VOLUMI")
        if layer not in doc.layers:
            doc.layers.add(layer, color=b.get("colore", ACI["default"]))
        dx, dy, dz = b["x1"] - b["x0"], b["y1"] - b["y0"], b["z1"] - b["z0"]
        mesh = forms.cube(center=False)  # unit cube 0..1
        mesh = mesh.scale(dx, dy, dz).translate(b["x0"], b["y0"], b["z0"])
        m = mesh.render_mesh(msp, dxfattribs={"layer": layer})
    doc.saveas(out_dxf)


def crea_scr(boxes, out_scr):
    righe = ["._-LAYER _M VOLUMI", "", ""]
    righe = ["._UCS", "_W", ""]
    for b in boxes:
        dx, dy, dz = b["x1"] - b["x0"], b["y1"] - b["y0"], b["z1"] - b["z0"]
        righe.append("._BOX")
        righe.append(f"{b['x0']},{b['y0']},{b['z0']}")
        righe.append(f"@{dx},{dy}")
        righe.append(f"{dz}")
    righe.append("._ZOOM")
    righe.append("_E")
    righe.append("")
    with open(out_scr, "w", encoding="ascii") as fh:
        fh.write("\n".join(righe))


def crea_assonometria(boxes, titolo, out_png):
    """Proiezione ortografica manuale + algoritmo del pittore (deterministico)."""
    import math
    import numpy as np
    from matplotlib.collections import PolyCollection

    az_deg = float(os.environ.get("AZ", 115))
    el_deg = float(os.environ.get("EL", 20))
    az, el = math.radians(az_deg), math.radians(el_deg)
    cam = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    f = -cam / np.linalg.norm(cam)                      # avanti (verso la scena)
    # r = ẑ × f  → X del modello cresce verso destra sullo schermo (come nel prospetto CAD)
    r = np.cross(np.array([0.0, 0.0, 1.0]), f); r /= np.linalg.norm(r)
    u = np.cross(f, r)
    luce = np.array([-0.35, 0.75, 0.55]); luce /= np.linalg.norm(luce)

    facce = []  # (profondità, poly2d, tinta_ombreggiata)
    for b in boxes:
        x0, y0, z0, x1, y1, z1 = b["x0"], b["y0"], b["z0"], b["x1"], b["y1"], b["z1"]
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
            if np.dot(n, f) > 0:        # back-face: non visibile
                continue
            pts = v[idx]
            depth = float(np.mean(pts @ f))
            poly = [(float(p @ r), float(p @ u)) for p in pts]
            lum = 0.62 + 0.38 * max(0.0, float(np.dot(n, luce)))
            facce.append((depth, poly, tuple(np.clip(base * lum, 0, 1))))

    facce.sort(key=lambda t: -t[0])     # prima le più lontane
    fig, ax = plt.subplots(figsize=(10, 8), dpi=140)
    pc = PolyCollection([p for _, p, _ in facce],
                        facecolors=[c for _, _, c in facce],
                        edgecolors="#2f2f2f", linewidths=0.6)
    ax.add_collection(pc)
    ax.autoscale()
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title(titolo, fontsize=11)
    fig.tight_layout()
    fig.savefig(out_png, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    src, out = sys.argv[1], sys.argv[2]
    boxes, titolo = leggi_box(src)
    crea_dxf(boxes, titolo, out + ".dxf")
    crea_scr(boxes, out + ".scr")
    crea_assonometria(boxes, titolo, out + "_assonometria.png")
    tot_x0 = min(b["x0"] for b in boxes); tot_x1 = max(b["x1"] for b in boxes)
    tot_z0 = min(b["z0"] for b in boxes); tot_z1 = max(b["z1"] for b in boxes)
    tot_y0 = min(b["y0"] for b in boxes); tot_y1 = max(b["y1"] for b in boxes)
    print(f"{len(boxes)} volumi. Ingombro: L {tot_x1-tot_x0:.0f} x P {tot_y1-tot_y0:.0f} x H {tot_z1-tot_z0:.0f} mm")
    print(f"H/L = {(tot_z1-tot_z0)/(tot_x1-tot_x0):.2f}")


if __name__ == "__main__":
    main()
