# -*- coding: utf-8 -*-
"""Analizza l'orientamento dei blocchi della libreria per il montaggio:
per ogni file trova bbox globale, tazze Ø35 (asse+centro), fori Ø5 e cilindri
notevoli, così so come ruotare/traslare il blocco nel mobile.
Uso: freecadcmd orienta_blocchi.py  (env FILES = "path1;path2;...")
"""
import os
import FreeCAD as App
import Import

FILES = [f for f in os.environ["FILES"].split(";") if f.strip()]

def asse_nome(d):
    for n, v in (("X", (1, 0, 0)), ("Y", (0, 1, 0)), ("Z", (0, 0, 1))):
        if abs(abs(d.x * v[0] + d.y * v[1] + d.z * v[2]) - 1.0) < 1e-4:
            return n
    return "OBL"

for path in FILES:
    doc = App.newDocument("o")
    Import.insert(path, doc.Name)
    solidi = [o for o in doc.Objects if hasattr(o, "Shape") and o.Shape.Solids]
    # bbox globale
    import Part
    comp = Part.makeCompound([o.Shape for o in solidi])
    bb = comp.BoundBox
    print(f"\n=== {os.path.basename(path)} ===")
    print(f"  bbox X[{bb.XMin:.1f},{bb.XMax:.1f}] Y[{bb.YMin:.1f},{bb.YMax:.1f}] Z[{bb.ZMin:.1f},{bb.ZMax:.1f}]"
          f"  dims={bb.XLength:.1f}x{bb.YLength:.1f}x{bb.ZLength:.1f}")
    # cilindri notevoli (raggruppati per raggio/asse)
    visti = set()
    for o in solidi:
        for f in o.Shape.Faces:
            s = f.Surface
            if s.__class__.__name__ != "Cylinder":
                continue
            r = s.Radius
            if r < 2.4:
                continue
            c, d = s.Center, s.Axis
            key = (round(r, 1), round(c.x, 0), round(c.y, 0), round(c.z, 0), asse_nome(d))
            if key in visti:
                continue
            visti.add(key)
            tag = "TAZZA35" if abs(r - 17.5) < 1.5 else ("PERNO" if abs(r - 4) < 1 else f"Ø{2*r:.0f}")
            print(f"  cil r={r:5.2f} d{2*r:5.1f} {tag:8s} centro=({c.x:6.1f},{c.y:6.1f},{c.z:6.1f}) asse={asse_nome(d)}")
    App.closeDocument(doc.Name)
