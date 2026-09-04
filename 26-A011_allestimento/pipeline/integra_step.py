#!/usr/bin/env python3
"""Integra nel modello del truck gli STEP che manda Matteo (assiemi con i nomi dei pezzi).

Per ogni pezzo: legge l'assieme STEP (nomi dalla distinta), lo POSIZIONA nelle
coordinate trailer usando la planimetria, tessella ogni parte mantenendo il NOME,
ed esporta lo STEP posizionato.

Le trasformazioni sono state ricavate confrontando il modello con la planimetria
(match esatto: fianchi armadio offset 991; pannelli TV divisorio su X 4150/3984).
"""
import json, pathlib, math, sys
import cadquery as cq
from cadquery import exporters
from step_assembly import read_assembly
HERE = pathlib.Path(__file__).parent
PAV = 1395.0

# key -> (file, trasformazione)   rot = gradi attorno a Z, poi traslazione
PEZZI = {
 'armadio_master':    dict(rot=0,  off=(991.0,   49.0, PAV)),
 'parete_div_master': dict(rot=90, off=(4278.0, 1242.0, PAV)),
 'armadio_doppia':    dict(rot=0,  off=(11382.0, 49.0, PAV)),   # match esatto sugli 8 fianchi
}

def colore(nome):
    n = nome.upper()
    if 'ANTA' in n:                                   return '#7a5a36'
    if 'CASSETTO' in n or 'CTRA' in n or 'CASSETT' in n: return '#8a6a42'
    if 'RIPIANO' in n:                                return '#c9a878'
    if 'FASCIA' in n or 'FASCIONE' in n or 'VELETTA' in n: return '#6f5334'
    if 'CORNICE' in n:                                return '#8c6a45'
    if 'PANNELLO_TV' in n or 'PANNCAM' in n:          return '#4a5a66'
    if 'PORTA' in n:                                  return '#9a7b52'
    if 'MONTANTE' in n or 'SPALLETTA' in n or 'TRAVON' in n or 'TRAV' in n: return '#b8946a'
    return '#a8825a'                                   # carcassa (fianchi/base/cielo/schiena)

def posiziona(shape, rot, off):
    s = cq.Shape.cast(shape)
    if rot:
        s = s.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), rot)
    return s.translate(cq.Vector(*off))

def integra(key, path, tol=0.4):
    cfg = PEZZI[key]
    parts = read_assembly(str(path))
    mesh, solids = [], []
    for nome, sh in parts:
        s = posiziona(sh, cfg['rot'], cfg['off'])
        solids.append(s)
        v, t = s.tessellate(tol)
        mesh.append({'l': nome.replace('26-A011_', ''), 'c': colore(nome),
                     'v': [[round(a.x, 1), round(a.y, 1), round(a.z, 1)] for a in v],
                     'f': [[int(i) for i in f] for f in t]})
    comp = cq.Compound.makeCompound(solids)
    exporters.export(comp, str(HERE / 'mobili' / f'{key}_posizionato.step'))
    bb = comp.BoundingBox()
    print(f"{key}: {len(parts)} pezzi  vol={comp.Volume()/1e9:.3f} m3  "
          f"X[{bb.xmin:.0f},{bb.xmax:.0f}] Y[{bb.ymin:.0f},{bb.ymax:.0f}] Z[{bb.zmin:.0f},{bb.zmax:.0f}]")
    return mesh

if __name__ == '__main__':
    # uso: integra_step.py chiave=percorso.stp [chiave=percorso.stp ...]
    out = {}
    for arg in sys.argv[1:]:
        key, path = arg.split('=', 1)
        out[key] = integra(key, path)
    if out:
        json.dump(out, open(HERE / 'mobili' / 'step_matteo_mesh.json', 'w'), separators=(',', ':'))
        print('scritto mobili/step_matteo_mesh.json  ->', {k: len(v) for k, v in out.items()})
