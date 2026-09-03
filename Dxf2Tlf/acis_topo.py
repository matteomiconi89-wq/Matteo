# -*- coding: utf-8 -*-
"""
acis_topo - tasche/scassi SAGOMATI dalla topologia ACIS dei 3DSOLID (SAT).

Legge facce/anelli/spigoli con ezdxf (classi ellipse-curve e cone-surface
registrate a mano: la 1.4.4 non le ha) e ritorna le tasche con il CONTORNO
VERO (poligonizzato) oppure il cerchio, la profondita' e la faccia di
apertura (sopra/sotto). Funziona sui DXF con ACIS TESTUALE (DXF 2000);
i DXF 2018 (SAB) non si caricano: il chiamante usa il fallback geometrico.

Convenzioni ACIS verificate (spike 21/07/2026):
- face.sense True='reversed' -> normale effettiva = -surface.normal
- edge.sense True -> l'edge va contro la parametrizzazione della curva
- coedge.sense True -> il coedge percorre l'edge da end a start
- ACIS 400: start/end_param assenti -> angoli ricavati dai vertici
- esterno/interno di un loop: area con segno attorno alla normale faccia
"""
import math
from ezdxf.math import Vec3
from ezdxf.acis import api
from ezdxf.acis.entities import register, Curve, Surface, DataLoader, Factory


@register
class EllipseCurve(Curve):
    type: str = "ellipse-curve"
    center = Vec3(0, 0, 0)
    normal = Vec3(0, 0, 1)
    major_axis = Vec3(1, 0, 0)
    ratio: float = 1.0

    def restore_common(self, loader: DataLoader, entity_factory: Factory) -> None:
        super().restore_common(loader, entity_factory)
        self.center = Vec3(loader.read_vec3())
        self.normal = Vec3(loader.read_vec3())
        self.major_axis = Vec3(loader.read_vec3())
        self.ratio = loader.read_double()

    @property
    def radius(self) -> float:
        return self.major_axis.magnitude

    @property
    def minor_dir(self) -> Vec3:
        return self.normal.cross(self.major_axis)

    def evaluate(self, param: float) -> Vec3:
        return (self.center + self.major_axis * math.cos(param)
                + self.minor_dir * (self.ratio * math.sin(param)))


@register
class ConeSurface(Surface):
    type: str = "cone-surface"
    origin = Vec3(0, 0, 0)
    axis = Vec3(0, 0, 1)
    major_axis = Vec3(1, 0, 0)
    ratio: float = 1.0
    sine: float = 0.0
    cosine: float = 1.0
    scale: float = 1.0
    reversed_u: bool = False

    def restore_common(self, loader: DataLoader, entity_factory: Factory) -> None:
        super().restore_common(loader, entity_factory)
        self.origin = Vec3(loader.read_vec3())
        self.axis = Vec3(loader.read_vec3())
        self.major_axis = Vec3(loader.read_vec3())
        self.ratio = loader.read_double()
        loader.read_interval()
        loader.read_interval()
        self.sine = loader.read_double()
        self.cosine = loader.read_double()
        self.scale = loader.read_double()
        self.reversed_u = loader.read_bool("reversed", "forward")

    def evaluate(self, u: float, v: float) -> Vec3:
        raise NotImplementedError


def _coedge_ordinati(loop):
    out = []
    start = loop.coedge
    ce = start
    while True:
        out.append(ce)
        ce = ce.next_coedge
        if ce.is_none or ce is start:
            break
    return out


def _angolo(curve, p):
    u = p - curve.center
    m = curve.major_axis
    n = curve.minor_dir
    cos_t = u.dot(m) / m.magnitude_square
    sin_t = u.dot(n) / (n.magnitude_square * curve.ratio)
    return math.atan2(sin_t, cos_t)


def _punti_spigolo(ce, sagitta=0.2):
    """Punti dello spigolo nel verso di percorrenza del loop (poligonizzato)."""
    edge = ce.edge
    curve = edge.curve
    sp = edge.start_vertex.point.location
    ep = edge.end_vertex.point.location
    if curve.type == "ellipse-curve":
        r = max(curve.radius, 0.1)
        t0 = _angolo(curve, sp)
        t1 = _angolo(curve, ep)
        pieno = sp.isclose(ep, abs_tol=1e-9)
        if not edge.sense:
            if pieno:
                t1 = t0 + 2 * math.pi
            elif t1 <= t0:
                t1 += 2 * math.pi
        else:
            if pieno:
                t1 = t0 - 2 * math.pi
            elif t1 >= t0:
                t1 -= 2 * math.pi
        # passi per freccia (sagitta) <= 0.2 mm
        sweep = abs(t1 - t0)
        try:
            passo = 2 * math.acos(max(0.0, 1 - sagitta / r))
        except ValueError:
            passo = 0.5
        n = max(4, int(math.ceil(sweep / max(passo, 0.05))))
        pts = [curve.evaluate(t0 + (t1 - t0) * i / n) for i in range(n + 1)]
    elif curve.type == "straight-curve":
        pts = [sp, ep]
    else:
        pts = [sp, ep]          # spline ecc.: corda (avviso dal chiamante)
    if ce.sense:
        pts = list(reversed(pts))
    return pts


def _tratti_spigolo(ce):
    """Spigolo come TRATTI veri nel verso di percorrenza:
    ("L", arrivo) per le rette, ("A", arrivo, punto_medio, raggio) per gli
    archi TONDI (ratio 1); archi > 180 gradi spezzati in due; ellissi vere
    e spline -> None (il chiamante ripiega sulla poligonale)."""
    edge = ce.edge
    curve = edge.curve
    sp = edge.start_vertex.point.location
    ep = edge.end_vertex.point.location
    if curve.type == "straight-curve":
        seg = [("L", ep)] if not ce.sense else [("L", sp)]
        return seg
    if curve.type != "ellipse-curve" or abs(curve.ratio - 1.0) > 1e-6:
        return None
    r = curve.radius
    if r < 0.05:
        return None
    t0 = _angolo(curve, sp)
    t1 = _angolo(curve, ep)
    pieno = sp.isclose(ep, abs_tol=1e-9)
    if not edge.sense:
        if pieno:
            t1 = t0 + 2 * math.pi
        elif t1 <= t0:
            t1 += 2 * math.pi
    else:
        if pieno:
            t1 = t0 - 2 * math.pi
        elif t1 >= t0:
            t1 -= 2 * math.pi
    if ce.sense:                       # percorso al contrario
        t0, t1 = t1, t0
    sweep = t1 - t0
    tratti = []
    n_spezzi = 2 if abs(sweep) > math.pi else 1
    for i in range(n_spezzi):
        ta = t0 + sweep * i / n_spezzi
        tb = t0 + sweep * (i + 1) / n_spezzi
        tratti.append(("A", curve.evaluate(tb),
                       curve.evaluate((ta + tb) / 2.0), r))
    return tratti


def _area_segnata(punti2d):
    a = 0.0
    for i in range(len(punti2d)):
        x0, y0 = punti2d[i]
        x1, y1 = punti2d[(i + 1) % len(punti2d)]
        a += x0 * y1 - x1 * y0
    return 0.5 * a


def _e_cerchio(loop):
    """(centro, raggio) se il loop e' un cerchio pieno (1+ archi coassiali)."""
    curve0 = None
    for ce in _coedge_ordinati(loop):
        c = ce.edge.curve
        if c.type != "ellipse-curve" or abs(c.ratio - 1.0) > 1e-6:
            return None
        if curve0 is None:
            curve0 = c
        elif not (c.center.isclose(curve0.center, abs_tol=0.01)
                  and abs(c.radius - curve0.radius) < 0.01):
            return None
    if curve0 is None:
        return None
    return curve0.center, curve0.radius


def tasche_da_solido(acis_data, alt_raw_axis=None):
    """Estrae le tasche di UN solido (coordinate GREZZE del disegno).

    Ritorna (facce_piane, avvisi) dove ogni faccia piana e':
      {"normale": Vec3 effettiva, "quota": float lungo la normale,
       "punto": Vec3 di riferimento, "loops": [ {"esterno": bool,
       "cerchio": (Vec3 centro, r) | None, "punti": [Vec3...] } ]}
    Il chiamante applica le SUE trasformazioni (permutazioni/specchi) e
    decide cosa e' tasca, foro o apertura.
    """
    avvisi = []
    facce = []
    bodies = api.load(acis_data)
    for body in bodies:
        # transform del body: AutoCAD scrive il corpo in coordinate LOCALI
        # e mette rotazione+traslazione qui: va applicata a tutto
        m = None
        btr = getattr(body, "transform", None)
        if btr is not None and not getattr(btr, "is_none", True):
            m = getattr(btr, "matrix", None)
        for face in body.lump.shell.faces():
            srf = face.surface
            if srf.type != "plane-surface":
                continue
            normale = -srf.normal if face.sense else srf.normal
            normale = normale.normalize()
            if m is not None:
                normale = Vec3(m.transform_direction(normale)).normalize()
            loops = []
            for lp in face.loops():
                punti = []
                archi = []          # raccordi (archi PARZIALI) del contorno
                tratti = []         # tratti VERI (rette+archi) del contorno
                spline = False
                for ce in _coedge_ordinati(lp):
                    cv = ce.edge.curve
                    if cv.type not in ("ellipse-curve", "straight-curve"):
                        spline = True
                    elif (cv.type == "ellipse-curve"
                          and abs(cv.ratio - 1.0) < 1e-6):
                        archi.append((cv.center, cv.radius))
                    if tratti is not None:
                        t_e = _tratti_spigolo(ce)
                        if t_e is None:
                            tratti = None      # spline/ellisse: si ripiega
                        else:
                            tratti.extend(t_e)
                    punti.extend(_punti_spigolo(ce)[:-1])
                if len(punti) < 3:
                    continue
                if spline:
                    avvisi.append("contorno con SPLINE approssimato a corde")
                if m is not None:
                    punti = [Vec3(m.transform(p)) for p in punti]
                    if tratti:
                        tratti = [
                            ("L", Vec3(m.transform(t[1]))) if t[0] == "L"
                            else ("A", Vec3(m.transform(t[1])),
                                  Vec3(m.transform(t[2])), t[3])
                            for t in tratti]
                # area con segno nel piano della faccia
                w = normale
                u = w.cross(Vec3(1, 0, 0))
                if u.magnitude < 1e-9:
                    u = w.cross(Vec3(0, 1, 0))
                u = u.normalize()
                v = w.cross(u)
                p2 = [(p.dot(u), p.dot(v)) for p in punti]
                area = _area_segnata(p2)
                cerchio = _e_cerchio(lp)
                if m is not None:
                    if cerchio:
                        cerchio = (Vec3(m.transform(cerchio[0])), cerchio[1])
                    archi = [(Vec3(m.transform(c)), r) for c, r in archi]
                loops.append({"esterno": area > 0,
                              "cerchio": cerchio,
                              # un cerchio PIENO e' un foro vero, non raccordo
                              "archi": [] if cerchio else archi,
                              "punti": punti,
                              "tratti": tratti or None,
                              "area": abs(area)})
            if loops:
                facce.append({"normale": normale,
                              "quota": loops[0]["punti"][0].dot(normale),
                              "punto": loops[0]["punti"][0],
                              "loops": loops})
    return facce, avvisi
