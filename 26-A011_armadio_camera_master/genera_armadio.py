#!/usr/bin/env python3
"""Genera volumi.json dell'armadio camera master 026-A011.

Origine: X=0 filo sinistro struttura (pianta), Y=0 filo retro (rivestimento
parete), Z=0 pavimento. Quote lette dalla geometria del DWG:
pianta sol.C (X e Y, traslata +20 rispetto al prospetto: compensata),
prospetto fronte chiuso (X e Z), sez.2 (Y e Z).
Collaudo incrociato: P 599.0 pianta = 599.0 sezione; ante coincidenti
pianta/prospetto al decimo; file cassetti identiche in prospetto e sezione.
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
H_FIANCO = (5.5, 2045.5)      # z fondo..cielo (cassone tessuto H 2040)
P_CASSONE = 580.0             # profondita' fianchi/fondi/cieli (y 0..580)
Y_INT = (21.0, 569.0)         # interno cassone in profondita' (dietro schienale sp9)

TES = dict(layer="VOL_TESSUTO", colore=8, tinta="#b9b2a6", materiale="MULTI rivestito tessuto")
LAM = dict(layer="VOL_LAMINATO", colore=250, tinta="#4a4a48", materiale="MULTI laminato OPACO")
LED = dict(layer="VOL_LED", colore=2, tinta="#ffe08a", materiale="STRIP-LED")

# ---- fianchi verticali sp18 (12, P580, H2040) — X di pianta -9744.9
FIANCHI = [36.0, 366.0, 420.0, 850.0, 933.0, 1363.0, 1421.0, 1851.0,
           1934.0, 2364.0, 2418.0, 2748.0]
for i, x in enumerate(FIANCHI, 1):
    B(f"FIANCO_{i:02d}_sp18", **TES, x0=x, y0=0, z0=H_FIANCO[0],
      x1=x + SP, y1=P_CASSONE, z1=H_FIANCO[1])

# ---- moduli: (nome, interno x0..x1, schienale x0..x1)
MODULI = {
    "A": (54.0, 366.0, 47.5, 372.5),     # interno fino alla spalla inclusa
    "B": (438.0, 850.0, 431.5, 856.5),
    "C": (951.0, 1363.0, 944.5, 1369.5),
    "D": (1439.0, 1851.0, 1432.5, 1857.5),
    "E": (1952.0, 2364.0, 1945.5, 2370.5),
    "F": (2436.0, 2748.0, 2429.5, 2754.5),
}
for m, (x0, x1, sx0, sx1) in MODULI.items():
    B(f"MOD{m}_fondo_sp18", **TES, x0=x0, y0=0, z0=5.5, x1=x1, y1=P_CASSONE, z1=23.5)
    B(f"MOD{m}_cielo_sp18", **TES, x0=x0, y0=0, z0=2027.5, x1=x1, y1=P_CASSONE, z1=2045.5)
    B(f"MOD{m}_schienale_sp9", **TES, x0=sx0, y0=12.0, z0=5.5, x1=sx1, y1=21.0, z1=2045.5)

# ---- ripiani a tutto vano, fianco a fianco (checkpoint Matteo 03/09:
# niente doppia spalla nei moduli A/F; profondita' come ripiano cassettiera)
Y_RIP = (51.0, 581.0)
for m, xs, quote_z in [("A", (54.0, 366.0), (273.5, 541.5, 809.5)),
                       ("B", (438.0, 850.0), (962.5,)),
                       ("E", (1952.0, 2364.0), (962.5,)),
                       ("F", (2436.0, 2748.0), (273.5, 541.5, 809.5))]:
    for k, z in enumerate(quote_z, 1):
        B(f"MOD{m}_ripiano{k}_sp18", **TES, x0=xs[0], y0=Y_RIP[0], z0=z,
          x1=xs[1], y1=Y_RIP[1], z1=z + SP)

# ---- cassettiere nei moduli C e D (da pianta: accostate al fianco sx del modulo)
for m, x_int in [("C", 951.0), ("D", 1439.0)]:
    sp_sx, sp_dx = x_int, x_int + 364.0             # spalle: interno cassetti 346
    B(f"MOD{m}_cass_spalla_SX_sp18", **TES, x0=sp_sx, y0=Y_INT[0], z0=23.5,
      x1=sp_sx + SP, y1=551.0, z1=564.5)
    B(f"MOD{m}_cass_spalla_DX_sp18", **TES, x0=sp_dx, y0=Y_INT[0], z0=23.5,
      x1=sp_dx + SP, y1=551.0, z1=564.5)
    B(f"MOD{m}_cass_ripiano_top_sp18", **TES, x0=x_int, y0=Y_RIP[0], z0=583.5,
      x1=x_int + 412.0, y1=Y_RIP[1], z1=601.5)
    for k, z in enumerate((33.5, 216.5, 399.5), 1):
        B(f"MOD{m}_cassetto{k}_fronte_sp18", **TES, x0=sp_sx + 3.0, y0=551.0,
          z0=z, x1=sp_sx + 3.0 + 376.0, y1=569.0, z1=z + 180.0)
        B(f"MOD{m}_cassetto{k}_vasca", **TES, x0=sp_sx + 39.0, y0=61.0,
          z0=z + 12.5, x1=sp_sx + 39.0 + 304.0, y1=551.0, z1=z + 162.5)

# ---- ante a battente (6, sp18, H2050, z5..2055, davanti alla struttura)
Y_ANTA = (581.0, 599.0)
for k, (x, w) in enumerate([(39.0, 350.0), (423.0, 450.0), (936.0, 450.0),
                             (1416.0, 450.0), (1929.0, 450.0), (2413.0, 350.0)], 1):
    B(f"ANTA_{k}_sp18_H2050", **LAM, x0=x, y0=Y_ANTA[0], z0=5.0,
      x1=x + w, y1=Y_ANTA[1], z1=2055.0)

# ---- montanti frontali laminato (tra le ante, arretrati: y 540..558, H2080)
for nome, x0, x1 in [("BATTUTA_SX_36", 0.0, 36.0), ("MONTANTE_1_54", 366.0, 420.0),
                     ("MONTANTE_2_65", 868.0, 933.0), ("MONTANTE_3_40", 1381.0, 1421.0),
                     ("MONTANTE_4_65", 1869.0, 1934.0), ("MONTANTE_5_54", 2382.0, 2436.0),
                     ("BATTUTA_DX_36", 2766.0, 2802.0)]:
    B(f"LES_{nome}", **LAM, x0=x0, y0=540.0, z0=0.0, x1=x1, y1=558.0, z1=2080.0)

# ---- lesene sporgenti 30 x 60 (4, H2080, sporgono 19 oltre le ante)
for nome, x in [("SX", 6.0), ("CSX", 903.0), ("CDX", 1869.0), ("DX", 2766.0)]:
    B(f"LESENA_{nome}_30x60", **LAM, x0=x, y0=558.0, z0=0.0, x1=x + 30.0,
      y1=618.0, z1=2080.0)

# ---- fascia frontale sopra le ante (z 2055..2080) e staffa posteriore a soffitto
B("FASCIA_sup_frontale_sp18", **LAM, x0=36.0, y0=Y_ANTA[0], z0=2055.0,
  x1=2766.0, y1=Y_ANTA[1], z1=2080.0)
B("STAFFA_sup_posteriore_sp18", **LAM, x0=36.0, y0=18.0, z0=2045.5,
  x1=2766.0, y1=36.0, z1=2080.0)

# ---- LED INCASSATI negli scassi 9x5 del disegno (checkpoint Matteo 03/09).
# 4 frontali nelle lesene (y 606..610) + 6 interni nei fianchi, uno per
# modulo, aperti verso il vano (y 528..532). Barra 8 larga dentro scasso 9.
for nome, x in [("LESENA_SX", 28.0), ("LESENA_CSX", 903.0),
                ("LESENA_CDX", 1891.0), ("LESENA_DX", 2766.0)]:
    B(f"LED_{nome}_incassato", **LED, x0=x, y0=606.0, z0=30.0,
      x1=x + 8.0, y1=610.0, z1=2050.0)
for nome, x in [("MODA", 366.0), ("MODB", 850.0), ("MODC", 1363.0),
                ("MODD", 1431.0), ("MODE", 1944.0), ("MODF", 2428.0)]:
    B(f"LED_{nome}_incassato", **LED, x0=x, y0=528.0, z0=30.0,
      x1=x + 8.0, y1=532.0, z1=2030.0)

data = {
    "titolo": "ARMADIO CAMERA MASTER 026-A011 sol.C - VOLUMI (no ferramenta) rev.02",
    "note": "Rev.02 dopo checkpoint Matteo 03/09/2026: niente doppia spalla nei "
            "moduli A/F (ripiani a tutto vano 312), cassettiere da pianta "
            "(accostate al fianco SX del modulo), ante H2050 confermate, "
            "laminato ok per ora, LED INCASSATI nei 10 scassi 9x5 del disegno "
            "(4 nelle lesene frontali + 6 nei fianchi, uno per modulo). "
            "X=0 filo sx struttura (L 2802 dalla pianta sol.C; il prospetto "
            "disegna +14mm per lato: probabile rivestimento parete). "
            "Y=0 filo retro, fronte ante y599, lesene y618. Z=0 pavimento, "
            "H 2080 a soffitto. Pianta disegnata +20 in X sul prospetto: "
            "compensata. 6 ante battenti 350/450x4/350, interno 6 moduli "
            "312/412/412/412/412/312.",
    "materiali": {
        "FIANCO_": "MULTI rivestito tessuto",
        "MOD": "MULTI rivestito tessuto",
        "ANTA_": "MULTI laminato OPACO",
        "LES_": "MULTI laminato OPACO",
        "LESENA_": "MULTI laminato OPACO",
        "FASCIA_": "MULTI laminato OPACO",
        "STAFFA_": "MULTI laminato OPACO",
        "LED_": "STRIP-LED",
    },
    "box": box,
}
with open("volumi.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=1, ensure_ascii=False)
print(f"{len(box)} pezzi -> volumi.json")
