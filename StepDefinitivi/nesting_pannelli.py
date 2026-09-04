# -*- coding: utf-8 -*-
"""nesting_pannelli - schema di taglio per sezionatrice dalla filiera.

Dal riepilogo (L/H/SP/q.ta/materiale) e dalle lastre del catalogo
PANNELLAME dello stampo SCHEDA BASE:
  - misure di TAGLIO come la sezionatura della scheda: +10 su L e H,
    minimi 350 x 110
  - nesting a GHIGLIOTTINA per strisce (come si taglia al banco):
    rifilo perimetrale, lama tra i tagli, strisce alte quanto il pezzo
    piu' alto che ci entra
  - VENATURA: sui materiali venati (rovere, noce, tranciati...) i pezzi
    NON si ruotano; sugli altri si' se conviene
Uscite: PDF con lo schema (un foglio per pagina, pezzi etichettati col
numero programma) + {materiale: numero fogli} per la SCHEDA BASE.
"""

import os
import re

LAMA = 5.0            # mm mangiati da ogni taglio
RIFILO = 10.0         # mm di rifilo per lato della lastra
MAGG = 10.0           # maggiorazione taglio su L e H
MIN_L, MIN_H = 350.0, 110.0
VENATI = re.compile(r"ROVERE|NOCE|TANGAN|TRANC|LIST\.IMP|PARONA|TEAK|"
                    r"FRASSINO|LARICE|OLMO", re.IGNORECASE)

STAMPO = (r"C:\Users\User\Desktop\CLAUDE\Definitivi"
          r"\SCHEDA_BASE_MODELLO_FILIERA.xlsm")


def _lastre_catalogo():
    """[(nome, W, H, sp)] dal foglio PANNELLAME dello stampo."""
    import openpyxl
    wb = openpyxl.load_workbook(STAMPO, read_only=True, data_only=True)
    ws = wb["PANNELLAME"]
    out = []
    for r in ws.iter_rows(min_row=2, max_col=4, values_only=True):
        if r and isinstance(r[0], str) and r[0].strip() and r[1] and r[2]:
            try:
                out.append((r[0].strip(), float(r[1]), float(r[2]),
                            float(r[3]) if r[3] is not None else None))
            except (TypeError, ValueError):
                continue
    return out


NON_PANNELLI = re.compile(r"MARMO|SPECCHIO|VETRO|INTONACO|METALLO",
                          re.IGNORECASE)
LASTRA_STD = (2800.0, 2070.0)


def _lastra_di_riserva(mat):
    """Formato lastra quando il catalogo non aiuta: prima il formato
    scritto NEL NOME del materiale (es. '366x187' in cm -> 3660x1870),
    senno' la lastra standard 2800x2070 (da verificare)."""
    m = re.search(r"(\d{2,4})\s*[xX]\s*(\d{2,4})", str(mat))
    if m:
        w, h = float(m.group(1)), float(m.group(2))
        if w < 1000:
            w, h = w * 10, h * 10
        if w >= 1000 and h >= 800:
            return (f"formato dal nome ({m.group(0)})", w, h)
    return ("LASTRA STANDARD 2800x2070: VERIFICARE",) + LASTRA_STD


def _taglio(l, h):
    return max(l + MAGG, MIN_L), max(h + MAGG, MIN_H)


def nesting_materiale(pezzi, W, H, ruota):
    """Nesting a strisce (ghigliottina). pezzi = [(l, h, etich)] gia'
    espansi per quantita'. Ritorna lista fogli; ogni foglio = lista
    strisce; striscia = (y, alt, [(x, l, h, etich, ruotato)])."""
    UW, UH = W - 2 * RIFILO, H - 2 * RIFILO
    # dal piu' alto (ruotando i ruotabili per stare "sdraiati" se aiuta)
    ordinati = []
    for l, h, et in pezzi:
        if ruota and h > l and h <= UW and l <= UH:
            l, h, r = h, l, True     # sdraiato: strisce piu' basse
        else:
            r = False
        ordinati.append((l, h, et, r))
    ordinati.sort(key=lambda p: (-p[1], -p[0]))
    fogli = []
    for l, h, et, r in ordinati:
        if l > UW or h > UH:
            if ruota and h <= UW and l <= UH:
                l, h, r = h, l, not r
            else:
                # pezzo fuori lastra: foglio dedicato, segnalato
                fogli.append([(0.0, min(h, UH),
                               [(0.0, min(l, UW), min(h, UH),
                                 et + " (FUORI LASTRA!)", r)])])
                continue
        piazzato = False
        for foglio in fogli:
            for i, (y, alt, righe) in enumerate(foglio):
                usato = sum(p[1] for p in righe) + LAMA * len(righe)
                if h <= alt and usato + l <= UW:
                    righe.append((usato, l, h, et, r))
                    piazzato = True
                    break
            if piazzato:
                break
            y_next = (foglio[-1][0] + foglio[-1][1] + LAMA) if foglio else 0
            if y_next + h <= UH:
                foglio.append((y_next, h, [(0.0, l, h, et, r)]))
                piazzato = True
                break
        if not piazzato:
            fogli.append([(0.0, h, [(0.0, l, h, et, r)])])
    return fogli


def _disegna(pagine, mat, lastra, W, H, fogli, font, mm2px):
    from PIL import Image, ImageDraw
    for i, foglio in enumerate(fogli, 1):
        img = Image.new("RGB", (2338, 1653), "white")
        dr = ImageDraw.Draw(img)
        area = sum(p[1] * p[2] for _, _, righe in
                   [(0, 0, r) for _, _, r in foglio] for p in righe)
        eff = area / (W * H) * 100
        dr.text((60, 30), f"{mat}", fill="black", font=font(40, True))
        dr.text((60, 84), f"lastra {lastra}  {W:g} x {H:g} mm   -   "
                          f"foglio {i}/{len(fogli)}   -   resa {eff:.0f}%",
                fill=(90, 90, 90), font=font(28))
        sc = min(2218.0 / W, 1440.0 / H)
        ox, oy = 60, 150
        dr.rectangle([ox, oy, ox + W * sc, oy + H * sc],
                     outline="black", width=3)
        for y, alt, righe in foglio:
            for x, l, h, et, r in righe:
                x0 = ox + (RIFILO + x) * sc
                y0 = oy + (RIFILO + y) * sc
                dr.rectangle([x0, y0, x0 + l * sc, y0 + h * sc],
                             fill=(232, 238, 244), outline=(60, 60, 60),
                             width=2)
                lab = f"{et}  {l:g}x{h:g}" + (" R" if r else "")
                px = 26 if min(l, h) * sc > 60 else 18
                dr.text((x0 + 8, y0 + 6), lab[:38], fill="black",
                        font=font(px))
        pagine.append(img)


def nesting_lavoro(base, log=print):
    """base = cartella madre "Programmi CNC".
    Ritorna ({materiale: n fogli}, pdf_path)."""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from scheda_base_da_filiera import (_leggi_riepilogo, _codice_num,
                                        abbina_lastra)

    pu = os.path.join(base, "PROGRAMMI_UNICI")
    righe = _leggi_riepilogo(pu)
    lastre = _lastre_catalogo()
    gruppi = {}
    fuori = []
    for r in righe:
        m = (r["mat"] or "").strip()
        if not m or "MASSELLO" in m.upper():
            continue
        if NON_PANNELLI.search(m):
            if m not in fuori:
                fuori.append(m)
            continue
        gruppi.setdefault(m, []).append(r)
    if fuori:
        log("  nesting: fuori taglio pannelli (marmo/specchio/...): "
            + ", ".join(f[:25] for f in fuori))

    from PIL import Image, ImageFont

    def font(px, bold=False):
        return ImageFont.truetype(
            os.path.join(r"C:\Windows\Fonts",
                         "arialbd.ttf" if bold else "arial.ttf"), px)

    pagine = []
    fogli_per_mat = {}
    saltati = []
    for mat, rs in sorted(gruppi.items()):
        sps = [r["SP"] for r in rs if r["SP"]]
        sp = max(set(sps), key=sps.count) if sps else None
        ab = abbina_lastra(mat, sp, lastre)
        da_catalogo = ab is not None
        if not ab:
            ab = _lastra_di_riserva(mat)
            saltati.append(mat)
        lastra, W, H = ab
        pezzi = []
        for r in rs:
            lt, ht = _taglio(float(r["L"] or 0), float(r["H"] or 0))
            et = str(_codice_num(r["pezzo"]) or r["pezzo"])
            for _ in range(int(r["qta"] or 1)):
                pezzi.append((lt, ht, et))
        ruota = not VENATI.search(mat + " " + lastra)
        fogli = nesting_materiale(pezzi, W, H, ruota)
        if da_catalogo:                  # in scheda solo i conteggi certi
            fogli_per_mat[mat] = len(fogli)
        _disegna(pagine, mat, lastra, W, H, fogli, font, None)
        log(f"  nesting {mat[:35]}: {len(pezzi)} pezzi -> "
            f"{len(fogli)} fogli" + ("" if ruota else " (venato: no rotaz.)"))
    if saltati:
        log(f"  [!] lastra dal ripiego (verifica il formato sul PDF): "
            f"{', '.join(s[:25] for s in saltati)}")
    if not pagine:
        return fogli_per_mat, None

    lavoro = os.path.basename(os.path.dirname(base)) or "lavoro"
    # dentro la cartella madre del lavoro: prima usciva accanto ai file 3D
    pdf = os.path.join(base, f"NESTING_{lavoro}.pdf")
    tmp = pdf + ".parte"
    Image.init()
    pag = [p.convert("L") for p in pagine]
    pag[0].save(tmp, format="PDF", save_all=True, append_images=pag[1:],
                resolution=200, quality=92)
    try:
        os.replace(tmp, pdf)
    except PermissionError:
        try:
            os.remove(tmp)
        except OSError:
            pass
        log(f"  [!] {os.path.basename(pdf)} aperto: chiudilo e rilancia")
        return fogli_per_mat, None
    log(f"  -> {pdf} ({len(pag)} fogli disegnati)")
    return fogli_per_mat, pdf
