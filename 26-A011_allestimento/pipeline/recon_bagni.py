#!/usr/bin/env python3
# Bagni come da DWG: muri (dal contorno stanza), doccia (piatto+vetri), WC + bidet nelle posizioni
# reali (layer F_SANITARI). + letto camera doppia. Sostituisce i bagni grezzi nella geometria.
import json, pathlib, cadquery as cq
from shapely.geometry import Polygon
BASE=pathlib.Path(__file__).parent
PAV=1395.0
BD=json.load(open(BASE/'bagni_data.json'))
G=json.load(open(BASE/'arredo_geometry_solidi.json'))

def box(x0,x1,y0,y1,z0,z1): return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))
def poly_ext(ring,z0,z1):
    return cq.Workplane('XY',origin=(0,0,z0)).polyline([(x,y) for x,y in ring]).close().extrude(z1-z0)

new={}
def tess(sol):
    v,t=sol.val().tessellate(0.5)
    return {'v':[[round(a.x,1),round(a.y,1),round(a.z,1)] for a in v],'f':[[int(i) for i in f] for f in t]}
def addmesh(key,sol,lab):
    try: new.setdefault(key,[]).append(dict(tess(sol),l=lab))
    except Exception as ex: print('tess err',key,ex)

# bbox reale della stanza bagno (dalla pianta): muri come anello attorno
ROOM={'bagno_ant':(1000,3812,3582,4767),'bagno_post':(10538,13488,3582,4767)}
for key in ('bagno_ant','bagno_post'):
    D=BD[key]
    # --- MURI: anello 90mm attorno al vano bagno, h2100 (lato interno aperto verso corridoio) ---
    rx0,rx1,ry0,ry1=ROOM[key]; tk=90
    try:
        outer=box(rx0,rx1,ry0,ry1,PAV,PAV+2100)
        inner=box(rx0+tk,rx1-tk,ry0+tk,ry1-tk,PAV-10,PAV+2110)
        walls=outer.cut(inner)
        addmesh(key+'_muri',walls,'BAGNO_muro')
    except Exception as ex: print('muri err',key,ex)
    # --- DOCCIA: piatto + 2 vetri ---
    t=D['tray']
    if t:
        x0,y0,x1,y1=t
        addmesh(key+'_sanitari',box(x0,x1,y0,y1,PAV,PAV+120),'DOCCIA_piatto')
        addmesh(key+'_sanitari',box(x0,x0+40,y0,y1,PAV,PAV+1950),'DOCCIA_vetro')      # vetro lato
        addmesh(key+'_sanitari',box(x0,x1,y1-40,y1,PAV,PAV+1950),'DOCCIA_vetro')      # vetro fronte
    # --- WC + bidet ai centri dei cerchi sanitari ---
    for i,(cx,cy,r) in enumerate(sorted(D['circ'])[:2]):
        addmesh(key+'_sanitari',box(cx-185,cx+185,cy-270,cy+270,PAV,PAV+400),'WC' if i==0 else 'BIDET')

# --- LETTO camera doppia (retro): matrimoniale 1600(X) x 2000(Y), testata verso il retro ---
# vano camera doppia: X ~11600..13480, lato living Y ~1100..3300
bx0,by0=11780,1150
addmesh('letto_doppia',box(bx0,bx0+1600,by0,by0+2000,PAV,PAV+350),'LETTO_base')       # base
addmesh('letto_doppia',box(bx0,bx0+1600,by0,by0+2000,PAV+350,PAV+520),'LETTO_mater')  # materasso
addmesh('letto_doppia',box(bx0+1600-60,bx0+1600,by0,by0+2000,PAV,PAV+950),'LETTO_testata') # testata al retro

# --- merge: rimuovi i bagni grezzi, aggiungi i nuovi ---
for old in ('bagno_ant','bagno_post'):
    G['mobili'].pop(old,None)
for k,meshes in new.items():
    G['mobili'][k]=meshes
json.dump(G,open(BASE/'arredo_geometry_solidi.json','w'),separators=(',',':'))
print('nuovi pezzi:',list(new.keys()))
print('mobili totali:',len(G['mobili']))
