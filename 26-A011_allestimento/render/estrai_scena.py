#!/usr/bin/env python3
"""Rigenera la scena della camera master dentro render_camera_master.html.

Sorgenti: ../arredo_geometry.json (mesh con il NOME di distinta di ogni pezzo),
../materiali.json (layer materiale letto dal DWG, vedi pipeline/materiali_da_dwg.py)
e materiali_render.json (come si rende ogni materiale). Riscrive nel render le righe
`const SCENA={...};` e `const MATERIALI={...};`, cosi' resta allineato ai modelli
senza rifare l'HTML a mano.

    python3 estrai_scena.py
"""
import json, pathlib, re

HERE = pathlib.Path(__file__).parent
G = json.load(open(HERE.parent / "arredo_geometry.json"))["mobili"]

# chiave -> etichetta mostrata quando si clicca un pezzo
CAMERA_MASTER = {
    "armadio_master":    "Armadio",
    "letto_master":      "Testata e letto",
    "parete_div_master": "Divisorio",
}

MAT = json.load(open(HERE.parent / "materiali.json"))

scena = {}
for k, label in CAMERA_MASTER.items():
    parts = G.get(k)
    if not parts:
        raise SystemExit(f"manca {k} in arredo_geometry.json")
    mat = MAT.get(k, [])
    scena[k] = {"label": label, "parts": [
        {"n": p["l"], "v": p["v"], "f": p["f"],
         "m": mat[i][1] if i < len(mat) else None,      # layer materiale dal DWG
         "p": mat[i][2] if i < len(mat) else "ignoto"}  # come e' stato ricavato
        for i, p in enumerate(parts)]}

html = HERE / "render_camera_master.html"
testo = html.read_text()
nuovo = "const SCENA = " + json.dumps(scena, separators=(",", ":")) + ";"
testo, n = re.subn(r"const SCENA *= *\{.*\};\n", lambda _: nuovo + "\n", testo, count=1)
if n != 1:
    raise SystemExit("riga `const SCENA=...` non trovata nel render")

res = json.load(open(HERE / "materiali_render.json"))
riga = "const MATERIALI = " + json.dumps(res, separators=(",", ":"), ensure_ascii=False) + ";"
testo, n = re.subn(r"const MATERIALI *= *\{.*?\};\n", lambda _: riga + "\n", testo,
                   count=1, flags=re.S)
if n != 1:
    raise SystemExit("riga `const MATERIALI=...` non trovata nel render")
html.write_text(testo)
print("scena aggiornata:", {k: len(v["parts"]) for k, v in scena.items()},
      "->", html.name, len(testo) // 1024, "KB")
