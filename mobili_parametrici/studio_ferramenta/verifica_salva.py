# -*- coding: utf-8 -*-
"""Censimento per indice (niente enumeratore) + salvataggio del doc PEZZI_DOMANDE."""
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
n = com_retry(lambda: ms.Count)
tipi = {}
for i in range(n):
    try:
        e = ms.Item(i)
        tipi[e.EntityName] = tipi.get(e.EntityName, 0) + 1
    except Exception:
        tipi["?"] = tipi.get("?", 0) + 1
print(f"entita': {n} -> {tipi}")

com_retry(lambda: doc.SendCommand("(command \"_.ZOOM\" \"_E\") "))
time.sleep(1)
com_retry(lambda: doc.Save())
print("SALVATO", doc.FullName)
