# -*- coding: utf-8 -*-
"""Ri-legge divano_letto.dxf: verifica struttura, conta entita', bbox.
Se Pillow e' disponibile, salva un'anteprima PNG."""
import os

here = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(here, "divano_letto.dxf")
with open(path, "r", encoding="ascii") as fh:
    raw = fh.read().split("\n")
# rimuove eventuale ultima riga vuota
while raw and raw[-1] == "":
    raw.pop()

pairs = []
for i in range(0, len(raw) - 1, 2):
    pairs.append((raw[i].strip(), raw[i + 1]))

# --- controllo struttura ---
sec = sum(1 for c, v in pairs if c == "0" and v == "SECTION")
end = sum(1 for c, v in pairs if c == "0" and v == "ENDSEC")
has_eof = any(c == "0" and v == "EOF" for c, v in pairs)
ents = {"LINE": 0, "SOLID": 0, "TEXT": 0}
lines, solids, texts = [], [], []

i = 0
n = len(pairs)
while i < n:
    c, v = pairs[i]
    if c == "0" and v in ents:
        kind = v
        ents[kind] += 1
        attr = {}
        j = i + 1
        while j < n and pairs[j][0] != "0":
            attr.setdefault(pairs[j][0], pairs[j][1])
            j += 1
        if kind == "LINE":
            lines.append((float(attr["10"]), float(attr["20"]),
                          float(attr["11"]), float(attr["21"]),
                          attr.get("8", "")))
        elif kind == "SOLID":
            solids.append((float(attr["10"]), float(attr["20"]),
                           float(attr["11"]), float(attr["21"]),
                           float(attr["12"]), float(attr["22"]),
                           attr.get("8", "")))
        elif kind == "TEXT":
            texts.append((float(attr["10"]), float(attr["20"]),
                          float(attr.get("40", "5")), attr.get("1", ""),
                          int(attr.get("72", "0")), attr.get("8", "")))
        i = j
    else:
        i += 1

xs, ys = [], []
for x1, y1, x2, y2, _ in lines:
    xs += [x1, x2]; ys += [y1, y2]

print("SECTION =", sec, " ENDSEC =", end, " EOF =", has_eof)
print("Entita':", ents)
if xs:
    print("BBox X: %.1f .. %.1f   Y: %.1f .. %.1f" % (min(xs), max(xs), min(ys), max(ys)))
ok = (sec == end == 3) and has_eof and all(ents.values())
print("STRUTTURA:", "OK" if ok else "ATTENZIONE")

# --- anteprima PNG (se Pillow presente) ---
try:
    from PIL import Image, ImageDraw, ImageFont
    pad = 25
    minx, maxx = -45, 350
    miny, maxy = -45, 120
    W = 1700
    s = (W - 2 * pad) / (maxx - minx)
    H = int((maxy - miny) * s + 2 * pad)

    def tx(x): return pad + (x - minx) * s
    def ty(y): return H - pad - (y - miny) * s

    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    col = {"CONTORNO": (0, 0, 0), "QUOTE": (200, 0, 0),
           "PAVIMENTO": (140, 140, 140), "TESTO": (0, 110, 0)}
    for x1, y1, x2, y2, ly in lines:
        d.line([tx(x1), ty(y1), tx(x2), ty(y2)], fill=col.get(ly, (0, 0, 0)), width=2)
    for a in solids:
        x1, y1, x2, y2, x3, y3, ly = a
        d.polygon([tx(x1), ty(y1), tx(x2), ty(y2), tx(x3), ty(y3)], fill=col.get(ly, (0, 0, 0)))
    for x, y, h, s_, j, ly in texts:
        try:
            fnt = ImageFont.truetype("arial.ttf", max(10, int(h * s)))
        except Exception:
            fnt = ImageFont.load_default()
        anchor = "mm" if j == 1 else ("rm" if j == 2 else "lm")
        d.text((tx(x), ty(y)), s_, fill=col.get(ly, (0, 0, 0)), font=fnt, anchor=anchor)
    png = os.path.join(here, "anteprima.png")
    img.save(png)
    print("PNG:", png)
except ImportError:
    print("Pillow assente: salto anteprima PNG.")
