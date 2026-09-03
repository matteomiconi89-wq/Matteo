# -*- coding: utf-8 -*-
"""A) LEGRABOX: per ogni cassetto (fondo+schienale), trova i fori Ø5 orizzontali
dei pezzi vicini ai lati del cassetto -> pattern di fissaggio guide
(quota Y dal fronte cassetto, quota Z dal piano del fondo).
B) KREMENS (cabina W): posizioni cremagliere KC, staffe KME, fori Ø10 sottostruttura."""
import json
import os
import re
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
est = json.load(open(os.path.join(BASE, "estratto_ferramenta.json"), encoding="utf-8"))

print("################ A) GUIDE LEGRABOX ################")
for fk in ("25-A019_Mobile_Q.stp", "25-A019_Mobile_P.stp"):
    pezzi = est[fk]["pezzi"]
    fondi = {lab: p for lab, p in pezzi.items() if lab.startswith("Fondo_del_cassetto") or
             ("Symmetry" in lab and "Fondo" in lab)}
    print(f"\n=== {fk} ===")
    for flab, fp in sorted(fondi.items()):
        bb = fp["bbox"]  # fondo: X lati, Y fronte-retro, Z quota
        z_fondo = bb[2]
        y_fronte = bb[1]
        print(f"--- {flab}")
        print(f"    fondo X[{bb[0]:.0f},{bb[3]:.0f}] Y[{bb[1]:.0f},{bb[4]:.0f}] Zsotto={z_fondo:.0f}")
        # fori X-diretti di ALTRI pezzi vicino ai lati del cassetto (entro 60 mm fuori)
        for lab, p in sorted(pezzi.items()):
            if lab in fondi or "cassetto" in lab.lower():
                continue
            vicini = []
            for h in p["fori"]:
                if h["dir"] != "X":
                    continue
                if not (z_fondo - 60 <= h["cz"] <= z_fondo + 120):
                    continue
                # il foro deve stare vicino (in X) a un lato del cassetto
                lato = None
                if abs(h["cx"] - bb[0]) < 60:
                    lato = "SX"
                elif abs(h["cx"] - bb[3]) < 60:
                    lato = "DX"
                if lato is None:
                    continue
                if not (bb[1] - 60 <= h["cy"] <= bb[4] + 60):
                    continue
                vicini.append((lato, h))
            if vicini:
                print(f"    {lab}:")
                for lato, h in sorted(vicini, key=lambda t: (t[0], t[1]["cy"])):
                    print(f"       {lato} D{h['dia']:4.1f} len={h['len']:5.1f} "
                          f"Y={h['cy']:7.1f} (dal fronte {h['cy']-y_fronte:+7.1f}) "
                          f"Z={h['cz']:7.1f} (dal fondo {h['cz']-z_fondo:+6.1f})")

print()
print("################ B) KREMENS cabina W ################")
pezzi = est["25-A019_Mobile_W.stp"]["pezzi"]
kc = {lab: p for lab, p in pezzi.items() if lab.startswith("PAVANELLO")}
kme = {lab: p for lab, p in pezzi.items() if lab.startswith("KME")}
print("=== Cremagliere KC (bbox) ===")
for lab, p in sorted(kc.items()):
    bb = p["bbox"]
    print(f"{lab:32s} X[{bb[0]:7.1f},{bb[3]:7.1f}] Y[{bb[1]:7.1f},{bb[4]:7.1f}] Z[{bb[2]:7.1f},{bb[5]:7.1f}]")
print()
print("=== Staffe KME05: raggruppate per (X centro, Z centro) ===")
livelli = defaultdict(list)
for lab, p in kme.items():
    bb = p["bbox"]
    cx = round((bb[0] + bb[3]) / 2, 0)
    cz = round((bb[2] + bb[5]) / 2, 0)
    livelli[(cx, cz)].append(lab)
per_x = defaultdict(list)
for (cx, cz), labs in sorted(livelli.items()):
    per_x[cx].append(cz)
for cx, zz in sorted(per_x.items()):
    zz = sorted(zz)
    dz = [round(b - a) for a, b in zip(zz, zz[1:])]
    print(f"X={cx:7.1f}: quote Z {[round(z) for z in zz]}  Δ={dz}")
print()
print("=== Sottostruttura: fori Ø10×18 (posizioni X globali vs cremagliere) ===")
for lab, p in sorted(pezzi.items()):
    if not lab.startswith("25-A019_Sottostruttura"):
        continue
    xx = sorted({round(h["cx"], 1) for h in p["fori"] if h["dia"] == 10.0})
    zz = sorted({round(h["cz"], 1) for h in p["fori"] if h["dia"] == 10.0})
    if xx:
        bb = p["bbox"]
        print(f"{lab} bbox X[{bb[0]:.0f},{bb[3]:.0f}] Y[{bb[1]:.0f},{bb[4]:.0f}]")
        print(f"   X fori: {xx}")
        print(f"   Z fori: {zz}")
