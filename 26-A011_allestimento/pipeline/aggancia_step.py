#!/usr/bin/env python3
"""Trova da solo dove va posizionato uno STEP nel truck, confrontandolo con la pianta.

Finora la posizione di ogni mobile la ricavavo a mano leggendo le quote. Questo
script la deduce: prende le impronte in pianta dei pezzi dello STEP, le confronta
con le polilinee chiuse del DWG e vota la trasformazione (rotazione + offset) che
fa combaciare piu' pezzi. Le rotazioni provate sono 0/90/180/270 attorno a Z.

Serve perche' due mobili possono avere lo stesso ingombro ma orientamento opposto:
il mobile ingresso e' ruotato di -90, il divisorio di +90, e a occhio non si vede.

    python3 aggancia_step.py file.stp [file.stp ...]
"""
import collections, math, sys
import cadquery as cq
from step_assembly import read_assembly
from materiali_da_dwg import impronte

TOL = 1.0          # mm di tolleranza sulle dimensioni
TRUCK = (-800, 14000, -900, 5600)   # solo la pianta del veicolo: i DWG portano
                                    # anche copie di dettaglio fuori sagoma
PASSO = 0.1        # arrotondamento del voto sull'offset


def rettangoli_step(path):
    """impronta in pianta (x0,x1,y0,y1) di ogni pezzo dello STEP"""
    out = []
    for nome, sh in read_assembly(path):
        b = cq.Shape.cast(sh).BoundingBox()
        out.append((nome, b.xmin, b.xmax, b.ymin, b.ymax))
    return out


def ruota(r, gradi):
    """ruota un rettangolo attorno all'origine di 0/90/180/270 gradi"""
    _, x0, x1, y0, y1 = r
    c, s = round(math.cos(math.radians(gradi))), round(math.sin(math.radians(gradi)))
    xs = [x * c - y * s for x in (x0, x1) for y in (y0, y1)]
    ys = [x * s + y * c for x in (x0, x1) for y in (y0, y1)]
    return min(xs), max(xs), min(ys), max(ys)


def aggancia(path, pol):
    # indicizza le polilinee della pianta per dimensione, cosi' il confronto e' rapido
    per_dim = collections.defaultdict(list)
    for lay, x0, x1, y0, y1 in pol:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if not (TRUCK[0] < cx < TRUCK[1] and TRUCK[2] < cy < TRUCK[3]):
            continue                      # scarta le copie di dettaglio fuori sagoma
        per_dim[(round(x1 - x0), round(y1 - y0))].append((x0, y0))

    migliore = None
    for gradi in (0, 90, 180, 270):
        voti = collections.Counter()
        for r in rettangoli_step(path):
            x0, x1, y0, y1 = ruota(r, gradi)
            w, h = x1 - x0, y1 - y0
            for dw in (-1, 0, 1):                     # tolleranza sull'arrotondamento
                for dh in (-1, 0, 1):
                    for px, py in per_dim.get((round(w) + dw, round(h) + dh), ()):
                        if abs((px + w) - (px + w)) > TOL:
                            continue
                        voti[(round((px - x0) / PASSO), round((py - y0) / PASSO))] += 1
        if voti:
            (ox, oy), n = voti.most_common(1)[0]
            if migliore is None or n > migliore[0]:
                migliore = (n, gradi, ox * PASSO, oy * PASSO)
    return migliore


if __name__ == "__main__":
    pol = impronte("/tmp/pianta.dxf")
    print(f"{len(pol)} impronte in pianta\n")
    for p in sys.argv[1:]:
        tot = len(rettangoli_step(p))
        m = aggancia(p, pol)
        nome = p.rsplit("/", 1)[-1]
        if not m:
            print(f"{nome:44s} nessuna corrispondenza"); continue
        n, gradi, ox, oy = m
        print(f"{nome:44s} rot {gradi:4d}  offset ({ox:9.1f}, {oy:8.1f})   "
              f"{n}/{tot} pezzi combaciano")
