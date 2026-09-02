#!/usr/bin/env python3
"""Montaggio del tour video stile Abitativo: card + clip con targhette + dissolvenze.

Uso:
    python3 monta_tour.py progetto.json

progetto.json:
{
  "titolo": "DINO CHIESA",
  "sottotitolo": "Appartamento su ruote — tour virtuale",
  "clips": [ {"file": "clip_cucina.mp4", "targhetta": "CUCINA", "sotto": "colonne + basi, gola LED"}, ... ],
  "outro_qr": "QR_tour.png",            // opzionale: QR alla demo camminabile
  "outro_testo": "Cammina tu stesso nel progetto",
  "out": "TOUR_COMMESSA.mp4",
  "fps": 24, "w": 1280, "h": 720, "dissolvenza": 0.6, "durata_card": 4
}

Trappole gia' pagate (02/09/2026):
- il binario ffmpeg di imageio-ffmpeg NON ha drawtext -> testi come PNG (PIL) + overlay;
- catena xfade: l'offset cresce di (durata clip precedente - dissolvenza) a ogni anello;
- audio Veo nativo non collaudabile -> si butta ('-an'): il tour esce MUTO, dirlo in consegna.
Richiede: pip install pillow imageio-ffmpeg (ffprobe non serve: durate lette con imageio).
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FF = None
try:
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FF = 'ffmpeg'

FONT_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_R = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def font(path, dim):
    try:
        return ImageFont.truetype(path, dim)
    except OSError:
        return ImageFont.load_default()


def durata(video):
    out = subprocess.run([FF, '-i', str(video)], capture_output=True, text=True).stderr
    for riga in out.splitlines():
        if 'Duration:' in riga:
            hh, mm, ss = riga.split('Duration:')[1].split(',')[0].strip().split(':')
            return int(hh) * 3600 + int(mm) * 60 + float(ss)
    raise RuntimeError(f'durata non letta: {video}')


def card(testo1, testo2, w, h, qr=None, colore=(24, 26, 30)):
    im = Image.new('RGB', (w, h), colore)
    dr = ImageDraw.Draw(im)
    f1, f2 = font(FONT_B, h // 9), font(FONT_R, h // 22)
    y = h // 2 - h // 8 if not qr else h // 5
    for testo, f, dy in ((testo1, f1, 0), (testo2, f2, h // 7)):
        if not testo:
            continue
        box = dr.textbbox((0, 0), testo, font=f)
        dr.text(((w - box[2]) // 2, y + dy), testo, font=f, fill=(240, 238, 232))
    dr.line((w // 2 - w // 10, y + h // 5, w // 2 + w // 10, y + h // 5), fill=(198, 146, 84), width=4)
    if qr and Path(qr).exists():
        q = Image.open(qr).convert('RGB').resize((h // 3, h // 3))
        im.paste(q, ((w - q.width) // 2, h - q.height - h // 10))
    return im


def targhetta(titolo, sotto, w, h):
    """Fascia bassa semitrasparente con nome stanza: PNG RGBA da mettere in overlay."""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    fascia_h = h // 7
    y0 = h - fascia_h - h // 18
    dr.rectangle((0, y0, w // 2 + w // 8, y0 + fascia_h), fill=(16, 18, 22, 200))
    dr.rectangle((0, y0, w // 90, y0 + fascia_h), fill=(198, 146, 84, 255))
    f1, f2 = font(FONT_B, fascia_h // 2), font(FONT_R, fascia_h // 4)
    dr.text((w // 30, y0 + fascia_h // 8), titolo, font=f1, fill=(245, 243, 238, 255))
    if sotto:
        dr.text((w // 30, y0 + fascia_h - fascia_h // 3), sotto, font=f2, fill=(200, 198, 190, 255))
    return im


def main(percorso):
    p = json.loads(Path(percorso).read_text())
    w, h = p.get('w', 1280), p.get('h', 720)
    fps, diss, dcard = p.get('fps', 24), p.get('dissolvenza', 0.6), p.get('durata_card', 4)
    lavoro = Path(percorso).parent / '_montaggio'
    lavoro.mkdir(exist_ok=True)

    card('  ' + p.get('titolo', 'TOUR') + '  ', p.get('sottotitolo', ''), w, h).save(lavoro / 'card_in.png')
    card(p.get('titolo', ''), p.get('outro_testo', ''), w, h, qr=p.get('outro_qr')).save(lavoro / 'card_out.png')
    for nome, png in (('seg_in.mp4', 'card_in.png'), ('seg_out.mp4', 'card_out.png')):
        subprocess.run([FF, '-y', '-loop', '1', '-i', str(lavoro / png), '-t', str(dcard),
                        '-r', str(fps), '-pix_fmt', 'yuv420p', '-an', str(lavoro / nome)],
                       check=True, capture_output=True)

    segmenti = [str(lavoro / 'seg_in.mp4')]
    for i, c in enumerate(p['clips']):
        tpng = lavoro / f'targa_{i}.png'
        targhetta(c.get('targhetta', ''), c.get('sotto', ''), w, h).save(tpng)
        seg = lavoro / f'seg_{i}.mp4'
        dclip = durata(c['file'])
        # targhetta visibile da 0,6 s a (fine - 0,6 s): non lotta con le dissolvenze
        subprocess.run([FF, '-y', '-i', c['file'], '-i', str(tpng), '-filter_complex',
                        f"[0:v]scale={w}:{h},fps={fps}[v];"
                        f"[v][1:v]overlay=0:0:enable='between(t,0.6,{dclip - 0.6:.2f})'[vo]",
                        '-map', '[vo]', '-an', '-pix_fmt', 'yuv420p', str(seg)],
                       check=True, capture_output=True)
        segmenti.append(str(seg))
    segmenti.append(str(lavoro / 'seg_out.mp4'))

    durate = [durata(s) for s in segmenti]
    ing = sum((['-i', s] for s in segmenti), [])
    filtro, off, prec = [], 0.0, '[0:v]'
    for i in range(1, len(segmenti)):
        off += durate[i - 1] - diss
        uscita = f'[x{i}]' if i < len(segmenti) - 1 else '[vf]'
        filtro.append(f'{prec}[{i}:v]xfade=transition=fade:duration={diss}:offset={off:.3f}{uscita}')
        prec = f'[x{i}]'
    subprocess.run([FF, '-y', *ing, '-filter_complex', ';'.join(filtro), '-map', '[vf]',
                    '-an', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', p['out']],
                   check=True, capture_output=True)
    print(f"{p['out']}: {durata(p['out']):.1f} s, {Path(p['out']).stat().st_size/1e6:.1f} MB (muto: audio Veo scartato)")


if __name__ == '__main__':
    main(sys.argv[1])
