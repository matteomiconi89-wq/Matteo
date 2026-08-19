# SPEC ARREDO — TRONO, piano primo (4 opzioni)

Fonte: `ARREDO - 4 opzioni.pdf` su Dropbox `/STEFANO/Matteo/TRONO/`, **revisione del 19/08 ore 00:15**
(la revisione precedente delle 23:39 aveva 4 opzioni diverse: lineare / penisola / cabina comoda / smart
working — è stata sostituita). Rilievo di base: `Piano Primo(1).pdf`.

## Limite dichiarato di questa lavorazione

A differenza della commessa 26-A011, **qui non c'è àncora CAD**: `STATO_ATTUALE.dwg` sta su Dropbox ma
gli host di download (`dropboxusercontent.com`, `manuscdn.com`) sono bloccati dalla policy di egress
della sessione, quindi il DWG non è leggibile da qui. Si lavora sulle **quote scritte nel PDF**.
Conseguenza: i render sono coerenti con le misure, ma **non sono collaudabili contro i solidi 3D**.

## Stanze (misure nette, dal PDF)

| Stanza | Misure | Note |
|---|---|---|
| Camera matrimoniale | 3,52 × 4,00 | |
| Cabina armadio | 3,52 × 1,71 | accesso solo dalla camera |
| Cameretta 1 | 4,12 × 2,52 | |
| Cameretta 2 | 2,18 × 2,97 | accesso via disimpegno |
| Wc | 2,77 × 1,36 | non arredato nelle opzioni |
| Bagno | 2,77 × 1,70 + doccia | non arredato nelle opzioni |
| Soggiorno + cucina | 30 mq, ambiente unico | |
| Corridoio | 1,25 × 4,37 | |
| Scala | 2,24 di luce | |

**Altezza utile ovunque: 2,70.**

## Le due soluzioni in sezione (è il cuore delle 4 opzioni)

| | Letto a ponte (A, C, D) | Soppalco (B) |
|---|---|---|
| Letto | a terra | piano a 140 |
| Mobile | ponte 200 × 55h, intradosso 195 | armadio 200 × 135h sotto |
| Libero sopra il materasso | **150** | **105** |
| Scala | no | sì |

Nota del PDF: con 2,70 il soppalco resta basso — sotto ci passa un armadio, non una persona in piedi;
il ponte non ha questo limite ed è più prudente sotto i 10 anni.

## Arredi per opzione

**A — letto a ponte.** Mobili a parete, centro libero, cucina a L.
Cameretta 1: letto 90×200 + ponte, armadio 1,60, scrivania · Cameretta 2: letto 90×200 + ponte, armadio,
scrivania · Camera: letto 160×200, cassettiera · Cabina: armadio 600 → 3,53 ml, colonne 400 ·
Giorno: divano 3 posti, mobile tv, tavolo 6, cucina a L.

**B — soppalco.** Massimo pavimento libero, penisola.
Camerette: soppalco 140, armadio 200×135h sotto, scala, scrivania, armadio 2,00 · Camera: letto 160×200,
panca · Cabina: armadio 600, colonne 400 → 3,53 ml · Giorno: divano, parete tv, tavolo 6-8, cucina con
penisola.

**C — cabinato.** Ponte più armadi su tre lati, pensile sopra la porta della cameretta 2, cucina a U.
Cameretta 1: letto + ponte, armadi su tre lati, armadio 1,60, scrivania · Cameretta 2: letto + ponte,
pensile sopra la porta, armadio, scrivania · Camera: letto 160×200, cassettiera · Cabina: armadio 600 →
3,53 ml + armadio · Giorno: divano 3 posti, tavolo 6, cucina a U + colonne.

**D — studio.** Scrivania doppia in cameretta 1, letto contenitore nella 2, studio in cabina, lavatrice
in cucina.
Cameretta 1: letto + ponte, scrivania doppia, armadio · Cameretta 2: letto contenitore + ponte, armadio,
scrivania, pensili · Camera: letto 160×200 + armadio 2,65 ml in stanza · Cabina: armadio 2,73 ml, studio,
armadio 2,00 · Giorno: divano, mobile tv, tavolo 8, cucina con lavatrice a colonna.

## Palette (scelta da Claude su mandato di Matteo, 19/08) — identica nelle 4 opzioni

Pavimento rovere chiaro opaco a plancia, stessa posa ovunque · pareti e soffitto bianco caldo opaco ·
tutti i mobili fissi laccati opachi bianco caldo, ante lisce, **niente maniglie, apertura a gola** ·
piani scrivania, ripiani e interni a vista in rovere naturale · cucina fronti laccati opachi greige,
top effetto pietra chiara sp 20 · tessili verde salvia nelle camerette, grigio caldo in soggiorno,
biancheria bianco sporco in camera · luce diurna diffusa da sinistra, ombre morbide.

Serve identica in tutte e 40 le immagini: è ciò che rende le opzioni confrontabili.

## Àncore geometriche mandate a Manus

`ancore.py` genera 7 PNG, tutti caricati su Manus:
5 piante quotate (scatole **vuote**: danno misura e proporzione della stanza, non la disposizione) +
`sezione_ponte.png` e `sezione_soppalco.png` con le quote in altezza.
**Nessuna posizione di mobile è stata inventata**: la disposizione sta solo nel testo del brief.

## Giri Manus

| Opzione | Task | Lanciato |
|---|---|---|
| A — letto a ponte | `92ymBy2pwoMaK4op7bESAv` | 19/08 |
| B — soppalco | `S4Pwk82oXCFhZQqih3ePLJ` | 19/08 |
| C — cabinato | `cQwSWUhTY2wsMehpN3FN54` | 19/08 |
| D — studio | `ELPWo8eg2PrwyyRQeKJseY` | 19/08 |

Richiesta per ciascuno: 10 immagini 2400×1350 (2 viste × 5 stanze) + autocollaudo con le misure in pixel.

### Giro 1 — consegnato, collaudo sui numeri dichiarati

Tutte e quattro hanno consegnato **10 PNG + report di autoverifica**. Totale **7.186 crediti**
(A 1.818 · B 2.559 · C 1.830 · D 979).

| Opzione | Aria sopra il materasso, dichiarata | Target | Esito |
|---|---|---|---|
| **A ponte** | 154 (camtta 1) · 148 (camtta 2) | 150 | ✓ **passa** (entro ±10%) |
| **B soppalco** | ~130 · piano soppalco 136/126/138/140 | 105 · 140 | ✗ **troppo arioso** |
| **C cabinato** | 142 · 119 · 120 | 150 | ✗ **respinto** |
| **D studio** | 97–106 | 150 | ✗ **respinto** |

**Il difetto non è cosmetico: inverte il confronto.** Queste 4 tavole servono a far vedere che il ponte
dà 150 cm sopra il letto e il soppalco solo 105. Al giro 1 il soppalco (B) ne mostrava ~130 e il ponte
(C, D) 119–106: **il soppalco sembrava più arioso del ponte**, cioè l'opposto della verità. Un documento
così porta a scegliere male.

Cause dichiarate da Manus: in C il piano del materasso finisce a 59 e ~90 cm invece di 45; in D il ponte
è disegnato troppo basso. In B, Manus ha contestato la sezione sostenendo che 140 + 105 = 245 ≠ 270 —
**obiezione sbagliata**: mancava lo spessore del materasso, 140 + 25 + 105 = 270.

Da segnalare a favore di A: le prime due viste davano 119 cm, Manus se n'è accorto da solo, le ha
rigenerate e rimisurate. L'autocollaudo in pixel chiesto nel brief ha funzionato.

Note residue del giro 1: in C il passaggio libero in cameretta 2 risulta ~87 cm (chiesto ≥ 90);
in D la vista di dettaglio della zona giorno mostra l'anta della lavatrice aperta per documentarla.

### Giro 2 — correzioni mirate (in corso)

Lanciate su B, C e D come **giri single-fix sulle sole 4 viste delle camerette**, in continuazione dello
stesso task (le altre 6 immagini di ciascuna opzione restano quelle del giro 1, con lista
anti-regressione esplicita nel prompt). A non viene ritoccata.

Ancore passate in rapporto, non solo in mm — lezione del protocollo 26-A011:
aria/spessore ponte = 150/55 = 2,7 · aria/altezza utile = 150/270 = 0,56 · piano materasso/h utile = 0,17
(per B: aria/h utile = 105/270 = 0,39 · piano soppalco/h utile = 140/270 = 0,52).

## Punti aperti

- ⚠️ **Quota del ponte incoerente nel PDF**: le piante scrivono "ponte h 190", la tavola in sezione
  disegna intradosso 195 con 150 liberi. Ho passato a Manus **195 / 150** (la sezione è più esplicita).
  Da decidere quale vale.
- **Assegnazione mobile → stanza**: dedotta dall'ordine di lettura delle piante e dai titoli delle
  opzioni. I casi dichiarati nei titoli sono certi (scrivania doppia in cameretta 1, letto contenitore
  nella 2, studio in cabina, lavatrice in cucina); gli altri vanno verificati sul disegno.
- **Wc e bagno** non sono arredati in nessuna opzione: esclusi dai render.
- **Palette**: scelta d'ufficio, da confermare o correggere dopo il primo giro.
- **Coerenza di scena tra opzioni**: le 4 sono partite in parallelo con lo stesso blocco palette.
  Se l'ambiente diverge, si rilancia riusando un render approvato come riferimento (costa un giro).

### Giro 2 — correzioni mirate, esito

Rifatte solo le 4 viste delle camerette di ciascuna opzione; le altre 6 di ogni set restano quelle del
giro 1. Crediti a fine giro 2: **11.871** (A 1.818 · B 5.138 · C 3.115 · D 1.800).

**B — soppalco: ✓ passa.** Le ancore in rapporto hanno centrato il bersaglio.

| Vista | Piano soppalco (140) | Aria sopra materasso (105) |
|---|---|---|
| cameretta1_view1 | 142,0 | 103,9 |
| cameretta1_view2 | 139,3 | 101,1 |
| cameretta2_view1 | 142,5 | 108,9 |
| cameretta2_view2 | 139,7 | 103,6 |

Scarto massimo 1,8% sul piano e 3,7% sull'aria. Manus ha anche accettato la correzione sulla catena di
quote (140 + 25 + 105 = 270).

**C — cabinato: ✓ passa con una riserva.** Aria 154 · 142 · 138 · 137 contro 150 → tutte entro ±10%.
Il passaggio in cameretta 2 è salito da 87 a **102-103 cm** riducendo la profondità di un fronte a 45-50,
senza allargare la stanza. Riserva: in `cameretta1_view2` il ponte è reso spesso 39 cm invece di 55
(aria/ponte 3,61 invece di 2,7) → **giro 3 su quella sola immagine**.

**D — studio: ✗ non passa.** Aria 154 · 116 · 136 · 124 contro 150: solo `cameretta1_view1` è a target.
Causa dichiarata: il basamento del letto contenitore è disegnato a 70-76 cm invece di 45 e mangia l'aria
sopra il materasso. → **giro 3 sulle altre tre viste**.

### Giro 3 — chirurgico (in corso)

- **C**: la sola `cameretta1_view2`, per portare il ponte a spessore 55.
- **D**: `cameretta1_view2`, `cameretta2_view1`, `cameretta2_view2`. `cameretta1_view1` non si tocca.
  Ancora usata: non più millimetri ma un **riferimento a un altro oggetto nella stessa stanza** —
  il materasso (45) deve stare più in basso del piano della scrivania (75), a poco più della metà.
  È la lezione del giro 6 della cucina 26-A011: quando la quota assoluta non entra, si àncora a ciò che
  sta accanto.

**Lezione da portare sugli altri lavori:** le ancore in rapporto funzionano dove i millimetri falliscono.
B e C sono rientrate al primo tentativo dopo che i target sono stati riscritti come rapporti
(aria/spessore ponte, aria/altezza stanza) invece che come quote assolute.
