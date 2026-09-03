# -*- coding: utf-8 -*-
"""Dal foglio FERRAMENTA (ferramenta_scheda_base.json) costruisce il PIANO DI
RACCOLTA blocchi: per ogni articolo deduce marca e codice produttore.

Regole di riconoscimento codice produttore nella descrizione:
  Blum:   71B/71T/70T/75T (cerniere), 175H/177H/173L/174H (basette), 20F/20S/20K/22K (AVENTOS),
          750./753./760./766. (guide LEGRABOX/MOVENTO), T51/T55 (TIP-ON), ZS/ZI (LEGRABOX acc.)
  Häfele: fornitore HAFELE, codici tipo 262.xx.xxx / 8 cifre
"""
import json
import os
import re
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
righe = json.load(open(os.path.join(BASE, "ferramenta_scheda_base.json"), encoding="utf-8"))

BLUM_PAT = re.compile(r"\b(7[015][BT]\d{4}[A-Z]?|17[357][HL]\d{4}(\.ONS)?|17[45]H\d{4}|"
                      r"2[02][SKF]\d{4}[A-Z]?(\.B)?|7[05]\.\d{4}(\.ONS)?|"
                      r"75[03]\.\d{4}[A-Z]?|76[06]\.\d{4}[A-Z]?|T5[15]\.\d{3,4}[A-Z]?|"
                      r"Z[SIF][A-Z]?\.\d{3,4}[A-Z]?|20S\d{4}[A-Z]?)\b")
HAF_PAT = re.compile(r"\b(\d{3}\.\d{2}\.\d{3})\b")

piano = []
for r in righe[1:]:
    if len(r) < 8:
        r = r + [""] * (8 - len(r))
    cod_pav, descr, forn, prezzo = r[4], r[5], r[6], r[7]
    if not descr or descr in ("DESCRIZIONE",):
        continue
    marca, cod_prod = "", ""
    m = BLUM_PAT.search(descr)
    if m:
        marca, cod_prod = "BLUM", m.group(1)
    elif forn == "HAFELE":
        marca = "HAFELE"
        m2 = HAF_PAT.search(descr)
        cod_prod = m2.group(1) if m2 else (cod_pav if re.match(r"^\d{8}$", cod_pav or "") else "")
    elif re.search(r"LEGRABOX|MOVENTO|TANDEM|CLIP TOP|BLUMOTION|AVENTOS|TIP-ON|SERVO", descr, re.I):
        marca = "BLUM(senza codice)"
    elif re.search(r"FITLOCK", descr, re.I):
        marca = "ITALIANA_F/FITLOCK"
    elif re.search(r"KREMENS|REKORD|BONE|KEKU", descr, re.I):
        marca = "PAVANELLO/CAMAR"
    else:
        marca = forn or "?"
    piano.append({"cod_pavanello": cod_pav, "descr": descr[:70], "fornitore": forn,
                  "marca": marca, "cod_produttore": cod_prod})

# normalizza i codici Häfele a 8 cifre in formato teccad xxx.xx.xxx
for p in piano:
    if p["marca"] == "HAFELE" and not p["cod_produttore"]:
        cp = (p["cod_pavanello"] or "").strip()
        if re.match(r"^\d{8}$", cp):
            p["cod_produttore"] = f"{cp[:3]}.{cp[3:5]}.{cp[5:]}"

json.dump(piano, open(os.path.join(BASE, "piano_raccolta.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

# documento leggibile
righe_md = ["# PIANO RACCOLTA BLOCCHI FERRAMENTA (da SCHEDA BASE > foglio FERRAMENTA)", ""]
righe_md.append(f"Totale articoli: {len(piano)}\n")
def blocco_md(titolo, filtro, dove):
    sel = [p for p in piano if filtro(p)]
    vis = set()
    uniq = []
    for p in sel:
        k = p["cod_produttore"] or p["descr"]
        if k in vis:
            continue
        vis.add(k)
        uniq.append(p)
    righe_md.append(f"## {titolo} — {len(uniq)} articoli unici — *{dove}*\n")
    for p in uniq:
        cod = p["cod_produttore"] or p["cod_pavanello"] or "(codice da trovare)"
        righe_md.append(f"- `{cod}` — {p['descr']}")
    righe_md.append("")
blocco_md("BLUM con codice", lambda p: p["marca"] == "BLUM", "e-services Blum PAI048, Prodotto singolo 3D (serve login Matteo)")
blocco_md("BLUM senza codice (da identificare)", lambda p: p["marca"] == "BLUM(senza codice)", "e-services Blum, cercare per descrizione")
blocco_md("HAFELE", lambda p: p["marca"] == "HAFELE", "teccad.hafele.com (libero, gia' operativo)")
blocco_md("PAVANELLO / CAMAR / FITLOCK", lambda p: p["marca"] in ("PAVANELLO", "PAVANELLO/CAMAR", "ITALIANA_F/FITLOCK"), "NO CAD online: modellare da scheda o estrarre dai STEP 25-A019")
blocco_md("FAS / altri (minuteria, vetri, elettrico)", lambda p: p["marca"] in ("FAS", "FUTURGLASS", "FEREXPERT", "BERTI", "FORESTI E SUARDI", "NOVACIF", "AMAZON", "LATTANZI/SOVERCHIA", "SHOPMANCINI", "?"), "vari / non pertinenti al generatore")
open(os.path.join(BASE, "PIANO_RACCOLTA.md"), "w", encoding="utf-8").write("\n".join(righe_md))

cnt = Counter(p["marca"] for p in piano)
con_cod = sum(1 for p in piano if p["cod_produttore"])
print(f"ARTICOLI: {len(piano)} | con codice produttore estratto: {con_cod}")
for m, n in cnt.most_common():
    print(f"  {m:22s} x{n}")
print()
print("=== BLUM con codice (scaricabili da e-services) ===")
visti = set()
for p in piano:
    if p["marca"] == "BLUM" and p["cod_produttore"] not in visti:
        visti.add(p["cod_produttore"])
        print(f"  {p['cod_produttore']:16s} {p['descr'][:52]}")
print()
print("=== HAFELE (scaricabili da teccad) ===")
visti2 = set()
for p in piano:
    if p["marca"] == "HAFELE" and p["cod_produttore"] and p["cod_produttore"] not in visti2:
        visti2.add(p["cod_produttore"])
        print(f"  {p['cod_produttore']:16s} {p['descr'][:52]}")
