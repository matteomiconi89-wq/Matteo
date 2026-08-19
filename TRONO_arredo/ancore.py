# -*- coding: utf-8 -*-
"""Ancore geometriche per il brief Manus - arredo piano primo TRONO.
Solo dati presenti nel PDF 'ARREDO - 4 opzioni' (rev. 00:15): quote stanze e sezioni ponte/soppalco.
Nessuna posizione di mobile e' inventata: le piante sono scatole quotate vuote."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 1000
BG, INK, DIM, FILL = (255, 255, 255), (25, 25, 25), (120, 120, 120), (235, 235, 232)
ACC = (190, 60, 40)

def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            pass
    return ImageFont.load_default()

F, FB, FS = font(30), font(40), font(24)

def txt(d, xy, s, f=F, fill=INK, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)

def dimline(d, x1, y1, x2, y2, label, off=0, vert=False):
    d.line([(x1, y1), (x2, y2)], fill=DIM, width=2)
    t = 9
    if vert:
        d.line([(x1 - t, y1), (x1 + t, y1)], fill=DIM, width=2)
        d.line([(x2 - t, y2), (x2 + t, y2)], fill=DIM, width=2)
        txt(d, (x1 + off, (y1 + y2) // 2), label, FS, DIM)
    else:
        d.line([(x1, y1 - t), (x1, y1 + t)], fill=DIM, width=2)
        d.line([(x2, y2 - t), (x2, y2 + t)], fill=DIM, width=2)
        txt(d, ((x1 + x2) // 2, y1 + off), label, FS, DIM)

# ---------- PIANTE STANZE (scatole quotate, vuote) ----------
STANZE = [
    ("camera",        "CAMERA MATRIMONIALE",  3.52, 4.00),
    ("cabina",        "CABINA ARMADIO",       3.52, 1.71),
    ("cameretta1",    "CAMERETTA 1",          4.12, 2.52),
    ("cameretta2",    "CAMERETTA 2",          2.18, 2.97),
    ("zona_giorno",   "SOGGIORNO + CUCINA",   6.50, 4.62),  # 30 mq, ambiente unico
]

for slug, nome, L, P in STANZE:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    m = 210
    sc = min((W - 2 * m) / L, (H - 2 * m) / P)
    w, h = L * sc, P * sc
    x0, y0 = (W - w) / 2, (H - h) / 2 + 20
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=FILL, outline=INK, width=6)
    txt(d, (W / 2, 58), nome, FB)
    txt(d, (W / 2, 104), "pianta quotata - misure nette in metri - altezza utile 2,70",
        FS, DIM)
    dimline(d, x0, y0 + h + 60, x0 + w, y0 + h + 60, "%.2f m" % L, off=32)
    dimline(d, x0 - 60, y0, x0 - 60, y0 + h, "%.2f m" % P, off=-64, vert=True)
    txt(d, (W / 2, y0 + h / 2), "%.2f x %.2f m" % (L, P), F, (150, 150, 150))
    if slug == "zona_giorno":
        txt(d, (W / 2, y0 + h / 2 + 46), "ambiente unico, 30 mq", FS, (150, 150, 150))
    txt(d, (W / 2, H - 40),
        "SCATOLA VUOTA: proporzioni e dimensioni della stanza. La disposizione dei mobili e' nel testo del brief.",
        FS, ACC)
    img.save("pianta_%s.png" % slug)
    print("pianta_%s.png" % slug)

# ---------- SEZIONI ----------
def sezione(nome, fname, sub, disegna):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    txt(d, (W / 2, 58), nome, FB)
    txt(d, (W / 2, 104), sub, FS, DIM)
    sc = 2.4                      # px per cm
    y_pav = 860.0
    def Y(cm): return y_pav - cm * sc
    x0 = 420.0
    d.line([(180, y_pav), (1420, y_pav)], fill=INK, width=8)          # pavimento
    d.line([(180, Y(270)), (1420, Y(270))], fill=INK, width=5)        # soffitto
    txt(d, (1300, Y(270) - 26), "soffitto  h 270", FS, DIM)
    disegna(d, Y, x0, sc)
    dimline(d, 1450, Y(270), 1450, y_pav, "270", off=-58, vert=True)
    txt(d, (W / 2, H - 40), "quote in centimetri dal pavimento finito", FS, ACC)
    img.save(fname)
    print(fname)

def ponte(d, Y, x0, sc):
    Lbed = 200 * sc
    # letto a terra: materasso top 45
    d.rectangle([x0, Y(45), x0 + Lbed, y0_ := Y(0)], fill=FILL, outline=INK, width=5)
    txt(d, (x0 + Lbed / 2, Y(22)), "letto 90 x 200  +  cassettoni", FS)
    # ponte: 195..250
    d.rectangle([x0, Y(250), x0 + Lbed, Y(195)], fill=(222, 222, 218), outline=INK, width=5)
    txt(d, (x0 + Lbed / 2, Y(222)), "PONTE  200 x 55h", FS)
    # colonna a destra
    d.rectangle([x0 + Lbed, Y(250), x0 + Lbed + 60 * sc, Y(0)], fill=(222, 222, 218),
                outline=INK, width=5)
    txt(d, (x0 + Lbed + 30 * sc, Y(125)), "colonna", FS)
    dimline(d, x0 - 40, Y(195), x0 - 40, Y(45), "150 liberi\nsopra il letto", off=-96, vert=True)
    dimline(d, x0 + Lbed + 90 * sc, Y(250), x0 + Lbed + 90 * sc, Y(195), "55", off=52, vert=True)
    txt(d, (x0 + Lbed / 2, Y(262)), "nessuna scala: il letto sta a terra", FS, ACC)

def soppalco(d, Y, x0, sc):
    Lbed = 200 * sc
    # armadio sotto: 0..135
    d.rectangle([x0, Y(135), x0 + Lbed, Y(0)], fill=(222, 222, 218), outline=INK, width=5)
    txt(d, (x0 + Lbed / 2, Y(68)), "ARMADIO  200 x 135h", FS)
    # piano soppalco 140 + materasso fino a 165
    d.rectangle([x0, Y(140), x0 + Lbed, Y(135)], fill=INK, outline=INK, width=3)
    d.rectangle([x0, Y(165), x0 + Lbed, Y(140)], fill=FILL, outline=INK, width=5)
    txt(d, (x0 + Lbed / 2, Y(152)), "letto 90 x 200", FS)
    # scala
    xs = x0 + Lbed + 30 * sc
    for i in range(5):
        yy = Y(30 + i * 27)
        d.line([(xs, yy), (xs + 46 * sc, yy)], fill=INK, width=6)
    d.line([(xs, Y(0)), (xs, Y(140))], fill=INK, width=5)
    d.line([(xs + 46 * sc, Y(0)), (xs + 46 * sc, Y(140))], fill=INK, width=5)
    txt(d, (xs + 23 * sc, Y(155)), "scala", FS)
    dimline(d, x0 - 40, Y(270), x0 - 40, Y(165), "105 sopra\nil materasso", off=-96, vert=True)
    dimline(d, x0 + Lbed + 128 * sc, Y(140), x0 + Lbed + 128 * sc, Y(0), "140", off=52, vert=True)
    txt(d, (x0 + Lbed / 2, Y(182)), "sotto ci passa un armadio, NON una persona in piedi", FS, ACC)

sezione("SEZIONE - LETTO A PONTE  (opzioni A, C, D)", "sezione_ponte.png",
        "letto a terra, armadio sospeso sopra - altezza utile 2,70", ponte)
sezione("SEZIONE - SOPPALCO h 140  (opzione B)", "sezione_soppalco.png",
        "armadio sotto per tutta la lunghezza, serve la scaletta - altezza utile 2,70", soppalco)
