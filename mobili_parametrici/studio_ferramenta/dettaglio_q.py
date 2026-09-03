# -*- coding: utf-8 -*-
"""Dettaglio gerarchia Mobile_Q + facce dei pannelli (i fori ci sono?)."""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(BASE, "ricognizione.json"), encoding="utf-8"))

v = d["25-A019_Mobile_Q.stp"]
print("=== GERARCHIA Mobile_Q (oggetti con solidi o con figli) ===")
for o in v["oggetti"]:
    if not o.get("n_solidi") and not o.get("figli"):
        continue
    pad = ",".join(o.get("padri", [])) or "-"
    fig = len(o.get("figli", []))
    print(f"{o['label'][:55]:55s} tipo={o['tipo'].split('::')[-1]:12s} sol={o.get('n_solidi',0):3d} "
          f"facce={o.get('n_facce',0):4d} figli={fig} padri={pad[:50]}")

print()
print("=== FACCE per pannello (Armadio V, primi 30): fori presenti se facce > 6 ===")
va = d["25-A019_Armadio camera V.stp"]
solo = [o for o in va["oggetti"] if o.get("n_solidi") == 1]
for o in solo[:30]:
    print(f"{o['label']:40s} facce={o['n_facce']:4d} dims={o['dims']}")
print()
n_forati = sum(1 for o in solo if o["n_facce"] > 6)
print(f"Armadio V: {len(solo)} pannelli singoli, {n_forati} con piu' di 6 facce (=lavorati/forati)")
