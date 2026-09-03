# -*- coding: utf-8 -*-
"""Ultimi dettagli: scheda foratura scorrevole S, fori Ø12/Ø18 costa delle ante V,
cappello/basamento W (tiranti Ø16, masselli), pianetti Q con guide interne."""
import json
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
est = json.load(open(os.path.join(BASE, "estratto_ferramenta.json"), encoding="utf-8"))
pat = json.load(open(os.path.join(BASE, "pattern_pezzi.json"), encoding="utf-8"))

def scheda(fk, lab):
    p = pat[fk][lab]
    o = p["orient"]
    print(f"--- {fk} :: {lab} sp={o['sp']} A={o['lA']} B={o['lB']} ---")
    for f in sorted(p["fori"], key=lambda f: (f["dia"], f.get("prof", 0))):
        lato = f.get("faccia") or f.get("costa") or "OBL"
        if f["tipo"] == "FACCIA":
            print(f"   D{f['dia']:5.1f} {f['tipo']:6s} {lato:3s} prof={f.get('prof',0):5.1f} a={f['a']:8.1f} b={f['b']:7.1f}")
        elif f["tipo"] == "COSTA":
            print(f"   D{f['dia']:5.1f} {f['tipo']:6s} {lato:3s} prof={f.get('prof',0):5.1f} pos={f['pos']:8.1f} t={f['t']:5.1f}")
        else:
            print(f"   D{f['dia']:5.1f} OBL asse={f.get('asse')} a={f['a']} b={f['b']}")

print("################ SCORREVOLE S (anta completa) ################")
for lab in sorted(pat["25-A019_Scorrevole S.stp"]):
    scheda("25-A019_Scorrevole S.stp", lab)

print()
print("################ ANTE V: fori Ø12 e Ø18 in costa ################")
for lab, p in sorted(pat["25-A019_Armadio camera V.stp"].items()):
    ff = [f for f in p["fori"] if f["dia"] in (12.0, 18.0) and f["tipo"] == "COSTA"]
    if ff:
        o = p["orient"]
        print(f"--- {lab} sp={o['sp']} A={o['lA']} B={o['lB']}")
        for f in ff:
            print(f"   D{f['dia']:5.1f} costa={f['costa']} prof={f['prof']:.0f} pos={f['pos']:.1f} t={f['t']:.1f}")

print()
print("################ W: cappello (tiranti Ø16) e masselli ################")
for lab, p in sorted(pat["25-A019_Mobile_W.stp"].items()):
    if not (lab.startswith("25-A019_W_Cappello") or lab.startswith("25-A019_W_Masselli")
            or lab.startswith("25-A019_W_Basamento")):
        continue
    ff = [f for f in p["fori"]]
    if not ff:
        continue
    o = p["orient"]
    print(f"--- {lab} sp={o['sp']} A={o['lA']} B={o['lB']}")
    riass = defaultdict(int)
    for f in ff:
        lato = f.get("faccia") or f.get("costa") or "OBL"
        riass[(f["dia"], f["tipo"], lato, round(f.get("prof", f["len"])))] += 1
    for k, n in sorted(riass.items()):
        print(f"   D{k[0]:5.1f} {k[1]:6s} {k[2]:3s} prof~{k[3]:4d} x{n}")

print()
print("################ Q: pianetti Q005/Q006 (guide cassetti interni?) ################")
for lab in ("25-A019_Mobile Q005", "25-A019_Mobile Q006", "25-A019_Mobile Q011", "25-A019_Mobile Q012"):
    scheda("25-A019_Mobile_Q.stp", lab)
