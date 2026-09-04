#!/usr/bin/env python3
"""Controlla che le inquadrature del render non attraversino i mobili.

Il vano della camera master e' quasi tutto occupato: l'armadio chiude la parete
ingresso (z 1.16..1.78), la testata-letto la parete anteriore (x < 0.15) e il
divisorio chiude il lato living (x 1.52..1.86) tranne il varco della porta
(z > 0.59). Restano liberi solo due settori: la porta e il fianco che si allarga.

Per ogni inquadratura campiona il percorso e verifica:
  - la camera non finisce DENTRO un solido;
  - la linea di mira non e' ostruita (a parte il mobile che e' il soggetto).

    python3 verifica_inquadrature.py
"""
import json, math, pathlib

HERE = pathlib.Path(__file__).parent
CX, CY, PAV = 2422, 1829.5, 1395          # centro stanza / quota pavimento (mm)


def scena(v):              # trailer(mm) -> scena(m), Y in alto, z negato (terna destrorsa)
    return ((v[0] - CX) / 1000, (v[2] - PAV) / 1000, -(v[1] - CY) / 1000)


G = json.load(open(HERE.parent / "arredo_geometry.json"))["mobili"]
BOX = []
for k in ("armadio_master", "parete_letto_master", "letto_master", "parete_div_master"):
    for p in G[k]:
        a = [scena(v) for v in p["v"]]
        BOX.append((k, p["l"],
                    [min(c[i] for c in a) for i in range(3)],
                    [max(c[i] for c in a) for i in range(3)]))


def dentro(pt):
    return [f"{k}/{n}" for k, n, lo, hi in BOX
            if all(lo[i] - 0.02 <= pt[i] <= hi[i] + 0.02 for i in range(3))]


def ostruzioni(a, b):
    """slab test segmento/box: cosa si frappone tra camera e bersaglio"""
    out, d = [], [b[i] - a[i] for i in range(3)]
    for k, n, lo, hi in BOX:
        t0, t1, ok = 0.0, 1.0, True
        for i in range(3):
            if abs(d[i]) < 1e-9:
                if a[i] < lo[i] or a[i] > hi[i]:
                    ok = False; break
            else:
                u, v = (lo[i] - a[i]) / d[i], (hi[i] - a[i]) / d[i]
                if u > v: u, v = v, u
                t0, t1 = max(t0, u), min(t1, v)
                if t0 > t1:
                    ok = False; break
        if ok:
            out.append(f"{k}/{n}")
    return out


ease = lambda t: 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2
lerp = lambda a, b, k: [a[i] + (b[i] - a[i]) * k for i in range(3)]

# le stesse costanti che stanno in render_camera_master.html
SHOTS = [
    ("Dalla porta",       [2.80, 1.66, 1.30], [1.78, 1.56, 1.02],
                          [0.20, 1.02, 0.20], [-0.55, 0.98, -0.10], None),
    ("Armadio 6 casse",   [-1.20, 1.55, -0.58], [1.36, 1.50, -0.58],
                          [-1.10, 1.02, 1.45], [1.26, 1.02, 1.45], "armadio_master"),
    ("Testata e letto",   [1.28, 1.62, -0.78], [0.18, 1.30, -0.56],
                          [-1.32, 0.94, -0.42], [-1.62, 1.06, -0.46], "parete_letto"),
]
BERSAGLIO_VOLO = [-0.20, 1.00, -0.05]

problemi = 0
for nome, p0, p1, t0, t1, soggetto in SHOTS:
    cam, mira = set(), set()
    for j in range(41):
        k = ease(j / 40)
        p, t = lerp(p0, p1, k), lerp(t0, t1, k)
        cam.update(dentro(p))
        mira.update(o for o in ostruzioni(p, t) if not soggetto or not o.startswith(soggetto))
    problemi += len(cam) + len(mira)
    print(f"{nome:18s} camera dentro: {sorted(cam) or 'libera':<12} "
          f"ostruzioni: {sorted(mira)[:3] or 'nessuna'}")

cam, mira = set(), set()
for j in range(61):                        # volo: arco 55 -> 118 gradi
    e = ease(j / 60)
    a, r, y = math.radians(-(55 + 63 * e)), 3.10 - 0.55 * e, 1.75 - 0.40 * e
    p = [math.cos(a) * r, y, -0.10 + math.sin(a) * r]
    cam.update(dentro(p))
    mira.update(ostruzioni(p, BERSAGLIO_VOLO))
problemi += len(cam) + len(mira)
print(f"{'Spaccato fianco':18s} camera dentro: {sorted(cam) or 'libera':<12} "
      f"ostruzioni: {sorted(mira)[:3] or 'nessuna'}")
raise SystemExit(1 if problemi else 0)
