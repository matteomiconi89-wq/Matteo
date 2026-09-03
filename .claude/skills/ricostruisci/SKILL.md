---
name: ricostruisci
description: >
  Dal DWG 2D dell'allestimento 26-A011 (pianta con arredo assemblato + prospetti)
  genera in automatico TUTTI gli STEP dei mobili, precisi al millimetro, l'assieme
  unico e la geometria per il viewer 3D. Una sola parola: /ricostruisci.
  Usa questa skill ogni volta che l'utente chiede di rigenerare/aggiornare gli STEP
  o il modello 3D dei mobili partendo dai disegni 2D (DWG/DXF).
---

# Ricostruttore 2D → STEP (26-A011 "B&B CAR")

Obiettivo: **da una parola, tutti gli STEP precisi al mm** dei mobili del truck,
ricostruiti dai DWG 2D (pianta + prospetti) — non da mesh approssimate.

## Cosa produce
- `26-A011_allestimento/cad/step/<mobile>.step` — **uno STEP solido per ogni mobile** (21 pezzi).
- `26-A011_allestimento/cad/26A011_arredo_completo.step` — **assieme unico** di tutto l'arredo.
- `26-A011_allestimento/pipeline/arredo_geometry_mobili.json` — mesh per il viewer 3D.

I pezzi: cucina (7 moduli), armadi (master+doppia), letti (master + contenitore doppia),
divano+pensile, tavolo, libreria ufficio, mobile ingresso, i 2 mobili-lavabo bagno,
muri e sanitari dei 2 bagni, colonna lavatrice, muretti bagni, e le pareti/divisori
(plo ingresso, divisori living/master e living/doppia, parete lavanderia).

## Come eseguirla (una parola)

```bash
cd 26-A011_allestimento/pipeline
./genera_step.sh                     # usa ../26A011_PIANTA_GENERALE.dwg (nel repo)
```

Con i disegni aggiornati dell'utente (es. da Dropbox), passa i file espliciti:

```bash
./genera_step.sh /percorso/PIANTA.dwg /percorso/PROGETTO_prospetti.dwg ../cad
```

Accetta sia **.dwg** (convertito con LibreDWG `dwg2dxf`) sia **.dxf** (nessuna
dipendenza esterna). Se il PROGETTO (prospetti) non è fornito, la **cucina** viene
riusata dall'ultimo `cad/step/cucina.step` così l'output resta completo.

## Passi operativi per l'agente

1. **Dipendenze**: `pip install cadquery shapely ezdxf` (idempotente; lo fa già lo script).
2. **Sorgente**: se l'utente ha un DWG nuovo (di solito in Dropbox in
   `/STEFANO/26-A011 B&B CAR.../`), scaricalo prima e passalo come argomento.
   Altrimenti usa il DWG di pianta versionato nel repo.
3. **DWG→DXF**: serve `dwg2dxf` (LibreDWG). Se manca:
   `apt-get install -y libredwg-tools` oppure fai esportare/usare un `.dxf`.
4. **Esegui** `./genera_step.sh …` e **verifica**: ogni `.step` deve reimportare come
   solido con volume > 0. Controllo rapido:
   ```python
   from cadquery import importers, glob
   for f in glob.glob('../cad/step/*.step'):
       w=importers.importStep(f); v=sum(s.Volume() for s in w.solids().vals())
       print(f, len(w.solids().vals()), round(v/1e9,3),'m3')
   ```
5. **Viewer**: per aggiornare l'artifact 3D, rigenera l'HTML con
   `scratchpad/build_viewer.py` (mobili da `arredo_geometry_mobili.json`, guscio da
   `arredo_geometry_solidi.json`) e pubblicalo.
6. **Commit** su branch `claude/truck-render-measurements-7977e1`.

## Note tecniche (sistema di riferimento)
- Coord. **trailer** (mm): X = lunghezza (0 = muso), Y = larghezza (0 = lato ingresso),
  Z = altezza da terra; pavimento `PAV = 1395`.
- Pianta → trailer: `X = plan_X − 2293`, `Y = plan_Y − 3117`.
- `insert()` sceglie automaticamente l'istanza **dentro** il cassone e scarta le copie
  di dettaglio disegnate a lato (es. il letto master, disegnato anche specchiato).
- Layer DWG usati: `F_MULTI laminato OPACO` = ante, `…CERA` = carcassa,
  `F_CASSETTI` = cassetti, `F_SANITARI` = WC/bidet/doccia, `F_BETACRYL o CORIAN` = top lavabo,
  `F_VETRO` = vetri doccia, `F_STRIP-LED` = ignorato.

Il motore è `pipeline/ricostruisci.py` (ampiamente commentato): per aggiungere un
mobile, aggiungi un `put('<chiave>', <builder>(...))` nella sezione "costruzione pezzi".
