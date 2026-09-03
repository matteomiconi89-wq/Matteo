#!/usr/bin/env python3
# ARMADIO camera doppia — 4 BUSSOLOTTI distinti + fasce, SOLIDI veri. Fianchi reali dalla pianta.
# Altezza 2075 (come master); interni: 2 appenderia + 2 cassetti/ripiano (DA CONFERMARE in sezione).
import cadquery as cq, json, pathlib
from cadquery import exporters
BASE=pathlib.Path(__file__).parent; PAV=1395.0; T=18.0; H=2075.0
YB,YF=49.0,669.0; Z0=PAV; ZT=PAV+H; BASE_H=80.0; MID=1150.0; RAIL=1950.0
# 4 bussolotti (bordi esterni, da fianchi 11441/11891/11974/12404/12462/12892/12975/13425)
MODS=[(11432,11900),(11965,12413),(12453,12901),(12966,13434)]
PROG=['appenderia','cassetti','cassetti','appenderia']
Xtot0,Xtot1=11432.0,13434.0
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))
def rail(xi0,xi1,zq): return cq.Workplane('XY').cylinder(xi1-xi0-20,15,direct=(1,0,0),centered=True).translate(((xi0+xi1)/2,(YB+YF)/2,Z0+zq))
def shelf(xi0,xi1,zq): return box(xi0,xi1,YB+T,YF-30,Z0+zq,Z0+zq+T)
def drawer(xi0,xi1,q0,q1): return box(xi0+8,xi1-8,YB+T,YF-40,Z0+q0,Z0+q1)
solids=[]
solids.append(('fascia_base',box(Xtot0,Xtot1,YB,YF,Z0,Z0+BASE_H)))
solids.append(('fascia_cappello',box(Xtot0,Xtot1,YB,YF,ZT-T,ZT)))
solids.append(('fascia_schiena',box(Xtot0,Xtot1,YB,YB+T,Z0+BASE_H,ZT-T)))
for (xo0,xo1),prog in zip(MODS,PROG):
    xi0,xi1=xo0+T,xo1-T; zc0,zc1=Z0+BASE_H,ZT-T
    car=box(xo0,xo0+T,YB+T,YF,zc0,zc1).union(box(xo1-T,xo1,YB+T,YF,zc0,zc1))
    car=car.union(box(xo0,xo1,YB+T,YF,zc0,zc0+T)).union(box(xo0,xo1,YB+T,YF,zc1-T,zc1))
    car=car.union(shelf(xi0,xi1,MID))
    if prog=='appenderia':
        car=car.union(rail(xi0,xi1,RAIL)).union(rail(xi0,xi1,1080))
    else:
        car=car.union(drawer(xi0,xi1,402,502)).union(drawer(xi0,xi1,902,1002)).union(rail(xi0,xi1,RAIL))
    solids.append((f'bussolotto_{prog}',car))
for i,(xo0,xo1) in enumerate(MODS,1):
    solids.append((f'anta{i}',box(xo0+2,xo1-2,YF+1,YF+1+T,Z0+2,ZT-2)))
    cxm=(xo0+xo1)/2; hx=xo1-45 if cxm<(Xtot0+Xtot1)/2 else xo0+25
    solids.append((f'maniglia{i}',box(hx,hx+22,YF+1+T,YF+1+T+28,PAV+960,PAV+1280)))
comp=cq.Compound.makeCompound([s.val() for _,s in solids])
exporters.export(comp,str(BASE/'armadio_doppia_review.step'))
def col(l): return '#6f5334' if l.startswith('fascia') else '#7a5a36' if l.startswith('anta') else '#d8d8dc' if l.startswith('maniglia') else '#96733f'
mesh=[]
for lab,s in solids:
    v,t=s.val().tessellate(0.35)
    mesh.append({'l':lab,'c':col(lab),'v':[[round(a.x,1),round(a.y,1),round(a.z,1)] for a in v],'f':[[int(i) for i in f] for f in t]})
json.dump({'pezzo':'ARMADIO camera doppia (4 bussolotti)','mesh':mesh},open(BASE/'armadio_doppia_dettaglio.json','w'),separators=(',',':'))
print('STEP doppia:',comp.Volume()/1e9,'m3 solidi',len(solids),'  bbox W=',Xtot1-Xtot0)
