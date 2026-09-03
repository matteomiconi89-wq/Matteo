# -*- coding: utf-8 -*-
"""Spiana le cuciture del warp su soffitto + fascia di muro sopra il mobile:
blur uniforme y 0-336 a piena larghezza, feather in basso, faretti protetti da isole radiali."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image, ImageFilter, ImageDraw

DIR = r"C:\Users\User\Dropbox\STEFANO\Matteo\RENDER_MANUS\26-A011_mobile_ingresso"
p = DIR + r"\render_INGRESSO_FINALE_aperto.png"
im = Image.open(p).convert("RGB")
W, H = im.size

y1 = 336
fascia = im.crop((0, 0, W, y1)).filter(ImageFilter.GaussianBlur(2.5))
mask = Image.new("L", (W, y1), 255)
dr = ImageDraw.Draw(mask)
for j in range(24):
    a = int(255 * j / 24)
    dr.line([(0, y1 - 1 - j), (W, y1 - 1 - j)], fill=a)
# isole di protezione sui faretti (nessuna cade sulle cuciture a x~1128/1425-1465)
for cx in (568, 988, 1584, 1900, 2164, 2470):
    for r, a in ((70, 255), (58, 128), (46, 0)):
        dr.ellipse([cx - r, 62 - r, cx + r, 62 + r], fill=255 - a if a != 255 else 0)
# ricostruisci le isole con feather corretto: 0 dentro, 128 nel mezzo, pieno fuori
mask2 = Image.new("L", (W, y1), 255)
dr2 = ImageDraw.Draw(mask2)
for j in range(24):
    a = int(255 * j / 24)
    dr2.line([(0, y1 - 1 - j), (W, y1 - 1 - j)], fill=a)
for cx in (568, 988, 1584, 1900, 2164, 2470):
    dr2.ellipse([cx - 70, -8, cx + 70, 132], fill=90)
    dr2.ellipse([cx - 52, 10, cx + 52, 114], fill=0)
im.paste(fascia, (0, 0), mask2)
im.save(p)
print("soffitto+muro spianati, faretti protetti")
