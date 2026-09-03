#!/usr/bin/env python3
# LETTO MASTER = testata/parete + 2 comodini + letto contenitore (2000x1600) + guanciali.
# Footprint ESATTO dalla pianta DWG. Altezze: stimate (sezione sepolta) -> DA CONFERMARE.
import cadquery as cq, json, pathlib
from cadquery import exporters
BASE=pathlib.Path(__file__).parent; PAV=1395.0
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))
# --- footprint dalla pianta (trailer mm) ---
# testata/parete al capo (X basso), comodini agli angoli, letto verso X alto
WALL=(558,868,1528,3128)          # testata dietro il capo del letto
NS=[(558,868,1224,1528),(558,868,3128,3592)]   # 2 comodini agli estremi
BED=(573,2573,1528,3128)          # letto 2000x1600
PILL=[(618,1018,1586,2291),(618,1018,2364,3069)]  # 2 guanciali
# --- altezze (STIMATE, da confermare in sezione) ---
Hwall=1100; Hns=550; Hbase=320; Hmat=520; Hpill=650
solids=[]
x0,x1,y0,y1=WALL; solids.append(('testata',box(x0,x1,y0,y1,PAV,PAV+Hwall)))
for i,(x0,x1,y0,y1) in enumerate(NS,1): solids.append((f'comodino{i}',box(x0,x1,y0,y1,PAV,PAV+Hns)))
x0,x1,y0,y1=BED
solids.append(('letto_contenitore',box(x0,x1,y0,y1,PAV,PAV+Hbase)))      # cassone contenitore
solids.append(('materasso',box(x0,x1,y0,y1,PAV+Hbase,PAV+Hmat)))
for i,(x0,x1,y0,y1) in enumerate(PILL,1): solids.append((f'guanciale{i}',box(x0,x1,y0,y1,PAV+Hmat,PAV+Hpill)))
comp=cq.Compound.makeCompound([s.val() for _,s in solids])
exporters.export(comp,str(BASE/'letto_master_review.step'))
def col(l): return '#c7a34e' if 'materasso' in l else '#e8e8ea' if 'guanc' in l else '#8a6a42' if 'contenitore' in l else '#a8825a'
mesh=[]
for lab,s in solids:
    v,t=s.val().tessellate(0.4)
    mesh.append({'l':lab,'c':col(lab),'v':[[round(a.x,1),round(a.y,1),round(a.z,1)] for a in v],'f':[[int(i) for i in f] for f in t]})
json.dump({'pezzo':'LETTO master (testata+contenitore)','mesh':mesh},open(BASE/'letto_master_dettaglio.json','w'),separators=(',',':'))
print('STEP letto:',comp.Volume()/1e9,'m3  solidi:',len(solids))
# --- overlay pianta ---
import ezdxf, matplotlib, numpy as np
matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=ezdxf.readfile('pianta.dxf'); msp=d.modelspace(); TX,TY=2293,3117
def ins(name):
    cs=[e for e in msp if e.dxftype()=='INSERT' and e.dxf.name==name]
    for e in cs:
        xs=[p[0]-TX for v in e.virtual_entities() if v.dxftype()=='LWPOLYLINE' and v.closed for p in v.get_points('xy')]
        ys=[p[1]-TY for v in e.virtual_entities() if v.dxftype()=='LWPOLYLINE' and v.closed for p in v.get_points('xy')]
        if xs and -800<sum(xs)/len(xs)<14000 and -900<sum(ys)/len(ys)<5600: return e
    return cs[0] if cs else None
e=ins('PARETE LETTO_camera master_pianta')
fig,ax=plt.subplots(figsize=(11,11))
for v in e.virtual_entities():
    if v.dxftype()=='LWPOLYLINE':
        p=[(q[0]-TX,q[1]-TY) for q in v.get_points('xy')]
        xs=[a for a,b in p]+([p[0][0]] if v.closed else []);ys=[b for a,b in p]+([p[0][1]] if v.closed else [])
        ax.plot(xs,ys,'-',lw=1.2,color='#999')
for lab,s in solids:
    V=np.array([[a.x,a.y] for a in s.val().tessellate(1)[0]])
    ax.add_patch(plt.Rectangle((V[:,0].min(),V[:,1].min()),np.ptp(V[:,0]),np.ptp(V[:,1]),fill=False,ec='#2ca02c',lw=1.3))
ax.set_aspect('equal');ax.grid(True,lw=.3,alpha=.4);ax.set_title('OVERLAY PIANTA letto master: grigio=DWG, verde=mio')
plt.savefig(BASE/'overlay_letto.png',dpi=110,bbox_inches='tight');print('overlay salvato')
