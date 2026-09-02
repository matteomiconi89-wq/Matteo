#!/usr/bin/env python3
# Ricostruisce gli armadi dai PANNELLI della pianta (fianchi/ante/schienali estrusi a tutta altezza),
# invece che come scatola. + letto contenitore che esce dall'armadio camera doppia.
import ezdxf, json, pathlib, cadquery as cq
BASE=pathlib.Path(__file__).parent
PAV=1395.0; H=2200.0
d=ezdxf.readfile('pianta.dxf'); msp=d.modelspace(); TX,TY=2293,3117
G=json.load(open(BASE/'arredo_geometry_solidi.json'))

def box(x0,x1,y0,y1,z0,z1): return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))

def panels(blockname):
    for e in msp:
        if e.dxftype()=='INSERT' and e.dxf.name==blockname:
            out=[]
            for v in e.virtual_entities():
                if v.dxftype()=='LWPOLYLINE' and v.closed and 'led' not in v.dxf.layer.lower():
                    pts=[(p[0]-TX,p[1]-TY) for p in v.get_points('xy')]
                    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
                    w=max(xs)-min(xs); h=max(ys)-min(ys)
                    if min(w,h)<70 and max(w,h)>60 and w*h>600:      # pannello sottile (fianco/anta/schienale)
                        out.append((min(xs),min(ys),max(xs),max(ys),v.dxf.layer))
            return out
    return []

ARM={'armadio_master':'ARMADIO_camera master_sol.C_pianta','armadio_doppia':'ARMADIO_camera doppia_pianta'}
new={}
def tess(sol,lab):
    v,t=sol.val().tessellate(0.5)
    return {'l':lab,'v':[[round(a.x,1),round(a.y,1),round(a.z,1)] for a in v],'f':[[int(i) for i in f] for f in t]}
for key,blk in ARM.items():
    ps=panels(blk)
    meshes=[]
    # limita i pannelli (dedup vicini) e costruisci
    seen=set()
    for x0,y0,x1,y1,lay in ps:
        k=(round(x0/5),round(y0/5),round(x1/5),round(y1/5))
        if k in seen: continue
        seen.add(k)
        lab='ARM_anta' if 'opaco' in lay.lower() else 'ARM_str'
        try: meshes.append(tess(box(x0,x1,y0,y1,PAV,PAV+H),lab))
        except Exception: pass
    # schienale + cielo per chiudere il volume
    xs=[p[0] for p in ps]+[p[2] for p in ps]; ys=[p[1] for p in ps]+[p[3] for p in ps]
    X0,X1,Y0,Y1=min(xs),max(xs),min(ys),max(ys)
    try:
        meshes.append(tess(box(X0,X1,Y1-18,Y1,PAV,PAV+H),'ARM_str'))   # schienale
        meshes.append(tess(box(X0,X1,Y0,Y1,PAV+H-18,PAV+H),'ARM_str')) # cielo
    except Exception: pass
    new[key]=meshes
    print(f'{key:16s} pannelli usati={len(meshes)}  X[{X0:.0f},{X1:.0f}] Y[{Y0:.0f},{Y1:.0f}]')

# letto contenitore camera doppia: esce dall'armadio (Y bassa) verso il centro stanza
# armadio_doppia ~ X11382..13484 Y49..669 -> letto ribaltato davanti: Y 669..2669, largh ~1600 in X
lx0=11700
bed=[]
bed.append(tess(box(lx0,lx0+1600,669,669+2000,PAV,PAV+300),'LETTO_base'))
bed.append(tess(box(lx0,lx0+1600,669,669+2000,PAV+300,PAV+470),'LETTO_mater'))
new['letto_doppia']=bed
print('letto contenitore riposizionato (esce dall armadio doppia)')

for k,m in new.items(): G['mobili'][k]=m
json.dump(G,open(BASE/'arredo_geometry_solidi.json','w'),separators=(',',':'))
print('ok, mobili',len(G['mobili']))
