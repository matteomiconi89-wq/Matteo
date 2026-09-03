# -*- coding: utf-8 -*-
"""
Genera un DXF (R12 / AC1009) con gli INGOMBRI QUOTATI di un divano letto,
vista laterale, nelle due posizioni:
  - DIVANO CHIUSO : prof. seduta 57, alt. seduta 35, piede 8
  - LETTO APERTO  : lunghezza 200, base 86, alt. 41
Quote in centimetri (1 unita' disegno = 1 cm, INSUNITS=5).
Nessuna dipendenza esterna: scrive direttamente il file DXF di testo.
Per usarlo in mm: aprire in AutoCAD e SCALA con fattore 10.
"""

import os

# ---------------- parametri stile quote ----------------
GAP, OVER = 1.5, 2.0     # stacco/sporgenza linee di estensione
AL, AW    = 3.5, 1.2     # lunghezza / semilarghezza freccia
TH, TGAP  = 7.0, 1.5     # altezza testo quote / stacco testo
TITLE_H   = 9.0

CONT, QUO, FLOOR, TXT = "CONTORNO", "QUOTE", "PAVIMENTO", "TESTO"

buf = []
def g(code, value):
    buf.append(str(code)); buf.append(str(value))
def fnum(x):
    return "{:.4f}".format(x)

def line(x1, y1, x2, y2, layer):
    g(0, "LINE"); g(8, layer)
    g(10, fnum(x1)); g(20, fnum(y1)); g(30, "0.0")
    g(11, fnum(x2)); g(21, fnum(y2)); g(31, "0.0")

def solid(ax, ay, bx, by, cx, cy, layer):
    g(0, "SOLID"); g(8, layer)
    g(10, fnum(ax)); g(20, fnum(ay)); g(30, "0.0")
    g(11, fnum(bx)); g(21, fnum(by)); g(31, "0.0")
    g(12, fnum(cx)); g(22, fnum(cy)); g(32, "0.0")
    g(13, fnum(cx)); g(23, fnum(cy)); g(33, "0.0")

def text(x, y, h, s, layer, halign=0, valign=0):
    g(0, "TEXT"); g(8, layer)
    g(10, fnum(x)); g(20, fnum(y)); g(30, "0.0")
    g(40, fnum(h)); g(1, s); g(7, "STANDARD")
    if halign or valign:
        g(72, halign); g(73, valign)
        g(11, fnum(x)); g(21, fnum(y)); g(31, "0.0")

def poly(pts, layer):
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
        line(x1, y1, x2, y2, layer)

# ---------------- quote ----------------
def dim_h(x1, x2, y_obj, y_dim, label):
    yd = 1.0 if y_dim >= y_obj else -1.0
    line(x1, y_obj + yd * GAP, x1, y_dim + yd * OVER, QUO)
    line(x2, y_obj + yd * GAP, x2, y_dim + yd * OVER, QUO)
    line(x1, y_dim, x2, y_dim, QUO)
    solid(x1, y_dim, x1 + AL, y_dim + AW, x1 + AL, y_dim - AW, QUO)
    solid(x2, y_dim, x2 - AL, y_dim + AW, x2 - AL, y_dim - AW, QUO)
    if yd > 0:
        ty, va = y_dim + TGAP, 1
    else:
        ty, va = y_dim - TGAP, 3
    text((x1 + x2) / 2.0, ty, TH, label, QUO, halign=1, valign=va)

def dim_v(y1, y2, x_obj, x_dim, label):
    xd = 1.0 if x_dim >= x_obj else -1.0
    line(x_obj + xd * GAP, y1, x_dim + xd * OVER, y1, QUO)
    line(x_obj + xd * GAP, y2, x_dim + xd * OVER, y2, QUO)
    line(x_dim, y1, x_dim, y2, QUO)
    solid(x_dim, y1, x_dim + AW, y1 + AL, x_dim - AW, y1 + AL, QUO)
    solid(x_dim, y2, x_dim + AW, y2 - AL, x_dim - AW, y2 - AL, QUO)
    if xd > 0:
        tx, ha = x_dim + TGAP, 0
    else:
        tx, ha = x_dim - TGAP, 2
    text(tx, (y1 + y2) / 2.0, TH, label, QUO, halign=ha, valign=2)

# ================= DIVANO CHIUSO =================
poly([(0, 8), (57, 8), (57, 35), (0, 35)], CONT)          # corpo seduta+telaio
poly([(0, 35), (-13, 35), (-20, 80), (-7, 80)], CONT)     # schienale inclinato
poly([(3, 8), (7, 8), (7, 0), (3, 0)], CONT)              # piedino post.
poly([(50, 8), (54, 8), (54, 0), (50, 0)], CONT)          # piedino ant.
line(-32, 0, 78, 0, FLOOR)                                # pavimento
dim_h(0, 57, 35, 92, "57")                                # prof. seduta
dim_v(0, 35, 57, 70, "35")                                # alt. seduta
dim_v(0, 8, 0, -16, "8")                                  # piede
text(18, -30, TITLE_H, "DIVANO CHIUSO", TXT, halign=1, valign=3)

# ================= LETTO APERTO =================
DX = 120.0
def P(x, y):
    return (x + DX, y)
poly([P(0, 27), P(200, 27), P(200, 35), P(0, 35)], CONT)  # piano letto
poly([P(0, 8), P(86, 8), P(86, 27), P(0, 27)], CONT)      # scatola base
poly([P(3, 8), P(7, 8), P(7, 0), P(3, 0)], CONT)          # piedino
poly([P(80, 8), P(84, 8), P(84, 0), P(80, 0)], CONT)      # piedino
poly([P(193, 35), P(200, 35), P(200, 41), P(193, 41)], CONT)  # alzata terminale
line(DX - 10, 0, DX + 214, 0, FLOOR)                      # pavimento
dim_h(DX + 0, DX + 200, 41, 58, "200")                    # lunghezza totale
dim_h(DX + 0, DX + 86, 0, -16, "86")                      # base
dim_v(0, 41, DX + 200, DX + 214, "41")                    # altezza dx
text(DX + 100, -30, TITLE_H, "LETTO APERTO", TXT, halign=1, valign=3)

# titolo generale
text(-32, 104, TITLE_H + 1, "DIVANO LETTO  -  INGOMBRI (quote in cm)", TXT)

# ---------------- assemblaggio file DXF R12 ----------------
def layer(name, color):
    return ("0\nLAYER\n2\n%s\n70\n0\n62\n%d\n6\nCONTINUOUS\n" % (name, color))

PREFIX = (
    "0\nSECTION\n2\nHEADER\n"
    "9\n$ACADVER\n1\nAC1009\n"
    "9\n$INSUNITS\n70\n5\n"
    "9\n$EXTMIN\n10\n-40.0\n20\n-40.0\n30\n0.0\n"
    "9\n$EXTMAX\n10\n345.0\n20\n115.0\n30\n0.0\n"
    "0\nENDSEC\n"
    "0\nSECTION\n2\nTABLES\n"
    # LTYPE
    "0\nTABLE\n2\nLTYPE\n70\n1\n"
    "0\nLTYPE\n2\nCONTINUOUS\n70\n0\n3\nSolid line\n72\n65\n73\n0\n40\n0.0\n"
    "0\nENDTAB\n"
    # LAYER
    "0\nTABLE\n2\nLAYER\n70\n5\n"
    + layer("0", 7) + layer(CONT, 7) + layer(QUO, 1)
    + layer(FLOOR, 8) + layer(TXT, 3)
    + "0\nENDTAB\n"
    # STYLE
    "0\nTABLE\n2\nSTYLE\n70\n1\n"
    "0\nSTYLE\n2\nSTANDARD\n70\n0\n40\n0.0\n41\n1.0\n50\n0.0\n71\n0\n42\n2.5\n3\ntxt\n4\n\n"
    "0\nENDTAB\n"
    "0\nENDSEC\n"
    "0\nSECTION\n2\nENTITIES\n"
)
SUFFIX = "0\nENDSEC\n0\nEOF\n"

out = PREFIX + "\n".join(buf) + "\n" + SUFFIX
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "divano_letto.dxf")
with open(path, "w", encoding="ascii") as fh:
    fh.write(out)
print("Scritto:", path)
print("Entita':", out.count("\n0\nLINE") + out.count("\n0\nSOLID") + out.count("\n0\nTEXT"))
