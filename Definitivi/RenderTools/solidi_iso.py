# -*- coding: utf-8 -*-
"""Mini-motore assonometrico: solidi (box) -> vista cavaliera PNG con Pillow.
Protocollo Matteo: dal 2D monto i solidi senza forature, le viste vanno a Manus."""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image, ImageDraw

# proiezione cavaliera: X a destra, Z in alto, Y (profondita' verso l'osservatore) obliqua
KY = 0.45
ANG = 0.5  # componente verticale dell'obliqua

def proietta(x, y, z):
    return (x + KY * y, -(z + KY * ANG * y))

def disegna(solidi, out, scala=0.25, margine=60):
    # bounds
    pts = []
    for s in solidi:
        x0, y0, z0, x1, y1, z1 = s["box"]
        for x in (x0, x1):
            for y in (y0, y1):
                for z in (z0, z1):
                    pts.append(proietta(x, y, z))
    minx = min(p[0] for p in pts); maxx = max(p[0] for p in pts)
    miny = min(p[1] for p in pts); maxy = max(p[1] for p in pts)
    W = int((maxx - minx) * scala) + 2 * margine
    H = int((maxy - miny) * scala) + 2 * margine
    im = Image.new("RGB", (W, H), (250, 249, 247))
    dr = ImageDraw.Draw(im)
    def m(p):
        return ((p[0] - minx) * scala + margine, (p[1] - miny) * scala + margine)
    # painter: prima i lontani (y piccola), poi z bassa
    for s in sorted(solidi, key=lambda s: (s["box"][1] + s["box"][4], s["box"][2])):
        x0, y0, z0, x1, y1, z1 = s["box"]
        base = tuple(s.get("col", (200, 195, 188)))
        scuro = tuple(int(c * 0.72) for c in base)
        medio = tuple(int(c * 0.86) for c in base)
        # faccia laterale destra (x1)
        f = [proietta(x1, y0, z0), proietta(x1, y1, z0), proietta(x1, y1, z1), proietta(x1, y0, z1)]
        dr.polygon([m(p) for p in f], fill=scuro, outline=(90, 88, 85))
        # faccia top (z1)
        f = [proietta(x0, y0, z1), proietta(x1, y0, z1), proietta(x1, y1, z1), proietta(x0, y1, z1)]
        dr.polygon([m(p) for p in f], fill=medio, outline=(90, 88, 85))
        # faccia frontale (y1, verso osservatore)
        f = [proietta(x0, y1, z0), proietta(x1, y1, z0), proietta(x1, y1, z1), proietta(x0, y1, z1)]
        dr.polygon([m(p) for p in f], fill=base, outline=(90, 88, 85))
    im.save(out)
    print(f"{out}: {W}x{H}")

if __name__ == "__main__":
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    disegna(cfg["solidi"], cfg["out"], cfg.get("scala", 0.25))
