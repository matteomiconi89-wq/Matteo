#!/usr/bin/env python3
"""Analisi DXF per protocollo render: layer, blocchi con bbox, testi, estensioni."""
import sys
from collections import Counter

import ezdxf
from ezdxf import bbox as ezbbox

path = sys.argv[1]
doc = ezdxf.readfile(path)
msp = doc.modelspace()

print(f"=== {path} ===")
print(f"Versione DXF: {doc.dxfversion}  ({doc.acad_release})")
print(f"Unità INSUNITS: {doc.header.get('$INSUNITS', '?')}")

print("\n--- LAYER ---")
for layer in sorted(doc.layers, key=lambda l: l.dxf.name):
    print(f"  {layer.dxf.name}  colore={layer.dxf.color}  {'OFF' if layer.is_off() else 'on'}{'  FROZEN' if layer.is_frozen() else ''}")

print("\n--- ENTITÀ IN MODELSPACE (per tipo) ---")
counts = Counter(e.dxftype() for e in msp)
for t, n in counts.most_common():
    print(f"  {t}: {n}")

print("\n--- ENTITÀ PER LAYER ---")
lcounts = Counter(e.dxf.layer for e in msp)
for t, n in lcounts.most_common(40):
    print(f"  {t}: {n}")

print("\n--- BLOCCHI (INSERT) con bbox ---")
inserts = [e for e in msp if e.dxftype() == "INSERT"]
rows = []
for ins in inserts:
    name = ins.dxf.name
    try:
        cache = ezbbox.Cache()
        box = ezbbox.extents(ins.virtual_entities(), cache=cache)
        if box.has_data:
            (x0, y0, _z0), (x1, y1, _z1) = box.extmin, box.extmax
            rows.append((x0, name, x0, y0, x1, y1, x1 - x0, y1 - y0, ins.dxf.layer))
    except Exception as exc:  # noqa: BLE001
        rows.append((getattr(ins.dxf, "insert", (0, 0, 0))[0], name, None, None, None, None, None, None, f"ERRORE: {exc}"))
rows.sort(key=lambda r: r[0])
for r in rows:
    if r[2] is None:
        print(f"  {r[1]}  [{r[8]}]")
    else:
        print(f"  {r[1]}  X {r[2]:.0f}..{r[4]:.0f}  Y {r[3]:.0f}..{r[5]:.0f}  L={r[6]:.0f}  H={r[7]:.0f}  layer={r[8]}")

print("\n--- TESTI (TEXT/MTEXT) ---")
for e in msp:
    t = e.dxftype()
    if t == "TEXT":
        print(f"  TEXT [{e.dxf.layer}] @({e.dxf.insert[0]:.0f},{e.dxf.insert[1]:.0f}): {e.dxf.text!r}")
    elif t == "MTEXT":
        txt = e.plain_text().replace("\n", " | ")
        print(f"  MTEXT [{e.dxf.layer}] @({e.dxf.insert[0]:.0f},{e.dxf.insert[1]:.0f}): {txt!r}")

print("\n--- MLEADER ---")
for e in msp:
    if e.dxftype() in ("MLEADER", "MULTILEADER"):
        try:
            ctx = e.context
            txt = ctx.mtext.insert if hasattr(ctx, "mtext") else "?"
            content = e.get_mtext_content() if hasattr(e, "get_mtext_content") else ""
            print(f"  MLEADER [{e.dxf.layer}]: {content!r}")
        except Exception as exc:  # noqa: BLE001
            print(f"  MLEADER [{e.dxf.layer}]: (contenuto non leggibile: {exc})")

print("\n--- DIMENSIONI (DIMENSION) ---")
for e in msp:
    if e.dxftype() == "DIMENSION":
        try:
            meas = e.get_measurement()
            if isinstance(meas, (int, float)):
                print(f"  DIM [{e.dxf.layer}] misura={meas:.1f}  testo={e.dxf.text!r}")
            else:
                print(f"  DIM [{e.dxf.layer}] misura={meas}  testo={e.dxf.text!r}")
        except Exception:  # noqa: BLE001
            pass

print("\n--- ESTENSIONI GLOBALI MODELSPACE ---")
box = ezbbox.extents(msp, fast=True)
if box.has_data:
    print(f"  extmin={tuple(round(v) for v in box.extmin)}  extmax={tuple(round(v) for v in box.extmax)}")
    print(f"  L={box.extmax[0]-box.extmin[0]:.0f}  H={box.extmax[1]-box.extmin[1]:.0f}")
