#!/usr/bin/env python3
# ARMADIO camera MASTER — costruttore DETTAGLIATO (proposta in revisione con Matteo).
# Carcassa (sp.18) + montanti + ripiani + cassetti + ante + maniglie + bastoni appenderia.
# Dati vani/ante dalla PIANTA DWG (6 vani, 6 ante). Coord trailer mm.
# Output (in questa cartella): armadio_master_review.step  +  armadio_master_dettaglio.json
# Quando la geometria e' confermata, si integra in ../ricostruisci.py.
import cadquery as cq, json, pathlib
from cadquery import exporters
from collections import Counter
HERE=pathlib.Path(__file__).parent
PAV=1395.0
# --- dati dalla pianta (ARMADIO_camera master_sol.C_pianta) ---
X0,X1=1005.0,3807.0            # larghezza 2802
YB,YF=49.0,657.0              # YB=schienale (parete esterna), YF=fronte ante (verso stanza/letto)
H=2200.0; T=18.0; PLINT=100.0
Z0=PAV; ZT=PAV+H; Zb=Z0+PLINT+T; Zt=ZT-T
MONT=[1407,1906,2406,2907,3405]                       # centri montanti interni (dalla pianta)
DOORS=[(1048,350),(1436,450),(1945,450),(2429,450),(2942,450),(3426,350)]  # (x_sx, larghezza)
inner=[X0+T]+[m+T/2 for m in MONT]
right=[m-T/2 for m in MONT]+[X1-T]
VANI=list(zip(inner,right))
TIPI=['r','a','c','c','a','r']    # r=ripiani  a=appenderia  c=cassetti+appenderia  (DA CONFERMARE)

parts=[]
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))
def add(lab,x0,x1,y0,y1,z0,z1): parts.append((lab,box(x0,x1,y0,y1,z0,z1)))

# CARCASSA
add('carcassa', X0,X0+T, YB,YF, Z0+PLINT, ZT)
add('carcassa', X1-T,X1, YB,YF, Z0+PLINT, ZT)
add('carcassa', X0,X1, YB,YF, Z0+PLINT, Z0+PLINT+T)
add('carcassa', X0,X1, YB,YF, ZT-T, ZT)
add('carcassa', X0,X1, YB,YB+T, Z0+PLINT, ZT)
add('zoccolo',  X0,X1, YF-T,YF, Z0, Z0+PLINT)
add('zoccolo',  X0,X1, YB,YB+T, Z0, Z0+PLINT)
for xc in MONT: add('montante', xc-T/2,xc+T/2, YB+T,YF, Zb, Zt)

# INTERNI
for (xs,xd),tp in zip(VANI,TIPI):
    if tp=='r':
        for i in range(1,7):
            z=Zb+i*(Zt-Zb)/7.0; add('ripiano', xs,xd, YB+T,YF-30, z,z+T)
    elif tp=='a':
        zs=Zt-360; add('ripiano', xs,xd, YB+T,YF-30, zs,zs+T)
        parts.append(('bastone',cq.Workplane('XY').cylinder(xd-xs-20,15,direct=(1,0,0),centered=True).translate(((xs+xd)/2,(YB+YF)/2,zs-45))))
    else:
        for k in range(3):
            zc=Zb+k*230; add('cassetto', xs+8,xd-8, YB+T,YF-40, zc+8,zc+222)
        zs=Zb+3*230+40; add('ripiano', xs,xd, YB+T,YF-30, zs,zs+T)
        za=Zt-360; add('ripiano', xs,xd, YB+T,YF-30, za,za+T)
        parts.append(('bastone',cq.Workplane('XY').cylinder(xd-xs-20,15,direct=(1,0,0),centered=True).translate(((xs+xd)/2,(YB+YF)/2,za-45))))

# ANTE + MANIGLIE
for dx,dw in DOORS:
    add('anta', dx+2,dx+dw-2, YF, YF+T, Z0+PLINT+2, ZT-2)
    hx = dx+dw-45 if (dx+dw/2)<(X0+X1)/2 else dx+30
    parts.append(('maniglia',box(hx,hx+22, YF+T,YF+T+28, PAV+980, PAV+1300)))

# STEP (52 corpi separati: comodo da editare in CAD)
comp=cq.Compound.makeCompound([p[1].val() for p in parts])
exporters.export(comp, str(HERE/'armadio_master_review.step'))

# mesh etichettata per il viewer di controllo
COL={'carcassa':'#a8825a','zoccolo':'#6f5334','montante':'#b8946a','ripiano':'#c9a878',
     'cassetto':'#8a6a42','anta':'#7a5a36','maniglia':'#d8d8dc','bastone':'#9aa0a6'}
mesh=[]
for lab,s in parts:
    v,t=s.val().tessellate(0.3)
    mesh.append({'l':lab,'c':COL[lab],'v':[[round(a.x,1),round(a.y,1),round(a.z,1)] for a in v],'f':[[int(i) for i in f] for f in t]})
json.dump({'pezzo':'ARMADIO camera master','W':X1-X0,'D':YF-YB,'H':H,'vani':len(VANI),'tipi':TIPI,'mesh':mesh},
          open(HERE/'armadio_master_dettaglio.json','w'),separators=(',',':'))
print('STEP:',comp.Volume()/1e9,'m3  parti:',len(parts),dict(Counter(l for l,_ in parts)))
