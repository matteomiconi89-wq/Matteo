# -*- coding: utf-8 -*-
"""PROVA DEL NOVE del libro delle regole (v2, con le rifiniture del 1o giro):
  - anuba a 50-70 dal filo (simmetriche)
  - cerniera: quota 22.5 su UNO dei due assi (ribalte comprese); viti solo dove esistono
  - fitlock: bordi 80-102 o centro campata
  - rekord: 50 dal retro / 150 dal fronte; Ø12 delle porte con carrelli = canali aste (70/440)
  - sistema32: percentuale di passi multipli di 32 dentro ogni fila
"""
import json
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
pat = json.load(open(os.path.join(BASE, "pattern_pezzi.json"), encoding="utf-8"))
est = json.load(open(os.path.join(BASE, "estratto_ferramenta.json"), encoding="utf-8"))

TOL = 1.5
R = defaultdict(lambda: {"ok": 0, "no": 0, "esempi": []})

def vicino(x, atteso, tol=TOL):
    return abs(x - atteso) <= tol

def check(fam, cond, dettaglio):
    if cond:
        R[fam]["ok"] += 1
    else:
        R[fam]["no"] += 1
        if len(R[fam]["esempi"]) < 5:
            R[fam]["esempi"].append(dettaglio)

for fk, pezzi in pat.items():
    if "corretti" in fk:
        continue
    for lab, p in pezzi.items():
        o = p["orient"]
        fori = p["fori"]
        tag = f"{fk[8:24]}:{lab[-10:]}"

        tazze = [f for f in fori if f["dia"] == 35.0 and f["tipo"] == "FACCIA" and f.get("prof", 0) <= 14]
        svasi51 = [f for f in fori if f["dia"] == 51.0 and f["tipo"] == "FACCIA"]
        def ha_svaso(c):
            return any(vicino(s["a"], c["a"], 2) and vicino(s["b"], c["b"], 2) for s in svasi51)
        cerniere = [c for c in tazze if not ha_svaso(c)]
        fitlock = [f for f in fori if f["dia"] == 35.0 and f["tipo"] == "FACCIA" and ha_svaso(f)]

        # --- CERNIERE: 22.5 dal bordo su UNO dei due assi ---
        if cerniere:
            for c in cerniere:
                da = min(c["a"], o["lA"] - c["a"])
                db = min(c["b"], o["lB"] - c["b"])
                check("cerniera: quota 22.5 dal bordo (un asse)", vicino(da, 22.5) or vicino(db, 22.5),
                      f"{tag} da={da:.1f} db={db:.1f}")
            # linea cerniere: gruppo con stessa b (o stessa a per le ribalte girate)
            per_b = defaultdict(list)
            for c in cerniere:
                per_b[round(c["b"], 1)].append(c["a"])
            for b, aa in per_b.items():
                if len(aa) < 2:
                    continue
                aa = sorted(aa)
                n = len(aa)
                attese = [100.0 + i * (o["lA"] - 200.0) / (n - 1) for i in range(n)]
                for a_reale, a_att in zip(aa, attese):
                    check("cerniera: 100 dai fili + equidistanti", vicino(a_reale, a_att),
                          f"{tag} a={a_reale} att={a_att:.1f}")
                h = o["lA"]
                att_n = 2 if h < 900 else 3 if h < 1600 else 4 if h < 2000 else 5
                check("cerniera: conteggio per altezza", n == att_n,
                      f"{tag} h={h} n={n} att={att_n}")
            # viti: solo sui pezzi che le hanno (le ribalte a tazza sola sono senza)
            v5 = [f for f in fori if f["dia"] == 5.0 and f["tipo"] == "FACCIA"]
            con_viti = []
            for c in cerniere:
                segno = 1 if c["b"] < o["lB"] / 2 else -1
                trovate = sum(1 for dv in (-22.5, 22.5)
                              for f in v5
                              if vicino(f["a"], c["a"] + dv) and vicino(f["b"], c["b"] + segno * 9.5))
                con_viti.append(trovate)
            if any(t > 0 for t in con_viti):
                for c, t in zip(cerniere, con_viti):
                    check("cerniera: 2 viti ±22.5/+9.5", t == 2, f"{tag} tazza a={c['a']} trovate={t}")
            elif cerniere:
                check("cerniera: ribalta senza viti (inserta)", True, "")

        # --- FITLOCK: 80-102 dal bordo oppure centro campata ---
        if fitlock:
            col = sorted(set(round(f["a"]) for f in fitlock))
            rig = sorted(set(round(f["b"]) for f in fitlock))
            for f in fitlock:
                da = min(f["a"], o["lA"] - f["a"])
                db = min(f["b"], o["lB"] - f["b"])
                ok_a = 78 <= da <= 103 or vicino(f["a"], (col[0] + col[-1]) / 2, 12)
                ok_b = 78 <= db <= 103 or vicino(f["b"], (rig[0] + rig[-1]) / 2, 12)
                check("fitlock: griglia ~100 dai bordi + centro", ok_a and ok_b,
                      f"{tag} a={f['a']} b={f['b']}")

        # --- RAFIX ---
        for f in fori:
            if f["dia"] == 14.0 and f["tipo"] == "FACCIA" and vicino(f.get("prof", 0), 15, 1):
                d = min(f["a"], o["lA"] - f["a"], f["b"], o["lB"] - f["b"])
                check("rafix: centro a 21 dal bordo", vicino(d, 21), f"{tag} d={d:.1f}")

        # --- BONE ---
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
                check("bone: quadrato 4xØ5 lato 32", True, "")
                usati.add(i)
                usati.update(quad)

        # --- Ø12 FILO BASSO (rekord / allineamento porte / boccole listelli):
        #     sempre 2 per pezzo, quota dai fili per famiglia: 20/50/70/80-85/150 ---
        d12 = [f for f in fori if f["dia"] == 12.0 and f["tipo"] == "COSTA"
               and 55 <= f.get("prof", 0) <= 70]
        if d12:
            check("d12 filo basso: 2 per pezzo", len(d12) == 2, f"{tag} n={len(d12)}")
            for f in d12:
                lato_len = o["lB"] if f["costa"].startswith("A") else o["lA"]
                d = min(f["pos"], lato_len - f["pos"])
                ok = any(vicino(d, q, 2.5) for q in (20, 30, 50, 70, 80, 85, 150))
                check("d12 filo basso: quota di famiglia (20/50/70/80/150)", ok,
                      f"{tag} pos={f['pos']} lato={lato_len} d={d:.1f}")

        # --- ANUBA ---
        for f in fori:
            if f["dia"] == 8.5 and f["tipo"] == "COSTA" and vicino(f.get("prof", 0), 35, 2):
                lato_len = o["lB"] if f["costa"].startswith("A") else o["lA"]
                d = min(f["pos"], lato_len - f["pos"])
                check("anuba: a 50-70 dal filo", 48 <= d <= 72, f"{tag} pos={f['pos']} lato={lato_len}")
                check("anuba: asse a 5.5 dalla faccia", vicino(f["t"], 5.5, 1) or vicino(o["sp"] - f["t"], 5.5, 1),
                      f"{tag} t={f['t']}")

        # --- SISTEMA 32: solo le vere FILE REGGIPIANO (>=3 fori a passo costante 32/64);
        #     il resto delle Ø5 in faccia sono viti a quote funzionali (fuori regola) ---
        file5 = defaultdict(list)
        for f in fori:
            if f["dia"] == 5.0 and f["tipo"] == "FACCIA":
                file5[(f.get("faccia"), round(f["b"], 1))].append(f["a"])
        for (fac, b), aa in file5.items():
            if len(aa) < 3:
                continue
            aa = sorted(aa)
            passi = [round(x2 - x1, 1) for x1, x2 in zip(aa, aa[1:])]
            uniformi = len(set(passi)) == 1
            if uniformi and passi[0] in (32.0, 64.0):
                db = min(b, o["lB"] - b)
                check("sistema32: fila reggipiano a 37-38 dal bordo",
                      vicino(db, 37.5, 1.5), f"{tag} fila b={b} dist={db:.1f}")

# --- LEGRABOX ---
for fk in ("25-A019_Mobile_Q.stp", "25-A019_Mobile_P.stp"):
    pezzi = est[fk]["pezzi"]
    for lab, p in pezzi.items():
        if "Fondo" in lab and "cassetto" in lab.lower():
            bb = p["bbox"]
            for h in p["fori"]:
                if h["dia"] != 5.0:
                    continue
                dx = min(h["cx"] - bb[0], bb[3] - h["cx"])
                dy_f = h["cy"] - bb[1]
                check("legrabox fondo: 50 dai lati / 23.5+128 dal fronte",
                      48.5 <= dx <= 51 and (vicino(dy_f, 23.75, 1.2) or vicino(dy_f, 151.75, 1.2)),
                      f"{lab[-14:]} dx={dx:.1f} dy={dy_f:.1f}")
        if "Schienale" in lab and "cassetto" in lab.lower():
            bb = p["bbox"]
            for h in p["fori"]:
                if h["dia"] != 5.0:
                    continue
                dx = min(h["cx"] - bb[0], bb[3] - h["cx"])
                dz = h["cz"] - bb[2]
                check("legrabox schienale: 9 dai bordi + quote Blum",
                      vicino(dx, 9, 1) and any(vicino(dz, q, 1) for q in (19.4, 51.4, 115.4, 131.4)),
                      f"{lab[-14:]} dx={dx:.1f} dz={dz:.1f}")

print(f"{'FAMIGLIA':52s} {'OK':>5s} {'NO':>4s} {'%':>6s}")
print("-" * 72)
tot_ok = tot_no = 0
for fam in sorted(R):
    ok, no = R[fam]["ok"], R[fam]["no"]
    tot_ok += ok
    tot_no += no
    pct = 100.0 * ok / (ok + no) if ok + no else 0
    print(f"{fam:52s} {ok:5d} {no:4d} {pct:5.1f}%")
    for e in R[fam]["esempi"][:3]:
        if e:
            print(f"     MISS {e}")
print("-" * 72)
print(f"{'TOTALE':52s} {tot_ok:5d} {tot_no:4d} {100.0*tot_ok/(tot_ok+tot_no):5.1f}%")
