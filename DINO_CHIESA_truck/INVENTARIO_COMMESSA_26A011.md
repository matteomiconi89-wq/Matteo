# INVENTARIO COMMESSA 26-A011 — camion DINO CHIESA

> Letto da Claude il 04/09/2026 dai file caricati da Matteo. Tutte le misure
> sono in **millimetri**, prese DENTRO i file STEP (unità dichiarata `.MILLI.,.METRE.`,
> export CATIA V5R20 AP214). Nessuna misura è stimata a occhio.

## File ricevuti

| File | Cosa contiene | Leggibile? |
|---|---|---|
| `26-A011_Scocca.stp` (1,3 MB) | guscio del semirimorchio aperto | ✔ geometria completa |
| `26-A011_ArmadioCameraMaster.stp` (512 KB) | armadio camera master, 6 casse | ✔ 68 componenti |
| `26-A011_ArmadioCameraDoppia.stp` (390 KB) | armadio camera doppia, 4 casse | ✔ 51 componenti |
| `26-A011_IngressoLiving.stp` (331 KB) | libreria + appenderia + scarpiera | ✔ 36 componenti |
| `26-A011_Divisorio_living.stp` (347 KB) | divisorio living/camera con TV bifacciale | ✔ 47 componenti |
| `26-A011_PIANTA_GENERALE.dwg` (1,5 MB) | pianta con i posizionamenti | ✘ **DWG 2018 compresso: serve il DXF** |

## 1. SCOCCA — le misure vere del camion aperto

| Misura | Valore dal file |
|---|---|
| Lunghezza interna | **13.970 mm** (X da 0 a 13.973) |
| Larghezza totale aperta | **4.708 mm** (Y da −2.354 a +2.354) |
| Corridoio centrale, larghezza | **2.418 mm** (Y ±1.209) |
| Campate laterali, profondità | **1.145 mm** per lato |
| Corridoio, altezza soffitto | **~2.600 mm** (piano a 2.608, 923 punti) |
| Campate, altezza soffitto | **~2.400–2.515 mm** (più basse del corridoio) |
| Struttura sopra corridoio | fino a 2.688 / 2.706 / 2.850 mm |
| Pavimento | quota 0 (telaio da −145) |
| Colmo esterno | 3.515 mm |

### ⚠ Confronto col palcoscenico Manus già costruito (giri 1-8)

| Misura | Palcoscenico attuale | Scocca vera | Esito |
|---|---|---|---|
| Larghezza totale | 4.718 | 4.708 | ✔ (−10 mm) |
| Corridoio largo | 2.390 | 2.418 | ✔ (+28 mm) |
| Campate profondità | 1.152 / 1.176 | 1.145 | ✔ |
| **Lunghezza** | 9.200 (parete fondo) | **13.970** | ✘ **+4.770 mm** |
| **Corridoio altezza** | 2.251 | **~2.600** | ✘ **+350 mm** |
| **Campate altezza** | 2.151 / 2.103 | **~2.400–2.515** | ✘ **+250/+400 mm** |

**La pianta era giusta, le altezze e la lunghezza no.** È esattamente "la scocca
da sistemare" di Matteo: serve un giro Manus che riporti il palcoscenico alle
misure vere (la cucina già promossa si ri-piazza nella scena corretta).

## 2. MOBILI — ingombri esterni

| Mobile | L × P × H (mm) | Composizione |
|---|---|---|
| Armadio camera MASTER | **2.860 × 599 × 2.055** | 6 casse (A-F) = 6 ante + cassettiera interna |
| Armadio camera DOPPIA | **2.132 × 601 × 2.055** | 4 casse (1-4) = 4 ante + cassettiera interna |
| Divisorio living/camera | **2.368 × 397 × 2.220** | modulo porta + portale a 3 fasce, TV bifacciale |
| Ingresso living | **852 × 832 × 2.080** | libreria + appenderia + scarpiera |

### Armadio camera MASTER (2.860 × 599 × 2.055)
- Ante a battente, tutte alte **2.055**: A=353, B=453, C=453, D=450, E=450, F=350 mm
- Fianchi 18 mm sp., prof. 580, altezza cassa 2.045,5
- Fasce di battuta: 65, 54, 40 mm · spalletta 50 mm · montante 30×60
- Veletta di finitura in alto: 2.830 × 59,5
- Cassettiera interna (cassa C): cassetti frontale 427 × 213,5, fondo 10 mm,
  sponde 550 × 196
- Ripiani 569 di profondità · schiene 18 mm

### Armadio camera DOPPIA (2.132 × 601 × 2.055)
- 4 ante alte 2.055: 473, 453, 450, 470 mm
- Fianchi 18 sp. × 582 prof. · fasce 65 e 40 · spalletta 50 · montante 30×60
- Veletta 2.102 × 59,5 · cassettiera come la master

### Divisorio living/camera (2.368 × 397 × 2.220) — pezzo firma
- **Modulo porta** (a sinistra): pannello porta **786 × 45 × 2.168**, battuta
  22×11, fianchi 330 di profondità
- **Portale a 3 fasce**, larghezza utile 1.506:
  - fascia BASSA h 842: 3 ante (477 + 1.044 + 1.503) e specularmente 3
    pannelli verso camera
  - fascia CENTRALE: **pannello TV LIVING 1.506 × 1.692,5** + **pannello TV
    CAMERA** identico (TV su entrambi i lati), travoni 30 mm
  - fascia ALTA h 2.169,5: 3 ante + 3 pannelli camera
- Cornici da 8 mm sp.: verticale 2.214, orizzontale TV 1.488, orizz. porta 772
- Fascione di finitura 2.368 × 102,5

### Ingresso living (852 × 832 × 2.080)
- **Libreria**: fianchi 30 mm sp. × 600 prof. × 2.080 h, **vetro 8 mm**
  (338 × 2.056), ripiani 330 × 554,5 × 30, zoccolo 80 h
- **Appenderia**: anta 451,5 × 2.077, fianchi 18 × 581, ripiano, zoccolo 80
- **Scarpiera**: 3 ante (bassa 1.298, media 1.499, alta 2.077 di altezza,
  tutte 269,5 larghe), **ripiani inclinati** 247,5 × 465,5, fondali 247,5

## 3. Cosa portano gli STP e cosa portano i DXF

| Informazione | Dove sta | Note |
|---|---|---|
| Geometria e misure dei pezzi | **STP** ✔ | ogni componente al millimetro |
| **Materiali e finiture** | **STP ri-esportati (04/09) ✔ + layer DXF ✔** | vedi §5 e §7: i nuovi export CATIA hanno il materiale scritto nel nome di ogni pezzo |
| **Posizioni nel camion** | **DXF pianta generale** ✔ | vedi §4 — negli STP ogni mobile ha origine 0,0,0 |
| Ferramenta (marca/modello) | ✘ da nessuna parte | i componenti STP sono tutti pannelli; nei DXF c'è il layer `F_FERRAMENTA` col disegno, non i codici |

### Mobili ricevuti (aggiornato 04/09)

| Mobile | L × P × H (mm) | Componenti |
|---|---|---|
| Armadio camera MASTER | 2.860 × 599 × 2.055 | 68 |
| Armadio camera DOPPIA | 2.132 × 601 × 2.055 | 51 |
| Divisorio living | 2.368 × 397 × 2.220 | 47 |
| Ingresso living | 852 × 832 × 2.080 | 36 |
| **Parete letto MASTER** | **2.368 × 315 × 2.220** | 49 |
| **Parete letto CAMERA DOPPIA** | **2.368 × 315 × 2.220** (gemella) | 49 |

**Parete letto** (identica nelle due camere): colonna SX + testata + colonna DX.
Testata 1.714 × 307 × 2.191 con pannello 1.710 × 2.169; colonne con anta,
ripiani, **mensola in PLAC.SP30 CERA sp.30**, ripiano LED e cassetto
(frontale 205/365 × 212); cornici in **MASSELLO verniciato BVN** (vert. 30 e 36,
orizz. SX/testata/DX, sp. 8 mm); fascione 2.368 × 102.

## 4. POSIZIONI — dal DXF `26A011_PIANTA_GENERALE`

Sistema di riferimento adottato: **X = 0 all'inizio del cassone, Y = 0 sull'asse
del corridoio** (ricavato dal blocco `F_PARETI CASSONE`: 13.989 × 2.540 mm,
che conferma la scocca STP). Conversione dal disegno: `X = X_dxf − 2292`,
`Y = Y_dxf − 5525`.
Le due campate laterali si chiamano nel disegno **lato cucina** (Y positivo,
qui "NORD") e **lato ingresso** (Y negativo, qui "SUD").

### Mappa degli ambienti lungo i 14 metri

| Ambiente | Da X | A X | Cosa c'è |
|---|---|---|---|
| **CAMERA MASTER** | 0 | 3.944 | letto a 559 (corridoio) · armadio master a 1.006 (SUD) · bagno + lavabo a 1.001/1.790 (NORD) |
| *divisorio living-master* | 3.944 | 4.939 | |
| **LIVING + CUCINA** | 4.303 | 8.810 | divano a 4.410 (SUD) · cucina 4.417→8.523 (NORD) · tavolo a 5.984 (corridoio) · mobile ingresso-living a 7.010 (SUD) |
| **INGRESSO + scala** | 7.893 | 11.109 | porta e pianerottolo (SUD), scala esterna |
| **BAGNO-LAVANDERIA** | 8.386 | 10.486 | sol. B |
| *divisorio living-doppia* | 8.810 | 11.381 | |
| **CAMERA DOPPIA** | 10.539 | 13.927 | bagno + lavabo a 10.539/10.544 (NORD) · armadio doppia a 11.383 (SUD) · letto a 11.912 (corridoio) |

### Cucina — moduli veri (campata NORD, quota Y 1.273→2.354)

| Modulo | X da | X a | Largh. |
|---|---|---|---|
| Colonna frigo | 4.417 | 5.048 | 631 |
| Colonna forni | 5.027 | 5.698 | 671 |
| Base lavello | 5.647 | 6.400 | 753 |
| Base lavastoviglie | 6.248 | 6.846 | 598 |
| Base cassettiera posate L.403 | 6.847 | 7.577 | 730 |
| Base anta | 7.401 | 8.131 | 730 |
| Colonna L.220 | 7.988 | 8.523 | 535 |

> ⚠ Il palcoscenico Manus ha la cucina a X 4.407→8.291 con moduli
> 700+600+4×571+300: **posizione giusta, ripartizione dei moduli da correggere**
> con le larghezze qui sopra.

### Strutture mobili (slider)
- **Slider grande** (living/cucina): X 4.303→13.591, profondità 1.256 per lato
- **Slider piccola** (camera master): X 898→3.916, profondità 1.256
- **Pistoni escursori** `Pist. c.1150`: corsa **1.150 mm**, 8 posizioni lungo il
  camion (X 1.031 · 3.281 · 4.366 · 7.366 · 9.956 · 12.956 …)
- Controsoffitto: 13.005 × 2.418 · pavimento cassone: 13.265 × 2.290

## 5. MATERIALI — dai layer dei DXF (fonte vera)

**Pannelli e legno**
`MULTI laminato CERA` · `MULTI laminato OPACO` · `MULTI laminato_soffitto` (+ veletta)
· `MULTI OKUME` · `MULTI tessuto` · `LISTELLARE ALLEGARITO laminato o laccato`
· `LISTELLARE MDF laccato opaco colore…` · `LISTELLARE rovere` · `LSB Lam.to BIANCO`
· `Tamburato Laminato Nero Opaco` · `MASSELLO_abete` · `MASSELLO_rovere`
· `MASSELLO lac.to nero` · `Massello Lac.to colore NERO fin. OPACO`
· **`MASSELLO verniciato BVN`** (la verniciatura BVN delle tue formule)

**Superfici e rivestimenti**
**`BETACRYL o CORIAN`** (solid surface: top e lavabi) · `MINERAL WALL`
· `DIBOND_soffitto_cassone` · `LAMIERA ESTERNA` · `CARROZZERIA esterna`
· `VETRO` · **`VETRO stratificato_pellicola satinata`** · **`SPECCHIO`**
· `PROFILI_metallo` · `TUBOLARE sez. 40×40`

**Impianti e complementi**
`STRIP-LED` · `SANITARI` · `RUBINETTERIE` · `COMBIFIX bidet e wc`
· `ELETTRODOMESTICI` · `TV` · `Tendaggio` · `Piedini` · `Guide` · `Spondine`
· `FERRAMENTA` · `IMPIANTO ELETTRICO` · `IMPIANTO IDRAULICO` · `IMPIANTO cdz`
· `Illuminazione`

> Questi nomi **combaciano col capitolato di Matteo**: il vetro stratificato con
> pellicola satinata e lo specchio sono le paretine dei bagni; il laminato CERA
> è la cucina già renderizzata; BETACRYL/CORIAN è la famiglia del lavabo.

## 7. MATERIALI dagli STP ri-esportati (04/09) — il vero capitolato di produzione

Matteo ha ri-esportato gli STP con il materiale scritto nel nome di ogni pezzo.
Conteggio sui 6 mobili:

| Materiale | Pezzi | Dove |
|---|---|---|
| `MULT.LAM.B.18mm 305x130` | 88 | struttura e ante: divisorio, parete letto, ante armadi |
| `MULTI TESSUTO sp.18` | 68 | **casse degli armadi** (fianchi, basi, cieli, ripiani, schiene, cassettiera) |
| `MULT.LAM.B.18mm 305x130 CERA` | 13 | ingresso living: fianchi, basi, cappelli, ripiani, ripiani inclinati |
| `MASSELLO verniciato BVN` | 9 | cornici del divisorio e delle pareti letto |
| `MULT. PP/PLAC.SP30 3050X1300 BCO CERA BO13 CERA` | 5 | ingresso living |
| `MULT. PP/PLAC.SP30 CERA` | 4 | mensole pareti letto, travoni divisorio |
| `MULTI TESSUTO sp.10` | 2 | fondi cassetto armadi |
| `MULTI laminato OPACO sp.10` | 2 | fondi cassetto pareti letto |
| `Tamburato Laminato Nero Opaco` | 1 | **pannello porta del divisorio** |
| `VETRO STRATIFICATO SATINATO sp.8` | 1 | vetro della libreria ingresso |

> ⚠ **Da confermare con Matteo**: negli armadi il **tessuto sp.18 sta sulle CASSE**
> (fianchi, basi, cieli, ripiani) mentre le **ante** sono in laminato bianco.
> Di solito è il contrario: da falegname va verificato se l'assegnazione è
> quella voluta o se nell'export si sono scambiati i due materiali.

## 6. Cosa manca ancora

1. **STP dei mobili non ancora ricevuti**: bagno master, bagno guest,
   bagno-lavanderia, letti, divano, tavolo, libreria-parete ufficio.
   (In pianta ci sono tutti: si possono già piazzare come volumi con le misure
   del DXF, ma per il dettaglio dei frontali serve l'STP.)
2. **Codici finitura commerciali** già chiesti nel capitolato (WMT 538/520/542/511,
   Plexicor, Pral 2099, Macadamia, Champagne, tessuto 17020): i layer danno la
   famiglia del materiale, non il colore preciso.
