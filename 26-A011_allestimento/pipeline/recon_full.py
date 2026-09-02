#!/usr/bin/env python3
# Completa l'arredo: costruisce i mobili mancanti (armadi, bagni, lavabo bagni, parete master,
# tavolo, letto) dai footprint reali e li unisce alla geometria esistente.
import json, pathlib, numpy as np, cadquery as cq, traceback
BASE=pathlib.Path(__file__).parent
PAV=1395.0
FA=json.load(open(BASE/'footprints_all.json')); foot=FA['foot']; meta=FA['meta']
G=json.load(open(BASE/'arredo_geometry_solidi.json'))

def clean(r,tol=2.0):
    o=[]
    for p in r:
        if not o or abs(p[0]-o[-1][0])>tol or abs(p[1]-o[-1][1])>tol: o.append([float(p[0]),float(p[1])])
    if len(o)>1 and abs(o[0][0]-o[-1][0])<=tol and abs(o[0][1]-o[-1][1])<=tol: o.pop()
    return o
def extrude(rings,z0,z1):
    s=None
    for r in rings:
        r=clean(r)
        if len(r)<3: continue
        try: w=cq.Workplane('XY',origin=(0,0,z0)).polyline([(x,y) for x,y in r]).close().extrude(z1-z0)
        except Exception: continue
        s=w if s is None else s.union(w)
    return s
def dims(r):
    xs=[p[0] for p in r]; ys=[p[1] for p in r]
    return max(xs)-min(xs), max(ys)-min(ys)

new={}   # key -> list of cq solids (world coords)
def add(key,sol):
    if sol is not None: new.setdefault(key,[]).append(sol)

for key,typ in meta.items():
    try:
        rings=foot[key]
        if typ=='cabinet':
            H={'armadio_master':2200,'armadio_doppia':2200,'libreria':2080,
               'lavabo_bagno_ant':850,'lavabo_bagno_post':850}.get(key,2000)
            add(key,extrude(rings,PAV,PAV+H))
        elif typ=='wall':
            H={'plo_ingresso':2100}.get(key,2298)
            add(key,extrude(rings,PAV,PAV+H))
        elif typ=='bed':
            add(key,extrude(rings,PAV,PAV+650))          # piano letto basso
        elif typ=='table':
            add(key,extrude(rings,PAV+710,PAV+750))      # piano tavolo
            # gambe agli angoli
        elif typ=='bench':
            pass  # divano gia' presente
        elif typ=='room':
            for r in rings:
                w,h=dims(r); mn=min(w,h)
                if mn<250:                     # muretto/parete
                    add(key,extrude([r],PAV,PAV+2100))
                elif w*h<400000:               # sanitario/fixture basso
                    add(key,extrude([r],PAV,PAV+450))
                # else: area pavimento -> skip
        print(f'{key:20s} [{typ}] ok, solidi {len(new.get(key,[]))}')
    except Exception as ex:
        print('ERR',key,ex); traceback.print_exc()

# tessella e unisci (sostituisce parete_letto col letto basso; aggiunge i nuovi)
COL={'armadio_master':'#a8825a','armadio_doppia':'#a8825a','lavabo_bagno_ant':'#c58fa3',
     'bagno_ant':'#9fb8c0','bagno_post':'#9fb8c0','parete_div_master':'#c05f86',
     'tavolo':'#7d7f86','parete_letto':'#c7a34e','libreria':'#3f7fae'}
for key,sols in new.items():
    meshes=[]
    for s in sols:
        try:
            v,t=s.val().tessellate(0.5)
            meshes.append({'l':'R_'+key,'v':[[round(a.x,1),round(a.y,1),round(a.z,1)] for a in v],'f':[[int(i) for i in f] for f in t]})
        except Exception as ex: print('ERR tess',key,ex)
    if meshes: G['mobili'][key]=meshes
# rimuovi tavolo dagli ingombri (ora e' solido)
G['ingombri'].pop('tavolo_sedie',None)
G['ingombri'].pop('armadio_cam_doppia',None)
json.dump(G,open(BASE/'arredo_geometry_solidi.json','w'),separators=(',',':'))
import os
print('=== geometria completa ===','mobili',len(G['mobili']),'file',os.path.getsize(BASE/'arredo_geometry_solidi.json')//1024,'KB')
for k in sorted(G['mobili']): print('  ',k)
