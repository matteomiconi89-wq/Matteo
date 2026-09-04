# -*- coding: utf-8 -*-
"""Voci corte del VIDEO V2 (versione da un minuto) con edge-tts / Diego.

I testi NON stanno qui: arrivano da fai_video_v2_filiera.SCENE, cosi' voce e
video non possono divergere. Da lanciare sul PC di casa, dove la rete verso
Microsoft e' aperta (in sessione remota risponde 403).

Uso:  py genera_voci_60s.py            -> voce01.mp3 .. voce10.mp3 qui accanto
      py genera_voci_60s.py C:\\cartella -> nella cartella indicata
"""
import os
import sys
import asyncio
import subprocess

import edge_tts
import imageio_ffmpeg

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(QUI))
from fai_video_v2_filiera import SCENE, VOCE, RATE, durata_media  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else QUI


async def genera():
    os.makedirs(OUT, exist_ok=True)
    for i, (_, _, testo) in enumerate(SCENE, 1):
        mp3 = os.path.join(OUT, f"voce{i:02d}.mp3")
        await edge_tts.Communicate(testo, VOCE, rate=RATE).save(mp3)
        print(f"voce{i:02d}.mp3  {durata_media(mp3):5.2f}s  {testo}")


def main():
    asyncio.run(genera())
    tot = sum(durata_media(os.path.join(OUT, f"voce{i:02d}.mp3"))
              for i in range(1, len(SCENE) + 1))
    print(f"\nparlato totale: {tot:.1f}s (il montaggio aggiunge le pause e "
          f"tiene il video sotto i 60s)")


if __name__ == "__main__":
    main()
