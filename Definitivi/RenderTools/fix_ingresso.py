# -*- coding: utf-8 -*-
"""Chirurgia post-produzione mobile ingresso v4:
1) vista APERTA: rimozione anta inventata a dx della libreria (clone di parete+pavimento)
2) entrambe le viste: warp differenziale a bande verticali -> H/L ~1,03 e sezioni 600/900/600
Le bande strizzano le ante lisce (invisibile) e risparmiano capi appesi e libri."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image

DIR = r"C:\Users\User\Dropbox\STEFANO\Matteo\RENDER_MANUS\26-A011_mobile_ingresso"

def rimuovi_anta(im):
    """Clona la parete (e il pavimento) sopra l'anta inventata: dest x1725-1802, src x1815-1892."""
    im = im.copy()
    W, H = im.size
    x0d, x1d = 1725, 1802
    dx = 1815 - x0d + 0  # offset sorgente
    src = im.crop((x0d + 90, 295, x1d + 90, 1330))  # striscia pulita 90px piu' a destra
    larg = x1d - x0d
    alto = 1330 - 295
    # correzione luminanza: rapporto tra medie su righe pulite (muro sopra l'anta)
    zona_dst = im.crop((x0d, 200, x1d, 290)).convert("L")
    zona_src = im.crop((x0d + 90, 200, x1d + 90, 290)).convert("L")
    md = sum(zona_dst.getdata()) / (larg * 90)
    ms = sum(zona_src.getdata()) / (larg * 90)
    k = md / ms if ms else 1.0
    src = src.point(lambda v: min(255, int(v * k)))
    # feather orizzontale ai bordi (12 px)
    from PIL import ImageDraw
    mask = Image.new("L", (larg, alto), 255)
    dr = ImageDraw.Draw(mask)
    for i in range(12):
        a = int(255 * i / 12)
        dr.line([(i, 0), (i, alto)], fill=a)
        dr.line([(larg - 1 - i, 0), (larg - 1 - i, alto)], fill=a)
    im.paste(src, (x0d, 295), mask)
    return im

def warp(im, bande):
    """bande: lista (x_in0, x_in1, larghezza_out). Le x_out si accumulano da 0.
    Ogni banda diventa una strip del mesh a tutta altezza."""
    W, H = im.size
    mesh = []
    xo = 0.0
    for (xi0, xi1, lo) in bande:
        xo0, xo1 = xo, xo + lo
        mesh.append((
            (int(round(xo0)), 0, int(round(xo1)), H),
            (xi0, 0.0, xi0, float(H), xi1, float(H), xi1, 0.0),
        ))
        xo = xo1
    tot = int(round(xo))
    out = im.transform((tot, H), Image.MESH, mesh, resample=Image.BICUBIC)
    if tot != W:
        out = out.resize((W, H), Image.LANCZOS)  # non dovrebbe servire: bande tarate su W
    return out

# ---------- VISTA CHIUSA ----------
# giunzioni misurate: 827 | 1046 | 1094 | (maniglie 1250-1345) | 1510 | 1743
# target: mobile 808 px centrato -> parte a (2560-808)/2 = 876
chiuso_bande = [
    (0,    827,  876),            # muro sx (stretch x1.059)
    (827,  1046, 231),            # scarpiera x1.055 -> 28.6%
    (1046, 1094, 31),             # montante LED x0.65 (piu' slim, come CAD)
    (1094, 1250, 114),            # anta 1 liscia x0.73
    (1250, 1345, 81),             # zona maniglie x0.85 (ferramenta poco distorta)
    (1345, 1510, 120),            # anta 2 liscia x0.73
    (1510, 1743, 231),            # libreria x0.99 (libri intatti) -> 28.6%
    (1743, 2560, 876),            # muro dx
]

# ---------- VISTA APERTA ----------
# giunzioni: anta scarpe 710-819 | vano scarpe 819-1045 | montante 1045-1127 |
# vano guardaroba 1127-1470 | anta dx 1470-1523 | libreria 1523-1735 | muro (anta rimossa)
# target carcassa 795 px centrata -> carcassa a (2560-795)/2 = 882; anta scarpe subito prima
aperto_bande = [
    (0,    710,  777),            # muro sx (stretch, ingloba lo spazio liberato)
    (710,  819,  105),            # anta scarpe aperta ~rigida x0.96
    (819,  1045, 220),            # vano scarpiera x0.97 (scarpe quasi intatte)
    (1045, 1055, 7),              # bordo montante
    (1055, 1090, 30),             # pannello domotica + lama LED x0.86 (leggibile)
    (1090, 1127, 23),             # sliver anta sx ripiegata x0.62
    (1127, 1470, 295),            # vano guardaroba x0.86 (capi appena piu' slanciati)
    (1470, 1523, 48),             # anta dx guardaroba x0.90
    (1523, 1735, 172),            # libreria x0.81 (dorsi libri: larghezza non canonica)
    (1735, 2560, 883),            # muro dx (anta inventata gia' rimossa)
]

if __name__ == "__main__":
    im_c = Image.open(DIR + r"\render_INGRESSO_v4_chiuso.png").convert("RGB")
    out_c = warp(im_c, chiuso_bande)
    out_c.save(DIR + r"\render_INGRESSO_FINALE_chiuso.png")
    print(f"chiuso: {out_c.size}")

    im_a = Image.open(DIR + r"\render_INGRESSO_v4_aperto.png").convert("RGB")
    im_a = rimuovi_anta(im_a)
    im_a.save(DIR + r"\_v4_aperto_senza_anta.png")
    out_a = warp(im_a, aperto_bande)
    out_a.save(DIR + r"\render_INGRESSO_FINALE_aperto.png")
    print(f"aperto: {out_a.size}")
