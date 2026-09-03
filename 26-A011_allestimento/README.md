# ALLESTIMENTO 26-A011 "B&B CAR" — dal DWG 2D a tutti gli STEP, al millimetro

Ricostruzione 3D dell'arredo del truck espandibile **26-A011** (rif. DINO CHIESA):
da una sola parola, dal DWG 2D (pianta + prospetti) vengono generati **tutti gli STEP
dei mobili, precisi al mm**, l'assieme unico e il modello 3D interattivo.

**Viewer interattivo:** https://claude.ai/code/artifact/bda329f6-8860-4e4d-83f5-a32de719057b

## Una sola parola

```bash
cd 26-A011_allestimento/pipeline
./genera_step.sh                 # usa ../26A011_PIANTA_GENERALE.dwg (nel repo)
```

oppure con i disegni aggiornati (anche direttamente in `.dwg`):

```bash
./genera_step.sh /path/PIANTA.dwg /path/PROGETTO_prospetti.dwg ../cad
```

In sessione Claude Code è disponibile anche come skill: **`/ricostruisci`**.

Produce:
- `cad/step/<mobile>.step` — **uno STEP solido per ogni mobile** (21 pezzi);
- `cad/26A011_arredo_completo.step` — **assieme unico** (~20 m³ di arredo);
- `pipeline/arredo_geometry_mobili.json` — mesh per il viewer 3D.

Ogni STEP reimporta come solido valido (B-rep OpenCASCADE), quindi in AutoCAD/Inventor/
SolidWorks arriva come **corpo solido**, non come mesh.

## I 21 mobili ricostruiti

| Categoria | Pezzi |
|---|---|
| **Camere** | letto matrimoniale master (base+materasso+testata), armadio master, letto contenitore doppia, armadio doppia |
| **Living** | divano+pensile, tavolo, libreria-parete ufficio, mobile ingresso-living |
| **Cucina** | cucina 7 moduli (frigo, forni, lavello, lavastoviglie, cassettiera, cottura, dispensa) + pensile + top, colonna lavatrice |
| **Bagni** | muri + sanitari (doccia, WC, bidet) + mobile lavabo, per bagno anteriore e posteriore; muretti |
| **Pareti/divisori** | P.lo ingresso, divisorio living/master, divisorio living/doppia, parete/porta lavanderia |

Larghezze cucina validate sulle misure di collaudo (frigo 610, forni 620, lavello 600,
lavastoviglie 598, cassettiera 554, cottura 600, dispensa 300 mm).

## Come funziona (`pipeline/ricostruisci.py`)

Motore unico che legge il DWG (via DXF) e costruisce i solidi con **cadquery** (OpenCASCADE):

- **Mobili con ante/cassetti** (cucina, lavabi): carcassa 18 mm + fronti estratti dai
  prospetti / dai layer della pianta, per spessori e altezze reali.
- **Armadi**: fianchi / ante / schienali dai pannelli sottili della pianta, estrusi a tutta altezza.
- **Pareti e divisori**: estrusione dei footprint dei blocchi, allo spessore reale del disegno.
- **Bagni**: muri dal vano stanza, piatto+vetri doccia, WC e bidet nelle posizioni del layer `F_SANITARI`.
- **Letti**: zoccolo contenitore + materasso + testata.

`insert()` sceglie sempre l'istanza del blocco **dentro** il cassone, scartando le copie
di dettaglio disegnate a lato (es. il letto master, presente anche specchiato).

### Sistema di riferimento
`trailer_X = plan_X − 2293`, `trailer_Y = plan_Y − 3117` (scala 1:1). Trailer: X=lunghezza
(0 = muso), Y=larghezza (0 = lato ingresso), Z=altezza da terra; pavimento finito `PAV = 1395`.

### Layer DWG usati
`F_MULTI laminato OPACO` = ante · `…CERA` = carcassa · `F_CASSETTI` = cassetti ·
`F_SANITARI` = WC/bidet/doccia · `F_BETACRYL o CORIAN` = top lavabo · `F_VETRO` = vetri ·
`F_STRIP-LED` = ignorato.

## File

- `pipeline/ricostruisci.py` — il ricostruttore 2D→STEP (motore).
- `pipeline/genera_step.sh` — wrapper "una parola" (DWG→DXF→STEP, installa le dipendenze).
- `cad/step/*.step` — i 21 STEP dei mobili; `cad/26A011_arredo_completo.step` — l'assieme.
- `arredo_interattivo.html` — viewer 3D (Three.js): guscio scocca + 21 mobili con toggle,
  quote, categorie, viste preimpostate, griglia 0,5 m, persona 1,75 m.
- `arredo_geometry.json` — geometria combinata (guscio + mobili, coord. trailer).
- `build_viewer.py` + `viewer_template.html` — generano `arredo_interattivo.html`.
- `26A011_Scocca_controsoffitto_divisori.stp` — guscio scocca (controsoffitto + pannelli + muri).
- `26A011_PIANTA_GENERALE.dwg` — planimetria sorgente delle posizioni.

## Dipendenze
`cadquery` `shapely` `ezdxf` (Python). Per convertire `.dwg`→`.dxf`: LibreDWG
(`dwg2dxf`, es. `apt-get install libredwg-tools`); con input `.dxf` non serve.

## Da rifinire
- Maniglie/ferramenta e ripiani interni degli armadi (dal layer `F_FERRAMENTA` / dalle sezioni).
- Verifica altezze vs soffitto inclinato della baia (pareti attrezzate ~2.298 in alcuni punti).
- Integrare i prospetti aggiornati per i mobili lavabo (fronti reali al posto del footprint).
