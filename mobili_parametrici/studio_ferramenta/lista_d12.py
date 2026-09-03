# -*- coding: utf-8 -*-
"""Tutti i fori Ø12 in costa prof 55-70: chi li ha e dove."""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
pat = json.load(open(os.path.join(BASE, "pattern_pezzi.json"), encoding="utf-8"))

for fk, pezzi in pat.items():
    if "corretti" in fk:
        continue
    for lab, p in pezzi.items():
        o = p["orient"]
        ff = [f for f in p["fori"] if f["dia"] == 12.0 and f["tipo"] == "COSTA"
              and 55 <= f.get("prof", 0) <= 70]
        if ff:
            print(f"{fk[8:26]} :: {lab[-20:]} sp={o['sp']} A={o['lA']} B={o['lB']}")
            for f in ff:
                lato = o["lB"] if f["costa"].startswith("A") else o["lA"]
                print(f"   costa={f['costa']} prof={f['prof']} pos={f['pos']} (lato {lato}) t={f['t']}")
