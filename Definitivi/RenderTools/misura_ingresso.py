# -*- coding: utf-8 -*-
"""Misura deterministica del mobile ingresso nel render: bbox e giunzioni verticali.
Trova il mobile per contrasto col muro greige e le fughe come minimi di luminosita' colonna."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image

def misura(path):
    im = Image.open(path).convert("L")
    W, H = im.size
    px = im.load()
    # fascia orizzontale a meta' altezza del mobile presunto (35%-75% H): il mobile e' li'
    y0, y1 = int(H * 0.30), int(H * 0.72)
    colmean = []
    for x in range(W):
        s = 0
        for y in range(y0, y1, 4):
            s += px[x, y]
        colmean.append(s / len(range(y0, y1, 4)))
    # il muro e' relativamente uniforme: stimo il livello muro dai bordi estremi
    muro = (sum(colmean[:200]) + sum(colmean[-200:])) / 400
    # il mobile: zona centrale dove la media differisce dal muro o ci sono forti gradienti
    import statistics
    grad = [abs(colmean[x + 1] - colmean[x]) for x in range(W - 1)] + [0]
    # bordi mobile: primo/ultimo x con gradiente forte vicino al centro
    forti = [x for x in range(200, W - 200) if grad[x] > 6]
    if not forti:
        print(f"{path}: nessun bordo forte trovato"); return
    sinistra, destra = min(forti), max(forti)
    # bbox verticale: il top e' dove il profilo di riga DENTRO il mobile si stacca da quello
    # del muro FUORI (la linea del soffitto attraversa tutto il quadro e non deve contare);
    # il fondo e' la gola d'ombra scura sotto i frontali (riga piu' scura della fascia bassa)
    def rowprof(xa, xb):
        prof = []
        for y in range(H):
            s = 0; cnt = 0
            for x in range(xa, xb, 6):
                s += px[x, y]; cnt += 1
            prof.append(s / cnt)
        return prof
    dentro = rowprof(sinistra + 10, destra - 10)
    fx0 = max(10, sinistra - 320)
    fuori_sx = rowprof(fx0, max(fx0 + 30, sinistra - 60))
    fx1 = min(W - 10, destra + 320)
    fuori_dx = rowprof(min(fx1 - 30, destra + 60), fx1)
    fuori = [(a + b) / 2 for a, b in zip(fuori_sx, fuori_dx)]
    # top = spigolo netto: riga col gradiente piu' forte del profilo interno,
    # cercato sotto la linea del soffitto e sopra meta' mobile (l'ombra sul muro e' morbida)
    dgrad = [abs(dentro[y + 1] - dentro[y]) for y in range(H - 1)] + [0]
    top = max(range(int(H * 0.15), int(H * 0.55)), key=lambda y: dgrad[y])
    zona = range(int(H * 0.62), int(H * 0.94))
    fondo = min(zona, key=lambda y: dentro[y])
    lw = destra - sinistra
    lh = fondo - top
    print(f"{path}")
    print(f"  bbox mobile: x {sinistra}-{destra} (L={lw}), y {top}-{fondo} (H={lh}), H/L={lh/lw:.3f}")
    # giunzioni: minimi locali di luminosita' (fughe scure) dentro il mobile
    fughe = []
    for x in range(sinistra + 8, destra - 8):
        v = colmean[x]
        if v < muro - 25 and v == min(colmean[x - 8:x + 9]):
            if not fughe or x - fughe[-1] > 20:
                fughe.append(x)
    print(f"  livello muro {muro:.0f}; fughe scure (minimi): {fughe}")
    seg = [sinistra] + fughe + [destra]
    larghezze = [seg[i + 1] - seg[i] for i in range(len(seg) - 1)]
    tot = sum(larghezze)
    quote = [f"{l}px={l*100/tot:.1f}%" for l in larghezze]
    print(f"  sezioni: {quote}")

for p in sys.argv[1:]:
    misura(p)
