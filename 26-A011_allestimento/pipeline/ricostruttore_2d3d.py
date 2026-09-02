#!/usr/bin/env python3
# Ricostruttore 2D->3D (v1) applicato alla CUCINA: da ogni prospetto_fronte legge W, H e i fronti
# (ante/cassetti/vetri per layer) e costruisce carcassa + fronti come solidi. Profondita' per tipo.
import ezdxf, json, pathlib, numpy as np, cadquery as cq
BASE=pathlib.Path(__file__).parent
d=ezdxf.readfile('progetto.dxf'); msp=d.modelspace()

def rects_by_layer(blockname):
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

def classify(layer):
    l=layer.lower()
    if 'cassett' in l: return 'cassetto'
    if 'vetro' in l: return 'vetro'
    if 'opaco' in l or 'anta' in l: return 'anta'
    if 'maniglia' in l or 'ferrament' in l: return 'maniglia'
    return 'carcassa'

# moduli cucina in ordine, col prospetto e il tipo (profondita', z-base)
MODS=[
 ('frigo','COLONNA frigo_chiusa_prospetto_fronte_rev.02','colonna'),
 ('forni','COLONNA forni_chiusa_prospetto_fronte_rev.02','colonna'),
 ('lavello','BASE LAVELLO_chiuso_prospetto_fronte','base'),
 ('lavastoviglie','BASE LAVASTOVIGLIE_chiusa_prospetto_fronte','base'),
 ('cassettiera','BASE CAS.ra_L.554_chiusa_prospetto_fronte','base'),
 ('cottura','BASE PIANO COTTURA_L.600_chiuso_prospetto_fronte','base'),
 ('dispensa','COLONNA dispensa_chiusa_prospetto_fronte_rev.02','colonna'),
 ('pensile','PENSILE CUCINA_chiuso_prospetto fronte','pensile'),
]
DEPTH={'colonna':580,'base':600,'pensile':350}
matcol={'anta':'#8a5a3c','cassetto':'#a06a45','vetro':'#9fc3cf','carcassa':'#cdbb95','maniglia':'#444'}

def box(x0,x1,y0,y1,z0,z1): return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))

def build_module(rects, depth):
    xs0=min(r[1] for r in rects); ys0=min(r[2] for r in rects)
    W=max(r[3] for r in rects)-xs0; H=max(r[4] for r in rects)-ys0
    parts=[]  # (kind, cqsolid) in local coords X=larghezza Y=profondita Z=altezza
    D=depth
    # carcassa: fianchi 18 + base + cielo + schienale
    parts.append(('carcassa',box(0,18,0,D,0,H)))
    parts.append(('carcassa',box(W-18,W,0,D,0,H)))
    parts.append(('carcassa',box(18,W-18,0,D,0,18)))
    parts.append(('carcassa',box(18,W-18,0,D,H-18,H)))
    parts.append(('carcassa',box(18,W-18,D-10,D,18,H-18)))
    # fronti (ante/cassetti/vetri): rettangoli grandi sui layer relativi, sul fronte (Y 0)
    for lay,x0,y0,x1,y1 in rects:
        k=classify(lay);
        if k in ('carcassa','maniglia'): continue
        w=x1-x0; h=y1-y0
        if w*h < 30000: continue      # scarta bordi/strisce sottili
        lx=x0-xs0; lz=y0-ys0
        parts.append((k,box(lx+2,lx+w-2,-18,0,lz+2,lz+h-2)))
    return W,H,D,parts

# posiziona in fila; base a Z0, pensile sopra (Z 1350), colonna intera
PAV=1395.0; CUC_Y=4179.0
placed=[]; x_cursor=4416.0; report=[]
# ordine in fila: colonne+basi in sequenza; pensile sopra le basi
row=[m for m in MODS if m[0]!='pensile']
for key,blk,typ in row:
    R=rects_by_layer(blk)
    if not R: report.append((key,'NO BLOCK')); continue
    W,H,D,parts=build_module(R,DEPTH[typ])
    z0=PAV
    for k,p in parts:
        placed.append((key,k,p.translate((x_cursor, CUC_Y, z0))))
    nf=sum(1 for k,_ in parts if k in ('anta','cassetto','vetro'))
    report.append((key,f'W{W:.0f} H{H:.0f} D{D:.0f} fronti={nf}'))
    x_cursor+=W
# pensile sopra le basi (indicativo)
Rp=rects_by_layer('PENSILE CUCINA_chiuso_prospetto fronte')
if Rp:
    W,H,D,parts=build_module(Rp,DEPTH['pensile'])
    for k,p in parts: placed.append(('pensile',k,p.translate((5636, CUC_Y, PAV+1350))))
    report.append(('pensile',f'W{W:.0f} H{H:.0f} D{D:.0f}'))

print('=== moduli ricostruiti ===');
for k,v in report: print(f'  {k:14s} {v}')
tot_x0=min(min(pp.val().BoundingBox().xmin for _,_,pp in placed),4416)
tot_x1=max(pp.val().BoundingBox().xmax for _,_,pp in placed)
print(f'cucina ricostruita X[{tot_x0:.0f},{tot_x1:.0f}]  (nota cucina di collaudo X[4416,8298])')

# tessella per il viewer
mob=[]
for key,k,p in placed:
    v,t=p.val().tessellate(0.4)
    mob.append({'l':'CUC_'+k,'v':[[round(a.x,1),round(a.y,1),round(a.z,1)] for a in v],'f':[[int(i) for i in f] for f in t]})
json.dump(mob,open(BASE/'cucina_recon.json','w'),separators=(',',':'))
print('cucina_recon.json solidi',len(mob))

# render axo
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
fig=plt.figure(figsize=(14,5)); ax=fig.add_subplot(111,projection='3d')
for key,k,p in placed:
    v,t=p.val().tessellate(0.4); vv=np.array([[a.x,a.y,a.z] for a in v])
    ax.add_collection3d(Poly3DCollection([[vv[i] for i in f] for f in t],facecolor=matcol.get(k,'#bbb'),edgecolor='#333',linewidths=.1,alpha=.97))
ax.set_xlim(4300,8400); ax.set_ylim(4000,4900); ax.set_zlim(1395,3500); ax.set_box_aspect((4100,900,2100))
ax.view_init(elev=16,azim=-70); ax.set_axis_off()
plt.tight_layout(); plt.savefig('cucina_recon.png',dpi=100,bbox_inches='tight'); print('saved cucina_recon.png')
