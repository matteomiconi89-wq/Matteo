# -*- coding: utf-8 -*-
"""Tavole di riferimento per il brief bagni TRONO - piano primo.

Frame di lettura (lo stesso della pianta verificata):
  P = profondita', 0 alla parete esterna, cresce verso la parete porta
  L = larghezza,  0 alla parete di sinistra guardando dalla porta verso la finestra

Tutte le quote vengono dal rilievo vettoriale Piano Primo(1).pdf, scala 36,00 pt/m.
Le altezze NON sono nel rilievo (e' una pianta): sono scelte di progetto, marcate [P].
"""
from PIL import Image, ImageDraw, ImageFont
import math

FDIR = "/usr/share/fonts/truetype/dejavu/"
def font(sz, bold=False):
    try:
        return ImageFont.truetype(FDIR + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), sz)
    except Exception:
        return ImageFont.load_default()

MURO   = (28, 28, 30)
FILL   = (236, 236, 232)
QUOTA  = (95, 95, 100)
ROSSO  = (188, 62, 44)
BLU    = (30, 92, 160)
VETRO  = (150, 195, 215)
GRIGIO = (140, 140, 145)

class Tav:
    def __init__(self, w, h, k, ox, oy):
        self.img = Image.new("RGB", (w, h), (255, 255, 255))
        self.d = ImageDraw.Draw(self.img)
        self.k, self.ox, self.oy, self.w, self.h = k, ox, oy, w, h
    def X(self, l): return self.ox + l * self.k
    def Y(self, p): return self.oy + p * self.k
    def rect(self, l0, p0, l1, p1, fill=FILL, out=MURO, wd=3):
        self.d.rectangle([self.X(l0), self.Y(p0), self.X(l1), self.Y(p1)], fill=fill, outline=out, width=wd)
    def line(self, l0, p0, l1, p1, col=MURO, wd=3):
        self.d.line([self.X(l0), self.Y(p0), self.X(l1), self.Y(p1)], fill=col, width=wd)
    def txt(self, l, p, s, f, col=MURO, anchor="mm", dx=0, dy=0):
        self.d.text((self.X(l) + dx, self.Y(p) + dy), s, font=f, fill=col, anchor=anchor)
    def pxtxt(self, x, y, s, f, col=MURO, anchor="mm"):
        self.d.text((x, y), s, font=f, fill=col, anchor=anchor)

    def quota_h(self, l0, l1, p, testo, f, sopra=True, col=QUOTA):
        """catena di quota orizzontale alla profondita' p"""
        y = self.Y(p); x0, x1 = self.X(l0), self.X(l1)
        self.d.line([x0, y, x1, y], fill=col, width=2)
        for x in (x0, x1):
            self.d.line([x, y - 9, x, y + 9], fill=col, width=2)
        self.d.text(((x0 + x1) / 2, y - 15 if sopra else y + 15), testo, font=f, fill=col,
                    anchor="ms" if sopra else "mt")
    def quota_v(self, p0, p1, l, testo, f, sinistra=True, col=QUOTA):
        x = self.X(l); y0, y1 = self.Y(p0), self.Y(p1)
        self.d.line([x, y0, x, y1], fill=col, width=2)
        for y in (y0, y1):
            self.d.line([x - 9, y, x + 9, y], fill=col, width=2)
        tx = x - 14 if sinistra else x + 14
        im = Image.new("RGBA", (460, 46), (255, 255, 255, 0))
        ImageDraw.Draw(im).text((230, 23), testo, font=f, fill=col, anchor="mm")
        im = im.rotate(90, expand=True)
        self.img.paste(im, (int(tx - im.width // 2 - (10 if sinistra else -10)),
                            int((y0 + y1) / 2 - im.height // 2)), im)

    def camera(self, l, p, ang, fov, nome, dist=1.5, col=BLU):
        """cono di ripresa: ang in gradi, 0 = verso P decrescente (verso la parete esterna)"""
        cx, cy = self.X(l), self.Y(p)
        a0, a1 = math.radians(ang - fov / 2), math.radians(ang + fov / 2)
        pts = [(cx, cy)]
        for a in (a0, a1):
            pts.append((cx + math.sin(a) * dist * self.k, cy - math.cos(a) * dist * self.k))
        self.d.polygon(pts, fill=(214, 230, 245), outline=col)
        self.d.line([pts[0], pts[1]], fill=col, width=3)
        self.d.line([pts[0], pts[2]], fill=col, width=3)
        ac = math.radians(ang)
        self.d.line([cx, cy, cx + math.sin(ac) * dist * self.k * 0.9,
                     cy - math.cos(ac) * dist * self.k * 0.9], fill=col, width=2)
        self.d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=col)
        self.d.text((cx, cy), nome, font=font(19, True), fill=(255, 255, 255), anchor="mm")

    def save(self, nome):
        self.img.save("/home/user/Matteo/TRONO_arredo/" + nome)
        print(nome, self.img.size)

F_TIT, F_SUB, F_LAB, F_Q, F_MIN = font(40, True), font(22), font(23, True), font(21), font(18)

def murature(t, L, P, sp_est=0.35, sp=0.12, niche=None):
    t.rect(-sp, -sp_est, L + sp, 0.0, fill=(62, 62, 66), out=MURO, wd=2)
    t.rect(-sp, 0.0, 0.0, P, fill=(62, 62, 66), out=MURO, wd=2)
    t.rect(-sp, P, L + sp, P + sp, fill=(62, 62, 66), out=MURO, wd=2)
    if niche is None:
        t.rect(L, 0.0, L + sp, P, fill=(62, 62, 66), out=MURO, wd=2)
    else:
        nl, np_ = niche
        t.rect(nl, 0.0, nl + sp, np_, fill=(62, 62, 66), out=MURO, wd=2)
        t.rect(L, np_, nl + sp, np_ + sp, fill=(62, 62, 66), out=MURO, wd=2)
        t.rect(L, np_ + sp, L + sp, P, fill=(62, 62, 66), out=MURO, wd=2)
        t.rect(nl - 0.0, -sp_est, nl + sp, 0.0, fill=(62, 62, 66), out=MURO, wd=2)

# ============================================================ WC  (cieco)
WC_L, WC_P = 1.356, 2.768
t = Tav(1300, 1680, 300, 470, 340)
t.pxtxt(650, 66, "WC — pianta quotata", F_TIT)
t.pxtxt(650, 110, "1,356 × 2,768 m — LOCALE CIECO, nessuna finestra — quote dal rilievo vettoriale, scala 36,00 pt/m", F_SUB, QUOTA)
t.pxtxt(650, 146, "P = 0 alla parete esterna · P cresce verso la porta · L = 0 alla parete del lavabo", F_MIN, QUOTA)

murature(t, WC_L, WC_P)
t.rect(0, 0, WC_L, WC_P, fill=(252, 252, 250), out=MURO, wd=5)
t.camera(0.68, WC_P - 0.06, 0, 75, "1", dist=1.15)
t.camera(0.22, 0.20, 161.6, 70, "2", dist=1.15)

t.rect(0, 1.517, 0.448, 2.117); t.rect(0.048, 1.591, 0.400, 2.043, fill=(255, 255, 255), wd=2)
t.txt(0.224, 1.74, "LAVABO", F_MIN); t.txt(0.224, 1.89, "0,60 × 0,448", F_MIN, QUOTA)
for p0, nome in [(0.236, "VASO"), (0.928, "BIDET")]:
    t.rect(WC_L - 0.516, p0, WC_L, p0 + 0.368)
    t.rect(WC_L - 0.486, p0 + 0.030, WC_L - 0.030, p0 + 0.338, fill=(255, 255, 255), wd=2)
    t.txt(WC_L - 0.258, p0 + 0.13, nome, F_MIN)
    t.txt(WC_L - 0.258, p0 + 0.27, "0,368 × 0,516", F_MIN, QUOTA)

t.line(0.514, WC_P, 1.314, WC_P, col=(252, 252, 250), wd=10)
t.d.arc([t.X(0.514), t.Y(WC_P - 0.80), t.X(2.114), t.Y(WC_P + 0.80)], 180, 270, fill=GRIGIO, width=3)
t.line(1.314, WC_P, 1.314, WC_P - 0.80, col=ROSSO, wd=6)
t.txt(WC_L / 2, 0.115, "PARETE CIECA", F_LAB, (168, 60, 40))

t.quota_h(0, WC_L, -0.50, "1,356", F_Q)
t.quota_v(0, WC_P, -0.52, "2,768", F_Q)
for p0, p1, tx in [(0, 1.517, "1,517"), (1.517, 2.117, "0,600"), (2.117, WC_P, "0,651")]:
    t.quota_v(p0, p1, -0.94, tx, F_MIN)
for p0, p1, tx in [(0, 0.236, "0,236"), (0.236, 0.604, "0,368"), (0.604, 0.928, "0,324"),
                   (0.928, 1.296, "0,368"), (1.296, WC_P, "1,472")]:
    t.quota_v(p0, p1, WC_L + 0.42, tx, F_MIN, sinistra=False)
t.quota_h(0, 0.514, WC_P + 0.32, "0,514", F_MIN, sopra=False)
t.quota_h(0.514, 1.314, WC_P + 0.32, "luce porta 0,800", F_MIN, sopra=False)
t.quota_h(0.448, WC_L, 2.20, "0,908 libero", F_MIN, sopra=False)
t.txt(1.29, WC_P - 0.50, "porta 0,80", F_MIN, ROSSO, anchor="rm")
t.txt(1.29, WC_P - 0.36, "cardine a L 1,314", F_MIN, ROSSO, anchor="rm")

t.pxtxt(650, 1424, "CAMERA 1 — sulla soglia (L 0,68 · P 2,71), h 1,60, asse dritto verso la parete cieca, FOV 75°", F_Q, BLU)
t.pxtxt(650, 1458, "CAMERA 2 — angolo cieco lato lavabo (L 0,22 · P 0,20), h 1,55, verso l'angolo porta, FOV 70°", F_Q, BLU)
t.pxtxt(650, 1516, "Lavabo e vaso/bidet stanno su pareti OPPOSTE e si guardano: mai sulla stessa parete.", F_Q, (168, 60, 40))
t.pxtxt(650, 1552, "Il locale e' lungo esattamente il doppio della sua larghezza: 2,768 / 1,356 = 2,04.", F_Q, (168, 60, 40))
t.pxtxt(650, 1588, "Parete di fondo (P = 0) libera e cieca: niente sanitari, niente finestra, niente specchio.", F_Q, (168, 60, 40))
t.pxtxt(650, 1638, "Le altezze non sono nel rilievo: vedi la tavola dei prospetti.", F_MIN, QUOTA)
t.save("bagni_pianta_wc.png")

# ============================================================ BAGNO (pianta a L)
BG_L, BG_P, NI_L, NI_P = 1.700, 2.768, 2.688, 1.100
t = Tav(1660, 1810, 300, 500, 450)
t.pxtxt(830, 66, "BAGNO — pianta quotata", F_TIT)
t.pxtxt(830, 110, "corpo 1,700 × 2,768 m + nicchia doccia: PIANTA A L, non rettangolare — rilievo, scala 36,00 pt/m", F_SUB, QUOTA)
t.pxtxt(830, 146, "P = 0 alla parete esterna con la finestra · P cresce verso la porta · L = 0 alla parete dei tre ceramici", F_MIN, QUOTA)

for r in [(-0.12, -0.35, NI_L + 0.12, 0.0), (-0.12, 0.0, 0.0, BG_P), (-0.12, BG_P, BG_L + 0.12, BG_P + 0.12),
          (BG_L, NI_P, BG_L + 0.12, BG_P), (NI_L, 0.0, NI_L + 0.12, NI_P), (BG_L, NI_P, NI_L + 0.12, NI_P + 0.12)]:
    t.rect(*r, fill=(62, 62, 66), out=MURO, wd=2)
t.d.polygon([t.X(0), t.Y(0), t.X(NI_L), t.Y(0), t.X(NI_L), t.Y(NI_P), t.X(BG_L), t.Y(NI_P),
             t.X(BG_L), t.Y(BG_P), t.X(0), t.Y(BG_P)], fill=(252, 252, 250), outline=MURO)
t.d.line([t.X(0), t.Y(0), t.X(NI_L), t.Y(0), t.X(NI_L), t.Y(NI_P), t.X(BG_L), t.Y(NI_P),
          t.X(BG_L), t.Y(BG_P), t.X(0), t.Y(BG_P), t.X(0), t.Y(0)], fill=MURO, width=5)

t.camera(0.85, BG_P - 0.06, 0, 75, "1", dist=1.25)
t.camera(0.30, BG_P - 0.20, 45, 70, "2", dist=1.35)

for p0, nome in [(0.236, "VASO"), (0.928, "BIDET")]:
    t.rect(0, p0, 0.516, p0 + 0.368)
    t.rect(0.030, p0 + 0.030, 0.486, p0 + 0.338, fill=(255, 255, 255), wd=2)
    t.txt(0.258, p0 + 0.13, nome, F_MIN); t.txt(0.258, p0 + 0.27, "0,368 × 0,516", F_MIN, QUOTA)
t.rect(0, 1.600, 0.448, 2.200); t.rect(0.048, 1.674, 0.400, 2.126, fill=(255, 255, 255), wd=2)
t.txt(0.224, 1.82, "LAVABO", F_MIN); t.txt(0.224, 1.97, "0,60 × 0,448", F_MIN, QUOTA)

t.rect(1.988, 0.0, NI_L, NI_P, fill=(226, 234, 238))
t.rect(2.042, 0.047, 2.642, 1.047, fill=(244, 249, 251), wd=3)
t.line(2.042, 1.047, 2.642, 1.047, col=VETRO, wd=8)
t.line(2.042, 0.047, 2.042, 1.047, col=VETRO, wd=8)
t.d.ellipse([t.X(2.312), t.Y(0.517), t.X(2.372), t.Y(0.577)], outline=MURO, width=3)
t.txt(2.342, 0.30, "PIATTO DOCCIA", F_MIN); t.txt(2.342, 0.44, "0,60 × 1,00", F_MIN, QUOTA)
t.txt(2.342, 0.72, "piletta", F_MIN, QUOTA); t.txt(2.342, 0.86, "centrale", F_MIN, QUOTA)

t.line(0.172, 0, 1.333, 0, col=(252, 252, 250), wd=11)
t.line(0.253, -0.04, 1.250, -0.04, col=BLU, wd=7)
t.line(0.172, 0, 1.333, 0, col=BLU, wd=3)
t.txt(1.15, 0.17, "FINESTRA", F_LAB, BLU)
t.txt(1.15, 0.32, "telaio 1,00 · luce muro 1,161", F_MIN, BLU)

t.line(0.617, BG_P, 1.417, BG_P, col=(252, 252, 250), wd=10)
t.d.arc([t.X(0.617), t.Y(BG_P - 0.80), t.X(2.217), t.Y(BG_P + 0.80)], 180, 270, fill=GRIGIO, width=3)
t.line(1.417, BG_P, 1.417, BG_P - 0.80, col=ROSSO, wd=6)
t.txt(1.39, BG_P - 0.50, "porta 0,80", F_MIN, ROSSO, anchor="rm")
t.txt(1.39, BG_P - 0.36, "cardine a L 1,417", F_MIN, ROSSO, anchor="rm")

t.quota_h(0, BG_L, -0.50, "corpo 1,700", F_Q)
t.quota_h(0, NI_L, -0.80, "massimo 2,688", F_Q)
t.quota_v(0, BG_P, -0.52, "2,768", F_Q)
for p0, p1, tx in [(0, 0.236, "0,236"), (0.236, 0.604, "0,368"), (0.604, 0.928, "0,324"),
                   (0.928, 1.296, "0,368"), (1.296, 1.600, "0,304"), (1.600, 2.200, "0,600"), (2.200, BG_P, "0,568")]:
    t.quota_v(p0, p1, -0.94, tx, F_MIN)
t.quota_v(0, NI_P, NI_L + 0.30, "nicchia 1,100", F_MIN, sinistra=False)
t.quota_h(BG_L, NI_L, NI_P + 0.36, "0,988", F_MIN, sopra=False)
t.quota_h(0.516, BG_L, 1.45, "1,184 libero", F_MIN, sopra=False)
t.quota_h(0, 0.617, BG_P + 0.32, "0,617", F_MIN, sopra=False)
t.quota_h(0.617, 1.417, BG_P + 0.32, "luce porta 0,800", F_MIN, sopra=False)

t.pxtxt(830, 1550, "CAMERA 1 — sulla soglia (L 0,85 · P 2,71), h 1,60, asse dritto verso la finestra, FOV 75°", F_Q, BLU)
t.pxtxt(830, 1584, "CAMERA 2 — angolo porta lato ceramici (L 0,30 · P 2,57), h 1,60, diagonale verso la doccia, FOV 70°", F_Q, BLU)
t.pxtxt(830, 1642, "Vaso, bidet e lavabo sono TUTTI E TRE in fila sulla stessa parete (L = 0), in quest'ordine dalla finestra.", F_Q, (168, 60, 40))
t.pxtxt(830, 1678, "La stanza NON e' rettangolare: si allarga da 1,700 a 2,688 solo nei primi 1,100 m dalla finestra.", F_Q, (168, 60, 40))
t.pxtxt(830, 1714, "La doccia sta in quella rientranza, accanto alla finestra: non e' sul lato lungo e non e' in fondo.", F_Q, (168, 60, 40))
t.pxtxt(830, 1766, "Le altezze non sono nel rilievo: vedi la tavola dei prospetti.", F_MIN, QUOTA)
t.save("bagni_pianta_bagno.png")

# ============================================================ PROSPETTI
HU = 2.70   # altezza utile ASSUNTA, non documentata nel rilievo
class Pro:
    def __init__(s, img, d, k, ox, oy):
        s.img, s.d, s.k, s.ox, s.oy = img, d, k, ox, oy   # oy = quota del pavimento
    def X(s, x): return s.ox + x * s.k
    def Y(s, h): return s.oy - h * s.k
    def rect(s, x0, h0, x1, h1, fill=FILL, out=MURO, wd=3):
        s.d.rectangle([s.X(x0), s.Y(h1), s.X(x1), s.Y(h0)], fill=fill, outline=out, width=wd)
    def txt(s, x, h, t, f, col=MURO, anchor="mm"):
        s.d.text((s.X(x), s.Y(h)), t, font=f, fill=col, anchor=anchor)
    def quota_v(s, h0, h1, x, testo, f, col=QUOTA):
        px = s.X(x); y0, y1 = s.Y(h0), s.Y(h1)
        s.d.line([px, y0, px, y1], fill=col, width=2)
        for y in (y0, y1): s.d.line([px - 8, y, px + 8, y], fill=col, width=2)
        im = Image.new("RGBA", (400, 42), (255, 255, 255, 0))
        ImageDraw.Draw(im).text((200, 21), testo, font=f, fill=col, anchor="mm")
        im = im.rotate(90, expand=True)
        s.img.paste(im, (int(px - im.width // 2 - 12), int((y0 + y1) / 2 - im.height // 2)), im)
    def quota_h(s, x0, x1, h, testo, f, col=QUOTA, alt=0):
        y = s.Y(h); a, b = s.X(x0), s.X(x1)
        s.d.line([a, y, b, y], fill=col, width=2)
        for x in (a, b): s.d.line([x, y - 8, x, y + 8], fill=col, width=2)
        s.d.text(((a + b) / 2, y + 14 + alt * 30), testo, font=f, fill=col, anchor="mt")

def parete(p, larg, titolo, sottotitolo, verso):
    p.rect(0, 0, larg, HU, fill=(250, 250, 247), out=MURO, wd=5)
    p.d.rectangle([p.X(0), p.Y(0), p.X(larg), p.Y(0) + 16], fill=(62, 62, 66))
    p.d.text((p.X(larg / 2), p.Y(HU) - 62), titolo, font=font(30, True), fill=MURO, anchor="mm")
    p.d.text((p.X(larg / 2), p.Y(HU) - 28), sottotitolo, font=F_MIN, fill=QUOTA, anchor="mm")
    p.d.text((p.X(larg / 2), p.Y(0) + 148), verso, font=F_LAB, fill=BLU, anchor="mm")

def lavabo_prospetto(p, xc):
    p.rect(xc - 0.30, 0.45, xc + 0.30, 0.85)                       # mobile sospeso
    p.rect(xc - 0.25, 0.85, xc + 0.25, 0.90, fill=(255, 255, 255))  # catino
    p.d.line([p.X(xc), p.Y(0.90), p.X(xc), p.Y(1.05)], fill=MURO, width=5)
    p.rect(xc - 0.30, 1.05, xc + 0.30, 1.95, fill=(226, 236, 242))  # specchio
    p.txt(xc, 1.50, "specchio", F_MIN, QUOTA); p.txt(xc, 1.36, "0,60 × 0,90", F_MIN, QUOTA)
    p.txt(xc, 0.65, "mobile", F_MIN); p.txt(xc, 0.53, "sospeso", F_MIN)
    p.quota_v(0, 0.85, xc - 0.44, "piano 0,85", F_MIN)
    p.quota_v(1.05, 1.95, xc + 0.44, "specchio 1,05 → 1,95", F_MIN)

def ceramico(p, xc, nome, bordo):
    p.rect(xc - 0.184, 0.15, xc + 0.184, bordo)
    p.txt(xc, 0.28, nome, F_MIN)
    p.quota_v(0, bordo, xc - 0.30, "%0.2f" % bordo, F_MIN)
    if nome == "VASO":
        p.rect(xc - 0.11, 1.00, xc + 0.11, 1.14, fill=(240, 240, 236))
        p.txt(xc, 1.24, "placca 1,00", F_MIN, QUOTA)

# ---- WC: tre prospetti
K = 250
img = Image.new("RGB", (1180, 3230), (255, 255, 255)); d = ImageDraw.Draw(img)
d.text((590, 62), "WC — prospetti delle tre pareti", font=F_TIT, fill=MURO, anchor="mm")
d.text((590, 106), "altezza utile 2,70 ASSUNTA — il rilievo e' una pianta e non contiene quote verticali", font=F_SUB, fill=(168, 60, 40), anchor="mm")
d.text((590, 140), "tutte le altezze qui sotto sono scelte di progetto, non misure", font=F_MIN, fill=QUOTA, anchor="mm")

p = Pro(img, d, K, 300, 1030)
parete(p, 2.768, "A · parete del LAVABO (L = 0, verso la cameretta)", "lunga 2,768 — porta solo il lavabo, tutto il resto e' vuoto",
       "da sinistra a destra: P = 2,768 (porta)  →  P = 0 (parete cieca)")
lavabo_prospetto(p, 0.951)
p.quota_h(0, 0.651, -0.22, "0,651", F_MIN); p.quota_h(0.651, 1.251, -0.22, "0,600", F_MIN, alt=1)
p.quota_h(1.251, 2.768, -0.22, "1,517", F_MIN)
p.quota_v(0, HU, 2.92, "2,70 assunta", F_Q)

p = Pro(img, d, K, 300, 2100)
parete(p, 2.768, "B · parete di VASO e BIDET (L = 1,356, verso il bagno)", "lunga 2,768 — i due ceramici sono sospesi, cassetta incassata",
       "da sinistra a destra: P = 0 (parete cieca)  →  P = 2,768 (porta)")
ceramico(p, 0.420, "VASO", 0.42); ceramico(p, 1.112, "BIDET", 0.40)
p.quota_h(0, 0.236, -0.22, "0,236", F_MIN); p.quota_h(0.236, 0.604, -0.22, "0,368", F_MIN, alt=1)
p.quota_h(0.604, 0.928, -0.22, "0,324", F_MIN); p.quota_h(0.928, 1.296, -0.22, "0,368", F_MIN, alt=1)
p.quota_h(1.296, 2.768, -0.22, "1,472 di parete libera", F_MIN)
p.quota_v(0, HU, 2.92, "2,70 assunta", F_Q)

p = Pro(img, d, K, 500, 3060)
parete(p, 1.356, "C · parete della PORTA (lato corto, 1,356)", "porta 0,80 × 2,10, cardine a destra guardandola da dentro",
       "L = 0 a sinistra (lato lavabo)  →  L = 1,356 a destra (lato vaso)")
p.rect(0.514, 0, 1.314, 2.10, fill=(244, 238, 234), out=ROSSO, wd=4)
p.txt(0.914, 1.05, "porta", F_MIN, ROSSO); p.txt(0.914, 0.90, "0,80 × 2,10", F_MIN, ROSSO)
p.quota_h(0, 0.514, -0.22, "0,514", F_MIN); p.quota_h(0.514, 1.314, -0.22, "0,800", F_MIN)
img.save("/home/user/Matteo/TRONO_arredo/bagni_prospetti_wc.png"); print("prospetti wc", img.size)

# ---- BAGNO: due prospetti
img = Image.new("RGB", (1180, 2320), (255, 255, 255)); d = ImageDraw.Draw(img)
d.text((590, 62), "BAGNO — prospetti delle due pareti che portano qualcosa", font=font(34, True), fill=MURO, anchor="mm")
d.text((590, 106), "altezza utile 2,70 ASSUNTA — il rilievo e' una pianta e non contiene quote verticali", font=F_SUB, fill=(168, 60, 40), anchor="mm")

p = Pro(img, d, K, 300, 1030)
parete(p, 2.768, "A · parete dei TRE CERAMICI (L = 0, verso il wc)", "lunga 2,768 — vaso, bidet e lavabo in fila, in quest'ordine dalla finestra",
       "da sinistra a destra: P = 0 (finestra)  →  P = 2,768 (porta)")
ceramico(p, 0.420, "VASO", 0.42); ceramico(p, 1.112, "BIDET", 0.40); lavabo_prospetto(p, 1.900)
p.quota_h(0, 0.236, -0.22, "0,236", F_MIN); p.quota_h(0.236, 0.604, -0.22, "0,368", F_MIN, alt=1)
p.quota_h(0.604, 0.928, -0.22, "0,324", F_MIN); p.quota_h(0.928, 1.296, -0.22, "0,368", F_MIN, alt=1)
p.quota_h(1.296, 1.600, -0.22, "0,304", F_MIN); p.quota_h(1.600, 2.200, -0.22, "0,600", F_MIN, alt=1)
p.quota_h(2.200, 2.768, -0.22, "0,568", F_MIN)
p.quota_v(0, HU, 2.92, "2,70 assunta", F_Q)

p = Pro(img, d, K, 300, 2090)
parete(p, 2.688, "B · parete ESTERNA (P = 0): finestra + nicchia della doccia", "larga 2,688 in tutto: 1,700 di corpo con la finestra, poi 0,988 di nicchia",
       "da sinistra a destra: L = 0 (parete ceramici)  →  L = 2,688 (fondo nicchia)")
p.rect(0.172, 1.10, 1.333, 2.55, fill=(214, 232, 242), out=BLU, wd=4)
p.txt(0.75, 1.90, "FINESTRA", F_LAB, BLU); p.txt(0.75, 1.73, "luce 1,161 × 1,45", F_MIN, BLU)
p.quota_v(0, 1.10, 0.09, "davanzale 1,10", F_MIN); p.quota_v(1.10, 2.55, 1.43, "1,45", F_MIN)
d.line([p.X(1.700), p.Y(0), p.X(1.700), p.Y(HU)], fill=MURO, width=4)
p.rect(1.700, 0, 2.688, 0.03, fill=(226, 234, 238))
p.rect(1.988, 0, 2.688, 0.04, fill=(206, 220, 228))
d.line([p.X(2.34), p.Y(2.10), p.X(2.34), p.Y(2.70)], fill=(90, 90, 95), width=6)
p.d.ellipse([p.X(2.30), p.Y(2.16), p.X(2.38), p.Y(2.04)], fill=(90, 90, 95))
p.rect(2.30, 1.00, 2.38, 1.10, fill=(90, 90, 95), out=(90, 90, 95))
p.txt(2.34, 2.40, "soffione 2,10", F_MIN, QUOTA)
p.txt(2.34, 0.80, "miscelatore 1,05", F_MIN, QUOTA)
d.line([p.X(1.988), p.Y(0), p.X(1.988), p.Y(2.00)], fill=VETRO, width=8)
p.txt(1.94, 1.62, "vetro", F_MIN, (70, 115, 145), anchor="rm")
p.txt(1.94, 1.48, "fisso 2,00", F_MIN, (70, 115, 145), anchor="rm")
p.txt(2.34, 0.28, "piatto a filo pavimento", F_MIN, QUOTA)
p.quota_h(0, 1.700, -0.22, "1,700 corpo", F_MIN); p.quota_h(1.700, 2.688, -0.22, "0,988 nicchia", F_MIN)
p.quota_v(0, HU, 2.84, "2,70 assunta", F_Q)
img.save("/home/user/Matteo/TRONO_arredo/bagni_prospetti_bagno.png"); print("prospetti bagno", img.size)
