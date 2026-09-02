#!/usr/bin/env python3
# Estrae il footprint reale (unione sotto-rettangoli) di TUTTI i mobili della pianta assemblata,
# in coord. trailer. Sceglie l'istanza dentro al truck. Salva footprints_all.json.
import ezdxf, json, pathlib
from shapely.geometry import Polygon
from shapely.ops import unary_union
BASE=pathlib.Path(__file__).parent
d=ezdxf.readfile('pianta.dxf'); msp=d.modelspace()
TX,TY=2293,3117

# nome blocco -> (chiave, tipo)  tipo: cabinet|wall|bed|fixture|bench
TARGETS={
 'ARMADIO_camera master_sol.C_pianta':('armadio_master','cabinet'),
 'ARMADIO_camera doppia_pianta':('armadio_doppia','cabinet'),
 'MOBILE LAVABO_bagno doppia_pianta_rev.01':('lavabo_bagno_ant','cabinet'),
 'MOBILE LAVABO_bagno doppia_pianta_rev.02':('lavabo_bagno_post','cabinet'),
 'PARETE LETTO_camera master_pianta':('parete_letto','bed'),
 'F_PARETE DIVISORIA_living-camera master_pianta':('parete_div_master','wall'),
 'F_PARETE DIVISORIA_living-camera doppia_pianta':('parete_divisoria','wall'),
 'DIVANO_pianta':('divano','bench'),
 'LIBRERIA-PARETE_ufficio_rev.01_pianta':('libreria','cabinet'),
 'P.lo PARETE INGRESSO_pianta':('plo_ingresso','wall'),
 'TAVOLO_pianta':('tavolo','table'),
 'BAGNO_camera doppia_rev.01_pianta':('bagno_ant','room'),
 'BAGNO_camera doppia_rev.02_pianta':('bagno_post','room'),
 'BAGNO-LAVANDERIA_pianta_sol.B':('lavanderia','room'),
}
def polys_of(insert):
    out=[]
    for e in insert.virtual_entities():
        if e.dxftype()=='LWPOLYLINE' and e.closed:
            pts=[(p[0]-TX,p[1]-TY) for p in e.get_points('xy')]
            if len(pts)>=3:
                try:
                    pg=Polygon(pts)
                    if pg.is_valid and pg.area>1500: out.append(pg)
                    elif pg.buffer(0).area>1500: out.append(pg.buffer(0))
                except Exception: pass
    return out
def rings_of(u):
    geoms=list(u.geoms) if u.geom_type=='MultiPolygon' else [u]
    R=[]
    for g in geoms:
        g=g.simplify(3.0)
        if g.area>1500: R.append([[round(x,1),round(y,1)] for x,y in g.exterior.coords[:-1]])
    return R

foot={}; meta={}
for e in msp:
    if e.dxftype()!='INSERT' or e.dxf.name not in TARGETS: continue
    key,typ=TARGETS[e.dxf.name]
    pl=polys_of(e)
    if not pl: continue
    u=unary_union(pl); cx,cy=u.centroid.x,u.centroid.y
    if not (-800<cx<14000 and -900<cy<5600): continue   # dentro al truck
    if key in foot: continue
    foot[key]=rings_of(u); meta[key]=typ

json.dump({'foot':foot,'meta':meta},open(BASE/'footprints_all.json','w'))
for k in foot:
    allx=[p[0] for r in foot[k] for p in r]; ally=[p[1] for r in foot[k] for p in r]
    print(f'{k:20s} [{meta[k]:8s}] rings={len(foot[k])} X[{min(allx):.0f},{max(allx):.0f}] Y[{min(ally):.0f},{max(ally):.0f}]')
