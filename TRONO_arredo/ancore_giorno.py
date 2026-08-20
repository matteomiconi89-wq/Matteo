# -*- coding: utf-8 -*-
"""Piante della zona giorno ricavate dalla GEOMETRIA VETTORIALE del PDF
'ARREDO - 4 opzioni' (pagine 3-6). Nessuna misura inventata: coordinate lette dal file.
Scala del PDF: 39,63 punti = 1 metro."""
from PIL import Image, ImageDraw, ImageFont

S = 39.63                      # punti PDF per metro
CORPO = (116.9, 390.3, 358.2, 551.2)
ALA   = (358.2, 434.4, 435.2, 551.2)

MOB = {
"A": [[124.9,446.1,158.5,479.7],[168.4,531.4,263.5,551.2],[214.0,394.3,313.0,431.9],
      [303.1,473.8,366.4,509.4],[362.2,434.4,435.2,458.2],[411.5,458.2,435.2,551.2]],
"B": [[122.9,513.6,210.0,549.2],[185.1,390.3,272.2,406.2],[219.9,414.1,253.6,447.7],
      [271.4,501.7,342.7,537.4],[302.8,434.4,362.2,470.0],[362.2,434.4,435.2,458.2],
      [411.5,458.2,435.2,551.2]],
"C": [[124.9,446.1,158.5,479.7],[168.4,479.9,263.5,515.6],[185.1,390.3,319.7,408.1],
      [291.2,454.2,354.5,489.8],[362.2,434.4,435.2,458.2],[362.2,527.5,411.5,551.2],
      [411.5,458.2,435.2,551.2]],
"D": [[168.4,531.4,263.5,551.2],[172.4,465.9,243.7,501.5],[185.1,394.3,288.0,429.9],
      [288.0,394.3,321.7,457.6],[295.1,493.6,328.8,527.3],[362.2,434.4,411.5,458.2],
      [362.2,527.5,411.5,551.2],[411.5,434.4,435.2,551.2]],
}
LAB = {
"A": [[260.4,412.8,"divano 3 posti"],[214.1,541.0,"mobile tv"],[332.9,491.3,"tavolo 6"],[398.3,446.0,"cucina a L"]],
"B": [[166.2,531.1,"divano"],[226.4,397.9,"parete tv"],[304.7,519.2,"tavolo 6-8"],[398.3,446.0,"cucina"],[331.5,451.9,"penisola"]],
"C": [[212.8,497.4,"divano 3 posti"],[321.1,471.7,"tavolo 6"],[398.3,446.0,"cucina a U"],[386.9,539.0,"colonne"],[252.0,399.0,"parete attrezzata 3,40"]],
"D": [[236.4,411.8,"divano"],[214.1,541.0,"mobile tv"],[206.2,483.4,"tavolo 8"],[423.0,492.5,"cucina"],[384.0,539.0,"lavatrice"]],
}
TIT = {"A":"OPZIONE A - cucina a L","B":"OPZIONE B - penisola",
       "C":"OPZIONE C - cucina a U","D":"OPZIONE D - lavatrice in cucina"}

W, H = 1700, 1000
BG, INK, DIM, FILL, ACC = (255,255,255), (25,25,25), (120,120,120), (226,226,222), (190,60,40)
def font(sz):
    try: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", sz)
    except Exception: return ImageFont.load_default()
FB, F, FS = font(38), font(26), font(21)

K = 3.15                                   # px per punto PDF
OX, OY = 150, 230                          # origine su tela
def X(v): return OX + (v - CORPO[0]) * K
def Y(v): return OY + (v - CORPO[1]) * K

for op in "ABCD":
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    d.text((W/2, 52), "SOGGIORNO + CUCINA - " + TIT[op], font=FB, fill=INK, anchor="mm")
    d.text((W/2, 100), "pianta reale letta dal disegno - ambiente unico a L, 30,45 mq - altezza utile 2,70",
           font=FS, fill=DIM, anchor="mm")
    # sagoma a L
    poly = [(X(CORPO[0]),Y(CORPO[1])), (X(ALA[0]),Y(CORPO[1])), (X(ALA[0]),Y(ALA[1])),
            (X(ALA[2]),Y(ALA[1])), (X(ALA[2]),Y(ALA[3])), (X(CORPO[0]),Y(CORPO[3]))]
    d.polygon(poly, fill=(247,247,245), outline=INK)
    d.line(poly + [poly[0]], fill=INK, width=7)
    for r in MOB[op]:
        d.rectangle([X(r[0]),Y(r[1]),X(r[2]),Y(r[3])], fill=FILL, outline=INK, width=4)
    for lx, ly, t in LAB[op]:
        d.text((X(lx), Y(ly)), t, font=FS, fill=INK, anchor="mm")
    # quote
    def quota(x1,y1,x2,y2,txt,off,vert=False):
        d.line([(x1,y1),(x2,y2)], fill=DIM, width=2)
        t=8
        if vert:
            d.line([(x1-t,y1),(x1+t,y1)],fill=DIM,width=2); d.line([(x2-t,y2),(x2+t,y2)],fill=DIM,width=2)
            d.text((x1+off,(y1+y2)/2), txt, font=FS, fill=DIM, anchor="mm")
        else:
            d.line([(x1,y1-t),(x1,y1+t)],fill=DIM,width=2); d.line([(x2,y2-t),(x2,y2+t)],fill=DIM,width=2)
            d.text(((x1+x2)/2,y1+off), txt, font=FS, fill=DIM, anchor="mm")
    quota(X(CORPO[0]), Y(CORPO[3])+52, X(ALA[2]), Y(CORPO[3])+52, "8,03 m complessivi", 30)
    quota(X(CORPO[0])-52, Y(CORPO[1]), X(CORPO[0])-52, Y(CORPO[3]), "4,06 m", -55, True)
    quota(X(ALA[0]), Y(ALA[1])-34, X(ALA[2]), Y(ALA[1])-34, "1,94 m", -28)
    d.text((X(ALA[0])+ (X(ALA[2])-X(ALA[0]))/2, Y(CORPO[1])+26),
           "QUESTO ANGOLO NON ESISTE", font=FS, fill=ACC, anchor="mm")
    d.text((W/2, H-42),
           "L'ala larga 1,94 e' la zona cottura: la cucina sta LI', non lungo la parete del corpo principale.",
           font=FS, fill=ACC, anchor="mm")
    img.save("pianta_giorno_%s.png" % op)
    print("pianta_giorno_%s.png" % op)
