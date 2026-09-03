#!/usr/bin/env python3
# ARMADIO master v2 -> DXF/DWG a FACCE (anteprima rapida; per i SOLIDI usare lo STEP).
# Stessa geometria del builder solido: 6 bussolotti + fasce + ante + maniglie.
import ezdxf, pathlib
HERE=pathlib.Path(__file__).parent
PAV=1395.0; T=18.0; H=2200.0; PLINT=100.0
YB,YF=49.0,629.0; Z0=PAV; ZT=PAV+H
MODS=[(1041,1389),(1425,1873),(1938,2386),(2426,2874),(2939,3387),(3423,3771)]
DOORS=[(1044,1394),(1428,1878),(1941,2391),(2421,2871),(2934,3384),(3418,3768)]
TIPI=['ripiani','appenderia','ripiani','ripiani','appenderia','ripiani']
Xtot0,Xtot1=1041.0,3771.0
boxes=[]
def B(l,x0,x1,y0,y1,z0,z1): boxes.append((l,x0,x1,y0,y1,z0,z1))
B("FASCIA",Xtot0,Xtot1,YB,YF,Z0,Z0+PLINT); B("FASCIA",Xtot0,Xtot1,YB,YF,ZT-T,ZT); B("FASCIA",Xtot0,Xtot1,YB,YB+T,Z0+PLINT,ZT-T)
for (xo0,xo1),tp in zip(MODS,TIPI):
    xi0,xi1=xo0+T,xo1-T; zc0,zc1=Z0+PLINT,ZT-T
    B("FIANCO",xo0,xo0+T,YB+T,YF,zc0,zc1); B("FIANCO",xo1-T,xo1,YB+T,YF,zc0,zc1)
    B("FIANCO",xo0,xo1,YB+T,YF,zc0,zc0+T); B("FIANCO",xo0,xo1,YB+T,YF,zc1-T,zc1)
    if tp=='appenderia':
        zs=zc1-360; B("RIPIANO",xi0,xi1,YB+T,YF-30,zs,zs+T)
        B("BASTONE",xi0+10,xi1-10,(YB+YF)/2-15,(YB+YF)/2+15,zs-70,zs-40)
    else:
        for k in range(1,6):
            z=zc0+k*(zc1-zc0)/6.0; B("RIPIANO",xi0,xi1,YB+T,YF-30,z,z+T)
for (dx0,dx1) in DOORS:
    B("ANTA",dx0+2,dx1-2,YF+1,YF+1+T,Z0+PLINT+2,ZT-T-2)
    cxm=(dx0+dx1)/2; hx=dx1-45 if cxm<(Xtot0+Xtot1)/2 else dx0+25
    B("MANIGLIA",hx,hx+22,YF+1+T,YF+1+T+28,PAV+980,PAV+1300)

doc=ezdxf.new("R2010"); msp=doc.modelspace()
for n,c in {"FASCIA":18,"FIANCO":8,"RIPIANO":42,"BASTONE":251,"ANTA":24,"MANIGLIA":1}.items(): doc.layers.add(n,color=c)
def faces(x0,x1,y0,y1,z0,z1):
    c=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    return [(c[0],c[1],c[2],c[3]),(c[4],c[5],c[6],c[7]),(c[0],c[1],c[5],c[4]),(c[1],c[2],c[6],c[5]),(c[2],c[3],c[7],c[6]),(c[3],c[0],c[4],c[7])]
for l,x0,x1,y0,y1,z0,z1 in boxes:
    for f in faces(x0,x1,y0,y1,z0,z1): msp.add_3dface(f,dxfattribs={"layer":l})
doc.saveas(str(HERE/"armadio_master_3d.dxf"))
print("DXF v2 a facce:",len(boxes),"box, audit err:",len(doc.audit().errors))
