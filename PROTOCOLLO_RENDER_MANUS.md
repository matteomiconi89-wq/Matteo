# PROTOCOLLO RENDER MANUS — DWG → render fotorealistico collaudato

> Automazione operativa di Claude per Matteo. Non è un programma: è il metodo che Claude
> esegue in automatico ogni volta che Matteo manda un DWG/DXF di un mobile.
> Ricostruito il 12/08/2026 dalle `SPEC_COLLAUDO.md` della commessa 26-A011 su Dropbox
> (la sessione locale originale "Collaborazione MANUS per render DWG" del 06-07/08/2026 non è più raggiungibile).

## 1. Il flusso in una riga

**Matteo manda il DWG → Claude estrae le misure vere → Claude briefa Manus → Manus renderizza a giri → Claude collauda (misure + visivo) → post-produzione deterministica se serve → solo ciò che passa il collaudo arriva a Matteo come `render_FINALE`.**

Ruoli: Manus è il motore generativo (lavora a crediti, ~100–215 cr/giro). Claude è progettista della spec,
regista dei prompt e collaudatore. Matteo è l'occhio finale: **occhio del falegname > collaudo AI** —
se Matteo boccia una consegna promossa, il collaudo si aggiorna (è già successo: cucina giro 8).

## 2. Dove stanno i file

Dropbox, cartella di lavoro: `/STEFANO/Matteo/RENDER_MANUS/` (ns:12436541105//Matteo/RENDER_MANUS)

- Una sottocartella per mobile: `26-A011_<nome>` (es. `26-A011_cucina`).
- Dentro ognuna: estratti CAD (`*_tavola_cad.png`, `*_pianta.png`, `*_prospetto*.png`, `*_assonometria.png`),
  i giri di render (`render_v3_01_chiuso.png`, `render_L5_aperto.png`, …), la consegna (`render_*FINALE*.png`)
  e la **`SPEC_COLLAUDO.md`** del mobile (spec dal CAD + storico giri + lezioni).
- I DWG sorgente arrivano da Matteo (chat o Dropbox); i DXF di lavoro e gli script vivono nello scratchpad
  della sessione e i risultati si caricano su Dropbox.
- Attenzione ai link Dropbox monouso passati a Manus: un errore 400 su un URL sbagliato **consuma tutti i link**
  del lotto → rigenerarli tutti.

## 3. Fase A — Analisi del DWG (misure precise)

1. Convertire/aprire il DWG (ezdxf). Le misure si prendono dalle **bbox reali dei blocchi**;
   i blocchi si esplodono con `virtual_entities` e si ordinano per X (come `m6_esplodi_pianta.py`).
2. **I codici articolo si leggono dai MLEADER del DXF, mai dall'immagine** (errore storico: "WTS 510" letto
   dal render, il DXF diceva WTS 610).
3. **Il layer è specifica**: un'anta che stampa grigia ma sta sul layer "Tamburato Laminato NERO Opaco" è NERA.
   Ma **mai dedurre la ferramenta dal nome del blocco** (il blocco "maniglia+serratura" non implica che si veda:
   fa fede il disegno + le correzioni di Matteo).
4. Trappole note della tavola: testi ruotati di 180° nel sorgente (renderizzare con skip dei layer
   `F_Testi`/`F_Sezioni` e opzione `ruota180`), retini pieni che coprono i dettagli (opzione `no_hatch`).
5. Generare le tavole PNG per Manus: prospetto, pianta, sezioni (script `render.py` da rigenerare al bisogno:
   DXF→PNG con ezdxf+matplotlib, opzioni `no_hatch`, `ruota180`, skip layer).
6. **PROTOCOLLO SOLIDI** (standard dal 07/08, svolta anti-invenzioni): dal 2D costruire solidi 3D propri
   (senza forature) e dare a Manus **l'assonometria dei solidi come àncora geometrica**. Da quando si usa:
   "INVENZIONI ZERO". Lato AutoCAD esiste `esporta-solidi.lsp` in `/STEFANO/Matteo/CLAUDE/Definitivi/`.

## 4. Fase B — SPEC_COLLAUDO.md (da scrivere PRIMA del primo giro)

Partire **subito** con mappa moduli + spec: evita i giri 1–2 buttati (lezione cucina).
Template consolidato:

```markdown
# SPEC COLLAUDO — <Mobile> (<commessa>, <sigla>)
DXF: `<file>` — <viste disponibili>

## Spec dal CAD (mm)
- Totale L × H × P, rapporto H/L … ← SEMPRE, è la prima cosa che Manus sbaglia
- Tabella moduli: | Sigla | Zona | X da..a | Misure | Note |
- Dettagli vincolanti: ante/vani ESATTI ("ESATTAMENTE 4 frontali — né 5 né 6"),
  ferramenta a vista sì/no, zoccolo/piedini/fessura, finiture e codici (dai mleader)

## Ancore relative (rapporti, non solo mm)
- es. "TV = 70% del mobile = 1,44× l'anta", "DX/SX ≈ 1,80", "cimasa 400 sopra la placca"

## Regole trasversali del progetto
- finitura fronti (laminato opaco greige "CERA"), interni bianchi, stile scena = render approvato
  di riferimento (stesso ambiente, stessa luce, stesso pavimento)
- MA: **ogni mobile fa storia a sé — si guarda il SUO disegno** (mai importare lo zoccolo della
  cucina sulla lavanderia che ha i piedini)

## Storico giri
| Giro | Esito | Note |  ← aggiornare DOPO OGNI GIRO, coi crediti
```

La spec vive nella cartella Dropbox del mobile e si aggiorna a ogni giro e a ogni correzione di Matteo.

## 5. Fase C — Brief a Manus (regole d'oro)

1. **Primo brief completo**: spec + tavola CAD + assonometria solidi + **gabbia in pixel**
   (la gabbia funziona per composizione/centratura/numero campate; usarla dal primo giro, non dal terzo).
2. **Max 3–4 correzioni per giro.** Con 8 insieme entra tutto ma regredisce altro (lezione libreria).
3. Quando una correzione non entra dopo 2 tentativi → **giro single-fix con ancore spaziali**
   ("il piano cottura sta sopra M6, il modulo tra M5 e M7") — ha sbloccato la cucina al giro 6.
4. **Sempre lista anti-regressione nel prompt**: elencare esplicitamente ciò che è già giusto e va tenuto.
5. Le **posizioni** a volte le ignora dichiarando ✓ (specchio M1 mai spostato in 2 giri): se non si muove,
   passare alla chirurgia post.
6. Chiedere a Manus l'**auto-collaudo in pixel** nel prompt ("misura tu e riporta: sx 276/target 280…") —
   sul portale M2 ha funzionato al primo colpo.
7. Manus **non sa correggere le proporzioni globali via prompt**: 4 formulazioni diverse (rapporto, mm,
   gabbia, "H deve vincere") → sempre ~0,90. Le proporzioni fini NON si chiedono: si sistemano in post (Fase E).

## 6. Fase D — COLLAUDO (prima di qualsiasi consegna)

Checklist obbligatoria su OGNI render candidato:

1. **Misure col righello sui pixel**: H/L globale e rapporti-ancora della spec, confrontati col CAD.
   Tolleranza tipica accettata ±10% ("slop AI"); oltre → correzione o post.
2. **Voce per voce della spec**: numero ante/vani/frontali esatto, ferramenta, zoccolo/piedini,
   elettrodomestici e targhette (contro i codici DXF), allineamenti (gola continua, fasce in quota).
3. **ZOOM sulle aree critiche prima di promuovere** (zoccoli, basi, targhette, cerniere):
   mai giudicare dall'immagine intera (lezione cucina giro 9).
4. **Collaudo bidirezionale anche sulle zone già promosse**: ogni rigenerazione è un lancio di dadi
   (v4 ingresso ha inventato un'anta mentre "teneva tutto identico").
5. Coerenza tra viste (chiuso/aperto): stesse misure percepite, stessa scena.
6. Squadra a più lenti per i collaudi finali (6 lenti sull'ingresso: geometria, proporzioni, dettagli,
   artefatti, coerenza, scena) + ricollaudi mirati dopo ogni ritocco.
7. Esito nel file spec: ✓/✗ per voce, crediti del giro, decisione (nuovo giro / post / consegna).

**Consegna a Matteo solo dopo collaudo superato**, nominando `render_<X>_FINALE_*.png`.
I residui accettati si dichiarano onestamente nella spec (es. "H/L 1,10–1,13 vs CAD 1,05, tolleranza ok").

## 7. Fase E — Post-produzione deterministica ("bisturi", Pillow, 0 crediti)

Per la geometria di precisione e le pulizie che Manus non centra:

- **Strizzata globale** per il rapporto esatto (lavanderia: ×0,9396 → H/L 1,92 ESATTO; uscite non-16:9
  tipo 2405×1440 o 2291×1440 sono VOLUTE).
- **Warp a bande verticali** (PIL MESH): schiacciare le zone lisce (invisibile), risparmiare oggetti
  (capi ×0,86, libri, maniglie in patch quasi rigida). Bande SOLO su muri/fronti lisci.
- **MAI bande attraverso oggetti in primo piano** (il tavolo "a fagiolo" della libreria).
- **MAI strisce copiate su fronti con gradiente** (bande tonali) → sempre warp locale con feather,
  bordi su zone lisce; nei collage il **vincolo stretto vince sempre** e la toppa atterra su sfondo omogeneo.
- Rimozione oggetti su muro liscio in **clonazione** (gratis e pulita: anta fantasma ingresso, +90 px,
  correzione luminanza, feather) — preferirla a un giro Manus.
- Cuciture tonali da warp: **blur uniforme a piena larghezza** con isole di protezione (faretti),
  mai strisce locali (ammazzano la grana).
- **Coordinate delle toppe sempre MISURATE dai pixel, mai stimate** (3 tentativi sprecati sulla libreria).
- Strumento di misura: script tipo `misura_ingresso.py` (bbox e giunzioni: fughe = minimi di colonna,
  top = gradiente di riga più netto, fondo = gola d'ombra), tarato fino a coincidere con la squadra di collaudo.
- Cerniere sul bordo sbagliato → **specchiare l'anta nella sua banda** (ingresso r2).

## 8. Stato commessa 26-A011 (al 07/08/2026)

| Mobile | Cartella | Consegna FINALE | Giri/crediti |
|---|---|---|---|
| Cucina truck | `26-A011_cucina` | `render_v10_01_chiuso` (approvato Matteo) + `render_v11_02_aperto` | 11 giri, 1.541 cr |
| Lavanderia living | `26-A011_lavanderia` | `render_FINALE_chiuso/aperto` (2405×1440) | 8 giri, 1.319 cr + post gratis |
| Mobile ingresso living | `26-A011_mobile_ingresso` | `render_INGRESSO_FINALE_chiuso/aperto` | 549 cr + chirurgia |
| Parete porta living (M1) | `26-A011_parete_porta_living` | `render_M1_FINALE_chiusa/aperta` | 271 cr + bisturi |
| Portale ingresso (M2) | `26-A011_portale_ingresso` | `render_M2_FINALE_frontale/trequarti` | 703 cr (gabbia pixel + auto-collaudo) |
| Divisorio living/master (M3) | `26-A011_divisorio_living_master` | `render_M3_FINALE_aperto/chiuso` | 154 cr (v4) + bisturi TV |
| Parete letto (M4) | `26-A011_parete_letto` | — solo `render_M4v2_*`, senza spec né FINALE | da chiudere |
| Muretti Geberit (M5) | `26-A011_bagni_geberit` | `render_M5_FINALE` | 250 cr + warp locale |
| Libreria ufficio (M6) | `26-A011_libreria_ufficio` | `render_M6_FINALE` | 336 cr + chirurgia |
| Divano pensile | `26-A011_divano_pensile` | — solo `render_DIVANO_*_v2`, senza spec né FINALE | da chiudere |

Residui dichiarati e accettati (dettaglio nelle singole spec): anta specchio libreria ruotata ~15°,
vetrata 1,96× vs 2,3×, ceramiche Geberit ~20% piccole in parallasse, giunti pannello portale non a vista
(giro dedicato solo se Fabio/cliente li vogliono: "visible 18 mm reveal at the panel edges").

## 9. Strumenti

- Script Python di sessione (da rigenerare al bisogno, vivevano nello scratchpad):
  `render.py` (DXF→PNG: ezdxf, opzioni `no_hatch`/`ruota180`/skip layer), `*_esplodi_pianta.py`
  (virtual_entities + bbox per X), `misura_*.py` (misura su pixel), `fix_*.py` (warp a bande + clonazioni),
  `*_solidi.json` (solidi del protocollo).
- Lato AutoCAD (Dropbox `/STEFANO/Matteo/CLAUDE/Definitivi/`): `esporta-solidi.lsp`, `misure-solidi.lsp`,
  `nomina-solididef.lsp`.
- Post: Pillow (PIL) — warp MESH, clone, blur, resize.

## 10. Come si riparte (per la prossima sessione Claude)

1. Leggere questo protocollo.
2. Farsi dare (o pescare da Dropbox) il DWG del mobile nuovo.
3. Fase A → B → C → D → (E) → consegna. Aggiornare la `SPEC_COLLAUDO.md` del mobile a ogni giro.
4. In caso di dubbio su una regola: le spec dei mobili già chiusi su
   `/STEFANO/Matteo/RENDER_MANUS/` sono la giurisprudenza.
