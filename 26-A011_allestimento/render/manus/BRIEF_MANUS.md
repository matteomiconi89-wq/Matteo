# 26-A011 B&B CAR (rif. Dino Chiesa) — pacchetto per il render

Truck espandibile per fiere. La geometria in questo pacchetto **non è modellata a
occhio**: viene dai file esecutivi (STEP dell'ufficio tecnico + DWG di progetto) ed è
precisa al millimetro. Ogni oggetto porta il proprio **codice di distinta**.
Da rifare non c'è nulla di geometrico: servono luci, materiali e inquadrature.

---

## 1. File

| file | cosa contiene |
|---|---|
| `26A011_camera_master.glb` | **camera master**, 214 pezzi, origine al centro della stanza |
| `26A011_camera_master.obj` + `material.mtl` | stessa cosa in OBJ, se serve |
| `26A011_arredo_completo.glb` | tutto l'arredo del veicolo, 448 pezzi |
| `26A011_scocca_aperta.glb` | scocca del truck in configurazione **aperta** (slider estratti) |
| `inquadrature.json` | le inquadrature già verificate, in coordinate |
| `arredo_plan.png`, `insieme_plan.png`, `arredo_axo.png` | pianta e assonometria di riferimento |

`arredo_completo` e `scocca_aperta` condividono la stessa origine: si sovrappongono
senza toccare nulla.

## 2. Convenzione (identica in tutti i file)

**Metri, terna destrorsa, Y in alto, pavimento a y = 0.**

    x = lunghezza del veicolo (verso la coda)
    y = altezza dal pavimento
    z = larghezza

Origini:
* `camera_master.glb` → centro della camera master
* `arredo_completo.glb` e `scocca_aperta.glb` → muso del trailer, mezzeria in larghezza

## 3. La camera master

Vano reale **3728 × 3562 × 2293 mm** (lunghezza × larghezza × altezza interna).

Il vano è chiuso su tre lati e questo condiziona tutto:

| lato | cosa c'è | in coordinate |
|---|---|---|
| anteriore | mobile contenitore testata-letto, alto 2291 | x < 0,15 |
| lato ingresso | armadio a 6 casse, profondo 620, alto 2105 | z da 1,16 a 1,78 |
| lato living | divisorio a tutta altezza **con la porta** | x da 1,52 a 1,86 |
| fianco che si allarga | è la parete che esce quando il truck si apre | z ≈ −1,78 |

**Il varco della porta** è l'unico buco nel divisorio: sta a **z > 0,59**.
Fuori da lì il divisorio è pieno.

Conseguenza pratica: **le uniche due posizioni da cui si vede davvero dentro la
stanza sono la porta e il fianco che si allarga.** Una camera messa altrove
inquadra il retro di un mobile. Le quattro inquadrature in `inquadrature.json`
sono state verificate una per una: campionando il percorso, la camera non finisce
mai dentro un solido e la linea di mira non è mai ostruita.

## 4. Materiali

I materiali vengono da due fonti, in quest'ordine:

1. **La distinta degli STEP.** I pezzi si chiamano
   `26-A011_PLS_174_RIPIANO -- MULT.LAM.B.18mm 305x130`: il materiale sta dopo il
   `--`, con spessore e formato lastra. È la fonte migliore e copre 378 pezzi su 448.
2. **I layer `F_...` del DWG**, per i mobili di cui non c'è ancora lo STEP.

Nel GLB lo **slot materiale porta il nome esatto della distinta**, quindi si
sostituisce la finitura senza toccare la geometria.

| pezzi | materiale | finitura |
|---:|---|---|
| 156 | `MULT.LAM.B.18mm 305x130` — multistrato laminato bianco 18 | bianco |
| 148 | `MULTI TESSUTO sp.18` — multistrato **rivestito in tessuto** | **tessuto da scegliere** |
| 32 | `F_MULTI laminato OPACO` (dal DWG) | da fissare |
| 26 | `MASSELLO verniciato BVN` | vernice trasparente |
| 16 | `MULT.LAM.B.18mm 305x130 CERA` | bianco cera |
| 12 | `MULTI TESSUTO sp.10` | **tessuto da scegliere** |
| 9 | `F_LISTELLARE ALLEGARITO_laminato o laccato` (dal DWG) | da fissare |
| 9 | `F_SANITARI` | ceramica bianca |
| 8 | `MULT. PP/PLAC.SP30 ... BCO CERA` | bianco cera |
| 7 | `F_Imbottiti` (divano) | da fissare |
| 6 | `MULT. PP/PLAC.SP30 CERA` | cera |
| 4 | `MULTI laminato OPACO sp.10` | da fissare |
| 1 | `VETRO STRATIFICATO SATINATO sp.8` | satinato |
| 1 | `Tamburato Laminato Nero Opaco` | nero opaco |
| 3 | `F_PROFILI_metallo`, `F_MINERAL WALL`, `F_PARETI_slider` | da fissare |

**Il dato che cambia l'aspetto del render: gli armadi sono rivestiti in tessuto**
(`MULTI TESSUTO sp.18`, 148 pezzi — le carcasse di entrambi gli armadi). Non sono
pannelli laminati. Il tessuto specifico non è indicato nella distinta: serve
scegliere colore e trama, e vanno resi come tessuto, non come legno.

Bianco e bianco cera sono invece già definiti. I colori nel GLB per i materiali
marcati "da fissare" sono un segnaposto plausibile.

Provenienza: 378 dalla distinta degli STEP, 32 lette dai layer del DWG, 27
ereditate dalla cassa di appartenenza, 5 dedotte dall'ingombro in pianta,
3 copiate dal mobile gemello, 3 fuori capitolato (materasso e guanciali).

## 5. Luci

Il truck è un espositore da fiera: luce artificiale, non sole. Nella stanza ci
sono strisce LED (layer `F_STRIP-LED` nel DWG, non modellate come geometria).
Impostazione che funziona:

* luce principale morbida che entra dal **fianco che si allarga** (z negativo);
* rimbalzo freddo dal lato opposto, molto tenue;
* LED caldi a soffitto lungo le velette, sopra armadio e testata;
* niente ombre nette: superfici opache, ambiente chiuso.

## 6. Inquadrature (già verificate)

Obiettivo **35 mm**, FOV verticale 42°. Coordinate in `inquadrature.json`.

1. **Dalla porta** (9 s) — si entra dal living attraverso il varco del divisorio.
2. **Armadio · 6 casse** (9 s) — carrellata parallela all'armadio, passando alta sopra il letto.
3. **Testata e letto** (8 s) — avvicinamento al mobile contenitore.
4. **Spaccato sul fianco** (12 s) — arco esterno oltre la parete che si allarga; quella parete **non va renderizzata**, serve come sezione.

## 7. Cosa non toccare

Le misure. Sono quelle esecutive: spessori 18 mm, montanti 30 × 60, cassetti a
passo 183, ripiani a passo 268. Se un pezzo sembra fuori posto è meglio segnalarlo
che spostarlo — probabilmente è giusto e riguarda un vincolo del veicolo.

Nota sulla **parete letto della camera doppia**: il mobile è reale (STEP, 50 pezzi,
con la sua distinta), ma questa revisione della pianta non disegna ancora quella
stanza, quindi la posizione non è agganciata al disegno come le altre — è ricavata
dal vano (schiena a X 13593,4, dove finiscono i rivestimenti laterali; stessa fascia
in larghezza della master; ruotata a guardare verso il divisorio) e **confermata
direttamente dal progettista**. Tutto il resto è agganciato alla pianta.
