#!/usr/bin/env python3
# LIVING dettagliato: tavolo (piano+gambe), divano a L (chaise), libreria a ripiani.
# Footprint ESATTI dalla pianta DWG.
import cadquery as cq, json, pathlib
from cadquery import exporters
BASE=pathlib.Path('.'); PAV=1395.0
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))
def tess(s):
    v,t=s.val().tessellate(0.4); return {'v':[[round(a.x,1),round(a.y,1),round(a.z,1)] for a in v],'f':[[int(i) for i in f] for f in t]}
OUT={}
def piece(key, parts):   # parts: list of (label,color,solid)
    OUT[key]=[dict(tess(s),l=l,c=c) for l,c,s in parts]

# --- TAVOLO 2000x900, piano a 710-750 + 4 gambe ---
tx0,tx1,ty0,ty1=6358,8358,1960,2860
P=[('piano','#7d7f86',box(tx0,tx1,ty0,ty1,PAV+710,PAV+750))]
for gx in (tx0+80,tx1-140):
    for gy in (ty0+80,ty1-140):
        P.append(('gamba','#5a5c62',box(gx,gx+60,gy,gy+60,PAV,PAV+710)))
piece('tavolo',P)

# --- DIVANO a L (chaise a sx) ---
D=[]
D.append(('schienale','#b5573b',box(4509,7009,54,174,PAV,PAV+780)))          # schienale lungo il muro
D.append(('bracciolo','#b5573b',box(4409,4509,174,1249,PAV,PAV+600)))        # bracciolo sx (chaise)
D.append(('bracciolo','#b5573b',box(6909,7009,174,854,PAV,PAV+600)))         # bracciolo dx
D.append(('seduta','#c86b45',box(4509,5209,174,1249,PAV,PAV+400)))           # chaise (profonda)
D.append(('seduta','#c86b45',box(5209,6909,174,854,PAV,PAV+400)))            # seduta principale
D.append(('cuscino','#d67b52',box(4519,5199,184,1239,PAV+400,PAV+520)))      # cuscino chaise
D.append(('cuscino','#d67b52',box(5219,6899,184,844,PAV+400,PAV+520)))       # cuscino seduta
piece('divano',D)

# --- LIBRERIA ufficio: fianchi + fondo + ripiani ---
lx0,lx1,ly0,ly1=9449,11329,59,1201; H=2080; T=18
L=[('struttura','#3f7fae',box(lx0,lx0+T,ly0,ly1,PAV,PAV+H)),
   ('struttura','#3f7fae',box(lx1-T,lx1,ly0,ly1,PAV,PAV+H)),
   ('struttura','#3f7fae',box(lx0,lx1,ly0,ly0+T,PAV,PAV+H)),          # schienale
   ('struttura','#3f7fae',box(lx0,lx1,ly0,ly1,PAV+H-T,PAV+H))]        # cielo
# montante centrale + ripiani nei due vani
xm=(lx0+lx1)/2
L.append(('struttura','#3f7fae',box(xm-T/2,xm+T/2,ly0,ly1,PAV,PAV+H)))
for zx in (0.18,0.36,0.54,0.72,0.9):
    z=PAV+zx*H
    L.append(('ripiano','#5b9bc9',box(lx0+T,xm-T/2,ly0+T,ly1-40,z,z+T)))
    L.append(('ripiano','#5b9bc9',box(xm+T/2,lx1-T,ly0+T,ly1-40,z,z+T)))
piece('libreria',L)

json.dump(OUT,open(BASE/'living_v2_mesh.json','w'),separators=(',',':'))
print('living pezzi:',{k:len(v) for k,v in OUT.items()})
