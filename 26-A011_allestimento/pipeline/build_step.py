#!/usr/bin/env python3
# Costruisce SOLIDI 3D veri (STEP) estrudendo i footprint reali della pianta alle quote esatte.
# Esporta arredo_solidi.step (assieme) e le maglie tessellate per il viewer (mobili_step.json).
import json, pathlib, cadquery as cq
from cadquery import exporters
import numpy as np
BASE=pathlib.Path(__file__).parent
PAV=1395.0
foot=json.load(open(BASE/'footprints.json'))          # {piece:[ring,...]} coord trailer (mm)
COA=json.load(open(BASE/'stl_b64'/'coarse.json'))     # per le quote reali (wmin/wmax)

def H(piece):  # altezza reale (mm) dallo STL
    o=COA[piece]; return o['wmax'][2]-o['wmin'][2]

# pareti/colonne senza blocco pianta pulito -> footprint = rettangolo esatto (sono prismi)
def rect(x0,y0,x1,y1): return [[[x0,y0],[x1,y0],[x1,y1],[x0,y1]]]
foot['lavatrice']     = rect(9405,4073,10485,4762)
foot['muretti_bagni'] = rect(10543,4231,11687,4762)
foot['pli_lavanderia']= rect(8385,4100,11899,4200)

# altezze (mm); per divano e parete_letto uso l'altezza reale STL (prisma a footprint reale)
HEIGHTS={k:H(k) for k in ['divano','libreria','plo_ingresso','parete_letto','parete_divisoria',
                          'lavatrice','muretti_bagni','pli_lavanderia']}

def clean_ring(r, tol=2.0):
    out=[]
    for p in r:
        if not out or abs(p[0]-out[-1][0])>tol or abs(p[1]-out[-1][1])>tol:
            out.append([float(p[0]),float(p[1])])
    if len(out)>1 and abs(out[0][0]-out[-1][0])<=tol and abs(out[0][1]-out[-1][1])<=tol:
        out.pop()
    return out

def solid_from_rings(rings, h):
    sol=None
    for r in rings:
        r=clean_ring(r)
        if len(r)<3: continue
        w=cq.Workplane('XY').polyline([(x,y) for x,y in r]).close().extrude(h)
        sol=w if sol is None else sol.union(w)
    return sol

from shapely.geometry import Polygon as SPoly, box as sbox
from shapely.ops import unary_union as sunion
def divano_articolato(rings):
    # seduta (pavimento..850) su tutto il footprint + pensile (1500..2078) sulla fascia a parete (Y basso)
    polys=[SPoly(clean_ring(r)) for r in rings if len(clean_ring(r))>=3]
    u=sunion(polys)
    ymin=u.bounds[1]
    pens=u.intersection(sbox(u.bounds[0]-1, ymin-1, u.bounds[2]+1, ymin+420))
    def rings_of(g):
        gs=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
        return [[[x,y] for x,y in gg.exterior.coords[:-1]] for gg in gs if gg.area>1000]
    seat=solid_from_rings(rings_of(u),850)
    pen =solid_from_rings(rings_of(pens),578)   # 1500..2078
    if pen is not None: pen=pen.translate((0,0,1500))
    return seat.union(pen) if pen is not None else seat

mobili={}          # per il viewer: piece -> [ {l,v,f} ] in coord trailer
comp=[]            # solidi per l'assieme STEP
for piece,rings in foot.items():
    if piece not in HEIGHTS: continue
    h=HEIGHTS[piece]
    s=divano_articolato(rings) if piece=='divano' else solid_from_rings(rings,h)
    if s is None: continue
    s=s.translate((0,0,PAV))                      # appoggia a pavimento
    shp=s.val()
    comp.append((piece,shp))
    # tessella per il viewer
    verts,tris=shp.tessellate(4.0)
    V=[[round(v.x,1),round(v.y,1),round(v.z,1)] for v in verts]
    F=[[int(a),int(b),int(c)] for a,b,c in tris]
    mobili[piece]=[{"l":"STEP_"+piece,"v":V,"f":F}]
    print(f'{piece:18s} h={h:.0f} rings={len(rings)} tess V={len(V)} F={len(F)}')

# esporta assieme STEP
asm=cq.Assembly()
for name,shp in comp: asm.add(cq.Workplane(obj=[cq.Solid(shp.wrapped)]), name=name)
exporters.export(asm.toCompound(), str(BASE/'arredo_solidi.step'))
import os
print('STEP', os.path.getsize(BASE/'arredo_solidi.step')//1024,'KB  pezzi',len(comp))
json.dump(mobili,open(BASE/'mobili_step.json','w'),separators=(',',':'))
print('mobili_step.json', os.path.getsize(BASE/'mobili_step.json')//1024,'KB')
