# -*- coding: utf-8 -*-
"""Importa PEZZI_DOMANDE.stp in un NUOVO disegno AutoCAD (COM, sessione esistente
se c'e', senza chiudere nulla), etichetta i 3 pezzi e salva PEZZI_DOMANDE.dwg."""
import os
import time

import pythoncom
import win32com.client

BASE = os.path.dirname(os.path.abspath(__file__))
STP = os.path.join(BASE, "PEZZI_DOMANDE.stp")
DWG = os.path.join(BASE, "PEZZI_DOMANDE.dwg")

pythoncom.CoInitialize()
try:
    acad = win32com.client.GetActiveObject("AutoCAD.Application")
    print("AutoCAD gia' aperto: uso la sessione esistente")
except Exception:
    acad = win32com.client.Dispatch("AutoCAD.Application")
    print("Avvio nuova sessione AutoCAD")
acad.Visible = True

doc = acad.Documents.Add()
time.sleep(2)

def conta_solidi():
    n = 0
    try:
        for e in doc.ModelSpace:
            if "3dSolid" in e.EntityName or "3DSolid" in e.EntityName:
                n += 1
    except Exception:
        pass
    return n

# import STEP (gira in background: aspetto che compaiano i 3 solidi)
doc.SendCommand('(setvar "FILEDIA" 0) ')
doc.SendCommand('_-IMPORT\n"{}"\n'.format(STP.replace("\\", "/")))
print("IMPORT lanciato, attendo i solidi...")
t0 = time.time()
n = 0
while time.time() - t0 < 240:
    time.sleep(3)
    n = conta_solidi()
    if n >= 3:
        break
print(f"solidi in modello: {n} dopo {time.time()-t0:.0f}s")
doc.SendCommand('(setvar "FILEDIA" 1) ')

ms = doc.ModelSpace


def testo(txt, x, y, h=50.0):
    pt = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x, y, 0.0))
    ms.AddText(txt, pt, h)

testo("V027 (18x580x2100): D12x60 nel filo basso (50 dai bordi) + file D5 passo 20 + D6x4 a 52 dal filo - COSA SONO?", 0, -180)
testo("Q005 pianetto Q sopra i cassetti (700x446x18): 2+2 quadrati di 4 fori D5x13 lato 32 - PIASTRINE DI COSA?", 0, -300)
testo("AC026 (120x18x818): D6x4 superficiali - RIFERIMENTI/CENTRATORI?", 0, -420)

doc.SendCommand("_ZOOM\n_E\n")
time.sleep(1)
try:
    doc.SaveAs(DWG)
    print("SALVATO", DWG)
except Exception as ex:
    print("ERRORE SaveAs:", ex)
