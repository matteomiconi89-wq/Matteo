#!/usr/bin/env python3
"""Volumi JSON -> DXF 3D (mesh) + script AutoCAD (BOX/CYLINDER nativi) + assonometrie.

X = lunghezza (0 = muso), Y = trasversale (0 = faccia estrattore ingresso APERTO),
Z = altezza da terra (mm, 1:1 come nel CAD).
Genera due configurazioni: APERTO (di progetto) e CHIUSO (estrattori rientrati di 1150,
senza i pezzi marcati "solo_aperto"). Assonometrie con algoritmo del pittore, deterministiche.
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

CORSA = 1150  # rientro estrattori nel passaggio aperto -> chiuso


def config_chiusa(boxes):
    out = []
    for b in boxes:
        if b.get("solo_aperto"):
            continue
        # divisori/vetrate dentro le zone estrattori: rientrano col modulo, nel chiuso si omettono
        if b["gruppo"] in ("divisori", "vetrate") and (b["y0"] >= 3603 or b["y1"] <= 1213):
            continue
        b = dict(b)
        dy = CORSA if b["gruppo"] == "estr_ing" else -CORSA if b["gruppo"] == "estr_cuc" else 0
        if dy:
            if b.get("tipo") == "prisma_x":
                b["profilo"] = [[y + dy, z] for y, z in b["profilo"]]
            else:
                b["y0"] += dy; b["y1"] += dy
        out.append(b)
    return out


def crea_dxf(boxes, out_dxf):
    doc = ezdxf.new("R2018", setup=True)
    doc.header["$INSUNITS"] = 4  # millimetri
    msp = doc.modelspace()
    for b in boxes:
        layer = b.get("layer", "VOLUMI")
        if layer not in doc.layers:
            doc.layers.add(layer, color=b.get("colore", 8))
        if b.get("tipo") == "cilindro_y":
            L = b["y1"] - b["y0"]
            mesh = forms.cylinder(count=24, radius=b["r"], top_center=(0, 0, L))
            mesh = mesh.rotate_x(math.radians(-90)).translate(b["cx"], b["y0"], b["cz"])
        elif b.get("tipo") == "prisma_x":
            from ezdxf.render import MeshBuilder
            prof = b["profilo"]
            v0 = [(b["x0"], y, z) for y, z in prof]
            v1 = [(b["x1"], y, z) for y, z in prof]
            mesh = MeshBuilder()
            mesh.add_face(v0[::-1])
            mesh.add_face(v1)
            n = len(prof)
            for i in range(n):
                j = (i + 1) % n
                mesh.add_face([v0[i], v0[j], v1[j], v1[i]])
        else:
            dx, dy, dz = b["x1"] - b["x0"], b["y1"] - b["y0"], b["z1"] - b["z0"]
            mesh = forms.cube(center=False).scale(dx, dy, dz).translate(b["x0"], b["y0"], b["z0"])
        mesh.render_mesh(msp, dxfattribs={"layer": layer})
    doc.saveas(out_dxf)


def crea_scr(boxes, out_scr):
    """Script AutoCAD: un layer per gruppo, BOX nativo (CYLINDER per le ruote)."""
    righe = ["._UCS", "_W", ""]
    layer_corrente = None
    for b in boxes:
        lay = b.get("layer", "VOLUMI")
        if lay != layer_corrente:
            righe += ["._-LAYER", "_M", lay, "_C", str(b.get("colore", 8)), "", ""]
            layer_corrente = lay
        if b.get("tipo") == "cilindro_y":
            righe += ["._CYLINDER", f"{b['cx']},{b['y0']},{b['cz']}", f"{b['r']}",
                      "_A", f"{b['cx']},{b['y1']},{b['cz']}"]
        elif b.get("tipo") == "prisma_x":
            # UCS sul piano YZ in x0 (X ucs = Y mondo, Y ucs = Z mondo, Z ucs = X mondo),
            # profilo in PLINE chiusa, poi EXTRUDE lungo la lunghezza. Solido nativo.
            righe += ["._UCS", "_W",
                      "._UCS", "_3", f"{b['x0']},0,0", f"{b['x0']},1,0", f"{b['x0']},0,1",
                      "._PLINE"]
            righe += [f"{y},{z}" for y, z in b["profilo"]]
            righe += ["_C",
                      "._EXTRUDE", "_L", "", f"{b['x1'] - b['x0']}",
                      "._UCS", "_W"]
        else:
            dx, dy, dz = b["x1"] - b["x0"], b["y1"] - b["y0"], b["z1"] - b["z0"]
            righe += ["._BOX", f"{b['x0']},{b['y0']},{b['z0']}", f"@{dx},{dy}", f"{dz}"]
    righe += ["._-VIEW", "_SWISO", "._ZOOM", "_E", "._VSCURRENT", "_S", ""]
    open(out_scr, "w", encoding="ascii").write("\n".join(righe))


def facce_box(b, base):
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
    return [(v[idx], np.array(n, dtype=float), base) for idx, n in quads]


def facce_cilindro_y(b, base, n=24):
    cx, cz, r, y0, y1 = b["cx"], b["cz"], b["r"], b["y0"], b["y1"]
    ang = np.linspace(0, 2 * math.pi, n, endpoint=False)
    out = []
    for a0, a1 in zip(ang, np.roll(ang, -1)):
        p00 = (cx + r * math.cos(a0), y0, cz + r * math.sin(a0))
        p01 = (cx + r * math.cos(a1), y0, cz + r * math.sin(a1))
        p11 = (cx + r * math.cos(a1), y1, cz + r * math.sin(a1))
        p10 = (cx + r * math.cos(a0), y1, cz + r * math.sin(a0))
        nrm = np.array([math.cos((a0 + a1) / 2), 0.0, math.sin((a0 + a1) / 2)])
        out.append((np.array([p00, p01, p11, p10]), nrm, base))
    for y, ny in ((y0, -1.0), (y1, 1.0)):
        ring = np.array([(cx + r * math.cos(a), y, cz + r * math.sin(a)) for a in ang])
        out.append((ring, np.array([0.0, ny, 0.0]), base))
    return out


def facce_prisma_x(b, base):
    prof = b["profilo"]
    v0 = np.array([(b["x0"], y, z) for y, z in prof], dtype=float)
    v1 = np.array([(b["x1"], y, z) for y, z in prof], dtype=float)
    centro = np.vstack([v0, v1]).mean(axis=0)
    out = []
    n = len(prof)
    facce = [list(v0), list(v1)]
    for i in range(n):
        j = (i + 1) % n
        facce.append([v0[i], v0[j], v1[j], v1[i]])
    for pts in facce:
        pts = np.array(pts)
        nrm = np.cross(pts[1] - pts[0], pts[2] - pts[0])
        ln = np.linalg.norm(nrm)
        if ln < 1e-9:
            continue
        nrm /= ln
        if np.dot(nrm, pts.mean(axis=0) - centro) < 0:
            nrm = -nrm
        out.append((pts, nrm, base))
    return out


def proietta(boxes, az_deg, el_deg):
    az, el = math.radians(az_deg), math.radians(el_deg)
    cam = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    f = -cam / np.linalg.norm(cam)
    r = np.cross(np.array([0.0, 0.0, 1.0]), f); r /= np.linalg.norm(r)
    u = np.cross(f, r)
    luce = np.array([-0.45, -0.7, 0.55]); luce /= np.linalg.norm(luce)

    facce = []
    for b in boxes:
        base = np.array(matplotlib.colors.to_rgb(b.get("tinta", "#d7d2c8")))
        if b.get("tipo") == "cilindro_y":
            gen = facce_cilindro_y(b, base)
        elif b.get("tipo") == "prisma_x":
            gen = facce_prisma_x(b, base)
        else:
            gen = facce_box(b, base)
        for pts, n, col in gen:
            if np.dot(n, f) > 0:
                continue
            depth = float(np.mean(pts @ f))
            poly = [(float(p @ r), float(p @ u)) for p in pts]
            lum = 0.58 + 0.42 * max(0.0, float(np.dot(n, luce)))
            facce.append((depth, poly, tuple(np.clip(col * lum, 0, 1))))
    facce.sort(key=lambda t: -t[0])
    return facce


def disegna(boxes, titolo, out_png, az=215, el=16, quote=None):
    facce = proietta(boxes, az, el)
    fig, ax = plt.subplots(figsize=(13, 8), dpi=150)
    ax.add_collection(PolyCollection([p for _, p, _ in facce],
                                     facecolors=[c for _, _, c in facce],
                                     edgecolors="#2b2b2b", linewidths=0.5))
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
    aperto, titolo = data["box"], data.get("titolo", "VOLUMI")
    chiuso = config_chiusa(aperto)

    crea_dxf(aperto, out + "_aperto.dxf")
    crea_scr(aperto, out + "_aperto.scr")
    crea_dxf(chiuso, out + "_chiuso.dxf")
    crea_scr(chiuso, out + "_chiuso.scr")

    q = ("APERTO: 13989 x 4840 x H 4000 mm  |  CHIUSO: 13989 x 2540 x H 4000 mm  |  "
         "pav. +1395, h utile 2290, finestre 2395-3042, controsoffitto 3646, sporg. estrattori 1150")

    scocca = [b for b in aperto if b["gruppo"] != "telaio"]
    senza_tetto = [b for b in aperto
                   if b["gruppo"] not in ("tetto", "controsoffitto")
                   and "_tetto" not in b["nome"]]
    # il clima sta dentro il pacco tetto: nei complessivi non si vede (e sporca il painter)
    aperto_v = [b for b in aperto if b["gruppo"] != "clima"]
    chiuso_v = [b for b in chiuso if b["gruppo"] != "clima"]

    disegna(aperto_v, titolo + "\ncomplessivo APERTO (telaio e ruote indicativi)",
            out + "_1_assonometria_aperto.png", az=215, el=16, quote=q)
    disegna(senza_tetto, titolo + "\nSENZA TETTI: baie estrattori, pilastrini, pavimenti",
            out + "_2_senza_tetto.png", az=215, el=38, quote=q)
    disegna(scocca, titolo + "\nvista frontale (dal muso): sezione trasversale aperta",
            out + "_3_fronte_aperto.png", az=180, el=3)
    disegna(chiuso_v, titolo.replace("APERTI", "CHIUSI") + "\ncomplessivo CHIUSO (sagoma stradale 2540)",
            out + "_4_assonometria_chiuso.png", az=215, el=16, quote=q)
    disegna(aperto_v, titolo + "\npianta dall'alto (lato INGRESSO in alto)",
            out + "_5_pianta.png", az=90, el=88)

    print(f"{len(aperto)} solidi APERTO / {len(chiuso)} CHIUSO -> {out}_aperto/_chiuso .dxf/.scr + 5 viste")


if __name__ == "__main__":
    main()
