#!/usr/bin/env python3
"""Legge i MATERIALI dalla PIANTA GENERALE e li assegna ai pezzi dei modelli 3D.

Gli STEP aggiornati portano gia' il materiale nel nome del pezzo
(`..._RIPIANO -- MULT.LAM.B.18mm 305x130`): quella e' la fonte migliore e viene
usata per prima. Per tutto il resto il materiale sta nei LAYER `F_...` del DWG,
su cui e' disegnata la geometria dentro i blocchi (es. `F_MULTI laminato OPACO`,
`F_MASSELLO_abete`, `F_VETRO`). Questo script:

  1. estrae dalla pianta ogni polilinea chiusa disegnata su un layer materiale,
     esplodendo i blocchi (virtual_entities);
  2. per ogni pezzo dei modelli 3D confronta l'impronta in pianta con quelle
     polilinee e prende il layer di quella che combacia (IoU);
  3. per i pezzi ORIZZONTALI, che in pianta non si vedono (ripiani, basi, cieli),
     eredita il materiale prevalente della cassa a cui appartengono;
  4. per i mobili modellati come volume unico usa i materiali delle polilinee che
     cadono DENTRO la sua impronta;
  5. i mobili gemelli (la doppia e' il master specchiato) copiano pezzo per pezzo.

Ogni assegnazione porta la sua provenienza: 'dwg' se letta, 'ereditato' se dedotta.

    python3 materiali_da_dwg.py [pianta.dxf]        -> ../materiali.json
"""
import json, pathlib, sys, collections
import ezdxf

HERE = pathlib.Path(__file__).parent
DXF = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("/tmp/pianta.dxf")
TX, TY = 2293.0, 3117.0              # pianta -> trailer
IOU_MIN = 0.35
GEMELLI = {"letto_doppia": "letto_master"}   # stesso mobile, specchiato

# layer `F_` che NON sono materiali ma servizi di disegno
NON_MATERIALI = {
    "F_PROIEZIONI", "F_RETINI", "F_RETINO", "F_SEZIONI", "F_TESTI", "F_GUIDE",
    "F_LAVORAZIONI", "F_ARREDI", "F_ARREDI_PARETI", "F_PERSONE", "F_LIBRI",
    "F_IMPIANTO ELETTRICO", "F_IMPIANTO IDRAULICO", "F_IMPIANTO_CDZ",
    "F_ELETTRICO", "F_ILUMINAZIONE", "F_ESCURSORI_SLIDER", "F_SPONDINE",
}


def impronte(dxf_path):
    """[(layer, x0, x1, y0, y1), ...] in coordinate trailer, solo layer materiale"""
    doc = ezdxf.readfile(str(dxf_path))
    out = []

    def scendi(e, depth=0):
        t = e.dxftype()
        if t == "INSERT" and depth < 5:
            try:
                for v in e.virtual_entities():
                    scendi(v, depth + 1)
            except Exception:
                pass
            return
        if t == "LWPOLYLINE" and e.closed:
            lay = e.dxf.layer
            if not lay.upper().startswith("F_") or lay.upper() in NON_MATERIALI:
                return
            pts = [(p[0] - TX, p[1] - TY) for p in e.get_points("xy")]
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            out.append((lay, min(xs), max(xs), min(ys), max(ys)))

    for e in doc.modelspace():
        scendi(e)
    return out


def iou(a, b):
    ix = max(0.0, min(a[1], b[1]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[2], b[2]))
    inter = ix * iy
    ua = (a[1] - a[0]) * (a[3] - a[2])
    ub = (b[1] - b[0]) * (b[3] - b[2])
    tot = ua + ub - inter
    return inter / tot if tot > 0 else 0.0


def famiglia(nome):
    """prefisso di cassa: 26-A011_AMA_77_RIPIANO -> AMA"""
    p = nome.replace("26-A011_", "").split("_")
    return p[0] if p else ""


def contenuti(bb, pol):
    """materiale prevalente delle polilinee che cadono dentro l'impronta"""
    c = collections.Counter()
    for lay, x0, x1, y0, y1 in pol:
        if bb[0] <= x0 and x1 <= bb[1] and bb[2] <= y0 and y1 <= bb[3]:
            c[lay] += 1
    return c.most_common(1)[0][0] if c else None


def assegna(mobili, pol):
    ris, stat = {}, collections.Counter()
    for chiave, pezzi in mobili.items():
        if chiave in GEMELLI:
            continue                       # riempito dopo, copiando dal gemello
        letti, per_fam = {}, collections.defaultdict(collections.Counter)
        for i, m in enumerate(pezzi):
            if m.get("m"):
                continue                   # materiale gia' nel nome di distinta
            V = m["v"]
            bb = (min(p[0] for p in V), max(p[0] for p in V),
                  min(p[1] for p in V), max(p[1] for p in V))
            best, s = None, 0.0
            for q in pol:
                v = iou(bb, (q[1], q[2], q[3], q[4]))
                if v > s:
                    best, s = q[0], v
            if s >= IOU_MIN:
                letti[i] = best
                per_fam[famiglia(m["l"])][best] += 1
        voto_mobile = collections.Counter(letti.values()).most_common(1)
        ris[chiave] = []
        for i, m in enumerate(pezzi):
            u = m["l"].upper()
            if "MATERASSO" in u or "GUANCIALE" in u:      # non sono a capitolato
                mat = "_MATERASSO" if "MATERASSO" in u else "_GUANCIALE"
                ris[chiave].append([m["l"], mat, "fuori capitolato"])
                stat["fuori capitolato"] += 1
            elif m.get("m"):
                ris[chiave].append([m["l"], m["m"], "distinta"]); stat["distinta"] += 1
            elif i in letti:
                ris[chiave].append([m["l"], letti[i], "dwg"]); stat["dwg"] += 1
            else:
                f = per_fam.get(famiglia(m["l"]))
                if f:
                    ris[chiave].append([m["l"], f.most_common(1)[0][0], "ereditato"])
                    stat["ereditato"] += 1
                elif voto_mobile:
                    ris[chiave].append([m["l"], voto_mobile[0][0], "ereditato"])
                    stat["ereditato"] += 1
                else:
                    V = m["v"]
                    bb = (min(p[0] for p in V), max(p[0] for p in V),
                          min(p[1] for p in V), max(p[1] for p in V))
                    dentro = contenuti(bb, pol)
                    if dentro:
                        ris[chiave].append([m["l"], dentro, "contenuto"])
                        stat["contenuto"] += 1
                    else:
                        ris[chiave].append([m["l"], None, "ignoto"]); stat["ignoto"] += 1

    for gemello, sorgente in GEMELLI.items():           # copia pezzo per pezzo
        if gemello in mobili and sorgente in ris:
            da = {n: (mat, prov) for n, mat, prov in ris[sorgente]}
            ris[gemello] = []
            for m in mobili[gemello]:
                mat, prov = da.get(m["l"], (None, "ignoto"))
                ris[gemello].append([m["l"], mat, prov if mat is None else "gemello"])
                stat["gemello" if mat else "ignoto"] += 1
    return ris, stat


if __name__ == "__main__":
    pol = impronte(DXF)
    print(f"{len(pol)} impronte con layer materiale nella pianta")
    for l, n in collections.Counter(p[0] for p in pol).most_common(12):
        print(f"   {n:5d}  {l}")
    G = json.load(open(HERE.parent / "arredo_geometry.json"))
    ris, stat = assegna(G["mobili"], pol)
    json.dump(ris, open(HERE.parent / "materiali.json", "w"),
              ensure_ascii=False, separators=(",", ":"))
    print("\nassegnazioni:", dict(stat))
    for k, v in ris.items():
        c = collections.Counter(m for _, m, _ in v)
        print(f"  {k:22s} " + ", ".join(f"{n}x {m}" for m, n in c.most_common(3)))
