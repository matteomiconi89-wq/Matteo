#!/usr/bin/env python3
"""Collaudo numerico di un mondo Marble contro il render sorgente.

Uso:
    python3 collaudo_marble.py pano_equirettangolare.png render_sorgente.png

Perche' cosi': il pano e' equirettangolare e il render prospettico — il confronto
diretto da' correlazioni ~0,2 anche quando il mondo e' giusto. Quindi PRIMA si
riproietta il pano in prospettiva (proiezione gnomonica, fov ~55°, yaw/pitch 0 =
il punto di partenza del mondo), POI si correla col render.

Verdetto: correlazione >= 0,60 al centro = PROMOSSO (il mondo parte dal render
approvato). 0,45-0,60 = riserva, sotto 0,45 = bocciato. Caso collaudato il
02/09/2026 (cucina 26-A011): 0,701 = PROMOSSO. Resta l'occhio del falegname.
Richiede: pip install pillow numpy
"""
import sys

import numpy as np
from PIL import Image


def prospettiva(pano, fov_gradi=55, yaw=0.0, pitch=0.0, w=960, h=540):
    """Ritaglio prospettico (gnomonico) dall'equirettangolare."""
    pw, ph = pano.shape[1], pano.shape[0]
    fov = np.radians(fov_gradi)
    fx = (w / 2) / np.tan(fov / 2)
    xs, ys = np.meshgrid(np.arange(w) - w / 2, np.arange(h) - h / 2 * (h / w) * (w / h))
    ys = (np.arange(h) - h / 2)[:, None] * np.ones((1, w))
    z = np.full_like(xs, fx, dtype=float)
    v = np.stack([xs, ys, z], -1)
    v /= np.linalg.norm(v, axis=-1, keepdims=True)
    cp, sp = np.cos(pitch), np.sin(pitch)
    y2 = v[..., 1] * cp - v[..., 2] * sp
    z2 = v[..., 1] * sp + v[..., 2] * cp
    cy, sy = np.cos(yaw), np.sin(yaw)
    x3 = v[..., 0] * cy + z2 * sy
    z3 = -v[..., 0] * sy + z2 * cy
    lon = np.arctan2(x3, z3)
    lat = np.arcsin(np.clip(y2, -1, 1))
    px = ((lon / (2 * np.pi) + 0.5) * pw).astype(int) % pw
    py = np.clip(((lat / np.pi + 0.5) * ph).astype(int), 0, ph - 1)
    return pano[py, px]


def ncc(a, b):
    a = a.astype(float).mean(-1)
    b = b.astype(float).mean(-1)
    a -= a.mean()
    b -= b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()))


def main(pano_png, render_png):
    pano = np.asarray(Image.open(pano_png).convert('RGB'))
    render = np.asarray(Image.open(render_png).convert('RGB').resize((960, 540)))
    migliore = (-1.0, None)
    # piccolo ventaglio attorno al centro: il frame 0 del mondo puo' essere ruotato di poco
    for fov in (50, 55, 60):
        for yaw in (-0.1, 0.0, 0.1):
            for pitch in (-0.05, 0.0, 0.05):
                vista = prospettiva(pano, fov, yaw, pitch)
                c = ncc(vista, render)
                if c > migliore[0]:
                    migliore = (c, (fov, yaw, pitch))
    c, (fov, yaw, pitch) = migliore
    verdetto = 'PROMOSSO' if c >= 0.60 else ('RISERVA' if c >= 0.45 else 'BOCCIATO')
    print(f'correlazione massima {c:.3f} a fov {fov}°, yaw {yaw:+.2f}, pitch {pitch:+.2f} → {verdetto}')
    print('(soglie: ≥0,60 promosso · 0,45–0,60 riserva · <0,45 bocciato; poi occhio del falegname)')
    return 0 if c >= 0.60 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
