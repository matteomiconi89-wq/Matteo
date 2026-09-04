#!/usr/bin/env python3
"""Integra la SCOCCA reale del veicolo (STEP) al posto dei volumi semplificati.

Lo STEP della scocca e' un unico "Skeleton" che contiene 146 solidi: 126 pannelli
da 10-40 mm, 7 vetri, 5 telai e 8 volumi grossi. Gli 8 volumi non sono costruzione
ma INGOMBRI (il cassone, i quattro slider che escono, i due estrattori, la platea
del pavimento): renderizzarli come solidi riempirebbe le stanze, quindi vengono
tenuti da parte.

Il resto sono i divisori veri del cassone — telai, pannelli, vetri e porte — che
finora avevo approssimato con 8 volumi a scatola presi dal DXF.

Alcuni divisori vetrati della scocca attraversano gli armadi delle due camere.
Non e' un errore di posizionamento: gli offset sono ancorati agli ingombri della
scocca (larghezza 4840 esatta) e confermati dal tramezzo del bagno anteriore e
dai rivestimenti laterali, che cadono sulle polilinee della pianta. Sono i due
disegni a non concordare. L'arredo e' esecutivo e verificato sulla pianta, quindi
gli elementi che lo attraversano vengono messi da parte (gruppo CONFLITTO) invece
di finire nel render, e vanno chiariti con l'ufficio tecnico.

Coordinate dello STEP -> trailer:  X+30, Y+2420, Z+1095
(la quota Z e' agganciata al pavimento: i divisori partono da Z 300 nello STEP,
che e' il piano di calpestio PAV=1395).

    python3 integra_scocca.py
"""
import json, pathlib
import cadquery as cq
from cadquery import exporters
from step_assembly import read_assembly
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID

HERE = pathlib.Path(__file__).parent
STEP = pathlib.Path("/root/.claude/uploads/31efb9b7-647e-5589-8875-ea5660dd57ca"
                    "/07972229-26A011_Scocca.stp")
OFF = (30.0, 2420.0, 1095.0)
PAV, SOFFITTO = 1395.0, 3688.0


def classifica(b):
    """dal solo ingombro capisce che cos'e' il pezzo"""
    dx, dy, dz = b.xmax - b.xmin, b.ymax - b.ymin, b.zmax - b.zmin
    sp = min(dx, dy, dz)
    if sp > 120:
        return 'INGOMBRO', None                      # cassone, slider, estrattori, platea
    if sp <= 10:
        return 'VETRO', 'F_VETRO'
    if dz < 60 and b.zmin > SOFFITTO - 200:
        return 'CONTROSOFFITTO', 'F_MULTI laminato_soffitto'
    if dz < 60 and b.zmin < PAV + 100:
        return 'PAVIMENTO', 'F_PARETI-PAVIMENTI e SOFFITTI_cassone'
    if dz > 1500:
        return ('TELAIO_DIVISORIO', 'F_PROFILI_metallo') if sp > 40 else \
               ('DIVISORIO', 'F_PARETI-PAVIMENTI e SOFFITTI_cassone')
    return 'SCOCCA', 'F_PARETI-PAVIMENTI e SOFFITTI_cassone'


def solidi(path):
    out = []
    for _, sh in read_assembly(str(path)):
        ex = TopExp_Explorer(sh, TopAbs_SOLID)
        while ex.More():
            out.append(cq.Shape.cast(ex.Current()))
            ex.Next()
    return out


if __name__ == '__main__':
    tutti = [s.translate(cq.Vector(*OFF)) for s in solidi(STEP)]
    render, ingombri, conto = [], [], {}
    for s in tutti:
        tipo, mat = classifica(s.BoundingBox())
        conto[tipo] = conto.get(tipo, 0) + 1
        (ingombri if tipo == 'INGOMBRO' else render).append((tipo, mat, s))

    # scarta dal render gli elementi che compenetrano l'arredo (vedi sopra)
    geo = HERE.parent / 'arredo_geometry.json'
    G = json.load(open(geo))
    arredo = []
    for parts in G['mobili'].values():
        for m in parts:
            V = m['v']
            arredo.append((min(c[0] for c in V), max(c[0] for c in V),
                           min(c[1] for c in V), max(c[1] for c in V),
                           min(c[2] for c in V), max(c[2] for c in V)))

    def tocca(b):
        """vero conflitto: solo per i divisori verticali, e con compenetrazione
        significativa. I pannelli del controsoffitto che sfiorano la veletta di un
        armadio per pochi mm non sono un conflitto."""
        if b.zmax - b.zmin < 1000:
            return False                    # solo divisori verticali
        r = (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)
        for a in arredo:
            d = [min(r[2*i+1], a[2*i+1]) - max(r[2*i], a[2*i]) for i in range(3)]
            if min(d) > 0 and d[0] * d[1] * d[2] > 1e5:   # oltre 0,1 dm3 di compenetrazione
                return True
        return False

    puliti, conflitto = [], []
    for tipo, mat, s in render:
        (conflitto if tocca(s.BoundingBox()) else puliti).append((tipo, mat, s))
    conto['CONFLITTO_con_arredo'] = len(conflitto)
    render = puliti

    mesh = []
    for i, (tipo, mat, s) in enumerate(render):
        v, t = s.tessellate(0.5)
        mesh.append({'l': f'SC_{i:03d}_{tipo}', 'm': mat,
                     'v': [[round(a.x, 1), round(a.y, 1), round(a.z, 1)] for a in v],
                     'f': [[int(k) for k in f] for f in t]})

    G['aperto'] = mesh
    G['_note'] = (G.get('_note', '') + ' | scocca: STEP reale di Matteo, '
                  f'{len(render)} elementi costruttivi; {len(ingombri)} volumi di '
                  f'ingombro (cassone, slider, estrattori, platea) e {len(conflitto)} '
                  'divisori che compenetrano l\'arredo, esclusi dal render.')
    json.dump(G, open(geo, 'w'), separators=(',', ':'))

    exporters.export(cq.Compound.makeCompound([s for _, _, s in render]),
                     str(HERE / 'mobili' / 'scocca_posizionata.step'))
    for k in sorted(conto, key=lambda k: -conto[k]):
        print(f"  {conto[k]:4d}  {k}")
    print(f"\n{len(render)} elementi nel render, {len(ingombri)} volumi di ingombro e "
          f"{len(conflitto)} divisori in conflitto esclusi")
    if conflitto:
        print("\ndivisori che attraversano l'arredo (da chiarire):")
        for tipo, _, s in conflitto:
            b = s.BoundingBox()
            print(f"   {tipo:18s} X[{b.xmin:7.0f},{b.xmax:7.0f}] "
                  f"Y[{b.ymin:6.0f},{b.ymax:6.0f}] Z[{b.zmin:6.0f},{b.zmax:6.0f}]")
