# -*- coding: utf-8 -*-
"""COSTRUISCI DA SPEC — da una specifica JSON di pannelli all'esecutivo 3D in AutoCAD.

Fa quello che farebbe l'esecutivista: posa i pannelli, RICONOSCE DA SOLO le giunzioni
(pannello che va in battuta su un altro) e le fora a regola di bottega (barilotti agli
estremi + spine in mezzo, passo 32), mette i piedini sotto i verticali che poggiano a
terra, le cerniere sulle ante dichiarate, verifica i volumi e salva DWG + lista + fori.

Uso: py costruisci_da_spec.py <spec.json> <out.dwg> [nome]
"""
import json
import os
import sys

sys.path.insert(0, r"C:\Users\User\Desktop\CLAUDE")
from bottega3d import Mobile, passo32, scegli_cerniera   # noqa: E402

TOL = 1.2            # tolleranza di contatto fra pannelli (mm)
MIN_GIUNTO = 60.0    # sotto questa larghezza di contatto non si fora


def dim(box):
    return [box[0][1] - box[0][0], box[1][1] - box[1][0], box[2][1] - box[2][0]]


def asse_spessore(box):
    """Indice dell'asse in cui il pannello e' sottile (0=X, 1=Y, 2=Z)."""
    d = dim(box)
    return d.index(min(d))


def layer_di(materiale, sp):
    u = (materiale or "").upper()
    if "VETRO" in u or "SPECCHIO" in u:
        return "VETRO E SPECCHIO"
    if "COMPLEMENT" in u or "SANITAR" in u or "ELETTRODOM" in u or "LAVABO" in u:
        return "COMPLEMENTO_FORNITURA"
    if "METALLO" in u or "TUBOLARE" in u or "ACCIAIO" in u:
        return "METALLO VERNICIATO"
    base = materiale.strip()[:40] if materiale else "PANNELLO"
    return "%s sp.%g" % (base, sp) if sp else base


def sovrapposizione(a, b, i, minimo=1.0):
    """Intervallo comune sull'asse i (None se il contatto e' inferiore a `minimo`)."""
    lo = max(a[i][0], b[i][0])
    hi = min(a[i][1], b[i][1])
    return (lo, hi) if hi - lo > minimo else None


def trova_giunti(pannelli):
    """Coppie (portato, portante) dove la TESTATA di un pannello va in battuta
    sulla FACCIA di un altro. Un asse libero e' quello lungo (dove si distribuiscono
    i fori), l'altro e' lo spessore del portato (pochi mm: non va preteso ampio)."""
    giunti = []
    for i, p in enumerate(pannelli):
        for j, q in enumerate(pannelli):
            if i == j:
                continue
            bp, bq = p["box"], q["box"]
            asse_q = asse_spessore(bq)          # q (portante) e' sottile qui
            if asse_spessore(bp) == asse_q:     # paralleli: non e' una testata
                continue
            for quota in (bq[asse_q][0], bq[asse_q][1]):
                if abs(bp[asse_q][1] - quota) < TOL:
                    verso = -1                  # p arriva da sotto/sinistra
                elif abs(bp[asse_q][0] - quota) < TOL:
                    verso = 1
                else:
                    continue
                altri = [k for k in (0, 1, 2) if k != asse_q]
                ov = [sovrapposizione(bp, bq, k, 1.0) for k in altri]
                if any(o is None for o in ov):
                    continue
                lung = [o[1] - o[0] for o in ov]
                if max(lung) < MIN_GIUNTO:      # contatto troppo piccolo per forare
                    continue
                giunti.append({"portato": p["nome"], "portante": q["nome"],
                               "asse": asse_q, "quota": quota, "verso": verso,
                               "assi_liberi": altri, "ov": ov,
                               "sp_portato": min(dim(bp))})
    # deduplica (stessa coppia, stessa quota)
    visti, out = set(), []
    for g in giunti:
        k = (g["portato"], g["portante"], round(g["quota"], 1))
        if k not in visti:
            visti.add(k)
            out.append(g)
    return out


def main():
    spec_path, out_dwg = sys.argv[1], sys.argv[2]
    spec = json.load(open(spec_path, encoding="utf-8"))
    spec = spec.get("result", spec)
    nome = sys.argv[3] if len(sys.argv) > 3 else spec.get("nome", "MOBILE")[:60]
    nome_file = "".join(c if c.isalnum() or c in "-_" else "_" for c in nome)[:50]

    pannelli = [p for p in spec["pannelli"] if len(p.get("box", [])) == 3]
    layers = {}
    for p in pannelli:
        p["_layer"] = layer_di(p.get("materiale", ""), p.get("sp", 0))
        layers.setdefault(p["_layer"], 40 + (len(layers) * 17) % 200)

    layers["FORO_SERRATURA_D16"] = 240
    layers["FERRAMENTA_SQUADRETTA_FISSAGGIO"] = 3
    m = Mobile(nome_file, out_dwg=out_dwg,
               scratch=os.path.dirname(out_dwg), layers_extra=layers)

    # ---- pannelli ----
    for p in pannelli:
        b = p["box"]
        nm = "".join(c if c.isalnum() or c in "-_" else "_" for c in p["nome"])[:48]
        p["_nome3d"] = nm
        m.box(nm, p["_layer"], b[0][0], b[0][1], b[1][0], b[1][1], b[2][0], b[2][1])

    idx = {p["nome"]: p for p in pannelli}

    # ---- CANALE LED: dove passa una strip, il legno va fresato (gola continua) ----
    # (regola Matteo 04/08: "il led deve essere un canale, ci sta sulle sezioni")
    GIOCO_LED = 1.0
    strisce = [p for p in pannelli
               if "LED" in (p.get("nome", "") + p.get("materiale", "")).upper()
               and "COMPLEMENT" in p.get("materiale", "").upper()]
    n_canali = 0
    for st in strisce:
        bs = st["box"]
        for p in pannelli:
            if p is st or "COMPLEMENT" in p["_layer"] or "VETRO" in p["_layer"]:
                continue
            bp = p["box"]
            ov = [sovrapposizione(bs, bp, k, 0.2) for k in (0, 1, 2)]
            if any(o is None for o in ov):
                continue                      # la strip non tocca questo pezzo
            # canale = sezione della strip + gioco, per tutta la sua corsa
            lung = [bs[k][1] - bs[k][0] for k in (0, 1, 2)]
            asse_corsa = lung.index(max(lung))
            lim = []
            for k in (0, 1, 2):
                if k == asse_corsa:
                    lim.append((max(bs[k][0], bp[k][0]) - 0.5, min(bs[k][1], bp[k][1]) + 0.5))
                else:
                    lim.append((bs[k][0] - GIOCO_LED, bs[k][1] + GIOCO_LED))
            vol = ((min(lim[0][1], bp[0][1]) - max(lim[0][0], bp[0][0])) *
                   (min(lim[1][1], bp[1][1]) - max(lim[1][0], bp[1][0])) *
                   (min(lim[2][1], bp[2][1]) - max(lim[2][0], bp[2][0])))
            m.scasso(p["_nome3d"], lim[0][0], lim[0][1], lim[1][0], lim[1][1],
                     lim[2][0], lim[2][1], vol=max(0.0, vol))
            n_canali += 1
    if n_canali:
        m.lista[("CANALE_LED", "Gola fresata per strip LED (canale continuo)")] += n_canali
        print("canali LED fresati:", n_canali)

    # ---- giunzioni riconosciute e forate a regola ----
    n_giunti = 0
    for g in trova_giunti(pannelli):
        pp, qq = idx[g["portato"]], idx[g["portante"]]
        if "COMPLEMENTO" in pp["_layer"] or "COMPLEMENTO" in qq["_layer"]:
            continue
        if "VETRO" in pp["_layer"] or "VETRO" in qq["_layer"]:
            continue
        asse, quota, verso = g["asse"], g["quota"], g["verso"]
        # asse lungo cui distribuire i fori = quello con sovrapposizione maggiore
        (a1, o1), (a2, o2) = zip(g["assi_liberi"], g["ov"])
        if (o1[1] - o1[0]) >= (o2[1] - o2[0]):
            asse_fila, span, asse_mez, mez = a1, o1, a2, o2
        else:
            asse_fila, span, asse_mez, mez = a2, o2, a1, o1
        centro_mez = (mez[0] + mez[1]) / 2.0
        posti = passo32(span[0], span[1], 150.0, 240.0, 60.0)
        if len(posti) < 2:
            continue
        d = [0.0, 0.0, 0.0]
        d[asse] = float(verso)          # dal portato verso il portante
        for k, t in enumerate(posti):
            base = [0.0, 0.0, 0.0]      # punto sul piano di contatto
            base[asse] = quota
            base[asse_fila] = t
            base[asse_mez] = centro_mez
            if k in (0, len(posti) - 1):
                # barilotto: sede D14x15 nella FACCIA del portato, a 21 dalla testata;
                # entra lungo l'asse dello spessore del portato (asse_mez)
                sede = list(base)
                sede[asse] = quota + 21.0 * verso
                sede[asse_mez] = mez[0]
                dir_sede = [0.0, 0.0, 0.0]
                dir_sede[asse_mez] = 1.0
                m.barilotto(pp["_nome3d"], qq["_nome3d"], sede, dir_sede, base, d)
            else:
                m.spina(qq["_nome3d"], pp["_nome3d"], base, [-v for v in d])
        n_giunti += 1

    # ---- piedini sotto i verticali che poggiano a terra ----
    zmin = min(p["box"][2][0] for p in pannelli)
    n_pied = 0
    for p in pannelli:
        b = p["box"]
        if b[2][0] > zmin + 12 or dim(b)[2] < 400:   # deve poggiare a terra
            continue
        if asse_spessore(b) != 0:            # solo i verticali sottili in X
            continue
        if "COMPLEMENTO" in p["_layer"] or "VETRO" in p["_layer"]:
            continue
        xm = (b[0][0] + b[0][1]) / 2.0
        prof = b[1][1] - b[1][0]
        if prof < 200:
            continue
        for y in (b[1][0] + 80.0, b[1][1] - 80.0):
            m.rekord(p["_nome3d"], xm, y, b[2][0], b[0][1], 1, int_h=52.0)
            n_pied += 1

    # ---- cerniere sulle ante dichiarate ----
    def trova(nome):
        """Collega la voce 'ante' al pannello anche se il nome ha suffissi
        descrittivi ('P29 ANTA (tamburato 764x...)') o e' troncato."""
        if not nome:
            return None
        if nome in idx:
            return idx[nome]
        n = str(nome).strip()
        base = n.split("(")[0].strip()
        if base in idx:
            return idx[base]
        cod = n.split()[0].rstrip(":.-")          # es. "P29", "D01", "A01"
        cand = [p for p in pannelli if p["nome"].split()[0].rstrip(":.-") == cod]
        if len(cand) == 1:
            return cand[0]
        low = base.lower()
        cand = [p for p in pannelli
                if p["nome"].lower().startswith(low[:18]) or low.startswith(p["nome"].lower()[:18])]
        return cand[0] if len(cand) == 1 else None

    for a in spec.get("ante", []):
        pa = trova(a.get("pannello"))
        pf = trova(a.get("fianco"))
        if not pa:
            print("[anta non collegata] %s" % str(a.get("pannello"))[:60])
            continue
        b = pa["box"]
        H = dim(b)[2]
        Lw = dim(b)[0]
        sc = scegli_cerniera(min(dim(b)), a.get("sormonto", 16.0), Lw, H)
        n = int(a.get("n_cerniere") or sc["n"])
        n = max(2, min(6, n))
        lato = str(a.get("lato_cerniere", "SX")).upper()

        # --- ANTA A RIBALTA (verso l'alto o a scendere): la foratura sta sul filo
        # orizzontale, non sui lati, e il meccanismo e' a compasso sui fianchi ---
        if any(k in lato for k in ("ALT", "RIBALT", "SOPRA", "BASS", "SCEND")):
            su = not any(k in lato for k in ("BASS", "SCEND"))
            z_t = b[2][1] - 22.5 if su else b[2][0] + 22.5   # tazza a 22,5 dal filo
            y_int = b[1][1]
            for x in passo32(b[0][0], b[0][1], 200.0, 400.0, 100.0)[:max(2, n)]:
                m.foro(pa["_nome3d"], "ribalta_tazza", 35.0, 13.0, (x, y_int, z_t),
                       (0, -1, 0), "FORO_TAZZA_D35")
            for pf, verso in ((trova(s.strip()), None) for s in
                              str(a.get("fianco", "")).replace("+", ",").split(",")):
                if not pf:
                    continue
                bf = pf["box"]
                # piastra compasso: 2 fori D5 sulla faccia interna del fianco, in alto
                x_f = bf[0][1] if bf[0][0] < b[0][0] else bf[0][0]
                vs = 1 if bf[0][0] < b[0][0] else -1
                for dy in (37.0, 69.0):
                    m.foro(pf["_nome3d"], "compasso_piastra", 5.0, 13.0,
                           (x_f, bf[1][0] + dy, b[2][1] - 40.0), (vs, 0, 0), "FORO_VITE_D5")
            m.lista[("COMPASSO_RIBALTA", "Meccanismo a compasso per anta a ribalta")] += 2
            # serratura F&S sul filo BASSO dell'anta (regola del disegno)
            m.foro(pa["_nome3d"], "pulsante_FS_336", 16.0, min(dim(b)) + 1.0,
                   ((b[0][0] + b[0][1]) / 2.0, y_int, b[2][0] + 30.0), (0, -1, 0),
                   "FORO_SERRATURA_D16")
            m.lista[("336.C", "Pulsante in ottone Foresti e Suardi (anta 19)")] += 1
            m.lista[("800/810", "Serratura a scrocco F&S per pulsante 336.C")] += 1
            m.foro(pa["_nome3d"], "tipon_piastra", 5.0, 11.0,
                   ((b[0][0] + b[0][1]) / 2.0 + 100.0, y_int, b[2][0] + 30.0),
                   (0, -1, 0), "FORO_VITE_D5")
            m.lista[("956.1201", "TIP-ON dritto + piastrina 956A1004")] += 1
            continue

        sx = lato.startswith("S")
        x_t = b[0][0] + 22.5 if sx else b[0][1] - 22.5
        verso = 1 if sx else -1
        zs = [b[2][0] + 100.0 + i * (H - 200.0) / (n - 1) for i in range(n)]
        y_int = b[1][1]
        for z in zs:
            m.foro(pa["_nome3d"], "cerniera_tazza", 35.0, 13.0, (x_t, y_int, z),
                   (0, -1, 0), "FORO_TAZZA_D35")
            for dz in (-22.5, 22.5):
                m.foro(pa["_nome3d"], "cerniera_vite", 5.0, 13.0,
                       (x_t + verso * 9.5, y_int, z + dz), (0, -1, 0), "FORO_VITE_D5")
            if pf:
                bf = pf["box"]
                xf = bf[0][1] if sx else bf[0][0]
                vs = 1 if sx else -1
                for q in (20.0, 52.0):
                    m.foro(pf["_nome3d"], "basetta_vite", 5.0, 13.0,
                           (xf, bf[1][0] + q, z), (vs, 0, 0), "FORO_VITE_D5")
            m.lista[(sc["cod"], "Cerniera CLIP top 110 %s" % sc["tipo"])] += 1
            m.lista[(sc["basetta"], "Basetta H%g" % sc["H"])] += 1

        # REGOLE TRUCK (Matteo 04/08): ogni anta ha TIP-ON + serratura Foresti e Suardi
        x_opp = b[0][1] - 40.0 if sx else b[0][0] + 40.0     # lato opposto alle cerniere
        z_mid = (b[2][0] + b[2][1]) / 2.0
        m.foro(pa["_nome3d"], "tipon_piastra", 5.0, 11.0,
               (x_opp, y_int, b[2][0] + H * 0.75), (0, -1, 0), "FORO_VITE_D5")
        m.lista[("956.1201", "TIP-ON dritto + piastrina 956A1004")] += 1
        # Foresti e Suardi (foglio FERRAMENTA SCHEDA BASE): pulsante in ottone 336.C
        # + serratura a scrocco art. 800/810 sul retro dell'anta.
        # NB nella nomenclatura F&S il numero e' lo SPESSORE ANTA (435=16, 436=19, 437=23):
        # 336 = anta 19. Foro pulsante D16 (da confermare sulla scheda tecnica).
        x_ser = b[0][1] - 30.0 if sx else b[0][0] + 30.0
        m.foro(pa["_nome3d"], "pulsante_FS_336", 16.0, min(dim(b)) + 1.0,
               (x_ser, b[1][1], z_mid), (0, -1, 0), "FORO_SERRATURA_D16")
        m.lista[("336.C", "Pulsante in ottone Foresti e Suardi (anta 19)")] += 1
        m.lista[("800/810", "Serratura a scrocco F&S per pulsante 336.C")] += 1

    # ---- ferramenta dichiarata nella spec (solo in lista, senza geometria) ----
    for f in spec.get("ferramenta", []):
        cod = f.get("codice") or f.get("tipo", "")[:26]
        q = int(f.get("quantita") or 1)
        if not any(k in (f.get("tipo") or "").lower()
                   for k in ("cernier", "basetta", "barilotto", "spina", "piedino", "rekord")):
            m.lista[(str(cod)[:26], (f.get("tipo") or "")[:60])] += q

    # ---- squadrette di fissaggio al truck (regola Matteo: si fissa con squadrette) ----
    zmax = max(p["box"][2][1] for p in pannelli)
    ymax = max(p["box"][1][1] for p in pannelli)
    Ltot = max(p["box"][0][1] for p in pannelli)
    n_sq = 0
    for x in passo32(0, Ltot, 500.0, 800.0, 120.0):
        for y, z in ((ymax - 60.0, zmax - 20.0), (ymax - 20.0, zmax - 300.0)):
            if z < 0:
                continue
            m.box("F_SQUADRETTA_%d_%d" % (int(x), int(z)),
                  "FERRAMENTA_SQUADRETTA_FISSAGGIO", x - 15, x + 15, y - 15, y + 15, z - 15, z + 15)
            n_sq += 1
    m.lista[("SQUADRETTA_FISSAGGIO", "Squadretta di fissaggio al telaio/parete truck")] += n_sq

    base_out = os.path.splitext(out_dwg)[0]
    res = m.chiudi(viste=False,
                   lista_txt=base_out + "_FERRAMENTA.txt",
                   fori_json=base_out + "_fori.json")
    print("GIUNTI riconosciuti e forati:", n_giunti, "| piedini:", n_pied)
    try:                     # non lasciare il documento aperto: la sessione e' dell'utente
        m._r(lambda: m.doc.Close(False), tries=20, label="close")
    except Exception:
        pass
    return res


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # se qualcosa va storto, chiudi comunque il documento orfano
        import traceback
        traceback.print_exc()
        try:
            import comtypes.client
            app = comtypes.client.GetActiveObject("AutoCAD.Application")
            d = app.ActiveDocument
            if d.Name.lower().startswith(("disegno", "drawing")):
                d.Close(False)
                print("[documento orfano chiuso]")
        except Exception:
            pass
        raise
