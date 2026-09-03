# -*- coding: utf-8 -*-
"""BOTTEGA3D — libreria per costruire esecutivi 3D di mobili in AutoCAD.

Racchiude quello che serve sempre: aggancio COM robusto all'AutoCAD gia' aperto,
layer a convenzione (FERRAMENTA_/FORO_/SCASSO_), pannelli come box, forature a
regola di bottega (spine 13/29, tazze 22,5, barilotto 14x15, REKORD, sistema 32),
verifica dei volumi, viste PNG, lista ferramenta e salvataggio.

Regole applicate: vedi Desktop\\CLAUDE\\MANUALE_ESECUTIVISTA.md
Uso tipico:

    from bottega3d import Mobile
    m = Mobile("NOME", out_dwg=r"...\\pezzo.dwg")
    m.box("01_Fianco_SX", m.NOB18, 0, 18, 0, 560, 0, 2000)
    m.spina_giunto("01_Fianco_SX", "03_Fondo", ...)
    m.chiudi()
"""
import json
import math
import os
import time
from array import array
from collections import Counter

import comtypes.client

ACUNION, ACSUBTRACT, ACINTERSECT = 0, 2, 1

# ---- regole di bottega (dal libro validato 504/504) ----
SPINA_FACCIA = 13.0
SPINA_COSTA = 29.0
TAZZA_DIA, TAZZA_PROF, TAZZA_QUOTA = 35.0, 13.0, 22.5
TAZZA_VITI_INTERASSE, TAZZA_VITI_ARRETRAMENTO = 45.0, 9.5
CERNIERA_DAL_FILO = 100.0
BASETTA_QUOTE = (20.0, 52.0)
BARILOTTO_DIA, BARILOTTO_PROF, BARILOTTO_DAL_BORDO = 14.0, 15.0, 21.0
BUSSOLA_DIA, BUSSOLA_PROF = 13.0, 14.4
SISTEMA32_DIA, SISTEMA32_PROF, SISTEMA32_DAL_FILO = 5.0, 13.0, 37.0
GIOCO = 3.0


def pt(x, y, z):
    return array('d', [float(x), float(y), float(z)])


def scegli_cerniera(sp_anta, sormonto, larghezza_anta=0.0, altezza_anta=0.0, B=5.0):
    """Formula catalogo Blum CLIP top 110: OL = X + B - H."""
    if sp_anta > 26:
        return {"tipo": "porta spessa 95", "cod": "71B9550", "basetta": "175H7100",
                "B": B, "H": 0.0, "OL": sormonto, "n": 3}
    if sormonto <= 0:
        X, tipo, cod = -7.5, "filo (inset)", "71B3750"
    elif sormonto <= 10:
        X, tipo, cod = 1.5, "mezza battuta", "71B3650"
    else:
        X, tipo, cod = 11.0, "battuta piena", "71B3550"
    H = min((0.0, 3.0, 9.0), key=lambda h: abs(h - (X + B - sormonto)))
    OL = X + B - H
    basetta = "175H3100" if H == 0 else ("175H7130" if H == 3 else "175H7190")
    # conteggio: peso (fascia catalogo) + 1 se anta larga oltre 600
    n = 2 if altezza_anta < 900 else 3 if altezza_anta < 1600 else 4 if altezza_anta < 2000 else 5
    if larghezza_anta > 600:
        n += 1
    return {"tipo": tipo, "cod": cod, "basetta": basetta, "B": B, "H": H, "OL": OL, "n": n}


def passo32(a, b, passo_min=110.0, passo_max=150.0, bordo=32.0, margine_min=24.0):
    """Fila a passo multiplo di 32 con margini simmetrici (regola sistema 32)."""
    lung = b - a
    utile = lung - 2 * bordo
    n = max(2, int(round(utile / ((passo_min + passo_max) / 2.0))) + 1)
    while n >= 2:
        step = max(32.0, round(utile / (n - 1) / 32.0) * 32.0)
        marg = (lung - (n - 1) * step) / 2.0
        if marg >= margine_min:
            return [a + marg + i * step for i in range(n)]
        n -= 1
    return [a + lung / 2.0]


class Mobile(object):
    def __init__(self, nome, out_dwg=None, scratch=None, layers_extra=None):
        self.nome = nome
        self.out_dwg = out_dwg
        self.scratch = scratch or os.path.expandvars(r"%TEMP%")
        self.registry = {}
        self.fori = []
        self.lista = Counter()
        self._n = Counter()
        self.errori = []
        self.app = self._aggancia()
        self.prev = self._r(lambda: self.app.ActiveDocument.Name, label="active")
        self.doc = self._r(lambda: self.app.Documents.Add(), label="Add")
        time.sleep(2)
        self.ms = self._r(lambda: self.doc.ModelSpace, label="ms")
        for v, val in (("SOLIDHIST", 1), ("SHOWHIST", 1), ("INSUNITS", 4)):
            self._r(lambda v=v, val=val: self.doc.SetVariable(v, val), label=v)
        self.LACC30 = "MDF LACC SP.30"
        self.LACC19 = "MDF LACC SP.19"
        self.BVN18 = "MDF VERN BVN SP.18"
        self.NOB18 = "MDF NOB BIANCO SP.18"
        base = {self.LACC30: 255, self.LACC19: 7, self.BVN18: 250, self.NOB18: 8,
                "FERRAMENTA_CERNIERA": 1, "FERRAMENTA_BASETTA": 30,
                "FERRAMENTA_PIEDINO": 6, "FERRAMENTA_VARIE": 3,
                "FORO_SPINA_D8": 240, "FORO_TAZZA_D35": 240, "FORO_VITE_D5": 240,
                "FORO_BARILOTTO_D14": 240, "FORO_BUSSOLA_D13": 240,
                "FORO_SISTEMA32_D5": 240, "FORO_PIEDINO_D12": 240,
                "FORO_CHIAVE_D6": 240, "FORO_PILOT_D3": 240, "FORO_VARIE": 240,
                "SCASSO_UTENSILE": 240}
        base.update(layers_extra or {})
        for n, c in base.items():
            self.layer(n, c)

    # ---------- COM ----------
    @staticmethod
    def _aggancia():
        for _ in range(90):
            try:
                a = comtypes.client.GetActiveObject("AutoCAD.Application")
                if "POINTER" in type(a).__name__:
                    return a
            except Exception:
                pass
            time.sleep(2)
        raise RuntimeError("AutoCAD non agganciato (serve early binding POINTER)")

    @staticmethod
    def _r(fn, tries=180, wait=1.0, label=""):
        last = None
        for _ in range(tries):
            try:
                return fn()
            except Exception as e:      # busy mascherato da AttributeError/COMError
                last = e
                time.sleep(wait)
        raise RuntimeError("COM fallito %s: %r" % (label, last))

    @staticmethod
    def nome_layer(nome):
        """AutoCAD vieta < > / \\ " : ; ? * | , = ` nei nomi layer."""
        out = "".join(" " if c in '<>/\\":;?*|,=`' else c for c in str(nome))
        out = " ".join(out.split()).strip(". ")
        return (out or "LAYER")[:200]

    def layer(self, nome, colore=7):
        nome = self.nome_layer(nome)

        def _mk():
            ly = self.doc.Layers.Add(nome)
            try:
                ly.color = colore
            except Exception:
                pass
            return ly
        return self._r(_mk, label="layer " + nome)

    # ---------- geometria ----------
    def box(self, nome, layer, x0, x1, y0, y1, z0, z1):
        layer = self.nome_layer(layer)
        cx, cy, cz = (x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0
        L, W, H = x1 - x0, y1 - y0, z1 - z0
        s = self._r(lambda: self.ms.AddBox(pt(cx, cy, cz), L, W, H), label="box " + nome)
        self._r(lambda: setattr(s, "Layer", layer), label="lay " + nome)
        self.registry[nome] = [s, L * W * H]
        return s

    def cilindro(self, cx, cy, cz, r, h, layer="SCASSO_UTENSILE", asse="z"):
        c = self._r(lambda: self.ms.AddCylinder(pt(cx, cy, cz), r, h), label="cyl")
        self._r(lambda: setattr(c, "Layer", layer), label="cyl lay")
        if asse == "x":
            self._r(lambda: c.Rotate3D(pt(cx, cy, cz), pt(cx, cy + 100, cz), math.pi / 2), label="rot x")
        elif asse == "y":
            self._r(lambda: c.Rotate3D(pt(cx, cy, cz), pt(cx + 100, cy, cz), math.pi / 2), label="rot y")
        return c

    def settore(self, nome, layer, cx, cy, r_est, r_int, z0, z1, quadrante):
        """Quarto d'anello (angolo raggiato). quadrante: 'so','se','no','ne'."""
        zm, h = (z0 + z1) / 2.0, z1 - z0
        out = self._r(lambda: self.ms.AddCylinder(pt(cx, cy, zm), r_est, h), label="set out")
        self._r(lambda: setattr(out, "Layer", layer), label="set lay")
        inn = self.cilindro(cx, cy, zm, r_int, h + 2)
        self._r(lambda: out.Boolean(ACSUBTRACT, inn), label="set anello")
        R = r_est + 50
        sx = -1 if quadrante[1] == "o" else 1     # o=ovest(x<cx), e=est(x>cx)
        sy = -1 if quadrante[0] == "s" else 1     # s=sud(y<cy), n=nord(y>cy)
        k1 = self.box("_k1", "SCASSO_UTENSILE",
                      cx if sx < 0 else cx - R, cx + R if sx < 0 else cx,
                      cy - R, cy + R, z0 - 2, z1 + 2)
        del self.registry["_k1"]
        self._r(lambda: out.Boolean(ACSUBTRACT, k1), label="set k1")
        k2 = self.box("_k2", "SCASSO_UTENSILE", cx - R, cx + R,
                      cy if sy < 0 else cy - R, cy + R if sy < 0 else cy, z0 - 2, z1 + 2)
        del self.registry["_k2"]
        self._r(lambda: out.Boolean(ACSUBTRACT, k2), label="set k2")
        self.registry[nome] = [out, math.pi * (r_est ** 2 - r_int ** 2) / 4.0 * h]
        return out

    def taglia(self, nome, tool, vol=None):
        self._r(lambda: self.registry[nome][0].Boolean(ACSUBTRACT, tool), label="cut " + nome)
        if vol is not None and self.registry[nome][1] is not None:
            self.registry[nome][1] -= vol
        elif vol is None:
            self.registry[nome][1] = None

    def unisci(self, nome, tool):
        self._r(lambda: self.registry[nome][0].Boolean(ACUNION, tool), label="uni " + nome)
        self.registry[nome][1] = None

    def scasso(self, nome, x0, x1, y0, y1, z0, z1, vol=None):
        t = self.box("_sc", "SCASSO_UTENSILE", x0, x1, y0, y1, z0, z1)
        del self.registry["_sc"]
        self.taglia(nome, t, vol if vol is not None else (x1 - x0) * (y1 - y0) * (z1 - z0))

    # ---------- forature ----------
    def foro(self, pezzo, fam, dia, prof, base, direz, layer="FORO_VARIE"):
        bx, by, bz = base
        dx, dy, dz = direz
        cx = bx + dx * (prof - 0.1) / 2.0
        cy = by + dy * (prof - 0.1) / 2.0
        cz = bz + dz * (prof - 0.1) / 2.0
        asse = "x" if abs(dx) > 0.5 else ("y" if abs(dy) > 0.5 else "z")
        cyl = self.cilindro(cx, cy, cz, dia / 2.0, prof + 0.1, layer, asse)
        self.taglia(pezzo, cyl, math.pi * (dia / 2.0) ** 2 * prof)
        self.fori.append({"pezzo": pezzo, "fam": fam, "dia": dia, "prof": prof,
                          "base": [round(v, 2) for v in base], "dir": list(direz)})

    def spina(self, portante, portato, base, direz_faccia, cod="SPINA_D8X30"):
        """Coppia foro faccia 13 (portante) + costa 29 (portato), stessa base."""
        d = direz_faccia
        self.foro(portante, "spina_faccia", 8.0, SPINA_FACCIA, base, d, "FORO_SPINA_D8")
        self.foro(portato, "spina_costa", 8.0, SPINA_COSTA, base,
                  (-d[0], -d[1], -d[2]), "FORO_SPINA_D8")
        self.lista[(cod, "Spina legno D8x30")] += 1

    def cerniera(self, anta, spalletta, x_tazza, y_anta, z, verso_x, x_faccia_spalletta,
                 verso_sp, cod="71B3550", basetta="175H3100", dir_tazza=(0, -1, 0)):
        """Tazza + 2 viti sull'anta, 2 fori basetta sulla spalletta (20/52 dal filo)."""
        self.foro(anta, "cerniera_tazza", TAZZA_DIA, TAZZA_PROF,
                  (x_tazza, y_anta, z), dir_tazza, "FORO_TAZZA_D35")
        for dz in (-TAZZA_VITI_INTERASSE / 2, TAZZA_VITI_INTERASSE / 2):
            self.foro(anta, "cerniera_vite", 5.0, 13.0,
                      (x_tazza + verso_x * TAZZA_VITI_ARRETRAMENTO, y_anta, z + dz),
                      dir_tazza, "FORO_VITE_D5")
        for q in BASETTA_QUOTE:
            self.foro(spalletta, "basetta_vite", 5.0, 13.0,
                      (x_faccia_spalletta, q, z), (verso_sp, 0, 0), "FORO_VITE_D5")
        self.lista[(cod, "Cerniera CLIP top 110")] += 1
        self.lista[(basetta, "Basetta")] += 1

    def barilotto(self, portato, portante, base_sede, dir_sede, base_perno, dir_perno):
        """Kit Pavanello: sede D14x15 a 21 dal bordo + bussola D13x14.4 sul portante."""
        self.foro(portato, "barilotto_sede", BARILOTTO_DIA, BARILOTTO_PROF,
                  base_sede, dir_sede, "FORO_BARILOTTO_D14")
        self.foro(portato, "perno_passaggio", 8.0, 26.0, base_perno, dir_perno, "FORO_SPINA_D8")
        self.foro(portante, "bussola", BUSSOLA_DIA, BUSSOLA_PROF, base_perno,
                  (-dir_perno[0], -dir_perno[1], -dir_perno[2]), "FORO_BUSSOLA_D13")
        for cod, d in (("00475143", "Barilotto D14 SL18 - LIVENZA"),
                       ("00491334", "Perno M6x7x36 I20 - EMUCA"),
                       ("00444828", "Bussola esagono M6x13 - PAVANELLO"),
                       ("00475372", "Grano 8MAx10 - LIVENZA")):
            self.lista[(cod, d)] += 1

    def rekord(self, pezzo, xm, y, z_basso, x_faccia, verso, int_h=25.0):
        """Piedino REKORD: gambo D12 prof Int+9 dal filo basso, chiave D6 a quota Int."""
        self.foro(pezzo, "rekord_gambo", 12.0, int_h + 9.0, (xm, y, z_basso), (0, 0, 1),
                  "FORO_PIEDINO_D12")
        self.foro(pezzo, "rekord_chiave", 6.0, 12.0, (x_faccia, y, z_basso + int_h),
                  (verso, 0, 0), "FORO_CHIAVE_D6")
        self.lista[("00650984", "Piedino REKORD TECH D12 Int%g - Pavanello" % int_h)] += 1

    def sistema32(self, pezzo, x_faccia, verso, y, z_da, z_a):
        z = z_da
        n = 0
        while z <= z_a:
            self.foro(pezzo, "sistema32", SISTEMA32_DIA, SISTEMA32_PROF,
                      (x_faccia, y, z), (verso, 0, 0), "FORO_SISTEMA32_D5")
            z += 32.0
            n += 1
        return n

    # ---------- chiusura ----------
    def verifica(self):
        report = []
        for nome, (sol, atteso) in sorted(self.registry.items()):
            try:
                v = self._r(lambda s=sol: s.Volume, tries=60, label="vol")
            except Exception as e:
                self.errori.append("%s: volume illeggibile %r" % (nome, e))
                continue
            if atteso is None:
                report.append("%-26s %12.0f mm3 (n/a)" % (nome, v))
                if v <= 0:
                    self.errori.append(nome + ": volume nullo")
            else:
                sc = abs(v - atteso) / atteso * 100 if atteso else 0
                report.append("%-26s %12.0f vs %12.0f (%+.2f%%)" % (nome, v, atteso, sc))
                if sc > 1.0:
                    self.errori.append("%s: scarto %.2f%%" % (nome, sc))
        return report

    def viste(self, prefisso):
        pngs = []
        for cmd, suff in (("_-VIEW _swiso _VSCURRENT _Conceptual ", "iso"),
                          ("_-VIEW _front ", "front")):
            png = os.path.join(self.scratch, "%s_%s.png" % (prefisso, suff))
            if os.path.exists(png):
                os.remove(png)
            self._r(lambda c=cmd: self.doc.SendCommand(c), label="vista")
            time.sleep(2)
            self._r(lambda: self.doc.SendCommand("_ZOOM _E "), label="zoom")
            time.sleep(1)
            self._r(lambda p=png: self.doc.SendCommand("FILEDIA 0 _PNGOUT %s\n\nFILEDIA 1 " % p),
                    label="png")
            t0 = time.time()
            while not os.path.exists(png) and time.time() - t0 < 90:
                time.sleep(1)
            if os.path.exists(png):
                pngs.append(png)
        self._r(lambda: self.doc.SendCommand("_-VIEW _swiso _ZOOM _E "), label="iso2")
        return pngs

    def _libera(self):
        if not self.out_dwg:
            return
        try:
            n = self._r(lambda: self.app.Documents.Count, tries=20, label="cnt")
            for i in range(n - 1, -1, -1):
                d = self._r(lambda i=i: self.app.Documents.Item(i), tries=20, label="item")
                if self._r(lambda d=d: d.Name, tries=20, label="nm").lower() != \
                        os.path.basename(self.out_dwg).lower():
                    continue
                if self._r(lambda d=d: d.ObjectID, tries=20, label="id") == \
                        self._r(lambda: self.doc.ObjectID, tries=20, label="id2"):
                    continue
                if self._r(lambda d=d: d.Saved, tries=20, label="sv"):
                    self._r(lambda d=d: d.Close(False), tries=20, label="close")
        except Exception:
            pass

    def chiudi(self, salva=True, viste=True, lista_txt=None, fori_json=None):
        rep = self.verifica()
        print("\n".join(rep), flush=True)
        if self.errori:
            print("!!! ANOMALIE:\n" + "\n".join(self.errori), flush=True)
        righe = ["LISTA FERRAMENTA - %s" % self.nome, "-" * 60]
        for (cod, descr), n in sorted(self.lista.items()):
            righe.append("%4d x %-26s %s" % (n, cod, descr))
        testo = "\n".join(righe)
        print(testo, flush=True)
        if lista_txt:
            open(lista_txt, "w", encoding="utf-8").write(testo)
        if fori_json:
            json.dump({"mobile": self.nome, "n_fori": len(self.fori), "fori": self.fori},
                      open(fori_json, "w", encoding="utf-8"), indent=1)
        pngs = self.viste(self.nome.replace(" ", "_")) if viste else []
        if salva and self.out_dwg:
            self._libera()
            try:
                self._r(lambda: self.doc.SaveAs(self.out_dwg), tries=30, wait=2.0, label="SaveAs")
            except Exception as e:
                alt = self.out_dwg.replace(".dwg", "_rev.dwg")
                print("SaveAs fallito (%r) -> %s" % (e, alt), flush=True)
                self._r(lambda: self.doc.SaveAs(alt), tries=30, wait=2.0, label="SaveAs alt")
                self.out_dwg = alt
            print("SALVATO:", self.out_dwg, flush=True)
        print("PEZZI: %d | FORI: %d" % (len(self.registry), len(self.fori)), flush=True)
        return {"pezzi": len(self.registry), "fori": len(self.fori),
                "errori": self.errori, "png": pngs, "dwg": self.out_dwg}
