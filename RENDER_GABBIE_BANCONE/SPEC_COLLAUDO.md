# SPEC COLLAUDO — Gabbie tubolari B34 + struttura C sul bancone (fotoinserimento)

Fonte geometria: `gabbia_tubolare_b34.html` / `.pdf` (branch `claude/gabbia-tubolare-disegno-yzv49u`).
Fonte scena: **foto frontale reale** del locale (bancone grigio al centro, 2 cubi-sub neri ai lati) —
la allega Matteo al brief; qui in cartella: `rif_scena_angolata.jpg` (vista angolata) e
`rif_dettaglio_cubo.jpg` (dettaglio cubo con piano effetto cemento).

## Scena (INTOCCABILE nel render)

- Camera, prospettiva, luci (faretto centrale con flare), riflessi sul pavimento nero, pareti nere,
  bancone grigio, cubi neri con piano effetto cemento: **identici alla foto**.
- Unica pulizia ammessa: togliere gli scatoloni appoggiati sopra il bancone e il piccolo oggetto
  a terra davanti; nessun'altra modifica alla scena.
- Nei vani frontali dei 2 cubi: aggiungere **grata metallica nera a maglia fitta** (i subwoofer
  non si vedono).

## Spec dal progetto (cm)

- **2 gabbie uguali sopra i cubi** — pianta 90 × 90 (esterno piedini, a filo dei bordi del cubo),
  h 230, tubo Ø 3,4 acciaio **nero opaco**, raccordi in ghisa neri a vista (manicotti sui nodi),
  flange nere alla base:
  - 4 montanti arretrati ~5 cm dal bordo del cubo (interasse 80);
  - telaio superiore chiuso su TUTTI e 4 i lati;
  - correnti intermedi a **76,7** e **153,3** dal piano del cubo **solo su 3 lati**;
  - il lato verso la camera è **APERTO** (solo il corrente di sommità lo attraversa).
- **Cubi esistenti**: 90 × 90 × h 70, piano effetto cemento (già in foto — non toccarli).
- **Struttura C sopra il bancone** (bancone h 150, in foto):
  - fronte da **220** verso la camera con **ESATTAMENTE 7 verticali visibili**
    (2 angolari + 5 intermedi a passo ≈ 36) — né 6 né 8;
  - braccio SX **110** all'indietro con 1 verticale a metà; braccio DX **180** con 3 verticali
    (passo ≈ 44); estremità libere chiuse da gomito a 90°;
  - verticali h 150, chiusura SOLO in sommità (nessun corrente intermedio);
  - **totale verticali C = 13** — né 12 né 14;
  - retro (verso la parete/operatore) APERTO.
- **SOMMITÀ TUTTE A FILO**: gabbie (70+230) e C (150+150) chiudono alla **stessa quota, 300 da
  terra** → nel render un'unica linea orizzontale di sommità per le 3 strutture.

## Ancore relative (collaudo sui pixel)

| Ancora | Valore atteso | Tolleranza |
|---|---|---|
| quota sommità gabbia SX = C = gabbia DX | stessa linea | ±1% del frame |
| top strutture / top bancone | 300/150 = **2,00** | ±10% |
| h gabbia / h cubo | 230/70 ≈ **3,29** | ±10% |
| larghezza gabbia / larghezza cubo | **1,00** (montanti ~5 cm dentro) | ±5% |
| campate fronte C | **6 uguali** | conteggio esatto |
| verticali fronte C (angolari compresi) | **7** | conteggio esatto |
| correnti intermedi gabbie (lati chiusi) | dividono l'altezza in **3 parti uguali** | ±10% |
| spessore tubo / larghezza cubo | 3,4/90 ≈ **0,038** | ±30% |

## Errori tipici Manus da controllare SEMPRE (giurisprudenza protocollo)

1. **Conteggi sbagliati** (prima cosa che sbaglia): verticali C, campate, correnti — contare a zoom.
2. **Proporzioni globali ~0,90**: non insistere via prompt, si corregge in post (Fase E).
3. **Posizioni ignorate dichiarando ✓**: verificare che il lato aperto delle gabbie sia davvero
   verso camera e che il retro della C sia libero.
4. **Invenzioni**: tubi in più, scritte, oggetti aggiunti, correnti sul lato aperto, tubi
   cromati/lucidi invece che nero opaco.
5. **Scena alterata**: camera spostata, luci cambiate, bancone/cubi ridisegnati.
6. **Zoom obbligatorio prima di promuovere**: nodi dei raccordi, flange alla base, linea di
   sommità, grate nei cubi. Mai giudicare dall'immagine intera.

## Storico giri

Esecuzione diretta Claude (fotoinserimento deterministico PIL, `render_tunnel.py`) sulla foto
angolata `rif_scena_angolata.jpg` — Manus non necessario, 0 crediti.

| Giro | Esito | Crediti | Note |
|---|---|---|---|
| v1 | ✗ | 0 | struttura ok; clonazioni scatoloni/cubo visibili, filo piano troppo chiaro |
| v2 | ✗ | 0 | piastrellatura muro sbagliata (tile grigi); gabbia meno sventagliata |
| v3 | ✗ | 0 | muro stirato per colonne ok; residui fondi scatole SOTTO il filo del piano |
| v4 | ✗ | 0 | bocciato da Matteo: bracci della C specchiati rispetto alla convenzione |
| v5 | ✓ | 0 | **PROMOSSO**: bracci corretti — dalla camera il braccio 180 (3 verticali) sta a SINISTRA, il 110 (1 verticale) a DESTRA. Convenzione fissata: SX/DX della C si leggono GUARDANDO DALL'APERTURA (da dietro il bancone), come confermato da Matteo |

## Collaudo v4 (esito)

- 7 verticali fronte C ✓ · 6 campate uguali ✓ · 13 verticali C totali ✓ (5+1+3 intermedi + 4 angoli)
- gabbia: 4 montanti ✓, 2 livelli di correnti su 3 lati ✓, fronte APERTO verso camera ✓
- h C = h bancone (per costruzione) ✓ · h gabbia / h cubo = 3,11 vs 3,29 (−5,5%, entro ±10%) ✓
- flange e manicotti sui nodi ✓ · nero opaco ✓ · scena/camera/luci intatte ✓ · grata nel vano ✓
- **Residui dichiarati**: (1) la gabbia DX non è in campo — la foto angolata inquadra solo il
  cubo SX; per la vista con entrambe serve il file della foto frontale; (2) lieve banda tonale
  sotto il filo del piano e cucitura a x≈768 visibili solo a zoom forte; (3) leggera toppa sul
  piano del cubo dove c'era l'attrezzo; (4) nessun riflesso dei tubi sul pavimento (tubi sopra
  cubo/bancone, impatto minimo).
