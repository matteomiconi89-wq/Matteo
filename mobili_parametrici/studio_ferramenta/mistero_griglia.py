# -*- coding: utf-8 -*-
"""Chi sono i pannelli con griglia Ø35+Ø51? Materiale da distinta + posizione nel mobile
(la faccia T+ delle tazze guarda il muro o la stanza?). E il Ø22 che li attraversa."""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
est = json.load(open(os.path.join(BASE, "estratto_ferramenta.json"), encoding="utf-8"))
dst = json.load(open(os.path.join(BASE, "distinte.json"), encoding="utf-8"))
agg = json.load(open(os.path.join(BASE, "aggancio.json"), encoding="utf-8"))

CASI = [
    ("25-A019_Mobile_P.stp", "25-A019_Mobile bagno P035", "MOBILE_P_DEF"),
    ("25-A019_Mobile_Q.stp", "25-A019_Mobile Q018", "MOBILE_Qdef"),
    ("25-A019_Armadio camera V.stp", "25-A019_Armadio camera V133", "MOBILE_V"),
]
for fk, lab, dn in CASI:
    p = est[fk]["pezzi"][lab]
    cod = agg[fk]["agganciati"].get(lab, {}).get("codice")
    mat = None
    for r in dst[dn]["righe"]:
        if str(r["codice"]) == str(cod):
            mat = r
            break
    # bbox del mobile intero
    tutti = [q["bbox"] for q in est[fk]["pezzi"].values()]
    mob = [min(b[0] for b in tutti), min(b[1] for b in tutti), min(b[2] for b in tutti),
           max(b[3] for b in tutti), max(b[4] for b in tutti), max(b[5] for b in tutti)]
    print(f"=== {fk} :: {lab} ===")
    print(f"  codice={cod} materiale={mat['materiale'] if mat else '?'} "
          f"H={mat['H'] if mat else '?'} L={mat['L'] if mat else '?'} SP={mat['SP'] if mat else '?'}")
    print(f"  bbox pezzo : {[round(x) for x in p['bbox']]}")
    print(f"  bbox mobile: {[round(x) for x in mob]}")
    fam = {}
    for h in p["fori"]:
        fam.setdefault((h["dia"], h["dir"]), []).append(h)
    for (dia, d), hh in sorted(fam.items()):
        print(f"  D{dia} dir={d} x{len(hh)}: ", end="")
        print("; ".join(f"({h['cx']:.0f},{h['cy']:.0f},{h['cz']:.0f})lo{h['lo']:.0f}hi{h['hi']:.0f}" for h in hh[:8]))
    print()

# e le controparti Ø22 nel mobile P (schiena P031)
print("=== Mobile P: fori Ø22 di P031 (schiena) e P035 (multistrato) ===")
for lab in ("25-A019_Mobile bagno P031", "25-A019_Mobile bagno P035"):
    p = est["25-A019_Mobile_P.stp"]["pezzi"][lab]
    for h in p["fori"]:
        if h["dia"] == 22.0:
            print(f"  {lab[-4:]}: dir={h['dir']} c=({h['cx']:.0f},{h['cy']:.0f},{h['cz']:.0f}) lo={h['lo']:.0f} hi={h['hi']:.0f} len={h['len']}")
