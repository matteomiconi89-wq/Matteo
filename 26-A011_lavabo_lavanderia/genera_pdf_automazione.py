#!/usr/bin/env python3
"""PDF riassuntivo dell'automazione DWG -> 3D volumi -> render Manus."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, Image, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)
from PIL import Image as PILImage

W, H = A4
SCR = "/tmp/claude-0/-home-user-Matteo/9d8a08b3-647f-5483-95d8-409ee5c210e1/scratchpad"
PDF = f"{SCR}/pdf"
OUT = f"{PDF}/AUTOMAZIONE_DWG_RENDER.pdf"

BLU = colors.HexColor("#1f3a5f")
GRIGIO = colors.HexColor("#555555")
CHIARO = colors.HexColor("#f1f0ed")
ORO = colors.HexColor("#a2701c")

ss = getSampleStyleSheet()
S = {
    "titolo": ParagraphStyle("t", parent=ss["Title"], fontSize=21, leading=24, textColor=BLU, spaceAfter=1),
    "sottotitolo": ParagraphStyle("st", parent=ss["Normal"], fontSize=10, leading=13,
                                  textColor=GRIGIO, alignment=TA_CENTER, spaceAfter=13),
    "fase": ParagraphStyle("f", parent=ss["Heading2"], fontSize=12.5, leading=15, textColor=BLU,
                           spaceBefore=9, spaceAfter=3),
    "corpo": ParagraphStyle("c", parent=ss["Normal"], fontSize=9.5, leading=13, alignment=TA_JUSTIFY,
                            spaceAfter=3),
    "did": ParagraphStyle("d", parent=ss["Normal"], fontSize=8, leading=10, textColor=GRIGIO,
                          alignment=TA_CENTER, spaceBefore=2, spaceAfter=6),
    "chi": ParagraphStyle("ch", parent=ss["Normal"], fontSize=9, leading=12, textColor=colors.white),
    "cella": ParagraphStyle("ce", parent=ss["Normal"], fontSize=8.6, leading=11),
}


def foto(nome, altezza_mm):
    w0, h0 = PILImage.open(f"{PDF}/{nome}").size
    h = altezza_mm * mm
    return Image(f"{PDF}/{nome}", width=h * w0 / h0, height=h)


def fascia(testo):
    t = Table([[Paragraph(testo, S["chi"])]], colWidths=[166 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLU),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def riquadro(righe, titolo=None):
    dati = ([[Paragraph(f"<b>{titolo}</b>", S["corpo"])]] if titolo else [])
    dati += [[Paragraph(r, S["corpo"])] for r in righe]
    t = Table(dati, colWidths=[166 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CHIARO),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#cfcbc3")),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


story = []

# ============ PAGINA 1 ============
story.append(Paragraph("Automazione DWG &rarr; Render", S["titolo"]))
story.append(Paragraph("Come lavoriamo io e Manus sui tuoi disegni &mdash; commessa 26-A011 "
                       "&middot; aggiornato al 12/08/2026", S["sottotitolo"]))
story.append(fascia("IL FLUSSO IN 7 PASSI &mdash; in arancione i passi dove decidi tu"))
story.append(Spacer(1, 5))

passi = [
    ("1", "Mi mandi il DWG", "In chat o su Dropbox. Nient'altro: le misure le prendo io dal file.", True),
    ("2", "Leggo le misure vere dal CAD", "Converto il DWG, esplodo i blocchi e leggo le coordinate reali in "
     "millimetri: spessori, luci dei vani, quote. Mai stime a occhio dalle immagini.", False),
    ("3", "Costruisco il 3D dei soli volumi", "Ogni pannello diventa un solido vero, alle misure esatte. "
     "Niente ferramenta e niente forature: solo i volumi, quelli che si vedono.", False),
    ("4", "TU LO APPROVI IN AUTOCAD", "Ti mando un DXF 3D e uno script che ti ricrea i solidi in AutoCAD. "
     "Lo orbiti, lo misuri, mi dici cosa non va. Qui le correzioni costano ZERO crediti.", True),
    ("5", "Briefo Manus", "Gli do la scheda di collaudo, le tavole CAD, il 3D approvato e la gabbia in pixel. "
     "Massimo 3-4 correzioni per giro, sempre con la lista di cosa NON deve cambiare.", False),
    ("6", "Collaudo il render", "Misuro i rapporti sui pixel, zoomo sulle zone critiche, ricontrollo anche "
     "quello che era gi&agrave; giusto. Le proporzioni fini le sistemo io dopo, e non costano nulla.", False),
    ("7", "Ti consegno solo ci&ograve; che passa", "Un render bocciato non arriva sulla tua scrivania. "
     "L'ultima parola resta comunque al tuo occhio.", True),
]
righe = []
for n, tit, desc, tuo in passi:
    col = ORO if tuo else BLU
    righe.append([
        Paragraph(f'<font color="{col.hexval()}" size="15"><b>{n}</b></font>', S["corpo"]),
        Paragraph(f'<b><font color="{col.hexval()}">{tit}</font></b><br/>{desc}', S["corpo"]),
    ])
t = Table(righe, colWidths=[11 * mm, 155 * mm])
t.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 4.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
    ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#dedad3")),
]))
story.append(t)
story.append(Spacer(1, 9))
story.append(riquadro([
    "Il passo 4 &egrave; la novit&agrave; di oggi. Prima si andava dritti a Manus e gli errori di geometria si "
    "scoprivano dopo aver speso crediti: sulla cucina sono serviti 11 giri, sulla lavanderia 8. "
    "Adesso la geometria la approvi tu <b>prima</b>, sul 3D, dove correggere non costa niente.",
]))
story.append(Spacer(1, 8))
story.append(foto("crop_lavabo_volumi_2_mobile_chiuso.png", 78))
story.append(Paragraph("Esempio del passo 3: il mobile lavabo lavanderia ricostruito in 47 solidi, "
                       "tutti alle misure del tuo DWG", S["did"]))

# ============ PAGINA 2 ============
story.append(PageBreak())
story.append(fascia("PASSI 2-3 &mdash; DAL DISEGNO AI VOLUMI"))
story.append(Spacer(1, 7))
story.append(Paragraph("Le misure si leggono, non si stimano", S["fase"]))
story.append(Paragraph(
    "Le profondit&agrave; e gli spessori escono dalla <b>sezione</b>, le larghezze dal <b>prospetto</b>, "
    "la posizione di lavabo e rubinetteria dalla <b>pianta</b>. Il layer di ogni pezzo dice il materiale "
    "e i retini dicono quali contorni sono pieni: cos&igrave; niente viene inventato. "
    "Esempio, quello che ho letto dal mobile lavabo lavanderia:", S["corpo"]))
story.append(Spacer(1, 4))

mis = [
    ["Elemento", "Misura letta dal CAD", "Dove l'ho letta"],
    ["Mobile", "1173 L &times; 400 P &times; 670 H (piano finito)", "prospetto + sezione"],
    ["Nicchia a giorno (sx)", "luce 432, un ripiano a quota 329", "prospetto"],
    ["Vano con 2 ante (dx)", "luce 687, un ripiano a quota 329", "prospetto"],
    ["Ante", "357 &times; 488, spessore 18, da quota 92 a 580", "prospetto + sezione"],
    ["Gola di presa", "30 mm aperti sopra le ante, fondo a specchio", "sezione"],
    ["Zoccolo", "spessore 18 arretrato di 98, altezza 95, su 3 piedini", "sezione + prospetto"],
    ["LED", "2 canali incassati: sotto il fondo e sotto il piano", "sezione"],
    ["Lavabo Galassia MEG 11 PRO", "603 &times; 379, bordo a quota 920", "pianta + prospetto"],
    ["Parete attrezzata", "spessore 66, tubolari 80&times;50, finestra h 720", "sezione"],
]
dati = [[Paragraph(f"<b>{c}</b>" if i == 0 else c, S["cella"]) for c in r] for i, r in enumerate(mis)]
t = Table(dati, colWidths=[47 * mm, 78 * mm, 41 * mm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), BLU),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CHIARO]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cfcbc3")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
]))
story.append(t)

story.append(Paragraph("Il 3D che ti arriva", S["fase"]))
story.append(Paragraph(
    "Un file <b>DXF</b> da aprire e orbitare, pi&ugrave; uno script <b>.scr</b> che in AutoCAD te li ricrea "
    "come solidi BOX nativi: cos&igrave; li puoi sezionare e misurare con i tuoi comandi. "
    "E te lo mando anche <b>senza ante</b>, altrimenti non potresti controllare l'interno.", S["corpo"]))
story.append(Spacer(1, 3))
due = Table([[foto("crop_lavabo_volumi_3_senza_ante.png", 76),
              foto("crop_lavabo_volumi_4_carcassa.png", 66)]], colWidths=[80 * mm, 86 * mm])
due.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
story.append(due)
story.append(Paragraph("Senza ante: nicchia e vano interno con i ripiani &nbsp;&middot;&nbsp; "
                       "Sola carcassa: fianchi, divisorio, schienale, traversi", S["did"]))

# ============ PAGINA 3 ============
story.append(PageBreak())
story.append(fascia("PASSO 4 &mdash; IL COLLAUDO PRIMA DI DARTELO"))
story.append(Spacer(1, 7))
story.append(Paragraph("Due controlli automatici", S["fase"]))
story.append(Paragraph(
    "Prima che tu apra il file, un programma verifica che <b>nessun solido compenetri un altro</b> "
    "(due pannelli non possono occupare lo stesso spazio: se succede, il modello &egrave; sbagliato) "
    "e che ogni quota coincida col CAD.", S["corpo"]))
story.append(Spacer(1, 3))
story.append(riquadro([
    '<font face="Courier" size="8">=== COLLAUDO &mdash; 47 solidi ===<br/><br/>'
    '--- 1. COMPENETRAZIONI ---<br/>'
    '&nbsp;&nbsp;OK  nessuna compenetrazione: tutti i solidi sono disgiunti<br/><br/>'
    '--- 2. VERIFICA CONTRO IL CAD ---<br/>'
    '&nbsp;&nbsp;OK  profondit&agrave; mobile: atteso 400, modello 400.0<br/>'
    '&nbsp;&nbsp;OK  larghezza mobile: atteso 1173, modello 1173.0<br/>'
    '&nbsp;&nbsp;OK  piano finito a quota: atteso 670, modello 670.0<br/>'
    '&nbsp;&nbsp;OK  anta: base 92, cima 580<br/>'
    '&nbsp;&nbsp;OK  ripiani a quota: atteso 328.5, modello 328.5<br/>'
    '&nbsp;&nbsp;OK  lavabo, bordo alto: atteso 920, modello 920.0<br/><br/>'
    '&nbsp;&nbsp;-&gt; GOLA DI PRESA: da 580 a 610 = 30 mm di apertura</font>'
], "Il collaudo del mobile lavabo lavanderia (superato)"))

story.append(Paragraph("Cinque controllori con occhi diversi", S["fase"]))
story.append(Paragraph(
    "Poi il modello viene riletto da cinque controllori indipendenti, ognuno col suo compito: "
    "uno ricontrolla la sezione, uno il prospetto, uno la pianta, uno ragiona <b>da falegname</b> "
    "(sta in piedi? i ripiani appoggiano da entrambi i lati? il piano &egrave; sostenuto?), "
    "uno cerca cosa manca rispetto al disegno. Ogni errore segnalato passa poi a un sesto controllore "
    "che prova a <b>smentirlo</b>: arriva a te solo quello che regge alla verifica.", S["corpo"]))
story.append(Spacer(1, 4))
story.append(foto("crop_lavabo_volumi_5_fianco.png", 62))
story.append(Paragraph("Vista di fianco: profondit&agrave;, sbalzi e allineamenti in un colpo d'occhio", S["did"]))
story.append(Spacer(1, 2))
story.append(riquadro([
    "<b>Insieme al 3D ti scrivo sempre in chat i materiali che ho trovato nel file</b> "
    "(laminato CERA, laminato OPACO, specchio, vetro, grigio arredo...), segnalando quelli da confermare. "
    "Se un colore &egrave; cambiato o me lo sono perso, me lo dici al volo prima che parta il render.",
]))

# ============ PAGINA 4 ============
story.append(PageBreak())
story.append(fascia("PASSI 5-7 &mdash; RENDER, COLLAUDO E CONSEGNA"))
story.append(Spacer(1, 7))
story.append(Paragraph("Le regole imparate lavorando con Manus", S["fase"]))
story.append(Paragraph(
    "Sono lezioni pagate coi crediti dei mobili gi&agrave; chiusi: cucina (11 giri), lavanderia (8), "
    "mobile ingresso, portale, libreria ufficio, muretti bagni.", S["corpo"]))
story.append(Spacer(1, 3))
regole = [
    ("Massimo 3-4 correzioni per giro",
     "Con otto insieme entrano tutte, ma qualcos'altro peggiora."),
    ("Sempre la lista di cosa NON cambiare",
     "Ogni rigenerazione &egrave; un lancio di dadi: una volta ha aggiunto un'anta mentre "
     "&quot;teneva tutto identico&quot;."),
    ("Le proporzioni non si chiedono a Manus",
     "Quattro modi diversi di chiederlo, sempre lo stesso errore. Si correggono dopo, "
     "con la matematica: costo zero."),
    ("Zoom prima di promuovere",
     "Zoccoli, piedini, targhette e cerniere non si giudicano dall'immagine intera."),
    ("Ogni mobile fa storia a s&eacute;",
     "Mai importare lo zoccolo della cucina sulla lavanderia: si guarda sempre il SUO disegno."),
    ("L'occhio del falegname vince sul collaudo",
     "&Egrave; gi&agrave; successo: una consegna promossa da me e bocciata da te. Da l&igrave; il collaudo &egrave; cambiato."),
]
dati = [[Paragraph(f"<b>{a}</b>", S["corpo"]), Paragraph(b, S["corpo"])] for a, b in regole]
t = Table(dati, colWidths=[60 * mm, 106 * mm])
t.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#dedad3")),
    ("BACKGROUND", (0, 0), (0, -1), CHIARO),
    ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
]))
story.append(t)

story.append(Paragraph("Dove finisce tutto", S["fase"]))
story.append(Paragraph(
    "Ogni mobile ha la sua cartella su Dropbox in <b>/Matteo/RENDER_MANUS/</b>: tavole, tutti i giri di render, "
    "la consegna finale e la scheda di collaudo aggiornata giro per giro. Il metodo completo &egrave; scritto in "
    "<b>PROTOCOLLO_RENDER_MANUS.md</b>, salvato sia su Dropbox sia sul repository GitHub, cos&igrave; non si perde "
    "pi&ugrave;: qualsiasi sessione futura riparte da l&igrave; senza rimettere in piedi il metodo da capo.", S["corpo"]))
story.append(Spacer(1, 7))
story.append(riquadro([
    "<b>Consegnati con collaudo superato:</b> cucina, lavanderia, mobile ingresso, parete porta living, "
    "portale ingresso, divisorio living/master, muretti bagni Geberit, libreria ufficio.",
    "<b>Da chiudere:</b> parete letto e divano pensile (hanno render ma non la scheda di collaudo).",
    "<b>In corso:</b> mobile lavabo lavanderia &mdash; 3D dei volumi al tuo controllo, zero crediti spesi finora.",
], "Stato della commessa 26-A011"))


def piede(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GRIGIO)
    canvas.drawString(22 * mm, 12 * mm, "Automazione DWG - Render  ·  commessa 26-A011  ·  12/08/2026")
    canvas.drawRightString(W - 22 * mm, 12 * mm, f"pag. {doc.page} di 4")
    canvas.setStrokeColor(colors.HexColor("#dedad3"))
    canvas.line(22 * mm, 15 * mm, W - 22 * mm, 15 * mm)
    canvas.restoreState()


doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm,
                      topMargin=17 * mm, bottomMargin=19 * mm,
                      title="Automazione DWG - Render", author="Claude per Matteo Miconi")
doc.addPageTemplates([PageTemplate(id="base", frames=[
    Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="n")], onPage=piede)])
doc.build(story)
print("scritto", OUT)
