# -*- coding: utf-8 -*-
"""Analisi Mobile_Q: posizioni LEGRABOX (verifica placement globale),
fori dei pezzi in legno del cassetto, fori dei fianchi nella zona guide."""
import json
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
est = json.load(open(os.path.join(BASE, "estratto_ferramenta.json"), encoding="utf-8"))
agg = json.load(open(os.path.join(BASE, "aggancio.json"), encoding="utf-8"))

FK = "25-A019_Mobile_Q.stp"
v = est[FK]["pezzi"]
a = agg[FK]["agganciati"]

def fmt_bb(bb):
    return f"X[{bb[0]:.0f},{bb[3]:.0f}] Y[{bb[1]:.0f},{bb[4]:.0f}] Z[{bb[2]:.0f},{bb[5]:.0f}]"

print("=== BBOX ferramenta LEGRABOX (coordinate globali) ===")
for lab, p in sorted(v.items()):
    if "cassetto" in lab.lower() or "LEGRABOX" in lab:
        print(f"{lab:42s} {fmt_bb(p['bbox'])}  dims={p['dims_ord']}")

print()
print("=== Assieme: bbox complessivo del mobile ===")
xs = [p["bbox"] for p in v.values()]
print("X", min(b[0] for b in xs), max(b[3] for b in xs),
      "| Y", min(b[1] for b in xs), max(b[4] for b in xs),
      "| Z", min(b[2] for b in xs), max(b[5] for b in xs))

print()
print("=== Fori dei pezzi in legno LEGRABOX ===")
for lab, p in sorted(v.items()):
    if "cassetto" not in lab.lower():
        continue
    print(f"--- {lab} bbox={fmt_bb(p['bbox'])} ---")
    for h in p["fori"]:
        print(f"    dir={h['dir']} dia={h['dia']:6.2f} c=({h['cx']:8.2f},{h['cy']:8.2f},{h['cz']:8.2f}) "
              f"lo={h['lo']:8.2f} hi={h['hi']:8.2f} len={h['len']:6.2f}")

print()
print("=== Pannelli del mobile: censimento fori per pezzo ===")
for lab, p in sorted(v.items()):
    if "cassetto" in lab.lower():
        continue
    cod = a.get(lab, {})
    dd = defaultdict(int)
    for h in p["fori"]:
        dd[(h["dia"], h["dir"])] += 1
    riass = ", ".join(f"D{d}{dr}x{n}" for (d, dr), n in sorted(dd.items()))
    print(f"{lab:28s} cod={cod.get('codice','-'):4} {str(p['dims_ord']):26s} {riass}")
