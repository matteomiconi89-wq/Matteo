# -*- coding: utf-8 -*-
"""Gira DENTRO freecadcmd: pesca dal file STEP del MOBILE il solido con le
quote richieste, lo porta in coordinate programma (origine 0,0,0, lato
lungo su X, spessore su Z) scegliendo tra i 4 RIBALTAMENTI possibili
quello in cui i FORI del solido combaciano coi fori del programma,
e lo esporta in BRep testuale.

uso: freecadcmd estrai_solido_step_fc.py -- <step> <lung> <larg> <alt>
     <out.brep> [fori.json]
fori.json = [[x, y], ...] dei fori verticali del programma (frame A)
"""
import json
import math
import sys

import Part
from FreeCAD import Base


def fori_verticali(solido):
    """Centri (x,y) degli assi dei cilindri ~verticali del solido."""
    out = []
    for f in solido.Faces:
        try:
            surf = f.Surface
            if surf.TypeId != "Part::GeomCylinder":
                continue
            ax = surf.Axis
            if abs(ax.z) < 0.99:
                continue
            c = surf.Center
            out.append((c.x, c.y))
        except Exception:
            continue
    return out


def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[-6:]
    step, lung, larg, alt, out = (argv[0], float(argv[1]), float(argv[2]),
                                  float(argv[3]), argv[4])
    fori_att = []
    if len(argv) > 5:
        fori_att = json.load(open(argv[5], encoding="utf-8"))
    forma = Part.Shape()
    forma.read(step)
    voluto = sorted((lung, larg, alt), reverse=True)
    scelto = None
    for s in forma.Solids:
        bb = s.BoundBox
        d = sorted((bb.XLength, bb.YLength, bb.ZLength), reverse=True)
        if all(abs(a - b) < 0.5 for a, b in zip(d, voluto)):
            scelto = s
            break
    if scelto is None:
        raise RuntimeError(f"nessun solido {voluto} nello step "
                           f"({len(forma.Solids)} solidi)")
    bb = scelto.BoundBox
    dims = [bb.XLength, bb.YLength, bb.ZLength]
    ordine = sorted(range(3), key=lambda i: -dims[i])
    base = scelto.copy()
    if ordine[2] == 0:
        base.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 1, 0), 90)
    elif ordine[2] == 1:
        base.rotate(Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), 90)
    bb = base.BoundBox
    if bb.XLength < bb.YLength:
        base.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 90)

    def punteggio(sol):
        """Quanti fori del programma trovano un cilindro nel solido."""
        if not fori_att:
            return 0
        fs = fori_verticali(sol)
        n = 0
        for x, y in fori_att:
            if any(abs(x - fx) < 0.6 and abs(y - fy) < 0.6 for fx, fy in fs):
                n += 1
        return n

    migliore, migliore_p = None, -1
    for rx in (0, 180):
        for rz in (0, 180):                 # 4 ribaltamenti propri
            s = base.copy()
            if rx:
                s.rotate(Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), 180)
            if rz:
                s.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 180)
            b = s.BoundBox
            s.translate(Base.Vector(-b.XMin, -b.YMin, -b.ZMin))
            p = punteggio(s)
            if p > migliore_p:
                migliore, migliore_p = s, p
    solido = max(migliore.Solids, key=lambda x: x.Volume)

    # CUOCI la trasformazione NELLA geometria: rotazioni/traslazioni di
    # FreeCAD stanno nel Placement (= location nel BRep) e a woodWOP la
    # location del solido non va giu'. transformed() = BRepBuilderAPI
    # rigido che PRESERVA piani e cilindri (transformGeometry li
    # convertirebbe in NURBS: file doppio e fori irriconoscibili)
    M = solido.Placement.toMatrix()
    s0 = solido.copy()
    s0.Placement = Base.Placement()
    try:
        finale = s0.transformed(M, copy=True)
    except Exception:
        finale = s0.transformGeometry(M)
    finale.Placement = Base.Placement()
    bb = finale.BoundBox
    # se la cottura non e' andata come previsto, riallinea a 0
    if max(abs(bb.XMin), abs(bb.YMin), abs(bb.ZMin)) > 0.01:
        sposta = Base.Matrix()
        sposta.move(Base.Vector(-bb.XMin, -bb.YMin, -bb.ZMin))
        try:
            finale = finale.transformed(sposta, copy=True)
        except Exception:
            finale = finale.transformGeometry(sposta)
        bb = finale.BoundBox
    p2 = punteggio(finale)
    finale.exportBrep(out)
    print(f"BREP-OK {bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f}, "
          f"{len(finale.Faces)} facce, fori combacianti {migliore_p}"
          f"/{len(fori_att)} (dopo cottura {p2}), "
          f"min ({bb.XMin:.2f},{bb.YMin:.2f},{bb.ZMin:.2f})")


main()
