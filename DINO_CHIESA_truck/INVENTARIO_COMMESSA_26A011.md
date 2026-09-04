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

## 3. Cosa gli STP NON portano (onestà)

- **Materiali e finiture: NON ci sono.** L'export CATIA ha un solo colore
  generico (RGB 210,210,255 = azzurro di default), nessun nome commerciale.
  → I materiali si prendono dal **capitolato di Matteo** (`CAPITOLATO_FINITURE.md`):
  Sabbia / Lava / Congo, WMT, Macadamia, Champagne, ecc.
- **Ferramenta: NON c'è.** I 203 componenti sono tutti pannelli in legno
  (fianchi, basi, cieli, ripiani, ante, schiene, zoccoli, cassetti, travoni,
  cornici): nessuna cerniera, guida o profilo gola nominato.
  → Se serve in distinta, va chiesta a parte.
- **Posizioni nel camion: NON ci sono.** Ogni mobile è esportato nel proprio
  sistema di riferimento (origine 0,0,0). Le trasformazioni interne descrivono
  solo i pezzi dentro il mobile.
  → **Servono dalla pianta**: per questo serve il DXF.

## 4. Cosa manca per andare avanti

1. **DXF della pianta generale** (da AutoCAD: `SALVACOME` → DXF 2010 o più
   recente). Il DWG 2018 è compresso e qui non è leggibile; l'anteprima
   incorporata (256×108 px) mostra il layout ma non permette misure.
   Serve per: posizione X,Y di ogni mobile, divisione degli ambienti,
   posizione di porte e finestre.
2. **Gli STP mancanti**: bagni, lavanderia, ufficio, letti, divano
   (dal capitolato risultano previsti ma non sono tra i file caricati).
