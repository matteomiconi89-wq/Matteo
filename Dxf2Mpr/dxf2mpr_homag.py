"""
dxf2mpr_homag - dai DXF 3D (3DSOLID) ai programmi woodWOP per la HOMAG
(BHC PC87 powerTouch), TUTTO in automatico, senza aprire woodWOP:

  1. estrae fori e scassi dalla geometria vera del solido
     (stesso motore di dxf2tlf_masterwood)
  2. scrive il .mpr TESTO nel dialetto woodWOP 9 (copiato riga per riga
     dai programmi reali della macchina: 21032 SET15_16 J03_04)
  3. TechAutoX.exe (CLI ufficiale HOMAG, -a=1) applica la tecnologia e
     genera il .mprx

Come per il TLF: se il pezzo ha lavorazioni sull'altra faccia esce anche
il programma  <nome>_B  girato di 180 attorno al lato lungo.

NB profondita' D14: qui NON si applica la regola 15.8 della Masterwood;
si usa la profondita' vera del 3D (14.2), come nei programmi HOMAG reali.
"""

import os
import sys
import math
import datetime
import shutil
import subprocess
import tempfile
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox

for _d in (r"C:\Users\User\Desktop\CLAUDE\Dxf2Tlf",):
    if _d not in sys.path:
        sys.path.append(_d)
from dxf2tlf_masterwood import estrai_geometria

WOODWOP_DIR = r"C:\Program Files (x86)\HOMAG Group\woodWOP6"
TECHAUTOX = os.path.join(WOODWOP_DIR, "TechAutoX.exe")
MACCHINA = 1


def _n(v):
    v = round(float(v), 4)
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


# ========================= scrittura MPR ===================================
def scrivi_mpr(path, dims, fori, scassi, tagli=None, profili=None,
               incl=None, squadra=True):
    lung, larg, alt = dims
    scassi = scassi or []
    tagli = tagli or []
    profili = profili or []      # profili ESTERNI sagomati (fresa di contorno)
    incl = incl or []            # biselli: tagli con lama INCLINATA
    sagome = [s for s in scassi if "contorno" in s]    # contorni veri (topo)
    fn = "1" if squadra else "0"     # soprammisura di squadratura 1 mm

    def prof_mpr(s):
        # passante: espressione "sp+5" come nei programmi macchina reali
        return f"{_n(alt)}+5" if s.get("thru") else _n(s["prof"])
    L = []
    a = L.append

    def kv(k, v):
        a(f'{k}="{v}"')

    # --- intestazione [H (dialetto WW 9.0.560 dei programmi macchina) -----
    a("[H")
    for k, v in (("VERSION", "4.0 Alpha"), ("WW", "9.0.560"), ("HP", "1"),
                 ("IN", "0"), ("GX", "0"), ("BFS", "1"), ("GY", "0"),
                 ("GXY", "0"), ("UP", "0"), ("FM", "1"), ("FW", "1000"),
                 ("ZS", "20"), ("UF", "20"), ("HS", "0"), ("OP", "0"),
                 ("MAT", "WEEKE"), ("DN", "STANDARD"),
                 ("HP_A_O", "STANDARD"), ("OVD_U", "0"), ("OVD", "0"),
                 ("OHD_U", "0"), ("OHD", "2"), ("OOMD_U", "1"),
                 ("DST", "0"), ("WRK2", "0"), ("EWL", "2"), ("INCH", "0"),
                 ("VIEW", "NOMIRROR"), ("ANZ", "1"), ("BES", "0"),
                 ("ENT", "0"), ("MATERIAL", ""), ("CUSTOMER", ""),
                 ("ORDER", ""), ("ARTICLE", ""), ("PARTID", ""),
                 ("PARTTYPE", ""), ("MPRCOUNT", "1"), ("MPRNUMBER", "1"),
                 ("INFO1", ""), ("INFO2", ""), ("INFO3", ""),
                 ("INFO4", ""), ("INFO5", "")):
        kv(k, v)
    a(f"_BSX={lung:.6f}")
    a(f"_BSY={larg:.6f}")
    a(f"_BSZ={alt:.6f}")
    a(f"_FNX={fn}.000000")
    a(f"_FNY={fn}.000000")
    a("_RNX=0.000000")
    a("_RNY=0.000000")
    a("_RNZ=0.000000")
    a(f"_RX={lung:.6f}")
    a(f"_RY={larg:.6f}")
    a("")

    # --- variabili [001 ---------------------------------------------------
    a("[001")
    kv("l", _n(lung)); kv("KM", "lunghezza")
    kv("h", _n(larg)); kv("KM", "larghezza")
    kv("s", _n(alt));  kv("KM", "spessore")
    a("")

    # --- CONTORNI ]n (prima di <100, come nei programmi macchina reali:
    # KP + KL/KA con X/Y ASSOLUTI, chiusura riportando l'ultimo punto sul
    # primo). Prima gli scassi sagomati (Z = spessore, come il programma
    # 05 della ditta), poi i profili esterni (Z = 0, come cas003.mpr).
    # Gli ARCHI escono come KA con R e verso DS (0=punto medio a sinistra
    # della corda, tarato su cas001_int.mpr della ditta), NON spezzettati.
    contorni = ([(s["contorno"], s.get("tratti"), alt) for s in sagome]
                + [(p["contorno"], p.get("tratti"), 0.0) for p in profili])
    n_elem = []                        # indice dell'ultimo $E per ogni ]n

    def cache_kl():
        a(".X=0.000000"); a(".Y=0.000000"); a(".Z=0.000000")
        a(".WI=0.000000"); a(".WZ=0.000000")

    for nc, (contorno, tratti, zq) in enumerate(contorni, 1):
        start = tuple(contorno[0])
        a(f"]{nc}")
        a("$E0")
        a("KP ")
        a(f"X={_n(start[0])}")
        a(f"Y={_n(start[1])}")
        a(f"Z={_n(zq)}")
        a("KO=00")
        a(".X=0.000000"); a(".Y=0.000000"); a(".Z=0.000000"); a(".KO=00")
        a("")
        if tratti:
            segs = list(tratti)
            ultimo = segs[-1][1]
            if (abs(ultimo[0] - start[0]) > 0.01
                    or abs(ultimo[1] - start[1]) > 0.01):
                segs.append(("L", start))
            prev = start
            for k, t in enumerate(segs, 1):
                a(f"$E{k}")
                if t[0] == "L":
                    a("KL ")
                    a(f"X={_n(t[1][0])}")
                    a(f"Y={_n(t[1][1])}")
                    a(f"Z={_n(zq)}")
                    cache_kl()
                else:
                    fine, medio, r = t[1], t[2], t[3]
                    cross = ((fine[0] - prev[0]) * (medio[1] - prev[1])
                             - (fine[1] - prev[1]) * (medio[0] - prev[0]))
                    a("KA ")
                    a(f"X={_n(fine[0])}")
                    a(f"Y={_n(fine[1])}")
                    a(f"Z={_n(zq)}")
                    a(f"DS={0 if cross > 0 else 1}")
                    a(f"R={_n(r)}")
                    a(".X=0.000000"); a(".Y=0.000000"); a(".Z=0.000000")
                    a(".I=0.000000"); a(".J=0.000000")
                    a(".DS=0"); a(".R=0.000000")
                    a(".WI=0.000000"); a(".WO=0.000000"); a(".WAZ=0.000000")
                a("")
                prev = t[1]
            n_elem.append(len(segs))
        else:
            punti = list(contorno)
            if (abs(punti[-1][0] - punti[0][0]) > 0.01
                    or abs(punti[-1][1] - punti[0][1]) > 0.01):
                punti.append(punti[0])
            n_elem.append(len(punti) - 1)
            for k, (px, py) in enumerate(punti[1:], 1):
                a(f"$E{k}")
                a("KL ")
                a(f"X={_n(px)}")
                a(f"Y={_n(py)}")
                a(f"Z={_n(zq)}")
                cache_kl()
                a("")

    # --- pezzo <100 -------------------------------------------------------
    a("<100 \\WerkStck\\")
    kv("LA", _n(lung)); kv("BR", _n(larg)); kv("DI", _n(alt))
    kv("FNX", fn); kv("FNY", fn); kv("AX", "0"); kv("AY", "0")
    a("")

    ori = 1

    # --- SQUADRATURA: componente della ditta (squad_lama con lama 149) ----
    # blocco copiato dal programma macchina 08_Frontale_Fisso_A102 corretto
    # dall'operatore; solo nel programma PRINCIPALE (fn=1)
    if squadra:
        a("<139 \\Komponente\\")
        kv("IN", "Fabrizio/squad_lama.mprx")
        kv("XA", "0.0"); kv("YA", "0.0"); kv("ZA", "0.0"); kv("WI", "0.0")
        kv("EM", "0")
        kv("VA", "l l"); kv("VA", "h h"); kv("VA", "s s")
        kv("VA", "profondita 9"); kv("VA", "lama 149")
        kv("VA", "avanzamento 6"); kv("VA", "incisione 3")
        kv("KAT", "Komponentenmakro"); kv("MNM", "squad_lama")
        kv("ORI", str(ori)); ori += 1
        kv("KO", "00")
        a("")

    # --- blocco <121 (come nei programmi macchina) ------------------------
    a("<121 \\Block\\")
    for k, v in (("XP", "0.0"), ("YP", "0.0"), ("ZP", "0.0"), ("AX", "1"),
                 ("AY", "1"), ("RX", "20"), ("RY", "20"), ("CS", "0"),
                 ("OC", "0"), ("KAT", "0"), ("MNM", ""), ("ORI", str(ori)),
                 ("NM", ""), ("DP", "29"), ("KO", "00")):
        kv(k, v)
    a("")

    ori += 1

    # --- fresatura di CONTORNO <105 (profilo sagomato del pezzo) ----------
    # template COPIATO dal programma macchina reale cas003.mpr
    # (Annarita_MC): primo blocco lavorazione, ZA=-3 (passante 3 mm sotto),
    # RK=NoWRK (fresa sulla linea), utensile TNO 140
    for i in range(len(profili)):
        nc = len(sagome) + 1 + i
        a("<105 \\Konturfraesen\\")
        kv("EA", f"{nc}:0")
        kv("MDA", "SEN")
        kv("STUFEN", "0"); kv("ZSTART", "0"); kv("ANZZST", "0")
        kv("RK", "NoWRK")
        kv("EE", f"{nc}:{n_elem[nc - 1]}")
        kv("MDE", "SEN_AB")
        kv("EM", "0"); kv("RI", "1")
        kv("TNO", "140"); kv("SM", "0"); kv("S_", "STANDARD")
        kv("F_", "5"); kv("AB", "0"); kv("VLS", "0"); kv("VLE", "0")
        kv("ZA", "-3")
        kv("HP", "0"); kv("SP", "0"); kv("YVE", "0")
        kv("WW", "1,2,3,401,402,403"); kv("ASG", "2")
        kv("RSEL", "0"); kv("RWID", "0")
        kv("MX", "0"); kv("MY", "0"); kv("MZ", "0")
        kv("MXF", "1"); kv("MYF", "1"); kv("MZF", "1")
        a("")

    def coda(kat, mnm, ww, flag_f="1"):
        nonlocal ori
        kv("HP", "0"); kv("SP", "0"); kv("YVE", "0")
        kv("WW", ww); kv("ASG", "2"); kv("HP_A_O", "STANDARD")
        kv("KAT", kat); kv("MNM", mnm); kv("ORI", str(ori)); ori += 1
        kv("MX", "0"); kv("MY", "0"); kv("MZ", "0")
        kv("MXF", flag_f); kv("MYF", flag_f); kv("MZF", flag_f)
        kv("SYA", "0"); kv("SYV", "0"); kv("KO", "00")
        a("")

    # --- fori orizzontali <103 (bordi) ------------------------------------
    # plane: 1=REAR(y=larg,WI 270) 2=FRONT(y=0,WI 90) 3=LEFT(x=0,WI 0)
    #        4=RIGHT(x=lung,WI 180); nei fori estratti x=quota lungo il
    #        bordo, y=quota nello spessore (ZA)
    for f in fori:
        p = f["plane"]
        if p == 0:
            continue
        if p == 1:
            xa, ya, wi = f["x"], larg, 270
        elif p == 2:
            xa, ya, wi = f["x"], 0, 90
        elif p == 3:
            xa, ya, wi = 0, f["x"], 0
        else:
            xa, ya, wi = lung, f["x"], 180
        a("<103 \\BohrHoriz\\")
        kv("MI", "0")
        kv("XA", _n(xa)); kv("YA", _n(ya)); kv("ZA", _n(f["y"]))
        kv("DU", _n(2 * f["r"])); kv("TI", _n(f["prof"]))
        kv("ANA", "20"); kv("BM", "C"); kv("WI", _n(wi))
        kv("AN", "1"); kv("AB", "32"); kv("BM2", "STD")
        kv("ZT", "0"); kv("RM", "0"); kv("VW", "0"); kv("SM", "0")
        kv("S_", "STANDARD")
        coda("Horizontalbohren", "Bohren horizontal",
             "50,51,52,53,56,59,153")

    # --- fori verticali <102 ----------------------------------------------
    for f in fori:
        if f["plane"] != 0:
            continue
        passante = f["prof"] > alt + 0.5      # dall'estrattore: ALT+4
        a("<102 \\BohrVert\\")
        kv("XA", _n(f["x"])); kv("YA", _n(f["y"]))
        if passante:
            kv("BM", "LSL")
        else:
            kv("BM", "LS"); kv("TI", _n(f["prof"]))
        kv("DU", _n(2 * f["r"]))
        kv("AN", "1"); kv("MI", "0"); kv("S_", "1"); kv("S_P", "100")
        kv("AB", "32"); kv("WI", "0")
        if passante:
            kv("ZA", _n(alt))
        kv("ZT", "0"); kv("RM", "0"); kv("VW", "0")
        coda("Bohren vertikal", "Bohren vertikal",
             "60,61,62,90,91,92,150,190")

    # --- FreiFormTasche <181 per gli scassi SAGOMATI (contorno vero) ------
    # (template copiato dal programma macchina 05_Sottotop_A115)
    for nc, s in enumerate(sagome, 1):
        a("<181 \\FreiFormTasche\\")
        kv("EA", f"{nc}:0")
        kv("AD", "0"); kv("AZ", "5")
        kv("UZU", "1"); kv("ZU", "0.5")
        kv("TI", prof_mpr(s)); kv("ZA", _n(alt)); kv("ZT", "0")
        kv("HU", "0"); kv("UXY", "1"); kv("XY", "50")
        kv("T_", "101"); kv("F_", "5"); kv("DS", "1")
        kv("OSZI", "0"); kv("BL", "0"); kv("OSZVS", "0"); kv("SM", "0")
        kv("S_", "STANDARD")
        kv("HP", "0"); kv("SP", "0"); kv("YVE", "0")
        kv("WW", "1,3,4,133,135,137,139,211,213,214,215,216,217,401,403")
        kv("ASG", "2"); kv("HP_A_O", "STANDARD")
        kv("KG", "0"); kv("RP", "STANDARD")
        kv("KAT", "Freiformtasche"); kv("MNM", "Fräsen Tasche Freiform")
        kv("ORI", str(ori)); ori += 1
        kv("MX", "0"); kv("MY", "0"); kv("MZ", "0")
        kv("MXF", "1"); kv("MYF", "1"); kv("MZF", "1")
        kv("SYA", "0"); kv("SYV", "0")
        a("")

    # --- tasche <112 (scassi rettangolari e cerchi grandi) ----------------
    for s in scassi:
        if "contorno" in s:
            continue                        # gia' fatte come FreiFormTasche
        a("<112 \\Tasche\\")
        kv("RPX", "1"); kv("RPY", "1")
        if s.get("cir"):
            xa, ya = s["x"], s["y"]
            la = br = 2 * s["r"]
            rd = s["r"]
        else:
            xa = (s["x1"] + s["x2"]) / 2.0
            ya = (s["y1"] + s["y2"]) / 2.0
            la = s["x2"] - s["x1"]
            br = s["y2"] - s["y1"]
            rd = 0
        kv("XA", _n(xa)); kv("YA", _n(ya)); kv("FO", "0")
        kv("LA", _n(la)); kv("BR", _n(br)); kv("RD", _n(rd))
        kv("WI", "0"); kv("TI", prof_mpr(s)); kv("ZA", _n(alt))
        kv("ZT", "0"); kv("UXY", "1"); kv("XY", "80")
        kv("T_", "101"); kv("F_", "STANDARD"); kv("DS", "1")
        kv("OSZI", "0"); kv("BL", "0"); kv("OSZVS", "0"); kv("SM", "0")
        kv("S_", "STANDARD"); kv("UZU", "1"); kv("ZU", "0"); kv("BM", "0")
        kv("DHR", "0"); kv("LZR", "0"); kv("WZHR", "0"); kv("SZHR", "0")
        kv("ABS", "0")
        kv("HP", "0"); kv("SP", "0"); kv("YVE", "0")
        kv("WW", "1,2,3"); kv("ASG", "2"); kv("HP_A_O", "STANDARD")
        kv("KG", "0"); kv("RP", "STANDARD")
        kv("KAT", "Tasche"); kv("MNM", "Fräsen Tasche vertikal")
        kv("ORI", str(ori)); ori += 1
        kv("MX", "0"); kv("MY", "0"); kv("MZ", "0")
        kv("MXF", "0"); kv("MYF", "0"); kv("MZF", "0")
        kv("SYA", "0"); kv("SYV", "0"); kv("KO", "00")
        a("")

    # --- lamate di sezionatura <124 (frontali cassetto uniti) -------------
    # macro copiata dai programmi reali ("Sezionare con angolo-A", lama
    # T_149): linea verticale A FILO del bordo destro del pezzo di
    # sinistra, percorsa da sopra a sotto, compensazione WRKL = lama
    # DENTRO la fuga (a filo anche del pezzo di destra con fuga 3.2)
    for t in tagli:
        a("<124 \\Nut_R\\")
        kv("XA", _n(t["x"]))
        kv("WI", "90"); kv("WI2", "90")
        kv("YA", "h")
        kv("XE", _n(t["x"])); kv("YE", "0")
        kv("BL", "0"); kv("SK", "1"); kv("RK", "WRKL")
        kv("EM", "MOD2"); kv("MV", "GL")
        kv("Z_", "-9"); kv("VZ", "s-3"); kv("VT", "0")
        kv("AB", "0"); kv("XY", "1"); kv("MN", "GGL")
        kv("T_", "149"); kv("F_", "6"); kv("ZU", "0")
        kv("SM", "0"); kv("S_", "STANDARD"); kv("ZA", "s")
        coda("Geschwenktes Nuten", "Sezionare con angolo-A",
             "141,142,144,146")

    # --- tagli INCLINATI (biselli) con lama ad angolo-A -------------------
    # come TOP_1.mpr della ditta: linea in pianta sul lato ESTERNO +
    # WI=WI2="90-beta" (lato largo SOPRA: lama piegata sotto il pezzo)
    # oppure "90+beta" (lato largo sotto); fuori a sinistra, RK=WRKL
    for c in incl:
        wi = f"90{'-' if c['largo_sopra'] else '+'}{_n(c['beta'])}"
        a("<124 \\Nut_R\\")
        kv("XA", _n(c["t1"][0]))
        kv("WI", wi); kv("WI2", wi)
        kv("YA", _n(c["t1"][1]))
        kv("XE", _n(c["t2"][0])); kv("YE", _n(c["t2"][1]))
        kv("BL", "0"); kv("SK", "1"); kv("RK", "WRKL")
        kv("EM", "MOD2"); kv("MV", "GL")
        kv("Z_", "-9"); kv("VZ", "s-3"); kv("VT", "0")
        kv("AB", "0"); kv("XY", "1"); kv("MN", "GGL")
        kv("T_", "149"); kv("F_", "6"); kv("ZU", "0")
        kv("SM", "0"); kv("S_", "STANDARD"); kv("ZA", "s")
        coda("Geschwenktes Nuten", "Sezionare con angolo-A",
             "141,142,144,146")

    a("!")
    with open(path, "w", encoding="cp1252", errors="replace",
              newline="\r\n") as fh:
        fh.write("\n".join(L) + "\n")


# ========================= TechAutoX (mpr -> mprx) =========================
def techautox(mpr_path, mprx_path, log=print):
    """Applica la tecnologia e genera il .mprx con la CLI ufficiale HOMAG.
    TechAutoX corrompe i caratteri speciali nei percorsi (es. l'apostrofo
    tipografico di una cartella cliente diventa '?' -> "no such folder" e
    crash 0xC0000005): si lavora SEMPRE in una cartella temporanea con
    nomi semplici e si copia il risultato a destinazione."""
    if not os.path.exists(TECHAUTOX):
        raise RuntimeError(f"TechAutoX.exe non trovato in {WOODWOP_DIR}")
    logf = os.path.join(os.path.dirname(mprx_path), "_techauto_log.txt")
    tmpd = tempfile.mkdtemp(prefix="ta_")
    t_mpr = os.path.join(tmpd, "p.mpr")
    t_mprx = os.path.join(tmpd, "p.mprx")
    t_log = os.path.join(tmpd, "log.txt")
    try:
        shutil.copyfile(mpr_path, t_mpr)
        r = subprocess.run(
            [TECHAUTOX, t_mpr, t_mprx, f"-a={MACCHINA}",
             f"-logfile={t_log}", "-outputfileformat=MPRX"],
            cwd=WOODWOP_DIR, capture_output=True, timeout=180)
        try:
            if os.path.isfile(t_log):
                with open(t_log, "rb") as f0, open(logf, "ab") as f1:
                    f1.write(("--- " + os.path.basename(mpr_path)
                              + " ---\r\n").encode("utf-8", "replace"))
                    f1.write(f0.read())
        except OSError:
            pass
        if r.returncode != 0 or not os.path.exists(t_mprx):
            raise RuntimeError(f"TechAutoX fallito (exit {r.returncode}), "
                               f"vedi {os.path.basename(logf)}")
        shutil.copyfile(t_mprx, mprx_path)
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)


def converti(dxf_path, out_mpr=None, log=print, fai_mprx=True, out_mprx=None):
    """Scrive i .mpr in out_mpr e i .mprx in out_mprx (se diversa);
    se out_mprx non e' data, i .mprx finiscono insieme ai .mpr."""
    base = os.path.splitext(os.path.basename(dxf_path))[0]
    out_mpr = out_mpr or os.path.dirname(dxf_path)
    out_mprx = out_mprx or out_mpr
    (dims, fori_A, scassi_A, fori_B, scassi_B, tagli, sagome, incl,
     avvisi) = estrai_geometria(dxf_path, prof_d14=None)  # profondita' vere
    alt = dims[2]
    # REGOLA (utente 30/07/2026, supera la scelta del 22/07): il foro del
    # BARILOTTO D14x14.2 e' un FORO (BohrVert), NON una tasca fresata --
    # i D14 ciechi restano nelle punte (la conversione in tasche e' stata
    # tolta; le tasche tondeggianti ~D14 diventano fori gia' nell'estrattore)

    # lamate, sagomature e tagli inclinati solo nel programma principale
    programmi = [(base, fori_A, scassi_A, tagli, sagome, incl)]
    if fori_B or scassi_B:
        programmi.append((base + "_B", fori_B, scassi_B, [], [], []))
    for nome, fori, scassi, tg, prof, inc in programmi:
        mpr = os.path.join(out_mpr, nome + ".mpr")
        # squadratura solo nel principale: nel _B il pezzo e' gia' squadrato
        scrivi_mpr(mpr, dims, fori, scassi, tg, prof, inc,
                   squadra=not nome.endswith("_B"))
        riga = (f"  {nome}: {_n(dims[0])} x {_n(dims[1])} x {_n(dims[2])}, "
                f"{len(fori)} fori, {len(scassi)} tasche"
                + (f", {len(tg)} lamate" if tg else "")
                + (f", {len(prof)} sagomature" if prof else "")
                + (f", {len(inc)} tagli inclinati" if inc else "")
                + f" -> {nome}.mpr")
        if fai_mprx:
            mprx = os.path.join(out_mprx, nome + ".mprx")
            techautox(mpr, mprx, log)
            riga += " + .mprx"
            # SOLIDO 3D dentro l'MPRX (solo programma principale: nel _B
            # il pezzo e' ribaltato); se fallisce il programma resta buono
            if not nome.endswith("_B"):
                try:
                    from inietta_3d import inietta_3d as _in3d
                    if _in3d(dxf_path, mprx, log=lambda m: None):
                        riga += " + 3D"
                except Exception as ex:
                    log(f"    [!] 3D non iniettato in {nome}: {ex}")
        log(riga)
    for msg in avvisi:
        log(f"    [!] {msg}")
    return os.path.join(out_mpr, base + ".mpr")


# ============================== GUI ========================================
def main():
    root = tk.Tk()
    root.title("FILIERA UN CLIC  |  DXF 3D -> MPR + MPRX woodWOP (HOMAG)")
    root.geometry("720x460")
    files = []

    def scegli():
        sel = filedialog.askopenfilenames(
            title="Scegli i DXF 3D da convertire",
            filetypes=[("DXF", "*.dxf"), ("Tutti i file", "*.*")])
        if sel:
            files.clear(); files.extend(sel)
            lista.delete(0, "end")
            for f in files:
                lista.insert("end", f)

    def log(msg):
        box.config(state="normal"); box.insert("end", msg + "\n")
        box.see("end"); box.config(state="disabled"); root.update_idletasks()

    def avvia():
        if not files:
            messagebox.showwarning("Attenzione", "Prima scegli i DXF.")
            return
        base_dir = os.path.dirname(files[0])
        mpr_dir = os.path.join(base_dir, "MPR")
        mprx_dir = os.path.join(base_dir, "MPRX")
        os.makedirs(mpr_dir, exist_ok=True)
        os.makedirs(mprx_dir, exist_ok=True)
        ok, err = 0, 0
        for f in files:
            try:
                converti(f, mpr_dir, log, out_mprx=mprx_dir)
                ok += 1
            except Exception as e:
                err += 1
                log(f"  [ERRORE] {os.path.basename(f)}: {e}")
        log(f"\n>>> Fatto: {ok} convertiti, {err} errori. "
            f".mpr in MPR\\, .mprx in MPRX\\ <<<")
        if err:
            messagebox.showwarning("Completato con errori",
                                   f"{ok} convertiti, {err} errori (vedi log).")
        else:
            messagebox.showinfo("Fatto", f"{ok} pezzi convertiti:\n"
                                f".mpr in {mpr_dir}\n.mprx in {mprx_dir}")

    tk.Button(root, text="1)  Scegli i DXF 3D...", font=("Segoe UI", 11),
              command=scegli).pack(fill="x", padx=10, pady=(10, 4))
    lista = tk.Listbox(root, height=8); lista.pack(fill="x", padx=10)
    tk.Button(root, text="2)  CONVERTI IN MPR + MPRX",
              font=("Segoe UI", 12, "bold"), bg="#2e7d32", fg="white",
              command=avvia).pack(fill="x", padx=10, pady=6)
    box = tk.Text(root, height=12, state="disabled", font=("Consolas", 9))
    box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for pth in sys.argv[1:]:
            converti(pth)
    else:
        main()
