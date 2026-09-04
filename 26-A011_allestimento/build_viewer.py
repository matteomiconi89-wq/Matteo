#!/usr/bin/env python3
# Genera il viewer 3D interattivo (arredo_interattivo.html) dell'allestimento 26-A011.
# Mobili = i 21 solidi ricostruiti al mm dal DWG (vedi pipeline/ricostruisci.py).
# Legge un unico file: arredo_geometry.json  {shell_step, aperto, mobili}.
import json, pathlib, os
BASE = pathlib.Path(__file__).parent
G = json.load(open(BASE/"arredo_geometry.json"))
MOB = G["mobili"]

def dims(meshes):
    xs=[c[0] for m in meshes for c in m['v']]; ys=[c[1] for m in meshes for c in m['v']]; zs=[c[2] for m in meshes for c in m['v']]
    return round(max(xs)-min(xs)), round(max(ys)-min(ys)), round(max(zs)-min(zs))

# key -> (label, hex color, categoria, fonte)  — 21 pezzi ricostruiti dal DWG 2D
META = {
 "letto_master":     ("Letto matrimoniale · master",   "#c7a34e","camera","footprint dalla pianta · ALTEZZE mie, da confermare"),
 "armadio_master":   ("Armadio camera master",         "#a8825a","camera","STEP REALE di Matteo (106 pezzi, nomi distinta)"),
 "letto_doppia":     ("Letto contenitore · doppia",    "#d0b25e","camera","IPOTESI: non e disegnato in pianta (ribaltabile da armadio)"),
 "armadio_doppia":   ("Armadio camera doppia",         "#96733f","camera","STEP REALE di Matteo (90 pezzi, nomi distinta)"),
 "divano":           ("Divano + pensile",              "#c86b45","living","footprint dalla pianta · ALTEZZE mie, da confermare"),
 "tavolo":           ("Tavolo",                        "#7d7f86","living","piano dalla pianta · gambe e altezza mie"),
 "libreria":         ("Libreria-parete ufficio",       "#3f7fae","living","footprint dalla pianta · ripiani e altezza miei"),
 "mobile_ingresso":  ("Mobile ingresso-living",        "#7a9a6d","living","footprint dalla pianta · altezza mia (2080)"),
 "cucina":           ("Cucina (7 moduli)",             "#b58b56","cucina","dai prospetti · larghezze validate"),
 "lavanderia":       ("Lavanderia (lavatrice+mobili)", "#4fb0a0","cucina","carcassa+ante+elettrodom. da pianta DWG"),
 "colonna_220":      ("Colonna dispensa L.220",        "#5aa0a6","cucina","footprint dalla pianta · altezza mia (2076)"),
 "bagno_ant_muri":   ("Bagno anteriore · muri",        "#b9c6cc","bagni","vano stanza stimato da me · sp.90 H2100 miei"),
 "bagno_ant_sanitari":("Bagno anteriore · sanitari",   "#7fa9b5","bagni","POSIZIONI dai cerchi DWG · forme e altezze mie"),
 "mobile_lavabo_ant":("Mobile lavabo · bagno ant.",    "#c58fa3","bagni","footprint dalla pianta · altezze mie (820/870)"),
 "bagno_post_muri":  ("Bagno posteriore · muri",       "#b9c6cc","bagni","vano stanza stimato da me · sp.90 H2100 miei"),
 "bagno_post_sanitari":("Bagno posteriore · sanitari", "#7fa9b5","bagni","POSIZIONI dai cerchi DWG · forme e altezze mie"),
 "mobile_lavabo_post":("Mobile lavabo · bagno post.",  "#b98298","bagni","footprint dalla pianta · altezze mie (820/870)"),
 "plo_ingresso":     ("Parete ingresso · P.lo",        "#9b6fb0","pareti","footprint dalla pianta · altezza mia (2100)"),
 "parete_div_master":("Divisorio living / master",     "#c05f86","pareti","STEP REALE di Matteo (55 pezzi, nomi distinta)"),
 "parete_divisoria": ("Divisorio living / doppia",     "#b0577c","pareti","pannelli letti uno a uno dalla pianta"),
}
CAT = {"camera":"Camere (letti · armadi)","living":"Living · ingresso · ufficio",
       "cucina":"Cucina · lavanderia","bagni":"Bagni (muri · sanitari · lavabi)","pareti":"Pareti e divisori"}

pieces=[]
for k,(label,col,cat,fonte) in META.items():
    meshes = MOB.get(k,[])
    if not meshes: print("  (manca)",k); continue
    L,P,H = dims(meshes)
    pieces.append({"key":k,"label":label,"color":col,"cat":cat,"fonte":fonte,"L":L,"P":P,"H":H})

data = {"shell_step":G.get("shell_step",[]), "aperto":G["aperto"], "mobili":MOB, "ingombri":{}}
geo_json = json.dumps(data, separators=(",",":"))
pieces_json = json.dumps(pieces, separators=(",",":"))
cat_json = json.dumps(CAT, ensure_ascii=False)

TEMPLATE = (BASE/"viewer_template.html").read_text()
HTML = TEMPLATE.replace("/*__GEO__*/", geo_json).replace("/*__PIECES__*/", pieces_json).replace("/*__CATS__*/", cat_json)
out = BASE/"arredo_interattivo.html"
out.write_text(HTML)
print("scritto", out.name, os.path.getsize(out)//1024,"KB", "pezzi:", len(pieces))
