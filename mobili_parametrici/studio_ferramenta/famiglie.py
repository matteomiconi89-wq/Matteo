# -*- coding: utf-8 -*-
"""Studio per famiglie:
1) RIGHE di fori (>=3 equidistanti, stessa dia/lato): passo e distanza dai bordi
2) Spine Ø8 lungo i giunti: passo e distanza dalle estremita'
3) Dove vivono le famiglie minori (Ø10x18, Ø16, Ø12, Ø8.5, Ø12.5, Ø20, Ø25, Ø18)
"""
import json
import os
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
pat = json.load(open(os.path.join(BASE, "pattern_pezzi.json"), encoding="utf-8"))

def righe_di(fori, key_fisso, key_var, tol=0.8):
    """Raggruppa per (dia, lato, coord fissa) e cerca sequenze equidistanti sulla variabile."""
    gruppi = defaultdict(list)
    for f in fori:
        if f["tipo"] == "OBL":
            continue
        lato = f.get("faccia") or f.get("costa")
        kf = f.get(key_fisso)
        kv = f.get(key_var)
        if kf is None or kv is None:
            continue
        gruppi[(f["dia"], f["tipo"], lato, round(kf, 1))].append(kv)
    out = []
    for (dia, tipo, lato, kf), vals in gruppi.items():
        if len(vals) < 3:
            continue
        vals = sorted(vals)
        passi = [round(b - a, 1) for a, b in zip(vals, vals[1:])]
        out.append({"dia": dia, "tipo": tipo, "lato": lato, "fisso": kf,
                    "n": len(vals), "da": vals[0], "a": vals[-1], "passi": passi})
    return out

print("=== 1) RIGHE Ø5 in FACCIA (sistema 32): passo e quota della riga ===")
passi_totali = Counter()
quote_riga = Counter()          # coord fissa b = distanza della fila dal bordo B
n_righe = 0
for fk, pezzi in pat.items():
    if "corretti" in fk:
        continue
    for lab, p in pezzi.items():
        o = p["orient"]
        for r in righe_di([f for f in p["fori"] if f["dia"] == 5.0 and f["tipo"] == "FACCIA"],
                          "b", "a"):
            n_righe += 1
            for x in r["passi"]:
                passi_totali[x] += 1
            # quota dal bordo B piu' vicino
            q = min(r["fisso"], round(o["lB"] - r["fisso"], 1))
            quote_riga[q] += 1
print(f"righe trovate: {n_righe}")
print("passi:", dict(passi_totali.most_common(12)))
print("quota riga dal bordo B (min dei due):", dict(quote_riga.most_common(15)))

print()
print("=== 2) SPINE Ø8 in COSTA: passo lungo il giunto e distanza dalle estremita' ===")
passi8 = Counter()
dist_estremi = Counter()
for fk, pezzi in pat.items():
    if "corretti" in fk:
        continue
    for lab, p in pezzi.items():
        o = p["orient"]
        fori_c = [f for f in p["fori"] if f["dia"] == 8.0 and f["tipo"] == "COSTA"]
        # gruppo per costa
        per_costa = defaultdict(list)
        for f in fori_c:
            per_costa[f["costa"]].append(f)
        for costa, ff in per_costa.items():
            lato_len = o["lB"] if costa.startswith("A") else o["lA"]
            pos = sorted(f["pos"] for f in ff)
            if len(pos) >= 2:
                for a, b in zip(pos, pos[1:]):
                    passi8[round(b - a)] += 1
            if pos:
                dist_estremi[round(min(pos))] += 1
                dist_estremi[round(lato_len - max(pos))] += 1
print("passi spine:", dict(passi8.most_common(15)))
print("distanza prima/ultima spina dall'estremita':", dict(dist_estremi.most_common(15)))

print()
print("=== 3) FAMIGLIE MINORI: dove vivono ===")
for dia_c, prof_c in [(10.0, 18), (10.0, 4), (16.0, None), (12.0, None), (8.5, None),
                      (12.5, None), (20.0, None), (25.0, None), (18.0, None), (15.0, None),
                      (26.0, None), (22.0, None), (3.0, None), (6.0, None)]:
    posti = Counter()
    es = []
    for fk, pezzi in pat.items():
        if "corretti" in fk:
            continue
        for lab, p in pezzi.items():
            for f in p["fori"]:
                if f["dia"] != dia_c:
                    continue
                pr = f.get("prof", f["len"])
                if prof_c is not None and round(pr) != prof_c:
                    continue
                lato = f.get("faccia") or f.get("costa") or "OBL"
                posti[(fk.split("_")[-1][:14], f["tipo"], lato, round(pr))] += 1
                if len(es) < 3:
                    es.append(f"{lab[-16:]} {f['tipo']}{lato} prof{pr:.0f} a={f.get('a', f.get('pos','?'))} b={f.get('b', f.get('t','?'))}")
    if posti:
        tag = f"Ø{dia_c:g}" + (f" prof{prof_c}" if prof_c else "")
        print(f"--- {tag} ---")
        for k, n in posti.most_common(6):
            print(f"   {k}: x{n}")
        for e in es:
            print(f"   es {e}")
