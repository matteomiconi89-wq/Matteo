# Estrae da una lista di STEP: pannelli (bbox, volume, spessore) + fori (asse, dia, quota, prof)
# Uso: freecadcmd estrai_batch.py  con env FILES_LIST (file separati da ;) e OUT_JSON
import os, json, sys
import FreeCAD as App
import Part
from FreeCAD import Base

FILES = [f for f in os.environ["FILES_LIST"].split(";") if f.strip()]
OUT = os.environ["OUT_JSON"]

def axdir(d):
    for name, v in (("X", Base.Vector(1,0,0)), ("Y", Base.Vector(0,1,0)), ("Z", Base.Vector(0,0,1))):
        if abs(abs(d.dot(v)) - 1.0) < 1e-6:
            return name
    return "OBL"

result = {}
for f in FILES:
    key = os.path.basename(f)
    try:
        doc = App.newDocument("an")
        import Import
        Import.insert(f, doc.Name)
        panels = {}
        assembly = None
        for obj in doc.Objects:
            if not (hasattr(obj, "Shape") and obj.Shape.Solids):
                continue
            lab = obj.Label
            sh = obj.Shape
            bb = sh.BoundBox
            info_bb = [round(bb.XMin,2), round(bb.YMin,2), round(bb.ZMin,2),
                       round(bb.XMax,2), round(bb.YMax,2), round(bb.ZMax,2)]
            # l'assieme totale: quello con piu' solidi
            if len(sh.Solids) > 3:
                if assembly is None or len(sh.Solids) > assembly["nsolids"]:
                    assembly = {"label": lab, "nsolids": len(sh.Solids), "bbox": info_bb,
                                "volume_cm3": round(sh.Volume/1000.0,1)}
                if lab.startswith("J-") or lab.endswith("_ASM") or len(sh.Solids) > 3:
                    continue
            if lab.startswith("SOLID"):
                continue
            holes = {}
            for face in sh.Faces:
                surf = face.Surface
                if surf.__class__.__name__ != "Cylinder":
                    continue
                c = surf.Center; d = surf.Axis
                dn = axdir(d); r = round(surf.Radius, 2)
                if dn == "X":
                    k = (dn, r, round(c.y,1), round(c.z,1)); lo, hi = face.BoundBox.XMin, face.BoundBox.XMax
                elif dn == "Y":
                    k = (dn, r, round(c.x,1), round(c.z,1)); lo, hi = face.BoundBox.YMin, face.BoundBox.YMax
                elif dn == "Z":
                    k = (dn, r, round(c.x,1), round(c.y,1)); lo, hi = face.BoundBox.ZMin, face.BoundBox.ZMax
                else:
                    k = ("OBL", r, round(c.x,1), round(c.y,1)); lo, hi = 0, 0
                e = holes.setdefault(k, {"dir": dn, "dia": round(2*r,2),
                                         "cx": round(c.x,2), "cy": round(c.y,2), "cz": round(c.z,2),
                                         "lo": lo, "hi": hi})
                e["lo"] = min(e["lo"], lo); e["hi"] = max(e["hi"], hi)
            hl = []
            for e in holes.values():
                e["len"] = round(e["hi"] - e["lo"], 2)
                e["lo"] = round(e["lo"],2); e["hi"] = round(e["hi"],2)
                hl.append(e)
            hl.sort(key=lambda h: (h["dir"], h["dia"], h["cx"], h["cy"], h["cz"]))
            # volume box teorico per capire se e' un semplice parallelepipedo
            dims = sorted([bb.XLength, bb.YLength, bb.ZLength])
            boxvol = bb.XLength*bb.YLength*bb.ZLength/1000.0
            panels[lab] = {
                "bbox": info_bb,
                "dims_ord": [round(x,2) for x in dims],
                "volume_cm3": round(sh.Volume/1000.0,1),
                "boxvol_cm3": round(boxvol,1),
                "is_box_like": abs(sh.Volume/1000.0 - boxvol) < 0.05*boxvol,
                "n_faces": len(sh.Faces),
                "n_fori": len(hl),
                "fori": hl,
            }
        result[key] = {"assembly": assembly, "panels": panels}
        App.closeDocument(doc.Name)
    except Exception as ex:
        result[key] = {"error": str(ex)}

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, indent=1, ensure_ascii=False)
print("SCRITTO", OUT, len(result), "file")
