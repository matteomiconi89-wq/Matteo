# 26-A011 B&B CAR (rif. Dino Chiesa) — pacchetto per il render

Truck espandibile per fiere. La geometria in questo pacchetto **non è modellata a
occhio**: viene dai file esecutivi (STEP dell'ufficio tecnico + DWG di progetto) ed è
precisa al millimetro. Ogni oggetto porta il proprio **codice di distinta**.
Da rifare non c'è nulla di geometrico: servono luci, materiali e inquadrature.

---

## 1. File

| file | cosa contiene |
|---|---|
| `26A011_camera_master.glb` | **camera master**, 182 pezzi, origine al centro della stanza |
| `26A011_camera_master.obj` + `material.mtl` | stessa cosa in OBJ, se serve |
| `26A011_arredo_completo.glb` | tutto l'arredo del veicolo, 348 pezzi |
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

Nel DWG i materiali **non sono un attributo**: sono i **layer `F_...`** su cui è
disegnata la geometria dentro i blocchi. Sono stati letti da lì e assegnati pezzo
per pezzo; nel GLB lo **slot materiale porta il nome del layer originale**, quindi
si sostituisce la finitura senza toccare la geometria.

| pezzi | layer del DWG | materiale | finitura |
|---:|---|---|---|
| 315 | `F_MULTI laminato OPACO` | multistrato + laminato opaco | **da fissare** |
| 9 | `F_LISTELLARE ALLEGARITO_laminato o laccato` | listellare alleggerito | **da fissare** |
| 9 | `F_SANITARI` | ceramica | bianco |
| 7 | `F_Imbottiti` | imbottito divano | **da fissare** |
| 3 | `F_PROFILI_metallo` | profili metallici | **da fissare** |
| 2 | `F_MULTI laminato CERA` | multistrato + laminato cera | **da fissare** |
| 1 | `F_PARETI_slider` | pareti slider | **da fissare** |
| 1 | `F_MINERAL WALL` | mineral wall | **da fissare** |
| 1 | `F_FERRAMENTA` | ferramenta | metallo |

**La camera master è tutta in `F_MULTI laminato OPACO`**: nel DWG non c'è un
materiale diverso per le ante. I colori nel GLB sono un segnaposto plausibile —
**il DWG dice il tipo di pannello, non il colore della finitura**, e un layer
si chiama letteralmente `F_LISTELLARE MDF_laccato_opaco_colore................`,
cioè colore ancora da decidere. Prima del render finale vanno definiti.

Provenienza delle assegnazioni: 215 lette direttamente dal DWG, 106 ereditate
dalla cassa di appartenenza (i ripiani e i cieli in pianta non si vedono, ma sono
lo stesso pannello dei fianchi), 21 copiate dal mobile gemello, 6 dedotte
dall'ingombro in pianta — queste ultime 6 sono le meno sicure e riguardano
lavanderia, mobile ingresso e mobile lavabo posteriore.

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
