# -*- coding: utf-8 -*-
"""STEP->DWG con la ricetta collaudata di step_dxf_definitivi:
(command "_.IMPORT" ...) + attesa conteggio stabile. Chiude il tentativo
precedente (solo il doc PEZZI_DOMANDE), importa, etichetta, salva."""
import os
import time

import pythoncom
import pywintypes
import win32com.client

BASE = os.path.dirname(os.path.abspath(__file__))
STP = os.path.join(BASE, "PEZZI_DOMANDE.stp")
DWG = os.path.join(BASE, "PEZZI_DOMANDE.dwg")

def fwd(p):
    return p.replace("\\", "/")

def com_retry(fn, tries=40, delay=1.0, descr=""):
    last = None
    for _ in range(tries):
        try:
            return fn()
        except (pywintypes.com_error, AttributeError) as e:
            last = e
            time.sleep(delay)
    raise RuntimeError(f"AutoCAD occupato ({descr}): {last}")

pythoncom.CoInitialize()
try:
    acad = win32com.client.GetActiveObject("AutoCAD.Application")
    print("AutoCAD gia' aperto: uso la sessione esistente")
except Exception:
    acad = win32com.client.Dispatch("AutoCAD.Application")
    print("Avvio nuova sessione AutoCAD")
acad.Visible = True

# chiudi SOLO il mio tentativo precedente, se ancora aperto
for d in acad.Documents:
    try:
        if d.Name.upper().startswith("PEZZI_DOMANDE"):
            d.Close(False)
            print("chiuso il tentativo precedente")
            break
    except Exception:
        pass

if os.path.exists(DWG):
    os.remove(DWG)

doc = com_retry(lambda: acad.Documents.Add(), descr="nuovo disegno")
time.sleep(1)

def send(s, descr=""):
    com_retry(lambda: doc.SendCommand(s), descr=descr or s[:40])

def conta():
    return com_retry(lambda: doc.ModelSpace.Count, descr="Count")

send('(setvar "FILEDIA" 0)(setvar "CMDECHO" 0) ')
send(f'(command "_.IMPORT" "{fwd(STP)}") ')
print("IMPORT lanciato, attendo la traduzione in background...")
t0 = time.time()
while True:
    n = conta()
    if n > 0:
        break
    if time.time() - t0 > 600:
        raise RuntimeError("IMPORT non terminato")
    time.sleep(2)
stabile = 0
while stabile < 3:
    time.sleep(2)
    m = conta()
    if m == n:
        stabile += 1
    else:
        n, stabile = m, 0
print(f"import completato: {n} entita' in {time.time()-t0:.0f}s")

ms = doc.ModelSpace

def testo(txt, x, y, h=50.0):
    pt = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x, y, 0.0))
    com_retry(lambda: ms.AddText(txt, pt, h), descr="AddText")

testo("V027 (18x580x2100): D12x60 nel filo basso (50 dai bordi) + file D5 passo 20 + D6x4 a 52 dal filo - COSA SONO?", 0, -180)
testo("Q005 pianetto Q sopra i cassetti (700x446x18): 2+2 quadrati di 4 fori D5x13 lato 32 - PIASTRINE DI COSA?", 0, -300)
testo("AC026 (120x18x818): D6x4 superficiali - RIFERIMENTI/CENTRATORI?", 0, -420)

send('(setvar "FILEDIA" 1) ')
send("(command \"_.ZOOM\" \"_E\") ")
time.sleep(1)
com_retry(lambda: doc.SaveAs(DWG), descr="SaveAs")
print("SALVATO", DWG)
