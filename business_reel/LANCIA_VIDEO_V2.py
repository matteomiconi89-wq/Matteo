# -*- coding: utf-8 -*-
"""DOPPIO CLIC QUI per fare il video FILIERA UN CLIC V2.

Fa tutto da solo: controlla i pacchetti che servono, li installa se mancano,
monta il video e apre la cartella dove l'ha messo. La finestra nera resta
aperta alla fine, cosi' si legge cosa e' successo.

Se il doppio clic apre il Blocco note invece di eseguirlo: tasto destro sul
file -> Apri con -> Python.
"""
import os
import sys
import subprocess

QUI = os.path.dirname(os.path.abspath(__file__))

# nome del modulo da importare -> nome del pacchetto da installare
SERVE = {
    "numpy": "numpy",
    "PIL": "pillow",
    "imageio_ffmpeg": "imageio-ffmpeg",
    "edge_tts": "edge-tts",          # la voce di Diego
}


def manca(modulo):
    try:
        __import__(modulo)
        return False
    except ImportError:
        return True


def installa(pacchetti):
    print("installo:", ", ".join(pacchetti))
    r = subprocess.run([sys.executable, "-m", "pip", "install", *pacchetti])
    if r.returncode != 0:
        raise SystemExit("installazione fallita: controlla la connessione")


def main():
    print("=" * 60)
    print(" FILIERA UN CLIC - VIDEO V2")
    print("=" * 60)
    print("python:", sys.version.split()[0])

    da_mettere = [pacchetto for modulo, pacchetto in SERVE.items()
                  if manca(modulo)]
    if da_mettere:
        installa(da_mettere)

    sys.path.insert(0, QUI)
    import fai_video_v2_filiera as video

    video.main()

    print("\nla cartella e':", video.OUT)
    if os.name == "nt":
        try:
            os.startfile(video.OUT)          # apre Esplora file sul risultato
        except Exception:
            pass


if __name__ == "__main__":
    try:
        main()
    except SystemExit as ex:
        print("\nFERMATO:", ex)
    except Exception as ex:
        import traceback
        traceback.print_exc()
        print("\nERRORE:", ex)
    try:
        input("\nPremi INVIO per chiudere questa finestra...")
    except EOFError:
        pass
