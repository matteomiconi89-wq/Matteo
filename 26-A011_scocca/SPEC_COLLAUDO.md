# SPEC COLLAUDO — Scocca / scena madre (26-A011)

DXF: `scocca_26A011_rev06_aperto.dxf` + `scocca_26A011_rev06_chiuso.dxf` — modelli 3D a mesh (163 volumi),
**geometria di Matteo, non ricostruita**: bbox reali, nessuna quota stimata.
Riferimento completo misure: `SPEC_SCOCCA.md` (stessa cartella) + render interattivo
https://claude.ai/code/artifact/a59b5a9a-3f1d-4721-ad9c-de4eddb77c36
Scopo: **la scocca è l'ambiente ("stage") di tutti i mobili della commessa** — questo collaudo
serve a bloccare misure e proporzioni dell'involucro prima di piazzarci dentro l'arredo.

## Spec dal CAD (mm)

Sistema: X = lunghezza (0 = fronte lato motrice), Y = larghezza (0 = filo esterno estrattore
ingresso aperto), Z = altezza da terra. **Pavimento finito Z 1.395 = quota zero arredi.**

| Sigla | Elemento | X da..a | Misure nette | Note |
|---|---|---|---|---|
| — | Scocca completa aperta | 0..13.989 | 13.989 × 4.840 × h 4.000 da terra | chiusa: largh. 2.540 |
| COR | Corridoio centrale | 919..13.928 | largh. 2.390 · h 2.251 | controsoffitto piatto |
| A | Zona A (sala) | 919..10.199 | 9.280 × 2.390 | aperta sulle 2 baie |
| B | Zona B | 10.279..11.184 | 905 × 2.390 | tra i 2 divisori pieni |
| C | Zona C | 11.265..13.928 | 2.663 × 2.390 | vetrata interna a L |
| BI | Baia ingresso (Y 61..1.213) | 977..3.835 + 4.382..13.510 | prof. 1.152 · h 2.103→2.151 | soffitto inclinato |
| BK | Baia cucina (Y 3.603..4.779) | idem | prof. 1.176 · h 2.103→2.151 | soffitto inclinato |
| V | Fascia vetrata baie | vedi SPEC_SCOCCA | davanzale +1.000 · vetro h 647 | 5 vetrine + 2 testate |
| O | Oblò | 5 posizioni | il 3° è il maggiore (1.292×650) | corsia centrale Y 2.095..2.745 |
| P | Pilastri fissi | 3.915..4.302 e 13.590..13.928 | non spostabili | interrompono le baie |

## Ancore relative (si collaudano col righello, non a occhio)

- **soffitto corridoio / larghezza corridoio = 2.251 / 2.390 = 0,94** (il varco è quasi quadrato)
- larghezza totale aperta / corridoio = 4.718 / 2.390 = **1,97**
- davanzale vetrine = **44%** dell'altezza del corridoio; fascia vetro = **29%**
- profondità baia / larghezza corridoio = 1.152 / 2.390 = **0,48**
- persona 1.750 = **78%** dell'altezza del corridoio
- vista madre (gabbia): corridoio a X=6.000 = **789 px**, soffitto = **743 px**, VP esatto a (1200, 675)

## Regole vincolanti

1. **Un solo livello di pavimento**: niente gradini, niente passaruota (ruote sotto quota pavimento).
2. **Due gradini di soffitto e basta**: corridoio piatto 2.251; baie più basse e inclinate 2.151→2.103.
3. Fascia vetrata SOLO tra +1.000 e +1.647 sulle pareti esterne baie, nei tratti di SPEC_SCOCCA
   (non vetrare tutta la parete).
4. Oblò: 4 visibili nella vista madre (il 5° oltre il divisorio di X 10.199).
5. Scena = stessa famiglia dei render approvati della commessa (luce, pavimento, mood):
   `render_v10_01_chiuso` / `render_v11_02_aperto` della cucina.
6. Nella vista madre: **nessun mobile, nessuna persona**, spazio vuoto — è lo stage.

## Punti aperti (da confermare con Matteo prima della consegna finale)

- **Finiture reali dell'involucro** (i DXF sono volumi senza materiali): pavimento, pareti,
  controsoffitto — nel giro 1 uso i default della scena approvata (pavimento dei render cucina,
  pareti bianco caldo opaco). Da confermare o correggere al giro 2.
- **Vetrata interna zona C e vetrine**: serigrafie/telai a vista? Nel giro 1 vetro neutro.
- Trattamento esterno oltre le vetrine (paesaggio/neutro): nel giro 1 esterno neutro luminoso.

## Storico

| Giro | Esito | Note |
|---|---|---|
| Rilievo (02/09) | ✓ | misure e tavole dai DXF rev.06; artifact + repo `26-A011_scocca` |
| Manus giro 1 | **lanciato 02/09 ~10:35 UTC** | task `WSLtwCSEyoi5azfnCcFKP5` (manus.im/app/WSLtwCSEyoi5azfnCcFKP5), account Composio `manus-render` (chiave rigenerata da Matteo), agent `manus-1.6` modo `agent`; 7 allegati: 5 tavole via URL GitHub raw + 2 render scena cucina via link Dropbox monouso; collaudo al ritiro |
