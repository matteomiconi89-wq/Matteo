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
 # camera master (fronte)
 "parete_letto":     ("Letto camera master",           "#c7a34e","camera","piano letto da pianta DWG"),
 "letto_doppia":     ("Letto contenitore (armadio)",   "#d0b25e","camera","ribaltabile dall armadio doppia"),
 "armadio_master":   ("Armadio camera master",         "#a8825a","camera","ante+fianchi dai pannelli pianta"),
 "parete_div_master":("Parete divisoria living/master","#c05f86","pareti","estruso da footprint DWG"),
 "bagno_ant_muri":   ("Bagno anteriore · muri",        "#b9c6cc","bagni","muri dal contorno stanza DWG"),
 "bagno_ant_sanitari":("Bagno anteriore · sanitari",   "#7fa9b5","bagni","doccia+WC+bidet dalle posizioni DWG"),
 "lavabo_bagno_ant": ("Lavabo bagno anteriore",        "#c58fa3","bagni","estruso da footprint DWG"),
 # living / ingresso / ufficio
 "divano":           ("Divano + pensile",              "#c86b45","living","ricostruito pianta+prospetto"),
 "tavolo":           ("Tavolo",                        "#7d7f86","living","piano da pianta DWG"),
 "mobile_ingresso":  ("Mobile ingresso-living",        "#7a9a6d","living","spec ESECUTIVI_3D (41 pann.)"),
 "plo_ingresso":     ("Parete ingresso · PLO",         "#9b6fb0","pareti","estruso da footprint DWG"),
 "libreria":         ("Libreria ufficio",              "#3f7fae","living","estruso da footprint DWG"),
 # cucina + lavanderia (baia)
 "cucina":           ("Cucina (7 moduli)",             "#b58b56","cucina","ricostruita da prospetti · validata"),
 "lavabo_lavanderia":("Lavabo lavanderia",             "#5aa0a6","cucina","volumi DXF (74 solidi)"),
 "lavatrice":        ("Colonna lavatrice",             "#4fb0a0","cucina","estruso da footprint DWG"),
 "lavanderia":       ("Lavanderia (muri)",             "#8fb0a8","bagni","muri da pianta DWG"),
 "pli_lavanderia":   ("Parete/porta lavanderia · PLI", "#5cb85c","pareti","estruso da footprint DWG"),
 # camera doppia (retro) + bagno posteriore
 "armadio_doppia":   ("Armadio doppia + letto cont.",  "#96733f","camera","ante+fianchi dai pannelli pianta"),
 "parete_divisoria": ("Parete divisoria living/doppia","#c05f86","pareti","estruso da footprint DWG"),
 "bagno_post_muri":  ("Bagno posteriore · muri",       "#b9c6cc","bagni","muri dal contorno stanza DWG"),
 "bagno_post_sanitari":("Bagno posteriore · sanitari", "#7fa9b5","bagni","doccia+WC+bidet dalle posizioni DWG"),
 "mobile_lavabo_bagno":("Mobile lavabo bagno post.",    "#c58fa3","bagni","ricostruito da prospetto"),
 "lavabo_bagno_post":("Lavabo bagno posteriore",       "#b98298","bagni","estruso da footprint DWG"),
 "muretti_bagni":    ("Muretti bagni",                 "#8a8a52","bagni","estruso da footprint DWG"),
}
CAT = {"camera":"Camere (letto · armadi)","living":"Living · ingresso · ufficio","cucina":"Cucina · lavanderia","bagni":"Bagni","pareti":"Pareti e divisori"}

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
