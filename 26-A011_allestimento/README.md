# ALLESTIMENTO 26A011 — arredo solido nella scocca

Montaggio di **tutti i mobili come solidi 3D reali** dentro la scocca aperta del truck,
posizionati secondo `26A011_PIANTA_GENERALE.dwg`.

**Viewer interattivo:** https://claude.ai/code/artifact/bda329f6-8860-4e4d-83f5-a32de719057b

## Fonte dei solidi

Gli 8 solidi principali sono i **file STL esportati da Matteo** da AutoCAD in
Dropbox `…/Progetti/stl/` (quote esatte, non approssimazioni), tessellati e decimati
per il web mantenendo il bounding box reale. Gli altri 3 mobili erano già ricostruiti
da specifiche/misure.

| Mobile | Fonte | Dim. reali L×P×H (mm) |
|---|---|---|
| Divano + pensile | STL `DIVANO_PENSILE_3D` | 2600 × 1195 × 2078 |
| Libreria ufficio | STL `LIBRERIA_UFFICIO_3D` | 1943 × 1605 × 2080 |
| Parete ingresso · PLO | STL `PLO_INGRESSO_3D` | 1814 × 81 × 2100 |
| Parete letto · camera master | STL `PARETE_LETTO_3D` | 2368 × 2315 × 2298 |
| Parete divisoria living/camera | STL `PARETE_DIVISORIA_3D` | 2510 × 340 × 2298 |
| Colonna lavatrice | STL `LAVATRICE_3D` | 1080 × 689 × 2076 |
| Muretti bagni | STL `MURETTI_BAGNI_3D` | 1144 × 531 × 1195 |
| Parete/porta lavanderia · PLI | STL `PLI_PORTA_LAVANDERIA_3D` | 3514 × 100 × 2080 |
| Mobile ingresso-living | spec ESECUTIVI_3D (41 pann.) | 1112 × 600 × 2080 |
| Lavabo lavanderia | volumi DXF (74 solidi) | 1173 × 474 × 2215 |
| Cucina | misure collaudo v10 | 3882 × 600 × 2025 |
| Tavolo + sedie *(ingombro)* | blocco planimetria | 2750 × 1816 × 760 |
| Armadio camera doppia *(ingombro)* | blocco planimetria | 2102 × 600 × 2200 |

## Mappatura pianta → trailer

`trailer_X = plan_X − 2293`, `trailer_Y = plan_Y − 3117` (scala **1:1**, verificata:
i footprint dei blocchi della `PIANTA_GENERALE` combaciano con le quote STL — es. divano
2600×1195, PLO 1822×82). Sistema trailer: X=lunghezza (0 = fronte), Y=larghezza
(0 = lato ingresso esterno, 4840 = lato cucina esterno), Z=altezza da terra; pavimento
finito a +1.395. La posizione X/Y di ogni pezzo è presa dal footprint del blocco in pianta;
l'altezza e la forma vengono dal solido STL.

## File

- `arredo_interattivo.html` — viewer 3D (Three.js): guscio scocca (ghost), 11 mobili
  come solidi con toggle e quote, 2 ingombri, viste preimpostate, griglia 0,5 m, persona 1,75 m.
- `arredo_geometry.json` — geometria combinata (guscio + mobili in coord. trailer).
- `assemble_solidi.py` — posa gli 8 solidi STL alle posizioni della pianta e li unisce
  ai mobili dettagliati e al guscio → `arredo_geometry.json`.
- `build_viewer.py` + `viewer_template.html` — generano `arredo_interattivo.html`.
- `mobili/solidi_stl.json` — gli 8 solidi STL decimati (coord. locali, con bbox reale).
- `mobili/mobile_ingresso_volumi.json`, `mobili/lavabo_lavanderia_mesh.json` — mobili dettagliati.
- `26A011_PIANTA_GENERALE.dwg` — planimetria sorgente delle posizioni.

## Da confermare con Matteo

1. **Orientamento Y / lato** di alcuni pezzi (posati contro parete esterna nella baia cucina,
   come divisori sul lato ingresso). Da confermare sulla pianta.
2. **Altezze vs soffitto inclinato della baia** (2.103–2.151 sopra il pavimento): la parete
   attrezzata del lavabo lavanderia (h 2.215) e le pareti living/camera (h ~2.298) superano
   localmente il soffitto — verificare o accorciare.
3. Piccole sovrapposizioni in pianta (divano ↔ mobile ingresso; PLI ↔ fronte baia) da rifinire.
4. **Controsoffitti**: Matteo ha aggiornato lo STEP della scocca includendo il controsoffitto —
   da integrare nel guscio del viewer.
