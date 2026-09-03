# -*- coding: utf-8 -*-
# SCENA "IL 3D DEL PROGETTISTA" — viewport stile AutoCAD scuro.
# Un armadio wireframe ciano si costruisce pannello per pannello, poi orbita.
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

# ---- palette di casa ----
SFONDO  = (18,16,14)
ARANCIO = (255,140,66)
BIANCO  = (245,242,238)
GRIGIO  = (150,145,140)
VERDE   = (110,200,120)
CIANO   = (143,214,247)
CIANO_SCURO = (96,158,186)
BARRA_TITOLO = (28,33,40)
BARRA_CMD    = (24,29,36)
GRIGLIA_CAD  = (20,26,33)

W, H = 1920, 1080
DUR_NOM = 7.0

# ---- layout viewport ----
H_TITOLO = 90          # barra titolo in alto
H_CMD    = 64          # barra comandi in basso
Y_CMD    = H - H_CMD   # 1016: bordo alto barra comandi

# ---- proiezione prospettica (collaudata) ----
CX, CY, CZ = 1200, 1300, 300
FOC = 4600
SC, XC, YB = 0.305, 960, 520  # scala e centro tarati per il 1920x1080
ANG0 = 26.0                   # angolo base di costruzione

def _ease(u):
    # ease-in-out coseno, clampato
    u = max(0.0, min(1.0, u))
    return 0.5 - 0.5*math.cos(math.pi*u)

def proietta(p, ang, sc, xc, yb):
    a = math.radians(ang)
    x, y, z = p[0]-CX, p[1]-CY, p[2]-CZ
    xr = x*math.cos(a) + z*math.sin(a)
    zr = -x*math.sin(a) + z*math.cos(a)
    s = FOC / (FOC + 1500 - zr)
    return (xc + xr*s*sc, yb - y*s*sc)

def box_3d(dr, b, ang, col, sc, xc, yb, wdt=2):
    x1,x2,y1,y2,z1,z2 = b
    v = [(x1,y1,z1),(x2,y1,z1),(x2,y2,z1),(x1,y2,z1),(x1,y1,z2),(x2,y1,z2),(x2,y2,z2),(x1,y2,z2)]
    p = [proietta(q, ang, sc, xc, yb) for q in v]
    for a_,b_ in [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]:
        dr.line([p[a_], p[b_]], fill=col, width=wdt)

# ---- pannelli dell'armadio 2400x2600x600, in ordine di apparizione ----
PANNELLI = [
    ((0,18,0,2600,0,600),        CIANO, 2),   # fianco sx
    ((2382,2400,0,2600,0,600),   CIANO, 2),   # fianco dx
    ((18,2382,60,78,0,600),      CIANO, 2),   # fondo
    ((18,2382,2582,2600,0,600),  CIANO, 2),   # cielo
    ((18,2382,78,2582,0,14),     CIANO_SCURO, 2),  # schienale
    ((791,809,78,2582,0,582),    CIANO, 2),   # divisorio 1
    ((1591,1609,78,2582,0,582),  CIANO, 2),   # divisorio 2
    ((18,791,1894,1912,40,582),  CIANO, 2),   # ripiano sx
    ((809,1591,1894,1912,40,582),CIANO, 2),   # ripiano centro
    ((1609,2382,1894,1912,40,582),CIANO, 2),  # ripiano dx
    ((829,1571,78,378,100,582),  CIANO, 2),   # cassetto basso
    ((829,1571,388,688,100,582), CIANO, 2),   # cassetto alto
]
for _i in range(6):  # 6 ante frontali in ciano scuro
    _x0 = _i*400
    PANNELLI.append(((_x0+3,_x0+397,0,2600,600,618), CIANO_SCURO, 2))
N_PAN = len(PANNELLI)
FADE = 0.25  # durata fade-in di ogni pannello

def _lerp_col(c1, c2, k):
    k = max(0.0, min(1.0, k))
    return (int(c1[0]+(c2[0]-c1[0])*k), int(c1[1]+(c2[1]-c1[1])*k), int(c1[2]+(c2[2]-c1[2])*k))

def _col_fade(k, target):
    # fade-in con piccolo "flash" chiaro stile rigenerazione CAD
    if k < 0.55:
        return _lerp_col(SFONDO, BIANCO, k/0.55)
    return _lerp_col(BIANCO, target, (k-0.55)/0.45)

# ---- cache lazy di elementi statici ----
_BASE = None
_FONTS = None
_PILL = None      # (rgb, alpha, w, h)

def _fonts():
    global _FONTS
    if _FONTS is None:
        _FONTS = {
            'titolo': ImageFont.truetype(F_MONO, 30),
            'cmd':    ImageFont.truetype(F_MONO, 26),
            'stato':  ImageFont.truetype(F_MONO, 20),
            'ucs':    ImageFont.truetype(F_MONO, 20),
            'cap':    ImageFont.truetype(F_BOLD, 52),
        }
    return _FONTS

def _base():
    global _BASE
    if _BASE is None:
        f = _fonts()
        img = Image.new('RGB', (W, H), SFONDO)
        dr = ImageDraw.Draw(img)
        # griglia CAD tenue nella zona viewport
        for x in range(0, W+1, 108):
            dr.line([(x, H_TITOLO), (x, Y_CMD)], fill=GRIGLIA_CAD, width=1)
        for y in range(H_TITOLO+108, Y_CMD, 108):
            dr.line([(0, y), (W, y)], fill=GRIGLIA_CAD, width=1)
        # barra titolo
        dr.rectangle([0, 0, W, H_TITOLO-1], fill=BARRA_TITOLO)
        dr.line([(0, H_TITOLO-2), (W, H_TITOLO-2)], fill=ARANCIO, width=2)  # accento brand
        dr.text((60, 45), 'AutoCAD \u2014 armadio 3D del progettista.dwg',
                font=f['titolo'], fill=BIANCO, anchor='lm')
        # tre pallini finestra a destra
        for i, c in enumerate((VERDE, ARANCIO, (220,80,70))):
            cx = 1770 + i*40
            dr.ellipse([cx-9, 36, cx+9, 54], fill=c)
        # barra comandi (il testo cambia nel tempo, disegnato in frame)
        dr.rectangle([0, Y_CMD, W, H], fill=BARRA_CMD)
        dr.line([(0, Y_CMD), (W, Y_CMD)], fill=(40,47,56), width=1)
        # icona UCS in basso a sinistra (assi X arancio / Y verde)
        ox, oy = 112, 962
        dr.line([(ox, oy), (ox+64, oy)], fill=ARANCIO, width=3)
        dr.polygon([(ox+64, oy-6), (ox+64, oy+6), (ox+76, oy)], fill=ARANCIO)
        dr.line([(ox, oy), (ox, oy-64)], fill=VERDE, width=3)
        dr.polygon([(ox-6, oy-64), (ox+6, oy-64), (ox, oy-76)], fill=VERDE)
        dr.text((ox+82, oy-2), 'X', font=f['ucs'], fill=ARANCIO, anchor='lm')
        dr.text((ox-2, oy-84), 'Y', font=f['ucs'], fill=VERDE, anchor='ms')
        _BASE = img
    return _BASE

def _pill():
    global _PILL
    if _PILL is None:
        f = _fonts()
        txt = 'il 3D che hai gi\u00e0'
        tmp = ImageDraw.Draw(Image.new('RGB', (8, 8)))
        bb = tmp.textbbox((0, 0), txt, font=f['cap'])
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
        pw, ph = tw + 96, th + 44
        pill = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pill)
        pd.rounded_rectangle([0, 0, pw-1, ph-1], radius=ph//2, fill=(0, 0, 0, 185))
        pd.text((pw//2 - (bb[2]+bb[0])//2, ph//2 - (bb[3]+bb[1])//2), txt,
                font=f['cap'], fill=BIANCO)
        _PILL = (pill.convert('RGB'), pill.split()[3], pw, ph)
    return _PILL

def frame(t, dur):
    dur = max(float(dur), 0.001)
    f = _fonts()
    img = _base().copy()
    dr = ImageDraw.Draw(img)

    # --- timing interno scalato su dur ---
    t0 = 0.05*dur                 # inizio costruzione
    fine_costr = 0.55*dur         # fine costruzione, poi orbita
    passo = (fine_costr - FADE - t0) / max(1, N_PAN-1)

    # --- angolo: fisso in costruzione, poi oscillazione sinusoidale morbida ---
    if t <= fine_costr:
        ang = ANG0
    else:
        tt = t - fine_costr
        env = _ease(min(1.0, tt/1.2))           # rampa dolce dell'orbita
        ang = ANG0 + 13.0*env*math.sin(2*math.pi*tt/5.5)

    # --- armadio pannello per pannello ---
    for i, (b, col, wdt) in enumerate(PANNELLI):
        k = (t - (t0 + i*passo)) / FADE
        if k <= 0:
            continue
        box_3d(dr, b, ang, _col_fade(k, col) if k < 1.0 else col, SC, XC, YB, wdt)

    # --- barra comandi: testo mono verde + cursore lampeggiante ---
    if t <= fine_costr:
        txt_cmd = 'Comando: _rigenera  modello 3D' + '.'*(1 + int(t*2.5) % 3)
    else:
        txt_cmd = 'Comando: _orbit'
    yc = Y_CMD + H_CMD//2
    dr.text((60, yc), txt_cmd, font=f['cmd'], fill=VERDE, anchor='lm')
    if int(t*2.4) % 2 == 0:  # cursore a blocco
        cw = dr.textlength(txt_cmd, font=f['cmd'])
        dr.rectangle([60+cw+10, yc-13, 60+cw+24, yc+13], fill=VERDE)
    dr.text((1860, yc), 'MODELLO | OSNAP | GRIGLIA', font=f['stato'], fill=GRIGIO, anchor='rm')

    # --- caption a pillola sopra la barra comandi ---
    ca = _ease((t - 0.30*dur) / 0.5)
    if ca > 0:
        rgb, alpha, pw, ph = _pill()
        px = (W - pw)//2
        py = Y_CMD - 20 - ph + int((1.0-ca)*22)   # leggera salita in ingresso
        if ca >= 1.0:
            img.paste(rgb, (px, py), alpha)
        else:
            img.paste(rgb, (px, py), alpha.point(lambda v: int(v*ca)))
    return img
