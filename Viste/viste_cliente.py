# -*- coding: utf-8 -*-
"""VISTE 2D PER IL CLIENTE dal 3D di un mobile.

Da un DWG/STEP 3D (o da una lista di box gia' estratti) produce UNA TAVOLA A3
con PIANTA, PROSPETTO, SEZIONE A-A (verticale) e SEZIONE B-B (orizzontale),
quotate (ingombri + divisioni principali) e colorate per MATERIALE con legenda
e cartiglio. Salva sia PDF (cliente) sia DWG (via DXF ezdxf -> AutoCAD).

I pannelli sono trattati come scatole (bbox): per un cliente che non legge i 3D
e' esattamente cio' che serve - viste pulite, quotate, coi materiali.

Uso:
    from viste_cliente import genera_viste_cliente
    genera_viste_cliente(r"...mobile_3D.dwg", out_dir, commessa="25-A018",
                         mobile="MOBILE TV")

Convenzione assi (verificata sui DWG di casa): X=larghezza, Y=profondita',
Z=altezza.
"""
import os
import time
import datetime

# ----------------------------------------------------------------------------
# COSTANTI
# ----------------------------------------------------------------------------
A3_W, A3_H = 420.0, 297.0            # mm, orizzontale
MARG = 8.0                            # margine cornice
TITLE_H = 30.0                        # altezza striscia cartiglio in basso
SCALE_STD = [5, 10, 15, 20, 25, 50, 75, 100]   # scale ammesse (1:n)
PANNELLO_MAX_SP = 60.0               # oltre questo non e' un "pannello sottile"
DIV_SPAN_MIN = 0.35                  # una divisione deve coprire >=35% della vista

# palette (RGB) per i materiali - tinte piene per legenda/bordi
PALETTE = [
    (0, 114, 178), (213, 94, 0), (0, 158, 115), (204, 121, 167),
    (230, 159, 0), (86, 180, 233), (150, 100, 40), (120, 94, 240),
    (0, 128, 128), (170, 0, 90),
]
LINE = (30, 30, 30)                  # linee disegno
GRAY = (150, 150, 150)               # linee tenui (pezzi non tagliati)
DIMCOL = (0, 90, 160)                # quote


def _tint(rgb, f=0.72):
    """schiarisce verso il bianco (riempimenti leggeri)."""
    return tuple(int(c + (255 - c) * f) for c in rgb)


# ----------------------------------------------------------------------------
# ESTRAZIONE BOX (leggera: min/max + nome/materiale dal layer) da DWG
# ----------------------------------------------------------------------------
def boxes_da_dwg_light(dwg_path, log=print):
    """bbox dei 3DSOLID (posizione assieme) via AutoCAD COM, sola lettura.
    Esclude ferramenta/fori/scassi per layer. Ritorna lista di dict con
    min/max/nome/mat. [] se non apribile."""
    try:
        import win32com.client
    except Exception as ex:
        log(f"  [!] win32com non disponibile: {ex}")
        return []
    acad = win32com.client.Dispatch("AutoCAD.Application")
    doc = None
    for _ in range(20):
        try:
            doc = acad.Documents.Open(dwg_path, True)   # read-only
            break
        except Exception:
            time.sleep(1)
    if doc is None:
        log("  [!] DWG non apribile (gia' aperto?)")
        return []
    out = []
    try:
        ms = doc.ModelSpace
        for i in range(ms.Count):
            try:
                e = ms.Item(i)
                if e.ObjectName != "AcDb3dSolid":
                    continue
                lay = e.Layer or ""
                L = lay.upper()
                if (L.startswith("FERRAMENTA") or L.startswith("FORO_")
                        or L.startswith("SCASSO_")):
                    continue
                mn, mx = e.GetBoundingBox()
                b = {"min": list(mn), "max": list(mx)}
                if " -- " in lay:
                    p = [x.strip() for x in lay.split(" -- ")]
                    b["nome"], b["mat"] = p[0], p[-1]
                out.append(b)
            except Exception:
                continue
    finally:
        try:
            doc.Close(False)
        except Exception:
            pass
    return out


# ----------------------------------------------------------------------------
# GEOMETRIA
# ----------------------------------------------------------------------------
def _pezzi_da_box(boxes):
    """box -> pezzi normalizzati con x0..z1, dx/dy/dz, asse spessore, nome/mat."""
    pz = []
    for b in boxes:
        mn, mx = b["min"], b["max"]
        d = [mx[k] - mn[k] for k in range(3)]
        if min(d) <= 0.1 or max(d) <= 1:
            continue
        pz.append({
            "x0": mn[0], "y0": mn[1], "z0": mn[2],
            "x1": mx[0], "y1": mx[1], "z1": mx[2],
            "dx": d[0], "dy": d[1], "dz": d[2],
            "sp": d.index(min(d)),                 # asse dello spessore 0/1/2
            "nome": b.get("nome", ""), "mat": b.get("mat", "?"),
        })
    return pz


def _divisioni(pezzi, asse, span_axis, span_tot, thin_axis, sel=None):
    """linee di divisione lungo `asse`: centri dei pannelli sottili in
    `thin_axis` che coprono >= DIV_SPAN_MIN di `span_tot` lungo `span_axis`.
    sel = sottoinsieme di pezzi (es. solo i tagliati)."""
    key0 = ("x0", "y0", "z0")
    key1 = ("x1", "y1", "z1")
    lines = []
    for p in (sel if sel is not None else pezzi):
        if p["sp"] != thin_axis:
            continue
        span = p[key1[span_axis]] - p[key0[span_axis]]
        if span < DIV_SPAN_MIN * span_tot:
            continue
        c = (p[key0[asse]] + p[key1[asse]]) / 2.0
        lines.append(c)
    lines.sort()
    # dedup ravvicinati (<40mm): elimina il "rumore" dei pannelli impilati,
    # tiene solo le divisioni principali
    out = []
    for v in lines:
        if not out or abs(v - out[-1]) > 50:
            out.append(v)
    return out


def _vani_utili(pezzi, asse, span_axis, span_tot, thin_axis, sel=None,
                gap_min=40):
    """spazi UTILI netti (faccia-a-faccia) tra i pannelli lungo `asse`:
    unisce gli intervalli dei pannelli sottili in `thin_axis` (che coprono
    >= DIV_SPAN_MIN di `span_tot`) e ritorna i vuoti fra loro come (lo, hi)."""
    k0 = ("x0", "y0", "z0")
    k1 = ("x1", "y1", "z1")
    ints = []
    for p in (sel if sel is not None else pezzi):
        if p["sp"] != thin_axis:
            continue
        if p[k1[span_axis]] - p[k0[span_axis]] < DIV_SPAN_MIN * span_tot:
            continue
        ints.append([p[k0[asse]], p[k1[asse]]])
    if not ints:
        return []
    ints.sort()
    merged = [ints[0][:]]
    for a, b in ints[1:]:
        if a <= merged[-1][1] + 2:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    vani = []
    for (a1, b1), (a2, b2) in zip(merged, merged[1:]):
        if a2 - b1 >= gap_min:
            vani.append((b1, a2))
    return vani


# ----------------------------------------------------------------------------
# SCENA (primitive in mm-foglio)  ->  ['rect'|'line'|'text'|'dimh'|'dimv', ...]
# ----------------------------------------------------------------------------
def _scegli_scala(viste, cell_w, cell_h):
    """la scala 1:n piu' grande (n piu' piccolo) che fa stare ogni vista nella
    cella utile."""
    need_w = max(v["w"] for v in viste)
    need_h = max(v["h"] for v in viste)
    for n in SCALE_STD:
        if need_w / n <= cell_w and need_h / n <= cell_h:
            return n
    return SCALE_STD[-1]


def costruisci_scena(pezzi, commessa, mobile, log=print):
    """ritorna (prim, scala, mat_colori). prim = lista di primitive in mm."""
    xs0 = min(p["x0"] for p in pezzi); xs1 = max(p["x1"] for p in pezzi)
    ys0 = min(p["y0"] for p in pezzi); ys1 = max(p["y1"] for p in pezzi)
    zs0 = min(p["z0"] for p in pezzi); zs1 = max(p["z1"] for p in pezzi)
    W = xs1 - xs0; D = ys1 - ys0; H = zs1 - zs0

    # piani di taglio: DUE sezioni VERTICALI, una taglia in Y (A-A) e una in
    # X (B-B). Ognuna cade al centro del vano piu' largo per non tagliare i
    # divisori.
    def _cut_centro_vano(divisioni, lo, hi):
        liv = [lo] + divisioni + [hi]
        cut = (lo + hi) / 2.0
        best = 0
        for a, b in zip(liv, liv[1:]):
            if b - a > best:
                best = b - a
                cut = (a + b) / 2.0
        return cut

    cutY = _cut_centro_vano(_divisioni(pezzi, 1, 2, H, 1), ys0, ys1)  # piano ⊥Y
    cutX = _cut_centro_vano(_divisioni(pezzi, 0, 2, H, 0), xs0, xs1)  # piano ⊥X

    # colori per materiale
    mats = []
    for p in pezzi:
        if p["mat"] not in mats:
            mats.append(p["mat"])
    mat_col = {m: PALETTE[i % len(PALETTE)] for i, m in enumerate(mats)}

    # definizione delle 4 viste: assi (orizz, vert), tipo, catene da mostrare
    # SEZIONE A-A = verticale, taglio in Y (vista X-Z: larghezza x altezza)
    # SEZIONE B-B = verticale, taglio in X (vista Y-Z: profondita' x altezza)
    viste = [
        {"key": "PROSPETTO", "w": W, "h": H, "ha": 0, "va": 2, "tipo": "proj",
         "vchain": True, "hchain": True},
        {"key": "SEZIONE A-A", "w": W, "h": H, "ha": 0, "va": 2,
         "tipo": "secY", "cut": cutY, "vchain": True, "hchain": True},
        {"key": "PIANTA", "w": W, "h": D, "ha": 0, "va": 1, "tipo": "proj",
         "vchain": False, "hchain": True},
        {"key": "SEZIONE B-B", "w": D, "h": H, "ha": 1, "va": 2,
         "tipo": "secX", "cut": cutX, "vchain": True, "hchain": True},
    ]

    # layout A3: area viste sopra, cartiglio sotto
    fx0, fy0 = MARG, MARG
    fx1, fy1 = A3_W - MARG, A3_H - MARG
    area_y0 = fy0 + TITLE_H + 4
    cols, rows = 2, 2
    gap = 6
    cell_w = (fx1 - fx0 - gap) / cols
    cell_h = (fy1 - area_y0 - gap) / rows
    pad = 20.0                                      # spazio interno per quote+titolo
    usable_w = cell_w - 2 * pad
    usable_h = cell_h - 2 * pad
    scala = _scegli_scala(viste, usable_w, usable_h)

    prim = []
    # cornice + cartiglio
    prim.append(("rect", fx0, fy0, fx1 - fx0, fy1 - fy0, LINE, False, "CORNICE"))
    prim.append(("line", fx0, fy0 + TITLE_H, fx1, fy0 + TITLE_H, LINE, "CORNICE"))

    # posizioni celle (r=0 in alto)
    def cella(idx):
        c = idx % cols
        r = idx // cols
        cx0 = fx0 + c * (cell_w + gap)
        cy1 = fy1 - r * (cell_h + gap)            # top della cella
        cy0 = cy1 - cell_h
        return cx0, cy0, cx0 + cell_w, cy1

    for idx, v in enumerate(viste):
        cx0, cy0, cx1, cy1 = cella(idx)
        # origine disegno (bottom-left del contenuto, centrato nella cella)
        dw = v["w"] / scala
        dh = v["h"] / scala
        ox = cx0 + pad + (usable_w - dw) / 2.0
        oy = cy0 + pad + (usable_h - dh) / 2.0
        v["ox"], v["oy"], v["dw"], v["dh"] = ox, oy, dw, dh

        ha, va = v["ha"], v["va"]
        k0 = ("x0", "y0", "z0"); k1 = ("x1", "y1", "z1")
        base_h = (xs0, ys0, zs0)[ha]
        base_v = (xs0, ys0, zs0)[va]

        def to_sheet(ph, pv):
            return (ox + (ph - base_h) / scala, oy + (pv - base_v) / scala)

        # quali pezzi sono "tagliati" (per le sezioni)
        def tagliato(p):
            if v["tipo"] == "secY":
                return p["y0"] <= v["cut"] <= p["y1"]
            if v["tipo"] == "secX":
                return p["x0"] <= v["cut"] <= p["x1"]
            return True

        # disegno pezzi
        for p in pezzi:
            h0 = p[k0[ha]]; h1 = p[k1[ha]]
            w0 = p[k0[va]]; w1 = p[k1[va]]
            sx, sy = to_sheet(h0, w0)
            w = (h1 - h0) / scala
            h = (w1 - w0) / scala
            if v["tipo"] in ("secY", "secX"):
                if tagliato(p):
                    prim.append(("rect", sx, sy, w, h,
                                 mat_col[p["mat"]], True, "SEZIONE"))
                else:
                    prim.append(("rect", sx, sy, w, h, GRAY, False, "VISTA_TENUE"))
            else:
                prim.append(("rect", sx, sy, w, h,
                             mat_col[p["mat"]], True, "PEZZI"))

        # riquadro/ingombro della vista
        prim.append(("rect", ox, oy, dw, dh, LINE, False, "INGOMBRO"))

        # titolo vista
        prim.append(("text", ox + dw / 2, cy1 - 6,
                     f"{v['key']}   (1:{scala})", 3.4, "c", LINE))

        # --- linee di taglio: A-A (in Y) e B-B (in X) entrambe sulla PIANTA -
        if v["key"] == "PIANTA":
            sy = oy + (cutY - ys0) / scala               # A-A: orizzontale
            prim.append(("line", ox, sy, ox + dw + 10, sy, DIMCOL, "TAGLIO"))
            prim.append(("text", ox + dw + 13, sy, "A", 3.4, "l", DIMCOL))
            sx = ox + (cutX - xs0) / scala               # B-B: verticale
            prim.append(("line", sx, oy, sx, oy + dh + 10, DIMCOL, "TAGLIO"))
            prim.append(("text", sx, oy + dh + 13, "B", 3.4, "c", DIMCOL))

        # --- QUOTE: ingombri + divisioni principali -----------------------
        prim.append(("dimh", ox, ox + dw, oy - 7, f"{int(round(v['w']))}"))
        prim.append(("dimv", oy, oy + dh, ox - 7, f"{int(round(v['h']))}"))

        sel = [p for p in pezzi if tagliato(p)] if v["tipo"].startswith("sec") \
            else None
        # catena verticale (divisioni lungo va: pannelli sottili in va, larghi
        # lungo ha) -> a sinistra
        if v["vchain"]:
            cc = _divisioni(pezzi, va, ha, v["w"], va, sel=sel)
            liv = [base_v] + cc + [base_v + v["h"]]
            for a, b in zip(liv, liv[1:]):
                if b - a < 50:
                    continue
                ya = oy + (a - base_v) / scala
                yb2 = oy + (b - base_v) / scala
                prim.append(("dimv", ya, yb2, ox - 15, f"{int(round(b - a))}"))
        # catena orizzontale (divisioni lungo ha) -> sotto
        if v["hchain"]:
            cc = _divisioni(pezzi, ha, va, v["h"], ha, sel=sel)
            liv = [base_h] + cc + [base_h + v["w"]]
            for a, b in zip(liv, liv[1:]):
                if b - a < 50:
                    continue
                xa = ox + (a - base_h) / scala
                xb = ox + (b - base_h) / scala
                prim.append(("dimh", xa, xb, oy - 15, f"{int(round(b - a))}"))

        # --- QUOTE SPESSORI: una per spessore distinto, nelle sezioni -------
        # (leader dal pezzo tagliato -> etichetta "sp.18" impilata a destra)
        if v["tipo"].startswith("sec"):
            visti = set()
            nlab = 0
            cut_p = sorted((p for p in pezzi if tagliato(p)),
                           key=lambda q: -(q["dx"] * q["dy"] * q["dz"]))
            for p in cut_p:
                sp = p["sp"]
                if sp not in (ha, va):          # spessore non visibile in vista
                    continue
                thick = int(round((p["dx"], p["dy"], p["dz"])[sp]))
                if thick in visti or thick <= 0:
                    continue
                visti.add(thick)
                cxr = (p[k0[ha]] + p[k1[ha]]) / 2
                cyr = (p[k0[va]] + p[k1[va]]) / 2
                px = ox + (cxr - base_h) / scala
                py = oy + (cyr - base_v) / scala
                txp = ox + dw + 5
                typ = oy + dh - 5.5 * nlab
                prim.append(("line", px, py, txp - 1, typ, GRAY, "QUOTE"))
                prim.append(("text", txp, typ, f"sp.{thick}", 2.3, "l", DIMCOL))
                nlab += 1
                if nlab >= 4:
                    break
            # spazi UTILI netti (luce interna) -> DENTRO la vista:
            #  - vani in altezza (tra i ripiani) su una colonna a sinistra-interna
            vani_v = _vani_utili(pezzi, va, ha, v["w"], va, sel=sel)
            xin = ox + dw * 0.24
            for lo, hi in vani_v:
                ya = oy + (lo - base_v) / scala
                yb = oy + (hi - base_v) / scala
                prim.append(("dimv", ya, yb, xin, f"{int(round(hi - lo))}"))
            #  - vani in larghezza/profondita' (tra fianchi/divisori) in basso
            vani_h = _vani_utili(pezzi, ha, va, v["h"], ha, sel=sel)
            yin = oy + dh * 0.12
            for lo, hi in vani_h:
                xa = ox + (lo - base_h) / scala
                xb = ox + (hi - base_h) / scala
                prim.append(("dimh", xa, xb, yin, f"{int(round(hi - lo))}"))

    # --- cartiglio + legenda -------------------------------------------------
    tx = fx0 + 4
    ty = fy0 + TITLE_H - 6
    oggi = datetime.date.today().strftime("%d/%m/%Y")
    prim.append(("text", tx, ty, "DISEGNO PER CLIENTE", 4.2, "l", LINE))
    prim.append(("text", tx, ty - 8,
                 f"Commessa: {commessa or '-'}    Mobile: {mobile or '-'}",
                 3.0, "l", LINE))
    prim.append(("text", tx, ty - 15,
                 f"Ingombri: {int(round(W))} x {int(round(D))} x {int(round(H))} mm "
                 f"(L x P x H)   Scala 1:{scala}   {oggi}", 2.7, "l", LINE))
    # legenda materiali (a destra del cartiglio)
    lx = fx0 + (fx1 - fx0) * 0.52
    ly = fy0 + TITLE_H - 7
    prim.append(("text", lx, ly, "MATERIALI:", 3.0, "l", LINE))
    for i, m in enumerate(mats):
        yy = ly - 6.5 * (i + 1)
        if yy < fy0 + 2:
            break
        prim.append(("rect", lx, yy - 2.6, 5, 3.6, mat_col[m], True, "LEGENDA"))
        prim.append(("text", lx + 7, yy, m, 2.5, "l", LINE))

    log(f"  scena: {len(pezzi)} pezzi, {len(mats)} materiali, scala 1:{scala}")
    return prim, scala, mat_col


# ----------------------------------------------------------------------------
# BACKEND PILLOW -> PDF
# ----------------------------------------------------------------------------
def _font(px):
    from PIL import ImageFont
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, max(6, int(px)))
        except Exception:
            continue
    return ImageFont.load_default()


def rendi_pdf(prim, out_pdf, dpi=200):
    from PIL import Image, ImageDraw
    mm = dpi / 25.4
    Wp, Hp = int(A3_W * mm), int(A3_H * mm)
    img = Image.new("RGB", (Wp, Hp), "white")
    d = ImageDraw.Draw(img)

    def X(x):
        return x * mm

    def Y(y):
        return Hp - y * mm                       # flip

    def line(x1, y1, x2, y2, col, w=1):
        d.line([X(x1), Y(y1), X(x2), Y(y2)], fill=col, width=w)

    def tick(xc, yc, ang):
        import math
        dx = math.cos(math.radians(ang)) * 1.4 * mm
        dy = math.sin(math.radians(ang)) * 1.4 * mm
        d.line([X(xc) - dx, Y(yc) + dy, X(xc) + dx, Y(yc) - dy],
               fill=DIMCOL, width=1)

    def text(x, y, s, hmm, anc, col):
        f = _font(hmm * mm)
        try:
            bb = d.textbbox((0, 0), s, font=f)
            tw, th = bb[2] - bb[0], bb[3] - bb[1]
        except Exception:
            tw, th = len(s) * hmm * mm * 0.5, hmm * mm
        px, py = X(x), Y(y)
        if anc == "c":
            px -= tw / 2
        elif anc == "r":
            px -= tw
        py -= th / 2
        d.text((px, py), s, fill=col, font=f)

    def vtext(x, y, s, hmm, col):
        """testo verticale (ruotato 90°, lettura dal basso), centrato in (x,y)."""
        f = _font(hmm * mm)
        tmp = Image.new("RGBA", (int(hmm * mm * len(s)) + 10,
                                 int(hmm * mm) + 8), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).text((3, 2), s, fill=col, font=f)
        bb = tmp.getbbox()
        if bb:
            tmp = tmp.crop(bb)
        tmp = tmp.rotate(90, expand=True)
        px, py = X(x), Y(y)
        img.paste(tmp, (int(px - tmp.width / 2), int(py - tmp.height / 2)), tmp)

    for p in prim:
        t = p[0]
        if t == "rect":
            _, x, y, w, h, col, filled, _lay = p
            xy = [X(x), Y(y + h), X(x + w), Y(y)]
            if filled:
                d.rectangle(xy, fill=_tint(col), outline=col, width=1)
            else:
                d.rectangle(xy, outline=col, width=1)
        elif t == "line":
            _, x1, y1, x2, y2, col, _lay = p
            line(x1, y1, x2, y2, col, 1)
        elif t == "text":
            _, x, y, s, hmm, anc, col = p
            text(x, y, s, hmm, anc, col)
        elif t == "dimh":
            _, x1, x2, y, s = p
            line(x1, y, x2, y, DIMCOL, 1)
            tick(x1, y, 45); tick(x2, y, 45)
            line(x1, y, x1, y + 1.5, DIMCOL); line(x2, y, x2, y + 1.5, DIMCOL)
            text((x1 + x2) / 2, y + 2.2, s, 2.4, "c", DIMCOL)
        elif t == "dimv":
            _, y1, y2, x, s = p
            line(x, y1, x, y2, DIMCOL, 1)
            tick(x, y1, 45); tick(x, y2, 45)
            line(x, y1, x + 1.5, y1, DIMCOL); line(x, y2, x + 1.5, y2, DIMCOL)
            vtext(x - 2.2, (y1 + y2) / 2, s, 2.4, DIMCOL)

    img.save(out_pdf, "PDF", resolution=dpi)
    return out_pdf


# ----------------------------------------------------------------------------
# BACKEND ezdxf -> DXF  (poi AutoCAD converte in DWG)
# ----------------------------------------------------------------------------
def rendi_dxf(prim, out_dxf, mat_col, k=1.0):
    """DXF a SCALA REALE 1:1 (coordinate della scena x k, dove k = la scala del
    foglio): la geometria misura i mm veri. Le quote sono QUOTE AUTOCAD VERE
    ASSOCIATIVE che MISURANO la geometria (nessun testo fisso), cosi' il cliente
    ci prende le misure reali direttamente in CAD."""
    import ezdxf
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()

    for lay in ("CORNICE", "PEZZI", "SEZIONE", "VISTA_TENUE", "INGOMBRO",
                "TAGLIO", "LEGENDA", "TESTI"):
        doc.layers.add(lay, color=7)
    doc.layers.add("QUOTE", color=5)
    try:                                    # azzera il dimlfac=100 di serie
        doc.dimstyles.get("EZDXF").dxf.dimlfac = 1.0
    except Exception:
        pass
    doc.header["$DIMLFAC"] = 1.0

    def Kx(v):
        return v * k

    def add_poly(x, y, w, h, rgb, filled, lay):
        pts = [(Kx(x), Kx(y)), (Kx(x + w), Kx(y)), (Kx(x + w), Kx(y + h)),
               (Kx(x), Kx(y + h)), (Kx(x), Kx(y))]
        pl = msp.add_lwpolyline(pts, dxfattribs={"layer": lay})
        pl.rgb = rgb
        if filled:
            hatch = msp.add_hatch(dxfattribs={"layer": lay})
            hatch.rgb = _tint(rgb)
            hatch.paths.add_polyline_path(pts[:-1], is_closed=True)

    # stile quote proporzionato alla scala reale.
    # dimlfac=1 OBBLIGATORIO: lo stile "EZDXF" di ezdxf nasce con dimlfac=100
    # (mostrerebbe 247 come 24700). dimlunit=2 decimale, dimdec=0 -> mm interi.
    dov = {"dimtxt": 2.4 * k, "dimasz": 1.6 * k, "dimexe": 1.0 * k,
           "dimexo": 1.2 * k, "dimgap": 0.8 * k, "dimclrt": 5, "dimclrd": 5,
           "dimclre": 5, "dimrnd": 1, "dimdec": 0, "dimlfac": 1.0,
           "dimlunit": 2, "dimzin": 8}

    for p in prim:
        t = p[0]
        if t == "rect":
            _, x, y, w, h, col, filled, lay = p
            add_poly(x, y, w, h, col, filled, lay)
        elif t == "line":
            _, x1, y1, x2, y2, col, lay = p
            ln = msp.add_line((Kx(x1), Kx(y1)), (Kx(x2), Kx(y2)),
                              dxfattribs={"layer": lay})
            ln.rgb = col
        elif t == "text":
            _, x, y, s, hmm, anc, col = p
            from ezdxf.enums import TextEntityAlignment as TA
            al = {"c": TA.MIDDLE_CENTER, "l": TA.MIDDLE_LEFT,
                  "r": TA.MIDDLE_RIGHT}[anc]
            mt = msp.add_text(s, dxfattribs={"height": hmm * k,
                                             "layer": "TESTI"})
            mt.set_placement((Kx(x), Kx(y)), align=al)
            mt.rgb = col
        elif t == "dimh":
            _, x1, x2, y, _s = p                       # _s ignorato: MISURA lui
            try:
                msp.add_linear_dim(
                    base=(0, Kx(y + 4)), p1=(Kx(x1), Kx(y)), p2=(Kx(x2), Kx(y)),
                    dimstyle="EZDXF", override=dov).render()
            except Exception:
                pass
        elif t == "dimv":
            _, y1, y2, x, _s = p
            try:
                msp.add_linear_dim(
                    base=(Kx(x - 4), 0), p1=(Kx(x), Kx(y1)), p2=(Kx(x), Kx(y2)),
                    angle=90, dimstyle="EZDXF", override=dov).render()
            except Exception:
                pass
    doc.saveas(out_dxf)
    return out_dxf


def dxf_a_dwg(dxf_path, dwg_path, log=print):
    """apre il DXF in AutoCAD (istanza gia' attiva) e lo salva come DWG.
    Non tocca i disegni dell'utente (nuovo documento, poi chiuso)."""
    dxf_path = os.path.abspath(dxf_path)
    dwg_path = os.path.abspath(dwg_path)
    try:
        import win32com.client
        acad = win32com.client.Dispatch("AutoCAD.Application")
        acad.Visible = True
        doc = None
        err = ""
        for _ in range(20):
            try:
                doc = acad.Documents.Open(dxf_path)
                break
            except Exception as ex:
                err = str(ex)
                time.sleep(1)
        if doc is None:
            log(f"  [!] DXF non apribile per conversione DWG ({err})")
            return None
        doc.SaveAs(dwg_path)                    # formato DWG corrente
        doc.Close(False)
        return dwg_path if os.path.isfile(dwg_path) else None
    except Exception as ex:
        log(f"  [!] conversione DWG fallita: {ex}")
        return None


# ----------------------------------------------------------------------------
# ORCHESTRATORE
# ----------------------------------------------------------------------------
def genera_viste_cliente(src, out_dir, commessa="", mobile="", boxes=None,
                         fai_dwg=True, log=print):
    """src = path DWG 3D (o None se passi boxes). Ritorna dict con i path."""
    os.makedirs(out_dir, exist_ok=True)
    if boxes is None:
        if not src or not os.path.isfile(src):
            log(f"  [!] sorgente 3D non trovata: {src}")
            return {}
        boxes = boxes_da_dwg_light(src, log)
    if not boxes:
        log("  [!] nessun pezzo estratto")
        return {}
    pezzi = _pezzi_da_box(boxes)
    if not pezzi:
        log("  [!] nessun pannello valido")
        return {}
    prim, scala, mat_col = costruisci_scena(pezzi, commessa, mobile, log)

    base = (mobile or (os.path.splitext(os.path.basename(src))[0] if src
                       else "mobile")).replace(" ", "_")
    res = {}
    pdf = os.path.join(out_dir, f"VISTE_{base}.pdf")
    try:
        rendi_pdf(prim, pdf)
        res["pdf"] = pdf
        log(f"  PDF -> {os.path.basename(pdf)}")
    except Exception as ex:
        log(f"  [!] PDF fallito: {ex}")
    dxf = os.path.join(out_dir, f"VISTE_{base}.dxf")
    try:
        rendi_dxf(prim, dxf, mat_col, k=scala)         # DWG/DXF a scala reale
        res["dxf"] = dxf
        log(f"  DXF -> {os.path.basename(dxf)}")
    except Exception as ex:
        log(f"  [!] DXF fallito: {ex}")
    if fai_dwg and res.get("dxf"):
        dwg = os.path.join(out_dir, f"VISTE_{base}.dwg")
        if dxf_a_dwg(dxf, dwg, log):
            res["dwg"] = dwg
            log(f"  DWG -> {os.path.basename(dwg)}")
    return res


if __name__ == "__main__":
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else None
    out = sys.argv[2] if len(sys.argv) > 2 else "."
    print(genera_viste_cliente(src, out, log=print))
