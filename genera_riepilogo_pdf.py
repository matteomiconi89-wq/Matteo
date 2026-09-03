# -*- coding: utf-8 -*-
"""Genera il PDF di riepilogo di tutte le automazioni fatte con Matteo."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, HRFlowable, ListFlowable, ListItem)

import os
OUT = r"C:\Users\User\Desktop\Riepilogo_Automazioni_Matteo.pdf"
# Se il PDF è aperto in un visualizzatore non si può sovrascrivere: fallback a _v2
try:
    if os.path.exists(OUT):
        with open(OUT, "ab"):
            pass
except PermissionError:
    OUT = r"C:\Users\User\Desktop\Riepilogo_Automazioni_Matteo_v2.pdf"

# ---- Palette (tono legno/officina) ----
LEGNO   = colors.HexColor("#6B4423")   # marrone scuro
LEGNO2  = colors.HexColor("#A0703C")   # marrone chiaro
ACCENT  = colors.HexColor("#1F6E8C")   # blu petrolio (accenti tecnici)
GRIGIO  = colors.HexColor("#444444")
CHIP    = colors.HexColor("#EFE7DD")   # beige tabelle

styles = getSampleStyleSheet()

def S(name, **kw):
    base = kw.pop("parent", styles["Normal"])
    return ParagraphStyle(name, parent=base, **kw)

st_title   = S("T", parent=styles["Title"], fontSize=26, textColor=LEGNO, spaceAfter=4, leading=30)
st_sub     = S("Sub", fontSize=12.5, textColor=LEGNO2, alignment=TA_CENTER, spaceAfter=2)
st_meta    = S("Meta", fontSize=9.5, textColor=GRIGIO, alignment=TA_CENTER)
st_h1      = S("H1", fontSize=15, textColor=colors.white, leading=18,
               backColor=LEGNO, borderPadding=(6, 8, 6, 8), spaceBefore=16, spaceAfter=8,
               fontName="Helvetica-Bold")
st_h2      = S("H2", fontSize=12, textColor=ACCENT, fontName="Helvetica-Bold",
               spaceBefore=10, spaceAfter=3, leading=14)
st_h3      = S("H3", fontSize=10.3, textColor=LEGNO, fontName="Helvetica-Bold",
               spaceBefore=7, spaceAfter=2, leading=13)
st_body    = S("Body", fontSize=10, leading=14.5, alignment=TA_JUSTIFY, textColor=colors.HexColor("#222222"))
st_bul     = S("Bul", fontSize=9.7, leading=13.5, textColor=colors.HexColor("#222222"))
st_path    = S("Path", fontSize=8.3, leading=11, textColor=GRIGIO, fontName="Courier")
st_lead    = S("Lead", fontSize=10.5, leading=15, alignment=TA_JUSTIFY, textColor=colors.HexColor("#333333"))
st_toc     = S("Toc", fontSize=10.5, leading=17, textColor=colors.HexColor("#222222"))
st_note    = S("Note", fontSize=9, leading=12.5, textColor=GRIGIO)
st_periodo = S("Per", fontSize=9.5, textColor=LEGNO2, fontName="Helvetica-Oblique", spaceAfter=5)

def bullets(items, style=st_bul):
    return ListFlowable(
        [ListItem(Paragraph(t, style), leftIndent=10, value="-") for t in items],
        bulletType="bullet", start="-", bulletFontSize=9, leftIndent=14, spaceBefore=1, spaceAfter=1)

def chip_table(rows):
    t = Table(rows, colWidths=[34*mm, 132*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), CHIP),
        ("TEXTCOLOR", (0,0), (0,-1), LEGNO),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 8.6),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LINEBELOW", (0,0), (-1,-1), 0.4, colors.HexColor("#D8CBBA")),
        ("GRID", (0,0), (-1,-1), 0, colors.white),
    ]))
    return t

def rule():
    return HRFlowable(width="100%", thickness=0.8, color=LEGNO2, spaceBefore=2, spaceAfter=6)

story = []

# ===================== COPERTINA =====================
story.append(Spacer(1, 40*mm))
story.append(Paragraph("Riepilogo delle Automazioni", st_title))
story.append(Paragraph("Tutto quello che abbiamo costruito insieme", st_sub))
story.append(Spacer(1, 4))
story.append(HRFlowable(width="55%", thickness=1.2, color=LEGNO2, hAlign="CENTER"))
story.append(Spacer(1, 8))
story.append(Paragraph("Falegnameria &amp; progettazione mobili su misura<br/>"
                       "AutoCAD 3D &bull; AutoLISP &bull; Python &bull; Excel &bull; CNC", st_sub))
story.append(Spacer(1, 30*mm))
story.append(Paragraph("Preparato per <b>Matteo</b>", st_meta))
story.append(Paragraph("17 giugno 2026", st_meta))
story.append(PageBreak())

# ===================== INDICE =====================
story.append(Paragraph("Indice dei lavori", st_h1))
toc = [
    "1.  Disegno mobili 3D partendo da Excel (Python + AutoCAD)",
    "2.  Toolchain AutoLISP dentro AutoCAD (creazione, numerazione, misure, export CNC)",
    "3.  Automazione WoodWop &ndash; import STEP/DXF nel CNC",
    "4.  Confronto Programmi CNC &ndash; deduplica DXF per geometria reale",
    "5.  Conversione DWG -> STEP per CATIA",
    "6.  Automazione preventivi &ndash; SCHEDA BASE (laccatura / ferramenta / illuminazione)",
    "7.  BOM unificata e sezionatura (pulsante Excel + programma esterno)",
    "8.  Rinomina automatica dei DXF col Codice Vecchio",
    "9.  Confronto Sponsor 2025 / 2026 (Los Passo)",
    "10. Strumenti di supporto (immagini, foto->DXF, helper AutoCAD)",
    "11. Progetto business &ndash; “Il Falegname Digitale”",
]
for t in toc:
    story.append(Paragraph(t, st_toc))
story.append(Spacer(1, 8))
story.append(rule())
story.append(Paragraph(
    "Negli ultimi mesi abbiamo trasformato una serie di lavori manuali e ripetitivi della tua "
    "falegnameria in strumenti automatici: dal disegno 3D dei mobili alla generazione dei preventivi, "
    "dalla preparazione dei programmi CNC fino alla gestione delle distinte (BOM) e all'analisi dei dati. "
    "Questo documento li raccoglie tutti, con cosa fanno, dove stanno i file e le scelte tecniche principali.",
    st_lead))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<i>Nota: i periodi indicati in ogni scheda sono ricavati dallo storico delle nostre sessioni e sono "
    "quindi approssimativi. Il grosso del lavoro si colloca tra metà maggio e metà giugno 2026.</i>",
    st_note))
story.append(PageBreak())

# Helper per una "scheda progetto"
def progetto(num, titolo, riga_obiettivo, file_rows, cosa_fa, dettagli=None, stato=None, periodo=None):
    story.append(Paragraph(f"{num}.&nbsp; {titolo}", st_h1))
    if periodo:
        story.append(Paragraph("Periodo:&nbsp; " + periodo, st_periodo))
    story.append(Paragraph("<b>A cosa serve.</b> " + riga_obiettivo, st_body))
    story.append(Spacer(1, 4))
    story.append(Paragraph("File e cartelle", st_h2))
    story.append(chip_table(file_rows))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Cosa fa", st_h2))
    story.append(bullets(cosa_fa))
    if dettagli:
        story.append(Spacer(1, 4))
        story.append(Paragraph("Dettagli tecnici / scelte chiave", st_h2))
        story.append(bullets(dettagli))
    if stato:
        story.append(Spacer(1, 5))
        story.append(Paragraph("<b>Stato:</b> " + stato, st_note))

# ===================== 1. MOBILI DA EXCEL =====================
progetto(
    "1", "Disegno mobili 3D partendo da Excel",
    "Compili un file Excel con le misure e le opzioni, fai doppio clic su un .bat e AutoCAD "
    "disegna da solo il mobile in 3D completo di pannelli e ferramenta. Due rami: <b>Armadio</b> e "
    "<b>Pannellatura</b> (boiserie a moduli).",
    [
        ["Cartella", "Dropbox\\STEFANO\\Matteo\\MobiliAutoCAD\\ (rami USO e SVILUPPO)"],
        ["Armadio", "USO\\Armadio\\mobile.xlsx + disegna.bat -> mobile.dwg"],
        ["Pannellatura", "USO\\Pannellatura\\pannellatura.xlsx + disegna_pannelli.bat -> pannellatura.dwg + _BOM.xlsx"],
        ["Motore", "disegna_mobile.py (~1500 righe), disegna_pannelli.py (~620 righe)"],
        ["Stack", "Python 3.14 + pyautocad/COM, openpyxl, pywin32 - AutoCAD 2025"],
    ],
    [
        "<b>Armadio:</b> disegna base, cappello, fianchi, schienale, ripiani, ante, zoccolo e ripiani fissi "
        "con due modalità di montaggio (fianchi che vincono, oppure base e cappello).",
        "<b>Ferramenta vera, non box generici:</b> giunti RAFIX (bussola + perno + barilotto + grano), "
        "spine di legno Ø8, viti truciolari, reggipiano TRIS Art. 4103, piedini REKORD TECH Ø12.",
        "<b>Cerniere Blum</b> inserite come blocchi DWG reali (CLIP top BLUMOTION 110°, versione a battuta e "
        "a filo) con basette H.0/H.3 scelte in automatico dalla tabella sormonto; numero cerniere calcolato "
        "dall'altezza dell'anta; foratura coppa Ø35 + viti euro.",
        "<b>Pannellatura/boiserie:</b> moduli affiancati con telaio LSB, pannello frontale F_MULTI, listelli MDF, "
        "incastri Keku Häfele, scassi per LED, piedini e giunti telaio (viti o ISOFIX).",
        "<b>Distinta automatica (BOM):</b> a fine disegno crea pannellatura_BOM.xlsx con foglio Pannelli "
        "(un pezzo per riga: misure e quantità) e foglio Ferramenta (totali per codice).",
        "<b>Menu a tendina</b> sulle opzioni Excel a valori fissi, per non sbagliare a digitare.",
    ],
    [
        "Tutte le chiamate ad AutoCAD passano da una funzione di retry per gestire gli errori COM intermittenti.",
        "Distribuzione di fori, spine e ferramenta sempre a passo multiplo di 32 mm (sistema 32 standard).",
        "All'avvio gli script attivano SOLIDHIST + SHOWHIST, così i DWG mantengono la cronologia parametrica "
        "ed è possibile aprirli e modificare i primitivi.",
        "Per modificare/forare un DWG già aperto si lavora sull'istanza attiva (mai riaprirlo, o si crea una "
        "copia read-only): si trovano i solidi via handle e si tagliano con operazioni booleane affidabili.",
        "Naming dei layer standardizzato (FERRAMENTA_/FORO_/SCASSO_) per farli riconoscere dagli strumenti LISP.",
    ],
    "Armadio completo e operativo; pannellatura completa con BOM. Aperto: portare lo stesso tracking BOM "
    "anche su disegna_mobile.py.",
    periodo="maggio 2026 (armadio da metà mese; pannellatura 18&ndash;23 maggio)"
)
story.append(PageBreak())

# ===================== 2. AUTOLISP (custom, con sotto-sezioni) =====================
story.append(Paragraph("2.&nbsp; Toolchain AutoLISP dentro AutoCAD", st_h1))
story.append(Paragraph("Periodo:&nbsp; maggio&ndash;giugno 2026", st_periodo))
story.append(Paragraph(
    "<b>A cosa serve.</b> È la cassetta degli attrezzi che gira <b>dentro</b> AutoCAD: una serie di comandi "
    "scritti in AutoLISP che creano i mobili in modo parametrico e poi li <b>numerano, misurano ed esportano</b> "
    "per la produzione (distinte di taglio e file per il CNC). È il cuore che collega il disegno alla fabbrica.",
    st_body))
story.append(Spacer(1, 4))
story.append(Paragraph("File e comandi", st_h2))
story.append(chip_table([
    ["Cartella attiva", "Desktop\\CLAUDE\\Definitivi\\ (copia canonica; ci sono copie vecchie in autocad\\)"],
    ["Creazione", "crea-toilette.lsp -> CREA-TOILETTE  |  crea-armadio.lsp -> CREA-ARMADIO, CARICA-ARMADIO, IMPORTA-BLUM, PREPARA-BLUM"],
    ["Numerazione", "nomina-solididef.lsp -> NOMINASOL, LEGGISOL, RESETSOL + esplosi"],
    ["Esplodi blocchi", "esplodi-nomi.lsp -> ESPLODINOMI, TROVANOME, CONTANOMI, CHIRALITA"],
    ["Copia codici", "copia-codici.lsp -> ESPORTACODICI, APPLICACODICI, LEGGICHIAVE"],
    ["Misure / BOM", "misure-solidi.lsp -> MISURESOL"],
    ["Export CNC", "esporta-solidi.lsp -> ESPSOL (un DXF per pezzo)"],
]))

story.append(Paragraph("Comando per comando", st_h2))

story.append(Paragraph("Creazione modelli &ndash; crea-toilette / crea-armadio", st_h3))
story.append(bullets([
    "<b>CREA-TOILETTE:</b> costruisce la composizione toilette parametrica (armadi grandi e piccoli, montanti, "
    "nicchia centrale con piano e specchio, cassetti con guide Blum Movento); ti chiede tutte le quote a video "
    "con valori di default.",
    "<b>CREA-ARMADIO:</b> armadio a vani parametrico, con un <b>layer per materiale</b>, ante in battuta / a filo / "
    "mezza battuta, cerniere Blum (modello o blocco STP), guide Movento, e interni a scelta (appendiabiti, ripiani, "
    "cassetti+ripiani). <b>CARICA-ARMADIO</b> fa lo stesso leggendo i parametri da un CSV (armadio-parametri.xlsx).",
    "<b>IMPORTA-BLUM / CREA-BLOCCO-BLUM / PREPARA-BLUM:</b> importano la cerniera Blum dal file STP e la "
    "trasformano in un blocco riusabile, con l'origine messa sul centro coppa.",
]))

story.append(Paragraph("Numerazione pezzi &ndash; NOMINASOL", st_h3))
story.append(bullets([
    "<b>NOMINASOL</b> assegna un codice a ogni pannello (la ferramenta è esclusa). In <b>Automatico</b> dà lo "
    "<b>stesso codice ai pezzi identici</b> grazie a una firma geometrica (dimensioni + volume + baricentro a 4 "
    "decimali) che però distingue i pezzi speculari destro/sinistro. In <b>Manuale</b> scrivi tu il numero pezzo "
    "per pezzo, e quello appena fatto viene nascosto così non lo conti due volte. Crea anche l'etichetta col "
    "numero sulla faccia del pezzo.",
    "<b>LEGGISOL / RESETSOL / MOSTRASOL:</b> leggi il codice di un pezzo, azzeri tutto, rendi di nuovo visibili "
    "i pezzi nascosti dal manuale.",
    "<b>ESPLODISOL / ESPLODIMONTAGGIO / ESPLODIBASI</b> (+ <b>RICOMPONI</b>): viste esplose dei mobili &ndash; "
    "radiale, in stile istruzioni di montaggio (ogni pannello si stacca lungo il suo spessore), o mobile per mobile "
    "&ndash; e ritorno esatto alla posizione originale.",
]))

story.append(Paragraph("Esplosione blocchi che mantengono il nome &ndash; ESPLODINOMI", st_h3))
story.append(bullets([
    "<b>ESPLODINOMI</b> esplode i blocchi (anche annidati su più livelli) e <b>trasferisce il nome del blocco</b> "
    "ai pezzi che ne escono, così la distinta li ritrova già nominati senza rinumerarli; la ferramenta resta come "
    "blocco. Se un blocco specchiato non si esplode, non lo perde: lo segnala nel report finale.",
    "<b>TROVANOME / CONTANOMI / CHIRALITA:</b> diagnostica per capire perché un pezzo non compare in lista, o se "
    "due pezzi speculari rischiano di essere uniti per errore nella distinta.",
]))

story.append(Paragraph("Copia codici tra disegni &ndash; copia-codici", st_h3))
story.append(bullets([
    "<b>ESPORTACODICI</b> + <b>APPLICACODICI:</b> copiano i codici da un disegno già numerato a uno nuovo con "
    "pezzi quasi uguali, abbinando per materiale (layer) + misure entro tolleranza (±2 mm) e usando baricentro e "
    "volume come spareggio per i speculari. I pezzi non abbinati o ambigui finiscono in un report.",
]))

story.append(Paragraph("Misure e distinta &ndash; MISURESOL", st_h3))
story.append(bullets([
    "<b>MISURESOL</b> esporta un Excel a due fogli &ndash; <b>SOLIDI</b> (i pannelli) e <b>FERRAMENTA</b> &ndash; "
    "misurando ogni pezzo e <b>raggruppandolo per geometria con la quantità</b>. Formato concordato: CODICE | "
    "MOBILE | MATERIALE | Q.TÀ | PEZZO | H | L | SP. Lavora su copie, quindi non tocca il disegno.",
]))

story.append(Paragraph("Export DXF per il CNC &ndash; ESPSOL", st_h3))
story.append(bullets([
    "<b>ESPSOL</b> esporta <b>ogni pannello in un DXF separato</b>, prima allineandolo al suo ingombro reale "
    "(faccia grande a terra, lato lungo su X, spessore su Z) con un algoritmo geometrico PCA/Jacobi, e raggruppando "
    "i pezzi identici. È il file che poi va al nesting/CNC e che alimenta gli altri strumenti (rinomina DXF, "
    "Confronto Programmi).",
]))

story.append(Spacer(1, 4))
story.append(Paragraph("Dettagli tecnici / scelte chiave", st_h2))
story.append(bullets([
    "Volume, baricentro e bounding box <b>non sono leggibili da Python</b> su questa configurazione: vanno "
    "calcolati in AutoLISP e passati a Python via CSV, che poi costruisce l'Excel.",
    "La firma usa il <b>baricentro relativo</b> a 4 decimali e NON i prodotti d'inerzia (instabili numericamente "
    "per i pezzi lontani dall'origine). La stessa firma è usata da NOMINASOL e da MISURESOL, così codici e "
    "raggruppamenti coincidono.",
    "In AutoCAD 2025 alcuni comandi sono inaffidabili (BOX da riga di comando, Boolean silenzioso): si usano le "
    "API vla- equivalenti.",
]))
story.append(Spacer(1, 5))
story.append(Paragraph("<b>Stato:</b> toolchain completa e in uso; modificare sempre prima la copia in Definitivi.", st_note))
story.append(PageBreak())

# ===================== 3. WOODWOP =====================
progetto(
    "3", "Automazione WoodWop &ndash; import STEP/DXF nel CNC",
    "Importa automaticamente in <b>WoodWop</b> (il CAM del centro di lavoro) una cartella intera di file STEP/DXF: "
    "esegue da solo la sequenza di click e tasti per ogni file e salva il programma in uscita. Toglie un lavoro "
    "ripetitivo e lungo: importare i pezzi uno per uno.",
    [
        ["Programma", "WoodWop_Automazione_COMPLETO.ahk (AutoHotkey)"],
        ["Cartella", "Desktop\\CLAUDE\\Definitivi\\"],
        ["Config", "woodwop_coords.ini (coordinate dei click + colore sfondo, generato in calibrazione)"],
    ],
    [
        "<b>Calibrazione una tantum:</b> registri la sequenza dei tuoi click (CTRL+SHIFT+C), il colore di sfondo "
        "della vista 3D (CTRL+SHIFT+B) e le posizioni (CTRL+SHIFT+O); tutto viene salvato nel file .ini.",
        "<b>Esecuzione (CTRL+G):</b> scegli cartella di origine e di destinazione; conta i file STP/STEP/DXF e per "
        "ognuno ripete i 17 passi (File -> Importa -> CAD, incolla il percorso, Invio, seleziona l'oggetto, Genera / "
        "Rilevamento caratteristiche, Salva con nome).",
        "<b>Trova il pezzo da solo:</b> scansiona la viewport e clicca il primo pixel diverso dal colore di sfondo; "
        "se non lo trova, ti chiede di cliccarlo a mano e prosegue.",
        "Aspetta che il cursore torni “normale” prima di continuare (gestisce i tempi di caricamento) e "
        "chiude da solo il messaggio “Impossibile trovare caratteristiche”.",
    ],
    [
        "È una macro che clicca a coordinate dello schermo: va <b>ricalibrata</b> se cambia la disposizione delle "
        "finestre, la risoluzione o il monitor.",
        "Gestisce un passo extra per i DXF (un Invio aggiuntivo) e mostra una barra di avanzamento con il conteggio "
        "file e gli eventuali errori a fine corsa.",
    ],
    "Funzionante; richiede la calibrazione iniziale e WoodWop aperto.",
    periodo="2026"
)
story.append(PageBreak())

# ===================== 4. CONFRONTO PROGRAMMI =====================
progetto(
    "4", "Confronto Programmi CNC &ndash; deduplica DXF",
    "Prende le cartelle delle varie camere piene di programmi CNC .dxf e tiene solo i programmi davvero unici, "
    "confrontandoli per geometria reale e non per nome o data. Genera anche il riepilogo Excel.",
    [
        ["App", "confronta_file_unici_dxf (Desktop\\CLAUDE\\ConfrontoProgrammi\\ + .exe sul Desktop)"],
        ["Uso", "GUI un pulsante -> scegli la cartella lavoro -> crea PROGRAMMI_UNICI"],
        ["Regole CNC", "_REGOLE_CNC.xlsx (creato al primo giro, poi lo modifichi tu)"],
    ],
    [
        "Confronto per <b>geometria vera ACIS</b> (vertici + fori, normalizzati): l'hash dei byte del file non "
        "funziona perché cambiano data/ora e ID a ogni export.",
        "I pezzi uguali in più camere danno un solo file; quelli diversi prendono un suffisso con le camere.",
        "Colonna CAMERE sempre con la lista esplicita delle camere (mai “TUTTE”).",
        "<b>Riepilogo Excel</b> con MATERIALE / CNC / BORDATURA compilate in automatico dal numero del pezzo, "
        "secondo le regole in _REGOLE_CNC.xlsx.",
        "<b>Pulizia nome:</b> butta via codice commessa, revisioni e suffisso _bis davanti/dietro, tenendo "
        "il nome utile NN_Descrizione.",
    ],
    [
        "ezdxf di alto livello non legge questo tipo di ACIS: si usa il decoder SAB a basso livello.",
        "Sincronizzazione minima dei file (solo mancanti/diversi) con retry sui lock di Dropbox/AutoCAD.",
        "Ricompilazione exe con PyInstaller; aggiornare anche la copia sul Desktop che lanci tu.",
    ],
    "In uso sul lavoro 21032 (di cui tieni una copia curata a mano che NON va rigenerata sopra).",
    periodo="giugno 2026 (11&ndash;15 giugno)"
)
story.append(PageBreak())

# ===================== 5. DWG -> STEP =====================
progetto(
    "5", "Conversione DWG -> STEP per CATIA",
    "Converte i mobili 3D dal formato AutoCAD al formato STEP, il formato neutro per passare i solidi a chi "
    "lavora in CATIA.",
    [
        ["Script", "dwg2step.py (Desktop\\CLAUDE\\dwg2step\\)"],
        ["Motore", "FreeCAD in modalità batch (FreeCADCmd.exe)"],
        ["Catena", "AutoCAD ACISOUT -> .sat -> script -> STEP"],
    ],
    [
        "Converte DWG/DXF/SAT in STEP, sia singolo file sia intera cartella.",
        "Per solidi affidabili conviene passare da .sat (la via DWG diretta perde spesso i solidi ACIS).",
    ],
    None,
    "Funzionante; richiede FreeCAD + ODA File Converter configurati.",
    periodo="maggio 2026"
)

# ===================== 6. SCHEDA BASE =====================
progetto(
    "6", "Automazione preventivi &ndash; SCHEDA BASE",
    "Da un'unica scheda di preventivo (SCHEDA BASE) genera in automatico i fogli pronti da mandare ai fornitori: "
    "laccatura per ogni laccatore, ferramenta, illuminazione e sezionatura.",
    [
        ["Programma", "automazioni_excel_FINALE.py (GUI con finestra)"],
        ["Copie", "Desktop\\CLAUDE\\Definitivi\\ + Dropbox\\STEFANO\\Matteo\\CLAUDE\\Definitivi\\"],
        ["Input", "SCHEDA BASE*.xlsm (foglio GENERALE, misure in mm)"],
        ["Output", "Fogli FERRAMENTA, ILLUMINAZIONE, LACCATURA_<fornitore>, SEZIONE"],
    ],
    [
        "Legge il foglio GENERALE (materiali, quantità, dimensioni, lati da laccare, finiture) e ribalta i dati "
        "nei fogli per fornitore, già nelle unità giuste (i fogli laccatura in cm).",
        "<b>Calcolo laccatura</b> secondo le tue regole: a MQ conta faccia per numero di lati più le coste "
        "(perimetro × spessore); a ML conta l'altezza in metri con minimo 1 m a pezzo; colonne CART.RA al ML e al MQ.",
        "Riga di riepilogo VERNICIATURA con una riga per finitura.",
    ],
    [
        "Le SCHEDA BASE hanno molti menu a tendina (validazioni): si modificano via Excel COM sull'istanza già "
        "aperta, MAI con openpyxl, che al salvataggio cancellerebbe i dropdown. Backup automatico prima di toccare.",
        "Esiste anche una skill dedicata (applica-laccature) che documenta e applica le formule di laccatura.",
    ],
    "In uso sul progetto 25-A019 GUIDO_St Paul (Master Bedroom).",
    periodo="inizio giugno 2026"
)
story.append(PageBreak())

# ===================== 7. BOM UNIFICATA =====================
progetto(
    "7", "BOM unificata e sezionatura",
    "Dalla distinta grezza dei pezzi genera la BOM completa con le colonne calcolate e la sezionatura "
    "consolidata per il taglio. Due modi d'uso: un pulsante dentro Excel e un programma esterno che non apre Excel.",
    [
        ["Pulsante Excel", "BOM_unificata*.xlsm + bom_automation.py (xlwings) - macro Rigenera"],
        ["Cartella", "Dropbox\\STEFANO\\Matteo\\ExtraOrdinario\\21032\\"],
        ["Programma esterno", "Desktop\\CLAUDE\\bom_exe\\ - genera_sezionatura_cp_21032.exe (+ .py)"],
        ["Output exe", "<nome>_LAVORATO.xlsx (origine intatto)"],
    ],
    [
        "<b>Versione pulsante:</b> dentro il file BOM un pulsante “Rigenera” ricalcola le colonne J-O/Q e "
        "la sezionatura; può anche scegliere un altro file BOM e rigenerarlo lasciando intatto quello col pulsante.",
        "<b>Versione exe (senza aprire Excel):</b> trascini il file grezzo sull'eseguibile e ottieni un nuovo file "
        "_LAVORATO con BOM completa, commessa, e foglio sezionatura consolidato; l'originale non viene toccato.",
        "<b>Frontali cassetto:</b> le righe SX/DX/CX vengono unite correttamente (gestendo suffissi e prefissi modello), "
        "con l'abbondo di 10 mm applicato solo ai pezzi realmente presenti.",
        "Formattazione identica al master (intestazioni ciano, bordi, filtri, riquadri bloccati).",
    ],
    [
        "La BOM tiene le formule visibili (così le puoi controllare); la sezionatura è a valori, "
        "calcolata in Python con la stessa logica. Verifica: 156/157 gruppi identici al ricalcolo Excel.",
        "L'exe legge le colonne per nome di intestazione (robusto se cambia l'ordine) e lavora a file chiuso "
        "(rileva i lock di Excel/Dropbox).",
    ],
    "Entrambe le versioni funzionanti; se modifichi i dati a monte va rilanciato (la sezionatura non si auto-aggiorna).",
    periodo="giugno 2026 (pulsante Excel, poi versione exe)"
)
story.append(PageBreak())

# ===================== 8. RINOMINA DXF =====================
progetto(
    "8", "Rinomina automatica dei DXF col Codice Vecchio",
    "Per ogni cartella MOBILE_x rinomina i file DXF dal codice nuovo al codice vecchio, leggendo la corrispondenza "
    "direttamente dall'Excel che tieni aperto (con le modifiche non ancora salvate).",
    [
        ["Contesto", "Dropbox\\STEFANO\\25-A019 GUIDO_St Paul - cartelle Esecutivi\\DXF\\MOBILE_x"],
        ["Sorgente dati", "Excel APERTO MOBILE_x.xlsx, foglio SOLIDI (live via win32com)"],
        ["Mappa", "colonna A CODICE (nome attuale) -> colonna I COD. VECCHIO (nuovo nome)"],
    ],
    [
        "Legge i dati dall'istanza Excel viva, perché la colonna COD. VECCHIO spesso esiste solo in RAM.",
        "Rinomina sempre in <b>due fasi</b> (prima tutti i file in nomi temporanei, poi nei nomi finali) perché "
        "è una permutazione: un target coincide spesso con un altro file.",
        "Gestisce i pezzi senza codice vecchio e gli orfani spostandoli in _backup_rinomina (mai cancellati a caso).",
        "A fine corsa scrive un log della mappa e uno script di UNDO per annullare tutto.",
    ],
    [
        "Gestione dei lock Dropbox (WinError 32): controllo iniziale, retry con attesa, rollback automatico della fase 1.",
        "L'auto-rilevamento della colonna per nome non funziona (è scritta “COD. VECCHIO”): si usa l'indice di colonna.",
    ],
    "Prassi consolidata; le scelte sui pezzi extra le decidi tu caso per caso.",
    periodo="giugno 2026 (inizio&ndash;metà mese)"
)
story.append(PageBreak())

# ===================== 9. CONFRONTO SPONSOR =====================
progetto(
    "9", "Confronto Sponsor 2025 / 2026 (Los Passo)",
    "Confronta gli incassi degli sponsor di due anni (2025 contro 2026) per <b>Los Passo</b>: chi ha rinnovato, "
    "chi è da richiamare, i nuovi, gli aumenti e i cali. Produce un Excel con sintesi, tabelle colorate e grafici.",
    [
        ["Analisi a video", "analisi_sponsor.py (stampa il confronto in console)"],
        ["Genera Excel", "genera_excel_confronto.py -> CONFRONTO_SPONSOR_2025_2026.xlsx"],
        ["Cartella output", "Dropbox\\STEFANO\\Matteo\\"],
        ["Input", "sponsor_los_passo.xlsx (fogli SPONSOR 2025 / SPONSOR 2026)"],
    ],
    [
        "<b>Abbina i clienti</b> tra i due anni prima per Partita IVA, poi per nome normalizzato (toglie "
        "SRL/SNC/SAS, punteggiatura, spazi doppi).",
        "<b>Classifica ogni sponsor:</b> Confermato, Aumentato, Diminuito, Da rinnovare (perso), Nuovo pagante, "
        "Nuovo contatto.",
        "<b>Excel a 4 fogli:</b> Sintesi (totali, variazione %, scomposizione), Confronto Clienti (una riga per "
        "cliente, colorata per stato), Da Richiamare (i 2025 non ancora rinnovati, ordinati per importo), "
        "Per Responsabile con <b>grafico a barre</b> 2025 vs 2026.",
    ],
    [
        "Salta le righe “totale” mascherate da sponsor e gli importi non numerici; pulisce le partite IVA.",
        "Tutto con openpyxl (non apre Excel); i grafici sono nativi del file Excel.",
    ],
    "Funzionante; i dati 2026 sono “al 10/06”, quindi va rigenerato quando aggiorni il file sorgente.",
    periodo="giugno 2026 (dati al 10/06)"
)
story.append(PageBreak())

# ===================== 10. STRUMENTI =====================
story.append(Paragraph("10.&nbsp; Strumenti di supporto", st_h1))
story.append(Paragraph("Periodo:&nbsp; maggio&ndash;giugno 2026 (man mano che servivano)", st_periodo))
story.append(Paragraph(
    "Oltre ai progetti principali abbiamo messo a punto diversi strumenti più piccoli che tornano utili in più lavori:",
    st_body))
story.append(Spacer(1, 4))
story.append(bullets([
    "<b>Estrazione immagini dalla chat:</b> le foto che incolli vengono salvate come PNG sul disco "
    "(estrai_immagini.py), per poterle elaborare/misurare.",
    "<b>Foto -> DXF (vettorizzazione):</b> vettorizza.py trasforma un'immagine raster in un DXF di contorni, "
    "in puro Python con la sola libreria PIL.",
    "<b>Helper AutoCAD:</b> dump della geometria via LISP, screenshot della finestra, lettura della trasformazione "
    "dei blocchi posizionati a mano, conversione misure CSV -> Excel.",
    "<b>Ambiente:</b> su questa macchina Python si lancia con il launcher <font face='Courier'>py</font>; "
    "installate Pillow, ezdxf, openpyxl, pywin32, PyInstaller, reportlab.",
]))
story.append(Spacer(1, 10))

# ===================== 11. BUSINESS =====================
story.append(Paragraph("11.&nbsp; Progetto business &ndash; “Il Falegname Digitale”", st_h1))
story.append(Paragraph("Periodo:&nbsp; giugno 2026", st_periodo))
story.append(Paragraph(
    "Oltre agli strumenti tecnici, abbiamo impostato un piano per monetizzare online il tuo lavoro di falegname "
    "con post e reel.", st_body))
story.append(Spacer(1, 4))
story.append(Paragraph("File e cartelle", st_h2))
story.append(chip_table([
    ["Cartella", "Desktop\\CLAUDE\\business_reel\\"],
    ["Documenti", "1_PIANO_BUSINESS.md, 2_30_IDEE_REEL.md, 3_SCRIPT_PRIMI_10_REEL.md, 4_CALENDARIO_MESE_1.md"],
]))
story.append(Spacer(1, 6))
story.append(Paragraph("Cosa contiene", st_h2))
story.append(bullets([
    "Tre fonti di guadagno: commesse da privati via DM/WhatsApp; vendita del sistema Excel/AutoCAD ad altri "
    "falegnami (49-149 €); affiliazioni e sponsor a regime.",
    "30 idee di reel, gli script dei primi 10 e il calendario del primo mese.",
    "Il reel n.10 è il test del prodotto digitale (CTA: commento “SISTEMA”).",
]))

story.append(Spacer(1, 16))
story.append(rule())
story.append(Paragraph(
    "<b>In sintesi:</b> abbiamo coperto l'intera catena del tuo lavoro &ndash; progettazione 3D, numerazione e "
    "distinte, preventivi, preparazione e deduplica dei programmi CNC, scambio file con altri CAD, e perfino la "
    "parte commerciale e l'analisi dati. Quando vuoi aggiungere un nuovo pezzo o sistemare qualcosa, partiamo da qui.",
    st_lead))

# ---- numerazione pagine ----
def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LEGNO2)
    canvas.setLineWidth(0.5)
    canvas.line(20*mm, 14*mm, 190*mm, 14*mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRIGIO)
    canvas.drawString(20*mm, 9*mm, "Riepilogo automazioni - Matteo")
    canvas.drawRightString(190*mm, 9*mm, "Pag. %d" % doc.page)
    canvas.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=20*mm, rightMargin=20*mm,
                        topMargin=18*mm, bottomMargin=20*mm,
                        title="Riepilogo Automazioni - Matteo",
                        author="Claude Code")
doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=footer)
print("PDF creato:", OUT)
