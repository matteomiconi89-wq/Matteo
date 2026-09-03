# -*- coding: utf-8 -*-
# Scena "RIEPILOGO COSTI" — video FILIERA UN CLIC / FALEGNAME DIGITALE
# Tabella costi commessa: righe che appaiono una alla volta con conteggio
# degli importi, totale finale in arancio con "pop" di scala e caption.
import os
import math
from PIL import Image, ImageDraw, ImageFont

def _fp(cands):
    for p in cands:
        if os.path.exists(p): return p
    raise RuntimeError('font mancante')
_WF = r'C:\Windows\Fonts'; _LF = '/usr/share/fonts/truetype/dejavu'
F_BOLD = _fp([os.path.join(_WF,'segoeuib.ttf'), os.path.join(_LF,'DejaVuSans-Bold.ttf')])
F_REG  = _fp([os.path.join(_WF,'segoeui.ttf'),  os.path.join(_LF,'DejaVuSans.ttf')])
F_MONO = _fp([os.path.join(_WF,'consola.ttf'),  os.path.join(_LF,'DejaVuSansMono.ttf')])

W, H = 1920, 1080
SFONDO  = (18, 16, 14)
ARANCIO = (255, 140, 66)
BIANCO  = (245, 242, 238)
GRIGIO  = (150, 145, 140)
VENA    = (24, 21, 18)   # venature verticali dello sfondo
SEP     = (60, 54, 48)   # righe separatrici della tabella

DUR_NOM = 7.0

TITOLO = 'RIEPILOGO COSTI \u2014 COMMESSA 25-A019'
RIGHE = [
    ('PANNELLAME',                        6635),
    ('FERRAMENTA',                         178),
    ('BORDI',                              952),
    ('MASSELLO / CORNICI',                  61),
    ('LACCATURA + CART.RA',               4302),
    ('ILLUMINAZIONE',                     2026),
    ('MANODOPERA (320 h \u00d7 45 \u20ac)', 14422),
]
TOT_VAL = 28577

# geometria (tabella centrata larga 1700px)
TAB_L, TAB_R = 110, 1810
ROW_Y0, ROW_H = 282, 60      # centro prima riga e passo verticale
TOT_Y  = 770                 # centro riga totale
CAP_Y  = 935                 # centro caption

_G = {}   # cache lazy: font, sfondo

def _font(path, size):
    k = (path, size)
    if k not in _G: _G[k] = ImageFont.truetype(path, size)
    return _G[k]

def _clamp01(x):
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)

def _ease(x):
    # ease-in-out morbido
    x = _clamp01(x)
    return 0.5 - 0.5 * math.cos(math.pi * x)

def _easeout(x):
    # ease-out cubico (per i conteggi: veloci all'inizio, dolci alla fine)
    x = _clamp01(x)
    return 1.0 - (1.0 - x) ** 3

def _mix(c1, c2, a):
    # interpolazione colore (fade su sfondo scuro)
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * a)) for i in range(3))

def _fmt(n):
    # formato migliaia col punto + spazio prima di €
    s = str(int(n)); out = ''
    while len(s) > 3:
        out = '.' + s[-3:] + out
        s = s[:-3]
    return s + out + ' \u20ac'

def _title_font():
    # dimensione titolo ~86px, ridotta se serve per stare nei margini
    f = _G.get('tf')
    if f is None:
        size = 86
        while size > 40:
            f = _font(F_BOLD, size)
            if f.getlength(TITOLO) <= 1800: break
            size -= 2
        _G['tf'] = f
    return f

def _bg():
    # sfondo standard con venature + marchio in alto (statici, cache)
    im = _G.get('bg')
    if im is None:
        im = Image.new('RGB', (W, H), SFONDO)
        d = ImageDraw.Draw(im)
        for x in range(0, W + 1, 108):
            d.line([(x, 0), (x, H)], fill=VENA, width=2)
        fb = _font(F_BOLD, 30)
        txt = 'FALEGNAME DIGITALE'
        wt = d.textlength(txt, font=fb)
        bx = (W - (wt + 26)) / 2.0
        d.rectangle([bx, 80 - 7, bx + 14, 80 + 7], fill=ARANCIO)
        d.text((bx + 26, 80), txt, font=fb, fill=GRIGIO, anchor='lm')
        _G['bg'] = im
    return im

def frame(t, dur):
    dur = max(float(dur), 1e-6)
    # timeline interna riscalata sulla durata reale: si conclude sempre a t=dur
    tt = _clamp01(t / dur) * DUR_NOM
    im = _bg().copy()
    d = ImageDraw.Draw(im)

    # --- titolo: fade + leggero slide verso l'alto (0.0 - 0.5) ---
    a = _ease(tt / 0.5)
    if a > 0.0:
        ft = _title_font()
        dy = int(18 * (1.0 - a))
        d.text((W // 2, 170 + dy), TITOLO, font=ft,
               fill=_mix(SFONDO, BIANCO, a), anchor='mm')

    # --- righe tabella: una alla volta, fade + slide da sinistra ---
    f_lab = _font(F_BOLD, 40)
    f_imp = _font(F_MONO, 42)
    for i, (nome, val) in enumerate(RIGHE):
        st = 0.7 + 0.55 * i
        p = (tt - st) / 0.5
        if p <= 0.0: continue
        a = _ease(p)
        dx = int(-46 * (1.0 - a))
        y = ROW_Y0 + i * ROW_H
        d.text((TAB_L + dx, y), nome, font=f_lab,
               fill=_mix(SFONDO, BIANCO, a), anchor='lm')
        # importo che conta da 0 al valore finale (~0.5s)
        v = int(round(val * _easeout(p)))
        d.text((TAB_R + dx, y), _fmt(v), font=f_imp,
               fill=_mix(SFONDO, GRIGIO, a), anchor='rm')
        ys = y + 29
        d.line([(TAB_L, ys), (TAB_R, ys)], fill=_mix(SFONDO, SEP, a), width=1)

    # --- totale in arancio: conteggio veloce (4.7 - 5.3) + pop (5.3 - 5.6) ---
    p = (tt - 4.7) / 0.6
    if p > 0.0:
        a = _ease((tt - 4.7) / 0.35)
        v = int(round(TOT_VAL * _easeout(p)))
        pp = (tt - 5.3) / 0.3
        sc = 1.0
        if 0.0 < pp < 1.0:
            sc = 1.0 + 0.06 * math.sin(math.pi * pp)   # 1.0 -> 1.06 -> 1.0
        f_tot = _font(F_BOLD, int(round(110 * sc)))
        col = _mix(SFONDO, ARANCIO, a)
        d.text((TAB_L, TOT_Y), 'TOTALE MOBILE', font=f_tot, fill=col, anchor='lm')
        d.text((TAB_R, TOT_Y), _fmt(v), font=f_tot, fill=col, anchor='rm')

    # --- caption sotto il totale (5.7 - 6.2) ---
    p = (tt - 5.7) / 0.5
    if p > 0.0:
        a = _ease(p)
        fc = _font(F_BOLD, 44)
        d.text((W // 2, CAP_Y), 'prima di accendere la sega', font=fc,
               fill=_mix(SFONDO, GRIGIO, a), anchor='mm')

    return im
