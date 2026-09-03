# -*- coding: utf-8 -*-
"""VIDEO V2 — FILIERA UN CLIC completa (viste cliente + costi + ordini).

Landscape 1920x1080, 30 fps. Undici scene: sei card Pillow con zoom morbido e
CINQUE SCENE ANIMATE frame-per-frame (moduli in scene_v2/: 3D che si monta,
click su AVVIA, filiera che gira in console, Ken Burns sulla tavola vera,
costi che contano). Musica procedurale sincronizzata (stesso motore di
genera_musica.py) e voce it-IT-Diego.

La voce si cerca in quest'ordine: 1) mp3 gia' pronti in voci_v2/ (generati da
un'altra sessione o dal PC), 2) edge-tts al volo se la rete lo permette,
3) niente voce: il video esce comunque guidato dai testi a schermo.

La scena VISTE usa la TAVOLA VERA: importa Viste/viste_cliente.py e genera la
tavola A3 del MOBILE TV demo (stesse misure del collaudo 25-A018) col codice
di produzione. Se sul PC esiste il girato reale (Desktop/FILIERA_UN_CLIC),
gli spezzoni configurati in GIRATO vengono inseriti da soli tra le scene.

Uso:  py fai_video_v2_filiera.py             -> video completo
      py fai_video_v2_filiera.py anteprima   -> solo le card PNG delle scene
Override cartella output: variabile d'ambiente FILIERA_VIDEO_OUT.
"""
import os
import re
import sys
import wave
import asyncio
import importlib.util
import subprocess

import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
QUI = os.path.dirname(os.path.abspath(__file__))
WINDOWS = os.name == "nt"

OUT = os.environ.get("FILIERA_VIDEO_OUT") or (
    os.path.join(os.path.expanduser("~"), "Desktop", "FILIERA_UN_CLIC_V2")
    if WINDOWS else os.path.join(QUI, "out_v2"))
os.makedirs(OUT, exist_ok=True)

# girato reale (solo sul PC di casa): se i file esistono vengono inseriti
GIRATO_DIR = os.environ.get("FILIERA_GIRATO") or os.path.join(
    os.path.expanduser("~"), "Desktop", "FILIERA_UN_CLIC")

W, H = 1920, 1080
CW, CH = 2880, 1620          # card sovracampionata 1.5x per lo zoom morbido
FPS = 30
VOCE = "it-IT-DiegoNeural"
VOCI_DIR = os.path.join(QUI, "voci_v2")      # mp3 pronti (da git o dal PC)

SFONDO = (18, 16, 14)
ARANCIO = (255, 140, 66)
BIANCO = (245, 242, 238)
GRIGIO = (150, 145, 140)
VERDE = (110, 200, 120)
ROSSO = (220, 80, 70)


# ----------------------------------------------------------------------------
# FONT (Segoe su Windows, DejaVu altrove)
# ----------------------------------------------------------------------------
def _primo_font(candidati):
    for p in candidati:
        if os.path.exists(p):
            return p
    raise SystemExit(f"nessun font trovato tra: {candidati}")

_WF = r"C:\Windows\Fonts"
_LF = "/usr/share/fonts/truetype/dejavu"
F_BLACK = _primo_font([os.path.join(_WF, "seguibl.ttf"),
                       os.path.join(_LF, "DejaVuSans-Bold.ttf")])
F_BOLD = _primo_font([os.path.join(_WF, "segoeuib.ttf"),
                      os.path.join(_LF, "DejaVuSans-Bold.ttf")])
F_REG = _primo_font([os.path.join(_WF, "segoeui.ttf"),
                     os.path.join(_LF, "DejaVuSans.ttf")])
F_MONO = _primo_font([os.path.join(_WF, "consola.ttf"),
                      os.path.join(_LF, "DejaVuSansMono.ttf")])


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(dr, testo, fnt, maxw):
    righe, riga = [], ""
    for parola in testo.split():
        prova = (riga + " " + parola).strip()
        if dr.textlength(prova, font=fnt) <= maxw:
            riga = prova
        else:
            if riga:
                righe.append(riga)
            riga = parola
    if riga:
        righe.append(riga)
    return righe


def croce(dr, x, y, s, colore, w=14):
    dr.line([x, y, x + s, y + s], fill=colore, width=w)
    dr.line([x + s, y, x, y + s], fill=colore, width=w)


def spunta(dr, x, y, s, colore, w=16):
    dr.line([(x, y + 0.55 * s), (x + 0.38 * s, y + s),
             (x + 1.05 * s, y + 0.08 * s)], fill=colore, width=w,
            joint="curve")


def freccia_dx(dr, x, cy, s, colore):
    dr.polygon([(x, cy - s), (x, cy + s), (x + 1.2 * s, cy)], fill=colore)


def card_base(marchio=True):
    img = Image.new("RGB", (CW, CH), SFONDO)
    dr = ImageDraw.Draw(img)
    for i in range(0, CW, 108):                      # venature discrete
        dr.line([(i, 0), (i, CH)], fill=(24, 21, 18), width=2)
    if marchio:
        f = font(F_BOLD, 48)
        t = "FALEGNAME  DIGITALE"
        tw = dr.textlength(t, font=f)
        dr.text(((CW - tw) / 2, 70), t, font=f, fill=GRIGIO)
        dr.rectangle([CW / 2 - 80, 148, CW / 2 + 80, 158], fill=ARANCIO)
    return img, dr


def testo_centrato(dr, righe_spec, y, maxw=None):
    """righe_spec: lista (testo, font, colore, interlinea_extra)."""
    maxw = maxw or CW - 300
    for testo, fnt, colore, extra in righe_spec:
        for riga in wrap(dr, testo, fnt, maxw):
            twl = dr.textlength(riga, font=fnt)
            dr.text(((CW - twl) / 2, y), riga, font=fnt, fill=colore)
            y += fnt.size * 1.16
        y += extra
    return y


def badge_v2(dr, cx, cy, h=120):
    f = font(F_BLACK, int(h * 0.72))
    t = "V2"
    tw = dr.textlength(t, font=f)
    w = tw + h * 0.7
    dr.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                         radius=h / 4, outline=ARANCIO, width=10)
    dr.text((cx - tw / 2, cy - f.size * 0.60), t, font=f, fill=ARANCIO)


# ----------------------------------------------------------------------------
# TAVOLA VERA dal codice di produzione (Viste/viste_cliente.py)
# ----------------------------------------------------------------------------
def _boxes_demo_mobile_tv():
    """Mobile TV demo, stesse misure del collaudo 25-A018: 1580x450x915."""
    SP, Wm, D, Hm, ZOC = 18, 1580, 450, 915, 60
    ROV, LAC = "ROVERE EGGER H1180", "LACCATO NCS 1002-Y50R"

    def box(nome, mat, x0, x1, y0, y1, z0, z1):
        return {"min": (x0, y0, z0), "max": (x1, y1, z1),
                "nome": nome, "mat": mat}
    return [
        box("FIANCO SX", ROV, 0, SP, 0, D, ZOC, Hm),
        box("FIANCO DX", ROV, Wm - SP, Wm, 0, D, ZOC, Hm),
        box("FONDO", ROV, SP, Wm - SP, 0, D, ZOC, ZOC + SP),
        box("CIELO", ROV, SP, Wm - SP, 0, D, Hm - SP, Hm),
        box("SCHIENALE", ROV, SP, Wm - SP, D - 14, D, ZOC + SP, Hm - SP),
        box("DIVISORIO 1", ROV, 522, 540, SP, D - 14, ZOC + SP, Hm - SP),
        box("DIVISORIO 2", ROV, 1040, 1058, SP, D - 14, ZOC + SP, Hm - SP),
        box("RIPIANO SX", ROV, SP, 522, SP, D - 14, 345, 363),
        box("RIPIANO CENTR", ROV, 540, 1040, SP, D - 14, 325, 343),
        box("RIPIANO DX", ROV, 1058, Wm - SP, SP, D - 14, 345, 363),
        box("ANTA SX", LAC, SP, 522, 0, SP, ZOC + SP, Hm - SP),
        box("ANTA DX", LAC, 1058, Wm - SP, 0, SP, ZOC + SP, Hm - SP),
        box("ZOCCOLO", LAC, SP, Wm - SP, 30, 48, 0, ZOC),
    ]


def genera_tavola_reale():
    """Tavola A3 col codice VERO -> PNG. None se qualcosa manca (si usa la
    card disegnata al posto della tavola)."""
    png = os.path.join(OUT, "tavola_demo.png")
    if os.path.exists(png):
        return png
    try:
        sys.path.insert(0, os.path.join(QUI, "..", "Viste"))
        from viste_cliente import genera_viste_cliente
        res = genera_viste_cliente(None, OUT, commessa="25-A018",
                                   mobile="MOBILE TV",
                                   boxes=_boxes_demo_mobile_tv(),
                                   fai_dwg=False)
        if not res.get("pdf"):
            return None
        import pypdfium2 as pdfium
        page = pdfium.PdfDocument(res["pdf"])[0]
        page.render(scale=300 / 72).to_pil().save(png)
        print("tavola vera ok")
        return png
    except Exception as ex:
        print(f"[!] tavola vera non disponibile ({ex}): uso la card disegnata")
        return None


# ----------------------------------------------------------------------------
# SCENE STATICHE (card 2880x1620)
# ----------------------------------------------------------------------------
def scena_titolo():
    img, dr = card_base()
    testo_centrato(dr, [
        ("FILIERA", font(F_BLACK, 300), ARANCIO, -30),
        ("UN CLIC", font(F_BLACK, 300), ARANCIO, 40),
    ], 330)
    badge_v2(dr, CW / 2, 1110, 130)
    testo_centrato(dr, [
        ("dal 3D del progettista alla commessa completa. Da sola.",
         font(F_BOLD, 78), BIANCO, 0),
    ], 1280)
    return img


def scena_problema():
    img, dr = card_base()
    testo_centrato(dr, [("UNA COMMESSA INTERA, A MANO:",
                         font(F_BLACK, 100), BIANCO, 0)], 230)
    voci = ["importare il 3D", "esplodere i pezzi",
            "DXF di ogni pezzo", "togliere i doppioni",
            "distinta e sezionatura", "programmare 2 macchine",
            "tavole per il cliente", "preventivo costi"]
    f = font(F_BOLD, 74)
    x0s, y0, dy = (330, 1560), 470, 165
    for i, voce in enumerate(voci):
        x = x0s[i // 4]
        y = y0 + (i % 4) * dy
        croce(dr, x, y + 14, 60, ROSSO)
        dr.text((x + 130, y), voce, font=f, fill=BIANCO)
    fo = font(F_BLACK, 210)
    t = "GIORNI."
    dr.text(((CW - dr.textlength(t, font=fo)) / 2, 1230), t, font=fo,
            fill=ARANCIO)
    return img


def scena_tre_d_fallback():
    img, dr = card_base()
    testo_centrato(dr, [
        ("TUTTO PARTE", font(F_BLACK, 170), BIANCO, 10),
        ("DAL 3D DEL PROGETTISTA", font(F_BLACK, 150), ARANCIO, 90),
        ("quello che hai già", font(F_BOLD, 84), GRIGIO, 0),
    ], 480)
    return img


def scena_bottone():
    img, dr = card_base()
    testo_centrato(dr, [
        ("Adesso io premo", font(F_BOLD, 110), GRIGIO, 20),
        ("UN BOTTONE.", font(F_BLACK, 230), BIANCO, 0),
    ], 380)
    bw, bh, cy = 760, 190, 1210
    dr.rounded_rectangle([CW / 2 - bw / 2, cy - bh / 2,
                          CW / 2 + bw / 2, cy + bh / 2], radius=45,
                         fill=ARANCIO)
    f = font(F_BLACK, 110)
    t = "AVVIA"
    dr.text(((CW - dr.textlength(t, font=f)) / 2, cy - f.size * 0.62), t,
            font=f, fill=SFONDO)
    return img


def scena_pipeline():
    img, dr = card_base()
    testo_centrato(dr, [("LA FILIERA PARTE DA SOLA",
                         font(F_BLACK, 100), BIANCO, 0)], 230)
    tappe = ["STEP 3D del progettista", "DXF di OGNI pezzo",
             "PROGRAMMI UNICI (no doppioni)", "DISTINTA + SEZIONATURA",
             "TLF Master | MPRX Homag"]
    fb = font(F_BOLD, 56)
    bw, bh, gap = 460, 250, 85
    x = (CW - 5 * bw - 4 * gap) / 2
    cy = 800
    for i, t in enumerate(tappe):
        ultimo = i == len(tappe) - 1
        dr.rounded_rectangle([x, cy - bh / 2, x + bw, cy + bh / 2], radius=34,
                             fill=ARANCIO if ultimo else (44, 40, 36))
        righe = wrap(dr, t, fb, bw - 60)
        ty = cy - len(righe) * fb.size * 1.12 / 2
        for riga in righe:
            twl = dr.textlength(riga, font=fb)
            dr.text((x + (bw - twl) / 2, ty), riga, font=fb,
                    fill=SFONDO if ultimo else BIANCO)
            ty += fb.size * 1.12
        if not ultimo:
            freccia_dx(dr, x + bw + 24, cy, 34, ARANCIO)
        x += bw + gap
    testo_centrato(dr, [("un pezzo solo di ogni tipo: la macchina lo taglia D volte",
                         font(F_BOLD, 64), GRIGIO, 0)], 1180)
    return img


def scena_macchine():
    img, dr = card_base()
    testo_centrato(dr, [("PROGRAMMI MACCHINA GIÀ FATTI",
                         font(F_BLACK, 100), ARANCIO, 0)], 230)
    card_w, card_h, gap = 1180, 940, 140
    x0 = (CW - 2 * card_w - gap) / 2
    titoli = ("TLF — MASTERWOOD", "MPRX — HOMAG")
    voci = (["fori, tasche, aperture", "frontali uniti, fuga 3,2",
             "programma girato per il retro", "LAMATE che staccano i pezzi"],
            ["stesso pezzo, stesso programma", "niente doppioni in bancale",
             "quote dal 3D, non ricopiate", "pronto in macchina"])
    for k in range(2):
        x = x0 + k * (card_w + gap)
        dr.rounded_rectangle([x, 430, x + card_w, 430 + card_h], radius=40,
                             fill=(34, 30, 26), outline=(60, 54, 48), width=4)
        ft = font(F_BLACK, 84)
        tw = dr.textlength(titoli[k], font=ft)
        dr.text((x + (card_w - tw) / 2, 500), titoli[k], font=ft, fill=BIANCO)
        fv = font(F_BOLD, 56)
        y = 680
        for voce in voci[k]:
            spunta(dr, x + 80, y + 12, 50, VERDE)
            dr.text((x + 180, y), voce, font=fv, fill=BIANCO)
            y += 150
    return img


def scena_scheda_ordini():
    img, dr = card_base()
    testo_centrato(dr, [("SCHEDA BASE  +  ORDINI FORNITORI",
                         font(F_BLACK, 100), BIANCO, 0)], 230)
    card_w, card_h, gap, y0 = 1180, 940, 140, 430
    x0 = (CW - 2 * card_w - gap) / 2
    # --- scheda base: mini foglio con formule ---
    x = x0
    dr.rounded_rectangle([x, y0, x + card_w, y0 + card_h], radius=40,
                         fill=(240, 238, 234))
    dr.rectangle([x + 40, y0 + 40, x + card_w - 40, y0 + 130],
                 fill=(15, 110, 86))
    fb = font(F_BOLD, 56)
    dr.text((x + 70, y0 + 58), "SCHEDA BASE _COMPLETO", font=fb,
            fill=(255, 255, 255))
    fr = font(F_REG, 48)
    righe = [("PEZZO", "MQ LACC.", "ML BORDO"),
             ("FIANCO SX", "1,46", "2,40"),
             ("ANTA  x2", "2,08", "3,15"),
             ("RIPIANO x3", "1,17", "1,50")]
    yy = y0 + 190
    for i, (a, b, c) in enumerate(righe):
        col = (90, 90, 90) if i == 0 else (30, 30, 30)
        dr.text((x + 80, yy), a, font=fr, fill=col)
        dr.text((x + 560, yy), b, font=fr, fill=col)
        dr.text((x + 850, yy), c, font=fr, fill=col)
        dr.line([x + 60, yy + 70, x + card_w - 60, yy + 70],
                fill=(200, 198, 194), width=2)
        yy += 90
    fm = font(F_MONO, 44)
    dr.text((x + 80, yy + 30), "MQ=(F*G*AK+(F+G)*H*2)/1e6*D", font=fm,
            fill=(15, 110, 86))
    dr.text((x + 80, yy + 100), "ML=MAX(F/1000;1)*D   (M17: 0,25)", font=fm,
            fill=(15, 110, 86))
    fc = font(F_BOLD, 54)
    dr.text((x + 80, yy + 190), "formule di casa, compilate da sole",
            font=fc, fill=(120, 80, 30))
    # --- ordine fornitore: pagina PDF ---
    x = x0 + card_w + gap
    dr.rounded_rectangle([x, y0, x + card_w, y0 + card_h], radius=40,
                         fill=(34, 30, 26), outline=(60, 54, 48), width=4)
    pw, ph = 620, 780
    px, py = x + (card_w - pw) / 2, y0 + 70
    dr.rectangle([px + 14, py + 14, px + pw + 14, py + ph + 14],
                 fill=(20, 17, 15))
    dr.rectangle([px, py, px + pw, py + ph], fill=(250, 249, 247))
    fh = font(F_BOLD, 46)
    dr.text((px + 40, py + 35), "ORDINE — PANNELLI", font=fh, fill=(30, 30, 30))
    dr.text((px + 40, py + 95), "rif. commessa 25-A018", font=font(F_REG, 38),
            fill=(110, 110, 110))
    for i in range(7):
        dr.line([px + 40, py + 190 + i * 62, px + pw - 40, py + 190 + i * 62],
                fill=(205, 203, 199), width=3)
    fe = font(F_BOLD, 36)
    te = "cartella ORDINI"
    dr.rectangle([px + 40, py + ph - 110,
                  px + 70 + dr.textlength(te, font=fe), py + ph - 50],
                 fill=(15, 110, 86))
    dr.text((px + 55, py + ph - 102), te, font=fe, fill=(255, 255, 255))
    fc2 = font(F_BOLD, 54)
    t = "un PDF per ogni fornitore"
    tw = dr.textlength(t, font=fc2)
    dr.text((x + (card_w - tw) / 2, y0 + card_h - 68), t, font=fc2,
            fill=ARANCIO)
    return img


def scena_viste(tavola=None):
    img, dr = card_base(marchio=False)
    dr.rectangle([0, 0, CW, 170], fill=ARANCIO)
    f = font(F_BLACK, 88)
    t = "NOVITÀ — LA TAVOLA PER IL CLIENTE"
    dr.text(((CW - dr.textlength(t, font=f)) / 2, 30), t, font=f, fill=SFONDO)
    if tavola and os.path.exists(tavola):
        tav = Image.open(tavola)
        tav.thumbnail((CW - 360, 1220), Image.LANCZOS)
        px = (CW - tav.width) // 2
        py = 230
        dr.rectangle([px + 18, py + 18, px + tav.width + 18,
                      py + tav.height + 18], fill=(8, 7, 6))
        img.paste(tav, (px, py))
    else:                                    # fallback disegnato
        testo_centrato(dr, [
            ("PIANTA · PROSPETTO · SEZIONI A-A e B-B",
             font(F_BLACK, 110), BIANCO, 30),
            ("quotate, coi vani utili e i materiali a colori",
             font(F_BOLD, 80), GRIGIO, 0),
        ], 560)
    testo_centrato(dr, [
        ("PDF in scala da stampare  +  DWG 1:1 con quote vere",
         font(F_BOLD, 68), BIANCO, 0),
    ], 1500)
    return img


def scena_costi():
    img, dr = card_base()
    testo_centrato(dr, [("RIEPILOGO COSTI — COMMESSA 25-A019",
                         font(F_BLACK, 96), BIANCO, 0)], 220)
    voci = [("PANNELLAME", "6.635"), ("FERRAMENTA", "178"),
            ("BORDI", "952"), ("MASSELLO / CORNICI", "61"),
            ("LACCATURA + CART.RA", "4.302"), ("ILLUMINAZIONE", "2.026"),
            ("MANODOPERA  (320 h × 45 €)", "14.422")]
    tw_, x = 1700, (CW - 1700) / 2
    y, dy = 420, 105
    fv = font(F_BOLD, 62)
    for nome, euro in voci:
        dr.text((x, y), nome, font=fv, fill=BIANCO)
        s = euro + " €"
        dr.text((x + tw_ - dr.textlength(s, font=fv), y), s, font=fv,
                fill=GRIGIO)
        dr.line([x, y + 84, x + tw_, y + 84], fill=(60, 54, 48), width=3)
        y += dy
    ft = font(F_BLACK, 96)
    y += 30
    dr.text((x, y), "TOTALE MOBILE", font=ft, fill=ARANCIO)
    s = "28.577 €"
    dr.text((x + tw_ - dr.textlength(s, font=ft), y), s, font=ft, fill=ARANCIO)
    testo_centrato(dr, [("prima di accendere la sega",
                         font(F_BOLD, 70), GRIGIO, 0)], 1460)
    return img


def scena_collaudo():
    img, dr = card_base()
    testo_centrato(dr, [
        ("COLLAUDATA", font(F_BLACK, 190), BIANCO, 20),
        ("sui programmi VERI delle macchine", font(F_BOLD, 84), GRIGIO, 110),
        ("IDENTICA AL 100%", font(F_BLACK, 210), VERDE, 0),
    ], 420)
    return img


def scena_cta():
    img, dr = card_base()
    testo_centrato(dr, [
        ("Selezioni i file.  Premi AVVIA.", font(F_BOLD, 96), BIANCO, 10),
        ("Torni a fare il falegname.", font(F_BOLD, 96), ARANCIO, 130),
        ("FILIERA UN CLIC", font(F_BLACK, 170), BIANCO, 40),
    ], 370)
    badge_v2(dr, CW / 2, 1230, 110)
    testo_centrato(dr, [("Scrivimi per provarla nella tua officina",
                         font(F_BOLD, 66), GRIGIO, 0)], 1400)
    return img


# ----------------------------------------------------------------------------
# STORYBOARD: (tipo, riferimento, stile musica, testo voce)
#   tipo "static" -> riferimento = funzione card
#   tipo "anim"   -> riferimento = nome modulo in scene_v2/ (con fallback card)
# ----------------------------------------------------------------------------
SCENE = [
    ("static", scena_titolo, "minimal",
     "Filiera un Clic, versione due. Dal 3D del progettista alla commessa "
     "completa: da sola."),
    ("static", scena_problema, "build",
     "Una commessa a mano? Import, esplosioni, DXF, doppioni, distinta, due "
     "macchine da programmare, tavole, preventivo. Giorni interi. Spariti."),
    ("anim", "anim_tre_d", "build",
     "Si parte dal 3D che hai già. Quello del tuo progettista."),
    ("anim", "anim_avvia", "minimal", "Poi premi un bottone. Uno."),
    ("anim", "anim_run", "drop",
     "E la filiera corre da sola: i DXF di ogni pezzo, i programmi unici "
     "senza doppioni, la distinta e la sezionatura. Fatti."),
    ("static", scena_macchine, "groove",
     "Fori, tasche, lamate: i programmi per la Masterwood e per la Homag "
     "escono già pronti. Tu li carichi, e tagli."),
    ("anim", "anim_sezionatura", "groove",
     "La sezionatura si disegna da sola: ogni pezzo al suo posto sul "
     "pannello, prima ancora di toccare la sega."),
    ("static", scena_scheda_ordini, "groove",
     "La scheda base si compila con le formule di casa. E ogni fornitore "
     "riceve il suo ordine in PDF, già pronto in cartella."),
    ("anim", "anim_tavola", "half",
     "E per il tuo cliente? La tavola quotata: pianta, prospetto, sezioni, "
     "materiali a colori. Da stampare, o in DWG con quote vere."),
    ("anim", "anim_costi", "groove",
     "E prima di partire sai già quanto ti costa il mobile: pannelli, bordi, "
     "ferramenta, laccatura, manodopera. Tutto, subito."),
    ("static", scena_collaudo, "groove",
     "Collaudata pezzo per pezzo sui programmi veri delle macchine: identica "
     "al cento per cento."),
    ("static", scena_cta, "outro",
     "Seleziona i file. Premi Avvia. E torna a fare il falegname. Filiera un "
     "Clic, dal Falegname Digitale. Scrivimi, e provala nella tua officina."),
]

FALLBACK = {"anim_tre_d": scena_tre_d_fallback, "anim_avvia": scena_bottone,
            "anim_run": scena_pipeline, "anim_tavola": None,  # gestita a parte
            "anim_costi": scena_costi, "anim_sezionatura": scena_pipeline}

# girato reale da inserire DOPO la scena indicata (1-based), se esiste
GIRATO = [
    (6, "girato_woodwop.mp4", 8.0),      # dopo le macchine: WoodWOP vero
    (8, "girato_demo.mp4", 8.0),         # dopo la tavola: app che gira davvero
]


def carica_modulo(nome):
    """importa scene_v2/<nome>.py; None se manca o non carica."""
    path = os.path.join(QUI, "scene_v2", f"{nome}.py")
    if not os.path.exists(path):
        return None
    try:
        spec = importlib.util.spec_from_file_location(nome, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert callable(mod.frame) and mod.DUR_NOM > 0
        return mod
    except Exception as ex:
        print(f"[!] modulo {nome} non caricabile ({ex}): uso la card fissa")
        return None


# ----------------------------------------------------------------------------
# VOCE: mp3 pronti in voci_v2/, altrimenti edge-tts, altrimenti niente
# ----------------------------------------------------------------------------
def _voce_path(i):
    return os.path.join(OUT, f"voce{i:02d}.mp3")


async def _genera_voci_async():
    import edge_tts
    for i, (_, _, _, testo) in enumerate(SCENE, 1):
        if os.path.exists(_voce_path(i)):
            continue
        await edge_tts.Communicate(testo, VOCE, rate="+10%").save(_voce_path(i))
        print("voce", i, "ok")


def trova_voci():
    """porta gli mp3 in OUT. True se ci sono tutti."""
    pronte = [os.path.join(VOCI_DIR, f"voce{i:02d}.mp3")
              for i in range(1, len(SCENE) + 1)]
    if all(os.path.exists(p) for p in pronte):
        for i, p in enumerate(pronte, 1):
            if not os.path.exists(_voce_path(i)):
                with open(p, "rb") as fi, open(_voce_path(i), "wb") as fo:
                    fo.write(fi.read())
        print("voci: mp3 pronti da voci_v2/")
        return True
    try:
        asyncio.run(_genera_voci_async())
        return all(os.path.exists(_voce_path(i))
                   for i in range(1, len(SCENE) + 1))
    except Exception as ex:
        print(f"[!] voce non disponibile ({ex}): video con musica e testi")
        return False


def durata_media(path):
    r = subprocess.run([FFMPEG, "-i", path, "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.findall(r"time=(\d+):(\d+):(\d+\.\d+)", r.stderr)
    hh, mm, ss = m[-1]
    return int(hh) * 3600 + int(mm) * 60 + float(ss)


# ----------------------------------------------------------------------------
# MUSICA procedurale (stesso motore di genera_musica.py, durata adattiva)
# ----------------------------------------------------------------------------
SR = 44100
BEAT = 60.0 / 138.0                         # 138 BPM: ritmo da spot
ACC = [55.00, 43.65, 65.41, 49.00]


def componi_musica(segmenti, wav_path, click_times=()):
    """segmenti = [(t0, dur, stile)];
    stile: minimal / build / groove / half / drop / outro.
    click_times: istanti (s) dove mettere il click del mouse su AVVIA."""
    tot = segmenti[-1][0] + segmenti[-1][1]
    N = int(SR * tot)
    rng = np.random.default_rng(32)
    bufL, bufR = np.zeros(N), np.zeros(N)

    def metti(suono, t0, gain=1.0, pan=0.0):
        i0 = int(t0 * SR)
        if i0 >= N or i0 < 0:
            return
        s = suono[:N - i0] * gain
        a = (pan + 1) * np.pi / 4
        bufL[i0:i0 + len(s)] += s * np.cos(a)
        bufR[i0:i0 + len(s)] += s * np.sin(a)

    def tempo(dur):
        return np.arange(int(dur * SR)) / SR

    def kick():
        t = tempo(0.30)
        f = 46 + 110 * np.exp(-t * 22)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)

    def hat(aperto=False):
        t = tempo(0.16 if aperto else 0.06)
        n = np.diff(rng.standard_normal(len(t)), prepend=0.0)
        return n * np.exp(-t * (16 if aperto else 65)) * 0.7

    def clap():
        t = tempo(0.22)
        n = np.diff(rng.standard_normal(len(t)), prepend=0.0)
        return n * np.exp(-t * 22) * (1 + 0.6 * np.sin(2 * np.pi * 95 * t))

    def basso(f, dur, dec=4.0):
        t = tempo(dur)
        s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) +
             0.12 * np.sin(6 * np.pi * f * t))
        return s * np.minimum(t / 0.008, 1) * np.exp(-t * dec)

    def pluck(f):
        t = tempo(0.45)
        return (np.sin(2 * np.pi * f * t) +
                0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 9)

    def pad(freqs, dur):
        t = tempo(dur)
        s = sum(np.sin(2 * np.pi * f * t + i)
                for i, f in enumerate(freqs)) / len(freqs)
        return (s * np.minimum(t / 0.7, 1) *
                np.clip(np.minimum((dur - t) / 0.8, 1), 0, 1))

    def riser(dur):
        t = tempo(dur)
        n = np.diff(rng.standard_normal(len(t)), prepend=0.0)
        return n * (t / dur) ** 2.2

    def boom():
        t = tempo(1.4)
        f = 40 + 30 * np.exp(-t * 6)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)

    def bar_of(t):
        return int(t / (BEAT * 4))

    def battute_groove(t0, nb, mezzo=False):
        for b in range(nb):
            t = t0 + b * BEAT
            bar = bar_of(t)
            if mezzo:
                if b % 4 == 0:
                    metti(kick(), t, 0.60)
                    metti(basso(ACC[bar % 4], 1.8, dec=1.2), t, 0.30)
            else:
                metti(kick(), t, 0.85)
                if b % 2 == 1:
                    metti(clap(), t, 0.30, pan=0.2)
                for k in range(2):
                    metti(basso(ACC[bar % 4], 0.20), t + k * BEAT / 2, 0.42)
                f0 = ACC[bar % 4] * 4
                metti(pluck([f0, f0 * 1.5, f0 * 2][b % 3]), t + BEAT / 2,
                      0.18, pan=0.4)
                metti(hat(), t + 0.75 * BEAT, 0.08, pan=0.25)   # sedicesimi
            metti(hat(), t + BEAT / 2, 0.10 if mezzo else 0.16, pan=-0.3)

    for t0, dur, stile in segmenti:
        nb = int(dur / BEAT)
        if stile == "minimal":
            for b in range(nb):
                t = t0 + b * BEAT
                if b % 2 == 0:
                    metti(kick(), t, 0.45)
                metti(hat(), t + BEAT / 2, 0.10, pan=-0.3)
            metti(basso(ACC[bar_of(t0) % 4], 1.6, dec=1.5), t0, 0.30)
            metti(riser(1.0), t0 + dur - 1.1, 0.18)
        elif stile == "build":
            for b in range(nb):
                t = t0 + b * BEAT
                if b % 2 == 0:
                    metti(kick(), t, 0.55)
                metti(hat(), t + BEAT / 2, 0.13, pan=-0.3)
                if b % 4 == 2:
                    metti(clap(), t, 0.22, pan=0.2)
                if b % 4 == 0:
                    metti(basso(ACC[bar_of(t) % 4], 1.6, dec=1.5), t, 0.30)
            metti(riser(1.2), t0 + dur - 1.3, 0.25)
        elif stile == "drop":
            metti(boom(), t0, 0.75)
            metti(clap(), t0, 0.30)
            battute_groove(t0, nb)
        elif stile == "groove":
            battute_groove(t0, nb)
        elif stile == "half":
            battute_groove(t0, nb, mezzo=True)
            metti(pad([220, 261.63, 329.63], min(dur, 6.0)), t0, 0.16)
        elif stile == "outro":
            metti(boom(), t0, 0.8)
            metti(clap(), t0, 0.35)
            metti(pad([220, 261.63, 329.63, 440], min(dur, 8.0)), t0 + 0.1,
                  0.15)
            for b in range(0, nb, 4):
                if b * BEAT < dur - 2.5:
                    metti(kick(), t0 + b * BEAT, 0.40)

    def click_ui():
        t = tempo(0.09)
        n = np.diff(rng.standard_normal(len(t)), prepend=0.0)
        blip = np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 90)
        return n * np.exp(-t * 220) * 0.8 + blip * 0.6

    for tc in click_times:
        metti(click_ui(), tc, 0.9)

    mix = np.tanh(np.vstack([bufL, bufR]) * 1.1)
    mix *= 0.95 / max(np.abs(mix).max(), 1e-9)
    nfade = min(int(1.6 * SR), N)
    mix[:, -nfade:] *= np.linspace(1, 0, nfade)
    mix[:, :2205] *= np.linspace(0, 1, 2205)
    with wave.open(wav_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix.T * 32767).astype(np.int16).tobytes())
    return wav_path


# ----------------------------------------------------------------------------
# MONTAGGIO
# ----------------------------------------------------------------------------
def _mux_audio(i, video, dur, mp3):
    """aggiunge la voce (o silenzio) a un video muto, -c:v copy."""
    mp4 = os.path.join(OUT, f"scena{i}.mp4")
    cmd = [FFMPEG, "-y", "-i", video]
    if mp3:
        cmd += ["-i", mp3, "-filter_complex", "[1:a]adelay=350|350,apad[a]"]
    else:
        cmd += ["-f", "lavfi", "-t", f"{dur:.2f}",
                "-i", "anullsrc=r=44100:cl=stereo",
                "-filter_complex", "[1:a]anull[a]"]
    cmd += ["-map", "0:v", "-map", "[a]", "-t", f"{dur:.2f}",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            mp4]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:])
        raise SystemExit(f"mux audio scena {i} fallito")
    return mp4


def scena_static_mp4(i, fabbrica, dur, mp3, ultimo, tavola=None):
    png = os.path.join(OUT, f"scena{i}.png")
    (fabbrica(tavola) if fabbrica is scena_viste else fabbrica()).save(png)
    frames = int(dur * FPS)
    vf = (f"zoompan=z='min(1.06,1+0.0006*on)':"
          f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
          f"d={frames}:s={W}x{H}:fps={FPS},fade=t=in:st=0:d=0.3")
    if ultimo:
        vf += f",fade=t=out:st={max(0, dur - 0.7):.2f}:d=0.7"
    muto = os.path.join(OUT, f"_v{i}.mp4")
    r = subprocess.run(
        [FFMPEG, "-y", "-loop", "1", "-framerate", str(FPS), "-i", png,
         "-vf", vf, "-t", f"{dur:.2f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", muto],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:])
        raise SystemExit(f"ffmpeg scena {i} fallito")
    return _mux_audio(i, muto, dur, mp3)


def scena_anim_mp4(i, mod, dur, mp3, ultimo):
    muto = os.path.join(OUT, f"_v{i}.mp4")
    gen = imageio_ffmpeg.write_frames(
        muto, (W, H), pix_fmt_in="rgb24", fps=FPS, codec="libx264",
        quality=None, macro_block_size=1,
        output_params=["-crf", "20", "-preset", "medium",
                       "-pix_fmt", "yuv420p"])
    gen.send(None)
    n = int(dur * FPS)
    for k in range(n):
        t = k / FPS
        im = mod.frame(t, dur)
        if im.size != (W, H):
            im = im.resize((W, H))
        a = np.asarray(im.convert("RGB"), dtype=np.uint8)
        fatt = min(1.0, t / 0.3)                       # fade-in
        if ultimo and t > dur - 0.7:
            fatt = min(fatt, max(0.0, (dur - t) / 0.7))
        if fatt < 1.0:
            a = (a.astype(np.float32) * fatt).astype(np.uint8)
        gen.send(np.ascontiguousarray(a))
    gen.close()
    return _mux_audio(i, muto, dur, mp3)


def girato_mp4(idx, nome, dur_max):
    src = os.path.join(GIRATO_DIR, nome)
    if not os.path.exists(src):
        return None
    mp4 = os.path.join(OUT, f"girato_{idx}.mp4")
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},"
          f"fade=t=in:st=0:d=0.3")
    r = subprocess.run(
        [FFMPEG, "-y", "-i", src,
         "-f", "lavfi", "-t", f"{dur_max:.2f}",
         "-i", "anullsrc=r=44100:cl=stereo",
         "-filter_complex", f"[0:v]{vf}[v];[1:a]anull[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{dur_max:.2f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-ar", "44100", mp4],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[!] girato {nome} scartato: {r.stderr[-300:]}")
        return None
    print(f"girato inserito: {nome}")
    return mp4


def main():
    tavola = genera_tavola_reale()
    if tavola:
        os.environ["FILIERA_TAVOLA_PNG"] = tavola

    if len(sys.argv) > 1 and sys.argv[1] == "anteprima":
        for i, (tipo, rif, _, _) in enumerate(SCENE, 1):
            if tipo == "static":
                img = rif(tavola) if rif is scena_viste else rif()
            else:
                mod = carica_modulo(rif)
                if mod:
                    img = mod.frame(mod.DUR_NOM * 0.6, mod.DUR_NOM)
                else:
                    fb = FALLBACK.get(rif) or scena_viste
                    img = fb(tavola) if fb is scena_viste else fb()
            img.save(os.path.join(OUT, f"scena{i}.png"))
        print("anteprime in", OUT)
        return

    con_voce = trova_voci()
    pezzi, segmenti, copione, click_times = [], [], [], []
    t_cursore = 0.0
    for i, (tipo, rif, stile, testo) in enumerate(SCENE, 1):
        ultimo = i == len(SCENE)
        mp3 = _voce_path(i) if con_voce else None
        vdur = durata_media(mp3) + 1.0 if mp3 else None
        if tipo == "anim":
            mod = carica_modulo(rif)
            if mod:
                dur = max(mod.DUR_NOM, vdur) if vdur else mod.DUR_NOM
                pezzi.append(scena_anim_mp4(i, mod, dur, mp3, ultimo))
            else:
                fb = FALLBACK.get(rif) or scena_viste
                dur = vdur if vdur else max(4.2, min(8.5, 1.8 + 0.04 * len(testo)))
                dur = max(4.0, dur)
                pezzi.append(scena_static_mp4(i, fb, dur, mp3, ultimo, tavola))
        else:
            dur = max(4.0, vdur) if vdur else max(4.2, min(8.5, 1.8 + 0.04 * len(testo)))
            pezzi.append(scena_static_mp4(i, rif, dur, mp3, ultimo, tavola))
        if tipo == "anim" and rif == "anim_avvia":
            click_times.append(t_cursore + 0.55 * dur)   # click su AVVIA
        segmenti.append((t_cursore, dur, stile))
        copione.append(f"SCENA {i}  ({dur:.1f}s)\n  {testo}\n")
        t_cursore += dur
        print(f"scena {i}: {dur:.1f}s ok")
        for idx, (dopo, nome, dmax) in enumerate(GIRATO):
            if dopo == i:
                g = girato_mp4(idx, nome, dmax)
                if g:
                    gd = durata_media(g)
                    pezzi.append(g)
                    segmenti.append((t_cursore, gd, "groove"))
                    t_cursore += gd

    lista = os.path.join(OUT, "_lista.txt")
    with open(lista, "w", encoding="utf-8") as fh:
        for p in pezzi:
            fh.write(f"file '{p}'\n")
    muto = os.path.join(OUT, "_senza_musica.mp4")
    r = subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0",
                        "-i", lista, "-c", "copy", muto],
                       capture_output=True, text=True)
    if r.returncode != 0:                        # codec diversi: ricodifica
        r = subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0",
                            "-i", lista,
                            "-c:v", "libx264", "-preset", "medium",
                            "-crf", "20", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "192k", muto],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr[-1500:])
            raise SystemExit("concat fallito")

    wav = componi_musica(segmenti, os.path.join(OUT, "musica_v2.wav"),
                         click_times)
    gain = 0.42 if con_voce else 0.85
    finale = os.path.join(OUT, "FILIERA_UN_CLIC_v2.mp4")
    r = subprocess.run(
        [FFMPEG, "-y", "-i", muto, "-i", wav,
         "-filter_complex",
         f"[1:a]volume={gain}[m];"
         f"[0:a][m]amix=inputs=2:duration=first:dropout_transition=0,"
         f"alimiter=limit=0.95[a]",
         "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", finale],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:])
        raise SystemExit("mix musica fallito")

    with open(os.path.join(OUT, "copione_v2.txt"), "w", encoding="utf-8") as fh:
        fh.write("FILIERA UN CLIC V2 - copione\n"
                 + ("(con voce)\n\n" if con_voce
                    else "(senza voce: musica + testi a schermo)\n\n")
                 + "\n".join(copione))
    print("\nVIDEO PRONTO:", finale)
    print("durata totale:", f"{durata_media(finale):.1f}s")


if __name__ == "__main__":
    main()
