# -*- coding: utf-8 -*-
"""Rendering PNG di regioni del DXF cucina — v2.
Bbox veri anche per i blocchi (ezdxf.bbox), poi si eliminano dalla copia in
memoria le entita' fuori regione e si disegna il layout intero (sfondo gestito bene).
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import ezdxf
from ezdxf import bbox as ezbbox
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing import pymupdf as pmb
from ezdxf.addons.drawing import layout, config

PATH = r"C:\Users\User\AppData\Local\Temp\claude\C--Users-User\53ab7e50-c7c9-4aa3-a2ad-1cdcdccbdaae\scratchpad\cucina.dxf"
OUT_DIR = r"C:\Users\User\AppData\Local\Temp\claude\C--Users-User\53ab7e50-c7c9-4aa3-a2ad-1cdcdccbdaae\scratchpad"

def ent_bbox(e, cache):
    """Bbox 2D dell'entita'; per INSERT/DIMENSION e tipi complessi usa ezdxf.bbox (contenuto vero)."""
    t = e.dxftype()
    try:
        if t == "LINE":
            p1, p2 = e.dxf.start, e.dxf.end
            return (min(p1.x, p2.x), min(p1.y, p2.y), max(p1.x, p2.x), max(p1.y, p2.y))
        if t == "LWPOLYLINE":
            pts = [(p[0], p[1]) for p in e.get_points()]
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            return (min(xs), min(ys), max(xs), max(ys))
        if t in ("CIRCLE", "ARC"):
            c, r = e.dxf.center, e.dxf.radius
            return (c.x - r, c.y - r, c.x + r, c.y + r)
        if t in ("TEXT", "MTEXT"):
            p = e.dxf.insert
            return (p.x, p.y, p.x, p.y)
        if t == "POINT":
            p = e.dxf.location
            return (p.x, p.y, p.x, p.y)
        # INSERT, DIMENSION, HATCH, SPLINE, ELLIPSE, resto: bbox vero via ezdxf
        ext = ezbbox.extents([e], fast=True, cache=cache)
        if ext.has_data:
            return (ext.extmin.x, ext.extmin.y, ext.extmax.x, ext.extmax.y)
    except Exception:
        return None
    return None

MOSTRI = ["PIEDINO_H.80 MM", "PIEDINO_H.80 MM_ditta HAFELE_art.637.76.352"]

def render_region(x0, y0, x1, y1, out_name, scale, skip_layers=(), dpi=96, crop=True):
    doc = ezdxf.readfile(PATH)
    msp = doc.modelspace()
    for nome in MOSTRI:
        try:
            blk = doc.blocks[nome]
            for e in list(blk):
                blk.delete_entity(e)
        except Exception:
            pass
    cache = ezbbox.Cache()
    skip = {s.upper() for s in skip_layers}
    to_delete, kept, no_box = [], 0, 0
    ext = [None, None, None, None]  # bbox di cio' che resta disegnato
    for e in msp:
        if e.dxf.layer.upper() in skip:
            to_delete.append(e); continue
        b = ent_bbox(e, cache)
        if b is None:
            no_box += 1
            to_delete.append(e); continue
        if b[2] < x0 or b[0] > x1 or b[3] < y0 or b[1] > y1:
            to_delete.append(e); continue
        if e.dxftype() == "TEXT":
            # stima larghezza/altezza del testo per l'estensione disegnata
            h = e.dxf.height or 100
            w = len(e.dxf.text or "") * h * 0.8
            b = (b[0], b[1], b[0] + w, b[1] + h * 1.4)
        kept += 1
        ext[0] = b[0] if ext[0] is None else min(ext[0], b[0])
        ext[1] = b[1] if ext[1] is None else min(ext[1], b[1])
        ext[2] = b[2] if ext[2] is None else max(ext[2], b[2])
        ext[3] = b[3] if ext[3] is None else max(ext[3], b[3])
    for e in to_delete:
        try:
            msp.delete_entity(e)
        except Exception:
            pass
    ctx = RenderContext(doc)
    backend = pmb.PyMuPdfBackend()
    cfg = config.Configuration(background_policy=config.BackgroundPolicy.WHITE)
    Frontend(ctx, backend, config=cfg).draw_layout(msp, finalize=True)
    page = layout.Page(0, 0, layout.Units.mm)
    settings = layout.Settings(scale=scale)
    png = backend.get_pixmap_bytes(page=page, fmt="png", settings=settings, dpi=dpi)
    out = OUT_DIR + "\\" + out_name
    with open(out, "wb") as f:
        f.write(png)
    from PIL import Image
    im = Image.open(out)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        base = Image.new("RGB", im.size, (255, 255, 255))
        base.paste(im, mask=im.split()[-1])
        im = base
    # ritaglio alla regione richiesta (il canvas copre l'estensione di tutto il disegnato)
    if crop and ext[0] is not None and ext[2] > ext[0] and ext[3] > ext[1]:
        ppm_x = im.size[0] / (ext[2] - ext[0])
        ppm_y = im.size[1] / (ext[3] - ext[1])
        left = max(0, int((x0 - ext[0]) * ppm_x))
        right = min(im.size[0], int((x1 - ext[0]) * ppm_x))
        top = max(0, int((ext[3] - y1) * ppm_y))
        bottom = min(im.size[1], int((ext[3] - y0) * ppm_y))
        if right > left + 50 and bottom > top + 50:
            im = im.crop((left, top, right, bottom))
    im.save(out)
    print(f"{out_name}: {kept} entita' tenute ({no_box} senza bbox), {im.size[0]}x{im.size[1]} px")

if __name__ == "__main__":
    import json
    if len(sys.argv) > 2:
        PATH = sys.argv[2]
    jobs = json.load(open(sys.argv[1], encoding="utf-8"))
    for j in jobs:
        render_region(j["x0"], j["y0"], j["x1"], j["y1"], j["out"], j["scale"],
                      skip_layers=j.get("skip", []), dpi=j.get("dpi", 96),
                      crop=j.get("crop", True))
