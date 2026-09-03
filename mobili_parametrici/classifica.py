# -*- coding: utf-8 -*-
"""
Classifica OGNI foro di OGNI pannello di OGNI esemplare confrontando gli esemplari
della stessa tipologia. Classi:
  FISSO  = stessa x in tutti (elemento del centro / scasso)
  SX     = segue il bordo sinistro (x + W/2 costante) o il fianco INT sinistro
  DX     = segue il bordo destro o il fianco INT destro
  ALTRO  = spine/fori ridistribuiti (nessuna legge stabile)
Output: classi_fori.json  { file: { pannello: [ {dir,dia,cx,cy,cz,lo,hi,classe} ] } }
"""
import json, glob, re, os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
TOL = 0.5

def tipo_di(k):
    m = re.search(r'J-03[._](\d+)', k)
    return 'J-03.' + m.group(1) if m else '?'

tot = {}
for f in glob.glob(os.path.join(BASE, 'estratto_b*.json')):
    tot.update(json.load(open(f, encoding='utf-8')))

def ctx_di(inst):
    bb = inst['assembly']['bbox']
    W = bb[3] - bb[0]
    c = {'W': W, 'hw': W/2}
    for lab in inst['panels']:
        if re.match(r'0?3\d*_Fianco_SX_INT$', lab):
            b = inst['panels'][lab]['bbox']; c['intL'] = (b[0]+b[3])/2
        if re.match(r'0?4\d*_Fianco_DX_INT$', lab):
            b = inst['panels'][lab]['bbox']; c['intR'] = (b[0]+b[3])/2
    return c

def riga_key(h):
    if h['dir'] == 'X':
        return ('X', round(h['dia'],1), round(h['cy']), round(h['cz']))
    if h['dir'] == 'Y':
        return ('Y', round(h['dia'],1), round(h['cz']), round(h['len']))
    return ('Z', round(h['dia'],1), round(h['cy']), round(h['lo']), round(h['len']))

LEGGI = [('FISSO', lambda x, c: x),
         ('SX',    lambda x, c: x + c['hw']),
         ('DX',    lambda x, c: c['hw'] - x),
         ('SX',    lambda x, c: (x - c['intL']) if 'intL' in c else None),
         ('DX',    lambda x, c: (c['intR'] - x) if 'intR' in c else None)]

out = {}
gruppi = defaultdict(list)
for k, v in tot.items():
    if 'error' in v or not v.get('assembly'):
        continue
    if 'ADA' in k or 'Schiena.stp' in k:
        continue
    gruppi[tipo_di(k)].append(k)

for tipo, files in gruppi.items():
    ctxs = {k: ctx_di(tot[k]) for k in files}
    pannelli = set()
    for k in files:
        pannelli |= set(tot[k]['panels'].keys())
    for k in files:
        out.setdefault(k, {})
    for lab in pannelli:
        use = [k for k in files if lab in tot[k]['panels']]
        righe = defaultdict(dict)
        for k in use:
            for h in tot[k]['panels'][lab]['fori']:
                if h['dia'] >= 30:
                    continue
                righe[riga_key(h)].setdefault(k, []).append(h)
        for rk, per in righe.items():
            pres = [k for k in use if per.get(k)]
            residui = {k: list(per[k]) for k in pres}
            # greedy: per ogni foro del primo file, prova le leggi
            for k0 in pres:
                for h0 in per[k0]:
                    if h0 not in residui[k0]:
                        continue
                    assegnato = None
                    for nome, fn in LEGGI:
                        p0 = fn(h0['cx'], ctxs[k0])
                        if p0 is None:
                            continue
                        trovati = {}
                        for k in pres:
                            best = None
                            for h in residui[k]:
                                v = fn(h['cx'], ctxs[k])
                                if v is not None and abs(v - p0) <= TOL:
                                    best = h; break
                            if best is None:
                                break
                            trovati[k] = best
                        if len(trovati) == len(pres):
                            for k, h in trovati.items():
                                residui[k].remove(h)
                                out[k].setdefault(lab, []).append(
                                    {**{q: h[q] for q in ('dir','dia','cx','cy','cz','lo','hi')},
                                     'classe': nome})
                            assegnato = nome
                            break
                    if assegnato is None and h0 in residui[k0]:
                        pass  # restera' come ALTRO nel giro sotto
            for k in pres:
                for h in residui[k]:
                    out[k].setdefault(lab, []).append(
                        {**{q: h[q] for q in ('dir','dia','cx','cy','cz','lo','hi')},
                         'classe': 'ALTRO'})

fn = os.path.join(BASE, 'classi_fori.json')
json.dump(out, open(fn, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
# riepilogo
for k in sorted(out):
    n = defaultdict(int)
    for lab, hh in out[k].items():
        for h in hh:
            n[h['classe']] += 1
    print(f"{k:40s} FISSO={n['FISSO']:3d} SX={n['SX']:3d} DX={n['DX']:3d} ALTRO={n['ALTRO']:3d}")
