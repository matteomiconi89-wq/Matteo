"""
dxf2tlf_masterwood - dai DXF 3D (3DSOLID, es. "Programmi CNC") ai .TLF
per Masterwood MW315 (PROJECT MW315 WINDOWS), senza aprire nessun software.

COME FUNZIONA
- legge il solido dal DXF (ACIS binario SAB o testuale SAT)
- pannello = bounding box dei vertici (LUNG x LARG x ALT)
- FORI = coppie di cerchi coassiali nell'ACIS (bordo di entrata + fondo):
    asse Z  -> PLANE 0 (piano),   X=x, Y=y
    asse Y  -> PLANE 1 REAR (y=LARG) / PLANE 2 FRONT (y=0), X=x, Y=z
    asse X  -> PLANE 3 LEFT (x=0)  / PLANE 4 RIGHT (x=LUNG), X=y, Y=z
  profondita' = distanza tra i due cerchi; foro passante = ALT + 4
- se i fori verticali entrano tutti da SOTTO il pezzo viene ribaltato
  (y -> LARG-y, z -> ALT-z) e lo segnala nel log
- lavorazioni non a foro (scassi, fresate, profili) NON sono gestite:
  il pezzo viene segnalato nel log, il TLF esce coi soli fori

Mappatura ricavata e VERIFICATA sulle coppie DXF/TLF reali della macchina
(21032 17_18: 031_Fianco_SX_INT, 04_Fianco_DX_INT_A109).
"""

import os
import sys
import math
import datetime
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox

TOL_FACE = 0.05      # un cerchio "sta" su una faccia se dista meno di cosi'
TOL_AXIS = 0.99      # |dot| minimo per considerare l'asse allineato a X/Y/Z
NDEC = 2             # arrotondamento coordinate per raggruppare i cerchi
THROUGH_EXTRA = 4    # foro passante: profondita' = ALT + questo (come MW315)
PROF_FORO_D14 = 15.8 # REGOLA: il foro D14 cieco (RAFIX) va SEMPRE a 15.8


# ========================= estrazione ACIS =================================
# I DXF di AutoCAD portano il corpo ACIS in coordinate LOCALI + un record
# "transform" (immagini degli assi x,y,z per colonne + traslazione): va
# applicato, senno' le rotazioni/traslazioni dell'export si perdono
# (coi pezzi ortogonali non si nota, con gli OBLIQUI raddrizzati si').
def _trasf_punto(tr, p):
    (cx, cy, cz), t = tr
    return (p[0]*cx[0] + p[1]*cy[0] + p[2]*cz[0] + t[0],
            p[0]*cx[1] + p[1]*cy[1] + p[2]*cz[1] + t[1],
            p[0]*cx[2] + p[1]*cy[2] + p[2]*cz[2] + t[2])


def _trasf_dir(tr, n):
    (cx, cy, cz), _t = tr
    return (n[0]*cx[0] + n[1]*cy[0] + n[2]*cz[0],
            n[0]*cx[1] + n[1]*cy[1] + n[2]*cz[1],
            n[0]*cx[2] + n[1]*cy[2] + n[2]*cz[2])


def _leggi_trasf(numeri):
    """12+ numeri del record transform -> ((cx,cy,cz), t) o None se identita'"""
    if len(numeri) < 12:
        return None
    cx, cy, cz, t = numeri[0:3], numeri[3:6], numeri[6:9], tuple(numeri[9:12])
    ident = (abs(cx[0]-1) < 1e-12 and abs(cy[1]-1) < 1e-12
             and abs(cz[2]-1) < 1e-12
             and all(abs(v) < 1e-12 for v in (cx[1], cx[2], cy[0], cy[2],
                                              cz[0], cz[1]))
             and all(abs(v) < 1e-12 for v in t))
    return None if ident else ((cx, cy, cz), t)


def _circles_sab(sab):
    from ezdxf.acis.sab import Decoder
    from ezdxf.acis.const import Tags
    dec = Decoder(sab); dec.read_header()
    pts, circles = [], []
    tr = None
    for rec in dec.read_records():
        if not rec:
            continue
        nm = rec[0].value if isinstance(rec[0].value, str) else ""
        locs = [t.value for t in rec if t.tag == Tags.LOCATION_VEC]
        dirs = [t.value for t in rec if t.tag == Tags.DIRECTION_VEC]
        if nm.startswith("transform") and tr is None:
            numeri = []
            for t in rec:
                if isinstance(t.value, (int, float)):
                    numeri.append(float(t.value))
                elif isinstance(t.value, (tuple, list)):
                    numeri.extend(float(v) for v in t.value)
            tr = _leggi_trasf(numeri)
        elif nm.startswith("point"):
            pts.extend(locs)
        elif "ellipse" in nm and locs and dirs:
            n = dirs[0] if len(dirs) >= 2 else (0, 0, 1)
            maj = dirs[-1]
            r = math.sqrt(maj[0]**2 + maj[1]**2 + maj[2]**2)
            circles.append((tuple(locs[0]), tuple(n), r))
    if tr:
        pts = [_trasf_punto(tr, p) for p in pts]
        circles = [(_trasf_punto(tr, c), _trasf_dir(tr, n), r)
                   for c, n, r in circles]
    return pts, circles


def _circles_sat(sat_lines):
    from ezdxf.acis.sat import parse_sat
    pts, circles = [], []
    tr = None
    for rec in parse_sat(sat_lines).entities:
        try:
            if rec.name == "transform" and tr is None:
                numeri = []
                for v in rec.data:
                    try:
                        numeri.append(float(v))
                    except (TypeError, ValueError):
                        pass
                tr = _leggi_trasf(numeri)
            elif rec.name.startswith("point"):
                pts.append(tuple(float(v) for v in rec.data[:3]))
            elif "ellipse" in rec.name:
                d = rec.data
                c = tuple(float(v) for v in d[0:3])
                n = tuple(float(v) for v in d[3:6])
                maj = [float(v) for v in d[6:9]]
                r = math.sqrt(maj[0]**2 + maj[1]**2 + maj[2]**2)
                circles.append((c, n, r))
        except (ValueError, IndexError):
            continue
    if tr:
        pts = [_trasf_punto(tr, p) for p in pts]
        circles = [(_trasf_punto(tr, c), _trasf_dir(tr, n), r)
                   for c, n, r in circles]
    return pts, circles


def _dist_pt_seg(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    if l2 < 1e-12:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def _biselli(pt, pb, alt, facce_incl):
    """Lati del contorno SOPRA sfalsati rispetto a quelli SOTTO = tagli
    INCLINATI nello spessore (giunti a bisettrice, teste in diagonale).
    Un bisello VERO ha una FACCIA INCLINATA tra i due bordi: senza
    (facce_incl vuote o lontane) e' una BATTUTA/gradino, non un bisello.
    -> [{"t1","t2" bordo sopra, "b1","b2" bordo sotto (versi col fuori a
        sinistra per WRKL), "beta" gradi dallo spessore, "largo_sopra"}]"""
    def segmenti(ps):
        out = []
        for i in range(len(ps)):
            a, b = ps[i], ps[(i + 1) % len(ps)]
            if math.hypot(b[0] - a[0], b[1] - a[1]) >= 30.0:
                out.append((a, b))
        return out

    def shoelace(ps):
        s = 0.0
        for i in range(len(ps)):
            x0, y0 = ps[i]; x1, y1 = ps[(i + 1) % len(ps)]
            s += x0 * y1 - x1 * y0
        return s / 2.0

    cx = sum(p[0] for p in pt) / len(pt)
    cy = sum(p[1] for p in pt) / len(pt)
    ccw = shoelace(pt) > 0
    out = []
    for a, b in segmenti(pt):
        dx, dy = b[0] - a[0], b[1] - a[1]
        ll = math.hypot(dx, dy)
        ux, uy = dx / ll, dy / ll
        best = None
        for c, d in segmenti(pb):
            ex, ey = d[0] - c[0], d[1] - c[1]
            l2 = math.hypot(ex, ey)
            if abs(ux * ey / l2 - uy * ex / l2) > 0.03:    # non paralleli
                continue
            off = abs((c[0] - a[0]) * (-uy) + (c[1] - a[1]) * ux)
            if off > 3.0 * alt:
                continue
            ta = [(p[0] - a[0]) * ux + (p[1] - a[1]) * uy for p in (a, b)]
            tb = [(p[0] - a[0]) * ux + (p[1] - a[1]) * uy for p in (c, d)]
            if min(max(ta), max(tb)) - max(min(ta), min(tb)) < 30.0:
                continue                                   # non sovrapposti
            # si tiene il partner con lo sfalsamento MINIMO: se sotto
            # esiste il gemello identico, il lato NON e' un bisello
            if best is None or off < best[2]:
                best = (c, d, off)
        if not best or best[2] < 0.3:
            continue
        c, d, off = best
        # dev'esserci una FACCIA INCLINATA lungo questo bordo (parallela
        # al lato, col baricentro tra le due linee): senno' e' una battuta
        trovata = False
        for fx, fy, fnx, fny in facce_incl:
            if abs(fnx * ux + fny * uy) > 0.2:      # normale non ⊥ al lato
                continue
            d_lato = abs((fx - a[0]) * (-uy) + (fy - a[1]) * ux)
            if d_lato > off + 2.0:                  # fuori dalla striscia
                continue
            tf = (fx - a[0]) * ux + (fy - a[1]) * uy
            ta_ = [(p[0] - a[0]) * ux + (p[1] - a[1]) * uy for p in (a, b)]
            if min(ta_) - 5 <= tf <= max(ta_) + 5:
                trovata = True
                break
        if not trovata:
            continue
        beta = math.degrees(math.atan2(off, alt))
        nx, ny = -uy, ux
        dist_t = abs((a[0] - cx) * nx + (a[1] - cy) * ny)
        dist_b = abs((c[0] - cx) * nx + (c[1] - cy) * ny)
        # verso col FUORI a sinistra (compensazione lama WRKL): contorno
        # antiorario = interno a sinistra -> si inverte; ordinati cosi'
        # SIA il bordo sopra (t) SIA quello sotto (b)
        tdx, tdy = (dx, dy) if not ccw else (-dx, -dy)
        t1, t2 = a, b
        if (t2[0] - t1[0]) * tdx + (t2[1] - t1[1]) * tdy < 0:
            t1, t2 = t2, t1
        b1, b2 = c, d
        if (b2[0] - b1[0]) * tdx + (b2[1] - b1[1]) * tdy < 0:
            b1, b2 = b2, b1
        out.append({"t1": t1, "t2": t2, "b1": b1, "b2": b2,
                    "beta": round(beta, 2),
                    "largo_sopra": dist_t >= dist_b})
    return out


def _scassi_topologia(solids, rimappa, rimappa_dir, mn, lung, larg, alt):
    """Tasche/scassi dai CONTORNI VERI della topologia ACIS (SAT).
    -> (scassi_sopra, scassi_sotto, fori_via, avvisi) in coord. canoniche.
    Entry: {"cir":True,x,y,r,prof,thru} oppure {"contorno":[(x,y)..],prof,thru}.
    fori_via: fori ciechi da TOGLIERE dalle punte perche' in realta' sono
    il gradino piccolo di uno scasso a gradini (es. FITLOCK D51x4 + D35x6)."""
    import acis_topo
    TOLF = 0.05
    R_FORO = 17.6          # sotto: e' un foro (lo fanno le punte), salta
    avv = []
    fondi_sopra, fondi_sotto = [], []
    bocche_top = []
    sagome_pezzo = []      # profili ESTERNI sagomati (non rettangolari)
    tagli_incl = []        # biselli: tagli con lama INCLINATA (angolo-A)
    archi_xy = []          # centri (x,y,r) dei RACCORDI dei contorni: i loro
                           # cilindri sembrano fori ma non lo sono

    def can_pt(p):
        q = rimappa((p.x - mn[0], p.y - mn[1], p.z - mn[2]))
        return (round(q[0], 3), round(q[1], 3), round(q[2], 3))

    def can_tratti(lo):
        """tratti veri del loop in coordinate canoniche (None se assenti)"""
        tt = lo.get("tratti")
        if not tt:
            return None
        out = []
        for t in tt:
            if t[0] == "L":
                out.append(("L", can_pt(t[1])[:2]))
            else:
                out.append(("A", can_pt(t[1])[:2], can_pt(t[2])[:2], t[3]))
        return out

    for e in solids:
        facce, a2 = acis_topo.tasche_da_solido(e.sat)
        for m in set(a2):
            avv.append(m)
        top_pezzo = None                     # faccia superiore del SOLIDO
        bot_pezzo = None                     # faccia inferiore (anti-bisello)
        facce_incl = []                      # facce INCLINATE (biselli veri)
        for f in facce:
            n = rimappa_dir((f["normale"].x, f["normale"].y, f["normale"].z))
            if abs(n[2]) < 0.99:
                if 0.03 < abs(n[2]) < 0.97:
                    # faccia inclinata nello spessore: candidata bisello;
                    # baricentro e direzione orizzontale della normale
                    lo = max(f["loops"], key=lambda q: q["area"])
                    ps = [can_pt(p)[:2] for p in lo["punti"]]
                    cx = sum(p[0] for p in ps) / len(ps)
                    cy = sum(p[1] for p in ps) / len(ps)
                    nn = math.hypot(n[0], n[1])
                    if nn > 1e-6:
                        facce_incl.append((cx, cy, n[0] / nn, n[1] / nn))
                continue
            for lo in f["loops"]:
                for c, r in lo.get("archi", ()):
                    q = can_pt(c)
                    archi_xy.append((q[0], q[1], round(r, 2)))
            z = can_pt(f["punto"])[2]
            if TOLF < z < alt - TOLF:
                (fondi_sopra if n[2] > 0 else fondi_sotto).append((z, f))
            elif abs(z - alt) < TOLF and n[2] > 0:
                for lo in f["loops"]:
                    if not lo["esterno"]:
                        bocche_top.append(lo)
                    elif (top_pezzo is None
                          or lo["area"] > top_pezzo["area"]):
                        top_pezzo = lo
            elif abs(z) < TOLF and n[2] < 0:
                for lo in f["loops"]:
                    if lo["esterno"] and (bot_pezzo is None
                                          or lo["area"] > bot_pezzo["area"]):
                        bot_pezzo = lo
        # PROFILO del pezzo: se il contorno esterno rientra dal rettangolo
        # (incastri, sagome lavabo, tagli in diagonale...) serve la
        # fresatura di contorno. Si campionano anche i PUNTI MEDI dei lati:
        # una diagonale da spigolo a spigolo non ha vertici interni!
        # NB: NON sui file multi-solido (frontali uniti): li' i bordi
        # interni dei pezzi sono fughe da LAMATA, non sagome
        if top_pezzo and len(solids) == 1:
            punti = [can_pt(p)[:2] for p in top_pezzo["punti"]]
            pb = ([can_pt(p)[:2] for p in bot_pezzo["punti"]]
                  if bot_pezzo is not None else None)
            # BISELLI: lati del contorno sopra sfalsati rispetto a quelli
            # sotto = tagli INCLINATI nello spessore -> lama ad angolo-A
            # (solo se esiste la faccia inclinata: senno' e' una battuta)
            coppie = _biselli(punti, pb, alt, facce_incl) if pb else []
            if coppie:
                tagli_incl.extend(coppie)
                avv.append(f"{len(coppie)} tagli INCLINATI con lama ad "
                           "angolo-A: "
                           + ", ".join(f"{c['beta']:.1f}" for c in coppie)
                           + " gradi dallo spessore")
            # PROFILO: si fresa sul contorno ESTERNO vero del pezzo.
            # Coi biselli: la faccia LARGA (il giro passa FUORI dal
            # bisello, che lo fa la lama inclinata). Senza biselli: il
            # contorno con l'AREA maggiore (una BATTUTA morde la faccia
            # sopra: il filo del pezzo e' quello dell'altra faccia)
            if coppie and all(c["largo_sopra"] for c in coppie):
                rif, rif_p = top_pezzo, punti
            elif coppie and pb is not None and all(not c["largo_sopra"]
                                                   for c in coppie):
                rif, rif_p = bot_pezzo, pb
            elif coppie:
                rif = rif_p = None
                avv.append("biselli MISTI sopra/sotto: sagomatura del "
                           "profilo NON gestita, controlla il pezzo")
            elif (pb is not None
                    and bot_pezzo["area"] > top_pezzo["area"] + 50):
                rif, rif_p = bot_pezzo, pb
            else:
                rif, rif_p = top_pezzo, punti
            if rif is not None:
                camp = list(rif_p)
                for p, q in zip(rif_p, rif_p[1:] + rif_p[:1]):
                    camp.append(((p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0))
                linee = []
                for c in coppie:
                    linee.append((c["t1"], c["t2"]))
                    linee.append((c["b1"], c["b2"]))
                rientra = 0.0
                for x, y in camp:
                    dentro = min(x, lung - x, y, larg - y)
                    if dentro <= max(rientra, 0.8):
                        continue
                    if linee and min(_dist_pt_seg((x, y), l1, l2)
                                     for l1, l2 in linee) <= 1.0:
                        continue           # deviazione da bisello: non conta
                    rientra = dentro
                if rientra > 0.8:
                    puliti = [rif_p[0]]
                    for p in rif_p[1:]:
                        if (abs(p[0] - puliti[-1][0]) > 0.01
                                or abs(p[1] - puliti[-1][1]) > 0.01):
                            puliti.append(p)
                    if len(puliti) >= 4:
                        sagome_pezzo.append({"contorno": puliti,
                                             "tratti": can_tratti(rif)})
                        avv.append(f"PROFILO SAGOMATO ({len(puliti)} punti, "
                                   f"rientro max {rientra:.1f}): fresatura "
                                   "di contorno")

    piccoli = {"sopra": [], "sotto": []}   # fondi tondi "da punta": candidati
                                           # gradino piccolo di scasso a gradini

    def entry(lo, prof, thru, lato=None):
        cer = lo["cerchio"]
        if cer:
            c, r = cer
            # cieco D35 = tazza (punta); PASSANTE D35 = tasca fresata
            soglia = 17.4 if thru else R_FORO
            if r < soglia:
                if lato and not thru:          # possibile gradino FITLOCK
                    cx, cy, _ = can_pt(c)
                    piccoli[lato].append({"cir": True, "x": cx, "y": cy,
                                          "r": round(r, 2), "prof": prof,
                                          "thru": False})
                return None                    # foro: gia' gestito dalle punte
            cx, cy, _ = can_pt(c)
            return {"cir": True, "x": cx, "y": cy, "r": round(r, 2),
                    "prof": prof, "thru": thru}
        punti = [can_pt(p)[:2] for p in lo["punti"]]
        # togli doppioni consecutivi
        puliti = [punti[0]]
        for p in punti[1:]:
            if abs(p[0] - puliti[-1][0]) > 0.01 or abs(p[1] - puliti[-1][1]) > 0.01:
                puliti.append(p)
        if len(puliti) < 3:
            return None
        return {"contorno": puliti, "prof": prof, "thru": thru,
                "tratti": can_tratti(lo)}

    def baricentro(lo):
        xs = [can_pt(p)[0] for p in lo["punti"]]
        ys = [can_pt(p)[1] for p in lo["punti"]]
        return sum(xs) / len(xs), sum(ys) / len(ys)

    sopra, sotto = [], []
    centri_fondi = []
    for z, f in fondi_sopra:
        for lo in f["loops"]:
            if not lo["esterno"]:
                continue
            en = entry(lo, round(alt - z, 2), False, lato="sopra")
            if en:
                sopra.append(en)
                centri_fondi.append(baricentro(lo))
    for z, f in fondi_sotto:
        for lo in f["loops"]:
            if not lo["esterno"]:
                continue
            en = entry(lo, round(z, 2), False, lato="sotto")
            if en:
                sotto.append(en)

    # --- bocche del piano superiore SENZA fondo = aperture PASSANTI -------
    for lo in bocche_top:
        bx, by = baricentro(lo)
        if any(abs(bx - cx) < 2 and abs(by - cy) < 2
               for cx, cy in centri_fondi):
            continue                            # e' la bocca di una tasca cieca
        cer = lo["cerchio"]
        if cer and cer[1] < 17.4:
            continue                            # foro passante: fanno le punte
        en = entry(lo, alt, True)
        if en:
            sopra.append(en)
            d = f"D{2*cer[1]:g}" if cer else f"{len(en.get('contorno', []))} punti"
            avv.append(f"apertura PASSANTE ({d}): fresata prof {alt:g}+5")

    # --- SCASSI A GRADINI (es. FITLOCK: D51 prof 4 + D35 prof 6) ----------
    # un fondo tondo "da punta" concentrico a una tasca piu' grande e MENO
    # profonda e' il secondo gradino: diventa TASCA anche lui, e il foro
    # corrispondente va tolto dalle punte.
    fori_via = []
    for lato, lst in (("sopra", sopra), ("sotto", sotto)):
        for p in piccoli[lato]:
            padre = None
            for s in lst:
                if s.get("thru"):
                    continue
                if s.get("cir"):
                    vicino = (abs(s["x"] - p["x"]) < 2
                              and abs(s["y"] - p["y"]) < 2
                              and s["r"] > p["r"] + 1)
                else:
                    xs = [q[0] for q in s["contorno"]]
                    ys = [q[1] for q in s["contorno"]]
                    vicino = (min(xs) - 1 < p["x"] < max(xs) + 1
                              and min(ys) - 1 < p["y"] < max(ys) + 1)
                if vicino and s["prof"] < p["prof"]:
                    padre = s
                    break
            if padre:
                lst.append(dict(p))
                fori_via.append((p["x"], p["y"], p["r"], lato))
                d_padre = (f"D{2*padre['r']:g}" if padre.get("cir")
                           else "sagomato")
                avv.append(f"scasso A GRADINI: {d_padre}x{padre['prof']:g}"
                           f" + D{2*p['r']:g}x{p['prof']:g}"
                           f" a ({p['x']:g},{p['y']:g})")
    return sopra, sotto, fori_via, sagome_pezzo, archi_xy, tagli_incl, avv


def estrai_geometria(dxf_path, prof_d14=PROF_FORO_D14):
    """-> (dims, fori_A, scassi_A, fori_B, scassi_B, tagli, sagome, avvisi).
    Normalizza al minimo del bounding box. Un foro = {plane, x, y, r, prof}.
    prof_d14: profondita' FISSA per i fori D14 ciechi (15.8 per la
    Masterwood); None = usa la profondita' vera della geometria (HOMAG)."""
    import ezdxf
    doc = ezdxf.readfile(dxf_path)
    solids = [e for e in doc.modelspace() if e.dxftype() == "3DSOLID"]
    if not solids:
        raise RuntimeError("nessun 3DSOLID nel file")
    pts, circles = [], []
    per_solido = []          # bbox grezzo di OGNI solido (per i tagli
                             # di sezionatura dei file uniti, es. frontali)
    for e in solids:
        if e.sab:
            p, c = _circles_sab(e.sab)
        elif e.sat:
            p, c = _circles_sat(e.sat)
        else:
            continue
        pts.extend(p); circles.extend(c)
        if p:
            per_solido.append(([min(q[i] for q in p) for i in range(3)],
                               [max(q[i] for q in p) for i in range(3)]))
    if not pts:
        raise RuntimeError("geometria ACIS vuota")

    mn = [min(p[i] for p in pts) for i in range(3)]
    mx = [max(p[i] for p in pts) for i in range(3)]
    dims0 = [mx[i] - mn[i] for i in range(3)]          # estensioni X, Y, Z
    avvisi = []

    # --- assi canonici: piu' lungo = LUNG, medio = LARG, corto = spessore --
    # (il DXF esportato puo' avere il pezzo "in piedi": qui si rimappa)
    perm = sorted(range(3), key=lambda i: -dims0[i])
    lung, larg, alt = dims0[perm[0]], dims0[perm[1]], dims0[perm[2]]

    # una permutazione DISPARI (scambio di due assi) e' una RIFLESSIONE:
    # produrrebbe il pezzo specchiato. Si ripristina l'orientamento fisico
    # vero specchiando la Y (verificato sul frontale fisso 08 vs programma
    # macchina HOMAG: senza questo le Y uscivano a LARG-Y).
    inversioni = sum(1 for i in range(3) for j in range(i + 1, 3)
                     if perm[i] > perm[j])
    specchia_y = (inversioni % 2) == 1
    if perm != [0, 1, 2]:
        avvisi.append(f"assi rimappati (pezzo non in piano): perm={perm}"
                      + (" +specchio Y" if specchia_y else ""))

    def rimappa(v):
        p = (v[perm[0]], v[perm[1]], v[perm[2]])
        if specchia_y:
            return (p[0], larg - p[1], p[2])
        return p

    def rimappa_dir(v):
        # per le DIREZIONI (normali): solo permutazione, niente specchio
        return (v[perm[0]], v[perm[1]], v[perm[2]])

    # --- raggruppa i cerchi coassiali in FORI -----------------------------
    # asse: 0=X 1=Y 2=Z (canonici); chiave = (asse, coord. perp., raggio)
    gruppi = {}
    for c, n, r in circles:
        c = rimappa(tuple(c[i] - mn[i] for i in range(3)))   # origine + assi
        n = rimappa_dir(n)
        ax = None
        for i in range(3):
            if abs(n[i]) >= TOL_AXIS:
                ax = i
        if ax is None:
            continue                                    # cerchio inclinato
        perp = tuple(round(c[i], NDEC) for i in range(3) if i != ax)
        key = (ax, perp, round(r, 2))
        gruppi.setdefault(key, []).append(c[ax])

    # due fori CONTRAPPOSTI sui bordi opposti condividono asse e coord.:
    # si separano spezzando dove il salto tra cerchi consecutivi e' grande
    GAP_MAX = 80
    fori = []          # (asse, cperp, r, pos_min, pos_max)
    scarti = 0
    for (ax, perp, r), posiz in gruppi.items():
        posiz = sorted(posiz)
        cluster = [posiz[0]]
        blocchi = []
        for p in posiz[1:]:
            if p - cluster[-1] > GAP_MAX:
                blocchi.append(cluster)
                cluster = [p]
            else:
                cluster.append(p)
        blocchi.append(cluster)
        for bl in blocchi:
            span = bl[-1] - bl[0]
            if span < 0.2:
                scarti += 1                             # cerchio isolato/raccordo
                continue
            fori.append((ax, perp, r, bl[0], bl[-1]))
    if scarti:
        avvisi.append(f"{scarti} cerchi isolati ignorati (raccordi o anelli)")

    # --- separa i fori per faccia di ingresso (coordinate canoniche) ------
    FORO_MAX_R = 17.5      # oltre questo raggio non e' una punta: si FRESA
    vert_sopra, vert_sotto, passanti, bordi = [], [], [], []
    cerchi_sopra, cerchi_sotto = [], []    # cerchi grandi da fresare
    assi_fori = []     # (asse, coord-perp, r): per filtrare i punti dei
                       # fori dal riconoscimento scassi
    for ax, perp, r, a, b in fori:
        assi_fori.append((ax, perp, r))
        if ax == 2:                                    # verticale
            x, y = perp
            sopra = abs(b - alt) < TOL_FACE
            sotto = abs(a) < TOL_FACE
            grande = r > FORO_MAX_R
            if grande:
                avvisi.append(f"cerchio D{2*r:g} a ({x:g},{y:g}): FRESATO "
                              "(troppo grande per una punta), controlla")
            if sopra and sotto:
                if grande:
                    cerchi_sopra.append((x, y, r, alt))    # scontorno passante
                else:
                    passanti.append((x, y, r))
            elif sopra:
                (cerchi_sopra if grande else vert_sopra).append((x, y, r, b - a))
            elif sotto:
                (cerchi_sotto if grande else vert_sotto).append((x, y, r, b - a))
            else:
                avvisi.append(f"foro verticale interno a ({x:g},{y:g}): SALTATO")
        else:
            bordi.append((ax, perp, r, a, b))

    # ================= SCASSI =============================================
    # 1a scelta: TOPOLOGIA ACIS (solo DXF con SAT testuale) -> contorni VERI
    # anche sagomati; fallback: metodo geometrico sui vertici (rettangoli).
    scassi_sopra, scassi_sotto = [], []
    sagome_pezzo = []
    tagli_incl = []
    scassi_topo_ok = False
    if all(getattr(e, "sat", None) for e in solids):
        try:
            (scassi_sopra, scassi_sotto, fori_via, sagome_pezzo, archi_xy,
             tagli_incl, avv_t) = _scassi_topologia(
                solids, rimappa, rimappa_dir, mn, lung, larg, alt)
            for m in avv_t:
                avvisi.append(m)
            # gradini piccoli degli scassi: via dalle punte
            for fx, fy, fr, lato in fori_via:
                lst = vert_sopra if lato == "sopra" else vert_sotto
                lst[:] = [v for v in lst
                          if not (abs(v[0] - fx) < 0.5 and abs(v[1] - fy) < 0.5
                                  and abs(v[2] - fr) < 0.3)]
            # i RACCORDI dei contorni (sagome, asole, angoli tasca) hanno
            # facce cilindriche che sembrano fori: via dalle punte
            def e_raccordo(x, y, r):
                return any(abs(x - ax) < 0.5 and abs(y - ay) < 0.5
                           and abs(r - ar) < 0.3 for ax, ay, ar in archi_xy)
            finti = len(passanti) + len(vert_sopra) + len(vert_sotto)
            passanti[:] = [p for p in passanti if not e_raccordo(*p)]
            vert_sopra[:] = [v for v in vert_sopra
                             if not e_raccordo(v[0], v[1], v[2])]
            vert_sotto[:] = [v for v in vert_sotto
                             if not e_raccordo(v[0], v[1], v[2])]
            finti -= len(passanti) + len(vert_sopra) + len(vert_sotto)
            if finti:
                avvisi.append(f"{finti} finti fori dai raccordi dei "
                              "contorni: TOLTI")

            # BARILOTTO (regola utente 30/07/2026): le tasche TONDE o
            # tondeggianti ~D14 CIECHE sono FORI da punta, non fresate
            # (D14x14.2 sulla HOMAG, 15.8 sul TLF via prof_d14)
            def d14_da_scassi(lst_scassi, lst_vert):
                resta, conv = [], 0
                for s in lst_scassi:
                    cx = cy = pr = None
                    if not s.get("thru"):
                        if s.get("cir") and 13.0 <= 2 * s["r"] <= 14.5:
                            cx, cy, pr = s["x"], s["y"], s["prof"]
                        elif "contorno" in s:
                            xs = [p[0] for p in s["contorno"]]
                            ys = [p[1] for p in s["contorno"]]
                            dx = max(xs) - min(xs)
                            dy = max(ys) - min(ys)
                            # tondeggiante: bbox da D14 e area da cerchio
                            # (un quadrato 14x14 resta tasca)
                            a2 = 0.0
                            n = len(s["contorno"])
                            for i in range(n):
                                x0, y0 = s["contorno"][i]
                                x1, y1 = s["contorno"][(i + 1) % n]
                                a2 += x0 * y1 - x1 * y0
                            if (13.0 <= dx <= 14.5 and 13.0 <= dy <= 14.5
                                    and abs(a2) / 2.0 < 0.9 * dx * dy):
                                cx = (max(xs) + min(xs)) / 2.0
                                cy = (max(ys) + min(ys)) / 2.0
                                pr = s["prof"]
                    if cx is None:
                        resta.append(s)
                    else:
                        lst_vert.append((cx, cy, 7.0, pr))
                        conv += 1
                return resta, conv
            scassi_sopra, c1 = d14_da_scassi(scassi_sopra, vert_sopra)
            scassi_sotto, c2 = d14_da_scassi(scassi_sotto, vert_sotto)
            if c1 + c2:
                avvisi.append(f"{c1 + c2} barilotti D14: FORO da punta "
                              "(non tasca fresata)")
            scassi_topo_ok = True
            if scassi_sopra or scassi_sotto:
                avvisi.append(f"scassi dalla TOPOLOGIA: {len(scassi_sopra)} "
                              f"sopra, {len(scassi_sotto)} sotto")
        except Exception as ex:
            avvisi.append(f"topologia ACIS non leggibile ({ex}): "
                          "uso il metodo geometrico")
    prefori_d35 = []
    if scassi_topo_ok:
        # i cerchi grandi sono gia' coperti dai contorni della topologia
        cerchi_sopra, cerchi_sotto = [], []
        # i passanti tondi grandi diventano tasca (topologia) + PREFORO
        # D35 prof 13 come nei programmi macchina reali (nel prog. PRINCIPALE)
        grandi = [(x, y, r) for x, y, r in passanti if r >= 17.4]
        passanti = [(x, y, r) for x, y, r in passanti if r < 17.4]
        prefori_d35 = [(x, y, r) for x, y, r in grandi if abs(r - 17.5) < 0.2]

    # ================= SCASSI (fallback geometrico) =======================
    # vertici del solido a quota interna 0<z<ALT che formano un rettangolo
    # coi 4 angoli di apertura su una delle due facce (sopra O sotto).
    def punto_di_foro(x, y, z):
        for ax, perp, r in assi_fori:
            if ax == 2:
                d = math.hypot(x - perp[0], y - perp[1])
            elif ax == 1:
                d = math.hypot(x - perp[0], z - perp[1])
            else:
                d = math.hypot(y - perp[0], z - perp[1])
            if d <= r + 0.5:
                return True
        return False

    if scassi_topo_ok:
        pts_f = set()                     # topologia gia' fatta: salta tutto
    else:
        pts_f = {tuple(round(c, 2) for c in rimappa(
                     tuple(p[i] - mn[i] for i in range(3))))
                 for p in pts}
    sopra_xy, sotto_xy, livelli = set(), set(), {}
    for x, y, z in pts_f:
        if punto_di_foro(x, y, z):
            continue
        if abs(z - alt) < TOL_FACE:
            sopra_xy.add((x, y))
        elif abs(z) < TOL_FACE:
            sotto_xy.add((x, y))
        elif TOL_FACE < z < alt - TOL_FACE:
            livelli.setdefault(z, set()).add((x, y))

    residui = 0
    for z0, punti in sorted(livelli.items()):
        xs = sorted({p[0] for p in punti})
        cand = []
        for i, x1 in enumerate(xs):
            for x2 in xs[i + 1:]:
                ys = sorted({p[1] for p in punti if p[0] in (x1, x2)})
                for j, y1 in enumerate(ys):
                    for y2 in ys[j + 1:]:
                        ang = {(x1, y1), (x1, y2), (x2, y1), (x2, y2)}
                        if ang <= punti:
                            cand.append(((x2 - x1) * (y2 - y1),
                                         x1, y1, x2, y2))
        cand.sort()
        usati = set()
        for area, x1, y1, x2, y2 in cand:
            ang = {(x1, y1), (x1, y2), (x2, y1), (x2, y2)}
            if ang & usati:
                continue
            dentro = [p for p in punti - ang
                      if x1 - 0.05 < p[0] < x2 + 0.05
                      and y1 - 0.05 < p[1] < y2 + 0.05]
            if dentro:
                continue
            rett = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
            if ang <= sopra_xy:                        # apre sulla faccia sopra
                scassi_sopra.append(dict(rett, prof=round(alt - z0, 2)))
            elif ang <= sotto_xy:                      # apre sulla faccia sotto
                scassi_sotto.append(dict(rett, prof=round(z0, 2)))
            else:
                continue
            usati |= ang
        residui += len(punti - usati)
    if residui:
        avvisi.append(f"{residui} vertici a quota interna NON riconosciuti "
                      "(scassi non rettangolari, laterali o passanti?): "
                      "CONTROLLA il pezzo")

    # --- SCASSI PASSANTI: rettangoli con gli angoli su ENTRAMBE le facce --
    # (aperture senza fondo, es. vani del frontale fisso). Vanno nel
    # programma principale con prof = spessore + 5 (come i programmi
    # macchina HOMAG reali: TI 24 su pannello 19).
    entrambe = {p for p in (sopra_xy & sotto_xy)
                if TOL_FACE < p[0] < lung - TOL_FACE
                and TOL_FACE < p[1] < larg - TOL_FACE}
    if entrambe:
        xs = sorted({p[0] for p in entrambe})
        cand = []
        for i, x1 in enumerate(xs):
            for x2 in xs[i + 1:]:
                ys = sorted({p[1] for p in entrambe if p[0] in (x1, x2)})
                for j, y1 in enumerate(ys):
                    for y2 in ys[j + 1:]:
                        ang = {(x1, y1), (x1, y2), (x2, y1), (x2, y2)}
                        if ang <= entrambe:
                            dentro = [p for p in entrambe - ang
                                      if x1 - 0.05 < p[0] < x2 + 0.05
                                      and y1 - 0.05 < p[1] < y2 + 0.05]
                            if not dentro:
                                cand.append((x1, y1, x2, y2))
        # celle contigue che condividono lo spigolo = vuoto/ponte alternati:
        # in una fila delimitata dal materiale la 1a, 3a, ... sono VUOTI
        # (aperture), le pari sono PONTI di materiale (che spesso portano
        # keku/spine). Verificato sul frontale fisso 08 vs macchina.
        per_riga = {}
        for x1, y1, x2, y2 in cand:
            per_riga.setdefault((y1, y2), []).append((x1, x2))
        for (y1, y2), celle in per_riga.items():
            celle.sort()
            catena = []
            for x1, x2 in celle:
                if catena and abs(x1 - catena[-1][1]) < 0.05:
                    catena.append((x1, x2))
                else:
                    if catena:
                        for k, (a1, a2) in enumerate(catena):
                            if k % 2 == 0:
                                scassi_sopra.append(
                                    {"x1": a1, "y1": y1, "x2": a2, "y2": y2,
                                     "prof": round(alt + 5, 2)})
                                avvisi.append(
                                    f"scasso PASSANTE {a2-a1:g}x{y2-y1:g} "
                                    f"a ({a1:g},{y1:g}): prof {alt + 5:g}")
                    catena = [(x1, x2)]
            for k, (a1, a2) in enumerate(catena):
                if k % 2 == 0:
                    scassi_sopra.append(
                        {"x1": a1, "y1": y1, "x2": a2, "y2": y2,
                         "prof": round(alt + 5, 2)})
                    avvisi.append(f"scasso PASSANTE {a2-a1:g}x{y2-y1:g} "
                                  f"a ({a1:g},{y1:g}): prof {alt + 5:g}")

    # --- faccia principale = quella con piu' lavorazioni ------------------
    # (l'altra faccia, se lavorata, finisce nel programma _B girato di 180
    # attorno al lato lungo: y -> LARG-y, z -> ALT-z)
    flip_A = (len(vert_sotto) + len(scassi_sotto) + len(cerchi_sotto)) > \
             (len(vert_sopra) + len(scassi_sopra) + len(cerchi_sopra))
    if flip_A:
        avvisi.append("faccia principale SOTTO: programma principale ribaltato")

    def prog_verticali(vert, flip):
        out = []
        for x, y, r, prof in vert:
            if flip:
                y = larg - y
            if prof_d14 and abs(2 * r - 14) < 0.1:   # regola fissa D14
                prof = prof_d14
            out.append({"plane": 0, "x": x, "y": y, "r": r, "prof": prof})
        return out

    def specchia_tratti(tratti):
        if not tratti:
            return None
        return [("L", (t[1][0], larg - t[1][1])) if t[0] == "L"
                else ("A", (t[1][0], larg - t[1][1]),
                      (t[2][0], larg - t[2][1]), t[3])
                for t in tratti]

    def prog_scassi(scassi, flip):
        out = []
        for s in scassi:
            if not flip:
                out.append(dict(s))
            elif "contorno" in s:
                out.append(dict(s, contorno=[(x, larg - y)
                                             for x, y in s["contorno"]],
                                tratti=specchia_tratti(s.get("tratti"))))
            elif s.get("cir"):
                out.append(dict(s, y=larg - s["y"]))
            else:
                out.append({"x1": s["x1"], "y1": larg - s["y2"],
                            "x2": s["x2"], "y2": larg - s["y1"],
                            "prof": s["prof"]})
        return out

    def prog_cerchi(cerchi, flip):
        return [{"cir": True, "x": x, "y": (larg - y) if flip else y,
                 "r": r, "prof": prof} for x, y, r, prof in cerchi]

    # le aperture PASSANTI vanno SEMPRE nel programma principale
    # (il lato e' indifferente: cosi' fanno i programmi macchina reali)
    tasche_thru = ([s for s in scassi_sopra if s.get("thru")]
                   + [s for s in scassi_sotto if s.get("thru")])
    scassi_sopra = [s for s in scassi_sopra if not s.get("thru")]
    scassi_sotto = [s for s in scassi_sotto if not s.get("thru")]

    # --- programma principale (A): faccia principale + passanti + bordi ---
    fori_A = prog_verticali(vert_sotto if flip_A else vert_sopra, flip_A)
    for x, y, r in passanti:
        fori_A.append({"plane": 0, "x": x, "y": (larg - y) if flip_A else y,
                       "r": r, "prof": alt + THROUGH_EXTRA})
    for x, y, r in prefori_d35:               # preforo tazza D35 prof 13
        fori_A.append({"plane": 0, "x": x, "y": (larg - y) if flip_A else y,
                       "r": r, "prof": 13.0})
    for ax, perp, r, a, b in bordi:
        if ax == 1:                                    # orizzontale asse Y
            x, z = perp
            zq = alt - z if flip_A else z
            if abs(a) < TOL_FACE and abs(b - larg) < TOL_FACE:
                avvisi.append(f"foro passante FRONT-REAR a x={x:g}: due lavorazioni")
                fori_A.append({"plane": 2, "x": x, "y": zq, "r": r, "prof": larg / 2 + 2})
                fori_A.append({"plane": 1, "x": x, "y": zq, "r": r, "prof": larg / 2 + 2})
                continue
            prof = b - a
            lato_front = abs(a) < TOL_FACE
            if flip_A:                                 # girato: lati invertiti
                lato_front = not lato_front and abs(b - larg) < TOL_FACE
            if lato_front:
                fori_A.append({"plane": 2, "x": x, "y": zq, "r": r, "prof": prof})
            elif abs(b - larg) < TOL_FACE or abs(a) < TOL_FACE:
                fori_A.append({"plane": 1, "x": x, "y": zq, "r": r, "prof": prof})
            else:
                avvisi.append(f"foro orizzontale interno a x={x:g}: SALTATO")
        else:                                          # orizzontale asse X
            y, z = perp
            yq = larg - y if flip_A else y
            zq = alt - z if flip_A else z
            if abs(a) < TOL_FACE and abs(b - lung) < TOL_FACE:
                avvisi.append(f"foro passante LEFT-RIGHT a y={yq:g}: due lavorazioni")
                fori_A.append({"plane": 3, "x": yq, "y": zq, "r": r, "prof": lung / 2 + 2})
                fori_A.append({"plane": 4, "x": yq, "y": zq, "r": r, "prof": lung / 2 + 2})
                continue
            prof = b - a
            if abs(a) < TOL_FACE:
                fori_A.append({"plane": 3, "x": yq, "y": zq, "r": r, "prof": prof})
            elif abs(b - lung) < TOL_FACE:
                fori_A.append({"plane": 4, "x": yq, "y": zq, "r": r, "prof": prof})
            else:
                avvisi.append(f"foro orizzontale interno a y={yq:g}: SALTATO")
    scassi_A = prog_scassi(scassi_sotto if flip_A else scassi_sopra, flip_A) \
        + prog_cerchi(cerchi_sotto if flip_A else cerchi_sopra, flip_A) \
        + prog_scassi(tasche_thru, flip_A)

    # il PROFILO sagomato e' passante: sempre nel programma principale
    sagome_A = []
    for sg in sagome_pezzo:
        if flip_A:
            sagome_A.append({"contorno": [(x, larg - y)
                                          for x, y in sg["contorno"]],
                             "tratti": specchia_tratti(sg.get("tratti"))})
        else:
            sagome_A.append(sg)

    # i tagli INCLINATI (biselli) sono passanti: programma principale;
    # col ribaltamento si specchia la linea, si inverte il verso (fuori
    # sempre a sinistra) e si scambia il lato largo sopra/sotto
    # la linea del <124 sta sul bordo della faccia SUPERIORE del programma:
    # col ribaltamento sopra e sotto si scambiano (e si specchia la y)
    tagli_incl_A = []
    for c in tagli_incl:
        if flip_A:
            tagli_incl_A.append(
                {"t1": (c["b2"][0], larg - c["b2"][1]),
                 "t2": (c["b1"][0], larg - c["b1"][1]),
                 "b1": (c["t2"][0], larg - c["t2"][1]),
                 "b2": (c["t1"][0], larg - c["t1"][1]),
                 "beta": c["beta"],
                 "largo_sopra": not c["largo_sopra"]})
        else:
            tagli_incl_A.append(c)

    # --- programma _B: SOLO le lavorazioni dell'altra faccia --------------
    flip_B = not flip_A
    fori_B = prog_verticali(vert_sopra if flip_A else vert_sotto, flip_B)
    scassi_B = prog_scassi(scassi_sopra if flip_A else scassi_sotto, flip_B) \
        + prog_cerchi(cerchi_sopra if flip_A else cerchi_sotto, flip_B)

    # --- TAGLI DI SEZIONATURA: file con PIU' solidi in fila (frontali
    # cassetto uniti): una lamata passante in ogni fuga, a filo del bordo
    # del pezzo di sinistra. Le posizioni X non cambiano con specchi/flip
    # (che agiscono solo su y/z).
    tagli = []
    if len(per_solido) > 1:
        ax0 = perm[0]
        interv = sorted((mn_i[ax0] - mn[ax0], mx_i[ax0] - mn[ax0])
                        for mn_i, mx_i in per_solido)
        for (a1, b1), (a2, b2) in zip(interv, interv[1:]):
            gap = a2 - b1
            if gap > 0.5:
                tagli.append({"x": round(b1, 2), "gap": round(gap, 2)})
                msg = f"TAGLIO di sezionatura a x={b1:g} (fuga {gap:g})"
                if abs(gap - 3.2) > 0.3:
                    msg += " [fuga diversa dalla lama 3.2: CONTROLLA]"
                avvisi.append(msg)

    return ((lung, larg, alt), fori_A, scassi_A, fori_B, scassi_B,
            tagli, sagome_A, tagli_incl_A, avvisi)


# ========================= scrittura TLF ===================================
def _n(v):
    """numero senza zeri inutili: 536.5, 19, 14.2, 87.25"""
    v = round(float(v), 4)
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def scrivi_tlf(path, dims, fori, scassi=None):
    lung, larg, alt = dims
    scassi = scassi or []
    rett = [s for s in scassi
            if not s.get("cir") and "contorno" not in s]   # rettangolari
    sagome = [s for s in scassi if "contorno" in s]        # contorni veri
    cerchi = [s for s in scassi if s.get("cir")]           # cerchi grandi

    def prof_di(s):
        return alt + 5 if s.get("thru") else s["prof"]
    oggi = datetime.date.today().strftime("%d/%m/%Y")
    r = []
    a = r.append
    a("TARGET"); a("8 PROJECT MW315 WINDOWS")
    a("PARGEN")
    a("LIMMINX"); a("0")
    a("LIMMINY"); a("0")
    a("LIMMAXX"); a(_n(lung))
    a("LIMMAXY"); a(_n(larg))
    a("RAGGIORACCORDO"); a("10")
    a("CURLAYER"); a("1")
    a("LAYER"); a("1"); a("CAD"); a("1"); a("\\LAYER")
    a("LAYER"); a("2"); a("CAM"); a("1"); a("\\LAYER")
    a("NUMPROG"); a("1")
    a("DESCR"); a("[NONE]")
    a("NUMTABUTE"); a("1")
    a("NUMTABVENT"); a("1")
    a("LUNG"); a(_n(lung))
    a("LARG"); a(_n(larg))
    a("ALT"); a(_n(alt))
    a("AUTORE"); a("CN MW315 Ver. 4.05 R5")
    a("DATACREAZ"); a(oggi)
    a("DATAMOD"); a(oggi)
    a("ORDINECOMP"); a("0|1|2|3|4|5|6|7|")
    a("ORIGLUNG"); a("-1")
    a("ORIGLARG"); a("-1")
    a("ORIGALT"); a("-1")
    a("FLAGOTTFORI"); a("1")
    a("FLAGOTTLAV"); a("0")
    a("DEFAULT_ALT_CUFFIA"); a("0")
    a("OFFSET_DIMA_X"); a("0")
    a("OFFSET_DIMA_XEXPR"); a("")
    a("OFFSET_DIMA_Y"); a("0")
    a("OFFSET_DIMA_YEXPR"); a("")
    a("OFFSET_DIMA_Z"); a("0")
    a("OFFSET_DIMA_ZEXPR"); a("")
    a("QUOTA_X_BREAK"); a("0")
    a("TOLL_BREAK"); a("0")
    a("BREAK_OFF")
    a("PIANO10")
    a("ALT"); a("0")
    a("ANG"); a("-90")
    a("LUNG"); a(_n(lung + 0.0002))
    a("P_START"); a("PSX"); a("0 I"); a("PSY"); a(_n(larg) + " F")
    a("P_END"); a("PEX"); a(_n(lung) + " F"); a("PEY"); a(_n(larg) + " F")
    a("P1"); a("P1X"); a("-0.0001 I"); a("P1Y"); a(_n(larg) + " F")
    a("P2"); a("P2X"); a(_n(lung + 0.0001) + " F"); a("P2Y"); a(_n(larg) + " F")
    a("P3"); a("P3X"); a("0 I"); a("P3Y"); a("0 I")
    a("P4"); a("P4X"); a(_n(lung) + " F"); a("P4Y"); a("0 I")
    a("ORIG"); a("OX"); a("-0.0001 I"); a("OY"); a(_n(larg) + " I")
    a("V1"); a("V1X"); a("0 I"); a("V1Y"); a("0 F")
    a("V2"); a("V2X"); a(_n(lung + 0.0002) + " F"); a("V2Y"); a("0 F")
    a("V3"); a("V3X"); a("0.0001 I"); a("V3Y"); a(_n(larg) + " I")
    a("V4"); a("V4X"); a(_n(lung + 0.0001) + " F"); a("V4Y"); a(_n(larg) + " I")
    a("\\PIANO10")
    a("QPARK_U1"); a("")
    a("QPARK_U2"); a("")
    a("QCARIC_U1"); a("")
    a("QCARIC_U2"); a("")
    a("QCARIC_V"); a("")
    a("BATT_AUX"); a("1")
    a("MOT_OTTIM"); a("")
    a("VEL_ROT"); a("0")
    a("PRG_BLOCCO"); a("")
    a("PRG_SBLOCCO"); a("")
    a("PLATEAU"); a("")
    a("LABEL1"); a("")
    a("LABEL2"); a("")
    a("LABEL3"); a("")
    a("LABEL4"); a("")
    a("MODENESTING"); a("0")
    a("RIPETIZIONI"); a("1")
    a("MATERIAL"); a("")
    a("VENATURA"); a("")
    a("FLAG_BATTUTA"); a("0")
    a("EXTIDCODE"); a("")
    a("\\PARGEN")
    a("PARAMETRICHE"); a("\\PARAMETRICHE")
    a("PARAMETRICHEPOST"); a("\\PARAMETRICHEPOST")

    per_piano = {p: [] for p in range(8)}
    for f in fori:
        per_piano[f["plane"]].append(f)
    # ordine stabile dentro il piano: per X poi Y
    for p in per_piano:
        per_piano[p].sort(key=lambda f: (f["x"], f["y"]))

    def _pol_vertice(x, y):
        a("V")
        a("X"); a(_n(x) + " I")
        a("Y"); a(_n(y) + " I")
        a("Z"); a(_n(alt) + " 0")
        a("XEXPR"); a("")
        a("YEXPR"); a("")
        a("ZEXPR"); a("")
        a("B"); a("0")
        a("REXPR"); a("")
        a("PARTDEF"); a("0")
        a("S"); a("0")
        a("\\V")

    a("ENTITIES")
    for p in range(8):
        a(f"PLANE {p}")
        for i, f in enumerate(per_piano[p]):
            a("CIR")
            a("INDEX"); a(str(i))
            a("LINKS"); a("1")
            a("L"); a("2")
            a("DIAM_UT"); a("0")
            a("X"); a(_n(f["x"]) + " I")
            a("Y"); a(_n(f["y"]) + " I")
            a("XEXPR"); a("")
            a("YEXPR"); a("")
            a("R"); a(_n(f["r"]))
            a("\\CIR")
        if p == 0:
            # cerchi grandi da fresare: entita' CIR dopo i CIR dei fori
            for k, s in enumerate(cerchi):
                a("CIR")
                a("INDEX"); a(str(len(per_piano[0]) + k))
                a("LINKS"); a("1")
                a("L"); a("2")
                a("DIAM_UT"); a("0")
                a("X"); a(_n(s["x"]) + " I")
                a("Y"); a(_n(s["y"]) + " I")
                a("XEXPR"); a("")
                a("YEXPR"); a("")
                a("R"); a(_n(s["r"]))
                a("\\CIR")
            # scassi: un POL chiuso per ciascuno, indici che PROSEGUONO
            # dopo i CIR del piano (come nei TLF veri)
            base_idx = len(per_piano[0]) + len(cerchi)

            def _pol(idx, vertici):
                a("POL")
                a("INDEX"); a(str(idx))
                a("LINKS"); a("1")
                a("L"); a("2")
                a("DIAM_UT"); a("0")
                a("X"); a(_n(vertici[0][0]) + " I")
                a("Y"); a(_n(vertici[0][1]) + " I")
                a("Z"); a(_n(alt) + " 0")
                a("XEXPR"); a("")
                a("YEXPR"); a("")
                a("ZEXPR"); a("")
                for vx, vy in vertici[1:]:
                    _pol_vertice(vx, vy)
                if (abs(vertici[-1][0] - vertici[0][0]) > 0.01
                        or abs(vertici[-1][1] - vertici[0][1]) > 0.01):
                    _pol_vertice(*vertici[0])          # chiudi sul primo
                a("C"); a("1")
                a("P0DEF"); a("0")
                a("\\POL")

            for k, s in enumerate(rett):
                x1, y1, x2, y2 = s["x1"], s["y1"], s["x2"], s["y2"]
                _pol(base_idx + k, [(x1, y1), (x2, y1), (x2, y2), (x1, y2),
                                    (x1, y1)])
            for k, s in enumerate(sagome):
                _pol(base_idx + len(rett) + k, s["contorno"])
    a("\\ENTITIES")

    a("WORKS")
    order = 998
    for p in range(8):
        a(f"PLANE {p}")
        if p == 0:
            # FRES di cerchi grandi e scassi (parametri come riv_pelle.tlf:
            # ut.30, compensazione 1 raggio 4; profondita' = prof)
            base_idx = len(per_piano[0])
            lavor = ([(base_idx + k, s["x"], s["y"], prof_di(s))
                      for k, s in enumerate(cerchi)]
                     + [(base_idx + len(cerchi) + k, s["x1"], s["y1"],
                         prof_di(s)) for k, s in enumerate(rett)]
                     + [(base_idx + len(cerchi) + len(rett) + k,
                         s["contorno"][0][0], s["contorno"][0][1], prof_di(s))
                        for k, s in enumerate(sagome)])
            for ent_idx, px, py, prof_s in lavor:
                a("FRES")
                a("ENT"); a(str(ent_idx))
                a("ENTORIG"); a("0")
                a("DESCRIZIONE"); a("")
                a("NUMUTENSILE"); a("30")
                a("VELROTAZIONE"); a("18")
                a("VELENTRATA"); a("0")
                a("PROFLAVORAZIONE"); a(_n(prof_s))
                a("PROFLAVORAZIONEEXPR"); a("")
                a("ANGTILTING"); a("90")
                a("ANGTILTINGEXPR"); a("")
                a("ANGINDEX"); a("0")
                a("ORDER"); a(str(order)); order -= 1
                a("SEQUENZA"); a("0")
                a("SPESS"); a(f"{alt:.2f}")
                a("ALT_CUFFIA"); a("0")
                a("IDPEZZONESTING"); a("0")
                a("ENABLEDEXPR"); a("")
                a("VELFRESATURA"); a("5")
                a("PUNTOPARTENZAX"); a(_n(px) + " I")
                a("PUNTOPARTENZAY"); a(_n(py) + " I")
                a("NONGENERAQ")
                a("VERSOPERC"); a("0")
                a("RACCORDO"); a("0")
                a("COMPENSAZ"); a("1")
                a("RAGGIOCOMP"); a("4")
                a("RAGGIOCOMPEXPR"); a("")
                a("PROFPASSATA"); a("0")
                a("SORMONTO"); a("0")
                a("PROFINIZ"); a("0")
                a("OUTPUT_COMPIL"); a("0")
                a("ANG_DEFL"); a("0")
                a("ISO"); a("")
                a("PROFILO_UTE"); a("STANDARD")
                a("RIFDELPROF"); a("0")
                a("QMAGGIORATAZ"); a("0")
                a("QAVVICINXY"); a("0")
                a("TCHIUPRESS"); a("0")
                a("PROFILATURA"); a("0")
                a("DYNDATA"); a("-1")
                a("\\FRES")
        for i, f in enumerate(per_piano[p]):
            a("FOR_SING")
            a("ENT"); a(str(i))
            a("ENTORIG"); a(str(i))
            a("DESCRIZIONE"); a("")
            a("NUMUTENSILE"); a("0")
            a("VELROTAZIONE"); a("0")
            a("VELENTRATA"); a("1")
            a("PROFLAVORAZIONE"); a(_n(f["prof"]))
            a("PROFLAVORAZIONEEXPR"); a("")
            a("ANGTILTING"); a("90")
            a("ANGTILTINGEXPR"); a("")
            a("ANGINDEX"); a("0")
            a("ORDER"); a(str(order)); order -= 1
            a("SEQUENZA"); a("0")
            a("SPESS"); a(f"{alt:.2f}")
            a("ALT_CUFFIA"); a("0")
            a("IDPEZZONESTING"); a("0")
            a("ENABLEDEXPR"); a("")
            a("VELLAVORAZIONE"); a("0")
            a("DIAMETRO"); a(_n(2 * f["r"]))
            a("OFFSET"); a("0")
            a("OFFSETEXPR"); a("")
            a("RALLFORO"); a("0")
            a("VELRALL"); a("0.4")
            a("TOPDIST"); a("3")
            a("BOTTOMDIST"); a("3")
            a("TIPOPUNTA"); a("0")
            a("\\FOR_SING")
    a("\\WORKS")
    a("EOF")

    with open(path, "w", encoding="ascii", errors="replace", newline="\r\n") as fh:
        fh.write("\n".join(r) + "\n")


def converti(dxf_path, out_dir=None, log=print):
    base = os.path.splitext(os.path.basename(dxf_path))[0]
    out_dir = out_dir or os.path.dirname(dxf_path)
    tlf = os.path.join(out_dir, base + ".tlf")
    dims, fori_A, scassi_A, fori_B, scassi_B, tagli, sagome, incl, avvisi = \
        estrai_geometria(dxf_path)
    if tagli:
        avvisi = avvisi + [f"{len(tagli)} tagli di sezionatura NON scritti "
                           "nel TLF (le lamate sono previste nei programmi "
                           "HOMAG .mpr/.mprx)"]
    if sagome:
        avvisi = avvisi + [f"{len(sagome)} profili sagomati NON scritti nel "
                           "TLF (la fresatura di contorno e' nei programmi "
                           "HOMAG .mpr/.mprx)"]
    if incl:
        avvisi = avvisi + [f"{len(incl)} tagli INCLINATI (lama ad angolo-A) "
                           "NON scritti nel TLF: sono nei programmi HOMAG"]
    scrivi_tlf(tlf, dims, fori_A, scassi_A)
    log(f"  {base}: {_n(dims[0])} x {_n(dims[1])} x {_n(dims[2])}, "
        f"{len(fori_A)} fori, {len(scassi_A)} scassi -> {os.path.basename(tlf)}")
    if fori_B or scassi_B:
        tlf_b = os.path.join(out_dir, base + "_B.tlf")
        scrivi_tlf(tlf_b, dims, fori_B, scassi_B)
        log(f"    + programma GIRATO 180: {len(fori_B)} fori, "
            f"{len(scassi_B)} scassi -> {os.path.basename(tlf_b)}")
    for msg in avvisi:
        log(f"    [!] {msg}")
    return tlf


# ============================== GUI ========================================
def main():
    root = tk.Tk()
    root.title("FILIERA UN CLIC  |  DXF 3D -> TLF Masterwood (MW315)")
    root.geometry("720x460")
    files = []

    def scegli():
        sel = filedialog.askopenfilenames(
            title="Scegli i DXF 3D da convertire",
            filetypes=[("DXF", "*.dxf"), ("Tutti i file", "*.*")])
        if sel:
            files.clear(); files.extend(sel)
            lista.delete(0, "end")
            for f in files:
                lista.insert("end", f)

    def log(msg):
        box.config(state="normal"); box.insert("end", msg + "\n")
        box.see("end"); box.config(state="disabled"); root.update_idletasks()

    def avvia():
        if not files:
            messagebox.showwarning("Attenzione", "Prima scegli i DXF.")
            return
        out_dir = os.path.join(os.path.dirname(files[0]), "TLF")
        os.makedirs(out_dir, exist_ok=True)
        ok, err = 0, 0
        for f in files:
            try:
                converti(f, out_dir, log)
                ok += 1
            except Exception as e:
                err += 1
                log(f"  [ERRORE] {os.path.basename(f)}: {e}")
        log(f"\n>>> Fatto: {ok} convertiti, {err} errori. TLF in {out_dir} <<<")
        if err:
            messagebox.showwarning("Completato con errori",
                                   f"{ok} convertiti, {err} errori (vedi log).")
        else:
            messagebox.showinfo("Fatto", f"{ok} TLF creati in:\n{out_dir}")

    tk.Button(root, text="1)  Scegli i DXF 3D...", font=("Segoe UI", 11),
              command=scegli).pack(fill="x", padx=10, pady=(10, 4))
    lista = tk.Listbox(root, height=8); lista.pack(fill="x", padx=10)
    tk.Button(root, text="2)  CONVERTI IN TLF", font=("Segoe UI", 12, "bold"),
              bg="#2e7d32", fg="white", command=avvia).pack(fill="x", padx=10, pady=6)
    box = tk.Text(root, height=12, state="disabled", font=("Consolas", 9))
    box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1:                      # uso da riga di comando / test
        for pth in sys.argv[1:]:
            converti(pth)
    else:
        main()
