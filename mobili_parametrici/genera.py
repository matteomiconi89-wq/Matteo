# -*- coding: utf-8 -*-
"""
GENERATORE PARAMETRICO (v2, stretch-with-holes, donatore a stesso F).
Principio: i fori NON si tappano/riforano (niente leggi inferite, niente errori).
Il pannello si taglia in zone lungo X e si stira nei CORRIDOI (bande prive di fori):
 - le zone laterali (fianchi + baie cassetti) TRASLANO rigide portando i fori esatti
 - il vano centrale si allarga per estrusione della sezione (banda libera)
A parita' di F la baia laterale ha larghezza fissa (F+7): con donatore a stesso F la
riproduzione degli esemplari esistenti e' ESATTA (donatore = se stesso -> identita').

Uso (env):
  GEN_TIPO   J-03.01 (default)
  GEN_W      larghezza totale (mm) [obbligatoria]
  GEN_F      forza il frontale laterale (default: regola automatica)
  GEN_OUT    percorso STEP di uscita
  GEN_DONOR  forza un file donatore
"""
import os, sys, json, math
BASE = r"C:\Users\User\Desktop\CLAUDE\mobili_parametrici"
sys.path.insert(0, BASE)
import FreeCAD as App
import Part, Import
from FreeCAD import Base
from motore import slice_stretch

DROP = {
 'Set17': r"C:\Users\User\Dropbox\STEFANO\Matteo\ExtraOrdinario\21032\Set_17_18",
 'Set18': r"C:\Users\User\Dropbox\STEFANO\Matteo\ExtraOrdinario\21032\Set_17_18",
 'Set19': r"C:\Users\User\Dropbox\STEFANO\Matteo\ExtraOrdinario\21032\SET_19_20_21_22",
}
# --- catalogo donatori J-03.01: F -> [(file, W)] ---
CATALOGO = {
 'J-03.01': {
   'front_rule': 'due_cassetti',      # F laterale in taglie, CX centrale
   'taglie_F': [310, 350, 400, 450, 500, 550],
   'CX_min': 671.0,
   'donatori': {
     310: [('Set19/21032_C108_J-03_01.stp', 1339), ('Set19/21032_M07_J-03_01.stp', 1339)],
     350: [('Set19/21032_C107_J-03_01.stp', 1429), ('Set19/21032_M06_J-03_01.stp', 1499),
           ('Set17/Set_17_A211_J-03.01.stp', 1452)],
     400: [('Set17/Set_17_A203_J-03.01.stp', 1547), ('Set18/Set_18_A110_J-03.01.stp', 1579),
           ('Set19/21032_M08_J-03_01.stp', 1586)],
     450: [('Set17/Set_17_A103_J-03.01.stp', 1601)],
   },
   # corridoi centrali (bande libere) per i pannelli che stirano: coppia simmetrica a +/- c
   'corridoi': {
     '05_Sottotop': 300, '06_Piano_Sottolavabo': 250, '07_Schiena': 150,
     '08_Frontale_Fisso': 120, '10_Base': 200, '11_Zoccolo': 200,
     '12_Canalina_Led': None,
   },
 },
}

def risolvi(path):
    for pre, d in DROP.items():
        if path.startswith(pre + '/'):
            return os.path.join(d, path[len(pre)+1:])
    return path

TIPO = os.environ.get('GEN_TIPO', 'J-03.01')
W = float(os.environ['GEN_W'])
OUT = os.environ.get('GEN_OUT', os.path.join(BASE, f'{TIPO}_L{int(W)}.stp'))
cat = CATALOGO[TIPO]

# --- scelta F ---
if os.environ.get('GEN_F'):
    F = float(os.environ['GEN_F'])
else:
    cand = [t for t in cat['taglie_F'] if W - 30 - 2*t >= cat['CX_min']]
    F = float(max(cand)) if cand else float(cat['taglie_F'][0])
CX = W - 30 - 2*F

# --- scelta donatore (stesso F, W piu' vicino) ---
if os.environ.get('GEN_DONOR'):
    donor_file = os.environ['GEN_DONOR']; donor_W = None
else:
    lst = cat['donatori'].get(int(F))
    if not lst:
        # fallback: F piu' vicino disponibile
        Fdisp = min(cat['donatori'], key=lambda x: abs(x-F))
        lst = cat['donatori'][Fdisp]
        print(f"ATT: nessun donatore F={F}, uso F={Fdisp}")
    donor_file, donor_W = min(lst, key=lambda t: abs(t[1]-W))
donor_path = risolvi(donor_file)

# leggo W reale del donatore
doc = App.newDocument("gen")
Import.insert(donor_path, doc.Name)
shapes = {}
for o in doc.Objects:
    if not (hasattr(o, 'Shape') and o.Shape.Solids):
        continue
    lab = o.Label; ns = len(o.Shape.Solids)
    if lab.startswith('J-03.01_Cassetto') and ns == 5:
        shapes.setdefault(lab, o.Shape.copy())
    elif ns == 1 and not lab.startswith('SOLID') and not lab.startswith('J-'):
        shapes.setdefault(lab, o.Shape.copy())
# W donatore da bbox del sottotop
bb = shapes['05_Sottotop'].BoundBox
Wd = round(bb.XMax - bb.XMin, 2); HWd = Wd/2
# CX donatore dai fianchi INT
bi = shapes['03_Fianco_SX_INT'].BoundBox
CXd = round(-2*((bi[3] if False else bi.XMax)), 2)  # INT inner face SX = -CXd/2
CXd = round(-2*bi.XMax, 2)
dW = W - Wd                      # allargamento totale
S = dW/2                         # traslazione laterale (sinistra -S, destra +S)
print(f"{TIPO} W={W} F={F} CX={CX} | donatore={os.path.basename(donor_path)} Wd={Wd} CXd={CXd} dW={dW}")

INTin_d = CXd/2                  # |x| faccia interna fianco INT donatore

def stira_centrale(lab):
    """3 zone: [sx..-c-g] shift -S ; [-c+g..c-g] fisso ; [c+g..dx] shift +S.
    I corridoi sono le bande [-c-g,-c+g] e [c-g,c+g], da tenere prive di fori."""
    sh = shapes[lab]
    c = cat['corridoi'].get(lab)
    if c is None or abs(dW) < 1e-6:
        return sh.copy()
    g = 25.0
    bbx = sh.BoundBox
    return slice_stretch(sh, [
        {'da': bbx.XMin-1, 'a': -c-g, 'shift': -S},
        {'da': -c+g,       'a':  c-g, 'shift': 0},
        {'da':  c+g,       'a': bbx.XMax+1, 'shift': +S},
    ])

risultato = {}
# pannelli laterali: traslazione rigida (S sinistra / destra)
TRASLA = {
  '01_Fianco_SX_EXT': -S, '03_Fianco_SX_INT': -S, '14_Massello_interno_SX': -S,
  '02_Fianco_DX_EXT': +S, '04_Fianco_DX_INT': +S, '14_Massello_interno_DX': +S,
  '12_Canalina_Led': +S,
  '09_Frontale_Cassetto_SX': -S, '09_Frontale_Cassetto_DX': +S,
  'J-03.01_Cassetto_SX': -S, 'J-03.01_Cassetto_DX': +S,
}
for lab, s in TRASLA.items():
    if lab not in shapes:
        continue
    f = shapes[lab].copy(); f.translate(Base.Vector(s, 0, 0)); risultato[lab] = f
# pannelli centrali che stirano
for lab in ['05_Sottotop','06_Piano_Sottolavabo','07_Schiena','08_Frontale_Fisso',
            '10_Base','11_Zoccolo','09_Frontale_Cassetto_CX']:
    if lab not in shapes:
        continue
    if lab == '09_Frontale_Cassetto_CX':
        # frontale centrale: stira in banda libera a +/-80
        sh = shapes[lab]; bbx = sh.BoundBox
        if abs(dW) < 1e-6:
            risultato[lab] = sh.copy()
        else:
            risultato[lab] = slice_stretch(sh, [
                {'da': bbx.XMin-1, 'a': -70, 'shift': -S},
                {'da': 70, 'a': bbx.XMax+1, 'shift': +S}])
    else:
        risultato[lab] = stira_centrale(lab)

# ------- controlli -------
attesi = {'05_Sottotop': W, '11_Zoccolo': W, '08_Frontale_Fisso': W,
          '07_Schiena': W-80, '09_Frontale_Cassetto_CX': CX}
ok = True
for lab, forma in risultato.items():
    bbx = forma.BoundBox; wx = bbx.XLength
    if lab in attesi and abs(wx - attesi[lab]) > 0.3:
        print(f"  *** {lab}: L={wx:.2f} attesa {attesi[lab]:.2f}"); ok = False
    if not forma.isValid():
        print(f"  *** {lab}: NON valido"); ok = False
print("controlli:", "OK" if ok else "PROBLEMI")

# etichette dei 5 sottopezzi cassetto, per lato, ordinate come nel donatore
SUB_SX = ['15_Sponda_SX', '16_Sponda_DX', '18_Traversa_SX', '17_Schiena', '20_Fondo']
SUB_DX = ['15_Sponda_SX001', '16_Sponda_DX001', '19_Traversa_DX', '17_Schiena001', '20_Fondo001']

def esplodi_cassetto(comp, lato_dx):
    """Ordina i 5 solidi e assegna le etichette del donatore (sponde per XMin,
    traversa=fronte y minore, schiena=retro, fondo=dz sottile)."""
    solids = list(comp.Solids)
    fondo = min(solids, key=lambda s: s.BoundBox.ZLength)
    resto = [s for s in solids if s is not fondo]
    thinX = sorted([s for s in resto if s.BoundBox.XLength < 15], key=lambda s: s.BoundBox.XMin)
    thinY = sorted([s for s in resto if s.BoundBox.XLength >= 15], key=lambda s: s.BoundBox.YMin)
    labs = SUB_DX if lato_dx else SUB_SX
    coppie = []
    if len(thinX) == 2 and len(thinY) == 2:
        coppie = [(labs[0], thinX[0]), (labs[1], thinX[1]),
                  (labs[2], thinY[0]), (labs[3], thinY[1]), (labs[4], fondo)]
    else:  # fallback: etichette generiche
        coppie = [(f"{'DX' if lato_dx else 'SX'}_cass_{i}", s) for i, s in enumerate(solids)]
    return coppie

# ------- export -------
doc2 = App.newDocument("out")
root = doc2.addObject("App::Part", "root"); root.Label = TIPO
n = 0
for lab in sorted(risultato):
    if lab.startswith('J-03.01_Cassetto'):
        for sub_lab, sub_sh in esplodi_cassetto(risultato[lab], lab.endswith('_DX')):
            n += 1
            fe = doc2.addObject("Part::Feature", f"f{n}"); fe.Label = sub_lab
            fe.Shape = sub_sh; root.addObject(fe)
        continue
    n += 1
    fe = doc2.addObject("Part::Feature", f"f{n}"); fe.Label = lab
    fe.Shape = risultato[lab]; root.addObject(fe)
Import.export([root], OUT)
print("SCRITTO", OUT)
App.closeDocument(doc.Name); App.closeDocument(doc2.Name)
