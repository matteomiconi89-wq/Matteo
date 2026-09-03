# -*- coding: utf-8 -*-
"""Estrae testo dal PDF Blum hinge specs e cerca overlay/part number/plate."""
import re
import sys

from pypdf import PdfReader

PDF = r"C:\Users\User\.claude\projects\C--Users-User\1b077b87-4d96-40d5-8a24-bec85b0f613c\tool-results\webfetch-1784809894643-22bpqb.pdf"
r = PdfReader(PDF)
print("PAGINE:", len(r.pages))
testo = []
for i, pg in enumerate(r.pages):
    try:
        t = pg.extract_text() or ""
    except Exception as ex:
        t = ""
    testo.append((i + 1, t))

chiavi = ("overlay", "Overlay", "OVERLAY", "boring", "Boring", "71B3", "71T3", "175H", "173L",
          "inset", "Inset", "half", "Half", "thick", "Thick")
for num, t in testo:
    if any(k in t for k in chiavi):
        righe = [ln.strip() for ln in t.splitlines() if any(k in ln for k in chiavi)]
        if righe:
            print(f"--- pag {num} ---")
            for ln in righe[:14]:
                print("   ", ln[:150])
