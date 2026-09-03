# -*- coding: utf-8 -*-
"""Facce cilindriche del blocco: per capire dove sta l'asse tazza Ø35 e quali
solidi sono lavorazioni. env BLOCCO = nome file in blocchi_hafele."""
import os
import FreeCAD as App
import Import

STP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "blocchi_hafele", os.environ["BLOCCO"])
doc = App.newDocument("cil")
Import.insert(STP, doc.Name)
for o in doc.Objects:
    if not (hasattr(o, "Shape") and o.Shape.Solids):
        continue
    sh = o.Shape
    print(f"=== {o.Label}  vol={sh.Volume/1000:.2f}cm3  facce={len(sh.Faces)} ===")
    visti = set()
    for f in sh.Faces:
        s = f.Surface
        if s.__class__.__name__ != "Cylinder":
            continue
        c, d, r = s.Center, s.Axis, s.Radius
        key = (round(r, 1), round(c.x, 1), round(c.y, 1), round(c.z, 1))
        if key in visti:
            continue
        visti.add(key)
        if r >= 1.0:
            print(f"   cil r={r:6.2f} centro=({c.x:7.2f},{c.y:7.2f},{c.z:7.2f}) asse=({d.x:+.2f},{d.y:+.2f},{d.z:+.2f})")
