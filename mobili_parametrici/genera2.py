# -*- coding: utf-8 -*-
"""
GENERATORE PARAMETRICO GENERALE (v5) per i vanity 21032 (J-03.xx).

Principi:
 1. STRETCH-WITH-HOLES: i fori viaggiano con le zone; si stira solo nei corridoi liberi.
 2. CLASSI DEI FORI (classi_fori.json, dedotte confrontando TUTTI gli esemplari):
      FISSO = resta dov'e' | SX = segue bordo/fianco sinistro | DX = destro | ALTRO = spina ridistribuita
    Il taglio viene scelto MINIMIZZANDO i fori dalla parte sbagliata; i pochi rimasti
    vengono RILOCATI (tappati e riforati alla posizione giusta).
 3. VETO SCASSI: mai tagliare dentro scassi (facce cilindriche verticali grandi, bspline):
    lo scasso del lavabo resta ESATTAMENTE quello del donatore (fisso per tipologia).
 4. DONATORE: stessa taglia/variante, appena piu' stretto della larghezza richiesta.

Env: GEN_TIPO (J-03.01|J-03.16|J-03.02), GEN_W, GEN_OUT, GEN_DONOR(opz), GEN_F(opz)
"""
import os, sys, json, re
BASE = r"C:\Users\User\Desktop\CLAUDE\mobili_parametrici"
sys.path.insert(0, BASE)
import FreeCAD as App
import Part, Import
from FreeCAD import Base
from motore import slice_stretch, tappa_fori, fora

DROP = {
 'Set17': r"C:\Users\User\Dropbox\STEFANO\Matteo\ExtraOrdinario\21032\Set_17_18",
 'Set18': r"C:\Users\User\Dropbox\STEFANO\Matteo\ExtraOrdinario\21032\Set_17_18",
 'Set19': r"C:\Users\User\Dropbox\STEFANO\Matteo\ExtraOrdinario\21032\SET_19_20_21_22",
}
def risolvi(p):
    for pre, d in DROP.items():
        if p.startswith(pre + '/'):
            return os.path.join(d, p[len(pre)+1:])
    return p

RICETTE = {
 'J-03.01': {
   'taglie_F': [310, 350, 400, 450, 500, 550], 'CX_min': 671.0,
   'donatori': [
     ('Set19/21032_C108_J-03_01.stp', 1339, 310), ('Set19/21032_M07_J-03_01.stp', 1339, 310),
     ('Set19/21032_C107_J-03_01.stp', 1429, 350), ('Set19/21032_M06_J-03_01.stp', 1499, 350),
     ('Set17/Set_17_A203_J-03.01.stp', 1547, 400), ('Set18/Set_18_A110_J-03.01.stp', 1579, 400),
     ('Set19/21032_M08_J-03_01.stp', 1586, 400),
     ('Set17/Set_17_A103_J-03.01.stp', 1601, 450),
   ],  # A211 escluso (profondita' anomala 602.5)
 },
 'J-03.16': {
   'donatori': [
     ('Set17/Set_17_B205_J-03.16_bis.stp', 1652, 'noINT'),
     ('Set19/21032_C101-102_J-03_16_bis.stp', 1709, 'INT'), ('Set18/Set_18_A105_J-03.16.stp', 1724, 'INT'),
     ('Set19/21032_C110_J-03_16.stp', 1770, 'INT'), ('Set19/21032_C204_J-03_16.stp', 1804, 'INT'),
     ('Set17/Set_17_A107_J-03.16.stp', 1851, 'INT'),
   ],
 },
 'J-03.02': {
   'donatori': [
     ('Set17/Set_17_B207_J-03.02.stp', 1979, '1INT'), ('Set17/Set_17_B208_J-03.02.stp', 2100, '1INT'),
     ('Set19/21032_B302_J-03_02_quat.stp', 2670, '2INT'), ('Set18/Set_18_B202_J-03.02_bis.stp', 2672, '2INT'),
   ],  # A102_ter escluso come donatore (divisori in posizione diversa)
 },
}

TIPO = os.environ.get('GEN_TIPO', 'J-03.01')
W = float(os.environ['GEN_W'])
OUT = os.environ.get('GEN_OUT', os.path.join(BASE, f'{TIPO}_L{int(W)}.stp'))
ric = RICETTE[TIPO]

# ---------- taglia/variante target ----------
if TIPO == 'J-03.01':
    if os.environ.get('GEN_F'):
        taglia = int(os.environ['GEN_F'])
    else:
        cand = [t for t in ric['taglie_F'] if W - 30 - 2*t >= ric['CX_min']]
        taglia = max(cand) if cand else ric['taglie_F'][0]
elif TIPO == 'J-03.16':
    taglia = 'INT' if W >= 1680 else 'noINT'
else:
    taglia = '2INT' if W >= 2400 else '1INT'

# ---------- donatore ----------
if os.environ.get('GEN_DONOR'):
    donor_file = os.environ['GEN_DONOR']
else:
    stessi = [(f, wd) for f, wd, t in ric['donatori'] if t == taglia]
    if not stessi:
        raise RuntimeError(f"nessun donatore per taglia {taglia}")
    sotto = [(f, wd) for f, wd in stessi if wd <= W]
    donor_file = max(sotto, key=lambda t: t[1])[0] if sotto else min(stessi, key=lambda t: t[1])[0]
donor_path = risolvi(donor_file)
donor_base = os.path.basename(donor_path)

CLASSI = json.load(open(os.path.join(BASE, 'classi_fori.json'), encoding='utf-8')).get(donor_base, {})
TARATURA = json.load(open(os.path.join(BASE, 'taratura_aree.json'), encoding='utf-8')).get(TIPO, {}).get(str(taglia), {})

# ---------- carica donatore ----------
doc = App.newDocument("gen")
Import.insert(donor_path, doc.Name)
shapes, comps = {}, {}
for o in doc.Objects:
    if not (hasattr(o, 'Shape') and o.Shape.Solids):
        continue
    lab = o.Label; ns = len(o.Shape.Solids)
    if ns >= 3 and 'Cassetto' in lab:
        comps.setdefault(lab, o.Shape.copy())
    elif ns == 1 and not lab.startswith('SOLID') and not lab.startswith('J-') \
            and not re.match(r'^(15_|16_|17_Schiena|18_Traversa|19_Traversa|20_Fondo)', lab):
        # i sotto-pezzi del cassetto nello STEP esistono anche come definizioni in
        # coordinate LOCALI (appoggiate all'origine): NON vanno esportati come pannelli,
        # il cassetto vero arriva solo dal compound montato nel mobile
        shapes.setdefault(lab, o.Shape.copy())

bbst = shapes['05_Sottotop'].BoundBox
Wd = round(bbst.XMax - bbst.XMin, 2)
S = (W - Wd) / 2.0
print(f"{TIPO} W={W} taglia={taglia} | donatore={donor_base} Wd={Wd} S={S:+.1f}")

# ---------- geometria di supporto ----------
def veto_intervalli(sh):
    """Intervalli X vietati al taglio: scassi (cilindri verticali grandi, bspline, tori)."""
    out = []
    for f in sh.Faces:
        s = f.Surface; cn = s.__class__.__name__; fb = f.BoundBox
        if cn == 'Cylinder':
            if s.Radius >= 15 and abs(abs(s.Axis.z) - 1.0) < 1e-6:
                out.append((fb.XMin - 3, fb.XMax + 3))
        elif cn not in ('Plane', 'SurfaceOfExtrusion'):
            out.append((fb.XMin - 3, fb.XMax + 3))
    return out

def intervalli_foro(h):
    """Intervalli X occupati dal foro. I fori orizzontali (asse X) estratti hanno
    lo/hi che uniscono il foro SX e DX alla stessa quota: li tratto come due punte."""
    if h['dir'] == 'X':
        if h['hi'] - h['lo'] > 100:
            return [(h['lo'] - 2, h['lo'] + 42), (h['hi'] - 42, h['hi'] + 2)]
        return [(h['lo'] - 2, h['hi'] + 2)]
    r = h['dia'] / 2
    return [(h['cx'] - r - 2, h['cx'] + r + 2)]

def gap_liberi(occupati, lo, hi, need):
    occ = sorted((max(a, lo - 1), min(b, hi + 1)) for a, b in occupati if b > lo and a < hi)
    fusi = []
    for a, b in occ:
        if fusi and a <= fusi[-1][1]:
            fusi[-1][1] = max(fusi[-1][1], b)
        else:
            fusi.append([a, b])
    bordi = [lo] + [x for ab in fusi for x in ab] + [hi]
    out = []
    for i in range(0, len(bordi), 2):
        a, b = bordi[i], bordi[i + 1]
        if b - a >= need:
            out.append((a, b))
    return out

def need_gap():
    return max(6.0, -2 * S + 6.0) if S < 0 else 6.0

def area_sez(sh, x):
    fetta = sh.common(Part.makeBox(0.5, 20000, 20000, Base.Vector(x - 0.25, -10000, -10000)))
    return fetta.Volume / 0.5

def banda_prismatica(sh, a, b):
    """True se la sezione YZ e' costante nella banda [a,b] (nessuno scasso/finestra)."""
    xs = [a + 1.5, (3*a + b)/4, (a + b)/2, (a + 3*b)/4, b - 1.5]
    aree = [area_sez(sh, x) for x in xs]
    m = max(aree)
    if m <= 1e-6:
        return False
    return (m - min(aree)) / m < 0.002

def raffina_bande(sh, a, b, need):
    """Spezza [a,b] in sottobande ad area costante (i gap larghi possono contenere
    transizioni di sagoma: gola->pieno, bordo scasso...). Ritorna [(a1,b1,area)...]."""
    if b - a <= 30:
        return [(a, b, area_sez(sh, (a + b) / 2))]
    n = max(4, int((b - a) / 8))
    xs = [a + (b - a) * i / n for i in range(n + 1)]
    aree = [area_sez(sh, x) for x in xs]
    out = []
    i0 = 0
    for i in range(1, n + 1):
        base = max(aree[i0], 1e-6)
        if abs(aree[i] - aree[i0]) / base > 0.002 or i == n:
            fine = xs[i - 1] if i < n or abs(aree[i] - aree[i0]) / base > 0.002 else xs[i]
            if fine - xs[i0] >= need:
                out.append((xs[i0], fine, aree[i0]))
            i0 = i
    if not out and b - a >= need:
        out.append((a, b, area_sez(sh, (a + b) / 2)))
    return out

def scegli_taglio(sh, fori, lato, lab="", Astar=None):
    """Sceglie il taglio che minimizza i fori dalla parte sbagliata.
       lato: 'sim' (taglio a +/-c su |x|), 'sx' o 'dx' (taglio singolo)."""
    bbx = sh.BoundBox
    veto = veto_intervalli(sh)
    if lato == 'sim':
        occup = []
        for h in fori:
            for a, b in intervalli_foro(h):
                if b < 0:
                    a, b = -b, -a
                elif a < 0:
                    a = 0.0
                occup.append((a, b))
        for a, b in veto:
            if b < 0:
                a, b = -b, -a
            elif a < 0:
                a = 0.0
            occup.append((a, b))
        lim = min(-bbx.XMin, bbx.XMax) - 20
        gaps = gap_liberi(occup, 8.0, lim, need_gap())
        if not gaps:
            raise RuntimeError(f"{lab}: nessuna banda libera simmetrica")
        cand = []
        for a0, b0 in gaps:
            for a, b, area in raffina_bande(sh, a0, b0, need_gap()):
                c = (a + b) / 2
                mis = 0
                for h in fori:
                    x = abs(h['cx'])
                    if h['classe'] in ('SX', 'DX') and x < c: mis += 1
                    elif h['classe'] == 'FISSO' and x > c: mis += 1
                cand.append((mis, area, b - a, a, b, c))
        if not cand:
            raise RuntimeError(f"{lab}: nessuna banda libera simmetrica")
        # preferenza: PRIMA la geometria (area di taratura A*, a scaglioni di 2 cm2),
        # POI il misfit dei fori (i fori dalla parte sbagliata vengono comunque rilocati)
        if Astar:
            cand.sort(key=lambda t: (round(abs(t[1] - Astar * 100.0) / 200.0), t[0], -t[2]))
        else:
            cand.sort(key=lambda t: (t[0], -round(t[1], 1), -t[2]))
        for mis, area, amp, a, b, c in cand:
            area_sx = area_sez(sh, -c)
            if abs(area_sx - area) / max(area, 1e-6) > 0.002:
                continue  # sagoma asimmetrica (es. incavo canalina): banda inaffidabile
            if banda_prismatica(sh, a, b) and banda_prismatica(sh, -b, -a):
                return c, min((b - a) / 2 - 0.5, max(need_gap() / 2, 3.0))
        raise RuntimeError(f"{lab}: nessuna banda prismatica simmetrica")
    else:
        occup = [iv for h in fori for iv in intervalli_foro(h)] + veto
        gaps = gap_liberi(occup, bbx.XMin + 20, bbx.XMax - 20, need_gap())
        if not gaps:
            raise RuntimeError(f"{lab}: nessuna banda libera")
        cand = []
        for a0, b0 in gaps:
            for a, b, area in raffina_bande(sh, a0, b0, need_gap()):
                c = (a + b) / 2
                mis = 0
                for h in fori:
                    mobile = (h['cx'] > c) if lato == 'dx' else (h['cx'] < c)
                    if h['classe'] in ('SX', 'DX') and not mobile: mis += 1
                    elif h['classe'] == 'FISSO' and mobile: mis += 1
                cand.append((mis, area, b - a, a, b, c))
        if not cand:
            raise RuntimeError(f"{lab}: nessuna banda libera")
        if Astar:
            cand.sort(key=lambda t: (round(abs(t[1] - Astar * 100.0) / 200.0), t[0], -t[2]))
        else:
            cand.sort(key=lambda t: (t[0], -round(t[1], 1), -t[2]))
        for mis, area, amp, a, b, c in cand:
            if banda_prismatica(sh, a, b):
                return c, min((b - a) / 2 - 0.5, max(need_gap() / 2, 3.0))
        raise RuntimeError(f"{lab}: nessuna banda prismatica")

def shift_di(h, zona_shift, classe):
    """(spostamento subito dalla zona, spostamento voluto dalla classe)."""
    if classe == 'SX':  voluto = -S
    elif classe == 'DX': voluto = +S
    elif classe == 'FISSO': voluto = 0.0
    else: return zona_shift, None  # ALTRO: nessuna pretesa
    return zona_shift, voluto

def trasla_foro(h, dx):
    h2 = dict(h)
    h2['cx'] = h['cx'] + dx
    if h['dir'] == 'X':
        h2['lo'] = h['lo'] + dx; h2['hi'] = h['hi'] + dx
    return h2

def stira_con_classi(lab, sh, lato):
    fori = CLASSI.get(lab, [])
    if abs(S) < 1e-6:
        return sh.copy()
    bbx = sh.BoundBox
    Astar = TARATURA.get(lab, {}).get('Astar_cm2')
    c, hgap = scegli_taglio(sh, fori, lato, lab, Astar)
    if lato == 'sim':
        zone = [
            {'da': bbx.XMin - 1, 'a': -c - hgap, 'shift': -S},
            {'da': -c + hgap, 'a': c - hgap, 'shift': 0},
            {'da': c + hgap, 'a': bbx.XMax + 1, 'shift': +S}]
        def zshift(x):
            if x < -c: return -S
            if x > c: return +S
            return 0.0
    elif lato == 'dx':
        zone = [{'da': bbx.XMin - 1, 'a': c - hgap, 'shift': 0},
                {'da': c + hgap, 'a': bbx.XMax + 1, 'shift': +S}]
        def zshift(x):
            return +S if x > c else 0.0
    else:
        zone = [{'da': bbx.XMin - 1, 'a': c - hgap, 'shift': -S},
                {'da': c + hgap, 'a': bbx.XMax + 1, 'shift': 0}]
        def zshift(x):
            return -S if x < c else 0.0
    nuovo = slice_stretch(sh, zone)
    # rilocazioni: fori la cui zona non da' lo spostamento voluto dalla classe
    tappe, rifori = [], []
    for h in fori:
        zs = zshift(h['cx'])
        _, voluto = shift_di(h, zs, h['classe'])
        if voluto is None or abs(zs - voluto) < 0.25:
            continue
        tappe.append(trasla_foro(h, zs))       # dove il foro e' finito
        rifori.append(trasla_foro(h, voluto))  # dove deve stare
    print(f"  {lab}: taglio {lato} a {c:.1f} (semigap {hgap:.1f}), rilocati {len(tappe)}")
    if tappe:
        nuovo = tappa_fori(nuovo, tappe)
        nuovo = fora(nuovo, rifori)
    return nuovo

# ---------- generazione ----------
INTpos = None
for lab in ['03_Fianco_SX_INT', '031_Fianco_SX_INT']:
    if lab in shapes:
        b = shapes[lab].BoundBox; INTpos = abs((b.XMin + b.XMax) / 2); break

def classe_pannello(lab, cx):
    """Classe di un pannello che NON si stira: maggioranza delle classi dei suoi fori.
    (es. fianco INT J-03.01 = SX/DX perche' segue la baia; J-03.16 = FISSO a +/-676).
    Se prevale ALTRO (posizione scelta camera per camera, es. divisori J-03.02):
    resta FERMO come nel donatore."""
    voti = {'FISSO': 0, 'SX': 0, 'DX': 0}
    altro = 0
    for h in CLASSI.get(lab, []):
        if h['classe'] in voti:
            voti[h['classe']] += 1
        elif h['classe'] == 'ALTRO':
            altro += 1
    if altro >= 2 and altro > sum(voti.values()):
        print(f"  {lab}: posizione per-camera (fori ALTRO): resta come nel donatore")
        return 'FISSO'
    if sum(voti.values()) >= 2:
        return max(voti, key=lambda k: voti[k])
    if abs(cx) < 40:
        return 'FISSO'
    return 'SX' if cx < 0 else 'DX'

risultato = {}
for lab, sh in shapes.items():
    bbx = sh.BoundBox
    cx = (bbx.XMin + bbx.XMax) / 2
    larg = bbx.XMax - bbx.XMin
    spanning = larg > 0.6 * Wd
    anta = ('Frontale_Cassetto_SX' in lab or 'Frontale_Cassetto_DX' in lab) and larg > 380 and TIPO != 'J-03.01'
    cx01 = TIPO == 'J-03.01' and 'Frontale_Cassetto_CX' in lab
    if spanning or cx01:
        risultato[lab] = stira_con_classi(lab, sh, 'sim')
    elif anta:
        risultato[lab] = stira_con_classi(lab, sh, 'dx' if cx > 0 else 'sx')
    else:
        cl = classe_pannello(lab, cx)
        s = {'FISSO': 0.0, 'SX': -S, 'DX': +S}[cl]
        f = sh.copy(); f.translate(Base.Vector(s, 0, 0)); risultato[lab] = f

for lab, comp in comps.items():
    bbx = comp.BoundBox; cx = (bbx.XMin + bbx.XMax) / 2
    if abs(cx) < 40:
        risultato[lab] = comp.copy()
    else:
        s = -S if cx < 0 else +S
        f = comp.copy(); f.translate(Base.Vector(s, 0, 0)); risultato[lab] = f

# ---------- controlli ----------
ok = True
for lab, forma in risultato.items():
    if not forma.isValid():
        print(f"  *** {lab}: NON valido"); ok = False
    if len(forma.Solids) not in (1, 5):
        print(f"  *** {lab}: {len(forma.Solids)} solidi"); ok = False
wtot = max(f.BoundBox.XMax for f in risultato.values()) - min(f.BoundBox.XMin for f in risultato.values())
if abs(wtot - W) > 0.3:
    print(f"  *** larghezza totale {wtot:.2f} != {W}"); ok = False
print(f"controlli: {'OK' if ok else 'PROBLEMI'} | Ltot={wtot:.1f}")

# ---------- export ----------
doc2 = App.newDocument("out")
root = doc2.addObject("App::Part", "root"); root.Label = TIPO
def etichette_cassetto(comp, dx01):
    """Assegna ai 5 solidi del cassetto i nomi del disegno originale."""
    solids = list(comp.Solids)
    fondo = min(solids, key=lambda x: x.BoundBox.ZLength)
    resto = [x for x in solids if x is not fondo]
    thinX = sorted([x for x in resto if x.BoundBox.XLength < 15], key=lambda x: x.BoundBox.XMin)
    thinY = sorted([x for x in resto if x.BoundBox.XLength >= 15], key=lambda x: x.BoundBox.YMin)
    if len(thinX) != 2 or len(thinY) != 2:
        return [(f'Cassetto_{i}', x) for i, x in enumerate(solids)]
    if dx01:
        return [('15_Sponda_SX001', thinX[0]), ('16_Sponda_DX001', thinX[1]),
                ('19_Traversa_DX', thinY[0]), ('17_Schiena001', thinY[1]), ('20_Fondo001', fondo)]
    return [('15_Sponda_SX', thinX[0]), ('16_Sponda_DX', thinX[1]),
            ('18_Traversa_SX', thinY[0]), ('17_Schiena', thinY[1]), ('20_Fondo', fondo)]

n = 0
for lab in sorted(risultato):
    forma = risultato[lab]
    if len(forma.Solids) >= 3:
        dx01 = TIPO == 'J-03.01' and (forma.BoundBox.XMin + forma.BoundBox.XMax) / 2 > 0
        for sub_lab, sol in etichette_cassetto(forma, dx01):
            n += 1; fe = doc2.addObject("Part::Feature", f"f{n}")
            fe.Label = sub_lab; fe.Shape = sol; root.addObject(fe)
        continue
    n += 1; fe = doc2.addObject("Part::Feature", f"f{n}")
    fe.Label = lab; fe.Shape = forma; root.addObject(fe)
Import.export([root], OUT)
print("SCRITTO", OUT)
App.closeDocument(doc.Name); App.closeDocument(doc2.Name)
