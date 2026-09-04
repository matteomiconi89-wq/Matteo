#!/usr/bin/env python3
"""Rigenera la scena della camera master dentro render_camera_master.html.

Sorgente: ../arredo_geometry.json (mesh con il NOME di distinta di ogni pezzo).
Prende i soli tre mobili della camera master e riscrive la riga `const SCENA={...};`
del render, cosi' il render resta allineato ai modelli senza rifare l'HTML a mano.

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

scena = {}
for k, label in CAMERA_MASTER.items():
    parts = G.get(k)
    if not parts:
        raise SystemExit(f"manca {k} in arredo_geometry.json")
    scena[k] = {"label": label,
                "parts": [{"n": p["l"], "v": p["v"], "f": p["f"]} for p in parts]}

html = HERE / "render_camera_master.html"
testo = html.read_text()
nuovo = "const SCENA = " + json.dumps(scena, separators=(",", ":")) + ";"
testo, n = re.subn(r"const SCENA *= *\{.*\};\n", lambda _: nuovo + "\n", testo, count=1)
if n != 1:
    raise SystemExit("riga `const SCENA=...` non trovata nel render")
html.write_text(testo)
print("scena aggiornata:", {k: len(v["parts"]) for k, v in scena.items()},
      "->", html.name, len(testo) // 1024, "KB")
