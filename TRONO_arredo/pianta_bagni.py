# -*- coding: utf-8 -*-
"""Trascrizione fedele della zona WC + BAGNO dal rilievo Piano Primo(1).pdf.
Nessuna interpretazione: ogni primitiva e' ridisegnata alle sue coordinate.
Scala del rilievo: 36,00 punti PDF = 1 metro."""
from PIL import Image, ImageDraw, ImageFont
S = 36.00
LINEE = [
 (484.4,266.2,484.4,308.0),(484.4,308.0,484.4,328.0),(484.4,328.0,484.4,474.2),
 (497.1,269.1,497.1,305.0),(490.8,269.1,490.8,305.0),(484.4,305.0,497.1,308.0),
 (490.8,287.0,546.6,287.0),(336.0,207.2,484.4,207.2),(336.0,203.2,484.4,203.2),
 (380.7,256.0,484.4,282.2),(441.2,328.0,484.4,360.4),(371.2,312.6,444.8,328.0),
 (332.4,368.0,402.3,368.0),(380.7,364.4,405.9,367.3),(484.4,364.0,484.4,367.6),
]
RETT = [  # x0,y0,x1,y1,etichetta
 (402.3,367.3,405.9,474.2,""),
 (444.8,331.6,484.4,356.8,"doccia 1,00 x 0,60"),(446.7,333.5,482.7,355.1,""),
 (462.7,237.4,475.9,256.0,"bidet"),(464.4,239.2,474.2,251.8,""),
 (437.8,237.4,451.0,256.0,"wc"),(439.5,239.2,449.3,251.8,""),
 (408.2,207.2,429.8,223.3,"lavabo 0,50"),(410.0,208.9,428.0,221.6,""),
 (462.7,260.0,475.9,278.8,"bidet"),(464.4,264.2,474.2,276.9,""),
 (437.8,260.0,451.0,278.8,"wc"),(439.5,264.2,449.3,276.9,""),
 (405.2,260.0,426.8,276.2,"lavabo 0,50"),(406.9,261.8,424.9,274.4,""),
]
PORTE = [(384.7,225.7,413.5,254.5,384.8,254.4,413.6,254.4),
         (384.7,282.2,413.5,311.0,384.8,311.0,413.6,311.0),
         (384.7,331.5,413.5,360.3,384.8,331.5,413.6,331.5)]
CERCHI = [(461.5,341.1,467.8,347.4),(468.8,253.5,470.1,254.8),(468.8,261.3,470.1,262.6)]

X0,X1,Y0,Y1 = 330.0, 512.0, 195.0, 380.0
K = 7.2
W = int((X1-X0)*K)+300; H = int((Y1-Y0)*K)+260
def X(v): return 150 + (v-X0)*K
def Y(v): return 150 + (v-Y0)*K
img = Image.new("RGB",(W,H),(255,255,255)); d = ImageDraw.Draw(img)
def font(s):
    try: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", s)
    except Exception: return ImageFont.load_default()
FB,F,FS = font(34), font(22), font(18)
d.text((W/2,48),"WC e BAGNO - trascrizione fedele dal rilievo", font=FB, fill=(20,20,20), anchor="mm")
d.text((W/2,86),"ogni elemento e' alle coordinate del disegno originale - scala 36,00 pt/m - nessuna interpretazione",
       font=FS, fill=(120,120,120), anchor="mm")
for x0,y0,x1,y1 in LINEE:
    d.line([X(x0),Y(y0),X(x1),Y(y1)], fill=(25,25,25), width=5)
for x0,y0,x1,y1,lab in RETT:
    d.rectangle([X(x0),Y(y0),X(x1),Y(y1)], fill=(232,232,228), outline=(25,25,25), width=3)
    if lab:
        d.text(((X(x0)+X(x1))/2,(Y(y0)+Y(y1))/2-14), lab, font=FS, fill=(25,25,25), anchor="mm")
        d.text(((X(x0)+X(x1))/2,(Y(y0)+Y(y1))/2+10),
               "%.2f x %.2f" % ((x1-x0)/S,(y1-y0)/S), font=FS, fill=(110,110,110), anchor="mm")
for ax0,ay0,ax1,ay1,lx0,ly0,lx1,ly1 in PORTE:
    d.arc([X(ax0),Y(ay0),X(ax1),Y(ay1)], 0, 360, fill=(170,170,170), width=2)
    d.line([X(lx0),Y(ly0),X(lx1),Y(ly1)], fill=(190,60,40), width=5)
    d.text(((X(lx0)+X(lx1))/2,(Y(ly0)+Y(ly1))/2-20),"porta 0,80", font=FS, fill=(190,60,40), anchor="mm")
for c in CERCHI:
    d.ellipse([X(c[0]),Y(c[1]),X(c[2]),Y(c[3])], outline=(25,25,25), width=2)
d.text((X(453),Y(232)),"WC  1,36 di profondita'", font=F, fill=(60,60,60), anchor="mm")
d.text((X(455),Y(300)),"BAGNO  2,69 di profondita'", font=F, fill=(60,60,60), anchor="mm")
d.text((W/2,H-46),
 "Le tre porte da 0,80 sono tutte sullo stesso filo a sinistra. Il rosso e' l'anta, il grigio il raggio di apertura.",
 font=FS, fill=(190,60,40), anchor="mm")
img.save("pianta_bagni_rilievo.png"); print("fatto")
