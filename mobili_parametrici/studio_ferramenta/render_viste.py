# -*- coding: utf-8 -*-
"""Genera viste PNG (wireframe proiettato) del MOBILE_DEMO per ispezione visiva.
freecadcmd render_viste.py"""
import os
import FreeCAD as App
import Import
from PIL import Image, ImageDraw

BASE = os.path.dirname(os.path.abspath(__file__))
doc = App.newDocument("r")
Import.insert(os.path.join(BASE, "MOBILE_DEMO.stp"), doc.Name)

def colore(lab):
    u = lab.upper()
    if "CERNIERA" in u:
        return (220, 30, 30)
    if "BASETTA" in u:
        return (240, 140, 0)
    if "LEGRABOX" in u or "GUIDA" in u:
        return (30, 90, 220)
    if "ANTA" in u:
        return (0, 150, 0)
    return (110, 110, 110)

pezzi = [o for o in doc.Objects if hasattr(o, "Shape") and o.Shape.Solids]

def rendi(nome, ax_h, ax_v, W=1500, H=1100, zfilter=None, only=None):
    # bbox globale sugli assi scelti
    pts = []
    for o in pezzi:
        bb = o.Shape.BoundBox
        pts += [(bb.XMin, bb.YMin, bb.ZMin), (bb.XMax, bb.YMax, bb.ZMax)]
    hs = [p[ax_h] for p in pts]; vs = [p[ax_v] for p in pts]
    hmin, hmax, vmin, vmax = min(hs), max(hs), min(vs), max(vs)
    mh = (hmax - hmin) * 0.06 + 10; mv = (vmax - vmin) * 0.06 + 10
    hmin -= mh; hmax += mh; vmin -= mv; vmax += mv
    sc = min((W - 20) / (hmax - hmin), (H - 20) / (vmax - vmin))
    def px(p):
        return (10 + (p[ax_h] - hmin) * sc, H - 10 - (p[ax_v] - vmin) * sc)
    img = Image.new("RGB", (W, H), (255, 255, 255))
    dr = ImageDraw.Draw(img)
    # ordine: pannelli prima, ferramenta sopra
    ordine = sorted(pezzi, key=lambda o: 0 if colore(o.Label) == (110, 110, 110) or "ANTA" in o.Label.upper() else 1)
    for o in ordine:
        if only and not any(k in o.Label.upper() for k in only):
            continue
        if zfilter is not None:
            bb = o.Shape.BoundBox
            zc = (bb.ZMin + bb.ZMax) / 2
            # per la pianta: tieni solo pezzi che attraversano la quota
            if not (bb.ZMin - 5 <= zfilter <= bb.ZMax + 5):
                continue
        col = colore(o.Label)
        for e in o.Shape.Edges:
            try:
                dpts = e.discretize(12)
            except Exception:
                continue
            for a, b in zip(dpts, dpts[1:]):
                dr.line([px(a), px(b)], fill=col, width=1)
    dr.text((12, 12), nome, fill=(0, 0, 0))
    out = os.path.join(BASE, "viste_" + nome + ".png")
    img.save(out)
    print("SCRITTO", out)

# 0=X,1=Y,2=Z
rendi("LATERALE_YZ", 1, 2)          # da X: profondita' x altezza (vedo ante, cassetto, guide)
rendi("FRONTE_XZ", 0, 2)            # da Y: larghezza x altezza
rendi("PIANTA_z103", 0, 1, zfilter=103.0)   # dall'alto alla quota 1a cerniera
rendi("PIANTA_cassetto_z260", 0, 1, zfilter=260.0)  # quota cassetto LEGRABOX
