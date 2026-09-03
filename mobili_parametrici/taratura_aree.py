# -*- coding: utf-8 -*-
"""
Taratura delle AREE DI INSERZIONE dai dati reali: per ogni tipologia/taglia e ogni
pannello, A* = dV/dW tra coppie di esemplari della stessa taglia = sezione (cm2) del
punto dove il CAD inserisce materiale. Il generatore scegliera' la banda di taglio
con area il piu' vicina possibile ad A*.
Output: taratura_aree.json  {tipo: {taglia: {pannello: {"Astar_cm2":..,"lato":"sim|anta"}}}}
"""
import json, glob, os
from statistics import median

BASE = os.path.dirname(os.path.abspath(__file__))
tot = {}
for f in glob.glob(os.path.join(BASE, 'estratto_b*.json')):
    tot.update(json.load(open(f, encoding='utf-8')))

# coppie di calibrazione (stessa taglia, W crescente)
COPPIE = {
 ('J-03.01', '350'): [('21032_C107_J-03_01.stp', '21032_M06_J-03_01.stp')],
 ('J-03.01', '400'): [('Set_17_A203_J-03.01.stp', 'Set_18_A110_J-03.01.stp'),
                      ('Set_18_A110_J-03.01.stp', '21032_M08_J-03_01.stp')],
 ('J-03.16', 'INT'): [('21032_C101-102_J-03_16_bis.stp', 'Set_18_A105_J-03.16.stp'),
                      ('Set_18_A105_J-03.16.stp', '21032_C110_J-03_16.stp'),
                      ('21032_C110_J-03_16.stp', '21032_C204_J-03_16.stp'),
                      ('21032_C204_J-03_16.stp', 'Set_17_A107_J-03.16.stp')],
 ('J-03.02', '1INT'): [('Set_17_B207_J-03.02.stp', 'Set_17_B208_J-03.02.stp')],
}
# pannelli che si stirano simmetrici e ante (per tipo)
SIM = ['05_Sottotop', '06_Piano_Sottolavabo', '07_Schiena', '08_Frontale_Fisso',
       '10_Base', '11_Zoccolo', '09_Frontale_Cassetto_CX']
ANTE = ['09_Frontale_Cassetto_SX', '09_Frontale_Cassetto_DX']

def W_di(k):
    bb = tot[k]['assembly']['bbox']
    return bb[3] - bb[0]

out = {}
for (tipo, taglia), coppie in COPPIE.items():
    acc = {}
    for a, b in coppie:
        Wa, Wb = W_di(a), W_di(b)
        dW = Wb - Wa
        if dW < 5:
            continue
        for lab in SIM + ANTE:
            pa = tot[a]['panels'].get(lab)
            pb = tot[b]['panels'].get(lab)
            if not pa or not pb:
                continue
            dV = pb['volume_cm3'] - pa['volume_cm3']
            if lab in ANTE:
                Astar = dV / (dW / 2.0 / 10.0)   # l'anta cresce di dW/2
            else:
                Astar = dV / (dW / 10.0)          # cresce dW totale (dW/2 per lato, 2 lati)
            acc.setdefault(lab, []).append(round(Astar, 2))
    out.setdefault(tipo, {})[taglia] = {
        lab: {'Astar_cm2': round(median(v), 2), 'campioni': v,
              'lato': 'anta' if lab in ANTE else 'sim'}
        for lab, v in acc.items()}

# sanificazione: le coppie possono essere contaminate da differenze REALI tra camere
# (es. scassi lavabo diversi): ogni taglia viene confrontata con la taglia di riferimento
# pulita della tipologia; valori oltre il 25% di scarto (o assurdi) vengono sostituiti.
RIF = {'J-03.01': '350', 'J-03.16': 'INT', 'J-03.02': '1INT'}
for tipo, tt in out.items():
    rif = out[tipo][RIF[tipo]]
    for taglia, pp in tt.items():
        if taglia == RIF[tipo]:
            continue
        for lab, d in pp.items():
            r = rif.get(lab)
            if not r:
                continue
            a, ar = d['Astar_cm2'], r['Astar_cm2']
            if ar > 1 and (a < 1 or abs(a - ar) / ar > 0.25):
                d['Astar_cm2'] = ar
                d['nota'] = 'sostituito dal riferimento (coppia contaminata da differenze di camera)'

# fallback: taglie senza coppia ereditano dalla taglia vicina della stessa tipologia
out['J-03.01']['310'] = out['J-03.01']['350']
out['J-03.01']['450'] = out['J-03.01']['400']
out['J-03.16']['noINT'] = out['J-03.16']['INT']
out['J-03.02']['2INT'] = out['J-03.02']['1INT']

fn = os.path.join(BASE, 'taratura_aree.json')
json.dump(out, open(fn, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
for tipo, tt in out.items():
    for taglia, pp in tt.items():
        riga = " ".join(f"{lab.split('_',1)[1][:12]}={d['Astar_cm2']}" for lab, d in sorted(pp.items()))
        print(f"{tipo} [{taglia}]: {riga}")
