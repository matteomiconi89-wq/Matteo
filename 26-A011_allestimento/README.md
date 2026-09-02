# ALLESTIMENTO 26A011 — arredo solido nella scocca

Montaggio dei mobili (volumi 3D solidi, protocollo "solidi") dentro la scocca aperta,
posizionati secondo `26A011_PIANTA_GENERALE.dwg`.

Viewer interattivo: https://claude.ai/code/artifact/bda329f6-8860-4e4d-83f5-a32de719057b

## Mappatura pianta → trailer

`trailer_X = plan_X − 2293` (scala **1:1**, verificata: COLONNA frigo in pianta = X 4.416,
coincide col frigo cucina del giro 2 Manus). `trailer_Y = plan_Y − 3117` (1:1, corridoio a ±30 mm).
Sistema trailer: X=lunghezza (0=fronte), Y=larghezza (0=ingresso esterno), Z=altezza da terra;
pavimento finito a +1.395.

## Layout completo dell'arredo (coordinate trailer, X in mm)

| Mobile | X da → a | Lato | Solidi disponibili |
|---|---|---|---|
| Divano | 4.409 → 7.009 | ingresso/living | DIVANO_PENSILE_3D.dwg |
| **Cucina** | 4.416 → 8.298 | baia cucina | box da misure collaudo v10 |
| Tavolo | 5.983 → 8.733 | centro | (blocco pianta) |
| **Mobile ingresso-living** | 6.780 → 7.892 | ingresso (divisorio) | MOBILE_INGRESSO_spec.json (41 pann.) |
| **Lavabo lavanderia** | 8.385 → 9.558 | baia cucina | lavabo_volumi.dxf (74 solidi) |
| Libreria ufficio | 9.440 → 11.329 | living | LIBRERIA_UFFICIO_3D.dwg |
| Bagno doppia + lavabo | 10.543 → 12.641 | baia cucina | LAVABO bagno / MURETTI_BAGNI |
| Armadio camera doppia | 11.382 → 13.484 | ingresso | ARMADIO (blocco pianta) |

In **grassetto** i 3 mobili già posati nel viewer. Gli altri hanno i DWG solidi in
Dropbox `ESECUTIVI_3D/` e si aggiungono con lo stesso metodo.

## File

- `arredo_interattivo.html` — viewer 3D (guscio trasparente + 3 mobili, toggle, viste, pianta).
- `arredo_geometry.json` — geometria combinata (guscio scocca + 3 mobili in coord. trailer).
- `assembla.py` — genera `arredo_geometry.json` da: `26-A011_scocca/geometry.json` (guscio),
  `mobili/mobile_ingresso_volumi.json`, `mobili/lavabo_lavanderia_mesh.json`, box cucina.
- `arredo_axo.png` / `arredo_plan.png` — verifiche matplotlib della posa.
- `26A011_PIANTA_GENERALE.dwg` / `.dxf` — planimetria sorgente (convertita con LibreDWG,
  57 blocchi INSERT esplosi per leggere le posizioni).
- `mobili/` — volumi dei singoli mobili pronti per l'assemblaggio.

## Da confermare con Matteo

1. **Parete attrezzata lavabo lavanderia** (h 2.215, cima a +2.215 = quota 3.610) **supera il
   soffitto inclinato della baia** (2.103–2.151). Spostare il lavabo verso la zona centrale
   (soffitto 2.251) o accorciare la parete.
2. **Y esatta e orientamento** di ogni mobile: qui posati contro parete esterna (cucina/lavanderia)
   e come divisorio lato ingresso (mobile ingresso). Da confermare sulla pianta.
3. Quali degli altri mobili aggiungere al montaggio completo.
