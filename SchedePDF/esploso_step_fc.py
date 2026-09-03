# -*- coding: utf-8 -*-
"""Gira DENTRO freecadcmd: dal file STEP del mobile tira fuori i box di
tutti i solidi (bbox min/max) in coordinate d'assieme -> JSON.

uso: freecadcmd esploso_step_fc.py -- <step> <out.json>
"""
import json
import sys

import Part


def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[-2:]
    step, out = argv[0], argv[1]
    forma = Part.Shape()
    forma.read(step)
    pezzi = []
    for s in forma.Solids:
        bb = s.BoundBox
        p = {"min": [bb.XMin, bb.YMin, bb.ZMin],
             "max": [bb.XMax, bb.YMax, bb.ZMax],
             "vol": s.Volume}
        # facce piane VERE (contorno esterno + fori) per disegnare
        # l'esploso com'e' fatto il pezzo, non a scatole
        facce, fori = [], []
        try:
            for f in s.Faces:
                if not isinstance(f.Surface, Part.Plane):
                    continue
                ow = f.OuterWire
                pts = [(v.x, v.y, v.z)
                       for v in ow.discretize(Deflection=1.0)]
                if len(pts) >= 3:
                    facce.append({"pts": pts})
                for w in f.Wires:
                    if w.isSame(ow):
                        continue
                    ps = [(v.x, v.y, v.z)
                          for v in w.discretize(Deflection=1.0)]
                    if len(ps) >= 3:
                        fori.append(ps)
        except Exception:
            facce, fori = [], []
        if facce:
            p["facce"] = facce
            p["fori"] = fori
        pezzi.append(p)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(pezzi, f)
    print(f"ESPLOSO-OK {len(pezzi)} solidi")


main()
