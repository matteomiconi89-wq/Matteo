# -*- coding: utf-8 -*-
"""Controprova del generatore: il MOBILE_DEMO riletto dallo STEP deve passare
gli STESSI controlli famiglia-per-famiglia usati sui mobili veri."""
import json
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
est = json.load(open(os.path.join(BASE, "estratto_demo.json"), encoding="utf-8"))

AXES = "XYZ"

def analizza_pezzo(p):
    bb = p["bbox"]
    Ld = [bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2]]
    mn = [bb[0], bb[1], bb[2]]
    iT = min(range(3), key=lambda i: Ld[i])
    iA = max(range(3), key=lambda i: Ld[i])
    iB = ({0, 1, 2} - {iT, iA}).pop()
    orient = {"sp": round(Ld[iT], 2), "lA": round(Ld[iA], 2), "lB": round(Ld[iB], 2)}
    out = []
    for h in p["fori"]:
        d = h["dir"]
        c = [h["cx"], h["cy"], h["cz"]]
        f = {"dia": h["dia"], "len": h["len"]}
        if d == "OBL":
            continue
        iD = AXES.index(d)
        lo_gap = h["lo"] - mn[iD]
        hi_gap = (mn[iD] + Ld[iD]) - h["hi"]
        if iD == iT:
            f["tipo"] = "FACCIA"
            f["a"] = round(c[iA] - mn[iA], 2)
            f["b"] = round(c[iB] - mn[iB], 2)
            f["faccia"] = "T-" if abs(lo_gap) <= abs(hi_gap) else "T+"
            f["prof"] = round(h["hi"] - mn[iD], 2) if f["faccia"] == "T-" else round(mn[iD] + Ld[iD] - h["lo"], 2)
        else:
            f["tipo"] = "COSTA"
            an = "A" if iD == iA else "B"
            if abs(lo_gap) <= abs(hi_gap):
                f["costa"] = an + "0"
                f["prof"] = round(h["hi"] - mn[iD], 2)
            else:
                f["costa"] = an + "1"
                f["prof"] = round(mn[iD] + Ld[iD] - h["lo"], 2)
            iAltro = iB if iD == iA else iA
            f["pos"] = round(c[iAltro] - mn[iAltro], 2)
            f["t"] = round(c[iT] - mn[iT], 2)
        out.append(f)
    return orient, out

TOL = 1.5
R = defaultdict(lambda: {"ok": 0, "no": 0, "esempi": []})

def vicino(x, atteso, tol=TOL):
    return abs(x - atteso) <= tol

def check(fam, cond, dett):
    if cond:
        R[fam]["ok"] += 1
    else:
        R[fam]["no"] += 1
        if len(R[fam]["esempi"]) < 4:
            R[fam]["esempi"].append(dett)

pezzi = {k: v for k, v in est["MOBILE_DEMO.stp"]["pezzi"].items()
         if not k.startswith("FERRAMENTA_")}
for lab, p in pezzi.items():
    o, fori = analizza_pezzo(p)
    # cerniere
    cerniere = [f for f in fori if f["dia"] == 35.0 and f["tipo"] == "FACCIA"]
    if cerniere:
        v5 = [f for f in fori if f["dia"] == 5.0 and f["tipo"] == "FACCIA"]
        for c in cerniere:
            da = min(c["a"], o["lA"] - c["a"])
            db = min(c["b"], o["lB"] - c["b"])
            check("cerniera 22.5 dal bordo", vicino(da, 22.5) or vicino(db, 22.5), f"{lab} {da:.1f}/{db:.1f}")
            segno = 1 if c["b"] < o["lB"] / 2 else -1
            trovate = sum(1 for dv in (-22.5, 22.5) for f in v5
                          if vicino(f["a"], c["a"] + dv) and vicino(f["b"], c["b"] + segno * 9.5))
            check("cerniera 2 viti", trovate == 2, f"{lab} a={c['a']} trovate={trovate}")
        aa = sorted(c["a"] for c in cerniere)
        n = len(aa)
        attese = [100.0 + i * (o["lA"] - 200.0) / (n - 1) for i in range(n)]
        for a_r, a_t in zip(aa, attese):
            check("cerniera 100+equidistanti", vicino(a_r, a_t), f"{lab} {a_r} vs {a_t:.1f}")
        h = o["lA"]
        att_n = 2 if h < 900 else 3 if h < 1600 else 4 if h < 2000 else 5
        check("cerniera conteggio", n == att_n, f"{lab} h={h} n={n} att={att_n}")
    # barilotto ("rafix" di bottega): sede Ø14x15 a 21 dal bordo
    for f in fori:
        if f["dia"] == 14.0 and f["tipo"] == "FACCIA" and vicino(f.get("prof", 0), 15, 1):
            d = min(f["a"], o["lA"] - f["a"], f["b"], o["lB"] - f["b"])
            check("barilotto: sede 14x15 a 21 dal bordo", vicino(d, 21), f"{lab} d={d:.1f}")
    # bussola: foro 13x14.4 (punta con svasatore, codice macchina 13)
    for f in fori:
        if f["dia"] == 13.0 and f["tipo"] == "FACCIA":
            check("bussola: foro 13x14.4", vicino(f.get("prof", 0), 14.4, 0.5), f"{lab} prof={f.get('prof')}")
    # bone
    v513 = [f for f in fori if f["dia"] == 5.0 and f["tipo"] == "FACCIA" and vicino(f.get("prof", 0), 13, 1)]
    usati = set()
    for i, f in enumerate(v513):
        if i in usati:
            continue
        quad = [j for j, g in enumerate(v513) if j != i and (
                (vicino(abs(g["a"] - f["a"]), 32, 1) and vicino(g["b"], f["b"], 1))
                or (vicino(abs(g["b"] - f["b"]), 32, 1) and vicino(g["a"], f["a"], 1))
                or (vicino(abs(g["a"] - f["a"]), 32, 1) and vicino(abs(g["b"] - f["b"]), 32, 1)))]
        if len(quad) == 3:
            check("bone quadrato 32", True, "")
            usati.add(i)
            usati.update(quad)
    # rekord
    for f in fori:
        if f["dia"] == 12.0 and f["tipo"] == "COSTA" and 55 <= f.get("prof", 0) <= 70:
            lato = o["lB"] if f["costa"].startswith("A") else o["lA"]
            d = min(f["pos"], lato - f["pos"])
            check("rekord quota 80", vicino(d, 80, 2.5), f"{lab} d={d:.1f}")
    # spine: costa 29 / faccia 13 — i passaggi perno (Ø8 costa ~26 sui pezzi con barilotti) sono un'altra famiglia
    ha_barilotti = any(f["dia"] == 14.0 and f["tipo"] == "FACCIA" for f in fori)
    for f in fori:
        if f["dia"] == 8.0 and f["tipo"] == "COSTA":
            if ha_barilotti and vicino(f["prof"], 26, 1.5):
                check("perno barilotto: passaggio costa Ø8x26", True, "")
            else:
                check("spina costa prof 29", vicino(f["prof"], 29, 1), f"{lab} prof={f['prof']}")
        if f["dia"] == 8.0 and f["tipo"] == "FACCIA":
            check("spina faccia prof 13 (incl. bussole)", vicino(f["prof"], 13, 1), f"{lab} prof={f['prof']}")
    # sistema32: file a passo 32 e quota 37
    file5 = defaultdict(list)
    for f in fori:
        if f["dia"] == 5.0 and f["tipo"] == "FACCIA":
            file5[(f.get("faccia"), round(f["b"], 1))].append(f["a"])
    for (fac, b), aa in file5.items():
        if len(aa) < 3:
            continue
        aa = sorted(aa)
        passi = set(round(x2 - x1, 1) for x1, x2 in zip(aa, aa[1:]))
        if passi == {32.0}:
            db = min(b, o["lB"] - b)
            check("sistema32 fila a 37", vicino(db, 37.5, 1.5), f"{lab} fila b={b} d={db:.1f}")

# basette: sui fianchi, coppie Ø5 X-dir a y=20/52 alle quote z delle tazze delle ante
cup_z = sorted({round(h["cz"], 1) for lab, p in pezzi.items() if "Anta" in lab
                for h in p["fori"] if h["dia"] == 35.0})
for lab, p in pezzi.items():
    if "Fianco" not in lab:
        continue
    b5 = [h for h in p["fori"] if h["dia"] == 5.0 and h["dir"] == "X"
          and round(h["cy"], 1) in (20.0, 52.0)]
    per_z = defaultdict(set)
    for h in b5:
        per_z[round(h["cz"], 1)].add(round(h["cy"], 1))
    for z in cup_z:
        check("basetta: coppia 20/52 alla quota tazza", per_z.get(z) == {20.0, 52.0},
              f"{lab} z={z} trovate={sorted(per_z.get(z, []))}")

# legrabox (globale)
for lab, p in pezzi.items():
    if "LEGRABOX_Fondo" in lab:
        bb = p["bbox"]
        for h in p["fori"]:
            dx = min(h["cx"] - bb[0], bb[3] - h["cx"])
            dy = h["cy"] - bb[1]
            check("legrabox fondo 50/23.5+128", 48.5 <= dx <= 51 and
                  (vicino(dy, 23.75, 1.2) or vicino(dy, 151.75, 1.2)), f"dx={dx:.1f} dy={dy:.1f}")
    if "LEGRABOX_Schienale" in lab:
        bb = p["bbox"]
        for h in p["fori"]:
            dx = min(h["cx"] - bb[0], bb[3] - h["cx"])
            dz = h["cz"] - bb[2]
            check("legrabox schienale 9+quote", vicino(dx, 9, 1) and
                  (vicino(dz, 19.4, 1) or vicino(dz, 51.4, 1)), f"dx={dx:.1f} dz={dz:.1f}")

print(f"{'CONTROPROVA GENERATORE':40s} {'OK':>5s} {'NO':>4s}")
print("-" * 55)
tot_ok = tot_no = 0
for fam in sorted(R):
    ok, no = R[fam]["ok"], R[fam]["no"]
    tot_ok += ok
    tot_no += no
    print(f"{fam:40s} {ok:5d} {no:4d}")
    for e in R[fam]["esempi"][:3]:
        if e:
            print(f"     MISS {e}")
print("-" * 55)
pct = 100.0 * tot_ok / (tot_ok + tot_no) if tot_ok + tot_no else 0
print(f"{'TOTALE':40s} {tot_ok:5d} {tot_no:4d}  ({pct:.1f}%)")
