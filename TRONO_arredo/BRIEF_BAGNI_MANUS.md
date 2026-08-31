# Brief bagni TRONO — piano primo

Da inviare a Manus con **cinque allegati**: le quattro tavole qui sotto piu' il ritaglio
del rilievo originale (`rilievo_bagni_zoom.png`, gia' su Manus come `file-VUubVn7zkwCfHFCLx2fPHu`).

| tavola | URL |
|---|---|
| `bagni_pianta_wc.png` | https://raw.githubusercontent.com/matteomiconi89-wq/Matteo/claude/copia-conversazione-arredo-1viyfd/TRONO_arredo/bagni_pianta_wc.png |
| `bagni_pianta_bagno.png` | https://raw.githubusercontent.com/matteomiconi89-wq/Matteo/claude/copia-conversazione-arredo-1viyfd/TRONO_arredo/bagni_pianta_bagno.png |
| `bagni_prospetti_wc.png` | https://raw.githubusercontent.com/matteomiconi89-wq/Matteo/claude/copia-conversazione-arredo-1viyfd/TRONO_arredo/bagni_prospetti_wc.png |
| `bagni_prospetti_bagno.png` | https://raw.githubusercontent.com/matteomiconi89-wq/Matteo/claude/copia-conversazione-arredo-1viyfd/TRONO_arredo/bagni_prospetti_bagno.png |

Agent profile `manus-1.6-max`, task mode `agent`. Rispondere in italiano.

---

## TESTO DEL BRIEF

Devi produrre **4 render fotorealistici** di due bagni di un appartamento reale al piano primo:
`wc_view1`, `wc_view2`, `bagno_view1`, `bagno_view2`. 3000 px sul lato lungo, 16:9 orizzontale.

I due locali **non cambiano fra le quattro opzioni di arredo**: queste 4 immagini valgono per tutte
e quattro. Non farne 16.

Ti allego quattro tavole quotate. **Le tavole comandano.** Se qualcosa nel testo qui sotto
sembra contraddire le tavole, valgono le tavole. Se qualcosa nelle tavole ti sembra sbagliato,
**fermati e dimmelo prima di renderizzare** — non correggerlo di tua iniziativa.

### 1. Come si leggono le tavole

Entrambi i locali sono descritti nello stesso sistema, quello che vedi stampato sulle piante:

- **P** e' la **profondita'**. `P = 0` sta sulla **parete esterna** (quella che da' fuori) e cresce
  andando verso la **porta**. Tutti e due i locali sono profondi **2,768 m**, quindi la porta e' a
  `P = 2,768`.
- **L** e' la **larghezza**, misurata a partire da una parete lunga di riferimento, dichiarata su
  ogni tavola.
- Ogni apparecchio e' quotato **da entrambi gli angoli**, non solo con il suo ingombro. Se metti
  il vaso 20 cm piu' in la', la quota "0,236" non torna piu' e il render e' sbagliato.

Le quote in pianta vengono da un rilievo vettoriale reale, scala 36,00 punti PDF per metro:
sono misure, non stime. **Le altezze invece non sono nel rilievo** (e' una pianta) e sono scelte
di progetto: le trovi sui prospetti, marcate come tali.

### 2. WC — giro delle pareti

Locale **1,356 larghezza × 2,768 profondita'**. **E' CIECO: non ha nessuna finestra.**
Ci gira dentro solo un lavabo, un vaso e un bidet.

- **Parete esterna, `P = 0`** (il fondo, quello che vedi dritto entrando):
  **completamente vuota e cieca**. Niente finestra, niente sanitari, niente specchio, niente
  nicchie. E' un muro. Se ci metti una finestra hai sbagliato il locale.
- **Parete lunga sinistra, `L = 0`** (verso la cameretta), lunga 2,768:
  porta **solo il lavabo**. Mobile sospeso 0,60 di fronte × 0,448 di profondita', da
  **`P = 1,517` a `P = 2,117`**. Restano 1,517 di muro vuoto verso la finestra e 0,651 vuoti
  verso la porta. Specchio 0,60 × 0,90 sopra il lavabo.
- **Parete lunga destra, `L = 1,356`** (verso il bagno grande), lunga 2,768:
  porta **vaso e bidet**, in quest'ordine partendo dalla parete cieca.
  Vaso da **`P = 0,236` a `P = 0,604`**; bidet da **`P = 0,928` a `P = 1,296`**.
  Ognuno 0,368 di fronte × 0,516 di sporgenza. Fra i due ci sono 0,324 di muro.
  Dopo il bidet la parete resta vuota per **1,472** fino alla porta.
- **Parete della porta, `P = 2,768`** (lato corto, largo 1,356):
  porta da **0,80 × 2,10**, luce da `L = 0,514` a `L = 1,314`, **cardine sul lato del vaso**
  (`L = 1,314`), apre verso l'interno ruotando verso il lato lavabo.

**Il punto che si sbaglia sempre:** lavabo da una parte, vaso e bidet dall'altra, **su pareti
opposte, uno di fronte all'altro**. Non sono in fila sulla stessa parete e non sono sul fondo.
Fra il lavabo e i sanitari restano **0,908 di passaggio libero**.

### 3. BAGNO — giro delle pareti

**Non e' rettangolare: e' a L.** Corpo principale **1,700 × 2,768**, che nei **primi 1,100 m
a partire dalla finestra** si allarga fino a **2,688**. Quella rientranza e' la **nicchia della
doccia**. Se renderizzi una stanza rettangolare hai sbagliato la stanza.

- **Parete esterna, `P = 0`** (il fondo), larga 2,688 in tutto:
  - nel corpo principale, **la finestra**: luce muraria **1,161 di larghezza × 1,45 di altezza**,
    telaio 1,00, da `L = 0,172` a `L = 1,333`. Davanzale a 1,10, architrave a 2,55.
    **Questo locale la finestra ce l'ha** — al contrario del wc.
  - di fianco, verso `L` crescente, si apre la **nicchia**, larga 0,988 e profonda 1,100.
- **Parete lunga sinistra, `L = 0`** (verso il wc), lunga 2,768:
  porta **tutti e tre i ceramici in fila**, in quest'ordine partendo dalla finestra —
  **vaso** `P = 0,236 → 0,604`, **bidet** `P = 0,928 → 1,296`, **lavabo** `P = 1,600 → 2,200`
  (mobile sospeso 0,60 × 0,448, specchio 0,60 × 0,90 sopra).
  Dopo il lavabo restano 0,568 di muro fino alla porta.
- **Nicchia della doccia**, in fondo a destra, addossata alla parete esterna accanto alla finestra:
  **piatto 0,60 × 1,00 a filo pavimento, piletta centrale**, appoggiato all'angolo esterno
  della nicchia. Il lato da 1,00 corre lungo la profondita' (da `P ≈ 0` a `P ≈ 1,05`),
  il lato da 0,60 lungo la larghezza. Vetro fisso senza telaio, h 2,00, sul filo verso la stanza.
  Soffione a parete a 2,10, miscelatore a 1,05.
- **Parete lunga destra, `L = 1,700`**: esiste **solo** da `P = 1,100` in giu', cioe' dalla fine
  della nicchia fino alla porta. Non ci va niente sopra.
- **Parete della porta, `P = 2,768`** (larga 1,700): porta 0,80 × 2,10, luce da `L = 0,617` a
  `L = 1,417`, cardine a `L = 1,417`, apre verso l'interno.

### 4. Ancore di proporzione — sono la verifica, non decorazione

Queste sono le stesse cose dette come rapporti. **Sono misurabili sul render finito**, ed e' con
queste che collaudo il lavoro. Se un rapporto non torna entro il 10 %, l'immagine e' da rifare.

**WC**
| rapporto | valore |
|---|---|
| lunghezza / larghezza del locale | **2,04** — il locale e' lungo esattamente il doppio di quanto e' largo |
| altezza utile / larghezza | **1,99** — e' alto quasi il doppio di quanto e' largo: e' un locale stretto e alto |
| sporgenza lavabo / larghezza | **0,33** — il lavabo si mangia un terzo della larghezza |
| passaggio libero davanti al lavabo / larghezza | **0,67** |
| larghezza porta / larghezza della parete che la contiene | **0,59** — la porta occupa piu' di meta' del lato corto |

**BAGNO**
| rapporto | valore |
|---|---|
| lunghezza / larghezza del corpo | **1,63** |
| larghezza massima / larghezza del corpo | **1,58** — quanto conta la nicchia |
| profondita' nicchia / lunghezza totale | **0,40** — la nicchia occupa i primi due quinti |
| luce finestra / larghezza del corpo | **0,68** — la finestra prende due terzi buoni della parete di fondo |
| tratto occupato dai tre ceramici / lunghezza parete | **0,71** |
| larghezza piatto doccia / larghezza corpo | **0,35** |

### 5. Le camere — non sceglierle tu

Posizione, altezza e apertura sono disegnate sulle piante come coni numerati. Rispettale.

- **`wc_view1`** — obiettivo sulla soglia, `L 0,68 · P 2,71`, **h 1,60**, asse **dritto** verso la
  parete cieca, **FOV orizzontale 75°**. Deve entrare tutta la lunghezza: lavabo a sinistra a
  meta' strada, vaso e bidet a destra in fondo, muro cieco sul fondo.
- **`wc_view2`** — obiettivo nell'angolo cieco lato lavabo, `L 0,22 · P 0,20`, **h 1,55**,
  puntato verso l'angolo della porta, **FOV 70°**. Vaso e bidet in primo piano a destra,
  lavabo e specchio a sinistra, porta in fondo.
- **`bagno_view1`** — obiettivo sulla soglia, `L 0,85 · P 2,71`, **h 1,60**, asse **dritto** verso
  la finestra, **FOV 75°**. I tre ceramici in fila a sinistra, la finestra in fondo,
  l'apertura della nicchia con la doccia a destra in fondo.
- **`bagno_view2`** — obiettivo nell'angolo della porta lato ceramici, `L 0,30 · P 2,57`,
  **h 1,60**, **diagonale verso la doccia**, **FOV 70°**. Questa e' l'immagine che deve far
  vedere che la stanza e' a L: nella stessa inquadratura ci devono stare il lavabo in primo piano
  a sinistra, la finestra, e la doccia dentro la rientranza.

Obiettivo **rettilineo**, nessuna distorsione a barilotto, **verticali perfettamente verticali**
(niente inclinazione della camera: shift, non tilt).

### 6. Finiture e luce — scelte nostre, dichiarate

Nessun disegno dice niente sulle finiture: quello che segue e' proposto, non rilevato.
Tienilo identico nei due locali, cosi' si leggono come lo stesso appartamento.

- Pavimento e rivestimento: **gres effetto pietra chiara**, formato grande, fuga sottile a tono,
  rivestimento a tutta altezza.
- Mobile lavabo **laccato bianco caldo, sospeso, a gola** (niente maniglie).
- **Rubinetteria nera opaca**, ceramiche bianche opache.
- Specchio con **luce lineare** integrata.
- **Bagno**: luce naturale da nord dalla finestra, ora del giorno, cielo coperto luminoso.
- **WC**: **e' cieco**, quindi solo luce artificiale — faretti a soffitto piu' la luce dello
  specchio. Non inventare luce che entra da una finestra che non c'e'.
- Niente accessori di troppo: un asciugamano, un porta-sapone. Non e' un catalogo.

### 7. Cosa non deve succedere — lista anti-regressione

Sono i tre errori del primo tentativo. Controllali uno per uno prima di consegnare.

1. **Il bagno non e' rettangolare.** Ha la nicchia. Se la pianta del tuo render e' un rettangolo,
   e' sbagliato.
2. **Il wc non ha finestre. Il bagno si.** Non scambiarli e non darne una a tutti e due.
3. **I ceramici stanno sulla parete lunga**, la tramezza fra i due locali — non sulla parete di
   fondo sotto la finestra. Nel bagno sono tutti e tre su quella parete; nel wc il lavabo sta
   sulla parete lunga **opposta**.
4. La doccia sta **nella nicchia accanto alla finestra**, non sul lato lungo e non in fondo alla
   stanza.
5. Nessun oggetto puo' invadere il passaggio libero: 0,908 nel wc, 1,184 nel bagno.
6. Non aggiungere quello che non c'e': niente vasca, niente lavatrice, niente colonna, niente
   seconda porta, niente specchio sulla parete cieca del wc.

### 8. Autoverifica obbligatoria prima di consegnare

Con le immagini mandami un **referto scritto** in cui, per ogni render, misuri **sui pixel**
e riporti il valore ottenuto accanto a quello richiesto:

1. `wc_view1`: rapporto lunghezza/larghezza del locale (atteso **2,04**).
2. `wc_view1`: passaggio libero fra il fronte del lavabo e la parete opposta, diviso la larghezza
   del locale (atteso **0,67**).
3. `wc_view2`: che la parete di fondo sia **cieca** — dichiaralo esplicitamente.
4. `bagno_view1`: luce della finestra diviso la larghezza del corpo (atteso **0,68**).
5. `bagno_view1`: che i tre ceramici siano **tutti sulla stessa parete** e nell'ordine
   vaso → bidet → lavabo partendo dalla finestra.
6. `bagno_view2`: larghezza massima diviso larghezza del corpo (atteso **1,58**), cioe' che la
   nicchia si veda.
7. Per tutti e quattro: che le verticali siano verticali.

Se un valore non torna, **dimmelo invece di consegnare lo stesso**: si corregge quello e basta.

### 9. Una cosa che devi sapere

**L'altezza utile 2,70 e' un'assunzione, non una misura.** Il rilievo e' una pianta e non contiene
quote verticali. Usa 2,70 per adesso, ma sappi che se il valore vero fosse diverso cambierebbe la
proporzione di entrambi i locali. E' segnato in rosso sulle tavole dei prospetti.
