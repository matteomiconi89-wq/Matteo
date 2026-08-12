# SPEC COLLAUDO — Mobile lavabo lavanderia (26-A011)

DWG: `26-A011 PROGETTO_living_mobile lavabo_lavanderia_rev.01.dwg`
Viste usate: sezione A-A' (dentro il blocco `MOBILE LAVABO_..._sez`), prospetto frontale, pianta.
3D dei volumi: `lavabo_volumi.dxf` / `.scr` — **74 solidi, rev.04, approvato da Matteo il 12/08/2026**.

## Spec dal CAD (mm)

Sistema: X = larghezza (0 = filo esterno fianco sx), Y = profondità (0 = faccia esterna parete lato
opposto, 466 = fronte anta), Z = altezza da pavimento.

| Sigla | Elemento | X da..a | Y da..a | Z da..a | Note |
|---|---|---|---|---|---|
| — | Mobile completo | 0..1173 | 66..466 | 0..670 | **L 1173 × P 400 × H 670** (piano finito) |
| N | Nicchia a giorno | 18..450 | 148..448 | 118..557 | luce 432, **sempre aperta**, 1 ripiano a 329 |
| D | Divisorio | 450..468 | 66..448 | 118..557 | sp 18 |
| V | Vano con 2 ante | 468..1155 | 148..448 | 118..557 | luce 687, 1 ripiano a 329 |
| A1 | Anta SX | 453..810 | 448..466 | 92..580 | 357 × 488, sp 18 |
| A2 | Anta DX | 813..1170 | 448..466 | 92..580 | 357 × 488, sp 18 |
| G | **Gola di presa** | 0..1173 | 418..448 | 580..610 | **30 mm APERTI**, fondo a specchio a Y 400..418 |
| T | Piano + bordo | 0..1173 | 66..466 | 610..670 | piano sp 18 a 652..670, bordo frontale h 60 |
| Z | Zoccolo | 0..1173 | 350..368 | 2..97 | **arretrato 98** dal fronte, su 6 piedini H100 |
| P | Piedini | — | 100..160 e 290..350 | 0..100 | **2 file da 3** (fila retro sotto lo schienale) |
| S | Schienale | 18..1155 | 130..148 | 118..557 | **arretrato 64 dal retro: ci passa lo scarico** |
| L | Lavabo | 499..1102 | 76.5..455.5 | 670..920 | Galassia MEG 11 PRO art. 5484, 603 × 379 |
| R | Miscelatore | 430..470 | 127..199 | 670..1100 | colonna a sx del lavabo, bocca verso destra |
| — | LED | 0..1173 | 396..400 e 431..435 | 100..108 e 652..660 | 2 strip **incassate**, non a vista |

**Parete attrezzata alle spalle** (sp 66, H 2215): mineral wall sp 4 sul lato lavanderia, orditura con
3 tubolari 80×50×3 (Z 920, 1650, 2105) + 1 tubolare 30×25×1,5 in sommità, **finestra con telaio sp 60
e vetro sp 6 h 720 (Z 965..1685) sulla faccia OPPOSTA**.

**Impianto di scarico** (12 pezzi dal layer F_SIFONAME): piletta → foro passante nel piano (80 × 18,
asse X 800) → tubo Ø32 → sifone a bottiglia (Z 185..375) → uscita e innesto in parete a Z ~310.

## Ancore relative (si collaudano col righello, non a occhio)

- **L / H-piano = 1173 / 670 = 1,75**
- **nicchia / anta = 432 / 357 = 1,21**
- ante+divisorio / nicchia = 723 / 432 = 1,67
- lavabo = 51% della larghezza del mobile; bordo lavabo (920) = 1,37 × l'altezza del piano
- zoccolo arretrato 98 = 24,5% della profondità del mobile

## Regole vincolanti

1. **NIENTE MANIGLIE E NIENTE FERRAMENTA A VISTA**: apertura a gola, i 30 mm aperti sopra le ante.
2. **ESATTAMENTE 2 ante** (nessuna terza anta, nessun cassetto) + **1 nicchia aperta** con **1 solo ripiano**.
3. **NIENTE ZOCCOLO A TERRA CONTINUO A FILO**: lo zoccolo è arretrato di 98, sotto resta la fessura d'ombra.
4. Ogni ripiano è **uno solo per vano**, a metà altezza (quota 329).
5. Finiture: carcassa/nicchia/ripiani/schienali in **laminato CERA**; ante, piano, bordo e zoccolo in
   **laminato OPACO**; fondo gola a specchio; interni chiari.
6. Stile scena = render approvati della stessa commessa (stesso ambiente truck, stessa luce, stesso pavimento).

## Punti aperti (da confermare con Matteo prima della consegna finale)

- **Colore del laminato OPACO** (ante/piano/zoccolo): nel 3D è reso antracite — da confermare.
- **Zoccolo e fondo gola**: il prospetto ci sovrappone un retino F_SPECCHIO; la sezione li disegna su
  laminato OPACO. Specchio vero o solo laminato?
- **Finestra nella parete**: confermare che sia una finestra e la sua larghezza (nel DWG non è quotata:
  nel 3D è larga quanto il mobile).
- **Colore della verniciatura dei tubolari** metallici.

## Storico

| Giro | Esito | Note |
|---|---|---|
| 3D rev.01 (12/08) | ritirato | letto solo il contorno esterno: mancava la sezione dentro il blocco |
| 3D rev.02 | ritirato | pannelli separati ma compenetrati fra loro |
| 3D rev.03 | quasi | 47 solidi, 0 compenetrazioni, 10/10 quote ok — mandato al collaudo incrociato |
| collaudo incrociato | 6 errori su 17 | 5 lenti indipendenti + verifica adversariale: 11 segnalazioni confutate |
| **3D rev.04** | ✓ **approvato da Matteo** | 74 solidi: schienali CERA, lavabo centrato, foro di scarico nel piano, impianto completo, 4° tubolare, **2 file di piedini** (indicazione di Matteo) |
| Manus giro 1 | da lanciare | brief pronto in `BRIEF_MANUS.md` + gabbia in `gabbia_pixel.png` |

**Errori miei da non ripetere** (validi anche per gli altri mobili):
- la sezione del mobile può stare **dentro un blocco INSERT**, non nel modelspace: sempre esploderlo
  (qui il blocco aveva 47.000 entità di ferramenta da filtrare via, il resto erano 79);
- un retino grigio sovrapposto **non è un materiale**: se è a L e non copre tutto il pannello, è ombra —
  qui lo stesso retino stava anche sopra un materiale diverso;
- un'isola vuota dentro un retino **è un foro** (qui il passaggio dello scarico nel piano);
- il layer `F_SIFONAME` non è decorazione: è l'impianto che **spiega** la geometria del mobile
  (lo schienale è arretrato di 64 proprio per farci passare il sifone).
