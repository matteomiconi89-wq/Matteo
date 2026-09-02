# BRIEF MANUS — GIRO 1 — Fotoinserimento strutture tubolari (locale nero)

**Allegare a Manus insieme a questo testo:**
1. La **foto frontale reale** del locale (bancone al centro, 2 cubi neri ai lati) — è la scena base.
2. `ancora_1_gabbia_assonometria.png` … `ancora_5_C_pianta_quote.png` (tavole tecniche = àncora geometrica).
3. `rif_dettaglio_cubo.jpg` (materiale reale dei cubi).

---

## COMPITO

Fotoinserimento fotorealistico nella FOTO 1. La scena resta **IDENTICA**: stessa inquadratura,
stessa prospettiva, stesse luci (faretto centrale), stessi riflessi sul pavimento nero, stesso
bancone grigio, stessi cubi neri. Puoi solo togliere gli scatoloni sopra il bancone e l'oggetto
a terra. Inserisci TRE strutture in tubo d'acciaio **NERO OPACO Ø 3,4 cm** con raccordi in ghisa
neri a vista (manicotti sui nodi, flange a terra), come da tavole allegate:

**1) GABBIA sul cubo SINISTRO e 2) GABBIA sul cubo DESTRO (identiche)**
- base 90 × 90 appoggiata sul piano del cubo, montanti ~5 cm dentro i bordi; altezza 230.
- 4 montanti verticali; telaio superiore chiuso sui 4 lati.
- 2 correnti orizzontali intermedi (a 1/3 e 2/3 dell'altezza) **solo su 3 lati**:
  il lato verso la camera è **APERTO** — lì passa solo il corrente di sommità.
- flange nere avvitate sul piano del cubo.

**3) STRUTTURA C sopra il BANCONE**
- verticali alti 150 sul piano del bancone, chiusi SOLO in sommità da un corrente che segue
  una C: fronte 220 verso camera, braccio sinistro 110 e braccio destro 180 all'indietro.
- sul fronte si vedono **ESATTAMENTE 7 verticali** (2 d'angolo + 5 intermedi, passo uguale ≈ 36 cm)
  → **6 campate uguali**. Né 6 né 8 verticali.
- braccio SX: 1 verticale a metà; braccio DX: 3 verticali; estremità libere con gomito a 90°.
- **13 verticali in totale**. Nessun corrente intermedio. Retro aperto.

**4) GRATE**: nel vano frontale di ciascun cubo, una **grata metallica nera a maglia fitta**
(i subwoofer dietro non si vedono).

## GEOMETRIA VINCOLANTE

- **Le sommità delle 3 strutture stanno sulla STESSA LINEA orizzontale** (tutte a 300 cm da terra:
  cubo 70+gabbia 230 = bancone 150+C 150). È l'ancora principale della composizione.
- top strutture = **2,0 ×** l'altezza del bancone in foto.
- altezza gabbia = **3,3 ×** l'altezza del cubo.
- larghezza gabbia = larghezza cubo (a filo).
- tubi sottili: Ø ≈ 1/26 della larghezza del cubo — niente tubi grossi.

## AUTO-COLLAUDO IN PIXEL (riporta i numeri nella risposta)

Misura sui pixel del tuo render e dichiara:
a) quota in px della sommità di gabbia SX, C, gabbia DX (devono coincidere ±1%);
b) conteggio verticali del fronte C (target: 7) e campate (target: 6 uguali);
c) rapporto h gabbia / h cubo (target ≈ 3,3);
d) conferma lato aperto gabbie verso camera e nessun corrente intermedio sulla C.

## NON FARE (anti-regressione)

- NON cambiare camera, prospettiva, luci, pavimento, pareti, bancone, cubi.
- NON aggiungere oggetti, persone, scritte, loghi, tubi extra: **INVENZIONI ZERO**.
- NON mettere correnti intermedi sul lato aperto delle gabbie né sulla C.
- NON fare tubi cromati, lucidi o grigi: **nero opaco**, riflessi coerenti col faretto.
- NON tagliare le strutture: tutte e tre interamente nel frame.

**OUTPUT**: 1 immagine fotorealistica, stessa risoluzione e stesso taglio della foto.
