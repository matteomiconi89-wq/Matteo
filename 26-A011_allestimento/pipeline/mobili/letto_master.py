#!/usr/bin/env python3
"""LETTO camera MASTER = MOBILE CONTENITORE TESTATA LETTO + letto.

Corretto sul DWG "026_A011_MOBILE_CONTENITORE_TESTATA_LETTO_rev_01":
  prospetto fronte 2368 x 2299   (NON una testata bassa: e' un mobile a tutta altezza)
  sezione C-C'    profondita 315
  sezione letto   materasso da Z 340, spessore 200 (top a 540)

Mappatura prospetto -> trailer:  Y = 1224 + x_prospetto ,  Z = PAV + y_prospetto ,
profondita X = 558..873. Verificata sulla pianta: la colonna sinistra (203) cade sul
comodino Y1254-1444 e la destra (363) su Y3212-3562.

Pannelli letti dal prospetto:
  montanti massello  x 0(30) 220(36) 1952(36) 2338(30), h 2214
  pannello centrale  x250 y17  1709x2168
  colonna sx  x24  y17  203x2168   (vano x33 y852 184x1323, base x33 y6 184x212)
  colonna dx  x1982 y17 363x2168   (vano x1991 y852 344x1323, base x1991 y6 344x212)
  fascia alta x0 y2197 2368x94
"""
import cadquery as cq, json, pathlib
from cadquery import exporters
HERE = pathlib.Path(__file__).parent
PAV = 1395.0
Y0, XF, XB = 1224.0, 558.0, 873.0        # origine lungo Y, fronte/retro in X (prof 315)
def P(x, y, w, h, x0=XF, x1=XB):          # pannello dal prospetto -> solido nel truck
    return cq.Workplane('XY').box(x1-x0, w, h, centered=False).translate((x0, Y0+x, PAV+y))
parts = []
# montanti in massello (tutta profondita')
for x, w in ((0,30),(220,36),(1952,36),(2338,30)):
    parts.append(('MONTANTE_massello', P(x, 0, w, 2214)))
# pannello centrale (testata) sul fronte
parts.append(('PANNELLO_TESTATA', P(250, 17, 1709, 2168, XB-18, XB)))
# colonne laterali: fianchi + ripiano vano + base
for tag, cx, cw, vx, vw in (('COLONNA_SX', 24, 203, 33, 184), ('COLONNA_DX', 1982, 363, 1991, 344)):
    parts.append((tag+'_FIANCO', P(cx, 17, 18, 2168)))
    parts.append((tag+'_FIANCO', P(cx+cw-18, 17, 18, 2168)))
    parts.append((tag+'_BASE',   P(vx, 6, vw, 212)))               # zoccolo/vano basso
    parts.append((tag+'_RIPIANO',P(vx, 852-18, vw, 18)))           # piano sotto il vano alto
    parts.append((tag+'_SCHIENA',P(vx, 17, vw, 2168, XF, XF+18)))  # schienale del vano
parts.append(('FASCIA_ALTA', P(0, 2197, 2368, 94, XB-18, XB)))
parts.append(('CIELO',       P(0, 2214, 2368, 18)))
# ---- letto: rete/contenitore + materasso + guanciali (footprint dalla pianta) ----
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))
BX0,BX1,BY0,BY1 = 573.0, 2573.0, 1528.0, 3128.0   # materasso 2000x1600 dalla pianta
parts.append(('LETTO_contenitore', box(BX0,BX1,BY0,BY1,PAV,PAV+340)))
parts.append(('MATERASSO',         box(BX0,BX1,BY0,BY1,PAV+340,PAV+540)))   # dalla sezione: 340..540
for gy in (BY0+60, BY0+830):
    parts.append(('GUANCIALE', box(BX0+60,BX0+460,gy,gy+700,PAV+540,PAV+660)))

MIRROR_X = 7023.0        # asse di specchiatura master -> camera doppia
def col(n):
    if 'MATERASSO' in n: return '#c7a34e'
    if 'GUANCIALE' in n: return '#e8e8ea'
    if 'contenitore' in n: return '#8a6a42'
    if 'MONTANTE' in n or 'FASCIA' in n or 'CIELO' in n: return '#6f5334'
    if 'TESTATA' in n: return '#a8825a'
    return '#b8946a'
def emetti(sol, key):
    comp=cq.Compound.makeCompound(sol)
    exporters.export(comp,str(HERE/f'{key}_posizionato.step'))
    mesh=[]
    for (n,_),s in zip(parts,sol):
        v,t=s.tessellate(0.4)
        mesh.append({'l':n,'c':col(n),'v':[[round(a.x,1),round(a.y,1),round(a.z,1)] for a in v],'f':[[int(i) for i in f] for f in t]})
    json.dump(mesh,open(HERE/f'{key}_mesh.json','w'),separators=(',',':'))
    bb=comp.BoundingBox()
    print(f"{key}: {len(sol)} pezzi  X[{bb.xmin:.0f},{bb.xmax:.0f}] Y[{bb.ymin:.0f},{bb.ymax:.0f}] "
          f"Z[{bb.zmin-PAV:.0f},{bb.zmax-PAV:.0f}] (da terra)")

sol=[s.val() for _,s in parts]
emetti(sol,'letto_master')
# camera doppia: stesso mobile, specchiato -> testata contro la parete di fondo (X 13488)
solD=[s.mirror('YZ', (MIRROR_X,0,0)) for s in sol]
emetti(solD,'letto_doppia')
