#!/usr/bin/env python3
"""Integra nel modello del truck gli STEP che manda Matteo (assiemi con la distinta).

Per ogni pezzo: legge l'assieme STEP, lo POSIZIONA in coordinate trailer, tessella
ogni parte mantenendo CODICE e MATERIALE, esporta lo STEP posizionato e riscrive la
sua voce dentro ../arredo_geometry.json.

I nomi dei pezzi negli STEP aggiornati sono nella forma
    26-A011_PLS_174_RIPIANO -- MULT.LAM.B.18mm 305x130
cioe' portano il materiale dopo il `--`: e' la fonte piu' attendibile che abbiamo,
piu' dei layer della pianta, e viene usata per prima.

Le trasformazioni non sono scritte a mano: le trova aggancia_step.py confrontando
le impronte dei pezzi con le polilinee della pianta (rot 0/90/180/270 + offset).

    python3 integra_step.py            # usa le posizioni gia' agganciate qui sotto
"""
import json, pathlib, sys
import cadquery as cq
from cadquery import exporters
from step_assembly import read_assembly

HERE = pathlib.Path(__file__).parent
PAV = 1395.0
UP = pathlib.Path("/root/.claude/uploads/31efb9b7-647e-5589-8875-ea5660dd57ca")

# chiave -> file, rotazione attorno a Z, offset in pianta.
# rot/offset verificati da aggancia_step.py sulle polilinee della pianta
# (pezzi che combaciano: master 26/106, doppia 24/90, divisorio 23/55,
#  parete letto 15/50, ingresso 29/37).
PEZZI = {
 'armadio_master':      dict(f='d48a28e2-26A011_ArmadioCameraMaster.stp', rot=0,   off=(990.9, 48.8)),
 'armadio_doppia':      dict(f='bfd25c55-26A011_ArmadioCameraDoppia.stp', rot=0,   off=(11381.9, 48.8)),
 'parete_div_master':   dict(f='16abd2bd-26A011_Divisorio_living.stp',    rot=90,  off=(4278.4, 1223.8)),
 'parete_letto_master': dict(f='fffdb07b-26A011_PareteLetto.stp',         rot=90,  off=(865.4, 1223.8)),
 'ingresso_living':     dict(f='de2fba7f-26A011_IngressoLiving.stp',      rot=270, off=(7008.9, 1226.3)),
 # la camera doppia non e' disegnata in questa revisione della pianta: la parete
 # letto e' ancorata al vano — schiena contro la testata del vano (X 13593.4, dove
 # finiscono i rivestimenti laterali) e stessa fascia in Y della master (1223.8..3591.8).
 # Ruotata di 270 perche' guarda verso il divisorio, non verso la coda. DA CONFERMARE.
 'parete_letto_doppia': dict(f='0b000a3b-26A011_PareteLetto_CameraDoppia.stp',
                             rot=270, off=(13286.4, 3591.8)),
}


def scomponi(nome):
    """'26-A011_PLS_174_RIPIANO -- MULT.LAM.B.18mm' -> ('PLS_174_RIPIANO', 'MULT.LAM.B.18mm')"""
    n = nome.replace('26-A011_', '').strip()
    if '--' in n:
        cod, mat = n.split('--', 1)
        return cod.strip(), mat.strip()
    return n, None


def posiziona(shape, rot, off):
    s = cq.Shape.cast(shape)
    if rot:
        s = s.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), rot)
    return s.translate(cq.Vector(off[0], off[1], PAV))


def integra(key, cfg, tol=0.4):
    parts = read_assembly(str(UP / cfg['f']))
    mesh, solidi, senza = [], [], 0
    for nome, sh in parts:
        cod, mat = scomponi(nome)
        senza += mat is None
        s = posiziona(sh, cfg['rot'], cfg['off'])
        solidi.append(s)
        v, t = s.tessellate(tol)
        mesh.append({'l': cod, 'm': mat,
                     'v': [[round(a.x, 1), round(a.y, 1), round(a.z, 1)] for a in v],
                     'f': [[int(i) for i in f] for f in t]})
    comp = cq.Compound.makeCompound(solidi)
    exporters.export(comp, str(HERE / 'mobili' / f'{key}_posizionato.step'))
    bb = comp.BoundingBox()
    print(f"{key:20s} {len(parts):3d} pezzi  ({senza} senza materiale)  vol={comp.Volume()/1e9:.3f} m3  "
          f"X[{bb.xmin:.0f},{bb.xmax:.0f}] Y[{bb.ymin:.0f},{bb.ymax:.0f}] Z[{bb.zmin:.0f},{bb.zmax:.0f}]")
    return mesh


# Il letto della doppia: ne abbiamo solo il materasso. Lo specchiamo dal master
# attorno all'asse che porta la schiena di una parete letto sulla schiena dell'altra
# (558.4 -> 13593.4), cosi' la testa del materasso entra nella campata centrale con
# lo stesso gioco di 15 mm che ha nel master.
MIRROR_X = (558.4 + 13593.4) / 2


def specchia(mesh, asse):
    fuori = []
    for m in mesh:
        fuori.append({'l': m['l'], 'm': m.get('m'),
                      'v': [[round(2 * asse - x, 1), y, z] for x, y, z in m['v']],
                      'f': [list(reversed(f)) for f in m['f']]})   # normali coerenti
    return fuori


if __name__ == '__main__':
    geo_path = HERE.parent / 'arredo_geometry.json'
    G = json.load(open(geo_path))
    for key, cfg in PEZZI.items():
        G['mobili'][key] = integra(key, cfg)
    # il vecchio mobile_ingresso e' sostituito dallo STEP reale
    G['mobili'].pop('mobile_ingresso', None)
    # letto_master conteneva anche la parete: ora la parete e' lo STEP, restano
    # materasso e guanciali (ricostruiti dalla sezione, quote reali Z 340..540)
    letto = [m for m in G['mobili'].get('letto_master', [])
             if 'MATERASSO' in m['l'].upper() or 'GUANCIALE' in m['l'].upper()]
    if letto:
        G['mobili']['letto_master'] = letto
        G['mobili']['letto_doppia'] = specchia(letto, MIRROR_X)

    json.dump(G, open(geo_path, 'w'), separators=(',', ':'))
    print(f"\nscritto {geo_path.name}: {len(G['mobili'])} mobili, "
          f"{sum(len(v) for v in G['mobili'].values())} pezzi")
