# -*- coding: utf-8 -*-
"""DOPPIO CLIC QUI per fare il video FILIERA UN CLIC V2.

Basta questo file. Se il resto del progetto non c'e', se lo scarica da solo
da GitHub; poi installa i pacchetti che mancano, monta il video e apre la
cartella dove l'ha messo. La finestra nera resta aperta a fine lavoro, cosi'
si legge cosa e' successo.

Se il doppio clic apre il Blocco note: tasto destro sul file -> Apri con ->
Python.
"""
import os
import sys
import subprocess
import urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))
RAMO = "claude/voci-v2-diego"
GITHUB = f"https://raw.githubusercontent.com/matteomiconi89-wq/Matteo/{RAMO}/"

# nome del modulo da importare -> nome del pacchetto da installare
SERVE = {
    "numpy": "numpy",
    "PIL": "pillow",
    "imageio_ffmpeg": "imageio-ffmpeg",
    "edge_tts": "edge-tts",          # la voce di Diego
    "pypdfium2": "pypdfium2",        # per la tavola vera dentro al video
}

# file del progetto che servono al video, col posto in cui devono stare
PEZZI = [
    "business_reel/fai_video_v2_filiera.py",
    "Viste/viste_cliente.py",
]


def manca(modulo):
    try:
        __import__(modulo)
        return False
    except ImportError:
        return True


def installa(pacchetti):
    print("installo:", ", ".join(pacchetti))
    if subprocess.run([sys.executable, "-m", "pip", "install",
                       *pacchetti]).returncode != 0:
        raise SystemExit("installazione fallita: controlla la connessione")


def scarica_progetto():
    """Se il video non e' qui accanto, tira giu' i sorgenti da GitHub.
    Torna la cartella da cui far partire il montaggio."""
    if os.path.exists(os.path.join(QUI, "fai_video_v2_filiera.py")):
        return QUI                                   # gia' dentro al progetto

    radice = os.path.join(QUI, "FILIERA_UN_CLIC_APP")
    for pezzo in PEZZI:
        dove = os.path.join(radice, *pezzo.split("/"))
        if os.path.exists(dove):
            continue
        os.makedirs(os.path.dirname(dove), exist_ok=True)
        print("scarico", pezzo)
        urllib.request.urlretrieve(GITHUB + pezzo, dove)
    return os.path.join(radice, "business_reel")


def main():
    print("=" * 60)
    print(" FILIERA UN CLIC - VIDEO V2")
    print("=" * 60)
    print("python:", sys.version.split()[0])

    da_mettere = [pac for mod, pac in SERVE.items() if manca(mod)]
    if da_mettere:
        installa(da_mettere)

    cartella = scarica_progetto()
    sys.path.insert(0, cartella)
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
