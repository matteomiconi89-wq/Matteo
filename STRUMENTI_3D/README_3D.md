# STRUMENTI 3D — dal 2D (pianta/prospetto/sezione) al 3D in STP + DXF/DWG

> Il "modo veloce" chiesto da Matteo il 03/09/2026. Due comandi e un file
> intermedio (`volumi.json`) che e' lo stesso gia' usato per la commessa
> 26-A011: quello che prima era solo DXF+SCR ora esce anche come **STEP
> con solidi veri**, il formato che apre CATIA.

## Il flusso in una riga

**Tavola 2D → `estrai_2d.py` (viste, quote, rettangoli, bozza) → Claude rifinisce
`volumi.json` → checkpoint di Matteo → `volumi_3d.py` → `nome.stp` + `nome_3d.dxf`
+ `nome.scr` (+ viste PNG di controllo, tutto collaudato in automatico).**

## Sul PC di Matteo: doppio click e basta

Nella radice del repo ci sono due `.bat` per Windows:

- **`SETUP_PC.bat`** — da lanciare UNA volta: mette le librerie Python, dice
  come installare Claude Code (una riga in PowerShell, login col proprio
  account Claude) e, facoltativo, l'ODA File Converter per i DWG.
- **`FAI_3D.bat`** — l'uso quotidiano: doppio click, oppure **trascinaci
  sopra i DWG/DXF**. I file finiscono in `CONSEGNA_2D/`, si apre Claude Code
  che sa gia' cosa fare (le istruzioni permanenti sono in `CLAUDE.md`:
  analisi, volumi, checkpoint, consegna in `USCITA_3D/`), e alla chiusura
  si apre la cartella dei risultati.

Lo stesso automatismo vale anche da telefono/browser (claude.ai/code, oppure
una chat con questo repo): qualsiasi sessione nuova legge `CLAUDE.md`, quindi
basta allegare la tavola e scrivere "FAI_3D" — non serve rispiegare niente.

## Comandi

```bash
# 0. una volta per sessione (container nuovo):
bash STRUMENTI_3D/setup_ambiente.sh              # ~2 min
bash STRUMENTI_3D/setup_ambiente.sh --libredwg   # se il 2D arriva come DWG

# 1. analisi della tavola 2D (accetta DXF, e DWG se c'e' LibreDWG):
python3 STRUMENTI_3D/estrai_2d.py TAVOLA.dxf uscita/nome
#    -> nome_report.txt   viste trovate, quote DIMENSION, rettangoli, testi
#    -> nome_bozza.json   scheletro di volumi.json (ingombro + prismi pianta)
#    -> nome_viste.png    tavola con le viste riquadrate e nominate

# 2. (Fase A del protocollo) dalla bozza si scrive il volumi.json vero:
#    quote lette dal report, pezzi battezzati, spessori giusti.
#    E' il lavoro di Claude in sessione; Matteo approva il checkpoint 3D.

# 3. generazione 3D, tutto in un colpo:
python3 STRUMENTI_3D/volumi_3d.py volumi.json uscita/nome
#    -> nome.stp          STEP AP214, SOLIDI VERI (CATIA, SolidWorks, NX, AutoCAD IMPORT)
#                         con i MATERIALI scritti dentro (vedi sotto)
#    -> nome_distinta.csv distinta pezzi: materiale, misure, volume (per Excel)
#    -> nome_3d.dxf       DXF 3D mesh (anteprima diretta in AutoCAD)
#    -> nome.scr          script AutoCAD: BOX solidi nativi
#    -> nome_asso/_fronte/_fianco.png   viste di controllo
```

## Materiali dai layer, dentro lo STEP

Nei DWG di Matteo **il layer e' la specifica del materiale** ("Tamburato
Laminato NERO Opaco"): la pipeline lo sfrutta. Ogni pezzo riceve il suo
materiale cosi', in ordine di precedenza:

1. campo `"materiale"` sul singolo box del `volumi.json`;
2. mappa `"materiali"` a livello di file, per famiglie di pezzi senza toccare
   le righe approvate: `{"CARC_": "Laminato CERA", "ANTA_": "Laminato OPACO"}`
   (vince il prefisso piu' lungo);
3. il **layer di provenienza** (quello che `estrai_2d.py` porta dietro in
   automatico dal 2D).

Nel file STEP il materiale viaggia come proprieta' standard del pezzo
(`PROPERTY_DEFINITION 'material property' -> DESCRIPTIVE_REPRESENTATION_ITEM`):
CATIA e SolidWorks la mostrano nelle proprieta', e il collaudo automatico
verifica che ogni materiale sia davvero finito nel file. La stessa
informazione esce anche in `nome_distinta.csv` (pezzo; materiale; L; P; H;
volume in dm3), pronta per preventivi e ordini.

## Come si arriva ai tre formati chiesti

| Formato | Come |
|---|---|
| **STP** | esce direttamente: `nome.stp`, STEP AP214 con un solido per pezzo, nomi dei pezzi e layer nell'albero, colori. Collaudato in automatico (rilettura + conteggio solidi + ingombro). |
| **DWG 3D** | in AutoCAD, 30 secondi, una delle due strade: **(a)** `IMPORT` → scegli `nome.stp` → entrano i solidi veri → `SAVEAS` DWG; **(b)** `SCRIPT` → `nome.scr` → i pezzi si ricreano come BOX nativi → `SAVEAS` DWG. In alternativa senza AutoCAD: installare l'**ODA File Converter** (gratuito, opendesign.com) — se `volumi_3d.py` lo trova nel PATH scrive lui il `nome.dwg` direttamente. |
| **CATIA** | **si usa lo stesso `nome.stp`**: CATIA lo apre nativamente (File → Open), schema AP214 "automotive_design" che e' proprio il suo dialetto preferito. Dentro CATIA si puo' poi salvare come `.CATPart`/`.CATProduct`. Il file `.CATPart` nativo NON si puo' generare da fuori senza licenze proprietarie (Dassault/Datakit): non e' un limite nostro, e' cosi' per tutti — e lo STEP e' lo standard con cui i fornitori si scambiano i modelli proprio per questo. |

### Perche' il DWG non esce "gia' pronto" da qui

L'unico convertitore libero (LibreDWG `dxf2dwg`) oggi scrive DWG rotti: collaudato
il 03/09/2026, 0 entita' rilette su 74. Lo script lo tenta comunque ma con un
**collaudo severo di round-trip** (riconversione e conteggio entita'): se il DWG
non e' perfetto lo scarta e lo dice. Quando ci sara' un convertitore affidabile
nel PATH (ODA File Converter) il DWG uscira' da solo, gia' collaudato.

## Collaudi integrati (in stile protocollo)

- `volumi.json` validato al caricamento (quote mancanti, dimensioni nulle/negative, nomi doppi).
- STEP **riletto** dopo la scrittura: numero solidi e ingombro devono tornare
  esatti (tolleranza 0,5 mm), altrimenti exit code ≠ 0.
- DWG consegnato solo se il round-trip restituisce tutte le entita'.
- Viste PNG (assonometria, fronte, fianco) per il colpo d'occhio prima del
  checkpoint di Matteo in AutoCAD.

## Cosa resta manuale (ed e' giusto cosi')

`estrai_2d.py` trova viste, quote e rettangoli, e propone una bozza; ma la
ricostruzione FEDELE (quale rettangolo e' un fianco, quale un'anta, gli spessori,
le sormonte) resta la Fase A del protocollo: la fa Claude leggendo il disegno,
e **il checkpoint 3D di Matteo in AutoCAD resta la regola fissa** prima di
qualsiasi uso a valle (render Manus, CATIA, fornitori). Un errore corretto al
checkpoint costa zero; dopo, costa.

## Esempio pronto

In `esempio/` c'e' una tavola di prova (mobile 600×400×720 con pianta,
prospetto e sezione quotate) con tutti i file che escono dai due comandi,
compreso lo `mobiletto.stp` da provare in CATIA.

## Riferimento reale

Il mobile lavabo 26-A011 (74 solidi, rev.04 approvata) rigenerato con questa
pipeline: `26-A011_lavabo_lavanderia/lavabo_volumi.stp` — collaudo 74/74 solidi,
ingombro 1173 × 474 × 2215 mm esatto, 12 materiali dentro lo STEP (quelli
della SPEC: Laminato CERA, Laminato OPACO, Specchio; il resto eredita il
layer, senza inventare nulla) + `lavabo_volumi_distinta.csv`.
