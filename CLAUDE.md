# Istruzioni permanenti per Claude — repo di Matteo (falegnameria/arredo)

Matteo e' un falegname/arredatore. Lavora in AutoCAD (e riceve/consegna DWG),
i fornitori usano anche CATIA/SolidWorks. Non e' un programmatore: rispondere
in italiano, tempi stimati dichiarati in chat ("~20 min, ti scrivo io"),
niente gergo inutile.

## FAI_3D — cosa fare quando Matteo "apre e basta"

Se la sessione parte con un messaggio che contiene **FAI_3D**, oppure ci sono
file nuovi in `CONSEGNA_2D/`, oppure Matteo allega una tavola 2D
(pianta/prospetto/sezione, DWG o DXF): **sai gia' cosa fare, non chiedere
cosa vuole.** Il flusso e' questo, dettagli in `STRUMENTI_3D/README_3D.md`:

1. Ambiente: `bash STRUMENTI_3D/setup_ambiente.sh` (in remoto; su PC Windows
   le librerie le ha gia' messe `SETUP_PC.bat`). Aggiungere `--libredwg` solo
   se c'e' un DWG da leggere e non c'e' ODAFileConverter.
2. Per ogni tavola 2D: `python3 STRUMENTI_3D/estrai_2d.py tavola uscita/nome`
   → report viste/quote/rettangoli + bozza volumi.
3. **Fase A (il tuo lavoro vero)**: dalla bozza e dal report costruire il
   `volumi.json` fedele — quote lette dalle DIMENSION, pezzi battezzati,
   spessori giusti, materiali dai layer (il layer E' la specifica del
   materiale; MAI inventare materiali non scritti nel disegno).
4. `python3 STRUMENTI_3D/volumi_3d.py volumi.json uscita/nome` → STP con
   materiali dentro, DXF 3D, SCR, distinta CSV, viste PNG. I collaudi
   automatici devono passare tutti.
5. **SQUADRA DI AGENTI (regola fissa dal 03/09/2026, richiesta di Matteo)**:
   per ogni mobile usare TUTTI gli agenti disponibili, non lavorare da soli.
   Il giro minimo, in parallelo (tool Workflow o Agent):
   - inventario per famiglia di pezzi (ante/frontali, vetri+telai, zoccoli/
     piedini, ripiani e interni, LED/elettrico) con coordinate esatte dal DXF;
   - forense ORIENTAMENTO: trasformazioni degli INSERT (rotazioni, scale
     negative, estrusione -Z), testi capovolti, direzione di vista delle
     sezioni — il mobile specchiato e' gia' successo (mobile ingresso);
   - verifica incrociata inventario vs volumi.json;
   - **AGENTE FALEGNAME**: rilegge il volumi.json finito con l'occhio di chi
     lo deve costruire — battute e giochi delle ante, sensi di apertura vs
     cerniere, spessori e sormonti realistici, zoccoli/piedini sensati,
     pezzi doppi o compenetrati, cose che "in officina non stanno in piedi".
     Le sue obiezioni si risolvono PRIMA del checkpoint di Matteo.
6. **CHECKPOINT DI MATTEO (regola fissa)**: mostrare le PNG + il report
   materiali con le voci da confermare e aspettare il suo OK prima di
   considerare consegnato. Un errore corretto qui costa zero.
7. Consegna in `USCITA_3D/<nome_mobile>/` (su PC) o inviando i file in chat
   (in remoto). Il DWG vero si fa in AutoCAD (IMPORT dello .stp o SCRIPT
   dello .scr, poi SAVEAS); se c'e' ODAFileConverter nel PATH esce da solo.

## Regole sempre valide

- Millimetri esatti, assi X=larghezza Y=profondita' Z=altezza.
- I codici articolo si leggono dai MLEADER del DXF, mai dalle immagini.
- Il protocollo render completo (Manus, collaudi, post) e' in
  `PROTOCOLLO_RENDER_MANUS.md`; la giurisprudenza sono le SPEC dei mobili
  chiusi (`26-A011_lavabo_lavanderia/SPEC_COLLAUDO.md` in repo, il resto
  su Dropbox `/STEFANO/Matteo/RENDER_MANUS/`).
- Ogni mobile fa storia a se': si guarda il SUO disegno.
