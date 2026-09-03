# -*- coding: utf-8 -*-
"""Matcher di giunzioni: accoppia i fori di pezzi DIVERSI dello stesso mobile
quando sono coassiali e vicini (stessa retta d'asse, estremi adiacenti).
Ogni coppia = un giunto: (dia_A, tipo_A) <-> (dia_B, tipo_B).
Riepilogo per tipo di giunto + esempi. Scrive giunzioni.json."""
import json
import os
from collections import defaultdict, Counter

BASE = os.path.dirname(os.path.abspath(__file__))
est = json.load(open(os.path.join(BASE, "estratto_ferramenta.json"), encoding="utf-8"))
pat = json.load(open(os.path.join(BASE, "pattern_pezzi.json"), encoding="utf-8"))

TOL_ASSE = 1.0    # scostamento max della retta d'asse
TOL_GAP = 25.0    # distanza max tra gli estremi dei due segmenti lungo l'asse

def chiave_asse(h):
    """Retta d'asse: (dir, coord perpendicolari arrotondate)."""
    if h["dir"] == "X":
        return ("X", round(h["cy"], 0), round(h["cz"], 0))
    if h["dir"] == "Y":
        return ("Y", round(h["cx"], 0), round(h["cz"], 0))
    if h["dir"] == "Z":
        return ("Z", round(h["cx"], 0), round(h["cy"], 0))
    return None

def perp(h):
    if h["dir"] == "X":
        return (h["cy"], h["cz"])
    if h["dir"] == "Y":
        return (h["cx"], h["cz"])
    return (h["cx"], h["cy"])

out = {}
riepilogo = Counter()
esempi = defaultdict(list)

for fk, v in est.items():
    if "error" in v or "corretti" in fk:
        continue
    pezzi = v["pezzi"]
    # indice: per direzione, lista (pezzo, foro)
    per_dir = defaultdict(list)
    for lab, p in pezzi.items():
        loc = pat[fk][lab]
        for i, (h, fl) in enumerate(zip(p["fori"], loc["fori"])):
            if h["dir"] == "OBL":
                continue
            per_dir[h["dir"]].append((lab, h, fl))
    accoppiati = []
    for d, lst in per_dir.items():
        for i in range(len(lst)):
            la, ha, fa = lst[i]
            pa = perp(ha)
            for j in range(i + 1, len(lst)):
                lb, hb, fb = lst[j]
                if la == lb:
                    continue
                pb = perp(hb)
                if abs(pa[0] - pb[0]) > TOL_ASSE or abs(pa[1] - pb[1]) > TOL_ASSE:
                    continue
                # gap lungo l'asse: i due segmenti devono essere adiacenti (non sovrapposti di molto)
                gap = max(ha["lo"], hb["lo"]) - min(ha["hi"], hb["hi"])
                if gap > TOL_GAP:
                    continue
                sovrap = min(ha["hi"], hb["hi"]) - max(ha["lo"], hb["lo"])
                if sovrap > 5:   # coassiali ma compenetranti: sospetto, tienili comunque
                    pass
                ta = fa.get("faccia") or fa.get("costa", "?")
                tb = fb.get("faccia") or fb.get("costa", "?")
                key = tuple(sorted([
                    f"D{ha['dia']:g}_{fa['tipo']}_prof{round(fa.get('prof', ha['len']))}",
                    f"D{hb['dia']:g}_{fb['tipo']}_prof{round(fb.get('prof', hb['len']))}",
                ]))
                riepilogo[key] += 1
                if len(esempi[key]) < 4:
                    esempi[key].append(f"{fk[:24]} {la[-12:]}<->{lb[-12:]} gap={gap:.1f}")
                accoppiati.append({
                    "a": {"pezzo": la, "dia": ha["dia"], "tipo": fa["tipo"], "lato": ta,
                          "prof": fa.get("prof", ha["len"])},
                    "b": {"pezzo": lb, "dia": hb["dia"], "tipo": fb["tipo"], "lato": tb,
                          "prof": fb.get("prof", hb["len"])},
                    "dir": d, "gap": round(gap, 2),
                    "pos": [round(x, 1) for x in ((ha["cx"], ha["cy"], ha["cz"]))],
                })
    out[fk] = accoppiati
    print(f"{fk}: {len(accoppiati)} giunzioni")

json.dump(out, open(os.path.join(BASE, "giunzioni.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

print("\n=== TIPI DI GIUNTO (coppie di firme) ===")
for k, n in riepilogo.most_common(40):
    print(f"{n:5d}  {k[0]}  <->  {k[1]}")
    for e in esempi[k][:2]:
        print(f"       es: {e}")
