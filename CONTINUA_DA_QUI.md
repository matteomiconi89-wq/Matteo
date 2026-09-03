# CONTINUA DA QUI — passaggio consegne (progetto Matteo)

> COME USARLO: apri una NUOVA conversazione di Claude Code dentro il progetto
> "Matteo" e **incolla tutto questo file come primo messaggio** (oppure, se la
> nuova sessione vede questo disco, scrivi: «leggi
> C:\Users\User\Desktop\CONTINUA_DA_QUI_matteo.md e continua da lì»).
> Data passaggio: 03/09/2026.

## Chi sono
Matteo, falegname/progettista (AutoCAD 3D, AutoLISP, Python, Blum). Parlo
italiano. Suite di tool "FILIERA UN CLIC": da STEP/DWG 3D → DXF, confronto/
deduplica, sezionatura, programmi macchina TLF (Masterwood) e MPRX (Homag),
libretti PDF, SCHEDA BASE, ordini fornitori, riepilogo costi, e ora le VISTE
per il cliente. Exe: FILIERA_GENERICO e FILIERA_21032 (sorgenti in
`C:\Users\User\Desktop\CLAUDE\StepDefinitivi`).

## Cosa abbiamo fatto in questa conversazione (tutto FATTO e in produzione)

### 1) RIEPILOGO COSTI per mobile (foglio nel _COMPLETO)
- `Desktop\CLAUDE\StepDefinitivi\riepilogo_costi.py` → `genera_riepilogo_costi`.
- Categorie: pannellame, ferramenta, bordi, massello, LACCATURA+CARTEGGIATURA,
  illuminazione + manodopera (€/h editabile, default 45).
- ILLUMINAZIONE per-mobile: letta dalla sezione ILLUMINAZIONE del GENERALE
  (col A mobile, col G €TOT), abbinata al mobile di distinta per CODICE-LETTERA
  (es. "P-PARETE"→MOBILE_P, "L2 -…"→PANNELLATURA_L2). Catch-all se non abbina.
- LACCATURA+CARTEGGIATURA (metodo Guido, studiato sul suo file): colonne
  distinta AL..AX (38..50). MQ=(F*G*AK+(F+G)*H*2)/1e6*D (sviluppo bordi UNA
  volta anche su 2 lati). ML=MAX(F/1000,1)*D (min 1 m). CART.RA AW(49)=Σml,
  AX(50)=Σmq. I PREZZI si leggono dalla sezione VERNICIATURA del GENERALE
  (descr = header riga3 della colonna); default in LACC_DEFAULT se mancano.
- Validato su 25-A019 GUIDO: pann 6635, ferr 178, bordi 952, massello 61,
  lacc+cart 4302, illum 2026, manod 320h×45=14.422 → TOTALE 28.577 €.

### 2) M17: minimo ML = 250 mm
- Aggiunto nello STAMPO `Dropbox\STEFANO\FORNITORI\SCHEDA_BASE_MODELLO_FILIERA.xlsm`,
  colonna AV (M17-ML): `MAX($F/1000,1)` → `MAX($F/1000,0.25)` (334 righe, via
  Excel COM). Solo M17; le altre finiture restano min 1 m. Backup:
  `..._BACKUP_pre_m17_250.xlsm`. NON ancora fatti i minimi mq 0,2 (da valutare).

### 3) ORDINI FORNITORI PDF + tutto già integrato
- `ordini_fornitori_pdf.py` (PDF ordine per fornitore, cartella ORDINI, rif.
  commessa) e il riepilogo costi girano in coda a `genera_ordini_fornitori`
  dentro `confronto_e_sezionatura` (solo MODO_GENERICO).

### 4) VISTE CLIENTE dal 3D  ← novità principale
- `Desktop\CLAUDE\Viste\viste_cliente.py` → `genera_viste_cliente(src_dwg,
  out_dir, commessa, mobile, boxes=None, fai_dwg=True)`.
- Tavola A3: PIANTA, PROSPETTO, SEZIONE A-A (verticale, taglio in Y),
  SEZIONE B-B (verticale, taglio in X). Linee taglio A/B sulla pianta.
- Quote: ingombri + catene posizione + VANI UTILI netti dentro le sezioni +
  SPESSORI (sp.18/25/50). Materiali a colore + legenda + cartiglio.
- PDF = tavola in scala (stampa). DWG = **scala reale 1:1** con **quote
  AutoCAD vere associative** (rendi_dxf moltiplica per k=scala; niente testo
  fisso). FIX IMPORTANTE: ezdxf setup=True mette DIMLFAC=100 → mostrava 24700
  invece di 247; risolto con dimlfac=1 (override + dimstyle + header).
- Pannelli trattati come scatole (bbox) via `boxes_da_dwg_light` (AutoCAD COM,
  sola lettura; nome+materiale dal layer "NOME -- MATERIALE"). Assi: X=largh,
  Y=prof, Z=altezza.
- INTEGRATO in FILIERA_GENERICO: `step_dxf_definitivi.py` →
  `viste_cliente_pdf(base, log)` (cicla i mobili, output in sottocartella
  VISTE), chiamato in MODO_GENERICO. Spec `step_dxf_generico.spec`:
  pathex+=Viste, hiddenimports+=viste_cliente, collect_all('ezdxf').
- Exe ricompilato: **FILIERA_GENERICO.exe md5 650ae945e0176bdc38b2b513ed217f4b**
  (dist Desktop + Dropbox\STEFANO\Matteo\CLAUDE\Definitivi\StepDXFDefinitivi).
- Validato sul 25-A018 Mobile TV: 32 pannelli, 2 materiali, scala 1:15, DWG con
  quote vere (1580/915/267/247…).

### 5) Git
- Creato repo locale in `Desktop\CLAUDE` (.gitignore: SOLO codice .py/.spec,
  niente dati cliente). Pushato su GitHub Matteo come branch
  **`claude/filiera-viste-costi-09f3dc`** (commit 23647e1, 105 file).

## COSA RESTA DA FARE (riprendi da qui)
1. **VIDEO v2 esplicativo di tutta la FILIERA UN CLIC** (ERA IL PROSSIMO PASSO).
   - Motore pronto in `Desktop\CLAUDE\business_reel` (edge-tts voce Diego +
     Pillow + ffmpeg via imageio). Girato reale esistente in
     `Desktop\FILIERA_UN_CLIC` (girato_demo.mp4, girato_demo2.mp4,
     girato_woodwop.mp4, s12_1/2/3.mp4).
   - Piano concordato: narrazione NUOVA e completa (tutta la filiera
     aggiornata) + frame REALI dei nuovi output (tavola viste, riepilogo costi,
     ordini) + spezzoni di processo riusati dal girato; landscape 1920×1080.
   - Il girato live delle app che girano davvero va rifatto in una sessione
     dedicata (qui il pilotaggio AutoCAD via COM è risultato instabile).
2. Facoltativo: minimi mq 0,2 laccatura (M17 e laccature/tinte) nello stampo.
3. Facoltativo: rifinire i leader degli spessori nelle viste (ora un po' lunghi).

## VINCOLI OPERATIVI (rispettare sempre)
- MAI killare/riavviare acad.exe; MAI salvare/modificare i DWG originali (aprire
  in sola lettura, Close(False)).
- SCHEDA BASE: editare via Excel COM (preserva formule/dropdown/VBA). Lo STAMPO
  condiviso è `Dropbox\STEFANO\FORNITORI\SCHEDA_BASE_MODELLO_FILIERA.xlsm`.
- Il 21032 (FILIERA_21032) va lasciato com'è; le novità solo su GENERICO.
- Verificare md5 su tutte le copie exe (Desktop dist + Dropbox).
- Trappola: `genera_riepilogo_costi` carica SENZA data_only (il _COMPLETO ha già
  i valori cotti). Per testare su una scheda "viva" fare prima il bake
  (load data_only=True → save).
