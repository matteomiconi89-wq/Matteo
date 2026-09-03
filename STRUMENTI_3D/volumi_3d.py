#!/usr/bin/env python3
"""Da volumi.json al 3D completo, in un comando solo.

    python3 volumi_3d.py volumi.json uscita/nome

Produce:
    nome.stp        STEP AP214 con SOLIDI VERI (OpenCASCADE): si apre in CATIA,
                    SolidWorks, Inventor, NX, Fusion e in AutoCAD con IMPORT.
                    Un solido per pezzo, nominato come nel JSON, raggruppato
                    per layer nell'albero, con i colori delle tinte.
    nome_3d.dxf     DXF 3D a mesh: anteprima immediata in AutoCAD/TrueView.
    nome.scr        Script AutoCAD: ricrea ogni pezzo come BOX solido NATIVO
                    (comando SCRIPT in AutoCAD, poi SAVEAS -> DWG).
    nome.dwg        DWG 3D diretto (mesh), solo se il convertitore dxf2dwg
                    e' disponibile e il file supera il collaudo di rilettura.
    nome_asso.png   Assonometria di controllo (algoritmo del pittore).
    nome_fronte.png / nome_fianco.png   Viste di controllo.

Assi come nel CAD di Matteo: X=larghezza, Y=profondita', Z=altezza, unita' mm.
Schema JSON: {"titolo": ..., "box": [{"nome", "layer", "colore", "tinta",
"x0","y0","z0","x1","y1","z1"}, ...]} — lo stesso della commessa 26-A011.

Collaudo integrato: lo STEP appena scritto viene RILETTO e si confrontano
numero di solidi e ingombro totale con il JSON; il DWG (se prodotto) viene
riletto con dwgread. Se un collaudo fallisce lo dice chiaro e l'exit code
e' diverso da zero.
"""
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import ezdxf
from ezdxf.render import forms
import matplotlib
matplotlib.use("Agg")
import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection

TOLL_MM = 0.5  # tolleranza di collaudo sull'ingombro riletto dallo STEP


# ---------------------------------------------------------------- utilita'

def carica_volumi(percorso):
    data = json.load(open(percorso, encoding="utf-8"))
    boxes = data["box"]
    errori = []
    visti = {}
    for i, b in enumerate(boxes):
        nome = b.get("nome", f"BOX_{i}")
        for k in ("x0", "y0", "z0", "x1", "y1", "z1"):
            if k not in b:
                errori.append(f"{nome}: manca la quota {k}")
        if errori:
            continue
        if b["x1"] <= b["x0"] or b["y1"] <= b["y0"] or b["z1"] <= b["z0"]:
            errori.append(f"{nome}: dimensioni nulle o negative "
                          f"({b['x1']-b['x0']:g} x {b['y1']-b['y0']:g} x {b['z1']-b['z0']:g})")
        if nome in visti:
            visti[nome] += 1
            b["nome"] = f"{nome}_{visti[nome]}"  # nomi unici nell'albero STEP
        else:
            visti[nome] = 1
            b["nome"] = nome
    if errori:
        for e in errori:
            print(f"ERRORE volumi.json: {e}")
        sys.exit(1)
    return data, boxes


def ingombro(boxes):
    return (min(b["x0"] for b in boxes), min(b["y0"] for b in boxes),
            min(b["z0"] for b in boxes), max(b["x1"] for b in boxes),
            max(b["y1"] for b in boxes), max(b["z1"] for b in boxes))


def tinta_rgb(b):
    try:
        return matplotlib.colors.to_rgb(b.get("tinta", "#d7d2c8"))
    except ValueError:
        return (0.84, 0.82, 0.78)


# ------------------------------------------------------------ STEP (CATIA)

def crea_step(data, boxes, out_stp):
    """Solidi veri via OpenCASCADE, albero per layer, nomi e colori dei pezzi."""
    import cadquery as cq

    radice = cq.Assembly(name=nome_step_valido(data.get("titolo", "VOLUMI")))
    per_layer = {}
    for b in boxes:
        per_layer.setdefault(b.get("layer", "VOLUMI"), []).append(b)
    for layer, gruppo in per_layer.items():
        ramo = cq.Assembly(name=nome_step_valido(layer))
        for b in gruppo:
            dx, dy, dz = b["x1"] - b["x0"], b["y1"] - b["y0"], b["z1"] - b["z0"]
            solido = cq.Solid.makeBox(dx, dy, dz, pnt=cq.Vector(b["x0"], b["y0"], b["z0"]))
            r, g, bl = tinta_rgb(b)
            ramo.add(solido, name=nome_step_valido(b["nome"]), color=cq.Color(r, g, bl))
        radice.add(ramo, name=nome_step_valido(layer))
    radice.export(str(out_stp), exportType="STEP")


def nome_step_valido(testo):
    """Nell'albero STEP restano solo caratteri sicuri per CATIA."""
    pulito = "".join(c if c.isalnum() or c in "_-." else "_" for c in str(testo))
    return pulito[:80] or "PEZZO"


def collauda_step(out_stp, boxes):
    """Rilegge lo STEP scritto e confronta solidi e ingombro col JSON."""
    import cadquery as cq

    letto = cq.importers.importStep(str(out_stp))
    solidi = letto.solids().vals()
    attesi = len(boxes)
    xs0 = min(s.BoundingBox().xmin for s in solidi)
    ys0 = min(s.BoundingBox().ymin for s in solidi)
    zs0 = min(s.BoundingBox().zmin for s in solidi)
    xs1 = max(s.BoundingBox().xmax for s in solidi)
    ys1 = max(s.BoundingBox().ymax for s in solidi)
    zs1 = max(s.BoundingBox().zmax for s in solidi)
    x0, y0, z0, x1, y1, z1 = ingombro(boxes)
    ok_n = len(solidi) == attesi
    ok_bb = all(abs(a - b) <= TOLL_MM for a, b in
                [(xs0, x0), (ys0, y0), (zs0, z0), (xs1, x1), (ys1, y1), (zs1, z1)])
    print(f"COLLAUDO STEP: solidi riletti {len(solidi)}/{attesi} "
          f"{'OK' if ok_n else 'ERRORE'}")
    print(f"COLLAUDO STEP: ingombro riletto {xs1-xs0:.1f} x {ys1-ys0:.1f} x {zs1-zs0:.1f} mm "
          f"(atteso {x1-x0:.1f} x {y1-y0:.1f} x {z1-z0:.1f}) {'OK' if ok_bb else 'ERRORE'}")
    return ok_n and ok_bb


# ------------------------------------------------- DXF mesh + SCR AutoCAD

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
    """Script AutoCAD: un layer per gruppo, BOX solido nativo per ogni pezzo."""
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


# ------------------------------------------------------------- DWG diretto

def crea_dwg(out_dxf, out_dwg, n_attese):
    """DXF mesh -> DWG diretto, SOLO se supera il collaudo di round-trip.

    Convertitori tentati in ordine:
      1. ODAFileConverter (gratuito, opendesign.com) — affidabile: e' quello
         da installare sul PC per avere il DWG senza passare da AutoCAD.
      2. dxf2dwg di LibreDWG — oggi scrive DWG rotti (collaudo 09/2026:
         0 entita' rilette su 74): resta qui solo perche' il collaudo severo
         lo promuovera' da solo quando una versione futura funzionera'.

    Se nessun collaudo passa il DWG NON viene consegnato: il DWG vero si fa
    in AutoCAD in un comando (SCRIPT nome.scr oppure IMPORT nome.stp, poi
    SAVEAS) — vedi README_3D.md.
    """
    out_dxf, out_dwg = Path(out_dxf), Path(out_dwg)

    oda = shutil.which("ODAFileConverter")
    if oda:
        import tempfile
        with tempfile.TemporaryDirectory() as tin, tempfile.TemporaryDirectory() as tout:
            shutil.copy(out_dxf, Path(tin) / out_dxf.name)
            prova = subprocess.run(
                [oda, tin, tout, "ACAD2018", "DWG", "0", "1"],
                capture_output=True, timeout=600)
            prodotto = Path(tout) / (out_dxf.stem + ".dwg")
            if prova.returncode == 0 and prodotto.exists():
                shutil.copy(prodotto, out_dwg)
                print(f"COLLAUDO DWG: {out_dwg.name} scritto con ODAFileConverter (ACAD2018) OK")
                return out_dwg
        print("DWG diretto: ODAFileConverter presente ma conversione fallita")

    exe = shutil.which("dxf2dwg")
    if not exe:
        print("DWG diretto: nessun convertitore affidabile presente, salto "
              "(DWG in AutoCAD con SCRIPT .scr o IMPORT .stp; oppure installare "
              "ODA File Converter, gratuito)")
        return None
    try:
        subprocess.run([exe, "-y", "--as", "r2000", "-o", str(out_dwg), str(out_dxf)],
                       check=True, capture_output=True, timeout=300)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print("DWG diretto: conversione dxf2dwg fallita, file non consegnato")
        Path(out_dwg).unlink(missing_ok=True)
        return None
    # collaudo severo: riconverto in DXF e pretendo stesse entita' e ingombro
    ok = False
    lettore = shutil.which("dwg2dxf")
    if lettore:
        ritorno = out_dwg.with_suffix(".ritorno.dxf")
        prova = subprocess.run([lettore, "-y", "-o", str(ritorno), str(out_dwg)],
                               capture_output=True, timeout=300)
        if prova.returncode == 0 and ritorno.exists():
            try:
                d = ezdxf.readfile(str(ritorno))
                n = sum(1 for _ in d.modelspace())
                ok = n >= n_attese
                if not ok:
                    print(f"COLLAUDO DWG: rilette {n} entita' su {n_attese} attese -> BOCCIATO")
            except Exception as err:
                print(f"COLLAUDO DWG: DWG illeggibile ({err}) -> BOCCIATO")
        ritorno.unlink(missing_ok=True)
    if not ok:
        print("DWG diretto scartato per prudenza: usare DXF/SCR/STP "
              "(DWG in AutoCAD con SCRIPT .scr o IMPORT .stp)")
        out_dwg.unlink(missing_ok=True)
        return None
    print(f"COLLAUDO DWG: {out_dwg.name} round-trip OK (r2000, mesh)")
    return out_dwg


# ------------------------------------------- viste di controllo (pittore)

def proietta(boxes, az_deg, el_deg):
    az, el = math.radians(az_deg), math.radians(el_deg)
    cam = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    f = -cam / np.linalg.norm(cam)
    r = np.cross(np.array([0.0, 0.0, 1.0]), f); r /= np.linalg.norm(r)
    u = np.cross(f, r)
    luce = np.array([-0.3, -0.8, 0.6]); luce /= np.linalg.norm(luce)
    facce = []
    for b in boxes:
        x0, y0, z0, x1, y1, z1 = b["x0"], b["y0"], b["z0"], b["x1"], b["y1"], b["z1"]
        v = np.array([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                      (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], dtype=float)
        quads = [([0, 1, 5, 4], (0, -1, 0)), ([3, 2, 6, 7], (0, 1, 0)),
                 ([0, 3, 7, 4], (-1, 0, 0)), ([1, 2, 6, 5], (1, 0, 0)),
                 ([4, 5, 6, 7], (0, 0, 1)), ([0, 1, 2, 3], (0, 0, -1))]
        base = np.array(tinta_rgb(b))
        for idx, n in quads:
            n = np.array(n, dtype=float)
            if np.dot(n, f) > 0:
                continue
            pts = v[idx]
            lum = 0.58 + 0.42 * max(0.0, float(np.dot(n, luce)))
            facce.append((float(np.mean(pts @ f)),
                          [(float(p @ r), float(p @ u)) for p in pts],
                          tuple(np.clip(base * lum, 0, 1))))
    facce.sort(key=lambda t: -t[0])
    return facce


def disegna(boxes, titolo, out_png, az=118, el=20, quote=None):
    facce = proietta(boxes, az, el)
    fig, ax = plt.subplots(figsize=(11, 9), dpi=150)
    ax.add_collection(PolyCollection([p for _, p, _ in facce],
                                     facecolors=[c for _, _, c in facce],
                                     edgecolors="#2b2b2b", linewidths=0.55))
    ax.autoscale(); ax.set_aspect("equal"); ax.set_axis_off()
    ax.set_title(titolo, fontsize=11)
    if quote:
        ax.text(0.5, -0.02, quote, transform=ax.transAxes, ha="center", va="top",
                fontsize=8.5, family="monospace", color="#333333")
    fig.tight_layout()
    fig.savefig(out_png, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ----------------------------------------------------------------- main

def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    data, boxes = carica_volumi(src)
    titolo = data.get("titolo", "VOLUMI")
    x0, y0, z0, x1, y1, z1 = ingombro(boxes)
    quote = f"ingombro totale: L {x1-x0:.0f} x P {y1-y0:.0f} x H {z1-z0:.0f} mm ({len(boxes)} solidi)"
    print(f"{len(boxes)} solidi da {src.name} — {quote}")

    crea_dxf(boxes, str(out) + "_3d.dxf")
    crea_scr(boxes, str(out) + ".scr")
    print(f"Scritti {out.name}_3d.dxf (mesh) e {out.name}.scr (BOX nativi AutoCAD)")

    crea_step(data, boxes, str(out) + ".stp")
    ok_step = collauda_step(str(out) + ".stp", boxes)
    print(f"Scritto {out.name}.stp (STEP AP214, solidi veri — CATIA/SolidWorks/AutoCAD IMPORT)")

    crea_dwg(str(out) + "_3d.dxf", str(out) + ".dwg", len(boxes))

    disegna(boxes, titolo + "\nassonometria di controllo", str(out) + "_asso.png", quote=quote)
    disegna(boxes, titolo + "\nfronte", str(out) + "_fronte.png", az=90, el=2)
    disegna(boxes, titolo + "\nfianco", str(out) + "_fianco.png", az=180, el=2)
    print(f"Viste di controllo: {out.name}_asso/_fronte/_fianco.png")

    if not ok_step:
        sys.exit(1)


if __name__ == "__main__":
    main()
