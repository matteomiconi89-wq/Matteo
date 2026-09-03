# -*- coding: utf-8 -*-
"""inietta_3d - mette il SOLIDO 3D del pezzo dentro l'MPRX (XmlOcaf).

Catena: DXF 3D del pezzo -> estrai_geometria (quote+lavorazioni) ->
ricostruzione del solido in FreeCAD (costruisci_pezzo_fc.py) -> BRep
testuale CASCADE -> iniezione nell'XML dell'MPRX: sezione <shapes> +
ramo "Shape 1" sotto la label "Shapes" (104), ricalcato dai file fatti
a video (444.mprx come riferimento).

uso: inietta_3d(dxf_path, mprx_path, log=print) -> True/False
"""
import json
import math
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "Dxf2Tlf"))
sys.path.insert(0, r"C:\Users\User\Desktop\CLAUDE\Dxf2Tlf")

FREECADCMD = r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe"
# percorso FISSO (gli exe PyInstaller non possono lanciare script interni):
# come per i LISP della filiera, gli script FreeCAD vivono in Dxf2Mpr
_QUI = r"C:\Users\User\Desktop\CLAUDE\Dxf2Mpr"
if not os.path.isfile(os.path.join(_QUI, "costruisci_pezzo_fc.py")):
    _QUI = os.path.dirname(os.path.abspath(__file__))
COSTRUTTORE = os.path.join(_QUI, "costruisci_pezzo_fc.py")


def _dati_pezzo(dxf_path):
    """Estrae le lavorazioni e le normalizza nel frame del programma A."""
    from dxf2tlf_masterwood import estrai_geometria
    (dims, fA, sA, fB, sB, tagli, sagome, incl, avvisi) = \
        estrai_geometria(dxf_path, prof_d14=None)
    lung, larg, alt = dims
    d = {"dims": [lung, larg, alt], "tasche": [], "fori_vert": [],
         "fori_lat": [], "sagome": sagome, "biselli": incl,
         "lamate": tagli}

    def specchia_contorno(s):
        n = dict(s, contorno=[(x, larg - y) for x, y in s["contorno"]])
        if s.get("tratti"):
            n["tratti"] = [("L", (t[1][0], larg - t[1][1])) if t[0] == "L"
                           else ("A", (t[1][0], larg - t[1][1]),
                                 (t[2][0], larg - t[2][1]), t[3])
                           for t in s["tratti"]]
        return n

    for s in sA:
        d["tasche"].append(dict(s, lato="sopra"))
    for s in sB:                        # frame _B: specchiato in y
        if s.get("cir"):
            d["tasche"].append(dict(s, y=larg - s["y"], lato="sotto"))
        elif "contorno" in s:
            d["tasche"].append(dict(specchia_contorno(s), lato="sotto"))
        else:
            d["tasche"].append({"x1": s["x1"], "y1": larg - s["y2"],
                                "x2": s["x2"], "y2": larg - s["y1"],
                                "prof": s["prof"], "lato": "sotto"})
    for f in fA:
        if f["plane"] == 0:
            d["fori_vert"].append({"x": f["x"], "y": f["y"], "r": f["r"],
                                   "prof": f["prof"], "lato": "sopra"})
        else:
            d["fori_lat"].append({"plane": f["plane"], "x": f["x"],
                                  "z": f["y"], "r": f["r"],
                                  "prof": f["prof"]})
    for f in fB:
        if f["plane"] == 0:
            d["fori_vert"].append({"x": f["x"], "y": larg - f["y"],
                                   "r": f["r"], "prof": f["prof"],
                                   "lato": "sotto"})
        # laterali del girato: rarissimi, si saltano (avviso dal chiamante)
    return d


def _costruisci_brep(dati, log):
    """FreeCAD ricostruisce il solido e lo esporta in BRep testuale."""
    tmp = tempfile.mkdtemp(prefix="inietta3d_")
    pj = os.path.join(tmp, "pezzo.json")
    pb = os.path.join(tmp, "pezzo.brep")
    with open(pj, "w", encoding="utf-8") as f:
        json.dump(dati, f)
    r = subprocess.run([FREECADCMD, COSTRUTTORE, "--", pj, pb],
                       capture_output=True, text=True, timeout=600)
    if "BREP-OK" not in (r.stdout or ""):
        raise RuntimeError("costruzione solido fallita: "
                           + (r.stdout or "")[-400:]
                           + (r.stderr or "")[-400:])
    testo = open(pb, encoding="ascii", errors="replace").read()
    return testo


def _prepara_shapes(brep_testo):
    """Dal .brep di FreeCAD alla sezione <shapes> dell'MPRX: si toglie
    l'intestazione DBRep e la RIGA RADICE finale (nei .mprx fatti a video
    la sezione chiude sull'ultimo record '*').
    Ritorna (testo_sezione, riferimento_radice, n_locations)."""
    i = brep_testo.find("CASCADE Topology")
    if i < 0:
        raise RuntimeError("BRep senza intestazione CASCADE")
    righe = brep_testo[i:].rstrip().splitlines()
    radice = None
    radice_loc = 0
    while righe and righe[-1].strip() and not righe[-1].rstrip().endswith("*"):
        m = re.match(r"^\s*([+-]\d+)(?:\s+(\d+))?\s*$", righe[-1])
        if m and radice is None:
            radice = m.group(1)
            radice_loc = int(m.group(2) or 0)
        righe.pop()
    while righe and not righe[-1].strip():
        righe.pop()
    if radice is None:
        raise RuntimeError("riga radice BRep non trovata in coda")
    corpo = "\n".join(righe)
    # ATTENZIONE numerazione: i riferimenti DENTRO il BRep (riga radice
    # compresa) contano dal BASSO; le etichette XmlOcaf dell'MPRX contano
    # dall'ALTO -> tshape_xml = n_tot + 1 - |ref| (verificato sul 444:
    # 181-100=81, 181-123=58...)
    mt = re.search(r"^TShapes\s+(\d+)", corpo, re.M)
    n_tot = int(mt.group(1))
    v = int(radice)
    radice = f"{'+' if v > 0 else '-'}{n_tot + 1 - abs(v)}"
    return corpo, radice, radice_loc


def _analizza_brep(corpo):
    """Dal testo TShapes: (facce del guscio con segno, in ordine).
    Il SOLIDO radice e' l'ultimo record; il suo ref porta al guscio,
    il guscio elenca le FACCE firmate (+/-) — quelle servono alla
    catena di etichette per-faccia dell'MPRX."""
    i = corpo.find("TShapes")
    n_tot = int(corpo[i:].split()[1])
    righe = corpo[i:].splitlines()[1:]
    records = []          # (codice, righe_del_record)
    cur = None
    for r in righe:
        rs = r.strip()
        if cur is None:
            if re.fullmatch(r"[A-Z][a-z]", rs):
                cur = (rs, [])
            continue
        cur[1].append(rs)
        if rs.endswith("*"):
            records.append(cur)
            cur = None
    if len(records) != n_tot:
        raise RuntimeError(f"parser TShapes: {len(records)} record, "
                           f"attesi {n_tot}")
    indice = {n_tot - k: rec for k, rec in enumerate(records)}

    def refs_di(rec):
        """Riferimenti ai sotto-shape del record: stanno DOPO l'ultima
        riga di flag [01]{7} e possono andare a capo su piu' righe."""
        corpo_rec = " ".join(rec[1])
        m = None
        for m in re.finditer(r"\b[01]{7}\b", corpo_rec):
            pass
        coda = corpo_rec[m.end():] if m else corpo_rec
        return re.findall(r"([+-]\d+)\s+\d+", coda)

    radice = records[-1]                      # ref-basso 1 = radice
    visti = 0
    while radice[0] == "Co" and visti < 5:    # compound: scendi al solido
        radice = indice[abs(int(refs_di(radice)[0]))]
        visti += 1
    if radice[0] != "So":
        raise RuntimeError(f"radice non e' un solido: {radice[0]}")
    guscio = indice[abs(int(refs_di(radice)[0]))]
    if guscio[0] != "Sh":
        raise RuntimeError(f"ref del solido non porta a un guscio: "
                           f"{guscio[0]}")
    # dai ref (dal basso) agli indici XmlOcaf (dall'alto)
    facce = []
    for r in refs_di(guscio):
        v = int(r)
        facce.append(f"{'+' if v > 0 else '-'}{n_tot + 1 - abs(v)}")
    return facce


def inietta_3d(dxf_path, mprx_path, log=print):
    """Ricostruisce il pezzo dal DXF e lo inietta nell'MPRX."""
    dati = _dati_pezzo(dxf_path)
    lung, larg, alt = dati["dims"]
    if larg < 1.0 or alt < 0.5:
        log("    [!] pezzo non a pannello (quote degeneri, tondo/tornito?): "
            "3D saltato")
        return False
    brep = _costruisci_brep(dati, log)
    return inietta_brep(brep, mprx_path, log)


def inietta_brep(brep, mprx_path, log=print):
    """Inietta un BRep gia' pronto (es. dal file STEP originale)."""
    corpo, radice, radice_loc = _prepara_shapes(brep)
    versione = "V1" if "Topology V1" in corpo[:60] else \
               "V2" if "Topology V2" in corpo[:60] else "V3"

    t = open(mprx_path, encoding="utf-8", errors="replace").read()
    if "<shapes>" in t:
        log("  [!] MPRX ha gia' una sezione shapes piena: salto")
        return False
    if ">Shapes<" not in t:
        log("  [!] MPRX senza label Shapes: salto")
        return False

    # id massimo degli attributi esistenti
    max_id = max(int(m) for m in re.findall(r'\bid="(\d+)"', t))
    nid = [max_id]

    def nuovo_id():
        nid[0] += 1
        return nid[0]

    # posizione nella lista locations per la radice: identita' = 1 se
    # esistono locations, altrimenti 0 (nessuna location)
    loc_attr = f' location="{radice_loc}"' if radice_loc else ""
    facce = _analizza_brep(corpo)
    n = len(facce)
    id_marker = nuovo_id()
    id_arr = nuovo_id()
    id_ns = nuovo_id()
    id_pres = nuovo_id()
    id_reali = nuovo_id()
    id_colori = nuovo_id()
    id_nome = nuovo_id()
    id_int = nuovo_id()
    id_tree = nuovo_id()
    id_tag = nuovo_id()
    id_ns2 = nuovo_id()

    # STORIA DELL'IMPORT in 3 stadi, ricalcata sui file fatti a video
    # (444.mprx): 1..n facce "primitive", n+1 "Transform" (modify),
    # n+2..2n+1 facce modify, 2n+2 "Relocate" (modify, entra la location),
    # 2n+3..3n+2 facce modify con location. In coda label 8 (IntegerArray)
    # e label 10 con la TFunction 2d29eb1d: SENZA la funzione woodWOP non
    # crea l'oggetto a video (ogni entita' vive tramite la sua TFunction).
    et = []
    for k, fa in enumerate(facce, 1):
        et.append(f"""       <label tag="{k}">
        <TNaming_NamedShape id="{nuovo_id()}" evolution="primitive">
         <olds/>
         <news>
          <shape tshape="{fa}" index="1"/>
         </news>
        </TNaming_NamedShape>
       </label>""")
    et.append(f"""       <label tag="{n + 1}">
        <TDataStd_Name id="{nuovo_id()}">Transform</TDataStd_Name>
        <TNaming_NamedShape id="{nuovo_id()}" evolution="modify">
         <olds>
          <shape tshape="{radice}" index="1"/>
         </olds>
         <news>
          <shape tshape="{radice}" index="1"/>
         </news>
        </TNaming_NamedShape>
       </label>""")
    for k, fa in enumerate(facce, 1):
        et.append(f"""       <label tag="{n + 1 + k}">
        <TNaming_NamedShape id="{nuovo_id()}" evolution="modify">
         <olds>
          <shape tshape="{fa}" index="1"/>
         </olds>
         <news>
          <shape tshape="{fa}" index="1"/>
         </news>
        </TNaming_NamedShape>
       </label>""")
    et.append(f"""       <label tag="{2 * n + 2}">
        <TDataStd_Name id="{nuovo_id()}">Relocate</TDataStd_Name>
        <TNaming_NamedShape id="{nuovo_id()}" evolution="modify">
         <olds>
          <shape tshape="{radice}" index="1"/>
         </olds>
         <news>
          <shape tshape="{radice}"{loc_attr} index="1"/>
         </news>
        </TNaming_NamedShape>
       </label>""")
    for k, fa in enumerate(facce, 1):
        et.append(f"""       <label tag="{2 * n + 2 + k}">
        <TNaming_NamedShape id="{nuovo_id()}" evolution="modify">
         <olds>
          <shape tshape="{fa}" index="1"/>
         </olds>
         <news>
          <shape tshape="{fa}"{loc_attr} index="1"/>
         </news>
        </TNaming_NamedShape>
       </label>""")
    storia = "\n".join(et)

    ramo = f"""     <label tag="1">
      <TDataStd_UAttribute id="{id_marker}" guid="e7b0e0a2-a186-4153-b27e-12fa0bdb9a9c"/>
      <TDataStd_ExtStringArray id="{id_arr}" first="0" last="0" delta="0">
       <string>0</string>
      </TDataStd_ExtStringArray>
      <TNaming_NamedShape id="{id_ns}" evolution="primitive" version="7">
       <olds/>
       <news>
        <shape tshape="{radice}"{loc_attr} index="1"/>
       </news>
      </TNaming_NamedShape>
      <TPrsStd_AISPresentation id="{id_pres}" guid="f81cbb75-db5c-4ea7-8bbf-a0e171127c5c" isdisplayed="true" mode="1"/>
      <TDataStd_RealArray id="{id_reali}" first="0" last="8" delta="0">0 0 0 0 0 1 1 0 0</TDataStd_RealArray>
      <TDataStd_IntegerArray id="{id_colori}" first="0" last="4" delta="0">0 126 126 126 0</TDataStd_IntegerArray>
      <TDataStd_Name id="{id_nome}">Shape 1</TDataStd_Name>
      <TDataStd_Integer id="{id_int}">17</TDataStd_Integer>
      <TDataStd_TreeNode id="{id_tree}" treeid="2a96b621-ec8b-11d0-bee7-080009dc3333"/>
      <label tag="1">
       <TDF_TagSource id="{id_tag}">{3 * n + 2}</TDF_TagSource>
       <TNaming_NamedShape id="{id_ns2}" evolution="primitive" version="2">
        <olds/>
        <news>
         <shape tshape="{radice}"{loc_attr} index="1"/>
        </news>
       </TNaming_NamedShape>
{storia}
      </label>
      <label tag="8">
       <TDataStd_IntegerArray id="{nuovo_id()}" first="0" last="0" delta="0">0</TDataStd_IntegerArray>
      </label>
      <label tag="10">
       <TFunction_Function id="{nuovo_id()}" guid="2d29eb1d-612d-4713-b3d9-b76404fba92c" failure="0"/>
      </label>
     </label>
    """

    # 1) label 104: contatore shapes 1->2, aggancio TreeNode al figlio,
    #    e il ramo "Shape 1" come figlio
    i = t.find(">Shapes<")
    ini = t.rfind("<label", 0, i)
    fine = t.find("</label>", i)
    blocco = t[ini:fine]
    b2 = re.sub(r'(<TDataStd_IntegerArray[^>]*first="0" last="1"[^>]*>)1 0',
                r"\g<1>2 0", blocco, count=1)
    b2 = re.sub(r'(<TDataStd_TreeNode id="\d+" '
                r'treeid="2a96b621-ec8b-11d0-bee7-080009dc3333")/>',
                rf'\g<1> children="{id_tree} "/>', b2, count=1)
    if b2 == blocco:
        log("  [!] struttura label Shapes inattesa: salto")
        return False
    t = t[:ini] + b2 + ramo + t[fine:]

    # 2) sezione <shapes> col BRep
    t = t.replace("<shapes/>", "<shapes>\n" + corpo + "\n</shapes>", 1)

    # 3) conteggio oggetti del documento (objnb): +attributi aggiunti
    aggiunti = nid[0] - max_id
    m = re.search(r'(<info[^>]*objnb=")(\d+)(")', t)
    if m:
        t = t[:m.start()] + m.group(1) + str(int(m.group(2)) + aggiunti) \
            + m.group(3) + t[m.end():]

    with open(mprx_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(t)
    log(f"  3D iniettato ({versione}, radice {radice}, "
        f"{len(corpo)//1024} KB di geometria)")
    return True


if __name__ == "__main__":
    inietta_3d(sys.argv[1], sys.argv[2])
