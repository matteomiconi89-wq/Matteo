# -*- coding: utf-8 -*-
"""Disegna le proiezioni ortogonali (fronte / pianta / laterale) di un mobile
descritto da una spec JSON con pannelli box + un JSON di fori. Nessun AutoCAD.

Uso: py render_mobile.py <spec.json> <fori.json> <out.png> [titolo]
"""
import json
import sys

from PIL import Image, ImageDraw, ImageFont

COLORI = {
    "CERA": (196, 168, 120), "OPACO": (168, 168, 172), "VETRO": (150, 200, 215),
    "LACC": (232, 230, 222), "BVN": (105, 105, 110), "NOB": (215, 215, 205),
}


def colore(mat):
    u = (mat or "").upper()
    for k, c in COLORI.items():
        if k in u:
            return c
    return (180, 180, 180)


def font(sz):
    for n in ("arial.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(n, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    spec = spec.get("result", spec)
    fori = []
    if len(sys.argv) > 2 and sys.argv[2] not in ("-", "none"):
        try:
            fori = json.load(open(sys.argv[2], encoding="utf-8")).get("fori", [])
        except Exception:
            fori = []
    out = sys.argv[3]
    titolo = sys.argv[4] if len(sys.argv) > 4 else spec.get("nome", "")

    pan = spec["pannelli"]
    L = max(p["box"][0][1] for p in pan)
    P = max(p["box"][1][1] for p in pan)
    H = max(p["box"][2][1] for p in pan)
    zmin = min(p["box"][2][0] for p in pan)

    MARG, GAP, TOP = 70, 90, 90
    scala = min(1500.0 / (L + P), 900.0 / max(H - zmin, P))
    W = int(L * scala) + GAP + int(P * scala) + 2 * MARG
    Ht = int((H - zmin) * scala) + int(P * scala) + GAP + TOP + MARG
    img = Image.new("RGB", (W, Ht), (250, 250, 248))
    d = ImageDraw.Draw(img)
    f12, f16, f22 = font(13), font(17), font(24)

    d.text((MARG, 24), titolo[:110], fill=(20, 20, 20), font=f22)
    d.text((MARG, 56), "ingombro %.0f x %.0f x h %.0f mm  ·  %d pannelli  ·  %d fori"
           % (L, P, H, len(pan), len(fori)), fill=(90, 90, 90), font=f16)

    # --- FRONTE: X orizzontale, Z verticale (origine in basso a sx) ---
    ox, oy = MARG, TOP + int((H - zmin) * scala)

    def fx(x):
        return ox + x * scala

    def fz(z):
        return oy - (z - zmin) * scala

    for p in sorted(pan, key=lambda q: -q["box"][1][0]):
        b = p["box"]
        c = colore(p["materiale"])
        d.rectangle([fx(b[0][0]), fz(b[2][1]), fx(b[0][1]), fz(b[2][0])],
                    fill=c, outline=(60, 60, 60))
    d.text((ox, oy + 8), "PROSPETTO FRONTE", fill=(20, 20, 20), font=f16)

    # fori visibili di fronte (asse Y)
    for h in fori:
        if abs(h["dir"][1]) > 0.5:
            x, z = h["base"][0], h["base"][2]
            r = max(1.5, h["dia"] / 2.0 * scala)
            d.ellipse([fx(x) - r, fz(z) - r, fx(x) + r, fz(z) + r],
                      outline=(200, 30, 30), width=2)

    # --- PIANTA: X orizzontale, Y verticale (sotto il fronte) ---
    py0 = oy + 40
    d.text((ox, py0 + int(P * scala) + 10), "PIANTA (fronte in basso)",
           fill=(20, 20, 20), font=f16)

    def pyf(y):
        return py0 + y * scala

    for p in sorted(pan, key=lambda q: -q["box"][2][0]):
        b = p["box"]
        d.rectangle([fx(b[0][0]), pyf(b[1][0]), fx(b[0][1]), pyf(b[1][1])],
                    fill=colore(p["materiale"]), outline=(60, 60, 60))

    # --- LATERALE: Y orizzontale, Z verticale (a destra del fronte) ---
    lx = MARG + int(L * scala) + GAP

    def sx(y):
        return lx + y * scala

    for p in sorted(pan, key=lambda q: q["box"][0][0]):
        b = p["box"]
        d.rectangle([sx(b[1][0]), fz(b[2][1]), sx(b[1][1]), fz(b[2][0])],
                    fill=colore(p["materiale"]), outline=(60, 60, 60))
    d.text((lx, oy + 8), "SEZIONE LATERALE (fronte a sinistra)", fill=(20, 20, 20), font=f16)

    # legenda materiali
    ly = py0 + int(P * scala) + 40
    mats = []
    for p in pan:
        if p["materiale"] not in mats:
            mats.append(p["materiale"])
    for i, mm in enumerate(mats[:8]):
        yy = ly + i * 22
        d.rectangle([MARG, yy, MARG + 26, yy + 14], fill=colore(mm), outline=(60, 60, 60))
        d.text((MARG + 34, yy), mm[:70], fill=(40, 40, 40), font=f12)

    img.save(out)
    print("scritto", out, img.size)


if __name__ == "__main__":
    main()
