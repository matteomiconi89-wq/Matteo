#!/usr/bin/env python3
# Dump misure scocca 26A011: bbox reali per mesh/layer + export geometry.json.
# Uso: python3 analizza_scocca.py   (richiede: pip install ezdxf)
import json, pathlib
from collections import defaultdict

import ezdxf

BASE = pathlib.Path(__file__).parent
FILES = [("aperto", BASE / "dxf" / "scocca_26A011_rev06_aperto.dxf"),
         ("chiuso", BASE / "dxf" / "scocca_26A011_rev06_chiuso.dxf")]

geo = {}
for name, path in FILES:
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    L = defaultdict(list)
    out = []
    for e in msp:
        if e.dxftype() != "MESH":
            continue
        verts = [[round(v[0], 1), round(v[1], 1), round(v[2], 1)] for v in e.vertices]
        faces = [list(map(int, f)) for f in e.faces]
        out.append({"l": e.dxf.layer, "v": verts, "f": faces})
        xs = [v[0] for v in verts]; ys = [v[1] for v in verts]; zs = [v[2] for v in verts]
        L[e.dxf.layer].append((min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
    geo[name] = out

    print("=" * 110)
    print(f"CONFIGURAZIONE: {name.upper()}  ({len(out)} mesh)")
    for layer in sorted(L):
        print(f"\n [{layer}]")
        for (x0, x1, y0, y1, z0, z1) in sorted(L[layer]):
            print(f"   X[{x0:8.1f},{x1:8.1f}] l={x1-x0:7.1f} | "
                  f"Y[{y0:7.1f},{y1:7.1f}] p={y1-y0:7.1f} | "
                  f"Z[{z0:7.1f},{z1:7.1f}] h={z1-z0:7.1f}")

(BASE / "geometry.json").write_text(json.dumps(geo, separators=(",", ":")))
print("\nscritto geometry.json")
