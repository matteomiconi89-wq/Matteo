# -*- coding: utf-8 -*-
"""Aggancia i pezzi STEP alle righe di distinta (per SP + due dimensioni maggiori)
e inventaria i blocchi ferramenta (etichette non seriali).
Output: aggancio.json { file: { pezzo: {codice, materiale} } } + report a video."""
import json
import os
import re
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
est = json.load(open(os.path.join(BASE, "estratto_ferramenta.json"), encoding="utf-8"))
dst = json.load(open(os.path.join(BASE, "distinte.json"), encoding="utf-8"))

# mappa file STEP -> distinta
MAPPA = {
    "25-A019_Armadio camera V.stp": "MOBILE_V",
    "25-A019_Armadio camera V (Pezzi corretti).stp": "MOBILE_V",
    "25-A019_Mobile bagno P.stp": "MOBILE_P_DEF",
    "25-A019_Mobile bagno P(pezzi corretti).stp": "MOBILE_P_DEF",
    "25-A019_Mobile_P.stp": "MOBILE_P_DEF",
    "25-A019_Mobile_Q.stp": "MOBILE_Qdef",
    "25-A019_Mobile Q(pezzi corretti).stp": "MOBILE_Qdef",
    "25-A019_Fascetta_Mobile_Q.stp": "MOBILE_Qdef",
    "25-A019_Mobile_R.stp": "MOBILE_R",
    "25-A019_Mobile_W.stp": "MOBILE_W_DEF",
    "25-A019_W_Basamento.stp": "MOBILE_W_DEF",
    "25-A019_AC.stp": "MOBILE_AC",
    "25-A019_T+T1.stp": "MOBILE_T_T1",
    "25-A019_Pannello X.stp": "MOBILE_X",
    "25-A019_Scorrevole S.stp": "MOBILE_S",
    "25-A019_Scorrevole U.stp": "MOBILE_U",
    "25-A019_Pannellatura I.stp": "MOBILE_I",
}

def is_seriale(fk, lab):
    """Etichetta 'seriale' = prefisso del file + numero (pannello anonimo)."""
    base = re.sub(r"[^A-Za-z0-9]", "", os.path.splitext(fk)[0]).lower()
    l = re.sub(r"(__\d+)$", "", lab)
    l = re.sub(r"[^A-Za-z0-9]", "", l).lower()
    l = re.sub(r"\d+$", "", l)
    return l and (l in base or base.startswith(l) or l.startswith(base[:12]))

TOL = 1.5
out = {}
for fk, v in est.items():
    if "error" in v:
        continue
    dnome = MAPPA.get(fk)
    righe = dst.get(dnome, {}).get("righe", []) if dnome else []
    # candidati per (SP, dims): righe con qta residua
    resid = []
    for r in righe:
        try:
            q = int(r["qta"] or 1)
        except Exception:
            q = 1
        for _ in range(q):
            resid.append(r)
    ferramenta, agganciati, orfani = [], {}, []
    for lab, p in sorted(v["pezzi"].items()):
        if not is_seriale(fk, lab):
            ferramenta.append((lab, p["dims_ord"], p["bbox"], p["n_solidi"]))
            continue
        d3 = p["dims_ord"]  # [sp, d1, d2]
        best = None
        for i, r in enumerate(resid):
            try:
                sp, H, L = float(r["SP"]), float(r["H"]), float(r["L"])
            except Exception:
                continue
            dd = sorted([H, L])
            err = abs(d3[0] - sp) + abs(d3[1] - dd[0]) + abs(d3[2] - dd[1])
            if abs(d3[0] - sp) <= TOL and abs(d3[1] - dd[0]) <= TOL and abs(d3[2] - dd[1]) <= TOL:
                if best is None or err < best[1]:
                    best = (i, err)
        if best is not None:
            r = resid.pop(best[0])
            agganciati[lab] = {"codice": r["codice"], "materiale": r["materiale"],
                               "codice_vecchio": r["codice_vecchio"]}
        else:
            orfani.append((lab, d3))
    out[fk] = {"distinta": dnome, "agganciati": agganciati}
    print(f"=== {fk} [{dnome}] : {len(agganciati)} agganciati, {len(orfani)} orfani, {len(ferramenta)} ferramenta ===")
    for lab, d3 in orfani[:10]:
        print(f"   ORFANO {lab:45s} dims={d3}")
    for lab, d3, bb, ns in ferramenta:
        print(f"   FERR   {lab:45s} dims={d3} nsol={ns}")

json.dump(out, open(os.path.join(BASE, "aggancio.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
