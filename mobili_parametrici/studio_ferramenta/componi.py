# -*- coding: utf-8 -*-
"""COMPONI v2 — genera un mobile STP da zero applicando il libro delle regole.

Novita' v2 (richieste Matteo 23/07):
  - BASETTE cerniera forate sul fianco: 2xØ5x13 a 20 e 52 dal filo davanti,
    alla quota esatta di ogni tazza (rilievo armadio V: 30 basette)
  - scelta cerniera automatica: OL = X + B - H (Blum CLIP top 110):
    X=11 battuta, X=1.5 mezza battuta, X=-7.5 filo; B=5 (bottega); H basetta 0/3/9
  - blocchi 3D FERRAMENTA_* con CODICE nel nome + LISTA FERRAMENTA a fine giro

Convenzioni: X = larghezza (0..L), Y = profondita' (0 = FRONTE), Z = altezza (0 = terra).
Uso: freecadcmd componi.py
"""
import json
import os
from collections import Counter

import FreeCAD as App
import Part
from FreeCAD import Vector

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_STP = os.path.join(BASE, "MOBILE_DEMO.stp")
OUT_JSON = os.path.join(BASE, "MOBILE_DEMO_fori.json")
OUT_LISTA = os.path.join(BASE, "LISTA_FERRAMENTA.txt")

# ---------------- SPEC ----------------
L, P, H = 900.0, 560.0, 2000.0
SP = 25.0
SP_SCHIENA = 18.0
SP_ANTA = 18.0
GIOCO = 3.0
Z_RIP_FISSO = 585.0
Z_RIP_RAFIX = 1200.0
NL = 450.0
ALT_M = 63.0
SORMONTO = 16.0     # copertura anta sul fianco (scelta di progetto)

pannelli = {}
fori = []
blocchi = []        # ferramenta 3D: (label, shape)
lista = Counter()   # codice -> qta

def pan(nome, x0, y0, z0, x1, y1, z1):
    pannelli[nome] = (x0, y0, z0, x1, y1, z1)

def foro(pannello, fam, dia, prof, base, direz):
    fori.append({"pannello": pannello, "fam": fam, "dia": dia, "prof": prof,
                 "base": [round(v, 2) for v in base], "dir": list(direz)})

_n_blocchi = Counter()

def blocco(label, shape, codice, descr):
    _n_blocchi[label] += 1
    blocchi.append((f"{label}_{_n_blocchi[label]:02d}", shape))
    lista[(codice, descr)] += 1

# ---------------- SCELTA CERNIERA (Blum CLIP top 110: OL = X + B - H) ----------------
def scegli_cerniera(sp_anta, sormonto, B=5.0):
    if sp_anta > 26:
        return {"tipo": "porta spessa 95", "cod": "71B9550", "basetta": "175H7100",
                "B": B, "H": 0.0, "OL": sormonto, "nota": "serie 95 porte spesse: verificare"}
    if sormonto <= 0:
        X, tipo, cod = -7.5, "filo (inset)", "71B3750"
    elif sormonto <= 10:
        X, tipo, cod = 1.5, "mezza battuta", "71B3650"
    else:
        X, tipo, cod = 11.0, "battuta piena", "71B3550"
    # H per centrare il sormonto richiesto (basette H disponibili 0/3/9)
    H_ideale = X + B - sormonto
    Hd = min((0.0, 3.0, 9.0), key=lambda h: abs(h - H_ideale))
    OL = X + B - Hd
    basetta = "175H3100" if Hd == 0 else ("175H7130" if Hd == 3 else "175H7190")
    return {"tipo": tipo, "cod": cod, "basetta": basetta, "B": B, "H": Hd, "OL": OL,
            "nota": f"OL ottenuto {OL} vs richiesto {sormonto}"}

CERN = scegli_cerniera(SP_ANTA, SORMONTO)

# ---------------- CARCASSA ----------------
pan("01_Fianco_SX", 0, 0, 0, SP, P, H)
pan("02_Fianco_DX", L - SP, 0, 0, L, P, H)
pan("03_Fondo", SP, 0, 0, L - SP, P, SP)
pan("04_Cielo", SP, 0, H - SP, L - SP, P, H)
pan("05_Ripiano_fisso", SP, 0, Z_RIP_FISSO, L - SP, P, Z_RIP_FISSO + SP)
pan("06_Ripiano_rafix", SP, 0, Z_RIP_RAFIX, L - SP, P, Z_RIP_RAFIX + SP)
pan("07_Schiena", SP, P - SP_SCHIENA, SP, L - SP, P, H - SP)

# ---------------- SPINE ----------------
def distribuisci(lung, passo_min=110.0, passo_max=150.0, bordo=32.0):
    utile = lung - 2 * bordo
    n = max(2, int(round(utile / ((passo_min + passo_max) / 2))) + 1)
    return [bordo + i * utile / (n - 1) for i in range(n)]

for portato_nome, z0 in (("03_Fondo", 0.0), ("04_Cielo", H - SP), ("05_Ripiano_fisso", Z_RIP_FISSO)):
    zm = z0 + SP / 2
    for y in distribuisci(P):
        foro("01_Fianco_SX", "spina_faccia", 8.0, 13.0, (SP, y, zm), (-1, 0, 0))
        foro(portato_nome, "spina_costa", 8.0, 29.0, (SP, y, zm), (1, 0, 0))
        foro("02_Fianco_DX", "spina_faccia", 8.0, 13.0, (L - SP, y, zm), (1, 0, 0))
        foro(portato_nome, "spina_costa", 8.0, 29.0, (L - SP, y, zm), (-1, 0, 0))
        lista[("SPINA_D8X30", "Spina legno Ø8x30")] += 2

ym = P - SP_SCHIENA / 2
for z in distribuisci(H - 2 * SP, 200, 260, 60):
    zz = SP + z
    foro("01_Fianco_SX", "spina_faccia", 8.0, 13.0, (SP, ym, zz), (-1, 0, 0))
    foro("07_Schiena", "spina_costa", 8.0, 29.0, (SP, ym, zz), (1, 0, 0))
    foro("02_Fianco_DX", "spina_faccia", 8.0, 13.0, (L - SP, ym, zz), (1, 0, 0))
    foro("07_Schiena", "spina_costa", 8.0, 29.0, (L - SP, ym, zz), (-1, 0, 0))
    lista[("SPINA_D8X30", "Spina legno Ø8x30")] += 2

# ---------------- RIPIANO SU GIUNZIONE A BARILOTTO (kit Pavanello, "rafix" di bottega) ----------------
# Sede barilotto Ø14x15 in faccia a 21 dal bordo (regola blindata, 126 sedi reali).
# Perno M6x7x36 I20 avvitato nella bussola M6x13 sul fianco, passaggio Ø8 in costa.
lavorazioni_extra = []   # (pannello, shape gia' posizionata) da scavare (per blocchi con lavorazione)
for x_acc, fianco, verso in ((SP, "01_Fianco_SX", 1), (L - SP, "02_Fianco_DX", -1)):
    for y in (65.0, P - SP_SCHIENA - 65.0):
        xs = x_acc + verso * 21.0
        zm = Z_RIP_RAFIX + SP / 2
        # sede barilotto nel ripiano (dal sotto)
        foro("06_Ripiano_rafix", "barilotto_sede", 14.0, 15.0, (xs, y, Z_RIP_RAFIX), (0, 0, 1))
        # passaggio perno Ø8 in costa del ripiano, fino oltre il barilotto
        foro("06_Ripiano_rafix", "perno_passaggio", 8.0, 26.0, (x_acc, y, zm), (verso, 0, 0))
        # bussola M6x13 nel fianco: foro Ø13x14.4 (punta dedicata con svasatore,
        # codificata in macchina come foro da 13 - regola Matteo 23/07)
        foro(fianco, "bussola_pilota", 13.0, 14.4, (x_acc, y, zm), (-verso, 0, 0))
        # blocchi coi codici veri
        blocco("FERRAMENTA_BARILOTTO_00475143",
               Part.makeCylinder(7.0, 14.5, Vector(xs, y, Z_RIP_RAFIX + 0.2), Vector(0, 0, 1)),
               "00475143", "Barilotto senza bordo Ø14 SL18 zincato - LIVENZA (Pavanello)")
        blocco("FERRAMENTA_PERNO_00491334",
               Part.makeCylinder(3.5, 36.0, Vector(x_acc, y, zm), Vector(verso, 0, 0)),
               "00491334", "Perno corto barilotto M6x7x36 I20 - EMUCA (Pavanello)")
        blocco("FERRAMENTA_BUSSOLA_00444828",
               Part.makeCylinder(6.4, 13.0, Vector(x_acc, y, zm), Vector(-verso, 0, 0)),
               "00444828", "Bussola esagono ferro/zinco M6x13 - PAVANELLO (foro 13x14.4)")
        lista[("00475372", "Grano 8MAx10 croce zincato - LIVENZA (Pavanello)")] += 1

# ---------------- SISTEMA 32 ----------------
for fianco, x_f, verso in (("01_Fianco_SX", SP, -1), ("02_Fianco_DX", L - SP, 1)):
    for y in (37.0, P - 37.0):
        z = 1296.0
        while z <= 1808.0:
            foro(fianco, "sistema32", 5.0, 13.0, (x_f, y, z), (verso, 0, 0))
            z += 32.0

# ---------------- ANTE con CERNIERE + BASETTE ----------------
# Blocco CAD vero Häfele Metalla 110 (311.90.500, posizione chiusa) da teccad:
# tazza Ø35 con asse in (X+7.5, Z0) locale, faccia anta = piano Y=0, braccio verso +X.
# libreria blocchi CAD reali (indice codice -> file)
LIBRERIA = json.load(open(os.path.join(BASE, "blocchi_libreria.json"), encoding="utf-8"))

def carica_blocco(codice, vol_min=1.0):
    """Carica un blocco della libreria come Compound (solidi sopra vol_min)."""
    v = LIBRERIA.get(codice)
    if not v:
        return None
    path = os.path.join(BASE, v["file"])
    if not os.path.exists(path):
        return None
    import Import as _I
    _d = App.newDocument("blk_" + codice.replace(".", "_"))
    _I.insert(path, _d.Name)
    sol = [o.Shape.copy() for o in _d.Objects
           if hasattr(o, "Shape") and o.Shape.Solids and o.Shape.Volume > vol_min]
    App.closeDocument(_d.Name)
    return Part.makeCompound(sol) if sol else None

# Modello 3D cerniera: uso il blocco Metalla in posizione CHIUSA (dettagliato e
# montabile), perche' il CAD Blum del singolo prodotto arriva solo in posizione APERTA
# (braccio disteso, non montabile a mobile chiuso). Il codice ordinato resta Blum.
cern_blocco = carica_blocco("311.90.500", vol_min=3.0) or carica_blocco(CERN["cod"], vol_min=1.0)
basetta_blocco = None   # la basetta e' inclusa nel corpo cerniera

# --- montaggio cerniera Blum: tazza blocco (asse Z, bocca a P0) -> foro anta ---
# convenzione blocco 71B3xxx: bocca tazza P0=(-6.5,0,51.3), asse Z, braccio +Y.
# mappa assi: anta Z->Y, fianco Y->X, terzo X->Z (ciclica). Bocca +Z -> +Y (guarda
# riferimenti nel blocco: bocca coppa (asse Z, verso +Z) e punto basetta (viti a Y~50).
# Montaggio a 3 riferimenti: coppa (asse+punto) nel foro anta + basetta verso il fianco
# -> determina il VERSO senza ambiguita' (il corpo resta dietro l'anta, verso l'interno).
CB = Vector(-6.5, 0.0, 51.3)      # bocca coppa blocco
AB = Vector(0.0, 0.0, 1.0)        # asse coppa blocco (dalla bocca verso il fondo = -AB)
BB = Vector(-15.5, 50.7, 38.3)    # punto basetta blocco (media viti)

def _rot_from_to(a, b):
    from FreeCAD import Rotation
    import math
    a = Vector(a); b = Vector(b)
    a.normalize(); b.normalize()
    d = max(-1.0, min(1.0, a.dot(b)))
    if d > 0.999999:
        return Rotation()
    if d < -0.999999:
        ax = a.cross(Vector(1, 0, 0))
        if ax.Length < 1e-6:
            ax = a.cross(Vector(0, 1, 0))
        ax.normalize()
        return Rotation(ax, 180)
    ax = a.cross(b)
    ax.normalize()
    return Rotation(ax, math.degrees(math.acos(d)))

def riferimenti_blocco(shape):
    """Auto-rileva coppa (bocca CB + asse AB verso il fondo) e corpo (BB=baricentro)."""
    best = None
    for f in shape.Faces:
        s = f.Surface
        if s.__class__.__name__ != "Cylinder":
            continue
        if 16.0 <= s.Radius <= 19.0:
            if best is None or f.Area > best[0]:
                best = (f.Area, s.Center, s.Axis)
    if best is None:
        return None
    _, c, ax = best
    ax = Vector(ax); ax.normalize()
    # bocca coppa = estremo del bbox della faccia lungo +ax (lato aperto, verso l'esterno)
    bb = shape.BoundBox
    # scegli come "bocca" il lato dell'asse dove la coppa e' aperta: usa il centro faccia
    CBl = Vector(c)
    ABl = ax                     # dalla bocca verso il fondo = -ABl (convenzione sotto)
    BBl = shape.CenterOfMass
    return CBl, ABl, BBl

def monta_cerniera(shape, Cm, Am, Bm):
    """Allinea coppa (asse) al foro anta e il corpo (baricentro) verso il fianco.
    Cm=bocca coppa target, Am=asse coppa (bocca->fondo, -Y), Bm=punto verso il fianco."""
    from FreeCAD import Rotation, Placement
    import math
    rif = riferimenti_blocco(shape)
    if rif is None:
        return shape.copy()
    CBl, ABl, BBl = rif
    Amn = Vector(Am); Amn.normalize()
    # l'asse coppa del blocco (ABl) deve diventare l'asse target (Am), con il corpo
    # (baricentro) dal lato giusto: se il baricentro e' verso -ABl, uso -ABl.
    corpo_dir = (BBl - CBl)
    if corpo_dir.dot(ABl) < 0:
        asse_blocco = ABl.multiply(-1)
    else:
        asse_blocco = ABl
    # ma l'asse coppa deve puntare bocca->fondo = Am; la bocca e' opposta al corpo.
    # affondamento coppa = verso il corpo NON e' garantito; usiamo: asse coppa target Am,
    # e allineiamo -asse_blocco (verso la bocca) all'opposto... semplice: allinea l'asse
    # e poi ruota per mettere il corpo verso Bm.
    R1 = _rot_from_to(ABl, Amn.multiply(-1) if corpo_dir.dot(ABl) > 0 else Amn)
    def proj(v):
        return Vector(v) - Amn * (Vector(v).dot(Amn))
    p_bb = proj(R1.multVec(BBl - CBl))
    p_vm = proj(Bm - Cm)
    if p_bb.Length > 1e-6 and p_vm.Length > 1e-6:
        p_bb.normalize(); p_vm.normalize()
        ang = math.degrees(math.atan2(p_bb.cross(p_vm).dot(Amn),
                                      max(-1.0, min(1.0, p_bb.dot(p_vm)))))
        R2 = Rotation(Amn, ang)
    else:
        R2 = Rotation()
    Rtot = R2.multiply(R1)
    plc = Placement(Cm - Rtot.multVec(CBl), Rtot)
    s = shape.copy()
    s.transformShape(plc.toMatrix())
    return s
ANTA_H = H - 2 * GIOCO
LUCE = L - 2 * SP
ANTA_TOT = LUCE + 2 * CERN["OL"]          # copertura data dalla cerniera scelta
ANTA_L = (ANTA_TOT - GIOCO) / 2
X0_SX = SP - CERN["OL"]
N_CERN = 2 if ANTA_H < 900 else 3 if ANTA_H < 1600 else 4 if ANTA_H < 2000 else 5

for nome, x0, lato, fianco, x_f, verso in (
        ("08_Anta_SX", X0_SX, "SX", "01_Fianco_SX", SP, -1),
        ("09_Anta_DX", X0_SX + ANTA_L + GIOCO, "DX", "02_Fianco_DX", L - SP, 1)):
    pan(nome, x0, -GIOCO - SP_ANTA, GIOCO, x0 + ANTA_L, -GIOCO, GIOCO + ANTA_H)
    x_tazza = (x0 + 22.5) if lato == "SX" else (x0 + ANTA_L - 22.5)
    segno = 1 if lato == "SX" else -1
    for i in range(N_CERN):
        z = GIOCO + 100.0 + i * (ANTA_H - 200.0) / (N_CERN - 1)
        y_int = -GIOCO
        # tazza + viti sull'anta
        foro(nome, "cerniera_tazza", 35.0, 13.0, (x_tazza, y_int, z), (0, -1, 0))
        for dz in (-22.5, 22.5):
            foro(nome, "cerniera_vite", 5.0, 13.0,
                 (x_tazza + segno * 9.5, y_int, z + dz), (0, -1, 0))
        # BASETTA sul fianco: 2xØ5x13 a 20 e 52 dal filo davanti, quota z tazza
        for yb in (20.0, 52.0):
            foro(fianco, "basetta_vite", 5.0, 13.0, (x_f, yb, z), (verso, 0, 0))
        # cerniera segnaposto REALISTICA e ben orientata (verso garantito): coppa svasata
        # + braccio a gomito verso il fianco + basetta cruciforme sul fianco.
        coppa = Part.makeCylinder(17.5, 12.0, Vector(x_tazza, -1.0, z), Vector(0, -1, 0))
        collo = Part.makeCylinder(9.0, 18.0, Vector(x_tazza, -1.0, z), Vector(0, 1, 0))
        x0b = min(x_f, x_tazza) - 2.0
        braccio = Part.makeBox(abs(x_f - x_tazza) + 8.0, 34.0, 13.0, Vector(x0b, 2.0, z - 6.5))
        bas = Part.makeBox(15.0, 42.0, 11.0,
                           Vector(x_f if verso < 0 else x_f - 15.0, 15.0, z - 5.5))
        cern_s = coppa.fuse(collo).fuse(braccio)
        blocco(f"FERRAMENTA_CERNIERA_{CERN['cod']}", cern_s,
               CERN["cod"], f"Cerniera {CERN['tipo']} 71B (verso montaggio; CAD reale in blocchi_blum)")
        blocco(f"FERRAMENTA_BASETTA_{CERN['basetta']}", bas,
               CERN["basetta"], f"Basetta {CERN['basetta']} H={CERN['H']:g}")

lista[(CERN["cod"], f"Cerniera {CERN['tipo']} (scelta a regola)")] += N_CERN * 2
lista[(CERN["basetta"], f"Basetta {CERN['basetta']} H={CERN['H']:g}")] += N_CERN * 2

# CAMPIONE: il blocco CAD Blum reale (dettagliato) posato accanto al mobile, a sinistra,
# cosi' e' visibile il modello vero (arriva in posizione aperta dal configuratore Blum).
_camp = carica_blocco(CERN["cod"], vol_min=1.0)
if _camp is not None:
    _bb = _camp.BoundBox
    _camp = _camp.copy()
    _camp.translate(Vector(-300.0 - _bb.XMin, -_bb.YMin, 200.0 - _bb.ZMin))
    blocco(f"CAMPIONE_CERNIERA_{CERN['cod']}", _camp,
           CERN["cod"], f"CAMPIONE blocco CAD Blum {CERN['cod']} (a lato mobile)")

# ---------------- CASSETTO LEGRABOX M ----------------
LW = LUCE
fondo_l = LW - 35.0
fondo_p = NL - 10.0
sch_l = LW - 38.0
zb = SP + 15.0
pan("10_LEGRABOX_Fondo", (L - fondo_l) / 2, 30.0, zb, (L + fondo_l) / 2, 30.0 + fondo_p, zb + 18.0)
pan("11_LEGRABOX_Schienale", (L - sch_l) / 2, 30.0 + fondo_p, zb + 18.0,
    (L + sch_l) / 2, 30.0 + fondo_p + 18.0, zb + 18.0 + ALT_M)

fx0, fy0 = (L - fondo_l) / 2, 30.0
for dx in (49.5, fondo_l - 49.5):
    for dy in (23.75, 23.75 + 128.0):
        foro("10_LEGRABOX_Fondo", "legrabox_fondo", 5.0, 13.0, (fx0 + dx, fy0 + dy, zb), (0, 0, 1))
sx0 = (L - sch_l) / 2
for dx in (9.0, sch_l - 9.0):
    for dz in (19.4, 51.4):
        foro("11_LEGRABOX_Schienale", "legrabox_schienale", 5.0, 13.0,
             (sx0 + dx, 30.0 + fondo_p, zb + 18.0 + dz), (0, 1, 0))
# --- CASSETTO LEGRABOX montato: guide + sponde + frontale (tutto verso l'INTERNO) ---
ALT_FIANCO_M = 90.5           # altezza fianco metallo LEGRABOX tipo M
y_cass = 30.0                 # fronte cassetto (dietro il frontale)
z_guida = zb + 18.0           # le guide/sponde poggiano sul piano del fondo cassetto
xf_sx, xf_dx = (L - fondo_l) / 2, (L + fondo_l) / 2   # bordi del fondo cassetto
for fianco, x_f, verso in (("01_Fianco_SX", SP, -1), ("02_Fianco_DX", L - SP, 1)):
    for dy in (37.0, 293.0):
        foro(fianco, "legrabox_guida", 5.0, 13.0, (x_f, 30.0 + dy, zb + 15.0), (verso, 0, 0))
    # GUIDA a L sulla faccia INTERNA del fianco (verso -verso = dentro), lunga NL
    x_int = x_f + (13.0 if verso < 0 else -13.0)       # 13mm verso l'interno
    parete = Part.makeBox(13.0, NL, 42.0, Vector(min(x_f, x_int), y_cass, z_guida - 6.0))
    base = Part.makeBox(22.0, NL, 6.0,
                        Vector(x_f if verso < 0 else x_f - 22.0, y_cass, z_guida - 6.0))
    blocco("FERRAMENTA_GUIDA_LEGRABOX_750.4001S", Part.makeCompound([parete, base]),
           "750.4001S", "Coppia guide LEGRABOX BLUMOTION 40kg est. totale")
# SPONDE metalliche del cassetto sui bordi del FONDO (altezza M), lunghe NL
for xb, dxo in ((xf_sx, 0.0), (xf_dx, -13.0)):
    sponda = Part.makeBox(13.0, NL, ALT_FIANCO_M, Vector(xb + dxo, y_cass, z_guida))
    blocco("FERRAMENTA_LEGRABOX_SPONDA_M", sponda,
           "ZC7M0U0S", "Sponda LEGRABOX altezza M (parete cassetto) - Blum")
lista[("LEGRABOX_SCHIENALE_M", "Schienale legno M h63 (LW-38)")] += 1
lista[("LEGRABOX_FONDO", "Fondo legno (LW-35 x NL-10)")] += 1
lista[("ZC7M0U0S", "Coppia sponde LEGRABOX altezza M")] += 1

# FRONTALE del cassetto: pannello a filo davanti al box, gioco 3
fr_l = LUCE - 2 * GIOCO
pan("12_LEGRABOX_Frontale", (L - fr_l) / 2, y_cass - 19.0, zb - 6.0,
    (L + fr_l) / 2, y_cass - 1.0, z_guida + ALT_FIANCO_M + 20.0)

# ---------------- BASI BONE ----------------
for cx in (66.0, LUCE - 66.0):
    for cy in (150.0, P - SP_SCHIENA - 160.0):
        for dx in (-16.0, 16.0):
            for dy in (-16.0, 16.0):
                foro("03_Fondo", "bone_base", 5.0, 13.0, (SP + cx + dx, cy + dy, 0.0), (0, 0, 1))
        blocco("FERRAMENTA_PIEDINO_BONE_00411431",
               Part.makeCylinder(24.0, 20.0, Vector(SP + cx, cy, -20.0), Vector(0, 0, 1)),
               "00411431", "Piedino BONE Ø48 H.150 (148-190) - Pavanello")
        lista[("00411448", "Base BONE Ø48 montaggio a vite - Pavanello")] += 1

# ---------------- SEDI REKORD ----------------
for fianco, xm in (("01_Fianco_SX", SP / 2), ("02_Fianco_DX", L - SP / 2)):
    for y in (80.0, P - 80.0):
        foro(fianco, "rekord", 12.0, 60.0, (xm, y, 0.0), (0, 0, 1))
        blocco("FERRAMENTA_PIEDINO_REKORD_00650984",
               Part.makeCylinder(14.0, 25.0, Vector(xm, y, -25.0), Vector(0, 0, 1)),
               "REKORD_00650984", "Piedino REKORD TECH - Pavanello 00650984")

# viti basette e tazze in lista
lista[("VITE_EURO_D5X13", "Viti fissaggio (tazze+basette+guide)")] += sum(
    1 for f in fori if f["fam"] in ("cerniera_vite", "basetta_vite", "legrabox_guida"))

# ---------------- COSTRUZIONE SOLIDI ----------------
doc = App.newDocument("demo")
riepilogo = {}
for nome, (x0, y0, z0, x1, y1, z1) in pannelli.items():
    box = Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))
    cils = []
    for f in fori:
        if f["pannello"] != nome:
            continue
        d = Vector(*f["dir"])
        base = Vector(*f["base"]) - d * 0.2
        cils.append(Part.makeCylinder(f["dia"] / 2.0, f["prof"] + 0.2, base, d))
        riepilogo[f["fam"]] = riepilogo.get(f["fam"], 0) + 1
    if cils:
        box = box.cut(Part.makeCompound(cils))
    for pan_lav, sh_lav in lavorazioni_extra:
        if pan_lav == nome:
            box = box.cut(sh_lav)
            riepilogo["lavorazione_blocco"] = riepilogo.get("lavorazione_blocco", 0) + 1
    o = doc.addObject("Part::Feature", "p")
    o.Shape = box
    o.Label = nome

for label, sh in blocchi:
    o = doc.addObject("Part::Feature", "f")
    o.Shape = sh
    o.Label = label

import Import
Import.export(doc.Objects, OUT_STP)
json.dump({"spec": {"L": L, "P": P, "H": H, "gioco": GIOCO, "NL": NL,
                    "cerniera": CERN, "n_cerniere_per_anta": N_CERN},
           "fori": fori}, open(OUT_JSON, "w", encoding="utf-8"), indent=1)

righe = [f"LISTA FERRAMENTA - MOBILE_DEMO {L:g}x{P:g}x{H:g}",
         f"cerniera scelta: {CERN['tipo']} {CERN['cod']} + basetta {CERN['basetta']} "
         f"(B={CERN['B']:g} H={CERN['H']:g} OL={CERN['OL']:g})", "-" * 60]
for (cod, descr), n in sorted(lista.items()):
    righe.append(f"{n:4d} x {cod:28s} {descr}")
open(OUT_LISTA, "w", encoding="utf-8").write("\n".join(righe))

print("PANNELLI:", len(pannelli), "| BLOCCHI FERRAMENTA:", len(blocchi))
tot = 0
for fam, n in sorted(riepilogo.items()):
    print(f"  {fam:22s} x{n}")
    tot += n
print("FORI TOTALI:", tot)
print("\n".join(righe))
print("SCRITTO", OUT_STP)
