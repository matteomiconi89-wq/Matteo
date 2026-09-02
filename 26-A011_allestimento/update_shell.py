#!/usr/bin/env python3
# Tessella il nuovo STEP scocca (con controsoffitto), lo porta in coord. trailer,
# lo decima leggero e aggiorna shell_step nella geometria dell'allestimento.
import cascadio, trimesh, numpy as np, json, pathlib
BASE = pathlib.Path(__file__).parent

cascadio.step_to_glb('step_new.stp','step_new.glb', tol_linear=0.4, tol_angular=0.3)
s=trimesh.load('step_new.glb')
g=s.to_geometry() if hasattr(s,'to_geometry') else s
V=np.array(g.vertices,float); F=np.array(g.faces,np.int64)

# STEP(m) -> trailer(mm): X*1000, Y*1000+2420, Z*1000+1395
W=np.empty_like(V)
W[:,0]=V[:,0]*1000.0
W[:,1]=V[:,1]*1000.0+2420.0
W[:,2]=V[:,2]*1000.0+1395.0

def cluster(V,F,grid):
    key=np.floor(V/grid).astype(np.int64)
    uniq,inv=np.unique(key,axis=0,return_inverse=True); inv=inv.ravel()
    nV=np.zeros((len(uniq),3)); cnt=np.zeros(len(uniq))
    np.add.at(nV,inv,V); np.add.at(cnt,inv,1); nV/=cnt[:,None]
    nf=inv[F]
    good=(nf[:,0]!=nf[:,1])&(nf[:,1]!=nf[:,2])&(nf[:,0]!=nf[:,2]); nf=nf[good]
    sF=np.sort(nf,axis=1); _,ui=np.unique(sF,axis=0,return_index=True)
    return nV,nf[ui]

g0=18.0; nV,nF=cluster(W,F,g0)
while len(nF)>8000:
    g0*=1.2; nV,nF=cluster(W,F,g0)
print(f"shell {len(F)} -> {len(nF)} faces (grid {g0:.0f}) bbox {nV.min(0).round(0)} {nV.max(0).round(0)}")

shell_mesh={"l":"SCOCCA_STEP","v":[[round(float(c),1) for c in p] for p in nV.tolist()],
            "f":[[int(i) for i in t] for t in nF.tolist()]}

G=json.load(open(BASE/"arredo_geometry_solidi.json"))
G["shell_step"]=[shell_mesh]
G["_shell_note"]="STEP 26A011_Scocca con controsoffitto (0ce015f6), decimato"
p=BASE/"arredo_geometry_solidi.json"
p.write_text(json.dumps(G,separators=(",",":")))
import os;print("aggiornato",p.name,os.path.getsize(p)//1024,"KB")
