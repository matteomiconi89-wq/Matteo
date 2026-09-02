# SPEC SCOCCA 26A011 rev.06 — misure e proporzioni per l'arredo

> Rilievo dimensionale della scocca (semirimorchio espandibile a doppio estrattore laterale),
> ricavato dalla geometria reale di `scocca_26A011_rev06_aperto.dxf` e `scocca_26A011_rev06_chiuso.dxf`
> (163 mesh, bbox reali — nessuna quota stimata a vista). Tutte le quote in **millimetri**.
> Questo file è il riferimento per Manus e per chiunque disegni i mobili da mettere dentro.
>
> Render interattivo (3D + tavole quotate): https://claude.ai/code/artifact/a59b5a9a-3f1d-4721-ad9c-de4eddb77c36

## Sistema di coordinate (identico nei due DXF e in tutte le tavole)

- `X = 0` fronte scocca lato motrice (ralla); X cresce verso il retro, fino a 13.989.
- `Y = 0` filo esterno dell'estrattore **ingresso** in apertura; il corpo fisso occupa Y 1.150–3.690;
  l'estrattore **cucina** aperto arriva a Y 4.840.
- `Z = 0` terra. **Pavimento finito a Z = 1.395: per l'arredo usare il pavimento come quota zero.**

## Ingombri esterni

| | Chiuso (marcia) | Aperto (esercizio) |
|---|---:|---:|
| Lunghezza | 13.989 | 13.989 |
| Larghezza | 2.540 | 4.840 |
| Altezza da terra | 4.000 (4.002 con oblò) | 4.000 |
| Corsa estrattori | — | +1.150 per lato |

**Da chiuso non esiste spazio abitabile** (corridoio residuo 240 mm tra gli estrattori rientrati):
tutti i mobili vanno pensati nella configurazione aperta, dentro le sagome della zona centrale
o delle baie estrattore.

## Quote verticali

| Elemento | da terra | dal pavimento |
|---|---:|---:|
| Pavimento finito | 1.395 | 0 |
| Davanzale fascia vetrata (baie) | 2.395 | +1.000 |
| Testa fascia vetrata | 3.042 | +1.647 |
| Soffitto baie — filo esterno | 3.498 | +2.103 |
| Soffitto baie — filo interno | 3.546 | +2.151 |
| Intradosso controsoffitto (zona centrale) | 3.646 | +2.251 |
| Colmo tetto | 4.000 | +2.605 |

Il soffitto delle baie è **inclinato** (sale verso il centro: 2.103 → 2.151).
Telaio: carrello a 2 assi, X 9.061–11.711 (interassi asse: 9.536 e 11.236 dal fronte,
interasse 1.700, ruote Ø950). Le ruote restano **interamente sotto quota pavimento**:
nessun passaruota in pianta.

## Zone interne — configurazione aperta

Larghezze nette: zona centrale 2.390 (Y 1.213–3.603) · baia ingresso 1.152 (Y 61–1.213) ·
baia cucina 1.176 (Y 3.603–4.779). Larghezza utile totale da parete a parete: **4.718**.

| Zona | X da → a | Netto L × P | Sup. | H utile | Note |
|---|---|---|---:|---|---|
| Zona A — sala principale | 919 → 10.199 | 9.280 × 2.390 | 22,2 m² | 2.251 | si apre su entrambe le baie |
| Zona B — locale intermedio | 10.279 → 11.184 | 905 × 2.390 | 2,2 m² | 2.251 | tra i due divisori pieni; chiusa verso baia cucina |
| Zona C — locale posteriore | 11.265 → 13.928 | 2.663 × 2.390 | 6,4 m² | 2.251 | vetrata interna a L (luci 537/605/789) |
| Baia ingresso — mod. anteriore | 977 → 3.835 | 2.858 × 1.089 | 3,1 m² | 2.103–2.151 | testata vetrata (luce 420) |
| Baia ingresso — mod. principale | 4.382 → 13.510 | 9.128 × 1.152 | 10,5 m² | 2.103–2.151 | settori 5.019 / 1.888 / 2.123 (divisori a X 9.401 e 11.329) |
| Baia cucina — mod. anteriore | 977 → 3.835 | 2.858 × 1.089 | 3,1 m² | 2.103–2.151 | testata vetrata (luce 420) |
| Baia cucina — mod. principale | 4.382 → 13.510 | 9.128 × 1.176 | 10,7 m² | 2.103–2.151 | settori 3.921 / 2.160 / 2.967 (divisori a X 8.303 e 10.503) |

Superficie utile complessiva da aperto: **≈ 58,6 m²**.

Elementi fissi del corpo (non spostabili): blocco frontale X 0–897 (vano tecnico),
pilastri X 3.915–4.302 e X 13.590–13.928, parete di fondo X 13.928–13.989.

## Divisori esistenti (spessori 40–81)

| Divisorio | Posizione | Estensione |
|---|---|---|
| Trasversale zona centrale 1 | X 10.199–10.279 | tutta larghezza, tutta altezza |
| Trasversale zona centrale 2 | X 11.184–11.265 | tutta larghezza, tutta altezza |
| Baia ingresso | X 9.401–9.441 e X 11.329–11.387 | tutta profondità baia, tutta altezza |
| Baia cucina | X 8.303–8.343 e X 10.503–10.543 | tutta profondità baia, tutta altezza |
| Parete lato cucina (su filo corpo fisso) | X 9.836–11.811, Y 3.603 | tutta altezza |
| Pannello sospeso lato cucina | X 8.327–9.002, Y 3.603 | da +715 dal pavimento al soffitto (varco sotto) |

## Vetrate

Fascia vetrata delle baie: **davanzale +1.000 dal pavimento, vetro h 647** (fino a +1.647).

| Elemento | Posizione X | Luce |
|---|---|---:|
| Vetrina cucina 1 | 2.659 → 3.529 | 870 |
| Vetrina cucina 2 | 5.679 → 7.949 | 2.270 |
| Vetrina cucina 3 | 9.059 → 9.779 | 720 |
| Vetrina cucina 4 | 10.799 → 11.769 | 970 |
| Vetrina ingresso | 9.634 → 11.204 | 1.570 |
| Testate anteriori baie (×2, tutta altezza) | X ≈ 948 | 420 |
| Vetrata interna zona C (tutta altezza) | 11.825 · 12.657 · 12.668→13.457 | 537 · 605 · 789 |

## Oblò a soffitto (5, in corsia centrale Y 2.095–2.745)

1.318→1.968 (650×600) · 4.921→5.701 (780×600) · 6.303→7.595 (1.292×650) ·
8.287→9.027 (740×600) · 12.302→12.992 (690×600)

Clima: 2 unità sopra il tetto (X 1.651–2.551 e 9.392–10.292), nessun ingombro interno.

## Vincoli per l'arredo (registro V1–V8)

- **V1 Altezze utili.** 2.251 in zona centrale; nelle baie 2.103–2.151. Colonne/armadi ≥ 2.100
  solo nella fascia centrale (larga 2.390).
- **V2 Fascia vetrata.** Contro le pareti esterne delle baie solo basi/banconi h ≤ 1.000;
  non ostruire le vetrine (+1.000 → +1.647).
- **V3 Pavimento unico.** Piano continuo a +1.395 da terra, senza gradini né passaruota.
- **V4 Elementi fissi.** Blocco frontale, pilastri e parete di fondo come sopra: non spostabili.
- **V5 Divisori esistenti.** Verificare prima di spostarli (tabella sopra).
- **V6 Oblò.** Niente pensili o controsoffitti pieni sotto le 5 posizioni.
- **V7 Pannello sospeso.** X 8.327–9.002 lato cucina, da +715 al soffitto.
- **V8 Carichi.** Arredi pesanti preferibilmente sopra il carrello (X 9.061–11.711);
  da validare con il costruttore della scocca.

## File in questa cartella

- `SPEC_COLLAUDO.md` + `BRIEF_MANUS.md` — spec di collaudo e brief giro 1 per Manus
  (anche su Dropbox: `/STEFANO/Matteo/RENDER_MANUS/26-A011_scocca/`).
- `gabbia_pixel_scocca.png` + `gabbia_scocca.py` — gabbia di inquadratura della vista madre
  (prospettiva centrale reale calcolata dalla geometria, quote in pixel).
- `scocca_misure_interattivo.html` — pagina interattiva (3D + tavole): copia locale dell'artifact.
- `scocca_assonometria_*.png` — àncora geometrica dei volumi per Manus (aperto ×2, chiuso).
- `scocca_pianta_aperta.png` · `scocca_sezione.png` · `scocca_prospetto.png` · `scocca_pianta_chiusa.png`
  — tavole quotate.
- `analizza_scocca.py` — dump misure (bbox per mesh/layer) dai DXF.
- `genera_tavole.py` — generatore delle tavole SVG quotate.
- `assonometria.py` + `geometry.json` — assonometrie dai volumi estratti.
- `dxf/` — i due DXF sorgente rev.06.
