#!/usr/bin/env python3
"""Volumi mobile ingresso-living 026-A011 rev.01.

Origine: X=0 filo sx (6632.8 nel DWG), Y=0 retro (3492.9), Z=0 pavimento
(3658.3). Pianta e vista frontale (sezione A-A') condividono le X del DWG;
la vista laterale (5660.4..6260.4) e' la colonna vista di fianco (P600).
Quote DIMENSION nel file: 266 / 446.5 / 360 di fronte, P600, H2080 — tutte
riscontrate sulla geometria al decimo.
"""
import json

box = []

def B(nome, layer, colore, tinta, x0, y0, z0, x1, y1, z1, materiale=None):
    b = {"nome": nome, "layer": layer, "colore": colore, "tinta": tinta,
         "x0": round(x0, 1), "y0": round(y0, 1), "z0": round(z0, 1),
         "x1": round(x1, 1), "y1": round(y1, 1), "z1": round(z1, 1)}
    if materiale:
        b["materiale"] = materiale
    box.append(b)

SP = 18.0
P = 600.0
LAM = dict(layer="VOL_LAMINATO", colore=250, tinta="#4a4a48", materiale="MULTI laminato OPACO")
CER = dict(layer="VOL_CERA", colore=8, tinta="#cfc8bb", materiale="MULTI laminato CERA")
VET = dict(layer="VOL_VETRO", colore=140, tinta="#bcdce4", materiale="VETRO stratificato satinato")
LED = dict(layer="VOL_LED", colore=2, tinta="#ffe08a", materiale="STRIP-LED")
DOM = dict(layer="VOL_DOMOTICA", colore=18, tinta="#1f1f22", materiale="Pannello DOMOTICA touch")

# ---------- COLONNA scarpiera/domotica: X 0..331 (fronte 266 quotato: 61.5..331)
B("COL_fianco_SX_sp18", **LAM, x0=0, y0=0, z0=5.5, x1=SP, y1=P, z1=2080)
B("COL_schienale_sp18", **CER, x0=0, y0=0, z0=5.5, x1=326.0, y1=SP, z1=2080)
B("COL_zoccolo_h74", **LAM, x0=78.0, y0=24.0, z0=5.5, x1=308.0, y1=582.0, z1=80.0)
B("COL_fronte_basso_sp18", **LAM, x0=61.5, y0=582.0, z0=80.0, x1=331.0, y1=P, z1=1298.0)
B("COL_pannello_DOMOTICA_h198", **DOM, x0=61.5, y0=582.0, z0=1301.0, x1=331.0, y1=P, z1=1499.0)
B("COL_fronte_alto_sp18", **LAM, x0=61.5, y0=582.0, z0=1502.0, x1=331.0, y1=P, z1=2077.0)
# ripiani scarpiera inclinati (retro alto, fronte basso ~300/620/950):
# qui volumi orizzontali alla quota del bordo frontale, da confermare
for k, z in enumerate((300.0, 620.0, 950.0), 1):
    B(f"COL_ripiano_scarpiera{k}_sp18", **CER, x0=SP, y0=60.0, z0=z,
      x1=326.0, y1=560.0, z1=z + SP)
B("COL_ripiano_divisorio_sp18", **CER, x0=SP, y0=60.0, z0=1298.0,
  x1=326.0, y1=560.0, z1=1316.0)

# ---------- MONTANTE tecnico 40: X 326..366, tutta altezza e profondita'
B("MONTANTE_40_H2080", **LAM, x0=326.0, y0=0, z0=0, x1=366.0, y1=P, z1=2080.0)

# ---------- GUARDAROBA: X 366..812.5 (vano 446.5), anta 450
B("GUA_zoccolo_h74", **LAM, x0=384.0, y0=24.0, z0=5.5, x1=794.5, y1=582.0, z1=80.0)
B("GUA_fondo_sp18", **CER, x0=366.0, y0=0, z0=80.0, x1=812.5, y1=582.0, z1=98.0)
B("GUA_cielo_sp18", **CER, x0=366.0, y0=0, z0=2056.0, x1=812.5, y1=582.0, z1=2074.0)
B("GUA_anta_450_sp18", **LAM, x0=361.0, y0=582.0, z0=80.0, x1=811.0, y1=P, z1=2077.0)

# ---------- LIBRERIA: X 812.5..1172.5 (montanti 30, vano 300, vetro frontale)
B("LIB_montante_SX_30", **LAM, x0=812.5, y0=0, z0=5.5, x1=842.5, y1=P, z1=2080.0)
B("LIB_montante_DX_30", **LAM, x0=1142.5, y0=300.0, z0=5.5, x1=1172.5, y1=P, z1=2080.0)
B("LIB_zoccolo_h74", **LAM, x0=842.5, y0=300.0, z0=5.5, x1=1142.5, y1=582.0, z1=80.0)
B("LIB_vetro_satinato_sp8", **VET, x0=834.5, y0=558.3, z0=102.0,
  x1=1148.5, y1=566.3, z1=1976.0)
for k, z in enumerate((80.0, 394.0, 720.0, 1150.0, 1540.0, 1970.0), 1):
    B(f"LIB_ripiano{k}_sp30", **LAM, x0=842.5, y0=304.0, z0=z,
      x1=1142.5, y1=554.5, z1=z + 30.0)

# ---------- LED: 2 lame verticali incassate nelle gole ai lati del montante
# (scassi 8x4 in pianta a y=535; lato colonna in 2 segmenti interrotti dal
# pannello domotica come da vista laterale)
B("LED_lama_colonna_basso", **LED, x0=308.1, y0=535.0, z0=98.0,
  x1=316.0, y1=539.0, z1=1290.5)
B("LED_lama_colonna_alto", **LED, x0=308.1, y0=535.0, z0=1509.5,
  x1=316.0, y1=539.0, z1=2062.0)
B("LED_lama_guardaroba", **LED, x0=376.1, y0=535.0, z0=98.0,
  x1=384.0, y1=539.0, z1=2062.0)

data = {
    "titolo": "MOBILE INGRESSO-LIVING 026-A011 rev.01 - VOLUMI (no ferramenta)",
    "note": "Quote dal DWG: fronte 266+40+446.5+360 = 1172.5, P600, H2080 "
            "(DIMENSION nel file, riscontrate sulla geometria). Colonna "
            "scarpiera con pannello DOMOTICA touch h198 a z1301 che "
            "interrompe la lama LED; guardaroba con anta 450 H1997; libreria "
            "a giorno 300x250 con 6 ripiani sp30 e VETRO satinato sp8 sul "
            "fronte. DA CONFERMARE: ripiani scarpiera qui orizzontali (nel "
            "disegno inclinati), guardaroba senza schienale disegnato, "
            "quote zoccoli arretrati, lama LED guardaroba senza interruzione.",
    "materiali": {},
    "box": box,
}
with open("volumi.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=1, ensure_ascii=False)
print(f"{len(box)} pezzi -> volumi.json")
