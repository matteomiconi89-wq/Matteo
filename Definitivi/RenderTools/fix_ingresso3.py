# -*- coding: utf-8 -*-
"""Terza passata vista APERTA, tutta dal v4 originale:
1) rimozione anta inventata v2: clone con correzione luminanza PER RIGA + feather sui 4 bordi
2) toppa sulla barretta-maniglia duplicata oltre il bordo dell'anta scarpiera
3) warp bande v3: anta dx SPECCHIATA nella sua banda (cerniere al giunto), H/L 1,030, laterali uguali"""
import sys, io
if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image, ImageDraw

DIR = r"C:\Users\User\Dropbox\STEFANO\Matteo\RENDER_MANUS\26-A011_mobile_ingresso"

def warp2(im, bande):
    """bande: (x_in0, x_in1, larghezza_out[, flip]). flip=True specchia la banda."""
    W, H = im.size
    mesh = []
    xo = 0.0
    for b in bande:
        xi0, xi1, lo = b[0], b[1], b[2]
        flip = len(b) > 3 and b[3]
        xo0, xo1 = xo, xo + lo
        if flip:
            quad = (xi1, 0.0, xi1, float(H), xi0, float(H), xi0, 0.0)
        else:
            quad = (xi0, 0.0, xi0, float(H), xi1, float(H), xi1, 0.0)
        mesh.append(((int(round(xo0)), 0, int(round(xo1)), H), quad))
        xo = xo1
    tot = int(round(xo))
    out = im.transform((tot, H), Image.MESH, mesh, resample=Image.BICUBIC)
    if tot != W:
        out = out.resize((W, H), Image.LANCZOS)
    return out

def rimuovi_anta_v2(im):
    """Clona muro+pavimento sull'anta inventata [1727..1795]x[285..1335], sorgente +88px,
    correzione di luminanza per riga, feather su tutti i bordi."""
    im = im.copy()
    g = im.convert("L")
    px = g.load()
    x0, x1, y0, y1 = 1727, 1795, 285, 1335
    off = 88
    larg, alto = x1 - x0, y1 - y0
    src = im.crop((x0 + off, y0, x1 + off, y1))
    # rapporto di luminanza per riga: colonne pulite adiacenti (dst 1797-1812 vs src 1885-1900)
    corr = []
    for y in range(y0, y1):
        sd = sum(px[x, y] for x in range(1797, 1812))
        ss = sum(px[x + off, y] for x in range(1797, 1812))
        corr.append(sd / ss if ss else 1.0)
    # smussa la serie (media mobile 31)
    lisc = []
    for i in range(len(corr)):
        a, b = max(0, i - 15), min(len(corr), i + 16)
        lisc.append(sum(corr[a:b]) / (b - a))
    sp = src.load()
    for j in range(alto):
        k = lisc[j]
        for i in range(larg):
            r, gg, bb = sp[i, j][:3]
            sp[i, j] = (min(255, int(r * k)), min(255, int(gg * k)), min(255, int(bb * k)))
    # feather: sx 4, dx 15, alto 15, basso 15
    mask = Image.new("L", (larg, alto), 255)
    dr = ImageDraw.Draw(mask)
    for i in range(15):
        a = int(255 * i / 15)
        if i < 4:
            dr.line([(i, 0), (i, alto)], fill=int(255 * i / 4))
        dr.line([(larg - 1 - i, 0), (larg - 1 - i, alto)], fill=a)
    for j in range(15):
        a = int(255 * j / 15)
        riga = mask.crop((0, j, larg, j + 1)).point(lambda v: min(v, a))
        mask.paste(riga, (0, j))
        riga = mask.crop((0, alto - 1 - j, larg, alto - j)).point(lambda v: min(v, a))
        mask.paste(riga, (0, alto - 1 - j))
    im.paste(src, (x0, y0), mask)
    return im

def fix_maniglia(im):
    """Toglie la barretta duplicata oltre il bordo dell'anta scarpiera (zona 704-718 x 756-812):
    muro dal blocco sopra, poi ripristina il bordo alluminio 716-724 copiandolo da sopra."""
    im = im.copy()
    muro = im.crop((702, 700, 720, 752)).resize((18, 62))
    mask = Image.new("L", (18, 62), 255)
    dr = ImageDraw.Draw(mask)
    for i in range(4):
        dr.line([(i, 0), (i, 62)], fill=int(255 * i / 4))
    for j in range(4):
        riga = mask.crop((0, j, 18, j + 1)).point(lambda v: min(v, int(255 * j / 4)))
        mask.paste(riga, (0, j))
        riga = mask.crop((0, 62 - 1 - j, 18, 62 - j)).point(lambda v: min(v, int(255 * j / 4)))
        mask.paste(riga, (0, 62 - 1 - j))
    im.paste(muro, (702, 754), mask)
    bordo = im.crop((715, 706, 726, 754)).resize((11, 64))
    im.paste(bordo, (715, 752))
    return im

# ---- BANDE v3: carcassa 804 px centrata [878..1682], H/L = 828/804 = 1,030 ----
aperto_bande3 = [
    (0,    710,  773),          # muro sx
    (710,  819,  105),          # anta scarpe aperta
    (819,  1045, 217),          # vano scarpiera -> laterale sx 217
    (1045, 1055, 7),            # bordo montante
    (1055, 1090, 28),           # pannello domotica + lama LED
    (1090, 1127, 15),           # sliver anta sx
    (1127, 1470, 281),          # vano guardaroba (capi x0.82 come gia' approvato)
    (1470, 1523, 38, True),     # anta dx SPECCHIATA: cerniere passano al bordo giunto
    (1523, 1538, 3),            # stile libreria quasi coperto dall'anta
    (1538, 1735, 215),          # libreria coi libri x1.09 -> laterale dx 218
    (1735, 2560, 878),          # muro dx
]

if __name__ == "__main__":
    im = Image.open(DIR + r"\render_INGRESSO_v4_aperto.png").convert("RGB")
    im = rimuovi_anta_v2(im)
    im = fix_maniglia(im)
    im.save(DIR + r"\_v4_aperto_pulito.png")
    out = warp2(im, aperto_bande3)
    out.save(DIR + r"\render_INGRESSO_FINALE_aperto.png")
    print(f"aperto v3: {out.size}")
