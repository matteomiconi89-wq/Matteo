# -*- coding: utf-8 -*-
# Estrattore per lo studio ferramenta.
# Prende SOLO le Part::Feature foglia (i contenitori App::Part duplicano i figli),
# porta ogni shape in coordinate GLOBALI (i blocchi ferramenta sono annidati con
# placement propri), ed estrae i fori come segmenti coassiali SEPARATI:
# stessa (dir, raggio, asse) ma intervalli assiali staccati = fori distinti.
# Uso: freecadcmd estrai_ferramenta.py  con env FILES_LIST (";"-sep) e OUT_JSON
import os, json
import FreeCAD as App
from FreeCAD import Base

FILES = [f for f in os.environ["FILES_LIST"].split(";") if f.strip()]
OUT = os.environ["OUT_JSON"]
GAP = 0.5  # mm: tolleranza per fondere segmenti dello stesso foro

def axdir(d):
    for name, v in (("X", Base.Vector(1, 0, 0)), ("Y", Base.Vector(0, 1, 0)), ("Z", Base.Vector(0, 0, 1))):
        if abs(abs(d.dot(v)) - 1.0) < 1e-6:
            return name
    return "OBL"

def catena_padri(o):
    """Risale i contenitori App::Part fino alla radice."""
    out = []
    cur = o
    for _ in range(20):
        pads = [p for p in cur.InList if p.TypeId == "App::Part" and hasattr(p, "Group") and cur in p.Group]
        if not pads:
            break
        cur = pads[0]
        out.append(cur.Label)
    return out

def estrai_fori(sh):
    """Fori = facce cilindriche raggruppate per asse; segmenti staccati = fori diversi."""
    assi = {}
    for face in sh.Faces:
        surf = face.Surface
        if surf.__class__.__name__ != "Cylinder":
            continue
        c, d, r = surf.Center, surf.Axis, surf.Radius
        dn = axdir(d)
        fb = face.BoundBox
        if dn == "X":
            key = (dn, round(r, 2), round(c.y, 1), round(c.z, 1))
            lo, hi = fb.XMin, fb.XMax
        elif dn == "Y":
            key = (dn, round(r, 2), round(c.x, 1), round(c.z, 1))
            lo, hi = fb.YMin, fb.YMax
        elif dn == "Z":
            key = (dn, round(r, 2), round(c.x, 1), round(c.y, 1))
            lo, hi = fb.ZMin, fb.ZMax
        else:
            key = (dn, round(r, 2), round(c.x, 1), round(c.y, 1), round(c.z, 1),
                   round(d.x, 3), round(d.y, 3), round(d.z, 3))
            lo, hi = -1.0, -1.0  # niente segmentazione per gli obliqui
        e = assi.setdefault(key, {"dir": dn, "dia": round(2 * r, 2),
                                  "cx": round(c.x, 2), "cy": round(c.y, 2), "cz": round(c.z, 2),
                                  "segs": []})
        if dn == "OBL":
            e["asse"] = [round(d.x, 3), round(d.y, 3), round(d.z, 3)]
        e["segs"].append((lo, hi))
    fori = []
    for e in assi.values():
        segs = sorted(e.pop("segs"))
        fusi = []
        for lo, hi in segs:
            if fusi and lo <= fusi[-1][1] + GAP:
                fusi[-1][1] = max(fusi[-1][1], hi)
            else:
                fusi.append([lo, hi])
        for lo, hi in fusi:
            f = dict(e)
            f["lo"] = round(lo, 2)
            f["hi"] = round(hi, 2)
            f["len"] = round(hi - lo, 2)
            if f["dir"] == "X":
                f["cx"] = round((lo + hi) / 2, 2)
            elif f["dir"] == "Y":
                f["cy"] = round((lo + hi) / 2, 2)
            elif f["dir"] == "Z":
                f["cz"] = round((lo + hi) / 2, 2)
            fori.append(f)
    fori.sort(key=lambda h: (h["dir"], h["dia"], h["cx"], h["cy"], h["cz"]))
    return fori

result = {}
if os.path.exists(OUT):
    result = json.load(open(OUT, encoding="utf-8"))

for f in FILES:
    key = os.path.basename(f)
    if key in result:
        continue
    try:
        doc = App.newDocument("fx")
        import Import
        Import.insert(f, doc.Name)
        pezzi = {}
        for o in doc.Objects:
            if o.TypeId != "Part::Feature":
                continue
            if not (hasattr(o, "Shape") and o.Shape.Solids):
                continue
            sh = o.Shape.copy()
            try:
                m = o.getGlobalPlacement().toMatrix().multiply(o.Placement.toMatrix().inverse())
                sh.transformShape(m)
            except Exception:
                pass
            bb = sh.BoundBox
            dims = sorted([bb.XLength, bb.YLength, bb.ZLength])
            boxvol = bb.XLength * bb.YLength * bb.ZLength / 1000.0
            vol = sh.Volume / 1000.0
            lab = o.Label
            n = 1
            while lab in pezzi:
                lab = f"{o.Label}__{n}"
                n += 1
            pezzi[lab] = {
                "padri": catena_padri(o),
                "n_solidi": len(sh.Solids),
                "bbox": [round(bb.XMin, 2), round(bb.YMin, 2), round(bb.ZMin, 2),
                         round(bb.XMax, 2), round(bb.YMax, 2), round(bb.ZMax, 2)],
                "dims_ord": [round(x, 2) for x in dims],
                "vol_cm3": round(vol, 1),
                "is_box_like": abs(vol - boxvol) < 0.05 * boxvol if boxvol else False,
                "n_facce": len(sh.Faces),
                "fori": estrai_fori(sh),
            }
        result[key] = {"pezzi": pezzi}
        App.closeDocument(doc.Name)
    except Exception as ex:
        result[key] = {"error": str(ex)}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, ensure_ascii=False)
    print("FATTO", key, len(result.get(key, {}).get("pezzi", {})), "pezzi")

print("SCRITTO", OUT)
