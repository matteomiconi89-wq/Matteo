# -*- coding: utf-8 -*-
"""Esplode il blocco dell'import nel doc PEZZI_DOMANDE aperto, verifica i 3 solidi,
risalva. Non tocca gli altri disegni."""
import time

import pythoncom
import pywintypes
import win32com.client

pythoncom.CoInitialize()
acad = win32com.client.GetActiveObject("AutoCAD.Application")

doc = None
for d in acad.Documents:
    if d.Name.upper().startswith("PEZZI_DOMANDE"):
        doc = d
        break
if doc is None:
    raise RuntimeError("doc PEZZI_DOMANDE non trovato tra i disegni aperti")

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
blocchi = []
for e in ms:
    if "BlockReference" in e.EntityName:
        blocchi.append(e)
print(f"block reference trovati: {len(blocchi)}")
for b in blocchi:
    try:
        b.Explode()
        b.Delete()
    except Exception as ex:
        print("explode fallito:", ex)

tipi = {}
for e in ms:
    tipi[e.EntityName] = tipi.get(e.EntityName, 0) + 1
print("entita' nel modello:", tipi)

com_retry(lambda: doc.SendCommand("(command \"_.ZOOM\" \"_E\") "))
time.sleep(1)
com_retry(lambda: doc.Save())
print("RISALVATO con solidi esplosi")
