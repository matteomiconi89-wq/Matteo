# -*- coding: utf-8 -*-
"""Genera il reel FILIERA UN CLIC: voce edge-tts + card Pillow + ffmpeg."""
import os
import re
import asyncio
import subprocess
import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
OUT = r"C:\Users\User\Desktop\FILIERA_UN_CLIC"
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1920
CW, CH = 1620, 2880          # card sovracampionata per lo zoom morbido
VOCE = "it-IT-DiegoNeural"

SFONDO = (18, 16, 14)
ARANCIO = (255, 140, 66)
BIANCO = (245, 242, 238)
GRIGIO = (150, 145, 140)
VERDE = (110, 200, 120)

F_BLACK = r"C:\Windows\Fonts\seguibl.ttf"     # Segoe UI Black
F_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
F_REG = r"C:\Windows\Fonts\segoeui.ttf"
for f in (F_BLACK, F_BOLD, F_REG):
    if not os.path.exists(f):
        raise SystemExit(f"font mancante: {f}")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(dr, testo, fnt, maxw):
    righe, riga = [], ""
    for parola in testo.split():
        prova = (riga + " " + parola).strip()
        if dr.textlength(prova, font=fnt) <= maxw:
            riga = prova
        else:
            if riga:
                righe.append(riga)
            riga = parola
    if riga:
        righe.append(riga)
    return righe


def croce(dr, x, y, s, colore, w=16):
    dr.line([x, y, x + s, y + s], fill=colore, width=w)
    dr.line([x + s, y, x, y + s], fill=colore, width=w)


def spunta(dr, x, y, s, colore, w=18):
    dr.line([(x, y + 0.55 * s), (x + 0.38 * s, y + s),
             (x + 1.05 * s, y + 0.08 * s)], fill=colore, width=w,
            joint="curve")


def freccia_giu(dr, cx, y, s, colore):
    dr.polygon([(cx - s, y), (cx + s, y), (cx, y + 1.2 * s)], fill=colore)


def card_base():
    img = Image.new("RGB", (CW, CH), SFONDO)
    dr = ImageDraw.Draw(img)
    # venature discrete di fondo
    for i in range(0, CW, 108):
        dr.line([(i, 0), (i, CH)], fill=(24, 21, 18), width=2)
    # marchio in alto
    f = font(F_BOLD, 54)
    t = "FALEGNAME  DIGITALE"
    tw = dr.textlength(t, font=f)
    dr.text(((CW - tw) / 2, 150), t, font=f, fill=GRIGIO)
    dr.rectangle([CW / 2 - 90, 240, CW / 2 + 90, 252], fill=ARANCIO)
    return img, dr


def blocco_testo(dr, righe_spec, y):
    """righe_spec: lista (testo, font, colore, interlinea_extra)"""
    for testo, fnt, colore, extra in righe_spec:
        for riga in wrap(dr, testo, fnt, CW - 260):
            twl = dr.textlength(riga, font=fnt)
            dr.text(((CW - twl) / 2, y), riga, font=fnt, fill=colore)
            y += fnt.size * 1.18
        y += extra
    return y


def scena1():
    img, dr = card_base()
    blocco_testo(dr, [
        ("QUANTO CI METTI", font(F_BLACK, 150), BIANCO, 30),
        ("a mettere in macchina", font(F_BOLD, 96), GRIGIO, 10),
        ("UN MOBILE INTERO?", font(F_BLACK, 150), ARANCIO, 0),
    ], 780)
    return img


def scena2():
    img, dr = card_base()
    y = 560
    f = font(F_BOLD, 88)
    for voce in ("importare il 3D", "esplodere i pezzi",
                 "esportare i DXF", "togliere i doppioni",
                 "distinta e sezionatura", "programmare 2 macchine"):
        croce(dr, 250, y + 20, 72, (220, 80, 70))
        dr.text((400, y), voce, font=f, fill=BIANCO)
        y += 168
    y += 60
    fo = font(F_BLACK, 220)
    t = "ORE."
    dr.text(((CW - dr.textlength(t, font=fo)) / 2, y), t, font=fo, fill=ARANCIO)
    return img


def scena3():
    img, dr = card_base()
    blocco_testo(dr, [
        ("Io premo", font(F_BOLD, 100), GRIGIO, 6),
        ("UN BOTTONE.", font(F_BLACK, 170), BIANCO, 160),
        ("FILIERA", font(F_BLACK, 230), ARANCIO, 0),
        ("UN CLIC", font(F_BLACK, 230), ARANCIO, 90),
        ("dal disegno 3D ai programmi macchina. Da sola.",
         font(F_BOLD, 76), BIANCO, 0),
    ], 620)
    return img


def scena4():
    img, dr = card_base()
    tappe = ["STEP 3D del progettista", "DWG AutoCAD salvati",
             "DXF di OGNI pezzo", "PROGRAMMI UNICI (no doppioni)",
             "DISTINTA + SEZIONATURA", "TLF Master  |  MPRX Homag"]
    y = 460
    fb = font(F_BOLD, 78)
    for i, t in enumerate(tappe):
        box_h = 170
        colore = ARANCIO if i == len(tappe) - 1 else (44, 40, 36)
        testo_c = SFONDO if i == len(tappe) - 1 else BIANCO
        dr.rounded_rectangle([170, y, CW - 170, y + box_h], radius=34,
                             fill=colore)
        twl = dr.textlength(t, font=fb)
        dr.text(((CW - twl) / 2, y + (box_h - fb.size * 1.1) / 2), t,
                font=fb, fill=testo_c)
        y += box_h
        if i < len(tappe) - 1:
            freccia_giu(dr, CW / 2, y + 26, 46, ARANCIO)
            y += 130
    return img


def scena5():
    img, dr = card_base()
    y = 520
    fb = font(F_BOLD, 84)
    for voce in ("fori, tasche, aperture", "frontali uniti, fuga 3,2",
                 "programma girato per il retro",
                 "LAMATE che staccano i pezzi"):
        spunta(dr, 230, y + 18, 70, VERDE)
        for riga in wrap(dr, voce, fb, CW - 600):
            dr.text((380, y), riga, font=fb, fill=BIANCO)
            y += 130
        y += 60
    y += 70
    blocco_testo(dr, [("programmi macchina GIÀ FATTI",
                       font(F_BLACK, 108), ARANCIO, 0)], y)
    return img


def scena6():
    img, dr = card_base()
    blocco_testo(dr, [
        ("COLLAUDATA", font(F_BLACK, 160), BIANCO, 30),
        ("sui programmi VERI delle macchine", font(F_BOLD, 84), GRIGIO, 140),
        ("IDENTICA", font(F_BLACK, 200), VERDE, 10),
        ("AL 100%", font(F_BLACK, 200), VERDE, 0),
    ], 700)
    return img


def scena7():
    img, dr = card_base()
    blocco_testo(dr, [
        ("Selezioni i file.", font(F_BOLD, 96), BIANCO, 10),
        ("Premi AVVIA.", font(F_BOLD, 96), BIANCO, 10),
        ("Torni a fare il falegname.", font(F_BOLD, 96), ARANCIO, 180),
        ("FILIERA UN CLIC", font(F_BLACK, 150), BIANCO, 60),
        ("Scrivimi per provarla nella tua officina",
         font(F_BOLD, 72), GRIGIO, 0),
    ], 640)
    return img


SCENE = [
    (scena1, "Quanto ci metti a mettere in macchina un mobile intero?"),
    (scena2, "Importare il 3D, esplodere i pezzi, esportare i DXF, togliere "
             "i doppioni, fare la distinta... e programmare due macchine "
             "diverse. Ore."),
    (scena3, "Io premo un bottone. Si chiama: Filiera un Clic."),
    (scena4, "Dai file del progettista escono da soli i disegni, i DXF di "
             "ogni pezzo, i programmi unici senza doppioni, la distinta e "
             "la sezionatura."),
    (scena5, "E i programmi macchina sono già fatti: TLF per la Masterwood, "
             "MPRX per la Homag. Fori, tasche, e le lamate che staccano i "
             "frontali."),
    (scena6, "Collaudata pezzo per pezzo contro i programmi veri delle mie "
             "macchine: identici al cento per cento."),
    (scena7, "Tu selezioni i file, premi avvia... e torni a fare il "
             "falegname. Filiera un Clic, dal Falegname Digitale."),
]


async def genera_voci():
    for i, (_, testo) in enumerate(SCENE, 1):
        mp3 = os.path.join(OUT, f"voce{i}.mp3")
        if os.path.exists(mp3):
            continue                      # gia' generata
        await edge_tts.Communicate(testo, VOCE, rate="+6%").save(mp3)
        print("voce", i, "ok")


def durata_mp3(path):
    r = subprocess.run([FFMPEG, "-i", path, "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.findall(r"time=(\d+):(\d+):(\d+\.\d+)", r.stderr)
    hh, mm, ss = m[-1]
    return int(hh) * 3600 + int(mm) * 60 + float(ss)


def main():
    asyncio.run(genera_voci())
    pezzi = []
    copione = []
    for i, (fabbrica, testo) in enumerate(SCENE, 1):
        png = os.path.join(OUT, f"scena{i}.png")
        fabbrica().save(png)
        mp3 = os.path.join(OUT, f"voce{i}.mp3")
        dur = max(3.5, durata_mp3(mp3) + 1.0)
        frames = int(dur * 30)
        mp4 = os.path.join(OUT, f"scena{i}.mp4")
        vf = (f"zoompan=z='min(1.09,1+0.0009*on)':"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
              f"d={frames}:s={W}x{H}:fps=30")
        r = subprocess.run(
            [FFMPEG, "-y", "-loop", "1", "-framerate", "30", "-i", png,
             "-i", mp3,
             "-filter_complex",
             f"[0:v]{vf}[v];[1:a]adelay=350|350,apad[a]",
             "-map", "[v]", "-map", "[a]", "-t", f"{dur:.2f}",
             "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-pix_fmt", "yuv420p", "-r", "30",
             "-c:a", "aac", "-b:a", "192k", "-ar", "44100", mp4],
            capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr[-1500:])
            raise SystemExit(f"ffmpeg scena {i} fallito")
        pezzi.append(mp4)
        copione.append(f"SCENA {i}  ({dur:.1f}s)\n  {testo}\n")
        print(f"scena {i}: {dur:.1f}s ok")

    lista = os.path.join(OUT, "_lista.txt")
    with open(lista, "w", encoding="utf-8") as fh:
        for p in pezzi:
            fh.write(f"file '{p}'\n")
    finale = os.path.join(OUT, "FILIERA_UN_CLIC_reel.mp4")
    r = subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0",
                        "-i", lista, "-c", "copy", finale],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:])
        raise SystemExit("concat fallito")
    with open(os.path.join(OUT, "copione.txt"), "w", encoding="utf-8") as fh:
        fh.write("FILIERA UN CLIC - copione del reel\n\n" + "\n".join(copione))
    print("\nREEL PRONTO:", finale)
    print("durata totale:", f"{durata_mp3(finale):.1f}s")


if __name__ == "__main__":
    main()
