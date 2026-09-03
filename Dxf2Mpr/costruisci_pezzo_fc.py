# -*- coding: utf-8 -*-
"""Gira DENTRO freecadcmd: legge pezzo.json (quote + lavorazioni in
coordinate programma A) e ricostruisce il SOLIDO del pezzo finito,
esportandolo in BRep testuale (CASCADE Topology) per l'MPRX.

uso: freecadcmd costruisci_pezzo_fc.py -- <pezzo.json> <out.brep>
"""
import json
import math
import sys

import Part
from FreeCAD import Base


def vec(x, y, z):
    return Base.Vector(float(x), float(y), float(z))


def faccia_da_contorno(punti, tratti, z):
    """Faccia piana a quota z dal contorno (archi VERI se ci sono i tratti)."""
    spigoli = []
    if tratti:
        prev = tuple(punti[0])
        for t in tratti:
            if t[0] == "L":
                fine = tuple(t[1])
                if math.hypot(fine[0]-prev[0], fine[1]-prev[1]) > 1e-6:
                    spigoli.append(Part.LineSegment(
                        vec(prev[0], prev[1], z),
                        vec(fine[0], fine[1], z)).toShape())
                prev = fine
            else:
                fine, medio = tuple(t[1]), tuple(t[2])
                spigoli.append(Part.Arc(
                    vec(prev[0], prev[1], z),
                    vec(medio[0], medio[1], z),
                    vec(fine[0], fine[1], z)).toShape())
                prev = fine
        # chiusura
        first = tuple(punti[0])
        if math.hypot(first[0]-prev[0], first[1]-prev[1]) > 1e-6:
            spigoli.append(Part.LineSegment(
                vec(prev[0], prev[1], z),
                vec(first[0], first[1], z)).toShape())
        filo = Part.Wire(Part.__sortEdges__(spigoli))
    else:
        pts = [vec(p[0], p[1], z) for p in punti]
        if (pts[0] - pts[-1]).Length > 1e-6:
            pts.append(pts[0])
        filo = Part.makePolygon(pts)
    return Part.Face(filo)


def main():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = argv[-2:]
    dati = json.load(open(argv[0], encoding="utf-8"))
    out_brep = argv[1]

    lung, larg, alt = dati["dims"]
    pezzo = Part.makeBox(lung, larg, alt)

    # --- profilo sagomato: si tiene solo cio' che sta nel contorno --------
    for sg in dati.get("sagome", []):
        prisma = faccia_da_contorno(sg["contorno"], sg.get("tratti"),
                                    -1.0).extrude(vec(0, 0, alt + 2))
        pezzo = pezzo.common(prisma)

    # --- biselli: taglio con piano inclinato ------------------------------
    # la linea t sta sul bordo della faccia SUPERIORE; il cuneo da togliere
    # sta FUORI dalla linea (a sinistra del verso di percorrenza).
    # Frame locale: X'=verso linea, Y'=fuori, Z'=su, origine (x1,y1,alt);
    # il coltello e' un box col piano interno su Y'=0, poi inclinato di
    # beta attorno a X' (+beta se largo sotto, -beta se largo sopra)
    for c in dati.get("biselli", []):
        (x1, y1), (x2, y2) = c["t1"], c["t2"]
        beta = float(c["beta"])
        ll = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / ll, (y2 - y1) / ll
        ang = math.degrees(math.atan2(uy, ux))
        colt = Part.makeBox(ll + 400, 3 * alt + 200, alt + 400,
                            vec(-200, 0, -(alt + 200)))
        segno = 1.0 if not c.get("largo_sopra") else -1.0
        rot = (Base.Rotation(vec(0, 0, 1), ang)
               .multiply(Base.Rotation(vec(1, 0, 0), segno * beta)))
        colt.Placement = Base.Placement(vec(x1, y1, alt), rot)
        pezzo = pezzo.cut(colt)

    # --- tasche sopra/sotto ----------------------------------------------
    for s in dati.get("tasche", []):
        prof = min(float(s["prof"]), alt + 10)
        if s["lato"] == "sopra":
            z0, dz = alt - prof, prof + 5
        else:
            z0, dz = -5.0, prof + 5
        if s.get("cir"):
            ut = Part.makeCylinder(s["r"], dz, vec(s["x"], s["y"], z0))
        elif "contorno" in s:
            ut = faccia_da_contorno(s["contorno"], s.get("tratti"),
                                    z0).extrude(vec(0, 0, dz))
        else:
            ut = Part.makeBox(s["x2"] - s["x1"], s["y2"] - s["y1"], dz,
                              vec(s["x1"], s["y1"], z0))
        pezzo = pezzo.cut(ut)

    # --- fori verticali ---------------------------------------------------
    for f in dati.get("fori_vert", []):
        prof = min(float(f["prof"]), alt + 10)
        if f["lato"] == "sopra":
            base = vec(f["x"], f["y"], alt - prof)
        else:
            base = vec(f["x"], f["y"], -2)
        pezzo = pezzo.cut(Part.makeCylinder(f["r"], prof + 2, base))

    # --- fori orizzontali (bordi) ----------------------------------------
    DIR = {1: (0, -1, 0), 2: (0, 1, 0), 3: (1, 0, 0), 4: (-1, 0, 0)}
    for f in dati.get("fori_lat", []):
        p = f["plane"]
        d = DIR[p]
        if p == 1:
            base = vec(f["x"], larg + 1, f["z"])
        elif p == 2:
            base = vec(f["x"], -1, f["z"])
        elif p == 3:
            base = vec(-1, f["x"], f["z"])
        else:
            base = vec(lung + 1, f["x"], f["z"])
        pezzo = pezzo.cut(Part.makeCylinder(
            f["r"], float(f["prof"]) + 1, base, vec(*d)))

    # --- lamate di sezionatura (frontali uniti): fughe passanti -----------
    for t in dati.get("lamate", []):
        pezzo = pezzo.cut(Part.makeBox(
            t["gap"], larg + 20, alt + 20, vec(t["x"], -10, -10)))

    if pezzo.isNull() or not pezzo.Solids:
        raise RuntimeError("solido vuoto dopo le lavorazioni")
    # esporta il SOLIDO nudo (il cut puo' restituire un Compound: l'MPRX
    # vuole la radice So, non Co)
    solido = max(pezzo.Solids, key=lambda s: s.Volume)
    solido.exportBrep(out_brep)
    print("BREP-OK", len(pezzo.Solids), "solidi,",
          len(solido.Faces), "facce")


main()
