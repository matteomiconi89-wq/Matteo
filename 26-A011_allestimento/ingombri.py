#!/usr/bin/env python3
# Aggiunge gli INGOMBRI (box placeholder) degli altri mobili alle posizioni della planimetria,
# accanto ai 3 mobili gia' dettagliati come solidi. Coord trailer (mm), pavimento a 1395.
import json, pathlib
BASE = pathlib.Path(__file__).parent
PAV = 1395.0

def box(x0,x1,y0,y1,z0,z1):
    v=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]]
    f=[[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[0,3,7,4]]
    return {"l":"INGOMBRO","v":v,"f":f}

# posizioni dal plan (trailer_X=plan_X-2293, trailer_Y=plan_Y-3117). H = stima per tipo.
# nome: (X0,X1, Y0,Y1, H_da_pavimento, lato)
ING = {
 "divano":            (4409,7009,   54,1004,  850,  "ingresso"),
 "tavolo_sedie":      (5983,8733,  1502,3318, 760,  "centro"),
 "libreria_ufficio":  (9440,11383,   61,1666, 2080, "ingresso/living"),  # dim reali dal DWG 1943x1605x2080
 "armadio_cam_doppia":(11382,13484,  61, 661, 2200, "ingresso"),
 "lavatrice":         (9558,10485, 4179,4779,  850, "cucina"),
 "lavabo_bagno":      (10543,12641,4362,4762, 1000, "cucina"),
}
out={}
for k,(x0,x1,y0,y1,h,lato) in ING.items():
    out[k]={"lato":lato,"dim":[round(x1-x0),round(y1-y0),h],"mesh":[box(x0,x1,y0,y1,PAV,PAV+h)]}

D=json.load(open(BASE/"arredo_geometry2.json"))
D["ingombri"]=out
json.dump(D,open(BASE/"arredo_geometry3.json","w"),separators=(",",":"))
import os;print("scritto arredo_geometry3.json",os.path.getsize(BASE/"arredo_geometry3.json")//1024,"KB")
for k,v in out.items(): print(f"  {k:20s} {v['dim'][0]}x{v['dim'][1]}x{v['dim'][2]}  [{v['lato']}]")
