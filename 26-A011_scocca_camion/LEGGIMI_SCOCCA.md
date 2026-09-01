# SCOCCA CAMION 26-A011 — Volumi 3D dal DWG 2D

Sorgente: `26A011_SCOSSA_CAMION_2D.dwg` (AutoCAD 2018, scala 1:1 mm) — planimetria
generale + sezioni trasversali A-A'/D-D'/E-E' ("Estrattori aperti") + longitudinali B-B'/C-C'.
Protocollo solidi: volumi puri, niente forature/ferramenta (checkpoint 3D di Matteo in AutoCAD).

## File

| File | Cosa |
|---|---|
| `volumi_scocca.json` | I 50 solidi con nome/gruppo/layer/quote (fonte unica) |
| `genera_scocca.py` | JSON → DXF mesh + SCR (BOX/CYLINDER nativi) + 5 viste PNG |
| `scocca_volumi_aperto.dxf/.scr` | Configurazione APERTO (di progetto) |
| `scocca_volumi_chiuso.dxf/.scr` | Configurazione CHIUSO (sagoma stradale, estrattori rientrati 1150) |
| `scocca_volumi_1..5_*.png` | Assonometrie di collaudo |

Rigenerare con: `python3 genera_scocca.py volumi_scocca.json scocca_volumi`

## Sistema di riferimento

X=0 faccia esterna muso, X+ verso coda. Y=0 faccia esterna estrattore lato INGRESSO
aperto (lato scala), Y+ verso lato cucina. Z=0 terra.

## Quote chiave lette dal DWG (mm)

| Quota | Valore | Da dove |
|---|---|---|
| Lunghezza esterna cassone | 13989 | pianta, pareti 24414→38403 |
| Larghezza esterna chiuso | 2540 | sezioni (2536-2540) e pianta |
| Larghezza interna | 2390 | quota in pianta |
| Larghezza tutto aperto | 4840 | sez. A-A'/E-E', sporgenza 1150 per lato |
| Altezza totale terra-tetto | 4000 | sezioni: terra 0 → tetto 4000 esatti |
| Pavimento finito interno | Z 1395 | tutte le sezioni (quota unica aperto) |
| Altezza utile al cassone | 2290 | cielo a Z 3685 (quota 2073+217 in E-E') |
| Altezza utile a parete estrattore | 2073 | quota sez. E-E' (cielo estrattore inclinato) |
| Telaio (indicativo) | Z 830-950 | sez. C-C' |
| Baia estrattori piccoli | X 897-3915 (luce 3018) | pianta 25311→28329 |
| Pilastrino fra le baie | 387 | pianta/C-C' 28329→28716 |
| Baia estrattori grandi | X 4302-13590 (luce 9288) | pianta 28716→38004 |
| Spalla di coda | 338 + parete 61 | C-C' 38004→38342→38403 |
| Pavimenti slide estrattori | sp.52, profondità 2340 | sez. A-A' ("PAVIMENTO SLIDE Sp.52 mm ca.") |
| Pav. centrale sollevabile | sp.52, escursione ca.83 | sez. A-A' (corsa pistone 100-95=5) |
| Finestre fasce laterali | davanzale Z 2395, architrave Z 3042 | C-C'/B-B' (non modellate: no forature) |

## Semplificazioni dichiarate (da sapere in collaudo)

1. **Muso**: in realtà raccordato e inclinato (sbalzo alto verso il fronte); qui blocco
   pieno X 0-897. La zona davanti alla parete interna (X~919) è tecnica.
2. **Tetto cassone**: slab unico sp.315 (Z 3685-4000); in realtà pacco travi
   80x50+120x50x2+50x50 con dorsale impianti/gruppo sollevamento al centro.
3. **Tetto estrattori**: slab piano Z 3490-3646; in realtà inclinato (cielo da 3685 al
   cassone a 3468 alla parete esterna, quota 2073).
4. **Telaio e ruote**: INDICATIVI (layer `VOL_TELAIO`), assi a X 9536/11236 stimati dalla
   C-C'; congelare/cancellare il layer se non servono.
5. **Niente forature**: porta ingresso, finestre, botole non tagliate (protocollo).
6. Nel CHIUSO i pavimenti slide e le gonne sono omessi (starebbero dentro la sagoma);
   nel reale si impacchettano con l'escursione 83 del pavimento centrale.

## Struttura trovata nel DWG (per il report materiali)

Pareti/tetto in tubolare acciaio: 80x50x3, 120x50x3, 50x50x3, 50x20x3, 40x40x2/3,
60x40x2, 50x30x3, 120x30x3, 30x25x1.5, 50x15x2, 30x15x2, piatti 40x5/40x8/50x10/110x10/120x10.
Pavimenti legno sp.18 + pacco slide sp.52. Gruppo sollevamento a soffitto con
"Hanging bolt M10 or W3/8 (procured by locally)", scarico "Drain pipe VP20",
"Electric parts box" — componenti del kit estrattori.
