#!/usr/bin/env python3
# Genera il viewer 3D interattivo (artifact) dell'allestimento 26A011 con i solidi reali STL.
import json, pathlib
BASE = pathlib.Path(__file__).parent
G = json.load(open(BASE/"arredo_geometry_solidi.json"))

def dims(meshes):
    xs=[c[0] for m in meshes for c in m['v']]; ys=[c[1] for m in meshes for c in m['v']]; zs=[c[2] for m in meshes for c in m['v']]
    return round(max(xs)-min(xs)), round(max(ys)-min(ys)), round(max(zs)-min(zs))

# metadati pezzi: key -> (label, hex color, categoria, fonte)
META = {
 "divano":           ("Divano + pensile",              "#c86b45","reali","ricostruito da pianta+prospetto DWG"),
 "libreria":         ("Libreria ufficio",              "#3f7fae","reali","estruso da footprint pianta DWG"),
 "plo_ingresso":     ("Parete ingresso · PLO",         "#9b6fb0","reali","estruso da footprint pianta DWG"),
 "parete_letto":     ("Parete letto · camera master",  "#c7a34e","reali","estruso da footprint pianta DWG"),
 "parete_divisoria": ("Parete divisoria living/camera","#c05f86","reali","estruso da footprint pianta DWG"),
 "lavatrice":        ("Colonna lavatrice",             "#4fb0a0","reali","estruso da footprint pianta DWG"),
 "muretti_bagni":    ("Muretti bagni",                 "#8a8a52","reali","estruso da footprint pianta DWG"),
 "pli_lavanderia":   ("Parete/porta lavanderia · PLI", "#5cb85c","reali","estruso da footprint pianta DWG"),
 "mobile_lavabo_bagno":("Mobile lavabo bagno doppia",   "#c58fa3","reali","ricostruito da prospetto DWG"),
 "mobile_ingresso":  ("Mobile ingresso-living",        "#7a9a6d","dett","spec ESECUTIVI_3D (41 pann.)"),
 "lavabo_lavanderia":("Lavabo lavanderia",             "#5aa0a6","dett","volumi DXF (74 solidi)"),
 "cucina":           ("Cucina (7 moduli)",             "#b58b56","reali","ricostruita da prospetti DWG · validata"),
 "tavolo_sedie":     ("Tavolo + sedie",                "#8b8f96","box","ingombro planimetria"),
 "armadio_cam_doppia":("Armadio camera doppia",        "#8b8f96","box","ingombro planimetria"),
}
CAT = {"reali":"Solidi ricostruiti dal DWG (2D→3D)","dett":"Solidi a livello pannello (specifiche)","box":"Ingombri (planimetria)"}

# costruisci lista pezzi per il viewer con dimensioni
pieces=[]
for k,(label,col,cat,fonte) in META.items():
    if cat=="box":
        meshes = G["ingombri"].get(k,{}).get("mesh",[])
    else:
        meshes = G["mobili"].get(k,[])
    if not meshes: continue
    L,P,H = dims(meshes)
    pieces.append({"key":k,"label":label,"color":col,"cat":cat,"fonte":fonte,"L":L,"P":P,"H":H})

data = {
 "shell_step": G.get("shell_step",[]),
 "aperto": G["aperto"],
 "mobili": G["mobili"],
 "ingombri": {k:v["mesh"] for k,v in G["ingombri"].items()},
}
geo_json = json.dumps(data, separators=(",",":"))
pieces_json = json.dumps(pieces, separators=(",",":"))
cat_json = json.dumps(CAT, ensure_ascii=False)

TEMPLATE = (BASE/"viewer_template.html").read_text()
HTML = TEMPLATE.replace("/*__GEO__*/", geo_json).replace("/*__PIECES__*/", pieces_json).replace("/*__CATS__*/", cat_json)
out = BASE/"arredo_solidi.html"
out.write_text(HTML)
import os
print("scritto", out.name, os.path.getsize(out)//1024,"KB", "pezzi:", len(pieces))
for p in pieces: print(f"  {p['key']:18s} {p['L']}x{p['P']}x{p['H']}  [{p['cat']}]")
