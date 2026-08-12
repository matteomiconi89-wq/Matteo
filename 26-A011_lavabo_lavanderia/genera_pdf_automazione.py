#!/usr/bin/env python3
"""PDF di una pagina: l'automazione DWG -> render in 7 passi."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle)
from PIL import Image as PILImage

W, H = A4
SCR = "/tmp/claude-0/-home-user-Matteo/9d8a08b3-647f-5483-95d8-409ee5c210e1/scratchpad"
PDF = f"{SCR}/pdf"
OUT = f"{PDF}/AUTOMAZIONE_DWG_RENDER.pdf"

BLU = colors.HexColor("#1f3a5f")
ORO = colors.HexColor("#a2701c")
GRIGIO = colors.HexColor("#555555")
CHIARO = colors.HexColor("#f1f0ed")

ss = getSampleStyleSheet()
T = ParagraphStyle("t", parent=ss["Title"], fontSize=19, leading=22, textColor=BLU, spaceAfter=1)
ST = ParagraphStyle("st", parent=ss["Normal"], fontSize=9.5, leading=12, textColor=GRIGIO,
                    alignment=TA_CENTER, spaceAfter=10)
P = ParagraphStyle("p", parent=ss["Normal"], fontSize=9.3, leading=12.2)
D = ParagraphStyle("d", parent=ss["Normal"], fontSize=7.6, leading=9.5, textColor=GRIGIO,
                   alignment=TA_CENTER, spaceBefore=3)


def foto(nome, altezza_mm):
    w0, h0 = PILImage.open(f"{PDF}/{nome}").size
    h = altezza_mm * mm
    return Image(f"{PDF}/{nome}", width=h * w0 / h0, height=h)


story = [
    Paragraph("Automazione DWG &rarr; Render", T),
    Paragraph("Come lavoriamo io e Manus sui tuoi disegni &middot; 26-A011 &middot; 12/08/2026", ST),
]

passi = [
    ("1", "Mi mandi il DWG", "Nient'altro: le misure le prendo io dal file.", True),
    ("2", "Leggo le misure vere dal CAD", "Coordinate reali in millimetri da sezione, prospetto e pianta. "
     "Mai stime a occhio.", False),
    ("3", "Costruisco il 3D dei volumi", "Ogni pannello un solido vero, alle misure esatte. "
     "Niente ferramenta, niente forature.", False),
    ("4", "TU LO APPROVI IN AUTOCAD", "Ti mando il DXF 3D + lo script che ricrea i solidi. "
     "Correggere qui costa ZERO crediti.", True),
    ("5", "Briefo Manus", "Scheda di collaudo, tavole, 3D approvato. Max 3-4 correzioni per giro, "
     "sempre con la lista di cosa non cambiare.", False),
    ("6", "Collaudo il render", "Righello sui pixel, zoom sulle zone critiche. "
     "Le proporzioni le sistemo io dopo, gratis.", False),
    ("7", "Ti consegno solo ci&ograve; che passa", "Un render bocciato non arriva sulla tua scrivania.", True),
]
righe = []
for n, tit, desc, tuo in passi:
    c = ORO if tuo else BLU
    righe.append([
        Paragraph(f'<font color="{c.hexval()}" size="13"><b>{n}</b></font>', P),
        Paragraph(f'<b><font color="{c.hexval()}">{tit}</font></b> &nbsp;{desc}', P),
    ])
t = Table(righe, colWidths=[8 * mm, 158 * mm])
t.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#dedad3")),
    ("LEFTPADDING", (0, 0), (0, -1), 2),
]))
story.append(t)
story.append(Spacer(1, 8))

nota = Table([[Paragraph(
    "<b>La novit&agrave; &egrave; il passo 4.</b> Prima si andava dritti a Manus e gli errori di geometria si "
    "scoprivano dopo aver speso crediti (cucina: 11 giri, lavanderia: 8). Ora la geometria la approvi tu "
    "<b>prima</b>, sul 3D, dove correggere non costa niente. In arancione i passi dove decidi tu.", P)]],
    colWidths=[166 * mm])
nota.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), CHIARO),
    ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#cfcbc3")),
    ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
story.append(nota)
story.append(Spacer(1, 9))

due = Table([[foto("crop_lavabo_volumi_2_mobile_chiuso.png", 62),
              foto("crop_lavabo_volumi_3_senza_ante.png", 62)]], colWidths=[83 * mm, 83 * mm])
due.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
story.append(due)
story.append(Paragraph("Esempio del passo 3-4: mobile lavabo lavanderia, 47 solidi alle misure del tuo DWG. "
                       "Te lo mando anche senza ante, per controllare ripiani e vani interni.", D))

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm,
                        topMargin=18 * mm, bottomMargin=15 * mm,
                        title="Automazione DWG - Render", author="Claude per Matteo Miconi")
doc.build(story)
print("scritto", OUT)
