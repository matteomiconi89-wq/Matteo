# -*- coding: utf-8 -*-
# Estrae i 3 pezzi delle domande aperte e li affianca in un unico STEP:
#   V027 (Armadio V), Q005 (Mobile Q), AC026 (AC)
# Uso: freecadcmd estrai_pezzi_domande.py
import os
import FreeCAD as App
import Part
import Import

SRC = r"C:\Users\User\Dropbox\STEFANO\25-A019 GUIDO_St Paul (Master Bedroom)\Esecutivi"
OUT = r"C:\Users\User\Desktop\CLAUDE\mobili_parametrici\studio_ferramenta\PEZZI_DOMANDE.stp"

PEZZI = [
    ("25-A019_Armadio camera V.stp", "25-A019_Armadio camera V027", "V027_D12basso_D5passo20_D6x4"),
    ("25-A019_Mobile_Q.stp", "25-A019_Mobile Q005", "Q005_quadrati_4xD5_32x32"),
    ("25-A019_AC.stp", "25-A019_AC026", "AC026_D6x4_superficiali"),
]

out_doc = App.newDocument("domande")
offset_x = 0.0
for fname, label, nuovo_nome in PEZZI:
    doc = App.newDocument("srcdoc")
    Import.insert(os.path.join(SRC, fname), doc.Name)
    trovato = None
    for o in doc.Objects:
        if o.TypeId == "Part::Feature" and o.Label == label and o.Shape.Solids:
            trovato = o
            break
    if trovato is None:
        print("NON TROVATO:", fname, label)
        App.closeDocument(doc.Name)
        continue
    sh = trovato.Shape.copy()
    try:
        m = trovato.getGlobalPlacement().toMatrix().multiply(trovato.Placement.toMatrix().inverse())
        sh.transformShape(m)
    except Exception:
        pass
    bb = sh.BoundBox
    # porta il pezzo con bbox-min su (offset_x, 0, 0)
    sh.translate(App.Vector(offset_x - bb.XMin, -bb.YMin, -bb.ZMin))
    obj = out_doc.addObject("Part::Feature", "pezzo")
    obj.Shape = sh
    obj.Label = nuovo_nome
    print(f"OK {label} -> {nuovo_nome} @X={offset_x:.0f} dims=({bb.XLength:.0f},{bb.YLength:.0f},{bb.ZLength:.0f})")
    offset_x += bb.XLength + 400.0
    App.closeDocument(doc.Name)

Import.export(out_doc.Objects, OUT)
print("SCRITTO", OUT)
