#!/usr/bin/env python3
# ARMADIO camera master — MODELLO 3D in DXF/DWG (polyface mesh, facce quadre pulite per snap).
# Parti come box -> 6 facce quadre; bastoni come barra. Layer per tipo. Coord trailer mm.
import ezdxf
from ezdxf.render import MeshBuilder
doc=ezdxf.new("R2010"); msp=doc.modelspace()
LAYCOL={"STRUTTURA":8,"MONTANTE":38,"RIPIANO":42,"CASSETTO":30,"ANTA":24,"MANIGLIA":1,"BASTONE":251,"ZOCCOLO":18}
for n,c in LAYCOL.items(): doc.layers.add(n,color=c)

PAV=1395.0
X0,X1=1005.0,3807.0; YB,YF=49.0,657.0
H=2200.0; T=18.0; PLINT=100.0
Z0=PAV; ZT=PAV+H; Zb=Z0+PLINT+T; Zt=ZT-T
MONT=[1407,1906,2406,2907,3405]
DOORS=[(1048,350),(1436,450),(1945,450),(2429,450),(2942,450),(3426,350)]
TIPI=['r','a','c','c','a','r']
inner=[X0+T]+[m+T/2 for m in MONT]; right=[m-T/2 for m in MONT]+[X1-T]
VANI=list(zip(inner,right))

boxes=[]  # (layer, x0,x1,y0,y1,z0,z1)
def B(l,x0,x1,y0,y1,z0,z1): boxes.append((l,x0,x1,y0,y1,z0,z1))
# CARCASSA
B("STRUTTURA",X0,X0+T,YB,YF,Z0+PLINT,ZT); B("STRUTTURA",X1-T,X1,YB,YF,Z0+PLINT,ZT)
B("STRUTTURA",X0,X1,YB,YF,Z0+PLINT,Z0+PLINT+T); B("STRUTTURA",X0,X1,YB,YF,ZT-T,ZT)
B("STRUTTURA",X0,X1,YB,YB+T,Z0+PLINT,ZT)
B("ZOCCOLO",X0,X1,YF-T,YF,Z0,Z0+PLINT); B("ZOCCOLO",X0,X1,YB,YB+T,Z0,Z0+PLINT)
for xc in MONT: B("MONTANTE",xc-T/2,xc+T/2,YB+T,YF,Zb,Zt)
# INTERNI
for (xs,xd),tp in zip(VANI,TIPI):
    if tp=='r':
        for i in range(1,7):
            z=Zb+i*(Zt-Zb)/7.0; B("RIPIANO",xs,xd,YB+T,YF-30,z,z+T)
    elif tp=='a':
        zs=Zt-360; B("RIPIANO",xs,xd,YB+T,YF-30,zs,zs+T)
        cx=(xs+xd)/2; B("BASTONE",xs+10,xd-10,(YB+YF)/2-15,(YB+YF)/2+15,zs-60,zs-30)
    else:
        for k in range(3):
            zc=Zb+k*230; B("CASSETTO",xs+8,xd-8,YB+T,YF-40,zc+8,zc+222)
        zs=Zb+3*230+40; B("RIPIANO",xs,xd,YB+T,YF-30,zs,zs+T)
        za=Zt-360; B("RIPIANO",xs,xd,YB+T,YF-30,za,za+T)
        B("BASTONE",xs+10,xd-10,(YB+YF)/2-15,(YB+YF)/2+15,za-60,za-30)
# ANTE + MANIGLIE
for dx,dw in DOORS:
    B("ANTA",dx+2,dx+dw-2,YF,YF+T,Z0+PLINT+2,ZT-2)
    hx=dx+dw-45 if (dx+dw/2)<(X0+X1)/2 else dx+30
    B("MANIGLIA",hx,hx+22,YF+T,YF+T+28,PAV+980,PAV+1300)

def add_box(lay,x0,x1,y0,y1,z0,z1):
    v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    f=[[0,1,2,3],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]  # 6 facce quadre
    mb=MeshBuilder(); mb.vertices=v; mb.faces=f
    mb.render_polyface(msp,dxfattribs={"layer":lay})
for b in boxes: add_box(*b)

import pathlib; doc.saveas(str(pathlib.Path(__file__).parent/"armadio_master_3d.dxf"))
print("DXF 3D salvato:",len(boxes),"parti (box)")
