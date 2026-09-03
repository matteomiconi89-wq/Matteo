# -*- coding: utf-8 -*-
# Scena "LA FILIERA GIRA" — video FILIERA UN CLIC / FALEGNAME DIGITALE (1920x1080).
# Sinistra: console di esecuzione con log progressivo. Destra: 5 tappe della filiera
# che si accendono in sincrono col log. In basso: barra avanzamento 0-100%.
# Finale: barra verde + banner "COMMESSA PRONTA". Esporta DUR_NOM e frame(t, dur).

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

DUR_NOM = 7.5
W, H = 1920, 1080

# palette di casa
SFONDO  = (18, 16, 14)
ARANCIO = (255, 140, 66)
BIANCO  = (245, 242, 238)
GRIGIO  = (150, 145, 140)
VERDE   = (110, 200, 120)
ROSSO   = (220, 80, 70)
CIANO   = (143, 214, 247)
VENA    = (24, 21, 18)      # venature verticali dello sfondo
CONSOLE = (24, 29, 36)      # pannello console
TITLEBAR = (33, 40, 49)     # barra titolo console
BOX_OFF = (44, 40, 36)      # tappa spenta
TESTO_SCURO = (30, 25, 20)  # testo su tappa accesa
ARROW_OFF = (82, 76, 70)    # freccia spenta

# geometria
CX0, CY0, CX1, CY1 = 60, 60, 1145, 930      # pannello console (~58%)
TBH = 52                                     # altezza barra titolo
LOG_X, LOG_Y0, LINE_H = 100, 142, 62         # area righe di log
RX0, RX1 = 1205, 1860                        # colonna tappe (~42%)
BOX_H, BOX_GAP = 130, 55
BAR_X0, BAR_Y0, BAR_X1, BAR_Y1 = 60, 966, 1760, 1010  # barra avanzamento

# righe di log: liste di segmenti (testo, colore) — etichette verdi/bianche
LOG = [
    [('> ', VERDE), ('STEP 3D  ->  DWG ', BIANCO), ('........ ', GRIGIO), ('ok', VERDE)],
    [('> ', VERDE), ('26 solidi letti, ', BIANCO), ('13 pezzi UNICI', ARANCIO)],
    [('> ', VERDE), ('001_FIANCO_SX.dxf', BIANCO)],
    [('> ', VERDE), ('002_FIANCO_DX.dxf', BIANCO)],
    [('> ', VERDE), ('003_CIELO.dxf   ', BIANCO), ('(+10 pezzi)', GRIGIO)],
    [('> ', VERDE), ('distinta.xlsx ', BIANCO), ('............ ', GRIGIO), ('ok', VERDE)],
    [('> ', VERDE), ('sezionatura.xlsx ', BIANCO), ('......... ', GRIGIO), ('ok', VERDE)],
    [('> ', VERDE), ('TLF Masterwood: ', BIANCO), ('13 programmi', ARANCIO)],
    [('> ', VERDE), ('MPRX Homag:     ', BIANCO), ('13 programmi', ARANCIO)],
    [('> ', VERDE), ('VISTE_MOBILE_TV.pdf ', BIANCO), ('...... ', GRIGIO), ('ok', VERDE)],
    [('> ', VERDE), ('ORDINI: 3 fornitori ', BIANCO), ('...... ', GRIGIO), ('ok', VERDE)],
    [('> ', VERDE), ('RIEPILOGO COSTI ', BIANCO), ('.......... ', GRIGIO), ('ok', VERDE)],
]
NLOG = len(LOG)

# tappe a destra e riga di log che accende ciascuna (ordine visivo alto->basso)
STAGES = ['STEP 3D', 'DXF di OGNI pezzo', 'PROGRAMMI UNICI',
          'DISTINTA + SEZIONATURA', 'TLF | MPRX']
STAGE_LINE = [0, 2, 4, 5, 8]

# cache lazy
_FONTS = {}
_BG = None
_BANNER = None

def _font(path, size):
    k = (path, size)
    if k not in _FONTS:
        _FONTS[k] = ImageFont.truetype(path, size)
    return _FONTS[k]

def _clamp(x, a=0.0, b=1.0):
    return a if x < a else (b if x > b else x)

def _ease(x):
    # ease-in-out morbido (smoothstep)
    x = _clamp(x)
    return x * x * (3.0 - 2.0 * x)

def _lerp(c1, c2, f):
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * f)) for i in range(3))

def _bg():
    # sfondo statico: venature + pannello console + barra titolo + bordo barra
    global _BG
    if _BG is not None:
        return _BG
    img = Image.new('RGB', (W, H), SFONDO)
    d = ImageDraw.Draw(img)
    for x in range(0, W + 1, 108):
        d.line((x, 0, x, H), fill=VENA, width=2)
    # pannello console con angoli arrotondati
    d.rounded_rectangle((CX0, CY0, CX1, CY1), radius=18, fill=CONSOLE)
    # barra titolo (angoli alti arrotondati, base squadrata)
    d.rounded_rectangle((CX0, CY0, CX1, CY0 + TBH), radius=18, fill=TITLEBAR)
    d.rectangle((CX0, CY0 + TBH - 20, CX1, CY0 + TBH), fill=TITLEBAR)
    d.line((CX0, CY0 + TBH, CX1, CY0 + TBH), fill=(16, 20, 26), width=2)
    # semafori della finestra
    ty = CY0 + TBH // 2
    for i, c in enumerate((ROSSO, ARANCIO, VERDE)):
        cx = 98 + i * 32
        d.ellipse((cx - 8, ty - 8, cx + 8, ty + 8), fill=c)
    d.text((196, ty + 1), 'FILIERA_GENERICO \u2014 esecuzione',
           font=_font(F_MONO, 24), fill=GRIGIO, anchor='lm')
    # bordo barra avanzamento
    d.rounded_rectangle((BAR_X0, BAR_Y0, BAR_X1, BAR_Y1), radius=10,
                        outline=GRIGIO, width=2)
    _BG = img
    return _BG

def _banner():
    # banner finale "COMMESSA PRONTA" pre-renderizzato in RGBA
    global _BANNER
    if _BANNER is not None:
        return _BANNER
    txt = 'COMMESSA PRONTA'
    size = 84
    while size > 56:
        if _font(F_BOLD, size).getlength(txt) + 130 <= (CX1 - CX0) - 40:
            break
        size -= 4
    f = _font(F_BOLD, size)
    bw = int(f.getlength(txt)) + 130
    bh = size + 86
    im = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    dd.rounded_rectangle((3, 3, bw - 4, bh - 4), radius=24,
                         fill=SFONDO + (240,), outline=VERDE + (255,), width=4)
    dd.text((bw // 2, bh // 2), txt, font=f, fill=VERDE + (255,), anchor='mm')
    _BANNER = im
    return _BANNER

def _line_start(i, dur):
    # partenze distribuite sul primo ~85% della durata reale
    return dur * (0.04 + 0.78 * (i / float(NLOG - 1)))

def frame(t, dur):
    dur = max(float(dur), 0.001)
    t = _clamp(float(t), 0.0, dur)
    F = min(0.35, 0.05 * dur)          # durata fade di ogni riga
    img = _bg().copy()
    d = ImageDraw.Draw(img)
    fm = _font(F_MONO, 34)

    # --- righe di log: appaiono una alla volta e restano ---
    prog_sum = 0.0
    shown = 0
    for i, segs in enumerate(LOG):
        f = _ease((t - _line_start(i, dur)) / F)
        prog_sum += f
        if f <= 0.0:
            continue
        if f > 0.45:
            shown = i + 1  # il cursore resta sulla riga finche' non e' ben visibile
        x = LOG_X + int((1.0 - f) * 14)
        y = LOG_Y0 + i * LINE_H
        for txt, col in segs:
            d.text((x, y), txt, font=fm, fill=_lerp(CONSOLE, col, f))
            x += int(fm.getlength(txt))

    # cursore lampeggiante finche' il log sta scrivendo (deterministico su t)
    log_end = _line_start(NLOG - 1, dur) + F
    if t < log_end and shown < NLOG and (t * 2.2) % 1.0 < 0.55:
        cy = LOG_Y0 + shown * LINE_H
        d.rectangle((LOG_X, cy + 4, LOG_X + 18, cy + 40), fill=VERDE)

    # --- tappe a destra: si accendono quando il log arriva alla loro riga ---
    fb = _font(F_BOLD, 33)
    cxm = (RX0 + RX1) // 2
    for j, name in enumerate(STAGES):
        y0 = CY0 + j * (BOX_H + BOX_GAP)
        y1 = y0 + BOX_H
        fj = _ease((t - (_line_start(STAGE_LINE[j], dur) + 0.10)) / 0.45)
        d.rounded_rectangle((RX0, y0, RX1, y1), radius=16,
                            fill=_lerp(BOX_OFF, ARANCIO, fj),
                            outline=_lerp((92, 86, 80), ARANCIO, fj), width=2)
        d.text((cxm, (y0 + y1) // 2), name, font=fb,
               fill=_lerp(GRIGIO, TESTO_SCURO, fj), anchor='mm')
        if j < len(STAGES) - 1:
            # freccia verso il basso: si accende con la tappa successiva
            f2 = _ease((t - (_line_start(STAGE_LINE[j + 1], dur) + 0.10)) / 0.45)
            ac = _lerp(ARROW_OFF, ARANCIO, f2)
            d.line((cxm, y1 + 8, cxm, y1 + 32), fill=ac, width=4)
            d.polygon((cxm - 11, y1 + 30, cxm + 11, y1 + 30, cxm, y1 + 46), fill=ac)

    # --- barra avanzamento sincronizzata col log ---
    p = _clamp(prog_sum / NLOG)
    g = _ease((t - 0.88 * dur) / (0.055 * dur))   # finale: arancio -> verde
    bcol = _lerp(ARANCIO, VERDE, g)
    fx1 = BAR_X0 + 5 + p * (BAR_X1 - BAR_X0 - 10)
    if fx1 > BAR_X0 + 12:
        d.rounded_rectangle((BAR_X0 + 5, BAR_Y0 + 5, fx1, BAR_Y1 - 5),
                            radius=7, fill=bcol)
    d.text((W - 60, (BAR_Y0 + BAR_Y1) // 2), '%d%%' % int(round(p * 100)),
           font=_font(F_MONO, 30), fill=_lerp(BIANCO, VERDE, g), anchor='rm')

    # --- finale: banner COMMESSA PRONTA sopra la console ---
    a = _ease((t - 0.885 * dur) / (0.05 * dur))
    if a > 0.0:
        ban = _banner()
        bw, bh = ban.size
        bx = (CX0 + CX1) // 2 - bw // 2
        by = 480 - bh // 2 + int((1.0 - a) * 26)
        mask = ban.split()[3].point(lambda v: int(v * a))
        img.paste(ban, (bx, by), mask)

    return img
