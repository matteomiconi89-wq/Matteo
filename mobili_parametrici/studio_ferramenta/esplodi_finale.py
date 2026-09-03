# -*- coding: utf-8 -*-
"""Esplode ricorsivamente i block reference (max 4 giri) finche' restano solo
3DSOLID + testi, poi salva. Accesso per indice, mai enumeratori."""
import time

import pythoncom
import pywintypes
import win32com.client

pythoncom.CoInitialize()
acad = win32com.client.GetActiveObject("AutoCAD.Application")

doc = None
for i in range(acad.Documents.Count):
    d = acad.Documents.Item(i)
    if d.Name.upper().startswith("PEZZI_DOMANDE"):
        doc = d
        break
if doc is None:
    raise RuntimeError("doc PEZZI_DOMANDE non trovato")

def com_retry(fn, tries=30, delay=1.0):
    last = None
    for _ in range(tries):
        try:
            return fn()
        except (pywintypes.com_error, AttributeError) as e:
            last = e
            time.sleep(delay)
    raise RuntimeError(f"COM: {last}")

ms = doc.ModelSpace
for giro in range(4):
    n = com_retry(lambda: ms.Count)
    da_esplodere = []
    for i in range(n):
        try:
            e = ms.Item(i)
            if "BlockReference" in e.EntityName:
                da_esplodere.append(e)
        except Exception:
            pass
    if not da_esplodere:
        break
    print(f"giro {giro+1}: esplodo {len(da_esplodere)} blocchi")
    for b in da_esplodere:
        try:
            b.Explode()
            b.Delete()
        except Exception as ex:
            print("  explode fallito:", ex)
    time.sleep(1)

n = com_retry(lambda: ms.Count)
tipi = {}
for i in range(n):
    try:
        e = ms.Item(i)
        tipi[e.EntityName] = tipi.get(e.EntityName, 0) + 1
    except Exception:
        tipi["?"] = tipi.get("?", 0) + 1
print(f"finale: {n} entita' -> {tipi}")

com_retry(lambda: doc.SendCommand("(command \"_.ZOOM\" \"_E\") "))
time.sleep(1)
com_retry(lambda: doc.Save())
print("SALVATO", doc.FullName)
