# -*- coding: utf-8 -*-
# Ricognizione struttura STEP: per ogni file dumpa TUTTI gli oggetti
# (label, tipo, n_solidi, bbox, dims, volume, padri/figli) senza filtri.
# Uso: freecadcmd ricognizione.py  con env FILES_LIST (";"-sep) e OUT_JSON
import os, json
import FreeCAD as App

FILES = [f for f in os.environ["FILES_LIST"].split(";") if f.strip()]
OUT = os.environ["OUT_JSON"]

result = {}
if os.path.exists(OUT):
    result = json.load(open(OUT, encoding="utf-8"))

for f in FILES:
    key = os.path.basename(f)
    if key in result:
        continue
    try:
        doc = App.newDocument("ric")
        import Import
        Import.insert(f, doc.Name)
        objs = []
        for o in doc.Objects:
            e = {"label": o.Label, "tipo": o.TypeId}
            try:
                figli = getattr(o, "Group", None)
                if figli:
                    e["figli"] = [c.Label for c in figli]
            except Exception:
                pass
            padri = [p.Label for p in o.InList]
            if padri:
                e["padri"] = padri
            if hasattr(o, "Shape") and o.Shape is not None:
                sh = o.Shape
                ns = len(sh.Solids)
                e["n_solidi"] = ns
                e["n_facce"] = len(sh.Faces)
                if ns or sh.Faces:
                    bb = sh.BoundBox
                    e["bbox"] = [round(bb.XMin, 1), round(bb.YMin, 1), round(bb.ZMin, 1),
                                 round(bb.XMax, 1), round(bb.YMax, 1), round(bb.ZMax, 1)]
                    e["dims"] = sorted([round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)])
                    try:
                        e["vol_cm3"] = round(sh.Volume / 1000.0, 2)
                    except Exception:
                        pass
            objs.append(e)
        result[key] = {"n_oggetti": len(objs), "oggetti": objs}
        App.closeDocument(doc.Name)
    except Exception as ex:
        result[key] = {"error": str(ex)}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, ensure_ascii=False)
    print("FATTO", key)

print("SCRITTO", OUT, len(result), "file")
