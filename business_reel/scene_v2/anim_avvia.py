# -*- coding: utf-8 -*-
# Scena "IL CLICK" — un cursore mouse preme il grande bottone AVVIA.
# Esporta: DUR_NOM (durata nominale) e frame(t, dur) -> PIL.Image RGB 1920x1080.
import os, math
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
VERDE   = (110, 200, 120)
ROSSO   = (220, 80, 70)
CIANO   = (143, 214, 247)

DUR_NOM = 4.5

# geometria bottone (centro e semi-dimensioni: 560x150)
BX, BY, BW2, BH2 = 960, 560, 280, 75

_CACHE = {}  # cache lazy di elementi statici

def _ease(p):
    # ease-in-out morbido, con clamp
    p = max(0.0, min(1.0, p))
    return 0.5 - 0.5 * math.cos(math.pi * p)

def _lerp(a, b, k):
    k = max(0.0, min(1.0, k))
    return tuple(int(round(a[i] + (b[i] - a[i]) * k)) for i in range(3))

def _bg():
    # sfondo standard: tinta + venature verticali + marchio in alto
    im = _CACHE.get('bg')
    if im is None:
        im = Image.new('RGB', (W, H), SFONDO)
        dr = ImageDraw.Draw(im)
        for x in range(54, W, 108):
            dr.line([(x, 0), (x, H)], fill=(24, 21, 18), width=2)
        fb = ImageFont.truetype(F_BOLD, 46)
        dr.text((W // 2, 66), 'FALEGNAME  DIGITALE', font=fb, fill=GRIGIO, anchor='ma')
        dr.rounded_rectangle([W // 2 - 60, 134, W // 2 + 60, 139], radius=2, fill=ARANCIO)
        _CACHE['bg'] = im
    return im

def _title():
    # titolo su un rigo, due corpi diversi, allineati al baseline
    im = _CACHE.get('title')
    if im is None:
        f1 = ImageFont.truetype(F_BOLD, 54)
        f2 = ImageFont.truetype(F_BOLD, 82)
        t1, t2 = 'Io premo ', 'UN BOTTONE.'
        tmp = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        w1 = tmp.textlength(t1, font=f1)
        w2 = tmp.textlength(t2, font=f2)
        im = Image.new('RGBA', (int(w1 + w2) + 8, 104), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        dr.text((0, 88), t1, font=f1, fill=BIANCO + (255,), anchor='ls')
        dr.text((w1, 88), t2, font=f2, fill=BIANCO + (255,), anchor='ls')
        _CACHE['title'] = im
    return im

def _subtext():
    # riga "FILIERA UN CLIC — in esecuzione" in mono, due colori
    im = _CACHE.get('sub')
    if im is None:
        fm = ImageFont.truetype(F_MONO, 42)
        a, b = 'FILIERA UN CLIC', ' — in esecuzione'
        tmp = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        wa = tmp.textlength(a, font=fm)
        wb = tmp.textlength(b, font=fm)
        im = Image.new('RGBA', (int(wa + wb) + 4, 58), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        dr.text((0, 6), a, font=fm, fill=ARANCIO + (255,))
        dr.text((wa, 6), b, font=fm, fill=BIANCO + (255,))
        _CACHE['sub'] = im
    return im

def _font(key, path, size):
    f = _CACHE.get(key)
    if f is None:
        f = ImageFont.truetype(path, size)
        _CACHE[key] = f
    return f

def _paste_fade(img, layer, xy, a):
    # incolla un layer RGBA con alfa globale a (0..1)
    if a <= 0.0:
        return
    if a >= 0.999:
        img.paste(layer, xy, layer)
    else:
        m = layer.split()[3].point(lambda v: int(v * a))
        img.paste(layer, xy, m)

# poligono del cursore mouse (punta in alto a sinistra, ~40px)
_PTS = [(0, 0), (0, 34), (8, 26), (14, 40), (18, 38), (13, 24), (24, 24)]

def _cursore(d, x, y):
    pts = [(x + px, y + py) for px, py in _PTS]
    d.polygon(pts, fill=BIANCO)
    d.line(pts + [pts[0]], fill=(22, 19, 16), width=3, joint='curve')

def frame(t, dur):
    dur = max(float(dur), 0.001)
    t = max(0.0, min(float(t), dur))
    img = _bg().copy()
    d = ImageDraw.Draw(img)

    # tempi chiave: i beat principali scalano su dur, i micro-tempi restano assoluti
    tc = 0.55 * dur                  # istante del click
    tin0, tin1 = 0.15 * dur, 0.45 * dur  # viaggio del cursore
    PRESS = 0.2                      # durata pressione (s)

    # --- stato del bottone ---
    a_btn = _ease((t - 0.04 * dur) / (0.10 * dur))       # comparsa
    hov = _ease((t - tin1) / (0.06 * dur)) if t > tin1 else 0.0  # hover
    q = (t - tc) / PRESS
    pr = math.sin(math.pi * q) if 0.0 <= q <= 1.0 else 0.0       # pressione 0->1->0

    col = _lerp(ARANCIO, (255, 172, 112), 0.55 * hov)    # schiarita hover
    col = _lerp(col, (196, 102, 44), 0.85 * pr)          # scurita al click
    col = _lerp(SFONDO, col, a_btn)                      # fade d'ingresso
    s = (0.94 + 0.06 * a_btn) * (1.0 - 0.03 * pr)        # scala (comparsa + -3% al click)
    bw, bh = BW2 * s, BH2 * s

    # --- anello radiale dopo il click (ellittico, due onde; sotto ai testi) ---
    rt0 = tc + PRESS * 0.6
    for delay, amp, kal in ((0.0, 250, 1.0), (0.16, 180, 0.55)):
        e = (t - rt0 - delay) / 0.8
        if 0.0 < e < 1.0:
            eo = 1.0 - (1.0 - e) ** 2                    # espansione ease-out
            px_, py_ = 20 + amp * eo, 14 + amp * 0.36 * eo
            al = ((1.0 - e) ** 2.0) * kal * a_btn
            rc = _lerp(SFONDO, ARANCIO, al)
            d.rounded_rectangle(
                [BX - bw - px_, BY - bh - py_, BX + bw + px_, BY + bh + py_],
                radius=30 + py_ * 0.8, outline=rc, width=max(2, int(3 + 8 * (1.0 - e))))

    # --- titolo (fade + leggera salita), sopra l'anello ---
    a_tit = _ease(t / (0.10 * dur))
    tit = _title()
    _paste_fade(img, tit, ((W - tit.width) // 2, 316 + int((1 - a_tit) * 20)), a_tit)

    # --- bottone (ombra + corpo + etichetta) ---
    if a_btn > 0.0:
        d.rounded_rectangle([BX - bw, BY - bh + 8, BX + bw, BY + bh + 8],
                            radius=30, fill=_lerp(SFONDO, (10, 9, 8), a_btn))
        d.rounded_rectangle([BX - bw, BY - bh, BX + bw, BY + bh], radius=30, fill=col)
        fA = _font('avvia', F_BOLD, 64)
        d.text((BX, BY + 3 * pr), 'AVVIA', font=fA,
               fill=_lerp(col, SFONDO, a_btn), anchor='mm')

    # --- riga di stato dopo il click, con cursore terminale lampeggiante ---
    ta0 = tc + 0.3
    a_sub = _ease((t - ta0) / 0.45)
    if a_sub > 0.0:
        sub = _subtext()
        tot = sub.width + 36                     # testo + spazio + blocco cursore
        x0 = (W - tot) // 2
        y0 = 806 + int((1 - a_sub) * 16)
        _paste_fade(img, sub, (x0, y0), a_sub)
        on = int((t - ta0) / 0.4) % 2 == 0       # lampeggio 0.4s on/off
        if on:
            d.rectangle([x0 + sub.width + 14, y0 + 8, x0 + sub.width + 36, y0 + 50],
                        fill=_lerp(SFONDO, ARANCIO, a_sub))

    # --- cursore mouse: bezier quadratica da basso-destra al bottone ---
    if t < tin0:
        u = 0.0
    elif t < tin1:
        u = _ease((t - tin0) / (tin1 - tin0))
    else:
        u = 1.0
    p0, pc, p1 = (1985, 1150), (1420, 880), (1002, 588)
    mx = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * pc[0] + u * u * p1[0]
    my = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * pc[1] + u * u * p1[1]
    _cursore(d, mx, my + 3 * pr)                 # piccolo affondo durante il click

    return img
