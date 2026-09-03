# -*- coding: utf-8 -*-
"""
Motore geometrico del generatore parametrico (gira dentro freecadcmd).
Operazioni chiave:
 - slice_stretch: taglia un solido in zone lungo X, trasla ogni zona, ricostruisce i corridoi
   per estrusione della sezione (funziona per qualsiasi profilo prismatico nel corridoio)
 - tappa_fori / fora: riempie e riesegue i fori cilindrici
"""
import FreeCAD as App
import Part
from FreeCAD import Base

BIG = 10000.0
TOLL = 1e-4


def _box_x(x0, x1):
    """Parallelepipedo che copre tutto tranne in X (per common)."""
    return Part.makeBox(x1 - x0, 2 * BIG, 2 * BIG, Base.Vector(x0, -BIG, -BIG))


def _sezione_faces(pezzo, x, verso):
    """Facce piane del pezzo giacenti sul piano X=x (facce nate dal taglio)."""
    out = []
    for f in pezzo.Faces:
        s = f.Surface
        if s.__class__.__name__ != 'Plane':
            continue
        n = s.Axis
        if abs(abs(n.x) - 1.0) > 1e-7:
            continue
        if abs(s.Position.x - x) < 1e-5:
            out.append(f)
    return out


def slice_stretch(solido, zone):
    """
    zone: lista ordinata di dict {'da': x0, 'a': x1, 'shift': s}
      Gli intervalli [da,a] delimitano le zone (in coordinate master); tra una zona e la
      successiva c'e' un corridoio prismatico che viene ricostruito alla nuova lunghezza.
      La zona k viene traslata di shift_k lungo X.
    Ritorna il nuovo solido.
    """
    if len(zone) == 1:
        s = solido.copy()
        s.translate(Base.Vector(zone[0]['shift'], 0, 0))
        return s
    pezzi = []
    for i, z in enumerate(zone):
        p = solido.common(_box_x(z['da'], z['a']))
        if p.Volume < 1e-6:
            raise RuntimeError(f"zona {i} vuota [{z['da']},{z['a']}]")
        p.translate(Base.Vector(z['shift'], 0, 0))
        pezzi.append(p)
    ponti = []
    for i in range(len(zone) - 1):
        zl, zr = zone[i], zone[i + 1]
        gap_master = zr['da'] - zl['a']
        gap_nuovo = gap_master + (zr['shift'] - zl['shift'])
        if gap_nuovo < -1e-6:
            raise RuntimeError(f"corridoio {i} negativo: {gap_nuovo}")
        if gap_nuovo < 1e-6:
            continue
        # sezione: facce del pezzo sinistro sul piano di taglio (gia' traslato)
        xs = zl['a'] + zl['shift']
        facce = _sezione_faces(pezzi[i], xs, +1)
        if not facce:
            raise RuntimeError(f"nessuna faccia di sezione a x={xs} (corridoio {i})")
        for f in facce:
            ponti.append(f.extrude(Base.Vector(gap_nuovo, 0, 0)))
    tutto = pezzi[0]
    for p in pezzi[1:] + ponti:
        tutto = tutto.fuse(p)
    tutto = tutto.removeSplitter()
    return tutto


def cilindro_foro(h, extra=0.2):
    """Cilindro dal descrittore foro {'dir','dia','cx','cy','cz','lo','hi'} con margine."""
    r = h['dia'] / 2.0
    L = (h['hi'] - h['lo']) + 2 * extra
    if h['dir'] == 'X':
        base = Base.Vector(h['lo'] - extra, h['cy'], h['cz']); asse = Base.Vector(1, 0, 0)
    elif h['dir'] == 'Y':
        base = Base.Vector(h['cx'], h['lo'] - extra, h['cz']); asse = Base.Vector(0, 1, 0)
    else:
        base = Base.Vector(h['cx'], h['cy'], h['lo'] - extra); asse = Base.Vector(0, 0, 1)
    return Part.makeCylinder(r, L, base, asse)


def tappa_fori(solido, fori):
    """Riempie i fori indicati fondendo cilindri esatti (senza margine radiale)."""
    if not fori:
        return solido
    s = solido
    for h in fori:
        r = h['dia'] / 2.0
        L = (h['hi'] - h['lo'])
        if h['dir'] == 'X':
            base = Base.Vector(h['lo'], h['cy'], h['cz']); asse = Base.Vector(1, 0, 0)
        elif h['dir'] == 'Y':
            base = Base.Vector(h['cx'], h['lo'], h['cz']); asse = Base.Vector(0, 1, 0)
        else:
            base = Base.Vector(h['cx'], h['cy'], h['lo']); asse = Base.Vector(0, 0, 1)
        s = s.fuse(Part.makeCylinder(r, L, base, asse))
    return s.removeSplitter()


def fora(solido, fori):
    # taglio SEQUENZIALE: il cut con compound di utensili tangenti ai tappi
    # puo' produrre solidi spezzati (bug booleano OCC)
    if not fori:
        return solido
    s = solido
    for h in fori:
        s = s.cut(cilindro_foro(h))
    return s.removeSplitter()
