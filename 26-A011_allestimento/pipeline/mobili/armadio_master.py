#!/usr/bin/env python3
# ARMADIO camera master — 6 BUSSOLOTTI distinti + fasce di collegamento, SOLIDI veri (B-rep).
# GUSCIO: dai fianchi reali della PIANTA (verificato: overlay pianta combacia al mm).
# INTERNI + ALTEZZA: dalla SEZIONE del progetto DWG (verificato: overlay sezione).
#   - altezza mobile 2075 (ante ~2074), divisione orizzontale ~1150,
#   - bussolotti 2 e 5 = appenderia (bastone, dalla pianta),
#   - vani centrali = cassetti (402-502, 902-1002) + ripiano 1152 + appenderia sopra,
#   - vani estremi = colonne a ripiani.
# Output: armadio_master_review.step + armadio_master_dettaglio.json
import cadquery as cq, json, pathlib
from cadquery import exporters
from collections import Counter
HERE=pathlib.Path(__file__).parent
PAV=1395.0; T=18.0; H=2075.0                 # <-- altezza corretta dalla sezione (era 2200)
YB,YF=49.0,629.0
Z0=PAV; ZT=PAV+H
BASE_H=80.0                                   # zoccolo/base interna
MID=1150.0                                    # divisione orizzontale dalla sezione
RAIL=1950.0                                   # bastone appenderia (zona alta)
MODS=[(1041,1389),(1425,1873),(1938,2386),(2426,2874),(2939,3387),(3423,3771)]
DOORS=[(1044,1394),(1428,1878),(1941,2391),(2421,2871),(2934,3384),(3418,3768)]
# programma interno per bussolotto (dalla pianta+sezione)
PROG=['ripiani','appenderia','cassetti','cassetti','appenderia','ripiani']
Xtot0,Xtot1=1041.0,3771.0

def box(x0,x1,y0,y1,z0,z1): return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))
def rail(xi0,xi1,zq): return cq.Workplane('XY').cylinder(xi1-xi0-20,15,direct=(1,0,0),centered=True).translate(((xi0+xi1)/2,(YB+YF)/2,Z0+zq))
solids=[]
# FASCE DI COLLEGAMENTO continue
solids.append(('fascia_base', box(Xtot0,Xtot1,YB,YF,Z0,Z0+BASE_H)))
solids.append(('fascia_cappello', box(Xtot0,Xtot1,YB,YF,ZT-T,ZT)))
solids.append(('fascia_schiena', box(Xtot0,Xtot1,YB,YB+T,Z0+BASE_H,ZT-T)))

def shelf(xi0,xi1,zq): return box(xi0,xi1,YB+T,YF-30,Z0+zq,Z0+zq+T)
def drawer(xi0,xi1,zq0,zq1): return box(xi0+8,xi1-8,YB+T,YF-40,Z0+zq0,Z0+zq1)

for (xo0,xo1),prog in zip(MODS,PROG):
    xi0,xi1=xo0+T,xo1-T; zc0,zc1=Z0+BASE_H,ZT-T
    car=box(xo0,xo0+T,YB+T,YF,zc0,zc1).union(box(xo1-T,xo1,YB+T,YF,zc0,zc1))   # fianchi
    car=car.union(box(xo0,xo1,YB+T,YF,zc0,zc0+T)).union(box(xo0,xo1,YB+T,YF,zc1-T,zc1))  # fondo+cielo
    car=car.union(shelf(xi0,xi1,MID))          # divisione orizzontale (tutti)
    if prog=='appenderia':                      # bussolotti 2,5 (bastone dalla pianta)
        car=car.union(rail(xi0,xi1,RAIL))       # appenderia alta
        car=car.union(rail(xi0,xi1,1080))       # appenderia bassa (doppia)
    elif prog=='cassetti':                      # vani centrali 3,4 (dalla sezione)
        car=car.union(drawer(xi0,xi1,402,502)).union(drawer(xi0,xi1,902,1002))  # cassetti 402-502, 902-1002
        car=car.union(rail(xi0,xi1,RAIL))       # appenderia sopra la divisione
    else:                                       # ripiani (colonne estreme 1,6)
        for zq in (330,650,1450,1720): car=car.union(shelf(xi0,xi1,zq))
    solids.append((f'bussolotto_{prog}', car))

# ANTE + MANIGLIE (ante ~2074 quasi a tutta altezza)
for i,(dx0,dx1) in enumerate(DOORS,1):
    solids.append((f'anta{i}', box(dx0+2,dx1-2,YF+1,YF+1+T,Z0+2,ZT-2)))
    cxm=(dx0+dx1)/2; hx=dx1-45 if cxm<(Xtot0+Xtot1)/2 else dx0+25
    solids.append((f'maniglia{i}', box(hx,hx+22,YF+1+T,YF+1+T+28,PAV+960,PAV+1280)))

comp=cq.Compound.makeCompound([s.val() for _,s in solids])
exporters.export(comp, str(HERE/'armadio_master_review.step'))
def col(l): return '#6f5334' if l.startswith('fascia') else '#7a5a36' if l.startswith('anta') else '#d8d8dc' if l.startswith('maniglia') else '#a8825a'
mesh=[]
for lab,s in solids:
    v,t=s.val().tessellate(0.3)
    mesh.append({'l':lab,'c':col(lab),'v':[[round(a.x,1),round(a.y,1),round(a.z,1)] for a in v],'f':[[int(i) for i in f] for f in t]})
json.dump({'pezzo':'ARMADIO camera master (6 bussolotti)','W':Xtot1-Xtot0,'D':YF-YB+20,'H':H,'vani':6,'tipi':PROG,'mesh':mesh},
          open(HERE/'armadio_master_dettaglio.json','w'),separators=(',',':'))
print('STEP:',comp.Volume()/1e9,'m3  n solidi:',len(solids),'H=',H)
