# -*- coding: utf-8 -*-
"""Verifica il montaggio dei blocchi cerniera Blum nel MOBILE_DEMO:
la tazza Ø35 (asse Y) di ogni blocco deve coincidere col foro tazza dell'anta.
Uso: freecadcmd verifica_montaggio.py"""
import os
import FreeCAD as App
import Import

STP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MOBILE_DEMO.stp")
doc = App.newDocument("v")
Import.insert(STP, doc.Name)

def tazze_di(shape):
    out = []
    for f in shape.Faces:
        s = f.Surface
        if s.__class__.__name__ != "Cylinder":
            continue
        if abs(s.Radius - 17.5) > 1.5:
            continue
        d = s.Axis
        asse = "Y" if abs(abs(d.y) - 1) < 1e-3 else ("X" if abs(abs(d.x) - 1) < 1e-3 else ("Z" if abs(abs(d.z) - 1) < 1e-3 else "OBL"))
        c = s.Center
        out.append((asse, round(c.x, 1), round(c.y, 1), round(c.z, 1)))
    return out

# fori tazza nelle ante (dai pannelli 08/09) e tazze nei blocchi cerniera
fori_anta = []
blocchi_taz = []
for o in doc.Objects:
    if not (hasattr(o, "Shape") and o.Shape.Solids):
        continue
    lab = o.Label
    if "Anta" in lab:
        for t in tazze_di(o.Shape):
            fori_anta.append(t)
    if "CERNIERA" in lab.upper():
        for t in set(tazze_di(o.Shape)):
            blocchi_taz.append((lab, t))

print(f"Fori tazza nelle ante: {len(set(fori_anta))}")
for t in sorted(set(fori_anta)):
    print(f"   anta  {t}")
print(f"\nTazze nei blocchi cerniera: {len(blocchi_taz)}")
ok = 0
for lab, t in sorted(blocchi_taz):
    # cerca un foro anta con stesso (x,z) entro 2mm, asse Y
    match = any(t[0] == "Y" and abs(t[1] - fa[1]) < 2 and abs(t[3] - fa[3]) < 2
                for fa in fori_anta)
    stato = "OK" if match else "NO-MATCH"
    if match:
        ok += 1
    print(f"   {stato:8s} {lab[:34]:34s} tazza asse={t[0]} c=({t[1]},{t[2]},{t[3]})")
print(f"\nTazze blocco allineate al foro anta: {ok}/{len(blocchi_taz)}")

print("\n=== VERSO del corpo cerniera (bbox): il corpo deve stare a Y>-3 (interno) e verso il fianco ===")
for o in doc.Objects:
    if not (hasattr(o, "Shape") and o.Shape.Solids):
        continue
    if "CERNIERA" not in o.Label.upper():
        continue
    bb = o.Shape.BoundBox
    verso_ok = bb.YMax > 10          # il corpo si estende verso l'interno
    fronte_bad = bb.YMin < -30       # sbuca troppo davanti al fronte
    stato = "OK" if (verso_ok and not fronte_bad) else "VERSO-DUBBIO"
    print(f"   {stato:12s} {o.Label[:26]:26s} X[{bb.XMin:.0f},{bb.XMax:.0f}] "
          f"Y[{bb.YMin:.0f},{bb.YMax:.0f}] Z[{bb.ZMin:.0f},{bb.ZMax:.0f}]")
