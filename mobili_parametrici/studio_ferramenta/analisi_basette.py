# -*- coding: utf-8 -*-
"""Caccia alle BASETTE: per ogni anta con tazze, calcola le quote globali delle
cerniere e cerca su TUTTI gli altri pezzi i fori Ø5 vicini a quelle quote
(l'asse della basetta e' parallelo all'asse tazza). Riporta la firma:
quota dal fronte del fianco, interasse viti, direzione."""
import json
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
est = json.load(open(os.path.join(BASE, "estratto_ferramenta.json"), encoding="utf-8"))

for fk in ("25-A019_Armadio camera V.stp", "25-A019_Mobile_R.stp", "25-A019_AC.stp",
           "25-A019_Mobile_W.stp"):
    pezzi = est[fk]["pezzi"]
    # ante = pezzi con tazze Ø35 prof<=14 senza svaso Ø51
    for lab, p in pezzi.items():
        cups = [h for h in p["fori"] if h["dia"] == 35.0 and h["len"] <= 14]
        if not cups:
            continue
        svasi = [h for h in p["fori"] if h["dia"] == 51.0]
        def con_svaso(c):
            return any(abs(s["cx"] - c["cx"]) < 3 and abs(s["cy"] - c["cy"]) < 3
                       and abs(s["cz"] - c["cz"]) < 3 for s in svasi)
        cups = [c for c in cups if not con_svaso(c)]
        if not cups:
            continue
        print(f"\n=== {fk[8:26]} :: ANTA {lab[-16:]} — {len(cups)} tazze, asse {cups[0]['dir']} ===")
        for c in cups[:6]:
            # cerco fori Ø5 su ALTRI pezzi alla stessa quota della tazza
            # (stessa coordinata lungo l'asse anta-verticale, entro ±40)
            trovati = []
            for lab2, p2 in pezzi.items():
                if lab2 == lab:
                    continue
                for h in p2["fori"]:
                    if h["dia"] != 5.0 or h["dir"] == "OBL":
                        continue
                    # distanza dalla tazza nelle 3 coordinate
                    dxx = abs(h["cx"] - c["cx"])
                    dyy = abs(h["cy"] - c["cy"])
                    dzz = abs(h["cz"] - c["cz"])
                    # vicino in 2 assi su 3 (la terza e' l'arretramento basetta)
                    vicini2 = sum(1 for d in (dxx, dyy, dzz) if d < 40)
                    if vicini2 == 3 and max(dxx, dyy, dzz) < 40:
                        trovati.append((lab2, h, dxx, dyy, dzz))
            if trovati:
                print(f"  tazza @({c['cx']:7.1f},{c['cy']:7.1f},{c['cz']:7.1f}):")
                for lab2, h, dxx, dyy, dzz in trovati[:8]:
                    print(f"     {lab2[-18:]:18s} D5 dir={h['dir']} len={h['len']:4.1f} "
                          f"@({h['cx']:7.1f},{h['cy']:7.1f},{h['cz']:7.1f}) Δ=({dxx:.1f},{dyy:.1f},{dzz:.1f})")
            else:
                print(f"  tazza @({c['cx']:7.1f},{c['cy']:7.1f},{c['cz']:7.1f}): NESSUN Ø5 entro 40 su altri pezzi")
