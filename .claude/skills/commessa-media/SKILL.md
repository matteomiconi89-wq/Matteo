---
name: commessa-media
description: >
  Pipeline automatica "da cartella a prodotti": l'utente indica la cartella di una
  commessa (pianta DWG/DXF, disegni STP dei mobili, distinta materiali e ferramenta)
  e la skill fa l'inventario, gli fa scegliere da un menu COSA tirare fuori (render
  fotorealistici, viste, demo 3D camminabile, mondo Marble, tour video stile
  Abitativo, clip social, PDF dossier) e poi produce solo quello, con collaudo a
  ogni passo. Usala OGNI VOLTA che l'utente indica una cartella di lavoro/commessa,
  nomina pianta+STP+materiali, o chiede render/viste/tour/video/mondo 3D/dossier da
  disegni CAD — anche per un solo prodotto ("fammi solo i render") e anche se non
  nomina la skill. Trigger tipici: "commessa", "cartella con la pianta", "disegni
  stp", "fammi i render/le viste/il tour", "come abbiamo fatto per DINO CHIESA",
  "AVVIA_COMMESSA". Also trigger on English requests like "renders/walkthrough/video
  tour from CAD folder".
---

# Commessa → Media

Un solo comando: l'utente dà una cartella, tu consegni i prodotti che sceglie.
Tu (Claude) sei il cervello dell'"exe": progettista della spec, regista delle AI
esterne (Manus, Marble/World Labs, Veo/Gemini), collaudatore. L'utente non deve
fare nulla, tranne: approvare i checkpoint, incollare le chiavi API quando servono,
e dire VAI prima di ogni spesa.

Lingua di lavoro: **italiano** (l'utente è un falegname italiano, niente gergo
informatico non spiegato). La verità è SEMPRE il disegno: mai inventare geometria,
misure o codici articolo che non stanno nei file.

Se lavori dentro il repo `Matteo`, fanno fede anche `PROTOCOLLO_RENDER_MANUS.md` e
`PROTOCOLLO_TOUR_VIRTUALE.md` (stato commessa, regole già concordate). Fuori dal
repo, tutto il necessario è in questa skill.

## Fase 0 — Inventario della cartella

Prima azione, sempre: scansiona la cartella indicata (ricorsivamente) e classifica:

| Cerca | Estensioni / indizi | Ruolo |
|---|---|---|
| Pianta / layout | `.dxf`, `.dwg`, PDF con "pianta/layout" nel nome | misure vere, posizioni mobili |
| Solidi mobili | `.stp`, `.step` | geometria di riferimento, un file per mobile |
| Distinta materiali | csv/xlsx/txt/pdf con "material/distinta/finiture" | finiture e colori per i prompt render |
| Ferramenta | csv/xlsx/txt con "ferramenta/cerniere/guide" | dettagli che nei render devono esserci (o NON esserci: es. gola = niente maniglie) |
| Render/foto esistenti | png/jpg | se già collaudati, si riusano senza rifare |
| Note/brief | txt/md | vincoli del cliente |

Scrivi `OUTPUT_MEDIA/INVENTARIO_COMMESSA.md` nella cartella della commessa (o dove
chiede l'utente): tabella file→ruolo, più la lista di **cosa manca**. Regole dure:

- Elenca SOLO file che esistono davvero. Niente inventari "presunti".
- `.dwg` binario non si legge qui: per misurare serve il `.dxf` → chiedi all'utente
  l'export DXF da AutoCAD (un minuto: `SALVACOME` → DXF). Non stimare misure a occhio.
- Gli `.stp` si aprono come testo per leggere l'header (nome pezzo, autore, CAD di
  origine); la geometria completa non si ricostruisce qui → i volumi 3D si fanno
  con le misure del DXF + distinta, gli STP servono da conferma nomi/conteggio.
- Se manca la pianta: dillo subito e proponi cosa si può comunque produrre
  (render per singolo mobile dagli STP + distinta) e cosa no (demo/tour d'ambiente).

## Fase 1 — Menu prodotti (il cliente decide, non il protocollo)

Motivo: per certi clienti il tour è inutile e i soldi vanno spesi solo su ciò che
serve. Se l'utente ha GIÀ detto cosa vuole ("solo render e PDF"), salta il menu e
registra la scelta nel piano. Altrimenti chiedi con `AskUserQuestion` (una chiamata,
2 domande, `multiSelect: true`):

**Domanda 1 — Prodotti fermi** · **Domanda 2 — Prodotti in movimento**

| # | Prodotto | Costo vivo | Tempo indicativo |
|---|---|---|---|
| A | Render fotorealistici (Manus, collaudo pixel) | crediti Manus | 1–2 giri/mobile |
| B | Viste alte 1500 px per stampa/preventivo | 0 € | minuti |
| C | Demo 3D camminabile (link + QR, ante apribili) | 0 € | ~1 ora |
| D | Mondo camminabile fotorealistico (Marble API) | ~1.580 crediti World Labs/ambiente | ~10 min/ambiente |
| E | Tour video stile Abitativo (Veo 3.1 + montaggio) | ~0,70 €/clip → ~5–8 € per 8 ambienti | ~1 ora |
| F | Clip social singola (1 ambiente) | ~0,70 € | ~10 min |
| G | PDF dossier commessa (viste + dati + QR) | 0 € | minuti |

Nel menu scrivi i costi: la scelta è anche una scelta di spesa. Dipendenze da
dichiarare: D, E, F richiedono render collaudati (A o esistenti); il tour E esce
meglio se prima c'è B (viste per le copertine e il PDF).

**Se non puoi fare domande** (esecuzione batch/subagente, nessun utente presente):
non bloccarti — scrivi il menu con la tua raccomandazione dentro il piano (Fase 2)
e produci SOLO ciò che il prompt ha chiesto esplicitamente.

## Fase 2 — Piano di produzione (prima di spendere un centesimo)

Scrivi `OUTPUT_MEDIA/PIANO_PRODUZIONE.md`: per ogni prodotto scelto, i passi, chi
fa cosa, il collaudo previsto, il costo. Poi la regola d'oro:

> **Nessuna chiamata a pagamento (Veo, Marble, Manus) parte senza un VAI esplicito
> dell'utente sul piano, con la cifra scritta.**

Chiavi API — il repo di lavoro può essere PUBBLICO, quindi:
- Le chiavi arrivano in chat o da variabili d'ambiente (`GEMINI_API_KEY`,
  `WLT_API_KEY`) o file effimeri (`~/.gem_key`, `~/.wlt_key`). MAI in un commit,
  MAI in un artifact, MAI in un file dentro la cartella commessa.
- A fine progetto ricorda all'utente di rigenerare le chiavi usate.

## Fase 3 — Produzione (per ciascun prodotto scelto)

Dettagli operativi, endpoint e trappole note: leggi
[references/pipeline_api.md](references/pipeline_api.md) PRIMA di eseguire D/E/F
o le catture headless. Script pronti in `scripts/` (non riscriverli da zero):

- `scripts/veo_clips.py` — clip Veo 3.1 da render: lotto con quota (coppie da 2,
  retry 429), polling, download. Chiave da ambiente, mai in chiaro.
- `scripts/monta_tour.py` — montaggio tour: card intro/outro, targhette per
  stanza (PIL, il ffmpeg di imageio NON ha drawtext), dissolvenze xfade, audio muto.
- `scripts/marble_world.py` — mondo Marble via API (upload render → generate →
  polling → link mondo/pano/splat). Da usare dove la rete arriva a `api.worldlabs.ai`.
- `scripts/collaudo_marble.py` — collaudo numerico del mondo: riproiezione
  pano→prospettiva e correlazione col render sorgente (soglia 0,6).

**A — Render (Manus)**: flusso del protocollo render. Misure dal DXF (ezdxf) →
volumi 3D di controllo → **checkpoint: l'utente approva i volumi PRIMA di spendere
crediti** → brief Manus pronto da incollare (geometria esatta in mm, materiali
dalla distinta, dettaglio firma tipo gola/LED, righe di auto-verifica) → l'utente
incolla e riporta i render → collaudo col righello sui pixel (proporzioni ±10%),
codici SOLO dai documenti, mai letti dall'immagine. Max 3–4 correzioni per giro +
lista anti-regressione. I brief vanno scritti in `OUTPUT_MEDIA/BRIEF_RENDER_<mobile>.md`.

**B — Viste**: dalla demo C (cattura headless, trucchi nel reference) o, se la demo
non è richiesta, impaginando i render collaudati a 1500 px con margini puliti.

**C — Demo 3D**: parti da `assets/demo_template.html` (motore three.js r128 già
collaudato: stanze/arredi/tappe data-driven, minimappa, schede ⓘ, ante apribili con
`anta()`). Sostituisci SOLO i dati (ROOMS/PARTS/TAPPE/schede) con le misure vere del
DXF. Pubblica come artifact + QR. Collaudo camminata: scala percepita (porte ~2 m,
piani ~0,85–0,90 m), conteggio moduli per parete contro la distinta, giro 360° a
caccia di oggetti inventati, fluidità su telefono.

**D — Mondo Marble**: un mondo PER AMBIENTE (non tutta la commessa in un colpo),
partendo dal render collaudato dell'ambiente. Prima di ogni giro controlla i
crediti; collaudo numerico col relativo script + occhio del falegname.

**E — Tour video**: sequenza = ordine di visita reale degli ambienti. Per clip:
prompt "slow smooth dolly-in, keep every cabinet exactly as in the reference image;
do not add or remove any furniture" + negative anti-invenzioni (people, text,
warped geometry, extra cabinets). Collaudo per clip sui fotogrammi 0 / metà / fine:
frame 0 deve essere il render; niente mobili nuovi. Montaggio con `monta_tour.py`
(copertina commessa, targhette, QR finale alla demo). L'audio nativo Veo non è
collaudabile da chi non ascolta → consegna MUTA e dillo.

**F — Clip social**: come E ma una sola clip, verticale se richiesto (aspectRatio 9:16).

**G — PDF dossier**: pagina HTML stampabile (copertina, una pagina per ambiente con
vista + misure vere + finiture dalla distinta, pagina contatti con QR) → chromium
headless `--print-to-pdf`. Niente dati inventati: ogni numero viene da DXF/distinta.

## Fase 4 — Collaudo finale e consegna

1. Ogni prodotto passa il suo collaudo PRIMA di essere mostrato come finito; esiti
   scritti in `OUTPUT_MEDIA/COLLAUDO.md` (voce per voce: ✓/✗ + misura). L'occhio
   del falegname batte il collaudo AI: nel dubbio, chiedi conferma su UNA immagine.
2. Consegna: file inviati in chat (SendUserFile), demo/pagine come artifact con QR,
   tabella riassuntiva "prodotto → dove sta → costo speso".
3. Aggiorna lo stato commessa (nel repo: tabella §7 del protocollo tour).
4. Chiudi ricordando la rotazione delle chiavi se sono state usate.

## Regole d'oro (sempre)

- Il disegno è la verità; l'AI si adegua o si boccia.
- Costi dichiarati PRIMA, spesa solo dopo il VAI.
- Un checkpoint umano prima di ogni salto di qualità (volumi prima dei render,
  render prima dei mondi/video).
- Mai chiavi o dati riservati in repo, artifact o file di consegna.
- Niente promesse sul non collaudabile (audio, resa su dispositivi che non hai).
