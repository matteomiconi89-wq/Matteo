#!/usr/bin/env python3
# Assembla scocca 26A011 (guscio) + 3 mobili solidi posizionati dalla planimetria generale.
# Coordinate mondo trailer: X=lunghezza(0 fronte), Y=larghezza(0 ingresso ester), Z=altezza da terra; pavimento a 1395.
import json, pathlib

BASE = pathlib.Path(__file__).parent
REPO = pathlib.Path("/home/user/Matteo")
PAV = 1395.0  # quota pavimento finito

def box_to_mesh(bx, by, bz):
    (x0,x1),(y0,y1),(z0,z1) = bx,by,bz
    v = [[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],
         [x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]]
    f = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[0,3,7,4]]
    return v, f

out = {"aperto": [], "mobili": {}}

# ---------- 1) GUSCIO scocca (config aperto) ----------
scocca = json.loads((REPO/"26-A011_scocca"/"geometry.json").read_text())
out["aperto"] = scocca["aperto"]

# ---------- helper: aggiungi mobile trasformando local->world ----------
def add_piece(key, meshes_local, place):
    """place(x,y,z)->(X,Y,Z) trasforma un punto locale in coordinate mondo trailer."""
    world = []
    for m in meshes_local:
        vw = [list(place(*p)) for p in m["v"]]
        world.append({"l": m["l"], "v": [[round(c,1) for c in p] for p in vw], "f": m["f"]})
    out["mobili"][key] = world

# ---------- 2) MOBILE INGRESSO-LIVING (41 box) ----------
# local: X=larghezza(0..1112.5), Y=profondita(0 ante lato ingresso .. 600 vetrina lato living), Z da base
# posa: divisorio, lungo X del trailer; X 6780..7892; back(vetrina) verso corridoio.
mi = json.loads((REPO/"26-A011_allestimento"/"mobili"/"mobile_ingresso_volumi.json").read_text())
mi_meshes = []
for p in mi["pannelli"]:
    v,f = box_to_mesh(*p["box"])
    lay = {"CERA":"MOB_CERA","OPACO":"MOB_OPACO","VETRO":"MOB_VETRO"}.get(p["m"],"MOB_CERA")
    mi_meshes.append({"l":lay,"v":v,"f":f})
MI_X0, MI_Yfront = 6780.0, 613.0   # ante lato ingresso a Y 613, vetrina verso corridoio (Y 1213)
add_piece("mobile_ingresso", mi_meshes,
          lambda x,y,z: (MI_X0 + x, MI_Yfront + y, PAV + z))

# ---------- 3) LAVABO LAVANDERIA (74 mesh reali) ----------
# local: X=larghezza(0..1173), Y=profondita(-8..600 parete attrezzata al fondo), Z(0..2215)
# posa: baia cucina, contro parete esterna (Y alto), fronti verso corridoio; X 8385..9558
lav = json.loads((REPO/"26-A011_allestimento"/"mobili"/"lavabo_lavanderia_mesh.json").read_text())
lav_meshes = [{"l":"LAV_"+m["l"].replace("VOL_",""),"v":m["v"],"f":m["f"]} for m in lav]
LAV_X0, LAV_Yfront = 8385.0, 4179.0   # fronte a Y 4179 (verso corridoio), parete verso esterno 4779
add_piece("lavabo_lavanderia", lav_meshes,
          lambda x,y,z: (LAV_X0 + x, LAV_Yfront + y, PAV + z))

# ---------- 4) CUCINA (box dalle misure di collaudo v10) ----------
# moduli da SPEC_COLLAUDO cucina: frigo 610, forno 620, lavello 600, lavastov 598, cassettiera 554,
# piano cottura 600, dispensa 300 -> lungo X 4416.. ; contro parete esterna baia cucina.
cuc_mods = [("frigo",610,2025),("forno",620,2025),("lavello",600,900),("lavastov",598,900),
            ("cassettiera",554,900),("cottura",600,900),("dispensa",300,2025)]
cx = 4416.0
cuc_meshes = []
DEPTH = 600.0
for name,w,h in cuc_mods:
    # base/colonna
    v,f = box_to_mesh((cx, cx+w), (0, DEPTH), (0, h))
    lay = "CUC_COLONNA" if h>1500 else "CUC_BASE"
    cuc_meshes.append({"l":lay,"v":v,"f":f})
    # top per le basi
    if h < 1500:
        v2,f2 = box_to_mesh((cx, cx+w), (0, DEPTH), (h, h+40))
        cuc_meshes.append({"l":"CUC_TOP","v":v2,"f":f2})
    cx += w
# pensili a ribalta sopra le basi (4 ante), da +1350 a +2025
pens_x0, pens_x1 = 4416+610+620, 4416+610+620+600+598+554+600  # sopra lavello..cottura
v,f = box_to_mesh((pens_x0, pens_x1), (0, 360), (1350, 1667))
cuc_meshes.append({"l":"CUC_PENSILE","v":v,"f":f})
CUC_Yfront = 4179.0
add_piece("cucina", cuc_meshes,
          lambda x,y,z: (x, CUC_Yfront + y, PAV + z))

# ---------- scrivi ----------
p = BASE/"arredo_geometry.json"
p.write_text(json.dumps(out, separators=(",",":")))
import os
print("scritto", p.name, os.path.getsize(p)//1024, "KB")
for k,v in out["mobili"].items():
    xs=[c[0] for m in v for c in m["v"]]; ys=[c[1] for m in v for c in m["v"]]; zs=[c[2] for m in v for c in m["v"]]
    print(f"  {k:20s} {len(v):3d} solidi  X[{min(xs):.0f},{max(xs):.0f}] Y[{min(ys):.0f},{max(ys):.0f}] Z[{min(zs):.0f},{max(zs):.0f}]")
