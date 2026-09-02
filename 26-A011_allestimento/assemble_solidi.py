#!/usr/bin/env python3
# Posa gli 8 solidi reali (STL esportati da Matteo, decimati) nelle posizioni della
# PIANTA_GENERALE (footprint estratti dal DXF, trasform. trailer_X=planX-2293, trailer_Y=planY-3117).
# Unisce ai mobili gia' dettagliati (mobile_ingresso, lavabo_lavanderia, cucina) e al guscio scocca.
import json, pathlib
BASE = pathlib.Path(__file__).parent
PAV = 1395.0  # pavimento finito

COA = json.load(open(BASE/"stl_b64"/"coarse.json"))  # {name:{v,f,wmin,wmax}}

# posa: (X0, Y0, swap, note). world = (X0+x, Y0+y, PAV+z), swap => scambia x/y locali.
# X0,Y0 in coord trailer (mm). Footprint da PIANTA_GENERALE dove combacia con le quote STL.
PLACE = {
 # confidenti: footprint pianta combacia con le quote STL
 "divano":           (4409,  54, False, "living/ingresso — DIVANO_pianta 2600x1195 (match)"),
 "libreria":         (9440,  59, False, "living — LIBRERIA-PARETE ufficio (match)"),
 "plo_ingresso":     (7564,  49, False, "P.lo PARETE INGRESSO 1822x82 (match)"),
 # pareti / camera: ancorate al footprint pianta
 "parete_letto":     ( 504,1224, False, "camera master — PARETE LETTO (fronte truck)"),
 "parete_divisoria": (11040,1201, True, "divisorio living/camera doppia (parete trasversale, dietro libreria)"),
 # baia cucina/lavanderia/bagno: contro parete esterna (Y alto ~4762) o fronte corridoio
 "lavatrice":        (9405,4073, False, "lavanderia — colonna lavatrice, contro parete est."),
 "muretti_bagni":    (10543,4231,False, "bagno doppia — muretti (h 1195)"),
 "pli_lavanderia":   (8385,4100, False, "PLI porta/parete lavanderia (partizione corridoio)"),
}

def place_mesh(name):
    P = PLACE[name]; X0,Y0,swap,note = P
    obj = COA[name]
    V = obj["v"]; F = obj["f"]
    wmin = obj["wmin"]; wmax = obj["wmax"]
    # bbox reale dei vertici coarse (il clustering li ha ristretti verso l'interno)
    amn = [min(p[a] for p in V) for a in range(3)]
    amx = [max(p[a] for p in V) for a in range(3)]
    def rescale(p):
        r=[]
        for a in range(3):
            span = amx[a]-amn[a]
            if span < 1e-6:
                r.append(wmin[a])
            else:
                r.append(wmin[a] + (p[a]-amn[a])/span*(wmax[a]-wmin[a]))
        return r
    world_v = []
    for p in V:
        x,y,z = rescale(p)      # quote reali esatte (riempie il bbox vero)
        if swap: X,Y = X0+y, Y0+x
        else:    X,Y = X0+x, Y0+y
        world_v.append([round(X,1),round(Y,1),round(PAV+z,1)])
    return [{"l":"SOLID_"+name,"v":world_v,"f":F}]

# ---- carica geometria esistente (guscio + mobili dettagliati) ----
G = json.load(open(BASE/"arredo_geometry3.json"))
out = {
 "shell_step": G.get("shell_step",[]),
 "aperto": G["aperto"],
 "mobili": dict(G["mobili"]),      # mobile_ingresso, lavabo_lavanderia, cucina
 "ingombri": {}
}
# aggiungi gli 8 solidi reali ai mobili
for name in PLACE:
    out["mobili"][name] = place_mesh(name)

# ingombri residui: solo cio' che NON ha un solido (tavolo, armadio camera doppia)
for k in ("tavolo_sedie","armadio_cam_doppia"):
    if k in G["ingombri"]:
        out["ingombri"][k] = G["ingombri"][k]

p = BASE/"arredo_geometry_solidi.json"
p.write_text(json.dumps(out,separators=(",",":")))
import os
print("scritto", p.name, os.path.getsize(p)//1024,"KB")
print("mobili:", list(out["mobili"].keys()))
print("ingombri:", list(out["ingombri"].keys()))
for name in PLACE:
    m=out["mobili"][name]
    xs=[c[0] for mm in m for c in mm["v"]]; ys=[c[1] for mm in m for c in mm["v"]]; zs=[c[2] for mm in m for c in mm["v"]]
    print(f"  {name:18s} X[{min(xs):.0f},{max(xs):.0f}] Y[{min(ys):.0f},{max(ys):.0f}] Z[{min(zs):.0f},{max(zs):.0f}]")
