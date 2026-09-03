# -*- coding: utf-8 -*-
"""
Avvia la "Chiamata Numeri" da un mini server locale (solo sul PC, niente internet).
Serve a far caricare correttamente i file audio della voce neurale, cosa che con
il doppio clic su file:// a volte Edge blocca (e fa partire la voce robotica).

Doppio clic su "Avvia Cucina.bat"  (oppure:  py avvia.py)
Per fermare: chiudi questa finestra nera.
"""
import http.server, socketserver, webbrowser, os, subprocess, threading

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
PAGE = "chiamata_numeri.html"

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")  # niente cache: sempre l'ultima versione
        super().end_headers()
    def log_message(self, *a):
        pass  # finestra pulita

def crea_server():
    for porta in range(8000, 8050):
        try:
            return socketserver.TCPServer(("127.0.0.1", porta), Handler), porta
        except OSError:
            continue
    raise SystemExit("Nessuna porta libera tra 8000 e 8049.")

httpd, PORTA = crea_server()
URL = f"http://127.0.0.1:{PORTA}/{PAGE}"

def apri_browser():
    # Edge in modalita' app (finestra pulita, senza barre) se disponibile
    for edge in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                 r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
        if os.path.exists(edge):
            subprocess.Popen([edge, f"--app={URL}", "--start-fullscreen"])
            return
    webbrowser.open(URL)  # altrimenti il browser predefinito

threading.Timer(1.0, apri_browser).start()
print("=" * 52)
print("  CHIAMATA NUMERI  -  server attivo")
print("  Indirizzo:", URL)
print()
print("  Lascia aperta questa finestra durante la sagra.")
print("  Per CHIUDERE il programma: chiudi questa finestra.")
print("=" * 52)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
