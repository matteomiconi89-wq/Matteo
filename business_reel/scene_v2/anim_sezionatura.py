# -*- coding: utf-8 -*-
"""Scena animata: la SEZIONATURA si disegna da sola — i pezzi del mobile
volano sul bancale uno alla volta e si sistemano al loro posto."""
import os
import math
from PIL import Image, ImageDraw, ImageFont


def _fp(cands):
    for p in cands:
        if os.path.exists(p):
            return p
    raise RuntimeError('font mancante')

_WF = r'C:\Windows\Fonts'
_LF = '/usr/share/fonts/truetype/dejavu'
F_BOLD = _fp([os.path.join(_WF, 'segoeuib.ttf'),
              os.path.join(_LF, 'DejaVuSans-Bold.ttf')])
F_REG = _fp([os.path.join(_WF, 'segoeui.ttf'),
             os.path.join(_LF, 'DejaVuSans.ttf')])
F_MONO = _fp([os.path.join(_WF, 'consola.ttf'),
              os.path.join(_LF, 'DejaVuSansMono.ttf')])

W, H = 1920, 1080
SFONDO = (18, 16, 14)
ARANCIO = (255, 140, 66)
BIANCO = (245, 242, 238)
GRIGIO = (150, 145, 140)
VERDE = (110, 200, 120)
LEGNO = (222, 189, 140)          # pannello chiaro sul bancale scuro
LEGNO_B = (166, 132, 84)

DUR_NOM = 7.0

# bancale in mm e scala di disegno
BW_MM, BH_MM = 2800, 2070
SC = 0.36
BX, BY = 180, 250                 # angolo alto-sinistra del bancale sul frame

# pezzi: (nome, x, y, w, h) in mm sul bancale, in ordine di arrivo
PEZZI = [
    ("SCHIENALE", 10, 10, 1544, 800),
    ("CIELO", 10, 820, 1544, 440),
    ("FONDO", 10, 1270, 1544, 440),
    ("ANTA SX", 1564, 10, 500, 810),
    ("ANTA DX", 2074, 10, 500, 810),
    ("FIANCO SX", 1564, 830, 900, 440),
    ("FIANCO DX", 1564, 1280, 900, 440),
    ("DIV. 1", 2474, 830, 300, 440),
    ("DIV. 2", 2474, 1280, 300, 440),
    ("ZOCCOLO", 10, 1720, 1544, 80),
    ("RIPIANO 1", 10, 1810, 500, 250),
    ("RIPIANO 2", 520, 1810, 500, 250),
    ("RIPIANO 3", 1030, 1810, 500, 250),
]

_base = None


def _ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def _sfondo():
    global _base
    if _base is not None:
        return _base
    img = Image.new('RGB', (W, H), SFONDO)
    dr = ImageDraw.Draw(img)
    for i in range(0, W, 108):
        dr.line([(i, 0), (i, H)], fill=(24, 21, 18), width=2)
    f = font(F_BOLD, 34)
    t = 'FALEGNAME  DIGITALE'
    dr.text(((W - dr.textlength(t, font=f)) / 2, 42), t, font=f, fill=GRIGIO)
    dr.rectangle([W / 2 - 55, 96, W / 2 + 55, 103], fill=ARANCIO)
    ft = font(F_BOLD, 62)
    t = 'SEZIONATURA — bancale 2800 × 2070'
    dr.text(((W - dr.textlength(t, font=ft)) / 2, 128), t, font=ft, fill=BIANCO)
    # bancale
    bw, bh = int(BW_MM * SC), int(BH_MM * SC)
    dr.rectangle([BX + 12, BY + 12, BX + bw + 12, BY + bh + 12], fill=(8, 7, 6))
    dr.rectangle([BX, BY, BX + bw, BY + bh], fill=(38, 33, 28),
                 outline=(70, 62, 54), width=3)
    _base = img
    return img


def font(path, size):
    return ImageFont.truetype(path, size)


def _pezzo_img(nome, w_px, h_px):
    img = Image.new('RGB', (max(w_px, 2), max(h_px, 2)), LEGNO)
    dr = ImageDraw.Draw(img)
    dr.rectangle([0, 0, w_px - 1, h_px - 1], outline=LEGNO_B, width=2)
    fsize = max(16, min(30, int(min(w_px, h_px) * 0.28)))
    f = font(F_BOLD, fsize)
    tw = dr.textlength(nome, font=f)
    if tw < w_px - 10 and fsize < h_px - 6:
        dr.text(((w_px - tw) / 2, (h_px - fsize * 1.2) / 2), nome, font=f,
                fill=(70, 52, 30))
    return img


def frame(t, dur):
    tt = max(0.0, min(1.0, t / max(dur, 0.01)))     # 0..1 sulla scena
    img = _sfondo().copy()
    dr = ImageDraw.Draw(img)
    n = len(PEZZI)
    fine_posa = 0.82                                # i pezzi atterrano entro qui
    per_pezzo = fine_posa / n
    posati = 0
    for i, (nome, x, y, wmm, hmm) in enumerate(PEZZI):
        t0 = i * per_pezzo
        u = (tt - t0) / (per_pezzo * 1.6)           # leggero overlap tra pezzi
        if u <= 0:
            continue
        w_px, h_px = int(wmm * SC), int(hmm * SC)
        xf, yf = BX + int(x * SC), BY + int(y * SC)
        pez = _pezzo_img(nome, w_px, h_px)
        if u >= 1:
            img.paste(pez, (xf, yf))
            posati += 1
            # lampo arancio appena atterrato
            if u < 1.35:
                al = 1 - (u - 1) / 0.35
                dr = ImageDraw.Draw(img)
                col = tuple(int(a * al + b * (1 - al))
                            for a, b in zip(ARANCIO, LEGNO_B))
                dr.rectangle([xf, yf, xf + w_px - 1, yf + h_px - 1],
                             outline=col, width=4)
        else:
            e = _ease(u)
            xs = W + 60                               # parte da fuori a destra
            ys = yf - 140 * (1 - e)
            xc = int(xs + (xf - xs) * e)
            img.paste(pez, (xc, int(ys)))
    dr = ImageDraw.Draw(img)
    # contatore pezzi e stato
    fm = font(F_MONO, 36)
    dr.text((BX, BY + int(BH_MM * SC) + 26),
            f'> pezzi posati: {posati:2d}/{n}   doppioni: 0', font=fm,
            fill=(120, 200, 160))
    # cartellino sfrido a destra
    fb = font(F_BOLD, 44)
    dr.text((1330, BY + int(BH_MM * SC) + 22), 'sfrido 8%', font=fb,
            fill=GRIGIO)
    if tt > fine_posa + 0.06:
        al = min(1.0, (tt - fine_posa - 0.06) / 0.12)
        dr.rectangle([0, 972, W, 1056], fill=SFONDO)     # copre la riga di stato
        fv = font(F_BOLD, 58)
        t2 = 'SEZIONATURA PRONTA — zero doppioni'
        twl = dr.textlength(t2, font=fv)
        col = tuple(int(c * al + s * (1 - al)) for c, s in zip(VERDE, SFONDO))
        dr.text(((W - twl) / 2, 984), t2, font=fv, fill=col)
    return img
