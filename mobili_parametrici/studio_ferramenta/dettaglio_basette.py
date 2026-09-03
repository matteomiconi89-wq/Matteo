# -*- coding: utf-8 -*-
"""Dettaglio basette: bbox del fianco V041 e della sua anta V124, tutti i fori
Ø5 X-dir del fianco raggruppati per quota z (alle quote tazza)."""
import json
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
est = json.load(open(os.path.join(BASE, "estratto_ferramenta.json"), encoding="utf-8"))

pezzi = est["25-A019_Armadio camera V.stp"]["pezzi"]

for lab in ("25-A019_Armadio camera V041", "25-A019_Armadio camera V027"):
    p = pezzi[lab]
    bb = p["bbox"]
    print(f"=== {lab[-6:]} bbox X[{bb[0]:.1f},{bb[3]:.1f}] Y[{bb[1]:.1f},{bb[4]:.1f}] Z[{bb[2]:.1f},{bb[5]:.1f}] ===")
    per_z = defaultdict(list)
    for h in p["fori"]:
        if h["dia"] == 5.0 and h["dir"] == "X":
            per_z[round(h["cz"], 1)].append(h)
    for z in sorted(per_z):
        hh = per_z[z]
        ys = ", ".join(f"y={h['cy']:.1f}(len{h['len']:.0f})" for h in sorted(hh, key=lambda h: h["cy"]))
        print(f"  z={z:7.1f}: {ys}")

# anta di riferimento
for lab in ("25-A019_Armadio camera V124",):
    p = pezzi[lab]
    bb = p["bbox"]
    print(f"\n=== ANTA {lab[-6:]} bbox X[{bb[0]:.1f},{bb[3]:.1f}] Y[{bb[1]:.1f},{bb[4]:.1f}] Z[{bb[2]:.1f},{bb[5]:.1f}] ===")
    for h in p["fori"]:
        if h["dia"] == 35.0:
            print(f"  tazza @({h['cx']:.1f},{h['cy']:.1f},{h['cz']:.1f}) len={h['len']}")
