#!/usr/bin/env python3
"""RICOSTRUTTORE 2D->3D 26A011 — dal DWG di pianta (+prospetti) genera TUTTI gli STEP dei mobili,
precisi al mm, l'assieme, e la geometria per il viewer 3D.

Uso:  python3 ricostruisci.py [pianta.dxf] [progetto.dxf] [out_dir]
Default: pianta.dxf progetto.dxf  ->  ../cad/step/*.step  +  ../cad/26A011_arredo_completo.step
         + arredo_geometry_mobili.json
Dipendenze: ezdxf cadquery shapely (cascadio per il guscio STEP).
"""
import sys, os, json, math, pathlib
import ezdxf, cadquery as cq
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union
HERE = pathlib.Path(__file__).parent
PIANTA = sys.argv[1] if len(sys.argv)>1 else str(HERE/'pianta.dxf')
PROG   = sys.argv[2] if len(sys.argv)>2 else str(HERE/'progetto.dxf')
OUT    = pathlib.Path(sys.argv[3]) if len(sys.argv)>3 else (HERE.parent/'cad')
STEPDIR= OUT/'step'; STEPDIR.mkdir(parents=True, exist_ok=True)
PAV=1395.0; TX,TY=2293,3117

dp = ezdxf.readfile(PIANTA); msp = dp.modelspace()
dr = ezdxf.readfile(PROG) if os.path.exists(PROG) else None
mspr = dr.modelspace() if dr else None

# ---------- helpers ----------
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))
def clean(r,tol=2.0):
    o=[]
    for p in r:
        if not o or abs(p[0]-o[-1][0])>tol or abs(p[1]-o[-1][1])>tol: o.append((float(p[0]),float(p[1])))
    if len(o)>1 and abs(o[0][0]-o[-1][0])<=tol and abs(o[0][1]-o[-1][1])<=tol: o.pop()
    return o
def extrude(rings,z0,z1):
    s=None
    for r in rings:
        r=clean(r)
        if len(r)<3: continue
        try: w=cq.Workplane('XY',origin=(0,0,z0)).polyline(r).close().extrude(z1-z0)
        except Exception: continue
        s=w if s is None else s.union(w)
    return s
TRUCK=(-800,14000,-900,5600)   # envelope del cassone in coord trailer (mm)
def _centroid_in_truck(e):
    xs=[];ys=[]
    for v in e.virtual_entities():
        if v.dxftype()=='LWPOLYLINE' and v.closed:
            for p in v.get_points('xy'): xs.append(p[0]-TX); ys.append(p[1]-TY)
    if not xs: return False
    cx=sum(xs)/len(xs); cy=sum(ys)/len(ys)
    return TRUCK[0]<cx<TRUCK[1] and TRUCK[2]<cy<TRUCK[3]
def insert(msp_,name):
    """Ritorna l'istanza del blocco DENTRO il cassone (scarta le copie di dettaglio disegnate a lato)."""
    cands=[e for e in msp_ if e.dxftype()=='INSERT' and e.dxf.name==name]
    if not cands: return None
    if len(cands)==1: return cands[0]
    for e in cands:
        if _centroid_in_truck(e): return e
    return cands[0]
def closed_polys(ins,to_trailer=True):
    out=[]
    for v in ins.virtual_entities():
        if v.dxftype()=='LWPOLYLINE' and v.closed:
            off=(TX,TY) if to_trailer else (0,0)
            pts=[(p[0]-off[0],p[1]-off[1]) for p in v.get_points('xy')]
            if len(pts)>=3: out.append((v.dxf.layer,pts))
    return out
def footprint(name):
    ins=insert(msp,name)
    if not ins: return None
    polys=[]
    for lay,pts in closed_polys(ins):
        try:
            pg=Polygon(pts)
            if pg.area>1500: polys.append(pg if pg.is_valid else pg.buffer(0))
        except Exception: pass
    if not polys: return None
    u=unary_union(polys); cx,cy=u.centroid.x,u.centroid.y
    if not(-800<cx<14000 and -900<cy<5600): return None
    gs=list(u.geoms) if u.geom_type=='MultiPolygon' else [u]
    return [[[round(x,1),round(y,1)] for x,y in g.simplify(3).exterior.coords[:-1]] for g in gs if g.area>1500]

def classify(layer):
    l=layer.lower()
    if 'cassett' in l: return 'cassetto'
    if 'vetro' in l: return 'vetro'
    if 'opaco' in l or 'anta' in l: return 'anta'
    if 'maniglia' in l or 'ferrament' in l or 'led' in l: return 'skip'
    return 'carcassa'

def cabinet(prosp_block, depth):
    """carcassa 18mm + fronti dal prospetto_fronte (coord locali)."""
    if not mspr: return None
    ins=insert(mspr,prosp_block)
    if not ins: return None
    R=[]
    for lay,pts in closed_polys(ins,to_trailer=False):
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]; R.append((lay,min(xs),min(ys),max(xs),max(ys)))
    if not R: return None
    xs0=min(r[1] for r in R); ys0=min(r[2] for r in R)
    W=max(r[3] for r in R)-xs0; H=max(r[4] for r in R)-ys0
    if W<50 or H<50: return None
    D=depth; parts=[('carcassa',box(0,18,0,D,0,H)),('carcassa',box(W-18,W,0,D,0,H)),
        ('carcassa',box(18,W-18,0,D,0,18)),('carcassa',box(18,W-18,0,D,H-18,H)),
        ('carcassa',box(18,W-18,D-10,D,18,H-18))]
    for lay,x0,y0,x1,y1 in R:
        k=classify(lay)
        if k in ('carcassa','skip'): continue
        w=x1-x0; h=y1-y0
        if w*h<25000: continue
        parts.append((k,box(x0-xs0+2,x0-xs0+w-2,-18,0,y0-ys0+2,y0-ys0+h-2)))
    sol=None
    for _,p in parts: sol=p if sol is None else sol.union(p)
    return W,H,D,sol

def panels_solid(pianta_block,H):
    """armadio: fianchi/ante/schienali dai pannelli sottili della pianta, estrusi a tutta altezza."""
    ins=insert(msp,pianta_block)
    if not ins: return None
    rects=[]
    for lay,pts in closed_polys(ins):
        if 'led' in lay.lower(): continue
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]; w=max(xs)-min(xs); h=max(ys)-min(ys)
        if min(w,h)<70 and max(w,h)>60 and w*h>600: rects.append((min(xs),min(ys),max(xs),max(ys)))
    if not rects: return None
    seen=set(); sol=None
    for x0,y0,x1,y1 in rects:
        k=(round(x0/5),round(y0/5),round(x1/5),round(y1/5))
        if k in seen: continue
        seen.add(k)
        b=box(x0,x1,y0,y1,PAV,PAV+H); sol=b if sol is None else sol.union(b)
    xs=[r[0] for r in rects]+[r[2] for r in rects]; ys=[r[1] for r in rects]+[r[3] for r in rects]
    X0,X1,Y0,Y1=min(xs),max(xs),min(ys),max(ys)
    sol=sol.union(box(X0,X1,Y1-18,Y1,PAV,PAV+H)).union(box(X0,X1,Y0,Y1,PAV+H-18,PAV+H))
    return sol

def vanity(blockname,z_body=820,z_top=870):
    """mobile lavabo: corpo (ante/carcassa) fino al piano + top corian con lavabo."""
    ins=insert(msp,blockname)
    if not ins: return None
    body=[]; top=[]
    for lay,pts in closed_polys(ins):
        try: pg=Polygon(pts)
        except Exception: continue
        if not pg.is_valid or pg.area<3000: continue
        l=lay.lower()
        if 'corian' in l or 'betacryl' in l or 'lavabo' in l: top.append(pts)
        elif 'opaco' in l or 'cera' in l or 'bianco' in l or 'lsb' in l: body.append(pts)
    sol=extrude(body,PAV,PAV+z_body)
    t=extrude(top,PAV+z_body,PAV+z_top)
    if sol is None: sol=t
    elif t is not None: sol=sol.union(t)
    return sol

def bed(blockname):
    """letto: base contenitore (footprint) + materasso (rettangolo piu' grande) + testata (pannello opaco piu' alto)."""
    ins=insert(msp,blockname)
    if not ins: return None
    rings=[]; opaco=[]; biggest=None; ba=0
    for lay,pts in closed_polys(ins):
        try: pg=Polygon(pts)
        except Exception: continue
        if not pg.is_valid or pg.area<3000: continue
        rings.append(pts)
        if 'opaco' in lay.lower(): opaco.append(pts)
        if 1.8e6<pg.area<4.2e6 and pg.area>ba: ba=pg.area; biggest=pts   # materasso ~2000x1600
    base=extrude(rings,PAV,PAV+300)                       # zoccolo contenitore su tutto l'ingombro
    if base is None: return None
    sol=base
    if biggest is not None:
        m=extrude([biggest],PAV+300,PAV+520)              # materasso
        if m is not None: sol=sol.union(m)
    if opaco:
        h=extrude(opaco,PAV,PAV+1000)                     # testata
        if h is not None: sol=sol.union(h)
    return sol

def tall_unit(blockname,H):
    """mobile a tutta altezza (ingresso): footprint carcassa+ante estruso."""
    ins=insert(msp,blockname)
    if not ins: return None
    rings=[]
    for lay,pts in closed_polys(ins):
        try: pg=Polygon(pts)
        except Exception: continue
        l=lay.lower()
        if pg.is_valid and pg.area>4000 and 'led' not in l and 'vetro' not in l:
            rings.append(pts)
    return extrude(rings,PAV,PAV+H)

# ---------- costruzione pezzi ----------
solids={}   # key -> cq solid (compound), coord trailer mm
def put(k,s):
    if s is not None: solids[k]=s.val() if hasattr(s,'val') else s

# 1) CUCINA (7 moduli) da prospetti_fronte
CUC=[('COLONNA frigo_chiusa_prospetto_fronte_rev.02',580,'col'),('COLONNA forni_chiusa_prospetto_fronte_rev.02',580,'col'),
 ('BASE LAVELLO_chiuso_prospetto_fronte',600,'base'),('BASE LAVASTOVIGLIE_chiusa_prospetto_fronte',600,'base'),
 ('BASE CAS.ra_L.554_chiusa_prospetto_fronte',600,'base'),('BASE PIANO COTTURA_L.600_chiuso_prospetto_fronte',600,'base'),
 ('COLONNA dispensa_chiusa_prospetto_fronte_rev.02',580,'col')]
xc=4416.0; CY=4179.0; cuc=None; bx0=None;bx1=None
for blk,dep,typ in CUC:
    r=cabinet(blk,dep)
    if not r: continue
    W,H,D,s=r; s=s.translate((xc,CY,PAV))
    cuc=s if cuc is None else cuc.union(s)
    if typ=='base': bx0=xc if bx0 is None else bx0; bx1=xc+W
    xc+=W
if cuc is not None and bx0:
    cuc=cuc.union(box(bx0,bx1,CY,CY+600,PAV+820,PAV+860))   # piano di lavoro
    rp=cabinet('PENSILE CUCINA_chiuso_prospetto fronte',350)
    if rp: cuc=cuc.union(rp[3].translate((bx0,CY,PAV+1360)))
if cuc is None:
    # progetto.dxf (prospetti) assente: riusa la cucina gia' generata cosi' la pipeline resta completa
    cached=OUT/'step'/'cucina.step'
    if cached.exists():
        from cadquery import importers
        cuc=importers.importStep(str(cached)); print('cucina: riuso', cached.name, '(progetto.dxf assente)')
put('cucina',cuc)

# 2) ARMADI da pannelli pianta
put('armadio_master', panels_solid('ARMADIO_camera master_sol.C_pianta',2200))
put('armadio_doppia', panels_solid('ARMADIO_camera doppia_pianta',2200))

# 3) PARETI / PANNELLI da footprint
WALLS={'plo_ingresso':('P.lo PARETE INGRESSO_pianta',2100),
 'parete_divisoria':('F_PARETE DIVISORIA_living-camera doppia_pianta',2298),
 'parete_div_master':('F_PARETE DIVISORIA_living-camera master_pianta',2298),
 'libreria':('LIBRERIA-PARETE_ufficio_rev.01_pianta',2080)}
for k,(blk,h) in WALLS.items():
    fp=footprint(blk)
    if fp: put(k,extrude(fp,PAV,PAV+h))
for k,(x0,y0,x1,y1,h) in {'muretti_bagni':(10543,4231,11687,4762,1195),
        'pli_lavanderia':(8385,4100,11899,4200,2080)}.items():
    put(k,extrude([[[x0,y0],[x1,y0],[x1,y1],[x0,y1]]],PAV,PAV+h))
# lavanderia (colonna lavatrice+asciugatrice+mobili) e colonna dispensa 220, dai blocchi pianta
put('lavanderia', tall_unit('BAGNO-LAVANDERIA_pianta_sol.B',2076))
put('colonna_220', tall_unit('COLONNA L.220 MM_pianta',2076))

# 4) DIVANO (seduta+pensile) da footprint
fp=footprint('DIVANO_pianta')
if fp:
    u=unary_union([Polygon(r) for r in fp]); ymin=u.bounds[1]
    def rof(g):
        gs=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
        return [[[x,y] for x,y in gg.exterior.coords[:-1]] for gg in gs if gg.area>1000]
    seat=extrude(rof(u),PAV,PAV+820)
    pens=extrude(rof(u.intersection(sbox(u.bounds[0]-1,ymin-1,u.bounds[2]+1,ymin+380))),PAV+1480,PAV+2040)
    put('divano', seat.union(pens) if pens is not None else seat)

# 5) TAVOLO (piano)
fp=footprint('TAVOLO_pianta')
if fp: put('tavolo',extrude(fp,PAV+710,PAV+750))

# 6) BAGNI: muri (bbox stanza) + doccia + WC/bidet (posizioni F_SANITARI)
def walk(ins,acc):
    for e in ins.virtual_entities():
        if e.dxftype()=='INSERT': walk(e,acc)
        else: acc.append(e)
    return acc
BAGNI={'bagno_ant':('BAGNO_camera doppia_rev.01_pianta',(1000,3812,3582,4767)),
       'bagno_post':('BAGNO_camera doppia_rev.02_pianta',(10538,13488,3582,4767))}
for key,(blk,(rx0,rx1,ry0,ry1)) in BAGNI.items():
    ins=insert(msp,blk)
    if not ins: continue
    acc=walk(ins,[]); tray=None;ta=0; circ=[]
    for x in acc:
        if x.dxftype()=='LWPOLYLINE' and x.closed and 'sanitari' in x.dxf.layer.lower():
            pts=[(p[0]-TX,p[1]-TY) for p in x.get_points('xy')]; xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
            a=(max(xs)-min(xs))*(max(ys)-min(ys))
            if 700000<a<1300000 and a>ta: ta=a; tray=[min(xs),min(ys),max(xs),max(ys)]
        if x.dxftype()=='CIRCLE' and 'sanitari' in x.dxf.layer.lower() and x.dxf.radius>20:
            c=x.dxf.center; circ.append((c.x-TX,c.y-TY))
    tk=90; walls=box(rx0,rx1,ry0,ry1,PAV,PAV+2100).cut(box(rx0+tk,rx1-tk,ry0+tk,ry1-tk,PAV-10,PAV+2110))
    put(key+'_muri',walls)
    san=None
    if tray:
        x0,y0,x1,y1=tray
        for s in [box(x0,x1,y0,y1,PAV,PAV+120),box(x0,x0+40,y0,y1,PAV,PAV+1950),box(x0,x1,y1-40,y1,PAV,PAV+1950)]:
            san=s if san is None else san.union(s)
    for i,(cx,cy) in enumerate(sorted(circ)[:2]):
        b=box(cx-185,cx+185,cy-270,cy+270,PAV,PAV+400); san=b if san is None else san.union(b)
    if san is not None: put(key+'_sanitari',san)

# 7) MOBILI LAVABO bagni + MOBILE ingresso
put('mobile_lavabo_ant', vanity('MOBILE LAVABO_bagno doppia_pianta_rev.01'))
put('mobile_lavabo_post', vanity('MOBILE LAVABO_bagno doppia_pianta_rev.02'))
put('mobile_ingresso', tall_unit('MOBILE_ingresso-living_rev.01_pianta',2080))

# 8) LETTI
put('letto_master', bed('PARETE LETTO_camera master_pianta'))
lx=11700; put('letto_doppia', box(lx,lx+1600,669,669+2000,PAV,PAV+300).union(box(lx,lx+1600,669,669+2000,PAV+300,PAV+470)))

# ---------- export STEP per pezzo + assieme ----------
from cadquery import exporters
allshapes=[]
for k,s in solids.items():
    try:
        exporters.export(s, str(STEPDIR/f'{k}.step'))   # s e' una cq.Shape: export diretto scrive la geometria
        allshapes.append(s)
    except Exception as ex: print('step err',k,ex)
try:
    comp=cq.Compound.makeCompound(allshapes)
    exporters.export(comp, str(OUT/'26A011_arredo_completo.step'))
    print('assieme:', OUT/'26A011_arredo_completo.step', comp.Volume()/1e9, 'm3')
except Exception as ex: print('assembly err',ex)

# ---------- tessella per il viewer ----------
mob={}
for k,s in solids.items():
    try:
        v,t=s.tessellate(0.4)
        mob[k]=[{'l':'R_'+k,'v':[[round(a.x,1),round(a.y,1),round(a.z,1)] for a in v],'f':[[int(i) for i in f] for f in t]}]
    except Exception as ex: print('tess err',k,ex)
json.dump(mob,open(HERE/'arredo_geometry_mobili.json','w'),separators=(',',':'))
print(f'FATTO: {len(solids)} mobili -> STEP in {STEPDIR}, assieme in {OUT}, mesh viewer arredo_geometry_mobili.json')
for k in sorted(solids): print('  ',k)
