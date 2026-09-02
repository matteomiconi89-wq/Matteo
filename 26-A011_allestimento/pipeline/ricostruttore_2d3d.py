#!/usr/bin/env python3
# RICOSTRUTTORE MASTER 2D->3D: tutti i mobili come solidi reali.
#  - cabinet (cucina/divano/armadio/lavabo bagno/mobile letto): carcassa+fronti dai prospetti_fronte
#  - pareti/pannelli: estrusione del footprint reale della pianta
#  - mobile ingresso + lavabo lavanderia: restano a livello pannello (gia' precisi)
import ezdxf, json, pathlib, numpy as np, cadquery as cq, traceback
BASE=pathlib.Path(__file__).parent
PAV=1395.0
d=ezdxf.readfile('progetto.dxf'); msp=d.modelspace()
foot=json.load(open(BASE/'footprints.json'))
G3=json.load(open(BASE/'arredo_geometry3.json'))   # per mobile_ingresso, lavabo, ingombri, aperto
COA=json.load(open(BASE/'stl_b64'/'coarse.json'))

def box(x0,x1,y0,y1,z0,z1): return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))
def classify(layer):
    l=layer.lower()
    if 'cassett' in l: return 'cassetto'
    if 'vetro' in l: return 'vetro'
    if 'opaco' in l or 'anta' in l: return 'anta'
    if 'maniglia' in l or 'ferrament' in l: return 'skip'
    return 'carcassa'
def rects(blockname):
    for e in msp:
        if e.dxftype()=='INSERT' and e.dxf.name==blockname:
            R=[]
            for v in e.virtual_entities():
                if v.dxftype()=='LWPOLYLINE' and v.closed:
                    pts=[(p[0],p[1]) for p in v.get_points('xy')]
                    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
                    R.append((v.dxf.layer,min(xs),min(ys),max(xs),max(ys)))
            return R
    return None

def cabinet(block, depth):
    """carcassa 18mm + fronti (ante/cassetti/vetri) dal prospetto. local X=larghezza Y=prof Z=altezza."""
    R=rects(block)
    if not R: return None
    xs0=min(r[1] for r in R); ys0=min(r[2] for r in R)
    W=max(r[3] for r in R)-xs0; H=max(r[4] for r in R)-ys0
    if W<50 or H<50: return None
    D=depth; parts=[]
    parts+=[('carcassa',box(0,18,0,D,0,H)),('carcassa',box(W-18,W,0,D,0,H)),
            ('carcassa',box(18,W-18,0,D,0,18)),('carcassa',box(18,W-18,0,D,H-18,H)),
            ('carcassa',box(18,W-18,D-10,D,18,H-18))]
    for lay,x0,y0,x1,y1 in R:
        k=classify(lay)
        if k in ('carcassa','skip'): continue
        w=x1-x0; h=y1-y0
        if w*h<25000: continue
        lx=x0-xs0; lz=y0-ys0
        parts.append((k,box(lx+2,lx+w-2,-18,0,lz+2,lz+h-2)))
    return W,H,D,parts

def extrude_foot(rings,h):
    def clean(r):
        o=[]
        for p in r:
            if not o or abs(p[0]-o[-1][0])>2 or abs(p[1]-o[-1][1])>2: o.append([float(p[0]),float(p[1])])
        if len(o)>1 and abs(o[0][0]-o[-1][0])<=2 and abs(o[0][1]-o[-1][1])<=2: o.pop()
        return o
    s=None
    for r in rings:
        r=clean(r)
        if len(r)<3: continue
        w=cq.Workplane('XY').polyline([(x,y) for x,y in r]).close().extrude(h)
        s=w if s is None else s.union(w)
    return s

placed=[]  # (key, kind, cqsolid_world)
def emit(key, parts_local, place):
    for k,p in parts_local:
        placed.append((key,k,place(p)))

# ---------- CUCINA (multi-modulo) ----------
CUC=[('frigo','COLONNA frigo_chiusa_prospetto_fronte_rev.02',580,'colonna'),
 ('forni','COLONNA forni_chiusa_prospetto_fronte_rev.02',580,'colonna'),
 ('lavello','BASE LAVELLO_chiuso_prospetto_fronte',600,'base'),
 ('lavastoviglie','BASE LAVASTOVIGLIE_chiusa_prospetto_fronte',600,'base'),
 ('cassettiera','BASE CAS.ra_L.554_chiusa_prospetto_fronte',600,'base'),
 ('cottura','BASE PIANO COTTURA_L.600_chiuso_prospetto_fronte',600,'base'),
 ('dispensa','COLONNA dispensa_chiusa_prospetto_fronte_rev.02',580,'colonna')]
xc=4416.0; CUCY=4179.0; base_x0=None; base_x1=None
for key,blk,dep,typ in CUC:
    try:
        r=cabinet(blk,dep)
        if not r: print('cucina skip',key); continue
        W,H,D,parts=r
        emit('cucina',parts,lambda p,xc=xc: p.translate((xc,CUCY,PAV)))
        if typ=='base':
            base_x0=xc if base_x0 is None else base_x0; base_x1=xc+W
        xc+=W
    except Exception as ex: print('ERR cucina',key,ex)
# piano di lavoro continuo sopra le basi + pensile
if base_x0:
    placed.append(('cucina','top',box(base_x0,base_x1,CUCY,CUCY+600,PAV+820,PAV+860)))
    rp=cabinet('PENSILE CUCINA_chiuso_prospetto fronte',350)
    if rp:
        W,H,D,parts=rp
        emit('cucina',parts,lambda p: p.translate((base_x0,CUCY,PAV+1360)))

# ---------- CABINET dai prospetti ----------
CAB=[
 ('armadio','ARMADIO_camera doppia_prospetto_fronte_chiuso',600,(11382,61),False),
 ('mobile_lavabo_bagno','MOBILE LAVABO_bagno_camera doppia_prospetto_fronte',520,(10543,4242),True),
 ('mobile_letto','MOBILE LETTO_rev.01_prospetto_fronte',600,(600,1224),False),
]
for key,blk,dep,(X0,Y0),cucside in CAB:
    try:
        r=cabinet(blk,dep)
        if not r: print('cab skip',key); continue
        W,H,D,parts=r
        if cucside:  # fronte verso corridoio (Y basso): specchia in Y
            emit(key,parts,lambda p,Y0=Y0,D=D: p.mirror('XZ').translate((X0,Y0+D,PAV)))
        else:
            emit(key,parts,lambda p,X0=X0,Y0=Y0: p.translate((X0,Y0,PAV)))
        print(f'{key:20s} W{W:.0f} H{H:.0f} D{D:.0f}')
    except Exception as ex: print('ERR cab',key,ex); traceback.print_exc()

# ---------- DIVANO (seduta + pensile) ----------
try:
    r=cabinet('PANCA_DIVANO_LINEARE_rev.01_prospetto_chiuso',1195)
    # divano: uso il footprint reale per seduta bassa (0..820) + pensile a parete
    from shapely.geometry import Polygon as SP, box as sbox
    from shapely.ops import unary_union as su
    polys=[SP([(x,y) for x,y in ring]) for ring in foot['divano']]
    u=su(polys); ymin=u.bounds[1]
    def rings_of(g):
        gs=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
        return [[[x,y] for x,y in gg.exterior.coords[:-1]] for gg in gs if gg.area>1000]
    seat=extrude_foot(rings_of(u),820)
    placed.append(('divano','carcassa',seat.translate((0,0,PAV))))
    pens=u.intersection(sbox(u.bounds[0]-1,ymin-1,u.bounds[2]+1,ymin+380))
    pp=extrude_foot(rings_of(pens),560)
    if pp: placed.append(('divano','anta',pp.translate((0,0,PAV+1480))))
    print('divano ok (seduta+pensile)')
except Exception as ex: print('ERR divano',ex)

# ---------- PARETI / PANNELLI (estrusione footprint) ----------
def Hof(p): o=COA[p]; return o['wmax'][2]-o['wmin'][2]
def rect_rings(x0,y0,x1,y1): return [[[x0,y0],[x1,y0],[x1,y1],[x0,y1]]]
WALLS={
 'libreria':(foot['libreria'],Hof('libreria')),
 'plo_ingresso':(foot['plo_ingresso'],Hof('plo_ingresso')),
 'parete_letto':(foot['parete_letto'],Hof('parete_letto')),
 'parete_divisoria':(foot['parete_divisoria'],Hof('parete_divisoria')),
 'lavatrice':(rect_rings(9405,4073,10485,4762),Hof('lavatrice')),
 'muretti_bagni':(rect_rings(10543,4231,11687,4762),Hof('muretti_bagni')),
 'pli_lavanderia':(rect_rings(8385,4100,11899,4200),Hof('pli_lavanderia')),
}
for key,(rings,h) in WALLS.items():
    try:
        s=extrude_foot(rings,h)
        if s: placed.append((key,'carcassa',s.translate((0,0,PAV))))
        print(f'{key:20s} H{h:.0f} (parete/estrusione)')
    except Exception as ex: print('ERR wall',key,ex)

# ---------- tessella tutto ----------
mobili={}
for key,kind,solid in placed:
    try:
        v,t=solid.val().tessellate(0.5)
        mobili.setdefault(key,[]).append({'l':'R_'+kind,'v':[[round(a.x,1),round(a.y,1),round(a.z,1)] for a in v],'f':[[int(i) for i in f] for f in t]})
    except Exception as ex: print('ERR tess',key,ex)

# keep detailed pieces + shell + ingombri
out={'shell_step':G3.get('shell_step',[]),'aperto':G3['aperto'],'mobili':mobili,'ingombri':{}}
for k in ('mobile_ingresso','lavabo_lavanderia'):
    if k in G3['mobili']: out['mobili'][k]=G3['mobili'][k]
for k in ('tavolo_sedie','armadio_cam_doppia'):
    if k in G3['ingombri']: out['ingombri'][k]=G3['ingombri'][k]
json.dump(out,open(BASE/'arredo_geometry_all.json','w'),separators=(',',':'))
import os
# esporta STEP (assieme solidi ricostruiti)
try:
    comp=cq.Compound.makeCompound([s.val() for _,_,s in placed])
    cq.exporters.export(comp, str(BASE/'arredo_all.step'))
    print('STEP arredo_all.step', os.path.getsize(BASE/'arredo_all.step')//1024,'KB')
except Exception as ex: print('ERR step', ex)
print('=== TOTALE ===','pezzi',len(mobili),'file',os.path.getsize(BASE/'arredo_geometry_all.json')//1024,'KB')
for k,v in mobili.items():
    xs=[c[0] for m in v for c in m['v']]; zs=[c[2] for m in v for c in m['v']]
    print(f'  {k:20s} solidi {len(v):3d}  X[{min(xs):.0f},{max(xs):.0f}] Ztop {max(zs):.0f}')
