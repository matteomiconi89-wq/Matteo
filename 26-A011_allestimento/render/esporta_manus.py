#!/usr/bin/env python3
"""Pacchetto per il rendering esterno (Manus, Blender, qualunque motore).

Esporta la geometria dei modelli esecutivi in formati che un motore di render
legge senza CAD: GLB (consigliato) e OBJ/MTL. Ogni pezzo resta un oggetto
separato col suo CODICE DI DISTINTA, e il materiale e' quello LETTO DAI LAYER
del DWG (../materiali.json, vedi pipeline/materiali_da_dwg.py): lo slot nel GLB
porta il nome del layer, cosi' chi fa il render sostituisce la finitura senza
toccare la geometria.

Convenzione (la stessa in tutti i file esportati):
    metri, terna DESTRORSA, Y in alto, pavimento a y = 0
    x = (X_trailer - origine) / 1000        lunghezza del veicolo
    y = (Z_trailer - 1395)   / 1000         altezza dal pavimento
    z = -(Y_trailer - origine) / 1000       larghezza  (negato: senza il meno
                                            la scena esce SPECCHIATA)

    python3 esporta_manus.py
"""
import json, pathlib, shutil
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial

HERE = pathlib.Path(__file__).parent
OUT = HERE / "manus"
OUT.mkdir(exist_ok=True)
PAV = 1395.0
CENTRO_MASTER = (2422.0, 1829.5)           # centro della camera master, in pianta
ASSE_VEICOLO  = (0.0, 2420.0)              # muso del trailer, mezzeria in larghezza

# ---------------------------------------------------------------- materiali
# I materiali sono i layer `F_...` del DWG; materiali_render.json dice come renderli.
RESA = json.load(open(HERE / "materiali_render.json"))
MAT = json.load(open(HERE.parent / "materiali.json"))


def rgb(h):
    return [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]


_cache = {}
def materiale(layer):
    """layer del DWG -> materiale PBR con lo stesso nome"""
    if layer not in _cache:
        d = RESA.get(layer) or RESA["_default"]
        _cache[layer] = PBRMaterial(
            name=layer or "NON_DETERMINATO",
            baseColorFactor=rgb(d["base"]) + [1.0],
            roughnessFactor=d["ruv"], metallicFactor=d["met"])
    return _cache[layer]


def triangola(facce):
    """le mesh della scocca hanno anche facce a piu' di 3 lati: ventaglio"""
    tri = []
    for f in facce:
        for i in range(1, len(f) - 1):
            tri.append((f[0], f[i], f[i + 1]))
    return np.asarray(tri, dtype=np.int64) if tri else np.zeros((0, 3), dtype=np.int64)


def scena(meshes, origine, mat_fisso=None):
    """meshes = [(chiave, {l,v,f}), ...] -> trimesh.Scene in metri, Y in alto."""
    ox, oy = origine
    sc = trimesh.Scene()
    visti = {}
    materiali_pezzo = {(k, n): mat for k, lst in MAT.items() for n, mat, _ in lst}
    for chiave, m in meshes:
        V = np.asarray(m["v"], dtype=float)
        F = triangola(m["f"])
        if len(F) == 0:
            continue
        P = np.column_stack([(V[:, 0] - ox) / 1000.0,
                             (V[:, 2] - PAV) / 1000.0,
                             -(V[:, 1] - oy) / 1000.0])          # terna destrorsa
        t = trimesh.Trimesh(vertices=P, faces=F, process=False)
        t.visual = trimesh.visual.TextureVisuals(
            material=materiale(mat_fisso if mat_fisso is not None
                               else materiali_pezzo.get((chiave, m["l"]))))
        nome = f"{chiave}__{m['l']}"
        visti[nome] = visti.get(nome, 0) + 1
        if visti[nome] > 1:
            nome = f"{nome}_{visti[nome]:03d}"                    # nomi unici nel GLB
        sc.add_geometry(t, node_name=nome, geom_name=nome)
    return sc


G = json.load(open(HERE.parent / "arredo_geometry.json"))
MOB = G["mobili"]
CAMERA_MASTER = ("armadio_master", "parete_letto_master", "letto_master",
                 "parete_div_master")

# ------------------------------------------------- 1. camera master da sola
mm = [(k, m) for k in CAMERA_MASTER for m in MOB[k]]
sc = scena(mm, CENTRO_MASTER)
sc.export(OUT / "26A011_camera_master.glb")
sc.export(OUT / "26A011_camera_master.obj")
with open(OUT / "material.mtl", "w") as f:                 # trimesh lascia l'mtl vuoto
    for lay in sorted({m for k in CAMERA_MASTER for _, m, _ in MAT[k]}):
        d = RESA.get(lay) or RESA["_default"]
        r, g, b = rgb(d["base"])
        f.write(f"newmtl {(lay or 'NON_DETERMINATO').replace(' ', '_')}\n"
                f"# {d['nome']} — finitura: {d['finitura']}\n"
                f"Kd {r:.4f} {g:.4f} {b:.4f}\nKa 0 0 0\nKs 0.04 0.04 0.04\n"
                f"Ns {max(1, round((1 - d['ruv']) * 200))}\nd 1\nillum 2\n\n")
print("camera master :", len(mm), "pezzi ->", "26A011_camera_master.glb / .obj")

# ------------------------------------------------- 2. allestimento completo
tutti = [(k, m) for k, lst in MOB.items() for m in lst]
sc2 = scena(tutti, ASSE_VEICOLO)
sc2.export(OUT / "26A011_arredo_completo.glb")
print("arredo tutto  :", len(tutti), "pezzi -> 26A011_arredo_completo.glb")

# ------------------------------------------------- 3. scocca del veicolo aperta
sc3 = scena([("scocca", m) for m in G["aperto"]], ASSE_VEICOLO,
            mat_fisso="F_PARETI-PAVIMENTI e SOFFITTI_cassone")
sc3.export(OUT / "26A011_scocca_aperta.glb")
print("scocca aperta :", len(G["aperto"]), "volumi -> 26A011_scocca_aperta.glb")

# ------------------------------------------------- 4. inquadrature verificate
INQ = {
  "convenzione": "metri, Y in alto, terna destrorsa, pavimento y=0, "
                 "origine al centro della camera master (trailer X2422 Y1829.5)",
  "obiettivo_mm": 35, "fov_verticale_gradi": 42,
  "vano": {"lunghezza": 3.728, "larghezza": 3.562, "altezza": 2.293},
  "inquadrature": [
    {"nome": "Dalla porta", "durata_s": 9,
     "camera_da": [2.80, 1.66, 1.30],  "camera_a": [1.78, 1.56, 1.02],
     "mira_da":   [0.20, 1.02, 0.20],  "mira_a":   [-0.55, 0.98, -0.10],
     "nota": "si entra dal living attraverso il varco del divisorio"},
    {"nome": "Armadio 6 casse", "durata_s": 9,
     "camera_da": [-1.20, 1.55, -0.58], "camera_a": [1.36, 1.50, -0.58],
     "mira_da":   [-1.10, 1.02, 1.45],  "mira_a":   [1.26, 1.02, 1.45],
     "nota": "carrellata parallela all'armadio, sopra il letto"},
    {"nome": "Testata e letto", "durata_s": 8,
     "camera_da": [1.28, 1.62, -0.78], "camera_a": [0.18, 1.30, -0.56],
     "mira_da":   [-1.32, 0.94, -0.42], "mira_a":  [-1.62, 1.06, -0.46]},
    {"nome": "Spaccato sul fianco", "durata_s": 12, "tipo": "arco",
     "angolo_gradi": [-55, -118], "raggio": [3.10, 2.55], "altezza": [1.75, 1.35],
     "centro": [0.0, 0.0, -0.10], "mira": [-0.20, 1.00, -0.05],
     "nota": "camera fuori dal fianco che si allarga; la parete non va renderizzata"},
  ],
  "vincolo": "il vano e' chiuso su tre lati: armadio su z 1.16..1.78, testata su "
             "x < 0.15, divisorio su x 1.52..1.86 tranne il varco a z > 0.59. "
             "Camere fuori da questi due settori inquadrano un muro.",
}
json.dump(INQ, open(OUT / "inquadrature.json", "w"), indent=1, ensure_ascii=False)

# ------------------------------------------------- 5. disegni di riferimento
for f in ("arredo_plan.png", "insieme_plan.png", "arredo_axo.png"):
    p = HERE.parent / f
    if p.exists():
        shutil.copy(p, OUT / f)

for f in sorted(OUT.iterdir()):
    print(f"   {f.stat().st_size//1024:6d} KB  {f.name}")
