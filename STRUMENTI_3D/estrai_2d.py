#!/usr/bin/env python3
"""Analisi rapida di una tavola 2D PIANTA/PROSPETTO/SEZIONE (Fase A veloce).

    python3 estrai_2d.py tavola.dxf uscita/nome
    python3 estrai_2d.py tavola.dwg uscita/nome   (se c'e' dwg2dxf di LibreDWG)

Produce:
    nome_report.txt      layer, viste individuate, quote DIMENSION, rettangoli,
                         testi con misure: tutto quello che serve per scrivere
                         il volumi.json in pochi minuti.
    nome_bozza.json      scheletro di volumi.json: ingombro proposto dalla
                         combinazione delle viste + un prisma per ogni
                         rettangolo della pianta (layer BOZZA, da rifinire).
    nome_viste.png       la tavola con le viste riquadrate e nominate.

Non e' magia: la ricostruzione FEDELE resta il lavoro della Fase A del
protocollo (Claude legge, Matteo approva il checkpoint 3D). Questo script
elimina la parte lenta: trovare viste, quote e rettangoli nel file.
"""
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import ezdxf
from ezdxf import bbox as ezbbox
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

PAROLE_VISTE = {
    "PIANTA": "PIANTA", "PLANIMETRIA": "PIANTA", "PLAN": "PIANTA",
    "PROSPETTO": "PROSPETTO", "FRONTE": "PROSPETTO", "ELEVATION": "PROSPETTO",
    "SEZIONE": "SEZIONE", "SEZ.": "SEZIONE", "SEZ ": "SEZIONE", "SECTION": "SEZIONE",
    "FIANCO": "SEZIONE", "LATO": "SEZIONE",
}


def apri_documento(percorso):
    p = Path(percorso)
    if p.suffix.lower() == ".dwg":
        exe = shutil.which("dwg2dxf")
        if not exe:
            sys.exit("Il file e' un DWG e dwg2dxf (LibreDWG) non c'e': "
                     "convertirlo in DXF (in AutoCAD: SAVEAS -> DXF) e rilanciare.")
        tmp = Path(tempfile.mkdtemp()) / (p.stem + ".dxf")
        subprocess.run([exe, "-y", "-o", str(tmp), str(p)], check=True,
                       capture_output=True, timeout=600)
        print(f"DWG convertito in DXF di lavoro: {tmp}")
        p = tmp
    doc = ezdxf.readfile(str(p))
    return doc


def bbox_entita(e):
    """Bounding box 2D di una entita' (blocchi compresi), None se non ne ha."""
    try:
        cache = bbox_entita._cache
    except AttributeError:
        cache = bbox_entita._cache = ezbbox.Cache()
    box = ezbbox.extents([e], cache=cache)
    if not box.has_data:
        return None
    return (box.extmin.x, box.extmin.y, box.extmax.x, box.extmax.y)


def raggruppa_viste(rett):
    """Unisce i bbox vicini in cluster (le viste della tavola). Union-find."""
    if not rett:
        return []
    x0 = min(r[0] for r in rett); y0 = min(r[1] for r in rett)
    x1 = max(r[2] for r in rett); y1 = max(r[3] for r in rett)
    soglia = 0.02 * max(x1 - x0, y1 - y0)  # 2% della tavola = stessa vista

    padre = list(range(len(rett)))

    def trova(i):
        while padre[i] != i:
            padre[i] = padre[padre[i]]
            i = padre[i]
        return i

    def vicini(a, b):
        return not (a[2] + soglia < b[0] or b[2] + soglia < a[0] or
                    a[3] + soglia < b[1] or b[3] + soglia < a[1])

    for i in range(len(rett)):
        for j in range(i + 1, len(rett)):
            if vicini(rett[i], rett[j]):
                ri, rj = trova(i), trova(j)
                if ri != rj:
                    padre[ri] = rj
    gruppi = {}
    for i in range(len(rett)):
        gruppi.setdefault(trova(i), []).append(i)
    cluster = []
    for indici in gruppi.values():
        cluster.append((min(rett[i][0] for i in indici), min(rett[i][1] for i in indici),
                        max(rett[i][2] for i in indici), max(rett[i][3] for i in indici),
                        indici))
    # scarta i cluster-briciola (cartiglio, simboli): sotto il 4% del lato tavola
    lato = max(x1 - x0, y1 - y0)
    cluster = [c for c in cluster if max(c[2] - c[0], c[3] - c[1]) > 0.04 * lato]
    cluster.sort(key=lambda c: (-(c[3] - c[1]) * (c[2] - c[0])))
    return cluster


def dentro(px, py, c, margine=0.0):
    return c[0] - margine <= px <= c[2] + margine and c[1] - margine <= py <= c[3] + margine


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    src, out = sys.argv[1], Path(sys.argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = apri_documento(src)
    msp = doc.modelspace()

    per_layer = {}
    geometrie = []          # (bbox, layer, tipo)
    testi = []              # (x, y, testo)
    quote = []              # (x, y, misura, testo_override)
    rettangoli = []         # (bbox, layer, w, h)

    for e in msp:
        tipo = e.dxftype()
        per_layer[e.dxf.layer] = per_layer.get(e.dxf.layer, 0) + 1
        if tipo in ("TEXT", "MTEXT"):
            testo = e.dxf.text if tipo == "TEXT" else e.plain_text()
            ins = e.dxf.insert if tipo == "TEXT" else e.dxf.insert
            testi.append((ins.x, ins.y, " ".join(str(testo).split())))
            continue
        if tipo == "DIMENSION":
            b = bbox_entita(e)
            if b:
                try:
                    mis = e.get_measurement()
                    if isinstance(mis, (int, float)):
                        quote.append(((b[0] + b[2]) / 2, (b[1] + b[3]) / 2,
                                      float(mis), e.dxf.text or ""))
                except Exception:
                    pass
            continue
        if tipo not in ("LINE", "LWPOLYLINE", "POLYLINE", "ARC", "CIRCLE",
                        "ELLIPSE", "SPLINE", "INSERT", "HATCH", "SOLID"):
            continue
        b = bbox_entita(e)
        if not b:
            continue
        geometrie.append((b, e.dxf.layer, tipo))
        if tipo == "LWPOLYLINE" and e.closed and len(e) in (4, 5):
            w, h = b[2] - b[0], b[3] - b[1]
            if w > 1 and h > 1:
                rettangoli.append((b, e.dxf.layer, w, h))

    if not geometrie:
        sys.exit("Nessuna geometria trovata nel modello (tavola vuota o tutto in paperspace?)")

    cluster = raggruppa_viste([g[0] for g in geometrie])

    # nome della vista: ogni testo PIANTA/PROSPETTO/SEZIONE si aggancia alla
    # vista piu' vicina (i titoli di solito stanno SOTTO il riquadro della vista)
    def distanza_da(c, x, y):
        dx = max(c[0] - x, 0, x - c[2])
        dy = max(c[1] - y, 0, y - c[3])
        return math.hypot(dx, dy)

    nomi = {i: None for i in range(len(cluster))}
    tavola_lato = max(max(c[2] for c in cluster) - min(c[0] for c in cluster),
                      max(c[3] for c in cluster) - min(c[1] for c in cluster))
    candidati = []  # (distanza pesata, indice testo, indice cluster, nome)
    for it, (x, y, t) in enumerate(testi):
        maiuscolo = t.upper()
        nome = next((n for chiave, n in PAROLE_VISTE.items() if chiave in maiuscolo), None)
        if not nome:
            continue
        if nome == "SEZIONE":
            m = re.search(r"SEZ\w*\.?\s*([A-Z](?:\s*[-–]\s*[A-Z]'?)?)", maiuscolo)
            if m and m.group(1).strip():
                nome = "SEZIONE " + m.group(1).replace(" ", "")
        for i, c in enumerate(cluster):
            d = distanza_da(c, x, y)
            if d > 0.25 * tavola_lato:
                continue
            # il titolo di una vista sta quasi sempre SOTTO il suo riquadro,
            # allineato in orizzontale: quel caso vince sulla pura distanza
            if y <= c[1] and c[0] - 0.05 * tavola_lato <= x <= c[2]:
                d *= 0.3
            candidati.append((d, it, i, nome))
    testi_usati, viste_usate = set(), set()
    for d, it, i, nome in sorted(candidati):
        if it in testi_usati or i in viste_usate:
            continue
        nomi[i] = nome
        testi_usati.add(it)
        viste_usate.add(i)
    for i in range(len(cluster)):
        nomi[i] = nomi[i] or f"VISTA_{chr(65 + i)}"

    # ingombri per vista
    righe = [f"ANALISI 2D — {Path(src).name}", "=" * 60, "",
             "LAYER (entita'):"]
    for lay, n in sorted(per_layer.items(), key=lambda kv: -kv[1]):
        righe.append(f"  {lay:40s} {n}")
    righe += ["", f"VISTE INDIVIDUATE: {len(cluster)}"]
    for i, c in enumerate(cluster):
        righe.append(f"  [{nomi[i]}] larg {c[2]-c[0]:.0f} x alt {c[3]-c[1]:.0f} "
                     f"(unita' disegno) — origine ({c[0]:.0f}, {c[1]:.0f})")

    righe += ["", f"QUOTE (DIMENSION) trovate: {len(quote)}"]
    for x, y, mis, override in sorted(quote, key=lambda q: -q[2])[:80]:
        vista = next((nomi[i] for i, c in enumerate(cluster) if dentro(x, y, c, 0)), "?")
        extra = f"  [testo: {override}]" if override and override != "<>" else ""
        righe.append(f"  {mis:10.1f}  in {vista}{extra}")

    righe += ["", f"RETTANGOLI CHIUSI (candidati pannelli/pezzi): {len(rettangoli)}"]
    for b, lay, w, h in sorted(rettangoli, key=lambda r: -(r[2] * r[3]))[:120]:
        vista = next((nomi[i] for i, c in enumerate(cluster)
                      if dentro((b[0]+b[2])/2, (b[1]+b[3])/2, c, 0)), "?")
        righe.append(f"  {w:8.1f} x {h:8.1f}  layer {lay:30s} in {vista} "
                     f"a ({b[0]:.0f}, {b[1]:.0f})")

    misure_testo = [t for t in testi if re.search(r"\d{2,}", t[2])]
    righe += ["", f"TESTI CON NUMERI (possibili quote a testo): {len(misure_testo)}"]
    for x, y, t in misure_testo[:60]:
        righe.append(f"  '{t[:70]}' a ({x:.0f}, {y:.0f})")

    # proposta d'ingombro: pianta = X/Y, prospetto = X/Z, sezione = Y/Z
    trova_vista = lambda nome: next((c for i, c in enumerate(cluster)
                                     if nomi[i].startswith(nome)), None)
    pianta, prospetto = trova_vista("PIANTA"), trova_vista("PROSPETTO")
    sezione = trova_vista("SEZIONE")
    L = P = H = None
    if pianta:
        L, P = pianta[2] - pianta[0], pianta[3] - pianta[1]
    if prospetto:
        L = L or prospetto[2] - prospetto[0]
        H = prospetto[3] - prospetto[1]
    if sezione:
        P = P or sezione[2] - sezione[0]
        H = H or sezione[3] - sezione[1]
    righe += ["", "PROPOSTA INGOMBRO (dai bbox delle viste, VERIFICARE con le quote):",
              f"  L {L:.0f} x P {P:.0f} x H {H:.0f} mm" if L and P and H else
              "  viste insufficienti per proporre un ingombro completo"]

    Path(str(out) + "_report.txt").write_text("\n".join(righe), encoding="utf-8")
    print("\n".join(righe[:14]))
    print(f"... report completo in {out.name}_report.txt")

    # bozza volumi.json: ingombro + un prisma per ogni rettangolo di pianta
    box = []
    if L and P and H:
        box.append({"nome": "INGOMBRO_da_verificare", "layer": "BOZZA", "colore": 8,
                    "tinta": "#d7d2c8", "x0": 0, "y0": 0, "z0": 0,
                    "x1": round(L, 1), "y1": round(P, 1), "z1": round(H, 1)})
    if pianta and H:
        for k, (b, lay, w, h) in enumerate(
                sorted((r for r in rettangoli
                        if dentro((r[0][0]+r[0][2])/2, (r[0][1]+r[0][3])/2, pianta, 0)),
                       key=lambda r: r[0][0])):
            box.append({"nome": f"PIANTA_R{k+1:02d}_{lay[:20]}", "layer": "BOZZA",
                        "colore": 8, "tinta": "#c9c4ba",
                        "x0": round(b[0] - pianta[0], 1), "y0": round(b[1] - pianta[1], 1),
                        "z0": 0, "x1": round(b[2] - pianta[0], 1),
                        "y1": round(b[3] - pianta[1], 1), "z1": round(H, 1)})
    bozza = {"titolo": f"BOZZA da {Path(src).name} — DA RIFINIRE (Fase A del protocollo)",
             "note": "Ingombro proposto dai bbox delle viste; i prismi PIANTA_R* sono i "
                     "rettangoli della pianta estrusi a tutta altezza: vanno tagliati in "
                     "altezza con le quote di prospetto/sezione e battezzati coi nomi veri.",
             "box": box}
    Path(str(out) + "_bozza.json").write_text(
        json.dumps(bozza, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Bozza volumi: {out.name}_bozza.json ({len(box)} box)")

    # tavola con le viste riquadrate
    fig, ax = plt.subplots(figsize=(14, 10), dpi=130)
    for b, lay, tipo in geometrie:
        ax.add_patch(Rectangle((b[0], b[1]), b[2]-b[0], b[3]-b[1],
                               fill=False, linewidth=0.15, edgecolor="#888888"))
    colori = ["#c0392b", "#2471a3", "#1e8449", "#af601a", "#6c3483", "#117864"]
    for i, c in enumerate(cluster):
        ax.add_patch(Rectangle((c[0], c[1]), c[2]-c[0], c[3]-c[1], fill=False,
                               linewidth=1.6, edgecolor=colori[i % len(colori)]))
        ax.text(c[0], c[3], " " + nomi[i], fontsize=10, va="bottom",
                color=colori[i % len(colori)], weight="bold")
    ax.autoscale(); ax.set_aspect("equal"); ax.set_axis_off()
    ax.set_title(f"Viste individuate in {Path(src).name}")
    fig.tight_layout()
    fig.savefig(str(out) + "_viste.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Tavola riquadrata: {out.name}_viste.png")


if __name__ == "__main__":
    main()
