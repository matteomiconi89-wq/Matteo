# -*- coding: utf-8 -*-
"""Indice della libreria blocchi: scandisce blocchi_blum / blocchi_hafele e crea
blocchi_libreria.json { codice: {file, marca, descr} } per il generatore."""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
CARTELLE = {"BLUM": "blocchi_blum", "HAFELE": "blocchi_hafele"}

# codice -> descrizione leggibile (dai nomi file / foglio)
DESCR = {
    "71B3550": "Cerniera CLIP top BLUMOTION 110 battuta piena",
    "71B3650": "Cerniera CLIP top BLUMOTION 110 mezza battuta",
    "71B3750": "Cerniera CLIP top BLUMOTION 110 filo (inset)",
    "71B9550": "Cerniera CLIP top 95 porta spessa battuta",
    "71B9650": "Cerniera CLIP top 95 porta spessa mezza",
    "175H3100": "Basetta diritta H0 (CLIP)",
    "750.4001S": "Guida fianco LEGRABOX 40 kg estrazione totale",
    "262.34.302": "Giunto RAFIX TAB 20 S nero (Hafele)",
    "262.50.359": "KEKU Pacofix lato pannello (Hafele)",
    "262.50.390": "KEKU Pacofix lato telaio (Hafele)",
    "311.90.500": "Cerniera METALLA 110 G48/6 (Hafele)",
}

def codice_da_nome(nome):
    # 71B3550_... / 750_4001S_... / 262_34_302_...
    m = re.match(r"(\d{3}[._]\d{2}[._]\d{3})", nome)
    if m:
        return m.group(1).replace("_", ".")
    m = re.match(r"(7\d[A-Z]\d{4}S?|1\d{2}[HL]\d{4})", nome)
    if m:
        return m.group(1)
    m = re.match(r"(750[._]4001S)", nome)
    if m:
        return "750.4001S"
    return None

indice = {}
for marca, cart in CARTELLE.items():
    d = os.path.join(BASE, cart)
    if not os.path.isdir(d):
        continue
    for f in sorted(os.listdir(d)):
        if not f.lower().endswith((".step", ".stp")):
            continue
        cod = codice_da_nome(f)
        if not cod:
            continue
        indice[cod] = {"file": os.path.join(cart, f), "marca": marca,
                       "descr": DESCR.get(cod, f)}

json.dump(indice, open(os.path.join(BASE, "blocchi_libreria.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print(f"LIBRERIA BLOCCHI: {len(indice)} codici")
for cod, v in sorted(indice.items()):
    print(f"  {cod:12s} [{v['marca']:6s}] {v['descr'][:48]}  <- {os.path.basename(v['file'])}")
