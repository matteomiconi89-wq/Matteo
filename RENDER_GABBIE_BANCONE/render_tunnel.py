#!/usr/bin/env python3
# Fotoinserimento deterministico: gabbia sul cubo SX + struttura C sul bancone
# Foto base: rif_scena_angolata.jpg (2992x2992). Coordinate misurate in spazio 1200.
from PIL import Image, ImageDraw, ImageFilter

SRC = '/home/user/Matteo/RENDER_GABBIE_BANCONE/rif_scena_angolata.jpg'
OUT = 'render_TUNNEL_v4.png'
K = 2992/1200.0          # 1200-space -> full res
SS = 2                   # supersampling overlay

img = Image.open(SRC).convert('RGB')
W, H = img.size

# ---------- utilità ----------
def S(p):  # 1200-space -> full-res
    return (p[0]*K, p[1]*K)

def lerp(a, b, t):
    return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)

# ---------- 1) PULIZIE (clonazioni) ----------
def patch(dst_box, src_box):
    """copia src su dst (box in 1200-space, interi) con feather"""
    d = tuple(int(v*K) for v in dst_box)
    s = tuple(int(v*K) for v in src_box)
    region = img.crop(s).resize((d[2]-d[0], d[3]-d[1]))
    mask = Image.new('L', region.size, 255)
    mask = mask.filter(ImageFilter.GaussianBlur(6))
    img.paste(region, (d[0], d[1]), mask)

# scatoloni sopra il bancone: per ogni colonna si stira in giù il muro
# (e il pilastro luminoso) preso appena sopra gli scatoloni, fino al bordo
SLOPE = (526-512)/490.0
def edge_y(x): return 512 + SLOPE*(x-403)
X0, X1 = 452, 768
step = 4
for xc in range(X0, X1, step):
    x_px0, x_px1 = int(xc*K), int((xc+step)*K)
    ye = edge_y(xc)
    strip = img.crop((x_px0, int(398*K), x_px1, int(452*K)))
    strip = strip.resize((x_px1-x_px0, int(ye*K)-int(398*K)))
    img.paste(strip, (x_px0, int(398*K)))
    # fondi delle scatole che sporgevano sotto il filo: si stira in su la
    # fascia pulita del fronte del bancone
    fr = img.crop((x_px0, int((ye+17)*K), x_px1, int((ye+47)*K)))
    fr = fr.resize((x_px1-x_px0, int((ye+18)*K)-int(ye*K)))
    img.paste(fr, (x_px0, int(ye*K)))
# filo del piano ridisegnato interpolando i colori reali del bordo pulito
import math
cl = img.crop((int(424*K), int(511*K), int(434*K), int(514*K))).resize((1, 1)).getpixel((0, 0))
cr = img.crop((int(792*K), int(522*K), int(802*K), int(525*K))).resize((1, 1)).getpixel((0, 0))
de = ImageDraw.Draw(img)
for xc in range(X0, X1):
    t = (xc-424)/(792-424)
    col = tuple(int(cl[i]+(cr[i]-cl[i])*t) for i in range(3))
    ye = edge_y(xc)
    de.rectangle([xc*K, (ye-0.7)*K, (xc+1)*K, (ye+0.9)*K], fill=col)
# oggetto a terra davanti al bancone
patch((586, 792, 626, 822), (536, 792, 576, 822))
# attrezzo sul piano del cubo: clone da destra + pareggio luminanza + maschera morbida
tgt = (136, 788, 248, 848)
src = (254, 790, 366, 850)
d0 = tuple(int(v*K) for v in tgt)
s0 = tuple(int(v*K) for v in src)
reg = img.crop(s0).resize((d0[2]-d0[0], d0[3]-d0[1]))
ring = img.crop((d0[0]-24, d0[1]-24, d0[2]+24, d0[1]-4)).resize((1, 1)).getpixel((0, 0))
rm = reg.resize((1, 1)).getpixel((0, 0))
gain = (sum(ring)/3.0) / max(1.0, sum(rm)/3.0)
gain = max(0.85, min(1.15, gain)) * 0.96
reg = reg.point(lambda p: int(min(255, p*gain)))
m2 = Image.new('L', reg.size, 0)
ImageDraw.Draw(m2).rectangle([14, 14, reg.size[0]-14, reg.size[1]-14], fill=255)
m2 = m2.filter(ImageFilter.GaussianBlur(16))
img.paste(reg, (d0[0], d0[1]), m2)

# ---------- 2) OVERLAY TUBI ----------
ov = Image.new('RGBA', (W*SS, H*SS), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)

C_EDGE = (10, 10, 12, 255)
C_BODY = (38, 38, 44, 255)
C_HI   = (110, 110, 122, 160)
C_FIT  = (24, 24, 28, 255)
C_FITH = (84, 84, 94, 140)

def T(p):  # 1200-space -> overlay space
    return (p[0]*K*SS, p[1]*K*SS)

def tube(a, b, w):
    A, B = T(a), T(b)
    wpx = w*K*SS
    od.line([A, B], fill=C_EDGE, width=int(wpx))
    od.line([A, B], fill=C_BODY, width=max(1, int(wpx*0.68)))
    # highlight spostato verso la luce (alto-sinistra)
    off = wpx*0.16
    od.line([(A[0]-off, A[1]-off), (B[0]-off, B[1]-off)],
            fill=C_HI, width=max(1, int(wpx*0.22)))

def collar(p, w, along=None):
    """manicotto raccordo: segmento corto più grosso"""
    if along is None:
        a = (p[0], p[1]-w*0.9); b = (p[0], p[1]+w*0.9)
    else:
        dx, dy = along
        n = (dx*dx+dy*dy) ** 0.5 or 1
        dx, dy = dx/n, dy/n
        a = (p[0]-dx*w*0.9, p[1]-dy*w*0.9)
        b = (p[0]+dx*w*0.9, p[1]+dy*w*0.9)
    A, B = T(a), T(b)
    wpx = w*1.55*K*SS
    od.line([A, B], fill=C_EDGE, width=int(wpx))
    od.line([A, B], fill=C_FIT, width=max(1, int(wpx*0.7)))
    off = wpx*0.14
    od.line([(A[0]-off, A[1]-off), (B[0]-off, B[1]-off)],
            fill=C_FITH, width=max(1, int(wpx*0.2)))

def flange(p, w):
    P = T(p)
    rx, ry = w*1.9*K*SS, w*0.75*K*SS
    od.ellipse([P[0]-rx*1.25, P[1]-ry*1.15, P[0]+rx*1.25, P[1]+ry*1.35],
               fill=(0, 0, 0, 90))  # ombra di contatto
    od.ellipse([P[0]-rx, P[1]-ry, P[0]+rx, P[1]+ry], fill=C_FIT, outline=C_EDGE,
               width=max(1, int(0.5*K*SS)))

# ---------- 2a) STRUTTURA C SUL BANCONE ----------
# fronte 220: base sul bordo (403,512)->(893,526); h = altezza bancone locale
FL, FR = (403, 512), (893, 526)
HL, HR = 336, 304                     # h bancone in px ai due angoli
TL, TR = (FL[0], FL[1]-HL), (FR[0], FR[1]-HR)
wL, wR = 7.6, 6.9                     # Ø tubo in px ai due lati

# braccio DX (180 indietro, molto scorciato) con 3 verticali
arm_end_b = (957, 507)
arm_end_t = (957, 224)
tube(TR, arm_end_t, wR*0.92)          # corrente sommità braccio DX
arm_fracs = [0.34, 0.62, 0.84]        # 44/88/132 su 180 con compressione prospettica
for f in arm_fracs:
    b = lerp(FR, arm_end_b, f)
    t = lerp(TR, arm_end_t, f)
    tube(b, t, wR*0.9)
    collar(t, wR*0.72, along=(arm_end_t[0]-TR[0], arm_end_t[1]-TR[1]))
    flange(b, wR*0.8)
collar(arm_end_t, wR*0.8, along=(0, 1))  # gomito estremità
flange(arm_end_b, wR*0.8)
tube(arm_end_b, arm_end_t, wR*0.88)

# braccio SX (110 indietro, quasi di taglio) con 1 verticale a metà
axl_b = (447, 501)
axl_t = (447, 173)
tube(TL, axl_t, wL*0.94)
mb, mt = lerp(FL, axl_b, 0.55), lerp(TL, axl_t, 0.55)
tube(mb, mt, wL*0.92)
collar(mt, wL*0.72, along=(axl_t[0]-TL[0], axl_t[1]-TL[1]))
flange(mb, wL*0.82)
collar(axl_t, wL*0.8, along=(0, 1))
flange(axl_b, wL*0.82)
tube(axl_b, axl_t, wL*0.9)

# fronte: 7 verticali (2 angolari + 5 intermedi) e corrente di sommità
for i in range(7):
    t = i/6.0
    b = lerp(FL, FR, t)
    tp = lerp(TL, TR, t)
    w = wL + (wR-wL)*t
    tube(b, tp, w)
    flange(b, w*0.85)
    if 0 < i < 6:
        collar(tp, w*0.75, along=(FR[0]-FL[0], FR[1]-FL[1]))
tube(TL, TR, (wL+wR)/2)               # corrente sommità fronte (sopra i T)
collar(TL, wL*0.8); collar(TR, wR*0.8)  # angoli JM128

# ---------- 2b) GRATA NEL CUBO ----------
# faccia frontale del cubo: quad (62,858)-(455,903)-(450,1075)-(55,1090) con cornice
gq = [(62, 858), (455, 903), (450, 1075), (55, 1090)]
def quad_pt(u, v):
    top = lerp(gq[0], gq[1], u)
    bot = lerp(gq[3], gq[2], u)
    return lerp(top, bot, v)
ins = 0.09
g00, g10 = quad_pt(ins, ins+0.03), quad_pt(1-ins, ins+0.03)
g01, g11 = quad_pt(ins, 1-ins), quad_pt(1-ins, 1-ins)
od.polygon([T(g00), T(g10), T(g11), T(g01)], fill=(8, 8, 10, 235))
GL = (42, 42, 48, 255)
for i in range(1, 8):
    u = ins + (1-2*ins)*i/8.0
    od.line([T(quad_pt(u, ins+0.03)), T(quad_pt(u, 1-ins))], fill=GL,
            width=max(1, int(0.55*K*SS)))
for j in range(1, 6):
    v = ins+0.03 + (1-2*ins-0.03)*j/6.0
    od.line([T(quad_pt(ins, v)), T(quad_pt(1-ins, v))], fill=GL,
            width=max(1, int(0.55*K*SS)))

# ---------- 2c) GABBIA SUL CUBO ----------
# quad piano del cubo (senso orario): BL(back-left) BR FR FL(front-left)
q = {'BL': (170, 737), 'BR': (492, 760), 'FR': (455, 903), 'FL': (62, 858)}
def cube_pt(u, v):
    """u: sinistra->destra, v: dietro->davanti sul piano del cubo"""
    back = lerp(q['BL'], q['BR'], u)
    front = lerp(q['FL'], q['FR'], u)
    return lerp(back, front, v)
i5 = 5.0/90.0
base = {
    'BL': cube_pt(i5, i5), 'BR': cube_pt(1-i5, i5),
    'FR': cube_pt(1-i5, 1-i5), 'FL': cube_pt(i5, 1-i5),
}
hpx = {'FL': 700, 'FR': 555, 'BL': 630, 'BR': 500}   # 230cm in px per angolo
wpost = {'FL': 10.7, 'FR': 8.2, 'BL': 8.8, 'BR': 6.7}
top = {k: (base[k][0], base[k][1]-hpx[k]) for k in base}
lv = {k: [(base[k][0], base[k][1]-hpx[k]/3.0),
          (base[k][0], base[k][1]-hpx[k]*2/3.0)] for k in base}

def wmid(a, b): return (wpost[a]+wpost[b])/2

# ordine pittore: dietro -> davanti
flange(base['BL'], wpost['BL']); tube(base['BL'], top['BL'], wpost['BL'])
# correnti lato SINISTRO (FL-BL) e lato DIETRO (BL-BR)
for i in (0, 1):
    tube(lv['BL'][i], lv['BR'][i], wmid('BL', 'BR')*0.95)
    tube(lv['FL'][i], lv['BL'][i], wmid('FL', 'BL')*0.95)
# telaio superiore lati dietro e sinistro
tube(top['BL'], top['BR'], wmid('BL', 'BR'))
tube(top['FL'], top['BL'], wmid('FL', 'BL'))
collar(top['BL'], wpost['BL']*0.8)
for i in (0, 1):
    collar(lv['BL'][i], wpost['BL']*0.75)

flange(base['BR'], wpost['BR']); tube(base['BR'], top['BR'], wpost['BR'])
collar(top['BR'], wpost['BR']*0.8)
for i in (0, 1):
    tube(lv['FR'][i], lv['BR'][i], wmid('FR', 'BR')*0.95)   # lato DESTRO
    collar(lv['BR'][i], wpost['BR']*0.75)
tube(top['FR'], top['BR'], wmid('FR', 'BR'))

flange(base['FL'], wpost['FL']); tube(base['FL'], top['FL'], wpost['FL'])
collar(top['FL'], wpost['FL']*0.8)
for i in (0, 1):
    collar(lv['FL'][i], wpost['FL']*0.75)

flange(base['FR'], wpost['FR']); tube(base['FR'], top['FR'], wpost['FR'])
collar(top['FR'], wpost['FR']*0.8)
for i in (0, 1):
    collar(lv['FR'][i], wpost['FR']*0.75)
# fronte APERTO: solo corrente di sommità
tube(top['FL'], top['FR'], wmid('FL', 'FR'))

# ---------- 3) COMPOSIZIONE ----------
ov = ov.resize((W, H), Image.LANCZOS)
ov = ov.filter(ImageFilter.GaussianBlur(1.1))
img = img.convert('RGBA')
img.alpha_composite(ov)
img = img.convert('RGB')
img.save(OUT, quality=95)
print('salvato', OUT, img.size)
