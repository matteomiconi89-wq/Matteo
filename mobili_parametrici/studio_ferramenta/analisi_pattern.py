# -*- coding: utf-8 -*-
"""Porta ogni foro in coordinate locali del pannello e riconosce i pattern.

Per ogni pezzo:
  - asse spessore T = asse della dimensione minima del bbox
  - assi nel piano: A (dimensione maggiore), B (intermedia)
  - ogni foro: tipo FACCIA (asse//T) o COSTA (asse nel piano) o OBL
    FACCIA: entra da T- o T+ (gap piu' piccolo tra cilindro e superficie)
    COSTA: entra dalla costa piu' vicina all'estremo del segmento
  - coordinate locali: a (lungo A, da 0), b (lungo B, da 0), prof
Output: pattern_pezzi.json { file: { pezzo: {orient, fori_loc: [...] } } }
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
est = json.load(open(os.path.join(BASE, "estratto_ferramenta.json"), encoding="utf-8"))

AXES = "XYZ"

def analizza_pezzo(p):
    bb = p["bbox"]
    L = [bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2]]
    mn = [bb[0], bb[1], bb[2]]
    iT = min(range(3), key=lambda i: L[i])          # spessore
    iA = max(range(3), key=lambda i: L[i])          # lato lungo
    iB = ({0, 1, 2} - {iT, iA}).pop()               # lato medio
    if iA == iT:                                     # pezzo cubico degenerato
        iA, iB = [i for i in range(3) if i != iT]
    orient = {"T": AXES[iT], "A": AXES[iA], "B": AXES[iB],
              "sp": round(L[iT], 2), "lA": round(L[iA], 2), "lB": round(L[iB], 2)}
    out = []
    for h in p["fori"]:
        d = h["dir"]
        c = [h["cx"], h["cy"], h["cz"]]
        f = {"dia": h["dia"], "len": h["len"]}
        if d == "OBL":
            f["tipo"] = "OBL"
            f["a"] = round(c[iA] - mn[iA], 2)
            f["b"] = round(c[iB] - mn[iB], 2)
            f["t"] = round(c[iT] - mn[iT], 2)
            f["asse"] = h.get("asse")
            out.append(f)
            continue
        iD = AXES.index(d)
        lo_gap = h["lo"] - mn[iD]
        hi_gap = (mn[iD] + L[iD]) - h["hi"]
        if iD == iT:
            f["tipo"] = "FACCIA"
            f["a"] = round(c[iA] - mn[iA], 2)
            f["b"] = round(c[iB] - mn[iB], 2)
            # entra dal lato col gap minore; prof = estensione cilindro dal lato di entrata
            if abs(lo_gap) <= abs(hi_gap):
                f["faccia"] = "T-"
                f["prof"] = round(h["hi"] - mn[iD], 2)
            else:
                f["faccia"] = "T+"
                f["prof"] = round(mn[iD] + L[iD] - h["lo"], 2)
            f["passante"] = bool(abs(lo_gap) < 3.0 and abs(hi_gap) < 3.0)
        else:
            f["tipo"] = "COSTA"
            # quale costa: lungo l'asse del foro, dall'estremo col gap minore
            asse_nome = "A" if iD == iA else "B"
            if abs(lo_gap) <= abs(hi_gap):
                f["costa"] = asse_nome + "0"
                f["prof"] = round(h["hi"] - mn[iD], 2)
            else:
                f["costa"] = asse_nome + "1"
                f["prof"] = round(mn[iD] + L[iD] - h["lo"], 2)
            # coordinate nel piano della costa: posizione lungo l'altro asse piano + quota nello spessore
            iAltro = iB if iD == iA else iA
            f["pos"] = round(c[iAltro] - mn[iAltro], 2)      # lungo l'altro lato
            f["t"] = round(c[iT] - mn[iT], 2)                # quota nello spessore
        out.append(f)
    return orient, out

res = {}
for fk, v in est.items():
    if "error" in v:
        continue
    res[fk] = {}
    for lab, p in v["pezzi"].items():
        orient, fori = analizza_pezzo(p)
        res[fk][lab] = {"orient": orient, "bbox": p["bbox"], "n_solidi": p["n_solidi"],
                        "vol_cm3": p["vol_cm3"], "fori": fori}

json.dump(res, open(os.path.join(BASE, "pattern_pezzi.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

# censimento firme: (dia, tipo, prof arrotondata) globale
from collections import Counter
firme = Counter()
for fk, pezzi in res.items():
    for lab, p in pezzi.items():
        for f in p["fori"]:
            firme[(f["dia"], f["tipo"], f.get("faccia") or f.get("costa", "?"),
                   round(f.get("prof", f["len"])))] += 1
print("=== FIRME (dia, tipo, lato, prof) piu' comuni ===")
for k, n in firme.most_common(45):
    print(f"D{k[0]:6.2f} {k[1]:6s} {k[2]:3s} prof~{k[3]:4d} : {n}")
print("SCRITTO pattern_pezzi.json")
