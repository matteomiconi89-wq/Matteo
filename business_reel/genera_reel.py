# -*- coding: utf-8 -*-
# Genera REEL_01_armadio_2400.mp4 — 1080x1920, 30 fps, 28 s
# Uso:  py genera_reel.py            -> video completo
#       py genera_reel.py anteprima  -> salva solo i fotogrammi chiave in PNG

import math, sys, os
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 28.0
QUI = os.path.dirname(os.path.abspath(__file__))
FONTS = r"C:\Windows\Fonts"

def font(nome, px):
    return ImageFont.truetype(os.path.join(FONTS, nome), px)

F_CAP   = font("segoeuib.ttf", 52)
F_CAP2  = font("segoeuib.ttf", 46)
F_BAR   = font("segoeui.ttf", 40)
F_CELLA = font("segoeui.ttf", 52)
F_CELLA_B = font("segoeuib.ttf", 52)
F_BTN   = font("segoeuib.ttf", 46)
F_CMD   = font("consola.ttf", 34)
F_BIG   = font("segoeuib.ttf", 76)
F_PILL  = font("segoeuib.ttf", 50)
F_HANDLE= font("segoeui.ttf", 42)

def clamp(v, a, b): return max(a, min(b, v))
def lerp(a, b, u): return a + (b - a) * clamp(u, 0, 1)

def caption(img, righe, y, fnt=None):
    fnt = fnt or F_CAP
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    lh = fnt.size + 44
    for i, r in enumerate(righe):
        bb = d.textbbox((0, 0), r, font=fnt)
        tw = bb[2] - bb[0]
        x0 = (W - tw) / 2
        yy = y + i * lh
        d.rounded_rectangle([x0 - 24, yy - 14, x0 + tw + 24, yy + fnt.size + 18],
                            radius=18, fill=(0, 0, 0, 168))
        d.text((x0, yy), r, font=fnt, fill=(255, 255, 255, 255))
    img.alpha_composite(ov)

# ---------- SCENE 1-2 : EXCEL ----------
def scena_excel(t):
    img = Image.new("RGBA", (W, H), (243, 242, 239, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 150], fill=(15, 110, 86))
    d.text((40, 50), "mobile.xlsx — Excel", font=F_BAR, fill=(255, 255, 255))
    d.rectangle([0, 150, W, 220], fill=(226, 226, 224))
    d.text((290, 165), "B", font=F_CELLA, fill=(110, 110, 110))
    d.text((790, 165), "C", font=F_CELLA, fill=(110, 110, 110))
    righe = [("2", "Larghezza"), ("3", "Altezza"), ("4", "Profondità"), ("5", "Ante")]
    rh, y0, xnum, xb, xc, xfine = 130, 300, 0, 110, 620, 1040
    if t < 3.2: val_l = ""
    else:
        n = int(clamp((t - 3.2) / 0.55 * 4, 0, 4))
        val_l = "2400"[:n]
    valori = [val_l,
              "2600" if t >= 4.3 else "",
              "600"  if t >= 4.7 else "",
              "6"    if t >= 5.0 else ""]
    for i, (num, lab) in enumerate(righe):
        yy = y0 + i * rh
        d.rectangle([xnum, yy, xb, yy + rh], fill=(226, 226, 224), outline=(200, 200, 198))
        d.text((35, yy + 35), num, font=F_CELLA, fill=(110, 110, 110))
        d.rectangle([xb, yy, xc, yy + rh], fill=(255, 255, 255), outline=(205, 205, 203))
        d.text((xb + 30, yy + 35), lab, font=F_CELLA, fill=(40, 40, 40))
        attiva = (i == 0 and t < 4.3) or (i == 1 and 4.3 <= t < 4.7) or \
                 (i == 2 and 4.7 <= t < 5.0) or (i == 3 and t >= 5.0)
        d.rectangle([xc, yy, xfine, yy + rh],
                    fill=(225, 245, 238) if attiva else (255, 255, 255),
                    outline=(29, 158, 117) if attiva else (205, 205, 203),
                    width=5 if attiva else 1)
        d.text((xc + 30, yy + 35), valori[i], font=F_CELLA_B, fill=(20, 20, 20))
        if i == 0 and t < 3.75 and int(t * 2) % 2 == 0:
            bb = d.textbbox((0, 0), valori[0], font=F_CELLA_B)
            cx = xc + 34 + (bb[2] - bb[0])
            d.line([cx, yy + 25, cx, yy + rh - 25], fill=(30, 30, 30), width=4)
    if t >= 5.2:
        prem = 5.55 <= t < 5.85
        col = (12, 88, 68) if prem else (29, 158, 117)
        d.rounded_rectangle([330, 920, 750, 1030], radius=22, fill=col)
        bb = d.textbbox((0, 0), "RIGENERA 3D", font=F_BTN)
        d.text(((1080 - bb[2]) / 2, 945), "RIGENERA 3D", font=F_BTN, fill=(255, 255, 255))
    if t < 3:
        caption(img, ['Il cliente: "la parete è', '2 metri e 40. Ci stai', 'al millimetro?"'], 1380)
    else:
        caption(img, ["Scrivo le SUE misure.", "Tutto qui."], 1430)
    return img

# ---------- SCENE 3-4 : AUTOCAD 3D ----------
CX, CY, CZ = 1200, 1300, 300
FOC, SC, YB = 4600, 0.43, 935

def proietta(p, ang):
    a = math.radians(ang)
    x, y, z = p[0] - CX, p[1] - CY, p[2] - CZ
    xr = x * math.cos(a) + z * math.sin(a)
    zr = -x * math.sin(a) + z * math.cos(a)
    s = FOC / (FOC + 1500 - zr)
    return (540 + xr * s * SC, YB - y * s * SC)

def box_3d(d, b, ang, col, wdt=3):
    x1, x2, y1, y2, z1, z2 = b
    v = [(x1,y1,z1),(x2,y1,z1),(x2,y2,z1),(x1,y2,z1),
         (x1,y1,z2),(x2,y1,z2),(x2,y2,z2),(x1,y2,z2)]
    p = [proietta(q, ang) for q in v]
    arch = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    for a_, b_ in arch:
        d.line([p[a_], p[b_]], fill=col, width=wdt)

CIANO, CIANO2 = (143, 214, 247), (96, 158, 186)
PANNELLI = [
    ((0,18,0,2600,0,600),        6.4, CIANO),
    ((2382,2400,0,2600,0,600),   6.7, CIANO),
    ((18,2382,60,78,0,600),      7.0, CIANO),
    ((18,2382,2582,2600,0,600),  7.3, CIANO),
    ((18,2382,78,2582,0,14),     7.6, CIANO2),
    ((791,809,78,2582,0,582),    7.9, CIANO),
    ((1591,1609,78,2582,0,582),  8.2, CIANO),
    ((18,791,1894,1912,40,582),  8.5, CIANO),
    ((809,1591,1894,1912,40,582),8.7, CIANO),
    ((1609,2382,1894,1912,40,582),8.9, CIANO),
    ((829,1571,78,378,100,582),  9.2, CIANO),
    ((829,1571,388,688,100,582), 9.45, CIANO),
]
for i in range(6):
    x0 = i * 400
    PANNELLI.append(((x0 + 3, x0 + 397, 0, 2600, 600, 618), 9.8 + i * 0.28, CIANO2))

def scena_autocad(t):
    img = Image.new("RGBA", (W, H), (11, 15, 20, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 110], fill=(28, 33, 40))
    d.text((40, 32), "AutoCAD — armadio_2400.dwg", font=F_BAR, fill=(170, 180, 190))
    for gx in range(0, W, 108):
        d.line([gx, 110, gx, 1700], fill=(20, 26, 33), width=1)
    for gy in range(110, 1700, 108):
        d.line([0, gy, W, gy], fill=(20, 26, 33), width=1)
    if t < 12:
        ang = 22 + (t - 6) * 0.7
        cmd = "Comando: _rigenera  modello 3D..."
    else:
        ang = 26 + 24 * math.sin(math.pi * (t - 12) / 4)
        cmd = "Comando: _orbit"
    for b, ta, col in PANNELLI:
        if t >= ta:
            al = clamp((t - ta) / 0.25, 0, 1)
            c = tuple(int(ch * al) for ch in col)
            box_3d(d, b, ang, c)
    d.rectangle([0, 1700, W, 1775], fill=(24, 29, 36))
    d.text((40, 1716), cmd, font=F_CMD, fill=(120, 200, 160))
    if t < 12:
        caption(img, ["…e il suo armadio nasce", "in 3D. Da solo."], 1430)
    else:
        caption(img, ["6 ante. Ogni foro e ogni", "cerniera: già calcolati."], 1430)
    return img

# ---------- SCENA 5 : MOVENTO SLOW-MO ----------
def scena_movento(t):
    img = Image.new("RGBA", (W, H), (224, 219, 211, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1350, W, H], fill=(196, 188, 176))
    fianco = (122, 82, 45); bordo = (92, 60, 30)
    d.rectangle([0, 300, 70, 1350], fill=fianco, outline=bordo, width=3)
    d.rectangle([0, 1280, 720, 1350], fill=fianco, outline=bordo, width=3)
    d.rectangle([0, 300, 720, 370], fill=fianco, outline=bordo, width=3)
    u = clamp((t - 16) / 3.6, 0, 1)
    if u < 0.4:
        apertura = 330 - 250 * (u / 0.4)
    else:
        apertura = 80 * (1 - (u - 0.4) / 0.6) ** 2
    x0 = 100 + apertura
    LC = 560
    d.rectangle([90, 1080, 700, 1100], fill=(120, 124, 130))
    d.rectangle([x0, 1075, x0 + LC, 1095], fill=(70, 74, 80))
    d.rectangle([x0, 880, x0 + LC, 1075], fill=(170, 173, 178), outline=(110, 113, 118), width=3)
    d.rectangle([x0 + LC, 820, x0 + LC + 40, 1090], fill=(214, 178, 128), outline=bordo, width=3)
    if u < 0.95:
        for k in range(3):
            xa = x0 + LC + 70 + k * 26
            d.line([xa, 930, xa + 14, 980], fill=(120, 120, 120), width=5)
    d.text((70, 200), "rallentatore 0,5×", font=F_CMD, fill=(110, 105, 95))
    caption(img, ["Cassetti Blum: si chiudono", "da soli. Per i prossimi 20 anni."], 1480)
    return img

# ---------- SCENA 6 : ARMADIO MONTATO ----------
_stanza = None
def stanza_base():
    global _stanza
    if _stanza is not None: return _stanza
    Z = 1.10
    BW, BH = int(W * Z), int(H * Z)
    img = Image.new("RGBA", (BW, BH), (231, 221, 203, 255))
    d = ImageDraw.Draw(img)
    yfloor = int(BH * 0.78)
    d.rectangle([0, yfloor, BW, BH], fill=(193, 152, 106))
    for k in range(-4, 14):
        d.line([k * 150, yfloor, k * 150 + 260, BH], fill=(168, 128, 84), width=3)
    d.rectangle([0, yfloor - 26, BW, yfloor], fill=(243, 240, 234))
    aw, ah = int(BW * 0.78), int(BH * 0.62)
    x0, y0 = (BW - aw) // 2, yfloor - ah
    d.rectangle([x0 - 16, y0 - 16, x0 + aw + 16, yfloor], fill=(118, 80, 42))
    g = aw / 6
    for i in range(6):
        xa = x0 + int(i * g)
        d.rectangle([xa + 5, y0, xa + int(g) - 5, yfloor - 8], fill=(214, 175, 121), outline=(150, 110, 64), width=2)
        ym = y0 + int(ah * 0.52)
        if i % 2 == 0:
            d.ellipse([xa + int(g) - 28, ym, xa + int(g) - 10, ym + 18], fill=(70, 50, 30))
        else:
            d.ellipse([xa + 10, ym, xa + 28, ym + 18], fill=(70, 50, 30))
    _stanza = img
    return img

def scena_montato(t):
    base = stanza_base()
    z = 1.0 + 0.09 * clamp((t - 20) / 5, 0, 1)
    cw, ch = int(W / z * 1.10), int(H / z * 1.10)
    cx, cy = base.width // 2, base.height // 2
    box = (cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2)
    img = base.crop(box).resize((W, H), Image.LANCZOS)
    caption(img, ["Montato. Al millimetro."], 1480)
    return img

# ---------- SCENA 7 : INVITO ----------
def scena_cta(t):
    img = Image.new("RGBA", (W, H), (10, 10, 12, 255))
    d = ImageDraw.Draw(img)
    al = int(255 * clamp((t - 25) / 0.5, 0, 1))
    for i, r in enumerate(["Vuoi vedere il TUO", "mobile prima di", "comprarlo?"]):
        bb = d.textbbox((0, 0), r, font=F_BIG)
        d.text(((W - bb[2]) / 2, 640 + i * 105), r, font=F_BIG, fill=(255, 255, 255, al))
    if t >= 25.6:
        al2 = int(255 * clamp((t - 25.6) / 0.4, 0, 1))
        bb = d.textbbox((0, 0), "Scrivimi in DM", font=F_PILL)
        pw = bb[2] + 90
        d.rounded_rectangle([(W - pw) / 2, 1080, (W + pw) / 2, 1200], radius=60, fill=(255, 255, 255, al2))
        d.text(((W - bb[2]) / 2, 1110), "Scrivimi in DM", font=F_PILL, fill=(15, 15, 15, al2))
        bb = d.textbbox((0, 0), "@tuonome.falegname", font=F_HANDLE)
        d.text(((W - bb[2]) / 2, 1280), "@tuonome.falegname", font=F_HANDLE, fill=(150, 150, 155, al2))
    return img

def fotogramma(t):
    if t < 6:    return scena_excel(t)
    if t < 16:   return scena_autocad(t)
    if t < 20:   return scena_movento(t)
    if t < 25:   return scena_montato(t)
    return scena_cta(t)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "anteprima":
        for t in [1.5, 4.6, 9.5, 14.0, 18.5, 22.5, 27.0]:
            fotogramma(t).convert("RGB").save(os.path.join(QUI, f"anteprima_{t:.1f}s.png"))
        print("anteprime salvate")
    else:
        import numpy as np, imageio
        out = os.path.join(QUI, "REEL_01_armadio_2400.mp4")
        wr = imageio.get_writer(out, fps=FPS, codec="libx264", quality=8,
                                pixelformat="yuv420p", macro_block_size=1)
        n = int(DUR * FPS)
        for i in range(n):
            wr.append_data(np.array(fotogramma(i / FPS).convert("RGB")))
            if i % 120 == 0:
                print(f"{i}/{n}")
        wr.close()
        print("FATTO:", out)
