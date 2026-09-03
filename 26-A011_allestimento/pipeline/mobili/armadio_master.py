#!/usr/bin/env python3
# ARMADIO camera master — 6 BUSSOLOTTI distinti (ognuno una scatola SOLIDA) collegati da
# fasce di collegamento (base + cappello + schiena continui). SOLIDI veri (B-rep), non facce.
# Struttura e ante ricavate dai fianchi reali della pianta DWG. Coord trailer mm.
# Output (in questa cartella): armadio_master_review.step  +  armadio_master_dettaglio.json
# Nota: per un DWG con SOLIDI, importare lo STEP in AutoCAD (IMPORTA) e salvare in DWG;
#       gli strumenti liberi scrivono nel DWG solo facce, non solidi ACIS.
import cadquery as cq, json, pathlib
from cadquery import exporters
from collections import Counter
HERE=pathlib.Path(__file__).parent
PAV=1395.0; T=18.0; H=2200.0; PLINT=100.0
YB,YF=49.0,629.0
Z0=PAV; ZT=PAV+H
MODS=[(1041,1389),(1425,1873),(1938,2386),(2426,2874),(2939,3387),(3423,3771)]   # fianchi reali
DOORS=[(1044,1394),(1428,1878),(1941,2391),(2421,2871),(2934,3384),(3418,3768)]
TIPI=['ripiani','appenderia','ripiani','ripiani','appenderia','ripiani']          # M2,M5 appenderia (bastone in pianta)
Xtot0,Xtot1=1041.0,3771.0

def box(x0,x1,y0,y1,z0,z1): return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))
solids=[]
# FASCE DI COLLEGAMENTO continue
solids.append(('fascia_base', box(Xtot0,Xtot1,YB,YF,Z0,Z0+PLINT)))
solids.append(('fascia_cappello', box(Xtot0,Xtot1,YB,YF,ZT-T,ZT)))
solids.append(('fascia_schiena', box(Xtot0,Xtot1,YB,YB+T,Z0+PLINT,ZT-T)))
# 6 BUSSOLOTTI (scatole solide) + interni
for i,((xo0,xo1),tp) in enumerate(zip(MODS,TIPI),1):
    xi0,xi1=xo0+T,xo1-T; zc0,zc1=Z0+PLINT,ZT-T
    car=box(xo0,xo0+T,YB+T,YF,zc0,zc1).union(box(xo1-T,xo1,YB+T,YF,zc0,zc1))
    car=car.union(box(xo0,xo1,YB+T,YF,zc0,zc0+T)).union(box(xo0,xo1,YB+T,YF,zc1-T,zc1))
    if tp=='appenderia':
        zs=zc1-360; car=car.union(box(xi0,xi1,YB+T,YF-30,zs,zs+T))
        car=car.union(cq.Workplane('XY').cylinder(xi1-xi0-20,15,direct=(1,0,0),centered=True).translate(((xi0+xi1)/2,(YB+YF)/2,zs-55)))
    else:
        for k in range(1,6):
            z=zc0+k*(zc1-zc0)/6.0; car=car.union(box(xi0,xi1,YB+T,YF-30,z,z+T))
    solids.append((f'bussolotto{i}_{tp}', car))
# ANTE + MANIGLIE
for i,(dx0,dx1) in enumerate(DOORS,1):
    solids.append((f'anta{i}', box(dx0+2,dx1-2,YF+1,YF+1+T,Z0+PLINT+2,ZT-T-2)))
    cxm=(dx0+dx1)/2; hx=dx1-45 if cxm<(Xtot0+Xtot1)/2 else dx0+25
    solids.append((f'maniglia{i}', box(hx,hx+22,YF+1+T,YF+1+T+28,PAV+980,PAV+1300)))

comp=cq.Compound.makeCompound([s.val() for _,s in solids])
exporters.export(comp, str(HERE/'armadio_master_review.step'))
def col(l): return '#6f5334' if l.startswith('fascia') else '#7a5a36' if l.startswith('anta') else '#d8d8dc' if l.startswith('maniglia') else '#a8825a'
mesh=[]
for lab,s in solids:
    v,t=s.val().tessellate(0.3)
    mesh.append({'l':lab,'c':col(lab),'v':[[round(a.x,1),round(a.y,1),round(a.z,1)] for a in v],'f':[[int(i) for i in f] for f in t]})
json.dump({'pezzo':'ARMADIO camera master (6 bussolotti)','W':Xtot1-Xtot0,'D':YF-YB+20,'H':H,'vani':6,'tipi':TIPI,'mesh':mesh},
          open(HERE/'armadio_master_dettaglio.json','w'),separators=(',',':'))
print('STEP solidi:',comp.Volume()/1e9,'m3  n solidi:',len(solids))
