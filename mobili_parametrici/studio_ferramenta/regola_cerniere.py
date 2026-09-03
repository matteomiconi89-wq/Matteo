# -*- coding: utf-8 -*-
"""Tutti i pezzi con tazze Ø35 (cerniere) e con Ø14 (RAFIX): quote locali dai bordi.
Per le ante: numero tazze vs altezza anta, distanza tazza dal bordo (asse e bordo),
fori satellite vicini (viti tazza / inserti)."""
import json
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
pat = json.load(open(os.path.join(BASE, "pattern_pezzi.json"), encoding="utf-8"))
agg = json.load(open(os.path.join(BASE, "aggancio.json"), encoding="utf-8"))

print("################ CERNIERE (tazze Ø35) ################")
for fk, pezzi in pat.items():
    for lab, p in pezzi.items():
        cups = [f for f in p["fori"] if f["dia"] == 35.0 and f["tipo"] == "FACCIA"]
        if not cups:
            continue
        o = p["orient"]
        cod = agg.get(fk, {}).get("agganciati", {}).get(lab, {}).get("codice", "-")
        print(f"\n=== {fk} :: {lab} (cod {cod}) sp={o['sp']} A={o['lA']} B={o['lB']} ===")
        altri = [f for f in p["fori"] if f["dia"] != 35.0]
        for c in sorted(cups, key=lambda f: f["a"]):
            # fori satellite entro 30 mm dalla tazza
            sat = [f for f in altri if f["tipo"] == "FACCIA"
                   and abs(f["a"] - c["a"]) < 35 and abs(f["b"] - c["b"]) < 35]
            sat_s = "; ".join(f"D{f['dia']}@({f['a']-c['a']:+.1f},{f['b']-c['b']:+.1f})prof{f['prof']:.0f}"
                              for f in sat)
            print(f"  tazza a={c['a']:8.2f} b={c['b']:7.2f} prof={c['prof']:5.2f} "
                  f"faccia={c['faccia']} | dist bordi A: {c['a']:.1f}/{o['lA']-c['a']:.1f} "
                  f"B: {c['b']:.1f}/{o['lB']-c['b']:.1f} | sat: {sat_s}")

print("\n\n################ RAFIX (Ø14 prof 15) ################")
for fk, pezzi in pat.items():
    for lab, p in pezzi.items():
        raf = [f for f in p["fori"] if f["dia"] == 14.0 and f["tipo"] == "FACCIA"]
        if not raf:
            continue
        o = p["orient"]
        cod = agg.get(fk, {}).get("agganciati", {}).get(lab, {}).get("codice", "-")
        print(f"\n=== {fk} :: {lab} (cod {cod}) sp={o['sp']} A={o['lA']} B={o['lB']} ===")
        for c in sorted(raf, key=lambda f: (f["b"], f["a"])):
            print(f"  rafix a={c['a']:8.2f} b={c['b']:7.2f} prof={c['prof']:5.2f} faccia={c['faccia']} "
                  f"| dist bordi A: {c['a']:.1f}/{o['lA']-c['a']:.1f} B: {c['b']:.1f}/{o['lB']-c['b']:.1f}")
