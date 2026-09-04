#!/usr/bin/env python3
"""ARMADIO camera doppia — ricostruito col SISTEMA COSTRUTTIVO REALE di Matteo.

Regole prese dal suo STEP dell'armadio master (26A011_ArmadioCameraMaster.stp):
  pannelli 18 mm; fianco 18x580x2040 (Z 5.5..2045.5); base/cielo 18 (Z 5.5..23.5 / 2027.5..2045.5);
  schiena 18 (Y 2..20, Z 23.5..2027.5); ripiano 18 prof 548 (Y 21..569), passo 268 da Z 273.5;
  anta 18 (Y 581..599, Z 5..2055); spalletta/fascia/veletta sul piano Y 542..560;
  veletta Z 2045.5..2105; montante 30x60 (Y 560..620, Z 0..2055);
  cassettiera: fianchetti Y 20..550 Z 23.5..583.5, cassetti frontali 180 alti a Z 33.5/216.5/399.5.

Posizioni dalla PLANIMETRIA: fianchi a X 11441,11891,11974,12404,12462,12892,12975,13425
(offset trailer del modello = 11382). I vuoti tra le casse risultano 65/40/65 = fascia65 x2 +
fascia40 x1, e 50 agli estremi = spalletta x2, coerente con la distinta del DWG (90 solidi).

Distinta DWG: AD1 (6 ripiani, schiena), AD2 (2 ripiani, schiena), AD3/AD4 (senza schiena
-> cassettiere), + 2 fascia65, 1 fascia40, 2 spalletta, 4 montante, veletta, 2 cassettiere x3 cassetti.
NB: provvisorio finche' Matteo non manda lo .stp della doppia.
"""
import cadquery as cq, json, pathlib
from cadquery import exporters
HERE = pathlib.Path(__file__).parent
PAV = 1395.0
OFF = (11382.0, 49.0, PAV)          # locale -> trailer

def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0))

# casse: (tag, x_outer_sx, x_outer_dx, n_ripiani, schiena, cassettiera, appenderia)
# assegnazione dalla PIANTA: casse 1 e 4 hanno il bastone appendiabiti (abiti disegnati),
# con cassettiera sotto; casse 2 e 3 a ripiani (6 e 2, come da distinta DWG).
CASSE = [('AD1',  50.0,  518.0, 0, False, True,  True),
         ('AD2', 583.0, 1031.0, 6, True,  False, False),
         ('AD3',1071.0, 1519.0, 2, True,  False, False),
         ('AD4',1584.0, 2052.0, 0, False, True,  True)]
W = 2102.0
T = 18.0
parts = []          # (nome, solido)

for tag, xo0, xo1, nrip, schiena, ctra, appe in CASSE:
    xi0, xi1 = xo0+T, xo1-T                       # interno cassa
    parts.append((f'{tag}_FIANCO_DX', box(xo0, xo0+T, 0, 580, 5.5, 2045.5)))
    parts.append((f'{tag}_FIANCO_SX', box(xo1-T, xo1, 0, 580, 5.5, 2045.5)))
    parts.append((f'{tag}_BASE',      box(xi0, xi1, 0, 580, 5.5, 23.5)))
    parts.append((f'{tag}_CIELO',     box(xi0, xi1, 0, 580, 2027.5, 2045.5)))
    if schiena:
        parts.append((f'{tag}_SCHIENA', box(xi0, xi1, 2, 20, 23.5, 2027.5)))
    for k in range(nrip):
        z = 273.5 + k*268.0
        if z+18 < 2027: parts.append((f'{tag}_RIPIANO', box(xi0+0.5, xi1-0.5, 21, 569, z, z+18)))
    parts.append((f'{tag}_ANTA', box(xo0+3, xo1+5, 581, 599, 5, 2055)))
    if appe:                                      # bastone appendiabiti (come da pianta)
        parts.append((f'{tag}_BASTONE', cq.Workplane('XY').cylinder(xi1-xi0-20, 15,
                      direct=(1,0,0), centered=True).translate(((xi0+xi1)/2, 295, 1750))))
    if ctra:                                      # cassettiera dentro la cassa + 3 cassetti
        cx0, cx1 = xi0+18, xi1-18                 # sta DENTRO l'interno cassa
        parts.append(('AD_CTRA_FIANCHETTO_DX', box(cx0, cx0+T, 20, 550, 23.5, 583.5)))
        parts.append(('AD_CTRA_FIANCHETTO_SX', box(cx1-T, cx1, 20, 550, 23.5, 583.5)))
        parts.append(('AD_CTRA_FONDO',  box(cx0+T, cx1-T, 20, 550, 23.5, 41.5)))
        parts.append(('AD_CTRA_TOP',    box(cx0+T, cx1-T, 20, 550, 565.5, 583.5)))
        parts.append(('AD_CTRA_SCHIENALINO', box(cx0+T, cx1-T, 20, 38, 41.5, 565.5)))
        parts.append(('AD_DIST_CASSETTIERA', box(cx0-30, cx0, 532, 550, 23.5, 583.5)))
        for z0 in (33.5, 216.5, 399.5):
            parts.append(('AD_CASSETTO_FRONTALE', box(cx0+3, cx1-3, 550, 568, z0, z0+180)))
            parts.append(('AD_CASSETTO_SPONDA_DX', box(cx0+T, cx0+T+18, 40, 530, z0+8, z0+158)))
            parts.append(('AD_CASSETTO_SPONDA_SX', box(cx1-T-18, cx1-T, 40, 530, z0+8, z0+158)))
            parts.append(('AD_CASSETTO_FONDO', box(cx0+T, cx1-T, 40, 494, z0+8, z0+18)))

# elementi comuni sul fronte (piano Y 542..560)
parts.append(('AD_SPALLETTA', box(0, 50, 542, 560, 0, 2045.5)))
parts.append(('AD_SPALLETTA', box(W-50, W, 542, 560, 0, 2045.5)))
parts.append(('AD_FASCIA65',  box(518, 583, 542, 560, 0, 2045.5)))
parts.append(('AD_FASCIA65',  box(1519, 1584, 542, 560, 0, 2045.5)))
parts.append(('AD_FASCIA40',  box(1031, 1071, 542, 560, 0, 2045.5)))
parts.append(('AD_VELETTA',   box(0, W, 542, 560, 2045.5, 2105)))
for mx in (10, 531, 1531, W-40):
    parts.append(('AD_MONTANTE', box(mx, mx+30, 560, 620, 0, 2055)))

def colore(n):
    n = n.upper()
    if 'ANTA' in n: return '#7a5a36'
    if 'CASSETTO' in n or 'CTRA' in n: return '#8a6a42'
    if 'RIPIANO' in n: return '#c9a878'
    if 'FASCIA' in n or 'VELETTA' in n or 'SPALLETTA' in n: return '#6f5334'
    if 'MONTANTE' in n: return '#b8946a'
    return '#96733f'

sol = [s.val().translate(cq.Vector(*OFF)) for _, s in parts]
comp = cq.Compound.makeCompound(sol)
exporters.export(comp, str(HERE/'armadio_doppia_posizionato.step'))
mesh = []
for (n, _), s in zip(parts, sol):
    v, t = s.tessellate(0.4)
    mesh.append({'l': n, 'c': colore(n),
                 'v': [[round(a.x,1), round(a.y,1), round(a.z,1)] for a in v],
                 'f': [[int(i) for i in f] for f in t]})
json.dump(mesh, open(HERE/'armadio_doppia_mesh.json','w'), separators=(',',':'))
bb = comp.BoundingBox()
print(f"armadio doppia: {len(parts)} pezzi  vol={comp.Volume()/1e9:.3f} m3  "
      f"X[{bb.xmin:.0f},{bb.xmax:.0f}] Y[{bb.ymin:.0f},{bb.ymax:.0f}] Z[{bb.zmin:.0f},{bb.zmax:.0f}]")
