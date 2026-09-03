# -*- coding: utf-8 -*-
"""Ispeziona il blocco Häfele scaricato: oggetti, solidi, bbox, dove sta l'origine."""
import os
import FreeCAD as App
import Import

STP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "blocchi_hafele", os.environ.get("BLOCCO", "262_34_302_RAFIX_TAB_20_S_NERO.stp"))
doc = App.newDocument("blk")
Import.insert(STP, doc.Name)
print("OGGETTI:", len(doc.Objects))
for o in doc.Objects:
    if hasattr(o, "Shape") and o.Shape is not None:
        sh = o.Shape
        ns = len(sh.Solids)
        bb = sh.BoundBox
        print(f"  {o.TypeId.split('::')[-1]:10s} {o.Label[:40]:40s} sol={ns} "
              f"X[{bb.XMin:7.2f},{bb.XMax:7.2f}] Y[{bb.YMin:7.2f},{bb.YMax:7.2f}] Z[{bb.ZMin:7.2f},{bb.ZMax:7.2f}]"
              + (f" vol={sh.Volume/1000:.2f}cm3" if ns else ""))
    else:
        print(f"  {o.TypeId:28s} {o.Label[:40]}")
