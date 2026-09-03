#!/usr/bin/env python3
"""Volumi mobile ingresso-living 026-A011 — rev.02 dopo audit a 7 agenti.

Sistema del DISEGNO: x=0 a DWG 6632.8 (estremo sx schienale colonna),
y=0 al retro (DWG 3492.9), fronte y=600, z=0 pavimento (DWG 3658.3).
SPECCHIA_X ribalta poi tutto (decisione di Matteo al checkpoint: il mobile
reale e' speculare alla tavola → vetrina a sinistra, colonna a destra).

Fronti quotati (nel disegno): colonna 266 (60..326) + canale 40 (326..366)
+ guardaroba 446.5 (366..812.5) + vetrina 360 (812.5..1172.5). P600, H2080.
Corpo da z80 (5.5 luce piedini + 74.5 zoccolo).
"""
import json

box = []
SPECCHIA_X = True
L_TOT = 1172.5

def B(nome, layer, colore, tinta, x0, y0, z0, x1, y1, z1, materiale=None, ruota_x=None):
    if SPECCHIA_X:
        x0, x1 = L_TOT - x1, L_TOT - x0
    b = {"nome": nome, "layer": layer, "colore": colore, "tinta": tinta,
         "x0": round(x0, 1), "y0": round(y0, 1), "z0": round(z0, 1),
         "x1": round(x1, 1), "y1": round(y1, 1), "z1": round(z1, 1)}
    if materiale:
        b["materiale"] = materiale
    if ruota_x:
        b["ruota_x"] = ruota_x
    box.append(b)

LAM = dict(layer="VOL_LAMINATO", colore=250, tinta="#4a4a48", materiale="MULTI laminato OPACO")
CER = dict(layer="VOL_CERA", colore=8, tinta="#cfc8bb", materiale="MULTI laminato CERA")
VET = dict(layer="VOL_VETRO", colore=140, tinta="#bcdce4", materiale="VETRO stratificato satinato")
LED = dict(layer="VOL_LED", colore=2, tinta="#ffe08a", materiale="STRIP-LED")
DOM = dict(layer="VOL_DOMOTICA", colore=18, tinta="#1f1f22", materiale="DOMOTICA touch")

# ================= COLONNA scarpiera/domotica (fronte 266: 60..326) ======
B("COL_schienale_a_muro_sp18", **LAM, x0=0, y0=0, z0=5.5, x1=326.0, y1=18.0, z1=2080.0)
B("COL_fianco_int_SX_sp18", **CER, x0=60.0, y0=18.0, z0=5.5, x1=78.0, y1=581.0, z1=2080.0)
B("COL_fianco_int_DX_sp18_golaLED", **CER, x0=308.0, y0=18.0, z0=5.5, x1=326.0, y1=581.0, z1=2080.0)
B("COL_fondo_sp18", **CER, x0=78.0, y0=101.0, z0=80.0, x1=308.0, y1=581.0, z1=98.0)
B("COL_divisorio_sotto_domotica_sp18", **CER, x0=78.0, y0=101.0, z0=1290.5, x1=308.0, y1=581.0, z1=1308.5)
B("COL_ripiano_sopra_domotica_sp18", **CER, x0=78.0, y0=101.0, z0=1491.5, x1=308.0, y1=581.0, z1=1509.5)
B("COL_cielo_sp18", **CER, x0=78.0, y0=101.0, z0=2062.0, x1=308.0, y1=581.0, z1=2080.0)
B("COL_schienale_arretrato_basso_sp18", **CER, x0=78.5, y0=83.0, z0=98.0, x1=307.5, y1=101.0, z1=1290.5)
B("COL_schienale_arretrato_alto_sp18", **CER, x0=78.5, y0=83.0, z0=1509.5, x1=307.5, y1=101.0, z1=2062.0)
for k, z in enumerate((80.0, 1290.5, 1491.5, 2062.0), 1):
    B(f"COL_traverso50_{k}", **CER, x0=78.0, y0=25.5, z0=z, x1=308.0, y1=75.5, z1=z + 18.0)
B("COL_zoccolo_listello_sp18", **LAM, x0=78.0, y0=543.0, z0=5.5, x1=308.0, y1=561.0, z1=80.0)
B("ANTA_scarpiera_270x1218", **LAM, x0=61.5, y0=582.0, z0=80.0, x1=331.0, y1=600.0, z1=1298.0)
B("PANNELLO_domotica_270x198", **LAM, x0=61.5, y0=582.0, z0=1301.0, x1=331.0, y1=600.0, z1=1499.0)
B("DOMOTICA_placca_touch_196x147", **DOM, x0=95.0, y0=600.0, z0=1326.5, x1=291.0, y1=605.0, z1=1473.5)
B("DOMOTICA_scatola_186x137", **DOM, x0=101.3, y0=580.0, z0=1331.5, x1=287.3, y1=600.0, z1=1468.5)
B("PANNELLO_sup_colonna_270x575", **LAM, x0=61.5, y0=582.0, z0=1502.0, x1=331.0, y1=600.0, z1=2077.0)
# ripiani scarpiera INCLINATI 23.58 gradi (sviluppo 500, scendono verso il
# fronte: davanti-basso 263.1/590.6/918.1, dietro-alto 479.6/807.1/1134.6)
for k, cz in enumerate((371.35, 698.85, 1026.35), 1):
    B(f"COL_ripiano_scarpiera{k}_inclinato", **CER, x0=78.5, y0=89.6, z0=cz - 9.0,
      x1=307.5, y1=589.6, z1=cz + 9.0, ruota_x=-23.58)

# ================= CANALE montante 40 (326..366) =========================
B("MONT_fronte_40_H2080", **LAM, x0=326.0, y0=533.0, z0=0.0, x1=366.0, y1=551.0, z1=2080.0)
B("MONT_tassello_retro_40x18", **LAM, x0=326.0, y0=18.0, z0=5.5, x1=366.0, y1=36.0, z1=2080.0)

# ================= GUARDAROBA (vano 366..812.5) ==========================
B("GUA_fianco_int_SX_sp18_golaLED", **CER, x0=366.0, y0=18.0, z0=5.5, x1=384.0, y1=581.0, z1=2080.0)
B("GUA_fianco_int_DX_sp18", **CER, x0=794.5, y0=18.0, z0=5.5, x1=812.5, y1=581.0, z1=2080.0)
B("GUA_schienale_sp18", **LAM, x0=366.0, y0=0, z0=5.5, x1=812.5, y1=18.0, z1=2080.0)
B("GUA_fondo_sp18", **CER, x0=384.0, y0=18.0, z0=80.0, x1=794.5, y1=581.0, z1=98.0)
B("GUA_ripiano_intermedio_sp18", **CER, x0=384.0, y0=18.0, z0=583.5, x1=794.5, y1=581.0, z1=601.5)
B("GUA_cielo_sp18", **CER, x0=384.0, y0=18.0, z0=2062.0, x1=794.5, y1=581.0, z1=2080.0)
B("GUA_zoccolo_listello_sp18", **LAM, x0=384.0, y0=543.0, z0=5.5, x1=794.5, y1=561.0, z1=80.0)
B("ANTA_guardaroba_450x1997", **LAM, x0=361.0, y0=582.0, z0=80.0, x1=811.0, y1=600.0, z1=2077.0)

# ================= VETRINA libreria (812.5..1172.5) ======================
B("VETR_montante_SX_30_P600", **LAM, x0=812.5, y0=0, z0=5.5, x1=842.5, y1=600.0, z1=2080.0)
B("VETR_montante_DX_30_P300", **LAM, x0=1142.5, y0=300.0, z0=5.5, x1=1172.5, y1=600.0, z1=2080.0)
B("VETR_fondo_sp30_gola", **LAM, x0=842.5, y0=300.0, z0=80.0, x1=1142.5, y1=590.0, z1=110.0)
B("VETR_cappello_sp30_gola", **LAM, x0=842.5, y0=300.0, z0=2050.0, x1=1142.5, y1=590.0, z1=2080.0)
for k, z in enumerate((394.0, 720.0, 1150.0, 1540.0), 1):
    B(f"VETR_ripiano{k}_sp30", **LAM, x0=843.5, y0=304.0, z0=z, x1=1141.5, y1=556.3, z1=z + 30.0)
B("VETR_vetro_satinato_sp8", **VET, x0=834.5, y0=558.3, z0=102.0, x1=1148.5, y1=566.3, z1=2056.0)
B("VETR_zoccolo_ant_sp18", **LAM, x0=842.5, y0=552.0, z0=5.5, x1=1142.5, y1=570.0, z1=80.0)
B("VETR_zoccolo_post_sp18", **LAM, x0=842.5, y0=320.0, z0=5.5, x1=1142.5, y1=338.0, z1=80.0)

# ================= LED ===================================================
B("LED_lama_colonna_basso", **LED, x0=308.0, y0=531.1, z0=98.0, x1=315.9, y1=534.9, z1=1290.5)
B("LED_lama_colonna_alto", **LED, x0=308.0, y0=531.1, z0=1509.5, x1=315.9, y1=534.9, z1=2062.0)
B("LED_lama_guardaroba", **LED, x0=376.1, y0=531.1, z0=98.0, x1=384.0, y1=534.9, z1=2062.0)
B("LED_zoccolo_colonna", **LED, x0=78.0, y0=569.1, z0=80.0, x1=308.0, y1=572.9, z1=87.9)
B("LED_zoccolo_guardaroba", **LED, x0=384.0, y0=569.1, z0=80.0, x1=794.5, y1=572.9, z1=87.9)
B("LED_zoccolo_vetrina", **LED, x0=842.5, y0=578.1, z0=80.0, x1=1142.5, y1=581.9, z1=87.9)

data = {
    "titolo": "MOBILE INGRESSO-LIVING 026-A011 rev.03 - VOLUMI (no ferramenta)",
    "note": "Rev.03: rev.02 + correzioni AGENTE FALEGNAME (piani colonna fermati allo schienale arretrato y101 con traversi in appoggio sui fianchi; ripiani -2mm di luce per l'infilata: vetrina 298, scarpiera 229; 2mm aria ripiani-vetro). SUE SEGNALAZIONI APERTE per Matteo: gola cappello vetro da portare a 18 per montaggio (e larghezza 9-10 se stratificato 44.1); montante canale disegnato a terra z0 H2080 senza registro (tenuto come da tavola); piedini H52 vs luci 5.5/74.5; cerniere a filo pilastri (servono cerniere apertura parallela?); varco 60x563 lato fascia esterna colonna non quotata; vetrina senza schienale (bifacciale voluta?); anta 450x1997 sp18 rischio imbarcamento. Rev.02 da audit a 7 agenti + checkpoint Matteo 03/09/2026. "
            "SPECCHIATO come da indicazione di Matteo: vetrina a sinistra, "
            "colonna scarpiera/domotica a destra (la tavola disegna l'opposto; "
            "internamente non e' specchiata: rot 270 pura, det +1). "
            "Ripiani scarpiera INCLINATI 23.58 gradi (ruota_x). Zoccoli a "
            "listello arretrati (colonna 39 dal filo ante, vetrina 30/20, "
            "guardaroba NON misurabile: copiato dalla colonna, DA CONFERMARE). "
            "Vetrina col CAPPELLO della sez. B-B' e vetro H1954 (il frontale "
            "mostra in alternativa un ripiano a z1970 e vetro H1874: DA "
            "CONFERMARE quale). Doppio schienale colonna con intercapedine "
            "impianti 65. Anta scarpiera 270x1218 e anta guardaroba 450x1997 "
            "(sp18 per analogia, cerniere opposte tra loro; nel mobile "
            "specchiato: scarpiera cerniere DX, guardaroba cerniere SX). "
            "Pannello domotica con placca touch sporgente 5 e scatola "
            "retrostante. Apribilita' pannelli domotica/superiore non "
            "determinabile dal disegno. Tubo appenderia NON disegnato. "
            "Ferramenta esclusa: piedini H52, cerniere, maniglie+serrature "
            "(2), ringhierine Hafele 812.26.610, battute fermascarpe, perni "
            "reggipiano. Fascia x sinistra del disegno 0..61.5 (fianco "
            "esterno colonna): spessore non misurabile, non modellata.",
    "materiali": {},
    "box": box,
}
with open("volumi.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=1, ensure_ascii=False)
print(f"{len(box)} pezzi -> volumi.json (SPECCHIA_X={SPECCHIA_X})")
