# -*- coding: utf-8 -*-
"""Misura le quote verticali (35, 41) tramite le loro linee di estensione
ORIZZONTALI (i trattini in alto e in basso), per verificare l'isotropia."""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
img = Image.open(os.path.join(HERE, "foto_divanoletto.png")).convert("L")
W, H = img.size
d = list(img.getdata())
def ink(x, y): return d[y * W + x] < 160

def vspan(x0, x1, thr, label, real):
    rows = [y for y in range(H) if sum(1 for x in range(x0, x1) if ink(x, y)) >= thr]
    if not rows:
        print(" %s: nessuna estensione trovata in x=[%d,%d]" % (label, x0, x1)); return
    lo, hi = min(rows), max(rows)
    print(" %s: estensioni y=%d..%d span=%d px -> %g/span=%.4f cm/px"
          % (label, lo, hi, hi - lo, real, real / (hi - lo)))

# banda a destra del divano (quota 35) e all'estrema destra del letto (quota 41)
vspan(352, 405, 5, "35 (SX, dx furniture)", 35)
vspan(1085, 1170, 5, "41 (DX, estrema dx)", 41)
# riprova quota 8 (SX, estrema sinistra)
vspan(95, 140, 4, "8  (SX, estrema sx)", 8)
