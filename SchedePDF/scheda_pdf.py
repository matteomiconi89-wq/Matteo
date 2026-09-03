# -*- coding: utf-8 -*-
r"""scheda_pdf - il LIBRETTO PDF del mobile: copertina con l'ESPLOSO
(palloncini = numeri programma) + una SCHEDA per programma col disegno
del pezzo e le misure rilevanti. Tutto con Pillow (PDF multipagina).

uso: py scheda_pdf.py <base DXF DEFINITIVI> <camera/mobile> [step]
es.: py scheda_pdf.py "...\21032\SET_19_20_21_22\DXF DEFINITIVI" A102
     "...\21032_A102_J-03_02_ter.stp"
"""
import json
import math
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r"C:\Users\User\Desktop\CLAUDE\Dxf2Tlf")
sys.path.insert(0, r"C:\Users\User\Desktop\CLAUDE\Dxf2Mpr")

FREECADCMD = r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe"
_QUI = r"C:\Users\User\Desktop\CLAUDE\SchedePDF"
if not os.path.isfile(os.path.join(_QUI, "esploso_step_fc.py")):
    _QUI = os.path.dirname(os.path.abspath(__file__))
ESPLOSO_FC = os.path.join(_QUI, "esploso_step_fc.py")

PAG = (2338, 1653)                 # A4 orizzontale a 200 dpi
MARG = 90


def font(px, bold=False):
    nome = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(os.path.join(r"C:\Windows\Fonts", nome), px)


def pagina():
    img = Image.new("RGB", PAG, "white")
    return img, ImageDraw.Draw(img)


def intestazione(dr, titolo, sotto=""):
    dr.text((MARG, 40), titolo, fill="black", font=font(44, True))
    if sotto:
        dr.text((MARG, 100), sotto, fill=(90, 90, 90), font=font(28))
    dr.line([(MARG, 150), (PAG[0] - MARG, 150)], fill="black", width=3)


def num_programma(nome):
    """'07_Schiena' -> '07'; '14_Massello...' -> '14'; '3' -> '3'"""
    for sep in ("_", " ", "."):
        if sep in nome:
            testa = nome.split(sep)[0]
            if testa.isdigit():
                return testa
    return nome if nome[:2].isdigit() or nome[:1].isdigit() else nome[:4]


def iso(p, cx=0.0, cy=0.0, sc=1.0):
    """proiezione isometrica classica"""
    x, y, z = p
    return (cx + (x - y) * 0.866 * sc, cy + (x + y) * 0.5 * sc - z * sc)


# palette QUALITATIVA: colori ben distinti (un materiale = un colore),
# per distinguere a colpo d'occhio anche materiali simili (piu' legni)
PALETTE_MAT = [
    (214, 178, 130), (120, 170, 210), (210, 140, 140), (150, 195, 140),
    (225, 200, 120), (175, 150, 205), (130, 200, 195), (235, 165, 110),
    (165, 165, 170), (205, 160, 195), (140, 185, 160), (150, 175, 225),
    (200, 205, 130), (225, 180, 155), (170, 205, 215), (195, 155, 120),
]


def mappa_colori(materiali):
    """Assegna un colore distinto e STABILE a ogni materiale (ordine
    alfabetico -> palette): stesso materiale = stesso colore ovunque."""
    return {m: PALETTE_MAT[i % len(PALETTE_MAT)]
            for i, m in enumerate(sorted({x for x in materiali if x}))}


def _etichette(manifest):
    """Numero-etichetta per ogni programma, SEMPRE leggibile: il numero
    del nome se c'e' ('07_Schiena'->'07'), altrimenti un progressivo
    (pezzi coi nomi 'Solido_215' non davano numero -> palloncini 'Soli').
    Ritorna {out: etichetta}."""
    eti = {}
    nums = []
    for out, m in manifest.items():
        raw = num_programma(m.get("name") or out)
        if raw.isdigit():
            nums.append(int(raw))
    prossimo = (max(nums) + 1) if nums else 1
    per_nome = {}
    for out, m in sorted(manifest.items(),
                         key=lambda kv: str(kv[1].get("name") or kv[0])):
        nome = m.get("name") or out
        raw = num_programma(nome)
        if raw.isdigit():
            eti[out] = raw
        elif nome in per_nome:
            eti[out] = per_nome[nome]
        else:
            per_nome[nome] = str(prossimo)
            eti[out] = str(prossimo)
            prossimo += 1
    return eti


STRUT_KW = ("FIANCO", "SPALLA", "SPALLE", "TOP", "BASE", "CAPPELLO",
            "SCHIENA", "SCHIENALE", "ZOCCOLO", "MONTANTE", "CIELO",
            "FONDO", "CONTROBASE", "PIANO")
INT_KW = ("RIPIANO", "TRAVERSA", "CASSETTO", "FRONTALE", "ANTA", "GOLA",
          "SPONDA", "PIANETTO", "MASSELLO", "CANALINA", "CORNICE",
          "FASCIA", "MASSELL")


def pagina_esploso(mobile, programmi, boxes, manifest, mat_map=None,
                   finito_shots=None, ferr=None):
    """Copertina: esploso isometrico con palloncini numero programma.
    Ritorna UNA lista di pagine: mobile FINITO a colori, montato
    fronte/retro, poi l'esploso (1 o 2 viste struttura/interni).
    finito_shots=(png_fronte, png_retro, legenda): se ci sono, la pagina
    'COM'E' FINITO' usa gli SCREENSHOT veri di AutoCAD invece del 3D
    ricostruito a mano."""
    ETI = _etichette(manifest)
    mat_map = mat_map or {}
    COL_MAT = mappa_colori(mat_map.values())
    if not boxes:
        img, dr = pagina()
        intestazione(dr, f"MOBILE {mobile} - ESPLOSO",
                     "i numeri sono i PROGRAMMI (vedi schede seguenti)")
        dr.text((MARG, 300), "(nessun 3D d'assieme disponibile: "
                             "vedi l'elenco programmi nelle schede)",
                fill="black", font=font(32))
        return [img]
    # abbina ogni box a un programma per QUOTE ordinate, con PUNTEGGIO e
    # assegnazione ESCLUSIVA che rispetta la q.ta' del programma nel
    # mobile: con la tolleranza secca "primo che combacia" tre fianchi
    # quasi uguali finivano tutti sullo stesso numero e i pannelli
    # INCLINATI (ingombro mondo diverso dalle quote vere) sparivano
    def dims_di(b):
        d = [b["max"][i] - b["min"][i] for i in range(3)]
        return sorted((round(v, 1) for v in d), reverse=True)

    quota = {}
    dmord = {}
    for out, m in manifest.items():
        dm = sorted((round(v, 1) for v in m.get("dims", [])), reverse=True)
        if len(dm) != 3:
            continue
        dmord[out] = dm
        q = sum(1 for mem in (m.get("members") or [])
                if mem and mem[0] == mobile)
        quota[out] = q or m.get("qty") or 1

    # PASSO 1 - abbinamento ESATTO per NOME (variante coi nomi sul solido):
    # il nome del pezzo letto dal layer del box combacia col name del
    # programma nel manifest -> palloncino esatto, senza stime per quote
    num_di = {}
    nome2out = {}
    for out, m in manifest.items():
        nm = (m.get("name") or "").strip()
        if nm and out in quota:
            nome2out.setdefault(nm, []).append(out)
    for i, b in enumerate(boxes):
        nm = (b.get("nome") or "").strip()
        if not nm:
            continue
        for out in nome2out.get(nm, []):
            if quota.get(out, 0) > 0:
                quota[out] -= 1
                num_di[i] = (ETI.get(out, num_programma(
                    manifest[out].get("name") or out)), out)
                break

    # PASSO 2 - per le quote (score) sui box rimasti senza nome/abbinamento
    candidati = []          # (punteggio, indice box, programma, consuma)
    for i, b in enumerate(boxes):
        db = dims_di(b)
        for out, dm in dmord.items():
            err = [abs(a - c) / max(c, 1.0) for a, c in zip(db, dm)]
            if max(err) < 0.02 or all(abs(a - c) < 0.6
                                      for a, c in zip(db, dm)):
                # pezzo "dritto": tre quote d'ingombro = quote programma
                candidati.append((sum(err), i, out, True))
                continue
            pv = dm[0] * dm[1] * dm[2]
            ev = abs(b.get("vol", 0) - pv) / max(pv, 1.0)
            diag_b = (db[0] ** 2 + db[1] ** 2 + db[2] ** 2) ** 0.5
            diag_m = (dm[0] ** 2 + dm[1] ** 2 + dm[2] ** 2) ** 0.5
            if (b.get("vol") and ev < 0.25
                    and dm[0] <= diag_b * 1.02 and db[0] <= diag_m * 1.02):
                # pezzo INCLINATO: il VOLUME vero non cambia con
                # l'orientamento; le diagonali dicono se il pezzo ci puo'
                # stare in quell'ingombro (e viceversa)
                candidati.append((0.5 + ev, i, out, True))
                continue
            if (abs(db[1] - dm[1]) < 0.6 and abs(db[2] - dm[2]) < 0.6
                    and db[0] <= dm[0] + 1):
                # pezzi UNITI nel programma (frontali SX+CX+DX): il box
                # e' uno spezzone, contano le due quote minori
                candidati.append((1.0, i, out, False))
                continue
            if (abs(db[0] - dm[0]) < 3 and dm[1] and dm[2]
                    and abs(db[1] - dm[1]) / dm[1] < 0.15
                    and abs(db[2] - dm[2]) / dm[2] < 0.15):
                # RIPIEGO pezzi inclinati/sagomati: il bbox d'assieme
                # differisce da quello del programma raddrizzato, ma la
                # dim maggiore torna e le altre due sono vicine -> assegna
                # per esclusione (punteggio alto = solo se niente di meglio)
                candidati.append((2.0 + abs(db[1] - dm[1]) / dm[1],
                                  i, out, True))

    candidati.sort(key=lambda c: c[0])
    for _, i, out, consuma in candidati:
        if i in num_di:
            continue
        if consuma:
            if quota.get(out, 0) <= 0:
                continue
            quota[out] -= 1
        num_di[i] = (ETI.get(out, num_programma(manifest[out].get("name")
                                                or out)), out)

    abbinati = []
    scartati = 0
    for i, b in enumerate(boxes):
        nb = num_di.get(i)
        if nb is not None:
            abbinati.append((b, nb[0], nb[1]))
        elif dims_di(b)[1] >= 150:
            # un pezzo vero senza abbinamento credibile resta in disegno
            # con "?": meglio vederlo che perderlo
            abbinati.append((b, "?", None))
        else:
            # ferramenta e geometrie di servizio spariscono
            scartati += 1
    if not abbinati:
        img, dr = pagina()
        intestazione(dr, f"MOBILE {mobile} - ESPLOSO", "")
        dr.text((MARG, 300), "(nessun pezzo abbinabile ai programmi)",
                fill="black", font=font(32))
        return [img]
    # GRUPPI per vicinanza (i DWG hanno i mobili sparsi per il foglio):
    # union-find sui box che si toccano entro 250 mm
    n = len(abbinati)
    padre = list(range(n))

    def trova(i):
        while padre[i] != i:
            padre[i] = padre[padre[i]]
            i = padre[i]
        return i

    def vicini(a, b, m=250.0):
        return all(a["min"][k] - m <= b["max"][k]
                   and b["min"][k] - m <= a["max"][k] for k in range(3))

    for i in range(n):
        for j in range(i + 1, n):
            if vicini(abbinati[i][0], abbinati[j][0]):
                padre[trova(i)] = trova(j)
    gruppi_pos = {}
    for i in range(n):
        gruppi_pos.setdefault(trova(i), []).append(abbinati[i])
    gruppi = gruppi_pos
    # impacchetta i gruppi in fila lungo X (gap fisso), ognuno esplode
    # attorno al SUO baricentro; ogni pezzo e' un mazzo di FACCE VERE
    # (dal solido) o, in ripiego, le 6 facce dell'ingombro
    FATT = 0.55

    def facce_aabb(mn, mx):
        p = {}
        for i in (0, 1):
            for j in (0, 1):
                for k in (0, 1):
                    p[(i, j, k)] = (mx[0] if i else mn[0],
                                    mx[1] if j else mn[1],
                                    mx[2] if k else mn[2])
        idx = [((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)),
               ((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)),
               ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)),
               ((0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)),
               ((0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)),
               ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))]
        return [{"pts": [p[k] for k in f]} for f in idx]

    def costruisci(fatt):
        """Pezzi in posizione d'assieme: fatt=0.55 = esploso, fatt=0 =
        MONTATO (mobile finito). Ritorna [(facce, fori, cen, num, out, area)]."""
        res = []
        corsa = 0.0
        for gr in sorted(gruppi.values(), key=len, reverse=True):
            gx0 = min(b["min"][0] for b, _, _ in gr)
            gx1 = max(b["max"][0] for b, _, _ in gr)
            gy0 = min(b["min"][1] for b, _, _ in gr)
            gz0 = min(b["min"][2] for b, _, _ in gr)
            cx = sum((b["min"][0]+b["max"][0])/2 for b, _, _ in gr)/len(gr)
            cy = sum((b["min"][1]+b["max"][1])/2 for b, _, _ in gr)/len(gr)
            cz = sum((b["min"][2]+b["max"][2])/2 for b, _, _ in gr)/len(gr)
            for b, num, out in gr:
                bx = (b["min"][0] + b["max"][0]) / 2
                by = (b["min"][1] + b["max"][1]) / 2
                bz = (b["min"][2] + b["max"][2]) / 2
                dx = (bx - cx) * fatt + corsa - gx0
                dy = (by - cy) * fatt - gy0
                dz = (bz - cz) * fatt - gz0

                def tr(p, dx=dx, dy=dy, dz=dz):
                    return (p[0] + dx, p[1] + dy, p[2] + dz)

                if b.get("facce"):
                    facce = [{"pts": [tr(p) for p in f["pts"]]}
                             for f in b["facce"]
                             if len(f.get("pts", [])) >= 3]
                    fori = [[tr(p) for p in c]
                            for c in b.get("fori", []) if len(c) >= 3]
                else:
                    facce = [{"pts": [tr(p) for p in f["pts"]]}
                             for f in facce_aabb(b["min"], b["max"])]
                    fori = []
                dd = sorted((b["max"][k] - b["min"][k] for k in range(3)),
                            reverse=True)
                res.append((facce, fori, tr((bx, by, bz)), num, out,
                            dd[0] * dd[1]))
            corsa += (gx1 - gx0) * (1 + fatt) + 600.0
        return res

    esplosi = costruisci(0.55)
    montati = costruisci(0.0)

    def prof(p):
        return p[0] + p[1] - p[2]

    def normale_di(pts):
        nx = ny = nz = 0.0
        for a, b2 in zip(pts, pts[1:] + pts[:1]):
            nx += (a[1] - b2[1]) * (a[2] + b2[2])
            ny += (a[2] - b2[2]) * (a[0] + b2[0])
            nz += (a[0] - b2[0]) * (a[1] + b2[1])
        m = (nx * nx + ny * ny + nz * nz) ** 0.5 or 1.0
        return (nx / m, ny / m, nz / m)

    def render3d(dr, sub, retro, box, colori=False, mostra_fori=True,
                 pulito=False):
        """Disegna il 3D pieno dentro box=(x0,y0,x1,y1).
        retro=True gira di 180 attorno al verticale. colori=True: ogni
        pezzo col colore del suo materiale (mat_map). mostra_fori=False:
        niente forellini. pulito=True: resa "come AutoCAD" -> painter's a
        livello di FACCIA su TUTTI i pezzi insieme (occlusione vera fra
        pezzi, non piu' per-pezzo: cosi' i pannelli davanti coprono il
        disordine interno) + eliminazione delle facce che danno le spalle
        alla vista (backface culling con normale orientata verso l'esterno
        del pezzo) + spigoli fini. Ritorna pr(p) per i palloncini."""
        bx0, by0, bx1, by1 = box

        def T(p):                           # in coordinate di vista
            return (-p[0], -p[1], p[2]) if retro else p

        def projv(p):                       # p gia' in vista
            return ((p[0] - p[1]) * 0.866, (p[0] + p[1]) * 0.5 - p[2])

        def profv(p):                       # p gia' in vista
            return p[0] + p[1] - p[2]

        VIEW = (0.5774, 0.5774, -0.5774)    # verso la camera (grad. di prof)
        LUCE = (0.30, -0.55, 0.78)
        # una passata sola: raccolgo TUTTE le facce di TUTTI i pezzi con la
        # loro profondita' e colore; per il culling oriento la normale
        # verso l'esterno del pezzo (dal baricentro del pezzo)
        facce_g = []
        fori_g = []
        for facce, fori, cen, num, out, _a in sub:
            pc = T(cen)
            base = COL_MAT.get(mat_map.get(out)) if colori else None
            for f in facce:
                tp = [T(p) for p in f["pts"]]
                n = len(tp)
                if n < 3:
                    continue
                if pulito:
                    # area 3D vera (Newell): scarto le facce minuscole
                    # (fondo dei fori/tazze) che nella vista pulita
                    # sarebbero solo puntini di sporco
                    ax = ay = az = 0.0
                    for a, b2 in zip(tp, tp[1:] + tp[:1]):
                        ax += (a[1]-b2[1])*(a[2]+b2[2])
                        ay += (a[2]-b2[2])*(a[0]+b2[0])
                        az += (a[0]-b2[0])*(a[1]+b2[1])
                    if 0.5*(ax*ax + ay*ay + az*az) ** 0.5 < 800.0:
                        continue
                fc = (sum(p[0] for p in tp) / n, sum(p[1] for p in tp) / n,
                      sum(p[2] for p in tp) / n)
                nn = normale_di(tp)
                ov = (fc[0]-pc[0], fc[1]-pc[1], fc[2]-pc[2])
                if nn[0]*ov[0] + nn[1]*ov[1] + nn[2]*ov[2] < 0:
                    nn = (-nn[0], -nn[1], -nn[2])   # normale verso l'esterno
                if pulito and (nn[0]*VIEW[0] + nn[1]*VIEW[1]
                               + nn[2]*VIEW[2]) < -0.05:
                    continue                        # faccia che da' le spalle
                lum = abs(nn[0]*LUCE[0] + nn[1]*LUCE[1] + nn[2]*LUCE[2])
                if base:
                    fx = 0.66 + 0.34 * min(1.0, lum)
                    col = tuple(min(255, int(c * fx)) for c in base)
                else:
                    g = int(185 + 55 * min(1.0, lum))
                    col = (g, g, g)
                facce_g.append((sum(profv(p) for p in tp) / n, tp, col))
            if mostra_fori:
                for c in fori:
                    tp = [T(p) for p in c]
                    if len(tp) >= 3:
                        fori_g.append((sum(profv(p) for p in tp) / len(tp),
                                       tp))
        allp = [projv(p) for _, tp, _ in facce_g for p in tp]
        if not allp:
            return lambda p: (bx0, by0)
        x0 = min(p[0] for p in allp); x1 = max(p[0] for p in allp)
        y0 = min(p[1] for p in allp); y1 = max(p[1] for p in allp)
        aw, ah = bx1 - bx0, by1 - by0
        sc = min(aw / max(x1 - x0, 1), ah / max(y1 - y0, 1))
        ox = bx0 + (aw - (x1 - x0) * sc) / 2 - x0 * sc
        oy = by0 + (ah - (y1 - y0) * sc) / 2 - y0 * sc

        def prv(p):                         # p gia' in vista
            q = projv(p)
            return (ox + q[0] * sc, oy + q[1] * sc)

        def pr(p):
            return prv(T(p))

        ew = 1 if pulito else 2
        ec = (45, 45, 45) if pulito else (60, 60, 60)
        for _dep, tp, col in sorted(facce_g, key=lambda e: e[0]):
            poli = [prv(p) for p in tp]
            dr.polygon(poli, fill=col)
            dr.line(poli + poli[:1], fill=ec, width=ew)
        for _dep, tp in sorted(fori_g, key=lambda e: e[0]):
            poli = [prv(p) for p in tp]
            dr.line(poli + poli[:1], fill=(110, 110, 110), width=2)
        return pr

    def _incolla_shot(img, dr, png, box, etichetta):
        """Incolla lo screenshot AutoCAD nel rettangolo box mantenendo le
        proporzioni, centrato, con l'etichetta FRONTE/RETRO sotto."""
        bx0, by0, bx1, by1 = box
        try:
            s = Image.open(png).convert("RGB")
        except Exception:
            return
        aw, ah = bx1 - bx0, by1 - by0
        sc = min(aw / s.width, ah / s.height)
        nw, nh = max(1, int(s.width * sc)), max(1, int(s.height * sc))
        s = s.resize((nw, nh), Image.LANCZOS)
        px = int(bx0 + (aw - nw) / 2)
        py = int(by0 + (ah - nh) / 2)
        img.paste(s, (px, py))
        w = dr.textlength(etichetta, font=font(28, True))
        dr.text(((bx0 + bx1) / 2 - w / 2, by1 + 8), etichetta,
                fill=(80, 80, 80), font=font(28, True))

    def disegna_finito(sub):
        """UNA pagina: mobile FINITO fronte + retro. Se ci sono gli
        SCREENSHOT veri di AutoCAD (finito_shots) li incolla (resa pulita
        come apri il 3D); senno' ripiega sul 3D concettuale ricostruito
        (painter+culling). Legenda materiale->colore in basso."""
        img, dr = pagina()
        usa_shot = bool(finito_shots and finito_shots[0] and finito_shots[1])
        intestazione(dr, f"MOBILE {mobile} - COM'E' FINITO",
                     "il 3D come lo disegna AutoCAD, coi colori dei "
                     "materiali (fronte e retro)" if usa_shot else
                     "3D concettuale coi colori dei materiali "
                     "(fronte e retro)")
        mid = PAG[0] // 2
        yb = PAG[1] - 250                # spazio per la legenda in basso
        if usa_shot:
            frc, rec, leg = finito_shots
            _incolla_shot(img, dr, frc, (MARG, 250, mid - 20, yb), "FRONTE")
            _incolla_shot(img, dr, rec, (mid + 20, 250, PAG[0] - MARG, yb),
                          "RETRO")
            # legenda dai layer materiale F_* col loro colore VERO
            voci = []
            for nm, rgb in (leg or []):
                nome = nm[2:] if nm.upper().startswith("F_") else nm
                voci.append((nome.strip(), tuple(rgb)))
        else:
            render3d(dr, sub, False, (MARG, 250, mid - 20, yb),
                     colori=True, mostra_fori=False, pulito=True)
            render3d(dr, sub, True, (mid + 20, 250, PAG[0] - MARG, yb),
                     colori=True, mostra_fori=False, pulito=True)
            for testo, cx in (("FRONTE", (MARG + mid) // 2),
                              ("RETRO", (mid + PAG[0] - MARG) // 2)):
                w = dr.textlength(testo, font=font(28, True))
                dr.text((cx - w / 2, yb + 8), testo, fill=(80, 80, 80),
                        font=font(28, True))
            voci = []
            for e in sub:
                m = (mat_map.get(e[4]) or "").strip()
                if m and (m, COL_MAT.get(m, (200, 200, 200))) not in voci:
                    voci.append((m, COL_MAT.get(m, (200, 200, 200))))
        # legenda materiali in basso, a pastiglie su piu' righe
        x, y = MARG, yb + 58
        for nome, col in voci:
            dr.rectangle([x, y, x + 30, y + 22], fill=col,
                         outline=(80, 80, 80), width=2)
            et = nome[:34]
            dr.text((x + 40, y), et, fill="black", font=font(18))
            x += 40 + dr.textlength(et, font=font(18)) + 48
            if x > PAG[0] - MARG - 240:
                x = MARG; y += 34
        return img

    def disegna_montato(sub):
        """UNA pagina con il mobile montato FRONTE (sx) e RETRO (dx)."""
        img, dr = pagina()
        intestazione(dr, f"MOBILE {mobile} - 3D MONTATO (fronte e retro)",
                     "com'e' fatto il mobile finito "
                     "(pezzi ed esploso nelle pagine seguenti)")
        mid = PAG[0] // 2
        render3d(dr, sub, False, (MARG, 250, mid - 20, PAG[1] - 130))
        render3d(dr, sub, True, (mid + 20, 250, PAG[0] - MARG, PAG[1] - 130))
        for testo, cx in (("FRONTE", (MARG + mid) // 2),
                          ("RETRO", (mid + PAG[0] - MARG) // 2)):
            w = dr.textlength(testo, font=font(30, True))
            dr.text((cx - w / 2, PAG[1] - 110), testo, fill=(80, 80, 80),
                    font=font(30, True))
        return img

    def disegna_vista(sub, sottotit, numeri=True, retro=False, ferr=None):
        """Tavola esploso: 3D + palloncini + legenda. Se ferr, nella colonna
        destra (allargata) ci va anche il riepilogo FERRAMENTA del mobile
        (raggruppato per fornitore), cosi' NON serve un foglio a parte."""
        img, dr = pagina()
        intestazione(dr, f"MOBILE {mobile} - ESPLOSO"
                     + (f"  ({sottotit})" if sottotit else ""),
                     "i numeri sono i PROGRAMMI (vedi schede seguenti)")
        col_w = 560 if ferr else 360     # colonna destra + larga se c'e' ferramenta
        lx = PAG[0] - MARG - col_w
        x3d_r = lx - 20
        pr = render3d(dr, sub, retro, (MARG, 220, x3d_r, PAG[1] - 80))
        # palloncini sul pezzo con repulsione
        r = 24
        ancore = [pr(e[2]) for e in sub]
        pos = [[a[0], a[1]] for a in ancore]
        nums = [e[3] for e in sub]
        xmin, xmax = 60, x3d_r
        ymin, ymax = 230, PAG[1] - 70
        dmin = 2 * r + 8
        for _ in range(160):
            mosso = False
            for a in range(len(pos)):
                for b in range(a + 1, len(pos)):
                    ddx = pos[b][0] - pos[a][0]
                    ddy = pos[b][1] - pos[a][1]
                    d = (ddx * ddx + ddy * ddy) ** 0.5 or 0.01
                    if d < dmin:
                        s = (dmin - d) / 2; ux, uy = ddx / d, ddy / d
                        pos[a][0] -= ux*s; pos[a][1] -= uy*s
                        pos[b][0] += ux*s; pos[b][1] += uy*s
                        mosso = True
            for p in pos:
                p[0] = min(max(p[0], xmin), xmax)
                p[1] = min(max(p[1], ymin), ymax)
            if not mosso:
                break
        for i in range(len(pos)):
            px, py = pos[i]; ax, ay = ancore[i]
            if ((px-ax)**2 + (py-ay)**2) ** 0.5 > r * 1.6:
                dr.line([(ax, ay), (px, py)], fill=(130, 130, 130), width=1)
        for i in range(len(pos)):
            px, py = pos[i]
            dr.ellipse([px-r, py-r, px+r, py+r], fill="white",
                       outline="black", width=3)
            w = dr.textlength(nums[i], font=font(25, True))
            dr.text((px - w/2, py - 16), nums[i], fill="black",
                    font=font(25, True))
        # legenda dei soli pezzi presenti (nella colonna destra)
        presenti = {e[3] for e in sub}
        dr.text((lx, 200), "LEGENDA", fill="black", font=font(30, True))
        voci = []
        visti = set()
        for out, m in manifest.items():
            nn = ETI.get(out, num_programma(m.get("name") or out))
            if nn in visti or nn not in presenti:
                continue
            visti.add(nn)
            nome = m.get("name") or out
            raw = num_programma(nome)
            if nome.strip() == nn.strip() or not raw.isdigit():
                dm = m.get("dims") or []
                nome = " x ".join(f"{v:g}" for v in dm) if dm else nome
            voci.append((int(nn) if nn.isdigit() else 9999, nn, nome[:30]))
        voci.sort()
        yl = 250
        # se c'e' la ferramenta, la legenda si ferma piu' su per farle posto
        y_leg_max = 820 if ferr else (PAG[1] - 120)
        passo = min(30, (y_leg_max - yl) / max(len(voci), 1))
        fpx = 20 if passo >= 26 else 16
        for j, (_, nn, nome) in enumerate(voci):
            dr.text((lx, yl + j * passo), f"{nn}  {nome}", fill="black",
                    font=font(fpx))
        # RIEPILOGO FERRAMENTA del mobile, sotto la legenda (niente foglio a
        # parte): raggruppato per FORNITORE con subtotali
        if ferr:
            fy = 880
            tot = sum(q for q, _ in ferr.values())
            dr.text((lx, fy - 44), f"FERRAMENTA - {tot} pz", fill="black",
                    font=font(28, True))
            dr.line([(lx, fy - 8), (PAG[0] - MARG, fy - 8)], fill="black",
                    width=2)
            grp = {}
            for cod, (q, fn) in ferr.items():
                grp.setdefault((fn or "").strip() or "-", []).append((cod, q))
            nfer = len(ferr) + len(grp)
            fpasso = min(32, (PAG[1] - 80 - fy) / max(nfer, 1))
            ffx = 20 if fpasso >= 26 else (17 if fpasso >= 21 else 14)
            y = fy
            for fn in sorted(grp):
                righe = sorted(grp[fn])
                s2 = sum(q for _, q in righe)
                dr.rectangle([lx, y, PAG[0] - MARG, y + fpasso - 3],
                             fill=(232, 232, 236))
                dr.text((lx + 8, y), fn, fill="black", font=font(ffx, True))
                et = f"{s2} pz"
                w = dr.textlength(et, font=font(ffx, True))
                dr.text((PAG[0] - MARG - 8 - w, y), et, fill=(80, 80, 80),
                        font=font(ffx, True))
                y += fpasso
                for cod, q in righe:
                    dr.text((lx + 16, y), str(cod), fill="black", font=font(ffx))
                    wq = dr.textlength(str(q), font=font(ffx, True))
                    dr.text((PAG[0] - MARG - 8 - wq, y), str(q), fill="black",
                            font=font(ffx, True))
                    y += fpasso
        return img

    # foglio 1 = mobile: se ho i materiali -> FINITO a colori (concettuale,
    # fronte+retro); senno' il montato grigio tecnico (fronte+retro)
    pagine_out = [disegna_finito(montati) if mat_map
                  else disegna_montato(montati)]

    # UNA vista se pochi pezzi, DUE (struttura + interni) se tanti
    SOGLIA = 18
    if len(esplosi) <= SOGLIA:
        viste = [(esplosi, "")]
    else:
        # divisione: per nome se disponibile, senno' per area (mediana)
        def ruolo(e):
            out = e[4]
            nome = (manifest.get(out, {}).get("name") or "").upper() \
                if out else ""
            if any(k in nome for k in INT_KW):
                return "int"
            if any(k in nome for k in STRUT_KW):
                return "str"
            return None

        ruoli = [ruolo(e) for e in esplosi]
        con_nome = sum(1 for r in ruoli if r)
        if con_nome >= 0.6 * len(esplosi):
            aree = sorted(e[5] for e in esplosi)
            med = aree[len(aree) // 2]
            A = [e for e, r in zip(esplosi, ruoli)
                 if r == "str" or (r is None and e[5] >= med)]
            B = [e for e in esplosi if e not in A]
            titA, titB = "1 di 2 - STRUTTURA", "2 di 2 - INTERNI"
        else:
            aree = sorted(e[5] for e in esplosi)
            med = aree[len(aree) // 2]
            A = [e for e in esplosi if e[5] >= med]
            B = [e for e in esplosi if e[5] < med]
            titA, titB = "1 di 2 - PANNELLI PRINCIPALI", "2 di 2 - MINUTERIA"
        viste = []
        if A:
            viste.append((A, titA))
        if B:
            viste.append((B, titB))
        if not viste:
            viste = [(esplosi, "")]
    # la FERRAMENTA va sull'ULTIMA vista esploso (colonna destra), non su un
    # foglio a parte
    for k, (sub, tit) in enumerate(viste):
        ultima = (k == len(viste) - 1)
        pagine_out.append(disegna_vista(sub, tit,
                                        ferr=ferr if ultima else None))
    return pagine_out


def disegna_scheda(nome_prog, dxf_path, meta, etichetta=None):
    """Scheda del singolo programma: pianta quotata + note.
    etichetta = numero-programma coerente con esploso e scheda costo
    (dalla mappa _etichette); nel titolo il nome compare solo se e' un
    nome vero (non 'Solido_215')."""
    from dxf2tlf_masterwood import estrai_geometria
    (dims, fA, sA, fB, sB, tagli, sagome, incl, avvisi) = \
        estrai_geometria(dxf_path, prof_d14=None)
    lung, larg, alt = dims
    img, dr = pagina()
    num = etichetta or num_programma(nome_prog)
    nome_vero = nome_prog if not num_programma(nome_prog).startswith(
        nome_prog[:4]) or "_" in nome_prog else ""
    if nome_vero and nome_prog.upper().startswith("SOLIDO"):
        nome_vero = ""
    tit = f"PROGRAMMA {num}" + (f"  -  {nome_prog}" if nome_vero else "")
    if larg < 1.0 or alt < 0.1:
        intestazione(dr, tit, f"lunghezza {lung:g} mm")
        dr.text((MARG, 300), "Pezzo TONDO / TORNITO: non e' un pannello.",
                fill="black", font=font(34))
        dr.text((MARG, 360), "Vedi il programma in macchina per i dettagli.",
                fill=(90, 90, 90), font=font(28))
        return img
    intestazione(dr, tit,
                 f"{lung:g} x {larg:g} x {alt:g} mm"
                 + (f"   |   q.ta {meta.get('qty')}" if meta.get("qty") else "")
                 + (f"   |   {meta.get('mat')}" if meta.get("mat") else "")
                 + (f"   |   CNC {meta.get('cnc')}" if meta.get("cnc") else ""))

    # area disegno (centrata in verticale)
    ax, ay = MARG + 120, 260
    aw, ah = PAG[0] - 2 * MARG - 620, PAG[1] - 420
    sc = min(aw / lung, ah / larg)
    ay += (ah - larg * sc) / 2.0
    oy2 = ay + larg * sc                      # y disegno = ribaltata

    def P(x, y):
        return (ax + x * sc, oy2 - y * sc)

    # contorno (sagoma vera se c'e')
    if sagome:
        pts = [P(x, y) for x, y in sagome[0]["contorno"]]
        dr.polygon(pts, outline="black", fill=(250, 250, 250), width=3)
    else:
        dr.rectangle([P(0, larg), P(lung, 0)], outline="black",
                     fill=(250, 250, 250), width=3)

    def linea_tratt(a, b, col=(120, 120, 120), w=2):
        ll = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(ll / 12))
        for k in range(n):
            if k % 2 == 0:
                t0, t1 = k / n, min((k + 1) / n, 1.0)
                dr.line([(a[0] + (b[0] - a[0]) * t0,
                          a[1] + (b[1] - a[1]) * t0),
                         (a[0] + (b[0] - a[0]) * t1,
                          a[1] + (b[1] - a[1]) * t1)], fill=col, width=w)

    def tratteggio(pts, ch=True):
        for i in range(len(pts)):
            linea_tratt(pts[i], pts[(i + 1) % len(pts)])

    # tasche/scassi (programma A e girato B insieme, il B in grigio chiaro)
    for s, lato in ([(s, "A") for s in sA] + [(s, "B") for s in sB]):
        col = (120, 120, 120) if lato == "A" else (180, 180, 180)
        if s.get("cir"):
            x, y = (s["x"], s["y"]) if lato == "A" else (s["x"],
                                                         larg - s["y"])
            r = s["r"] * sc
            c = P(x, y)
            dr.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r],
                       outline=col, width=2)
        elif "contorno" in s:
            pts = s["contorno"] if lato == "A" else [(x, larg - y)
                                                     for x, y in s["contorno"]]
            tratteggio([P(x, y) for x, y in pts])
        else:
            x1, y1, x2, y2 = s["x1"], s["y1"], s["x2"], s["y2"]
            if lato == "B":
                y1, y2 = larg - y2, larg - y1
            tratteggio([P(x1, y1), P(x2, y1), P(x2, y2), P(x1, y2)])

    # fori verticali (A pieni, B vuoti)
    diam = {}
    for f, lato in ([(f, "A") for f in fA] + [(f, "B") for f in fB]):
        if f["plane"] != 0:
            continue
        x, y = (f["x"], f["y"]) if lato == "A" else (f["x"], larg - f["y"])
        r = max(f["r"] * sc, 3)
        c = P(x, y)
        dr.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r],
                   outline="black", width=2,
                   fill=(60, 60, 60) if lato == "A" else None)
        chiave = (round(2 * f["r"], 1), round(f["prof"], 1),
                  "sopra" if lato == "A" else "sotto")
        diam[chiave] = diam.get(chiave, 0) + 1

    # FORI DI TESTA (sui bordi): la "U" tratteggiata che entra dal bordo,
    # come da disegno tecnico (linee nascoste)
    for f in fA:
        if f["plane"] == 0:
            continue
        r, prof = f["r"], min(f["prof"], max(lung, larg))
        col = (90, 90, 90)
        if f["plane"] == 1:        # dietro (y = larg), entra verso il basso
            x = f["x"]
            linea_tratt(P(x - r, larg), P(x - r, larg - prof), col)
            linea_tratt(P(x + r, larg), P(x + r, larg - prof), col)
            linea_tratt(P(x - r, larg - prof), P(x + r, larg - prof), col)
        elif f["plane"] == 2:      # davanti (y = 0)
            x = f["x"]
            linea_tratt(P(x - r, 0), P(x - r, prof), col)
            linea_tratt(P(x + r, 0), P(x + r, prof), col)
            linea_tratt(P(x - r, prof), P(x + r, prof), col)
        elif f["plane"] == 3:      # sinistra (x = 0)
            y = f["x"]
            linea_tratt(P(0, y - r), P(prof, y - r), col)
            linea_tratt(P(0, y + r), P(prof, y + r), col)
            linea_tratt(P(prof, y - r), P(prof, y + r), col)
        else:                      # destra (x = lung)
            y = f["x"]
            linea_tratt(P(lung, y - r), P(lung - prof, y - r), col)
            linea_tratt(P(lung, y + r), P(lung - prof, y + r), col)
            linea_tratt(P(lung - prof, y - r), P(lung - prof, y + r), col)

    # lamate
    for t in tagli:
        dr.line([P(t["x"], 0), P(t["x"], larg)], fill="black", width=3)
        dr.line([P(t["x"] + t["gap"], 0), P(t["x"] + t["gap"], larg)],
                fill="black", width=3)

    # quote d'ingombro
    qy = oy2 + 46
    dr.line([P(0, 0)[0], qy, P(lung, 0)[0], qy], fill="black", width=2)
    testo = f"{lung:g}"
    w = dr.textlength(testo, font=font(28))
    dr.text(((P(0, 0)[0] + P(lung, 0)[0] - w) / 2, qy + 6), testo,
            fill="black", font=font(28))
    qx = ax - 46
    dr.line([qx, P(0, 0)[1], qx, P(0, larg)[1]], fill="black", width=2)
    dr.text((qx - 70, (P(0, 0)[1] + P(0, larg)[1]) / 2 - 16),
            f"{larg:g}", fill="black", font=font(28))

    # tabella fori a destra
    tx = PAG[0] - MARG - 420
    dr.text((tx, 220), "FORI (pianta)", fill="black", font=font(28, True))
    y = 266
    for (d, p, lato), n in sorted(diam.items()):
        dr.text((tx, y), f"{n} x  O {d:g}  prof {p:g}  ({lato})",
                fill="black", font=font(24))
        y += 34
    lat = {}
    for f in fA:
        if f["plane"] == 0:
            continue
        bordo = {1: "dietro", 2: "davanti", 3: "sinistra",
                 4: "destra"}[f["plane"]]
        chiave = (bordo, round(2 * f["r"], 1), round(f["prof"], 1))
        lat[chiave] = lat.get(chiave, 0) + 1
    if lat:
        y += 14
        dr.text((tx, y), "FORI SUI BORDI", fill="black", font=font(28, True))
        y += 44
        for (bordo, d, p), n in sorted(lat.items()):
            dr.text((tx, y), f"{n} x  O {d:g}  prof {p:g}  ({bordo})",
                    fill="black", font=font(24))
            y += 34
    note = []
    if sagome:
        note.append("profilo SAGOMATO (contorno)")
    for c in incl:
        note.append(f"taglio INCLINATO {c['beta']:g} gradi")
    if tagli:
        note.append(f"{len(tagli)} lamate sezionatura")
    if sB or [f for f in fB if f["plane"] == 0]:
        note.append("lavorazioni anche dal SOTTO (_B)")
    if note:
        y += 14
        dr.text((tx, y), "NOTE", fill="black", font=font(28, True))
        y += 44
        for nvo in note:
            dr.text((tx, y), "- " + nvo, fill="black", font=font(24))
            y += 34
    return img


def _facce_da_dxf(dxf_path, log=print):
    """Facce piane VERE dei 3DSOLID (coordinate d'assieme, transform ACIS
    applicata) dal DXF esportato via COM, col parser di casa (acis_topo).
    Ritorna [{'bb': (mn, mx), 'facce': [{'pts': [...]}], 'fori': [...]}]."""
    try:
        import ezdxf
        d = r"C:\Users\User\Desktop\CLAUDE\Dxf2Tlf"
        if d not in sys.path:
            sys.path.append(d)
        import acis_topo
        pezzi = []
        doc = ezdxf.readfile(dxf_path)
        for e in doc.modelspace().query("3DSOLID"):
            lay = (e.dxf.layer or "").upper()
            if (lay.startswith("FERRAMENTA") or lay.startswith("FORO_")
                    or lay.startswith("SCASSO_")):
                continue
            dati = e.sat if e.sat else e.sab
            try:
                fl, _ = acis_topo.tasche_da_solido(dati)
            except Exception:
                continue
            facce, fori, pts_tutti = [], [], []
            for fa in fl:
                for lp in fa["loops"]:
                    pts = [(p.x, p.y, p.z) for p in lp["punti"]]
                    if len(pts) < 3:
                        continue
                    if lp["esterno"]:
                        facce.append({"pts": pts})
                        pts_tutti.extend(pts)
                    else:
                        fori.append(pts)
            if not facce:
                continue
            mn = [min(p[i] for p in pts_tutti) for i in range(3)]
            mx = [max(p[i] for p in pts_tutti) for i in range(3)]
            pezzi.append({"bb": (mn, mx), "facce": facce, "fori": fori})
        return pezzi
    except Exception as ex:
        log(f"    [!] facce vere non lette ({ex}): esploso a scatole")
        return []


def boxes_da_dwg(dwg_path, log=print):
    """Bbox dei 3DSOLID in posizione d'ASSIEME dal DWG sorgente, via
    AutoCAD COM (aperto in sola lettura, mai salvato). Ferramenta e
    coltelli esclusi per layer. [] se il DWG non si puo' aprire."""
    import time
    try:
        import win32com.client
        acad = win32com.client.Dispatch("AutoCAD.Application")
        acad.Visible = True
        doc = None
        for _ in range(20):
            try:
                doc = acad.Documents.Open(dwg_path, True)   # read-only
                break
            except Exception:
                time.sleep(1)
        if doc is None:
            log("  [!] DWG non apribile (gia' aperto?): niente esploso")
            return []
        boxes = []
        try:
            ms = doc.ModelSpace
            for i in range(ms.Count):
                try:
                    e = ms.Item(i)
                    if e.ObjectName != "AcDb3dSolid":
                        continue
                    lay = (e.Layer or "").upper()
                    if (lay.startswith("FERRAMENTA") or lay.startswith("FORO_")
                            or lay.startswith("SCASSO_")):
                        continue
                    mn, mx = e.GetBoundingBox()
                    b = {"min": list(mn), "max": list(mx), "vol": 0}
                    # nome pezzo + materiale dal layer "NOME -- MATERIALE"
                    # (variante senza blocchi, nome sul solido): serve per
                    # l'abbinamento ESATTO box->programma nell'esploso
                    lay0 = e.Layer or ""
                    if " -- " in lay0:
                        parti = [p.strip() for p in lay0.split(" -- ")]
                        b["nome"] = parti[0]
                        b["materiale"] = parti[-1]
                    try:
                        b["vol"] = float(e.Volume)  # volume vero: serve
                    except Exception:               # per i pezzi inclinati
                        pass
                    try:
                        # baricentro + assi d'inerzia: per DISEGNARE i
                        # pezzi inclinati come tavole orientate vere
                        b["cen"] = list(e.Centroid)
                        pd = list(e.PrincipalDirections)
                        b["assi"] = [pd[0:3], pd[3:6], pd[6:9]]
                        b["mom"] = list(e.PrincipalMoments)
                    except Exception:
                        pass
                    boxes.append(b)
                except Exception:
                    continue
            # il disegno (aperto in sola lettura) viene RI-SALVATO come
            # DXF R2000 temporaneo: e' il formato coi SAT testuali che il
            # parser ACIS di casa legge (i SAB moderni AC1032 no); da li'
            # escono le FACCE VERE. L'originale su disco non si tocca.
            try:
                tmpd = tempfile.mkdtemp(prefix="esploso_dwg_")
                f2000 = os.path.join(tmpd, "assieme_2000.dxf")
                doc.SaveAs(f2000, 13)             # 13 = ac2000_dxf
                agganciati = 0
                if os.path.isfile(f2000):
                    for pz in _facce_da_dxf(f2000, log):
                        c = [(pz["bb"][0][i] + pz["bb"][1][i]) / 2
                             for i in range(3)]
                        for b in boxes:
                            bc = [(b["min"][i] + b["max"][i]) / 2
                                  for i in range(3)]
                            if all(abs(c[i] - bc[i]) < 5 for i in range(3)):
                                b["facce"] = pz["facce"]
                                b["fori"] = pz["fori"]
                                agganciati += 1
                                break
                if agganciati:
                    log(f"  facce vere: {agganciati}/{len(boxes)} pezzi")
                else:
                    log("    [!] niente facce vere dal DWG: "
                        "esploso a scatole")
                import shutil
                shutil.rmtree(tmpd, ignore_errors=True)
            except Exception as ex:
                log(f"    [!] facce dal DWG fallite ({ex}): "
                    "esploso a scatole")
        finally:
            try:
                doc.Close(False)
            except Exception:
                pass
        return boxes
    except Exception as ex:
        log(f"  [!] esploso dal DWG fallito: {ex}")
        return []


def _pulisci_shot(png_in, png_out):
    """Sfondo scuro AutoCAD -> BIANCO (floodfill dai bordi) + ritaglio
    stretto sul mobile. Ritorna (w, h) o None."""
    try:
        from PIL import ImageChops
        im = Image.open(png_in).convert("RGB")
        w, h = im.size
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, w, 46], fill=(255, 255, 255))   # via i tasti finestra
        for sx, sy in ((2, 60), (w-2, 60), (2, h-2), (w-2, h-2),
                       (w//2, h-2), (w//2, 60)):
            try:
                ImageDraw.floodfill(im, (sx, sy), (255, 255, 255), thresh=70)
            except Exception:
                pass
        bg = Image.new("RGB", im.size, (255, 255, 255))
        diff = ImageChops.difference(im, bg).convert("L")
        bb = diff.point(lambda p: 255 if p > 18 else 0).getbbox()
        if bb:
            p = 14
            im = im.crop((max(0, bb[0]-p), max(0, bb[1]-p),
                          min(w, bb[2]+p), min(h, bb[3]+p)))
        im.save(png_out)
        return im.size
    except Exception:
        return None


# palette ACI VERIFICATA (indice AutoCAD -> RGB reale letto da ly.TrueColor):
# coloro i solidi con e.Color=ACI e la legenda usa lo stesso RGB, cosi'
# render e legenda combaciano sempre
PALETTE_ACI = [
    (30, (255, 127, 0)), (5, (0, 0, 255)), (3, (0, 255, 0)),
    (1, (255, 0, 0)), (204, (114, 0, 153)), (4, (0, 255, 255)),
    (41, (255, 223, 127)), (171, (127, 127, 255)), (103, (102, 204, 127)),
    (6, (255, 0, 255)), (31, (255, 191, 127)), (2, (255, 255, 0)),
]


def screenshots_da_dwg(dwg_path, manifest=None, mobile=None, mat_map=None,
                       log=print):
    """Apre il DWG (sola lettura, mai salvato) e cattura il mobile FINITO
    come lo disegna AutoCAD (vista SHADED concettuale) FRONTE (SE iso) +
    RETRO (NW iso) con PNGOUT, sfondo portato a bianco e ritagliato.
    Accende SOLO i layer che portano solidi (via numeri/quote/testi e
    ferramenta/fori). Se il DWG NON ha i layer materiale F_* (solidi tutti
    su un layer), ricolora ogni solido per MATERIALE (dimensioni->programma
    ->materiale, palette ACI). Ritorna (png_fronte, png_retro, legenda) con
    legenda=[(materiale,(r,g,b))]; (None, None, []) se non ci riesce."""
    import time
    try:
        import win32com.client
        import win32gui
        import win32con
    except Exception as ex:
        log(f"    [!] screenshot 3D non disponibili ({ex})")
        return None, None, []
    manifest = manifest or {}
    mat_map = mat_map or {}
    tmp = tempfile.mkdtemp(prefix="shot3d_")
    fr = os.path.join(tmp, "fronte.png")
    re = os.path.join(tmp, "retro.png")
    frc = os.path.join(tmp, "fronte_c.png")
    rec = os.path.join(tmp, "retro_c.png")

    def wait_file(p, t=45):
        prev = -1
        for _ in range(t * 4):
            if os.path.isfile(p):
                s = os.path.getsize(p)
                if s > 0 and s == prev:
                    return True
                prev = s
            time.sleep(0.25)
        return os.path.isfile(p)

    def cattura(doc, preset, path):
        try:
            if os.path.isfile(path):
                os.remove(path)
        except OSError:
            pass
        doc.SendCommand("_.-VIEW\n%s\n" % preset)
        doc.SendCommand("_.ZOOM\n_E\n")
        doc.SendCommand("_.ZOOM\n0.92X\n")
        time.sleep(0.8)
        doc.SendCommand('_.PNGOUT\n"%s"\n\n' % path.replace("\\", "/"))
        return wait_file(path)

    doc = None
    try:
        acad = win32com.client.Dispatch("AutoCAD.Application")
        acad.Visible = True
        try:
            hwnd = acad.HWND
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetWindowPos(hwnd, 0, 60, 30, 1150, 1380,
                                  win32con.SWP_NOZORDER)
        except Exception:
            pass
        for _ in range(20):
            try:
                doc = acad.Documents.Open(dwg_path, True)
                break
            except Exception:
                time.sleep(1)
        if doc is None:
            log("    [!] DWG non apribile per gli screenshot 3D")
            return None, None, []
        time.sleep(1)
        ms = doc.ModelSpace
        # ESPLODO i blocchi (solo in memoria, doc read-only mai salvato):
        # cosi' i solidi ANNIDATI diventano di primo livello e la
        # ricolorazione per materiale li raggiunge. Explode NON toglie il
        # riferimento originale -> lo cancello. Piu' giri per i blocchi
        # annidati
        for _giro in range(5):
            refs = []
            for i in range(ms.Count):
                try:
                    e = ms.Item(i)
                    if e.ObjectName in ("AcDbBlockReference",
                                        "AcDbMInsertBlock"):
                        refs.append(e)
                except Exception:
                    continue
            if not refs:
                break
            for e in refs:
                try:
                    e.Explode()
                    e.Delete()
                except Exception:
                    pass
        # solidi veri (no ferramenta/fori/scassi) e i loro layer
        solidi = []
        solid_lay = set()
        for i in range(ms.Count):
            try:
                e = ms.Item(i)
                if e.ObjectName != "AcDb3dSolid":
                    continue
                u = (e.Layer or "").upper()
                if (u.startswith("FERRAMENTA") or u.startswith("FORO_")
                        or u.startswith("SCASSO_")):
                    continue
                solidi.append(e)
                solid_lay.add(e.Layer)
            except Exception:
                continue
        # ACCENDO SOLO i layer che portano solidi: cosi' spariscono numeri,
        # quote e testi (che stanno su altri layer) senza sapere il loro nome
        for i in range(doc.Layers.Count):
            ly = doc.Layers.Item(i)
            try:
                ly.LayerOn = (ly.Name in solid_lay)
            except Exception:
                pass
        mat_lay = [l for l in solid_lay if (l or "").upper().startswith("F")]
        sep_lay = [l for l in solid_lay if " -- " in (l or "")]
        leg = []
        if len(sep_lay) >= max(2, len(solid_lay) * 0.5):
            # VARIANTE senza blocchi col NOME sul solido: il layer e'
            # "NOME_PEZZO -- MATERIALE" (convenzione [[project-mobile-tv-25A018]]
            # / esplodi-nomi.lsp) -> materiale ESATTO per-solido letto dal nome
            # del layer, niente stime per dimensioni. Ricoloro con la palette
            mats = sorted({l.split(" -- ")[-1].strip() for l in sep_lay
                           if l.split(" -- ")[-1].strip()})
            matcol = {mt: PALETTE_ACI[i % len(PALETTE_ACI)]
                      for i, mt in enumerate(mats)}
            usati = set()
            for e in solidi:
                try:
                    lay = e.Layer or ""
                    if " -- " in lay:
                        mt = lay.split(" -- ")[-1].strip()
                        if mt in matcol:
                            e.Color = matcol[mt][0]
                            usati.add(mt)
                except Exception:
                    continue
            leg = [(mt, matcol[mt][1]) for mt in mats if mt in usati]
            log(f"  materiale dal NOME LAYER (NOME -- MATERIALE): "
                f"{len(usati)} materiali")
        elif len(mat_lay) >= 2:
            # il DWG HA i layer materiale (F_*): colori gia' a posto, legenda
            # dai layer col loro RGB vero
            for i in range(doc.Layers.Count):
                ly = doc.Layers.Item(i)
                if (ly.Name or "").upper().startswith("F_"):
                    try:
                        tc = ly.TrueColor
                        leg.append((ly.Name, (tc.Red, tc.Green, tc.Blue)))
                    except Exception:
                        leg.append((ly.Name, (170, 170, 170)))
        else:
            # DWG monocromo: RICOLORO ogni solido per MATERIALE
            # (dimensioni bbox -> programma -> materiale, palette ACI)
            dimmat = {}
            sp_cnt = {}
            for out, m in manifest.items():
                mat = (mat_map.get(out) or "").strip()
                dm = m.get("dims") or []
                if mat and len(dm) == 3:
                    k = tuple(sorted(round(v) for v in dm))
                    dimmat.setdefault(k, mat)
                    sp = k[0]            # spessore = quota minore
                    sp_cnt.setdefault(sp, {}).setdefault(mat, 0)
                    sp_cnt[sp][mat] += 1
            # materiale dominante per ogni spessore (ripiego per i pezzi non
            # abbinabili per quote esatte, es. fianchi tagliati su misura)
            sp2mat = {sp: max(c, key=c.get) for sp, c in sp_cnt.items()}
            mats = sorted({v for v in dimmat.values()})
            matcol = {mt: PALETTE_ACI[i % len(PALETTE_ACI)]
                      for i, mt in enumerate(mats)}

            def materiale_di(dims):
                k = tuple(sorted(round(v) for v in dims))
                if k in dimmat:
                    return dimmat[k]
                best, bd = None, 3.0     # tolleranza 3 mm sulle 3 quote
                for kk, mt in dimmat.items():
                    d = max(abs(a-b) for a, b in zip(k, kk))
                    if d < bd:
                        bd, best = d, mt
                if best:
                    return best
                # ripiego: materiale dominante dello spessore PIU' VICINO
                # (senza soglia: cosi' nessun pezzo resta senza materiale ->
                # niente colori fuori legenda)
                sp = k[0]
                best, bd = None, 1e9
                for s, mt in sp2mat.items():
                    if abs(s - sp) < bd:
                        bd, best = abs(s - sp), mt
                return best

            usati = set()
            for e in solidi:
                try:
                    mn, mx = e.GetBoundingBox()
                    dims = [mx[j]-mn[j] for j in range(3)]
                    mt = materiale_di(dims)
                    if mt:
                        aci, _rgb = matcol[mt]
                        e.Color = aci
                        usati.add(mt)
                except Exception:
                    continue
            leg = [(mt, matcol[mt][1]) for mt in mats if mt in usati]
            log(f"  3D monocromo: ricolorati {len(usati)} materiali")
        try:
            doc.SetVariable("GRIDMODE", 0)
        except Exception:
            pass
        try:
            doc.SetVariable("FILEDIA", 0)
        except Exception:
            pass
        doc.SendCommand("_.UCSICON\n_OFF\n")
        doc.SendCommand("_.VSCURRENT\n_C\n")     # concettuale (shaded, come img2)
        time.sleep(1)
        okf = cattura(doc, "_SEISO", fr)
        okr = cattura(doc, "_NWISO", re)
        try:
            doc.SetVariable("FILEDIA", 1)
        except Exception:
            pass
        if not (okf and okr):
            log("    [!] PNGOUT 3D non riuscito")
            return None, None, []
        _pulisci_shot(fr, frc)
        _pulisci_shot(re, rec)
        log("  screenshot 3D FRONTE/RETRO da AutoCAD ok")
        return frc, rec, leg
    except Exception as ex:
        log(f"    [!] screenshot 3D falliti ({ex})")
        return None, None, []
    finally:
        try:
            if doc is not None:
                doc.Close(False)
        except Exception:
            pass


def ferramenta_da_dwg(dwg_path, log=print):
    """Lista ferramenta dal DWG d'assieme (variante coi nomi sui solidi):
    ogni pezzo di ferramenta e' su un layer "Ferramenta -- CODICE -- FORNITORE"
    e la QUANTITA' e' il numero di solidi su quel layer (verificato = q.ta
    della distinta). Ritorna {codice: (qta, fornitore)} o {} se non ci
    riesce. Sola lettura, doc mai salvato."""
    import time
    try:
        import win32com.client
    except Exception:
        return {}
    doc = None
    try:
        acad = win32com.client.Dispatch("AutoCAD.Application")
        acad.Visible = True
        for _ in range(20):
            try:
                doc = acad.Documents.Open(dwg_path, True)
                break
            except Exception:
                time.sleep(1)
        if doc is None:
            return {}
        ferr = {}
        ms = doc.ModelSpace
        for i in range(ms.Count):
            try:
                e = ms.Item(i)
                if e.ObjectName != "AcDb3dSolid":
                    continue
                lay = e.Layer or ""
                if not lay.upper().startswith("FERRAMENTA"):
                    continue
                parti = [p.strip() for p in lay.split(" -- ")]
                if len(parti) < 2 or not parti[1]:
                    continue
                cod = parti[1]
                forn = parti[2] if len(parti) >= 3 else ""
                q, f0 = ferr.get(cod, (0, forn))
                ferr[cod] = (q + 1, f0 or forn)
            except Exception:
                continue
        if ferr:
            log(f"  ferramenta dal dwg: {len(ferr)} codici "
                f"({sum(q for q, _ in ferr.values())} pezzi)")
        return ferr
    except Exception as ex:
        log(f"    [!] ferramenta dal dwg fallita ({ex})")
        return {}
    finally:
        try:
            if doc is not None:
                doc.Close(False)
        except Exception:
            pass


def _dwg_ha_nomi(dwg_path):
    """True se il DWG usa la convenzione 'NOME_PEZZO -- MATERIALE' sui layer
    dei pezzi (la VARIANTE): controllo VELOCE sui soli nomi dei layer (niente
    SaveAs), sola lettura. Serve a preferire il DWG per l'esploso SOLO quando
    porta i nomi -> i lavori non-variante (es. 21032) restano sullo STEP."""
    import time
    try:
        import win32com.client
    except Exception:
        return False
    doc = None
    try:
        acad = win32com.client.Dispatch("AutoCAD.Application")
        acad.Visible = True
        for _ in range(20):
            try:
                doc = acad.Documents.Open(dwg_path, True)
                break
            except Exception:
                time.sleep(1)
        if doc is None:
            return False
        for i in range(doc.Layers.Count):
            nm = doc.Layers.Item(i).Name or ""
            u = nm.upper()
            if (" -- " in nm and not u.startswith("FERRAMENTA")
                    and not u.startswith("FORO_")
                    and not u.startswith("SCASSO_")):
                return True
        return False
    except Exception:
        return False
    finally:
        try:
            if doc is not None:
                doc.Close(False)
        except Exception:
            pass


def disegna_ferramenta(mobile, ferr):
    """Pagina riepilogo FERRAMENTA del mobile (da ordinare), RAGGRUPPATA per
    FORNITORE con subtotali. ferr = {codice: (qta, fornitore)}."""
    img, dr = pagina()
    tot = sum(q for q, _ in ferr.values())
    intestazione(dr, f"MOBILE {mobile} - FERRAMENTA",
                 f"da ordinare per questo mobile - {len(ferr)} codici, "
                 f"{tot} pezzi in tutto (raggruppati per fornitore)")
    grp = {}
    for cod, (q, fn) in ferr.items():
        grp.setdefault((fn or "").strip() or "(fornitore non indicato)",
                       []).append((cod, q))
    forn_ord = sorted(grp)
    n_righe = len(ferr) + len(forn_ord)
    y0, y1 = 200, PAG[1] - 70
    passo = min(46, (y1 - y0) / max(n_righe, 1))
    fpx = 26 if passo >= 34 else (22 if passo >= 26 else 18)
    x_cod = MARG + 24
    x_q = PAG[0] - MARG - 30
    y = y0
    for fn in forn_ord:
        righe = sorted(grp[fn])
        sub = sum(q for _, q in righe)
        dr.rectangle([MARG, y, PAG[0] - MARG, y + passo - 4],
                     fill=(232, 232, 236))
        dr.text((MARG + 12, y + 1), fn, fill="black", font=font(fpx, True))
        et = f"{sub} pz"
        w = dr.textlength(et, font=font(fpx, True))
        dr.text((PAG[0] - MARG - 12 - w, y + 1), et, fill=(80, 80, 80),
                font=font(fpx, True))
        y += passo
        for cod, q in righe:
            dr.text((x_cod, y), str(cod)[:64], fill="black", font=font(fpx))
            wq = dr.textlength(str(q), font=font(fpx, True))
            dr.text((x_q - wq, y), str(q), fill="black", font=font(fpx, True))
            y += passo
    return img


def genera(base, camera, step=None, out_dir=None, log=print, dwg=None):
    pu = os.path.join(base, "PROGRAMMI_UNICI")
    manifest = json.load(open(os.path.join(base, "_manifest.json"),
                              encoding="utf-8"))
    # programmi del mobile: membri con quella camera/gruppo
    def del_mobile(m):
        stanze = m.get("rooms") or m.get("groups") or []
        return camera in stanze
    miei = {k: v for k, v in manifest.items() if del_mobile(v)}
    if not miei:
        raise RuntimeError(f"nessun programma per {camera}")
    log(f"  {camera}: {len(miei)} programmi")

    boxes = []
    finito_shots = None
    # sorgente esploso: preferisco il DWG SOLO se i suoi solidi sono NOMINATI
    # (layer "NOME -- MATERIALE" -> abbinamento ESATTO pezzo->programma nei
    # palloncini). Cosi' i lavori non-variante (es. 21032) restano sullo STEP
    # com'erano; il DWG non nominato resta il ripiego finale (es. demo)
    if dwg and os.path.isfile(dwg) and _dwg_ha_nomi(dwg):
        boxes = boxes_da_dwg(dwg, log)
        if boxes:
            _nn = sum(1 for b in boxes if b.get("nome"))
            log(f"  esploso: {len(boxes)} solidi dal dwg, {_nn} coi nomi "
                "(abbinamento esatto)")
    if not boxes and step and os.path.isfile(step):
        # se FreeCAD manca o scade il tempo si perde SOLO l'esploso,
        # mai l'intero libretto (le schede non hanno bisogno di FreeCAD)
        try:
            import shutil
            tmp = tempfile.mkdtemp(prefix="esploso_")
            oj = os.path.join(tmp, "boxes.json")
            # freecadcmd storpia i caratteri speciali nei percorsi (es.
            # l'apostrofo tipografico di una cartella cliente: esce
            # "pulito" ma senza fare nulla): gli si da' SEMPRE una copia
            # dello STEP su percorso semplice
            s_tmp = os.path.join(tmp,
                                 "assieme" + os.path.splitext(step)[1])
            shutil.copyfile(step, s_tmp)
            r = subprocess.run([FREECADCMD, ESPLOSO_FC, "--", s_tmp, oj],
                               capture_output=True, timeout=600)
            if b"ESPLOSO-OK" in (r.stdout or b""):
                boxes = json.load(open(oj, encoding="utf-8"))
                log(f"  esploso: {len(boxes)} solidi dallo step")
            else:
                log("    [!] esploso dallo step non riuscito "
                    "(FreeCAD non ha letto il file): "
                    "libretto senza copertina-esploso")
            shutil.rmtree(tmp, ignore_errors=True)
        except Exception as ex:
            log(f"    [!] esploso dallo step non riuscito ({ex}): "
                "libretto senza copertina-esploso")
    if (not boxes and dwg and os.path.isfile(dwg)
            and not (step and os.path.isfile(step))):
        # DWG non nominato e NIENTE step (es. demo): esploso dal dwg, a quote.
        # Se lo step c'era ma e' fallito NON ripiego sul dwg: il lavoro
        # non-variante (es. 21032) resta "dallo step o niente", com'era
        boxes = boxes_da_dwg(dwg, log)
        if boxes:
            log(f"  esploso: {len(boxes)} solidi dal dwg")

    # materiale per programma dal riepilogo -> colori. La colonna MATERIALE
    # si cerca per NOME di intestazione: le due filiere hanno layout diversi
    # (generico: MATERIALE in col 7; 21032: MATERIALE in col 2, in col 7 c'e'
    # lo SPESSORE) -> con l'indice fisso si coloravano i pezzi per spessore
    mat_map = {}
    try:
        import openpyxl
        rp = os.path.join(pu, "_RIEPILOGO_programmi_unici.xlsx")
        if os.path.isfile(rp):
            wb = openpyxl.load_workbook(rp, read_only=True, data_only=True)
            ws = wb["PROGRAMMI_UNICI"]
            righe = ws.iter_rows(min_row=1, values_only=True)
            hdr = next(righe)
            ci_file, ci_mat = 0, None
            for j, h in enumerate(hdr):
                hs = str(h or "").strip().upper()
                if hs == "MATERIALE":
                    ci_mat = j
                elif hs.startswith("FILE"):
                    ci_file = j
            if ci_mat is None:
                ci_mat = 7          # ripiego: vecchio indice fisso
            for r in righe:
                if (r and len(r) > max(ci_file, ci_mat)
                        and r[ci_file] and r[ci_mat]):
                    mat_map[r[ci_file]] = str(r[ci_mat])
    except Exception as ex:
        log(f"    [!] materiali per la vista a colori non letti ({ex})")

    # pagina COM'E' FINITO = SCREENSHOT veri del 3D shaded da AutoCAD (piu'
    # puliti del 3D ricostruito): serve un DWG 3D, anche quando l'esploso
    # viene dallo STEP. Se il DWG non ha i layer materiale, ricolora per
    # materiale. Senza DWG -> ripiego sul 3D concettuale ricostruito.
    if dwg and os.path.isfile(dwg):
        try:
            fr, re, leg = screenshots_da_dwg(dwg, miei, camera, mat_map, log)
            if fr and re:
                finito_shots = (fr, re, leg)
        except Exception as ex:
            log(f"    [!] screenshot 3D saltati ({ex})")

    # numerazione UNICA (esploso, schede, scheda costo) da _etichette
    ETI = _etichette(miei)
    # ferramenta del mobile dai layer del DWG (Ferramenta -- CODICE -- FORNITORE,
    # q.ta = n. solidi): va nella COLONNA DESTRA dell'ultima vista esploso
    # (stessa pagina, niente foglio a parte)
    ferr_mob = {}
    if dwg and os.path.isfile(dwg):
        try:
            ferr_mob = ferramenta_da_dwg(dwg, log) or {}
        except Exception as ex:
            log(f"    [!] ferramenta dal dwg saltata ({ex})")
    pagine = list(pagina_esploso(camera, miei, boxes, miei, mat_map,
                                 finito_shots=finito_shots, ferr=ferr_mob))

    def _ord(kv):
        e = ETI.get(kv[0], num_programma(kv[1].get("name") or kv[0]))
        return (int(e) if str(e).isdigit() else 9999, str(e))
    for out, m in sorted(miei.items(), key=_ord):
        dxf = os.path.join(pu, out)
        if not os.path.isfile(dxf):
            continue
        # quantita' della SOLA camera del libretto, non del programma
        # unificato su tutti i mobili (members = coppie [camera, file])
        qty_cam = sum(1 for mem in (m.get("members") or [])
                      if mem and mem[0] == camera)
        meta = {"qty": qty_cam or m.get("qty"), "mat": m.get("materiale"),
                "cnc": m.get("cnc")}
        try:
            pagine.append(disegna_scheda(m.get("name") or out, dxf, meta,
                                         etichetta=ETI.get(out)))
        except Exception as ex:
            log(f"    [!] scheda {out}: {ex}")

    out_dir = out_dir or os.path.join(base, "SCHEDE_PDF")
    os.makedirs(out_dir, exist_ok=True)
    pdf = os.path.join(out_dir, f"SCHEDE_{camera}.pdf")
    # pagine RGB + JPEG (DCTDecode): tiene i COLORI (vista materiali) e
    # resta leggero (~200 KB/pag). Si scrive su un temporaneo e si scambia
    # solo alla fine: un PDF bloccato (viewer/Dropbox) non viene troncato.
    tmp_pdf = pdf + ".parte"
    Image.init()
    try:
        pag = [p.convert("RGB") for p in pagine]
        pag[0].save(tmp_pdf, format="PDF", save_all=True,
                    append_images=pag[1:], resolution=200, quality=90)
    except Exception as ex:
        log(f"    [!] pagine JPEG non riuscite ({ex}): ripiego in tavolozza")
        pag = [p.convert("P", palette=Image.ADAPTIVE, colors=64)
               for p in pagine]
        pag[0].save(tmp_pdf, format="PDF", save_all=True,
                    append_images=pag[1:], resolution=200)
    try:
        os.replace(tmp_pdf, pdf)
    except PermissionError:
        try:
            os.remove(tmp_pdf)
        except OSError:
            pass
        raise RuntimeError(f"{os.path.basename(pdf)} bloccato (aperto in un "
                           "viewer o in sincronizzazione?): chiudilo e "
                           "rigenera")
    log(f"  -> {pdf} ({len(pagine)} pagine)")
    return pdf


if __name__ == "__main__":
    genera(sys.argv[1], sys.argv[2],
           sys.argv[3] if len(sys.argv) > 3 else None)
