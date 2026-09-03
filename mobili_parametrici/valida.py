# -*- coding: utf-8 -*-
"""
Validazione: confronta STEP generato vs originale, pannello per pannello, foro per foro.
Env: VAL_GEN, VAL_RIF (percorsi STEP), VAL_OUT (json report).
"""
import os, sys, json
import FreeCAD as App
import Part, Import
from FreeCAD import Base

GEN = os.environ['VAL_GEN']; RIF = os.environ['VAL_RIF']
OUT = os.environ.get('VAL_OUT', '')

SUB_CASS = {'15_Sponda_SX', '15_Sponda_SX001', '16_Sponda_DX', '16_Sponda_DX001',
            '17_Schiena', '17_Schiena001', '18_Traversa_SX', '19_Traversa_DX',
            '20_Fondo', '20_Fondo001'}

def axdir(d):
    for name, v in (("X", Base.Vector(1,0,0)), ("Y", Base.Vector(0,1,0)), ("Z", Base.Vector(0,0,1))):
        if abs(abs(d.dot(v)) - 1.0) < 1e-6:
            return name
    return "OBL"

def fori_di(sh):
    holes = {}
    for face in sh.Faces:
        s = face.Surface
        if s.__class__.__name__ != 'Cylinder':
            continue
        c = s.Center; dn = axdir(s.Axis); r = round(s.Radius, 2)
        if 2*r >= 30:  # archi di scasso: confrontati via volume/bbox
            continue
        if dn == 'X':
            k = (dn, r, round(c.y,1), round(c.z,1)); lo, hi = face.BoundBox.XMin, face.BoundBox.XMax
        elif dn == 'Y':
            k = (dn, r, round(c.x,1), round(c.z,1)); lo, hi = face.BoundBox.YMin, face.BoundBox.YMax
        elif dn == 'Z':
            k = (dn, r, round(c.x,1), round(c.y,1)); lo, hi = face.BoundBox.ZMin, face.BoundBox.ZMax
        else:
            continue
        e = holes.setdefault(k, {'dir': dn, 'dia': 2*r, 'cx': c.x, 'cy': c.y, 'cz': c.z, 'lo': lo, 'hi': hi})
        e['lo'] = min(e['lo'], lo); e['hi'] = max(e['hi'], hi)
    return list(holes.values())

def carica(path):
    doc = App.newDocument("v")
    Import.insert(path, doc.Name)
    pan = {}
    for o in doc.Objects:
        if not (hasattr(o, 'Shape') and o.Shape.Solids):
            continue
        lab = o.Label
        ns = len(o.Shape.Solids)
        if lab.startswith('SOLID') or lab.startswith('J-') or lab.endswith('_Skeleton'):
            # tieni solo i compound cassetto
            if 'Cassetto' in lab and ns == 5:
                pan[lab] = o.Shape.copy()
            continue
        if lab in SUB_CASS:
            continue  # sotto-pezzi: nel generato li raggruppo sotto, nell'orig sono in coord locali
        if ns == 1 and lab not in pan:
            pan[lab] = o.Shape.copy()
    # nel file GENERATO i cassetti sono 5 feature globali: ricomponili
    gen_sub = {}
    for o in doc.Objects:
        if hasattr(o, 'Shape') and o.Shape.Solids and o.Label in SUB_CASS and len(o.Shape.Solids) == 1:
            gen_sub[o.Label] = o.Shape.copy()
    if gen_sub and not any('Cassetto' in l for l in pan):
        sx = [gen_sub[l] for l in ['15_Sponda_SX','16_Sponda_DX','17_Schiena','18_Traversa_SX','20_Fondo'] if l in gen_sub]
        dx = [gen_sub[l] for l in ['15_Sponda_SX001','16_Sponda_DX001','17_Schiena001','19_Traversa_DX','20_Fondo001'] if l in gen_sub]
        if len(sx) == 5: pan['J-03.01_Cassetto_SX'] = Part.makeCompound(sx)
        if len(dx) == 5: pan['J-03.01_Cassetto_DX'] = Part.makeCompound(dx)
    App.closeDocument(doc.Name)
    return pan

TOL = 0.3
def confronta_cassetti(g, r):
    """Confronta i compound cassetto per volume e n. cilindri (geometria complessiva)."""
    out = {}
    for lab in ['J-03.01_Cassetto_SX', 'J-03.01_Cassetto_DX']:
        if lab in g and lab in r:
            vg, vr = g[lab].Volume, r[lab].Volume
            cg = sum(1 for f in g[lab].Faces if f.Surface.__class__.__name__ == 'Cylinder')
            cr = sum(1 for f in r[lab].Faces if f.Surface.__class__.__name__ == 'Cylinder')
            out[lab] = {'vol_diff_pct': round(abs(vg-vr)/max(vr,1)*100, 3), 'cil_g': cg, 'cil_r': cr,
                        'esito': 'OK' if abs(vg-vr)/max(vr,1) < 0.005 and cg == cr else 'DIFF'}
    return out

g = carica(GEN); r = carica(RIF)
rep = {'gen': GEN, 'rif': RIF, 'pannelli': {}, 'solo_gen': sorted(set(g) - set(r)), 'solo_rif': sorted(set(r) - set(g))}
tot_mancanti = tot_extra = tot_spostati = 0
for lab in sorted(set(g) & set(r)):
    sg, sr = g[lab], r[lab]
    bg, br = sg.BoundBox, sr.BoundBox
    dbb = max(abs(bg.XMin-br.XMin), abs(bg.XMax-br.XMax), abs(bg.YMin-br.YMin),
              abs(bg.YMax-br.YMax), abs(bg.ZMin-br.ZMin), abs(bg.ZMax-br.ZMax))
    dvol = abs(sg.Volume - sr.Volume) / max(sr.Volume, 1)
    fg, fr = fori_di(sg), fori_di(sr)
    # match greedy fori
    # firma geometrica reale: coordinate PERPENDICOLARI all'asse + estensione lo/hi.
    # La coordinata lungo l'asse (cx per X, cy per Y, cz per Z) e' un base-point
    # arbitrario del cilindro STEP: si ignora (ridondante con lo/hi).
    def perp(h):
        if h['dir'] == 'X': return (h['cy'], h['cz'])
        if h['dir'] == 'Y': return (h['cx'], h['cz'])
        return (h['cx'], h['cy'])
    resti_r = list(fr); mancanti = []; extra = []
    for h in fg:
        best = None
        pa = perp(h)
        for h2 in resti_r:
            pb = perp(h2)
            if h2['dir']==h['dir'] and abs(h2['dia']-h['dia'])<0.05 and \
               abs(pb[0]-pa[0])<TOL and abs(pb[1]-pa[1])<TOL and \
               abs(h2['lo']-h['lo'])<TOL and abs(h2['hi']-h['hi'])<TOL:
                best = h2; break
        if best is not None:
            resti_r.remove(best)
        else:
            extra.append(h)
    mancanti = resti_r
    e = {'bbox_diff': round(dbb,3), 'vol_diff_pct': round(dvol*100,3),
         'fori_gen': len(fg), 'fori_rif': len(fr),
         'fori_mancanti': [{k: round(v,2) if isinstance(v,float) else v for k,v in h.items()} for h in mancanti],
         'fori_extra': [{k: round(v,2) if isinstance(v,float) else v for k,v in h.items()} for h in extra]}
    ok = dbb <= TOL and dvol < 0.005 and not mancanti and not extra
    e['esito'] = 'OK' if ok else 'DIFF'
    rep['pannelli'][lab] = e
    tot_mancanti += len(mancanti); tot_extra += len(extra)
    print(f"{'OK ' if ok else 'DIFF'} {lab:32s} bbox{dbb:7.3f} vol%{dvol*100:7.3f} fori {len(fg):3d}/{len(fr):3d} manc={len(mancanti)} extra={len(extra)}")
cass = confronta_cassetti(g, r)
for lab, e in cass.items():
    print(f"{'OK ' if e['esito']=='OK' else 'DIFF'} {lab:32s} vol%{e['vol_diff_pct']:7.3f} cil {e['cil_g']}/{e['cil_r']}")
rep['cassetti'] = cass
print(f"TOTALE: mancanti={tot_mancanti} extra={tot_extra} solo_gen={rep['solo_gen']} solo_rif={rep['solo_rif']}")
if OUT:
    json.dump(rep, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('report:', OUT)
