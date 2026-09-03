# -*- coding: utf-8 -*-
"""MOBILE_DEMO.stp -> MOBILE_DEMO.dwg con la ricetta collaudata
((command "_.IMPORT") + attesa conteggio stabile + esplosione blocchi)."""
import os
import time

import pythoncom
import pywintypes
import win32com.client

BASE = os.path.dirname(os.path.abspath(__file__))
STP = os.path.join(BASE, "MOBILE_DEMO.stp")
DWG = os.path.join(BASE, "MOBILE_DEMO.dwg")

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
    print("AutoCAD gia' aperto")
except Exception:
    acad = win32com.client.Dispatch("AutoCAD.Application")
    print("nuova sessione AutoCAD")
acad.Visible = True

for i in range(acad.Documents.Count):
    try:
        d = acad.Documents.Item(i)
        if d.Name.upper().startswith("MOBILE_DEMO"):
            d.Close(False)
            break
    except Exception:
        pass
if os.path.exists(DWG):
    os.remove(DWG)

doc = com_retry(lambda: acad.Documents.Add(), descr="nuovo disegno")
time.sleep(1)

def send(s):
    com_retry(lambda: doc.SendCommand(s), descr=s[:40])

def conta():
    return com_retry(lambda: doc.ModelSpace.Count, descr="Count")

send('(setvar "FILEDIA" 0)(setvar "CMDECHO" 0) ')
send(f'(command "_.IMPORT" "{fwd(STP)}") ')
print("IMPORT lanciato...")
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
print(f"import: {n} entita'")

ms = doc.ModelSpace
for giro in range(4):
    nn = conta()
    blocchi = []
    for i in range(nn):
        try:
            e = ms.Item(i)
            if "BlockReference" in e.EntityName:
                blocchi.append(e)
        except Exception:
            pass
    if not blocchi:
        break
    print(f"giro {giro+1}: esplodo {len(blocchi)} blocchi")
    for b in blocchi:
        try:
            b.Explode()
            b.Delete()
        except Exception as ex:
            print("  explode:", ex)
    time.sleep(1)

nn = conta()
tipi = {}
for i in range(nn):
    try:
        e = ms.Item(i)
        tipi[e.EntityName] = tipi.get(e.EntityName, 0) + 1
    except Exception:
        pass
print("finale:", tipi)

def testo(txt, x, y, h=40.0):
    pt = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x, y, 0.0))
    com_retry(lambda: ms.AddText(txt, pt, h))

testo("MOBILE_DEMO 900x560x2000 - composto DA ZERO col libro delle regole: spine 13/29, sistema 32, "
      "rafix 21, cerniere 71B3550 22.5/100 + BASETTE 175H3100 a 20/52, LEGRABOX M, BONE, REKORD, gioco 3", 0, -150)
testo("Blocchi FERRAMENTA_* coi codici dentro il modello - LISTA_FERRAMENTA.txt generata a fianco", 0, -260)

send('(setvar "FILEDIA" 1) ')
send("(command \"_.ZOOM\" \"_E\") ")
time.sleep(1)
com_retry(lambda: doc.SaveAs(DWG), descr="SaveAs")
print("SALVATO", DWG)
