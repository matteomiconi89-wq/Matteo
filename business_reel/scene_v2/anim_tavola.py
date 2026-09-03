# -*- coding: utf-8 -*-
# Scena "LA TAVOLA PER IL CLIENTE" — Ken Burns sulla tavola A3 reale.
# Esporta: DUR_NOM (float), frame(t, dur) -> PIL.Image RGB 1920x1080.
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def _fp(cands):
    for p in cands:
        if os.path.exists(p): return p
    raise RuntimeError('font mancante')
_WF = r'C:\Windows\Fonts'; _LF = '/usr/share/fonts/truetype/dejavu'
F_BOLD = _fp([os.path.join(_WF,'segoeuib.ttf'), os.path.join(_LF,'DejaVuSans-Bold.ttf')])
F_REG  = _fp([os.path.join(_WF,'segoeui.ttf'),  os.path.join(_LF,'DejaVuSans.ttf')])
F_MONO = _fp([os.path.join(_WF,'consola.ttf'),  os.path.join(_LF,'DejaVuSansMono.ttf')])

W, H = 1920, 1080
SFONDO=(18,16,14); ARANCIO=(255,140,66); BIANCO=(245,242,238); GRIGIO=(150,145,140)
VERDE=(110,200,120); ROSSO=(220,80,70); CIANO=(143,214,247)

DUR_NOM = 8.0

# --- layout fisso ---
BAND_H  = 160                      # fascia arancio in alto
SH_Y0, SH_Y1 = 172, 944            # area verticale del foglio
DISP_H  = SH_Y1 - SH_Y0            # 772
DISP_W  = 1092                     # ~ aspetto del foglio A3 (1.4146)
SH_X0   = (W - DISP_W)//2          # 414
CAP_Y   = 996                      # centro caption in basso

_G = {}                            # cache lazy di elementi statici

def _font(path, size):
    k = ('f', path, size)
    if k not in _G: _G[k] = ImageFont.truetype(path, size)
    return _G[k]

def _ease(x):
    # smoothstep morbido, clampato
    x = 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)
    return x*x*(3.0-2.0*x)

def _sorgente():
    # carica il PNG alta risoluzione una volta; placeholder se manca
    if 'src' in _G: return _G['src']
    p = os.environ.get('FILIERA_TAVOLA_PNG',
        '/tmp/claude-0/-home-user-Matteo/7a9c7fd3-d6f6-583a-8b7a-8df21dd0bb05/scratchpad/v2/tavola_demo.png')
    im = None
    try:
        if os.path.exists(p):
            im = Image.open(p).convert('RGB')
    except Exception:
        im = None
    if im is None:
        # placeholder: foglio bianco con scritta grigia, mai crashare
        im = Image.new('RGB', (2480, 1754), (252, 250, 247))
        d = ImageDraw.Draw(im)
        d.rectangle([30, 30, 2449, 1723], outline=(200, 196, 190), width=6)
        f = _font(F_BOLD, 150)
        d.text((1240, 877), 'TAVOLA CLIENTE', font=f, fill=GRIGIO, anchor='mm')
    # mipmap: mai piu' grande del necessario allo zoom max (solo downscale dopo)
    mw = min(im.width, 2760)
    if mw < im.width:
        mh = max(1, round(im.height * mw / float(im.width)))
        im = im.resize((mw, mh), Image.LANCZOS)
    _G['src'] = im
    return im

def _base():
    # sfondo + fasce + ombra + cornici: tutto lo statico, composto una volta
    if 'base' in _G: return _G['base']
    im = Image.new('RGB', (W, H), SFONDO)
    d = ImageDraw.Draw(im)
    # venature verticali discrete
    for x in range(108, W, 108):
        d.line([(x, 0), (x, H)], fill=(24, 21, 18), width=2)
    # ombra morbida sotto il foglio
    sh = Image.new('L', (W, H), 0)
    ds = ImageDraw.Draw(sh)
    ds.rectangle([SH_X0-6, SH_Y0-2, SH_X0+DISP_W+6, SH_Y1+14], fill=120)
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    im.paste(Image.new('RGB', (W, H), (6, 5, 4)), (0, 0), sh)
    # cornice sottile attorno al foglio + tacche arancio agli angoli
    d = ImageDraw.Draw(im)
    d.rectangle([SH_X0-3, SH_Y0-3, SH_X0+DISP_W+2, SH_Y1+2], outline=(62, 56, 50), width=2)
    L, o = 30, 9
    for cx, sx in ((SH_X0, 1), (SH_X0+DISP_W, -1)):
        for cy, sy in ((SH_Y0, 1), (SH_Y1, -1)):
            d.line([(cx-sx*o, cy-sy*o), (cx-sx*o+sx*L, cy-sy*o)], fill=ARANCIO, width=3)
            d.line([(cx-sx*o, cy-sy*o), (cx-sx*o, cy-sy*o+sy*L)], fill=ARANCIO, width=3)
    # fascia arancio in alto
    d.rectangle([0, 0, W, BAND_H], fill=ARANCIO)
    d.line([(0, BAND_H), (W, BAND_H)], fill=(200, 105, 45), width=2)
    _G['base'] = im
    return im

def _mix(a, b, k):
    return tuple(int(round(a[i] + (b[i]-a[i]) * k)) for i in range(3))

# tappe Ken Burns: (u, cx, cy, w) in frazioni del foglio; w = larghezza crop
_KEY = [
    (0.00, 0.500, 0.500, 0.998),   # vista intera
    (0.30, 0.490, 0.485, 0.950),   # zoom lento (senza tagliare il cartiglio)
    (0.58, 0.245, 0.245, 0.420),   # prospetto quotato (alto-sinistra)
    (0.70, 0.490, 0.245, 0.530),   # arco: leggero zoom-out durante il pan
    (0.82, 0.735, 0.245, 0.420),   # sezione A-A (alto-destra)
    (0.955, 0.500, 0.500, 0.992),  # ritorno concluso; poi resta vivo col respiro
]

def _cam(u, t):
    # interpola le tappe con easing; respiro micro-zoom per non fermarsi mai
    if u <= _KEY[0][0]: cx, cy, w = _KEY[0][1:]
    elif u >= _KEY[-1][0]: cx, cy, w = _KEY[-1][1:]
    else:
        for i in range(len(_KEY)-1):
            u0, x0, y0, w0 = _KEY[i]; u1, x1, y1, w1 = _KEY[i+1]
            if u0 <= u <= u1:
                k = _ease((u-u0)/(u1-u0))
                cx = x0+(x1-x0)*k; cy = y0+(y1-y0)*k; w = w0+(w1-w0)*k
                break
    w  = w  * (1.0 + 0.003*math.sin(2*math.pi*t/7.0))
    cy = cy + 0.0015*math.sin(2*math.pi*t/9.0 + 1.3)
    return cx, cy, w

def frame(t, dur):
    dur = max(float(dur), 0.001)
    u = min(max(t/dur, 0.0), 1.0)
    src = _sorgente()
    im = _base().copy()

    # crop con lo stesso aspect ratio dell'area di destinazione (no distorsioni)
    A = DISP_W / float(DISP_H)
    cx, cy, w = _cam(u, t)
    cw = w * src.width
    ch = cw / A
    if ch > src.height: ch = float(src.height); cw = ch * A
    if cw > src.width:  cw = float(src.width);  ch = cw / A
    x0 = cx*src.width - cw/2.0;  y0 = cy*src.height - ch/2.0
    x0 = min(max(x0, 0.0), src.width - cw)
    y0 = min(max(y0, 0.0), src.height - ch)
    tile = src.resize((DISP_W, DISP_H), Image.LANCZOS, box=(x0, y0, x0+cw, y0+ch))

    # fade-in rapido del foglio nei primi istanti
    a = _ease(u/0.05) if u < 0.05 else 1.0
    if a < 1.0:
        if 'buio' not in _G: _G['buio'] = Image.new('RGB', (DISP_W, DISP_H), SFONDO)
        tile = Image.blend(_G['buio'], tile, a)
    im.paste(tile, (SH_X0, SH_Y0))

    d = ImageDraw.Draw(im)
    # titolo scuro sulla fascia arancio: subito presente, micro-assestamento
    kt = _ease(u/0.06)
    ft = _font(F_BOLD, 46)
    d.text((W//2, 88 - int(round(6*(1.0-kt)))), 'NOVITÀ — LA TAVOLA PER IL CLIENTE',
           font=ft, fill=(24, 20, 16), anchor='mm')
    # caption in basso: bianco bold, "+" arancio, centrata come blocco unico
    kc = _ease((u-0.04)/0.10)
    fc = _font(F_BOLD, 36)
    seg = [('PDF in scala da stampare', _mix(SFONDO, BIANCO, kc)),
           ('  +  ', _mix(SFONDO, ARANCIO, kc)),
           ('DWG 1:1 con quote vere', _mix(SFONDO, BIANCO, kc))]
    tw = sum(d.textlength(s, font=fc) for s, _ in seg)
    x = (W - tw)/2.0
    for s, col in seg:
        d.text((x, CAP_Y), s, font=fc, fill=col, anchor='lm')
        x += d.textlength(s, font=fc)
    return im
