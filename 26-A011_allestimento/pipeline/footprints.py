#!/usr/bin/env python3
# Estrae il footprint reale di ogni mobile dalla PIANTA_GENERALE (unione dei sotto-rettangoli
# del simbolo di pianta), in coord. trailer. Salva footprints.json.
import ezdxf, json, pathlib
from shapely.geometry import Polygon
from shapely.ops import unary_union
BASE=pathlib.Path(__file__).parent
d=ezdxf.readfile('pianta.dxf'); msp=d.modelspace()
TX,TY=2293,3117

# blocco pianta -> (piece, expected trailer bbox per scegliere l'istanza giusta)
BLOCKS={
 'DIVANO_pianta':('divano',(4409,54,7009,1249)),
 'LIBRERIA-PARETE_ufficio_rev.01_pianta':('libreria',(9440,59,11383,1664)),
 'P.lo PARETE INGRESSO_pianta':('plo_ingresso',(7564,49,9378,130)),
 'PARETE LETTO_camera master_pianta':('parete_letto',(504,1224,2872,3539)),
 'F_PARETE DIVISORIA_living-camera doppia_pianta':('parete_divisoria',(8809,1201,11380,3587)),
}
def polys_of(insert):
    out=[]
    for e in insert.virtual_entities():
        if e.dxftype()=='LWPOLYLINE' and e.closed:
            pts=[(p[0]-TX,p[1]-TY) for p in e.get_points('xy')]
            if len(pts)>=3:
                try:
                    pg=Polygon(pts)
                    if pg.is_valid and pg.area>2000: out.append(pg)
                    elif (not pg.is_valid) and pg.buffer(0).area>2000: out.append(pg.buffer(0))
                except Exception: pass
    return out

foot={}
for e in msp:
    if e.dxftype()!='INSERT' or e.dxf.name not in BLOCKS: continue
    piece,(bx0,by0,bx1,by1)=BLOCKS[e.dxf.name]
    pl=polys_of(e)
    if not pl: continue
    u=unary_union(pl)
    # centro dell'unione deve cadere nella bbox attesa (scarta le istanze-dettaglio lontane)
    cx,cy=u.centroid.x,u.centroid.y
    if not (bx0-500<cx<bx1+500 and by0-500<cy<by1+500): continue
    # prendi i poligoni (Multi o singolo), semplifica
    geoms=list(u.geoms) if u.geom_type=='MultiPolygon' else [u]
    rings=[]
    for g in geoms:
        g=g.simplify(3.0)
        rings.append([[round(x,1),round(y,1)] for x,y in g.exterior.coords[:-1]])
    foot[piece]=rings

json.dump(foot,open(BASE/'footprints.json','w'))
for k,v in foot.items():
    allx=[p[0] for r in v for p in r]; ally=[p[1] for r in v for p in r]
    print(f'{k:18s} rings={len(v)} pts={sum(len(r) for r in v)} bbox X[{min(allx):.0f},{max(allx):.0f}] Y[{min(ally):.0f},{max(ally):.0f}]')

# plot
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
fig,ax=plt.subplots(figsize=(15,6))
cols={'divano':'#c86b45','libreria':'#3f7fae','plo_ingresso':'#9b6fb0','parete_letto':'#c7a34e','parete_divisoria':'#c05f86'}
for k,v in foot.items():
    for r in v:
        ax.add_patch(MPoly(r,closed=True,facecolor=cols.get(k,'#888'),alpha=.6,edgecolor='#222'))
    allx=[p[0] for r in v for p in r]; ally=[p[1] for r in v for p in r]
    ax.text(sum(allx)/len(allx),sum(ally)/len(ally),k,ha='center',fontsize=7)
from matplotlib.patches import Rectangle
ax.add_patch(Rectangle((0,0),13500,4840,fill=False,edgecolor='#333'))
ax.set_xlim(-300,14000); ax.set_ylim(-300,5200); ax.set_aspect('equal'); ax.invert_yaxis()
ax.set_title('Footprint reali (unione sotto-rettangoli pianta)')
plt.tight_layout(); plt.savefig('footprints_check.png',dpi=95); print('saved footprints_check.png')
