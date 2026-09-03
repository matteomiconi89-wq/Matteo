# -*- coding: utf-8 -*-
"""MOBILE_DEMO.stp -> MOBILE_DEMO.dwg COI NOMI: ogni blocco importato viene
esploso e i suoi solidi finiscono su un LAYER che si chiama come il pezzo
(01_Fianco_SX, FERRAMENTA_CERNIERA_71B3550, ...) - convenzione NOMINASOLIDI.
Layer ferramenta colorati per famiglia."""
import os
import re
import time

import pythoncom
import pywintypes
import win32com.client

BASE = os.path.dirname(os.path.abspath(__file__))
STP = os.path.join(BASE, "MOBILE_DEMO.stp")
DWG = os.path.join(BASE, "MOBILE_DEMO.dwg")

COLORI = (("FERRAMENTA_CERNIERA", 1), ("FERRAMENTA_BASETTA", 30), ("FERRAMENTA_GUIDA", 5),
          ("FERRAMENTA_PIEDINO_BONE", 6), ("FERRAMENTA_PIEDINO_REKORD", 200),
          ("FERRAMENTA_RAFIX", 3), ("FERRAMENTA", 2))

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
layers = doc.Layers

def layer_di(nome):
    nome = re.sub(r'[<>/\\":;?*|=`]', "_", nome)[:250] or "PEZZO"
    try:
        ly = layers.Add(nome)
    except Exception:
        ly = layers.Item(nome)
    try:
        for pref, col in COLORI:
            if nome.upper().startswith(pref):
                ly.Color = col
                break
    except Exception:
        pass
    return nome

def refs_correnti():
    out = []
    for i in range(conta()):
        try:
            e = ms.Item(i)
            if "BlockReference" in e.EntityName:
                out.append(e)
        except Exception:
            pass
    return out

# giro 1: esplodi il contenitore esterno (senza nome utile)
esterni = refs_correnti()
print(f"contenitori esterni: {len(esterni)}")
for b in esterni:
    try:
        b.Explode()
        b.Delete()
    except Exception as ex:
        print("  explode esterno:", ex)
time.sleep(1)

# giro 2: ogni blocco figlio = un pezzo/ferramenta -> layer col suo nome
figli = refs_correnti()
print(f"blocchi pezzo: {len(figli)}")
n_ok = 0
for b in figli:
    try:
        nome = b.Name
        if nome.startswith("*"):
            try:
                nome = b.EffectiveName
            except Exception:
                pass
        ly = layer_di(nome)
        nuovi = b.Explode()
        for e in nuovi:
            try:
                e.Layer = ly
            except Exception:
                pass
        b.Delete()
        n_ok += 1
    except Exception as ex:
        print("  explode figlio:", ex)
time.sleep(1)

# eventuali blocchi residui annidati: esplodi mantenendo il layer del padre
for giro in range(3):
    resti = refs_correnti()
    if not resti:
        break
    print(f"residui giro {giro+1}: {len(resti)}")
    for b in resti:
        try:
            ly = b.Layer
            nuovi = b.Explode()
            for e in nuovi:
                try:
                    e.Layer = ly
                except Exception:
                    pass
            b.Delete()
        except Exception as ex:
            print("  explode residuo:", ex)

nn = conta()
per_layer = {}
for i in range(nn):
    try:
        e = ms.Item(i)
        per_layer[e.Layer] = per_layer.get(e.Layer, 0) + 1
    except Exception:
        pass
print(f"finale: {nn} entita' su {len(per_layer)} layer")
for ly, cnt in sorted(per_layer.items()):
    print(f"   {ly}: {cnt}")

def testo(txt, x, y, h=40.0):
    pt = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x, y, 0.0))
    com_retry(lambda: ms.AddText(txt, pt, h))

testo("MOBILE_DEMO - i NOMI stanno nei LAYER: pannelli 01_..07_, ante 08/09, "
      "ferramenta sui layer FERRAMENTA_* coi CODICI (cerniere rosse, basette arancio, guide blu, piedini magenta)", 0, -150)

send('(setvar "FILEDIA" 1) ')
send("(command \"_.ZOOM\" \"_E\") ")
time.sleep(1)
com_retry(lambda: doc.SaveAs(DWG), descr="SaveAs")
print("SALVATO", DWG)
