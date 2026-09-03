# PROTOCOLLO TOUR VIRTUALE — dal render Manus al camion esplorabile

> Estensione del `PROTOCOLLO_RENDER_MANUS.md` per la commessa **DINO CHIESA**:
> camion showroom allestito come **appartamento completo su ruote** — salone, cucina,
> lavanderia, 2 bagni, ufficio e 2 camere. Obiettivo: far "camminare dentro"
> il camion i clienti da un link/QR, partendo dai render che già produciamo.
> Studio completo (tecnologie, costi, rischi): artifact **Tour Virtuale DINO CHIESA**
> — https://claude.ai/code/artifact/2597d17d-5488-4771-8203-e0b58e75cf6f
> Demo dell'esperienza finale: artifact **Truck Showroom DINO CHIESA**
> — https://claude.ai/code/artifact/01e6e2ab-fd56-4b42-965f-0a6c4fbe38c6
> (copia locale: `DINO_CHIESA_truck/demo_camminata.html`)

## 1. Il flusso in una riga

**DWG allestimento → solidi 3D (checkpoint AutoCAD di Matteo) → render Manus "viste a 1,60 m"
collaudati → [opz. panorama 360° con Skybox AI] → Marble genera il mondo esplorabile →
collaudo della camminata → pagina tour con tappe + schede prodotto + QR.**

Il "video interattivo" NON è un video: è un **mondo 3D nel browser** (Gaussian splat).
I video veri e propri (passivi) si generano a parte per i social (image-to-video) e portano al link.

## 2. I tre livelli di prodotto

| Livello | Cos'è | Strumenti | Uso |
|---|---|---|---|
| A — Video cinematico | clip passiva, camera che entra nel camion | render Manus → Kling 3.0 / Veo 3.1 / Runway (image-to-video con regia camera); montaggio Manus | social, teaser |
| B — Tour a tappe 360° | panorami collegati stile Street View | Skybox AI o foto reali + Pannellum/Marzipano (gratis) o Kuula | fallback leggero |
| C — **Mondo esplorabile** | camminata libera, tipo videogioco | **Marble (world model) → splat → viewer Spark/three.js o link Marble** | l'esperienza principale: QR sul camion, preventivi, fiere |

## 3. Attrezzi nuovi (oltre a Manus)

- **Marble** (World Labs, marble.worldlabs.ai): immagine/panorama/multi-immagine → mondo 3D
  navigabile in ~30 s. Export: Gaussian splat `.ply/.spz` (2M punti o **500k per il web**),
  mesh (per AutoCAD/Blender), video; oppure link navigabile diretto.
  Piani: Free 4 mondi/mese (per i test) · Standard $20 (multi-immagine) ·
  **Pro $35 (diritti commerciali — minimo per lavori a cliente)** · Max $95.
- **Skybox AI** (Blockade Labs, $24/mese): da vista → panorama equirettangolare fino a 8K.
  Passaggio opzionale: più copertura si dà a Marble, meno spazio alla sua fantasia.
- **Spark** (viewer splat open source su three.js): per incorporare il mondo nel nostro sito.
- **Fase 2 (camion reale)**: Insta360 X5 (~€650) → file nativo `.insv` su Scaniverse (gratis)
  o Splatica → splat fotografico del mezzo vero. In alternativa 5 foto 360° → tour Kuula in giornata.
- Manus: **non** fa mondi 3D né equirettangolari affidabili. Fa render (protocollo solito),
  video da prompt (per il livello A) e può assemblare la pagina web del tour.

## 3-bis. Automazione: chi fa cosa (regola operativa dal 02/09/2026)

Richiesta di Matteo: "tutto in automatico come coi render". Schema identico al protocollo render:

- **Claude** = progettista della spec, regista dei brief, collaudatore. Prepara brief
  **pronti da incollare** con dentro i link ai file (link Dropbox condivisi normali,
  NON monouso) e le istruzioni di auto-collaudo.
- **Manus** = braccio render. **DAL 02/09/2026 È PILOTATO DIRETTAMENTE DA CLAUDE
  via Composio** (toolkit `MANUS`, account "manus-render"): `MANUS_CREATE_TASK`
  con il brief + allegati, giri successivi sullo stesso `task_id` (scena
  conservata), `MANUS_GET_TASK` per esiti e file (su manuscdn → si scaricano dal
  sandbox). Matteo NON incolla più niente. Direttiva di Matteo dello stesso
  giorno: materiali e ferramenta si leggono DAGLI STP (componenti/colori
  nell'export), le distinte separate sono facoltative.
- **Matteo** = approva i checkpoint (volumi/scena), dà il VAI sulle spese, occhio
  del falegname sui collaudi. Basta.
- Vincolo d'ambiente verificato (02/09/2026): la rete della sessione Claude remota
  blocca `*.worldlabs.ai` (403 dal proxy) → le chiamate passano da un braccio esterno.
- **VIA MAESTRA (collaudata il 02/09/2026): API World Labs, zero mani.** Matteo ha creato
  la chiave API (piano free = 7.000 crediti API; ~1.580/mondo con `marble-1.1`).
  Claude esegue tutto dal **sandbox Composio** (che raggiunge `api.worldlabs.ai`):
  `media-assets:prepare_upload` → PUT del render (scaricato con link monouso Dropbox
  generato al momento) → `worlds:generate` (`WLT-Api-Key`, permission
  `allow_id_access:true`, seed fisso) → polling `operations/{id}` → `worlds/{id}` per
  link navigabile + pano + splat `.spz` (500k/150k/100k). Collaudo numerico nel sandbox:
  riproiezione equirect→prospettiva e correlazione col render sorgente (soglia ~0,6),
  profilo fughe sulla fascia basi, nitidezza laterale vs centro. NB: crediti app e
  crediti API sono separati; l'API può andare in overage fatturato a fine mese → una
  generazione per volta e controllo `credits` prima di ogni giro.
- **ANELLO VIDEO (collaudato il 02/09/2026): Veo 3.1 via API Gemini, zero mani.**
  Chiave Google AI Studio di Matteo (serve fatturazione attiva: senza, l'API risponde
  429 RESOURCE_EXHAUSTED). Nota di rete: `generativelanguage.googleapis.com` è
  raggiungibile DIRETTAMENTE dalla sessione Claude (a differenza di worldlabs) →
  niente sandbox per Veo. Flusso: render collaudato → base64 →
  `models/veo-3.1-fast-generate-preview:predictLongRunning` (header `x-goog-api-key`,
  instances[{prompt, image}], parameters {aspectRatio 16:9, resolution 720p,
  durationSeconds 8, negativePrompt anti-invenzioni}) → polling `v1beta/{operation}` →
  URI file `:download?alt=media` → mp4. Primo test cucina: generata in ~45 s,
  collaudo a occhio sui fotogrammi 0/4/7,5 s: PROMOSSA (frame 0 = il render, carrellata
  stabile, niente mobili inventati). Costo ~0,5-0,8 €/clip 8 s (fast 720p);
  modelli disponibili anche `veo-3.1-generate-preview` (qualità piena) e `-lite`.
  Prompt tipo: "Slow, smooth dolly-in ... keep every cabinet exactly as in the
  reference image; do not add or remove any furniture" + negative "people, text,
  warped geometry, extra cabinets". La chiave NON va mai nel repo (repo pubblico);
  a fine progetto Matteo la rigenera.
- Brief pronti in `DINO_CHIESA_truck/`: `BRIEF_MANUS_MARBLE.md` (fallback via Manus,
  se mai servisse il browser).

## 4. Fase 1 — dai disegni (si parte senza aspettare l'allestimento fisico)

1. **DWG → solidi 3D** dell'allestimento: protocollo render invariato (bbox reali, codici dai
   MLEADER, checkpoint volumi approvato da Matteo in AutoCAD prima di spendere crediti).
2. **Render Manus per ambiente**: 8–10 "viste eroe" ad **altezza occhio 1,60 m**, una per
   ambiente (salone → cucina → lavanderia → bagno ospiti → ufficio → cameretta →
   bagno master → camera master: l'ordine di visita della demo). Collaudo standard ±10%.
3. **[Opz.] Vista → panorama** con Skybox AI (remix dall'immagine collaudata).
4. **Marble**: UN MONDO PER AMBIENTE, 8 in tutto (non l'intero camion in un colpo — stessa
   filosofia dei giri sui singoli mobili). Con Pro c'è l'espansione scena per allargare dopo.
5. **Collaudo camminata** (v. §5) prima di mostrare qualunque cosa.
6. **Pagina tour**: mondo incorporato (splat 500k) o link Marble + tappe per zona + schede
   prodotto con le misure VERE dai DXF + contatti. Interfaccia = quella della demo
   (`DINO_CHIESA_truck/demo_camminata.html`: joystick/WASD, tappe numerate, schede ⓘ).
7. **Distribuzione**: QR su fiancata/portellone, link in preventivi, mail, fiere.

## 5. Collaudo della camminata (nuova checklist, si somma a quello dei render)

1. **Scala percepita** ad altezza occhio: porte ~2 m, piani lavabo ~0,85 m, corridoio credibile.
2. **Conteggio moduli per parete** contro la spec (né mobili in più né in meno).
3. **Oggetti inventati** fuori dall'inquadratura di partenza: giro completo a 360° in ogni zona.
4. **Leggibilità insegne/loghi** (niente scritte "alla AI").
5. **Fluidità su telefono** di fascia media con lo splat 500k; se soffre → fallback tour 360°.
6. Esito e crediti nella `SPEC_COLLAUDO.md` della zona, come per i render.
   Regola invariata: **occhio del falegname > collaudo AI**.

## 6. Fase 2 — camion reale allestito

- Mezza giornata di riprese: X5 su asta, vano illuminato, video 360° lento per zona.
- Scaniverse/Splatica → splat fotografico → stessa pagina tour (si sostituisce la sorgente).
- Le stesse riprese sono B-roll per i social + confronto "progetto → realizzato".
- Il tour è marketing, NON tavola tecnica: in pagina la dicitura "ambientazione indicativa";
  le misure contrattuali restano su DXF/preventivo.

## 6-bis. Tour video completo (prodotto il 02/09/2026)

`TOUR_APPARTAMENTO_DINO_CHIESA.mp4` — 1:05, 720p24, stile Abitativo: copertina DINO CHIESA,
8 ambienti dai render FINALE 26-A011 (Portale → Ingresso → Parete porta → Parete TV →
Cucina → Lavanderia → Libreria ufficio → Bagno), etichette per stanza (PNG+overlay:
il build ffmpeg di imageio NON ha drawtext), dissolvenze xfade 0,6 s, chiusura con QR
alla demo camminabile. Clip: Veo 3.1 Fast 8 s/720p dai FINALE (prompt "slow dolly" +
anti-invenzioni), ~0,70 €/clip → tour ≈ 5 €. Collaudo fotogrammi finali: 7/8 promosse
piene; lavanderia promossa con riserva (chiusura su dettaglio mensola — eventualmente
rigenerare con carrellata più corta). Le clip Veo portano audio ambientale AAC nativo:
NON collaudabile da Claude (non ascolta) → consegna MUTA, musica da aggiungere a parte.
Limite quota Veo osservato: ~3 generazioni in parallelo, poi 429 → lavorare a coppie.

## 7. Stato commessa DINO CHIESA (02/09/2026)

| Voce | Stato |
|---|---|
| Studio tecnologie + piano | ✔ consegnato (artifact + questo protocollo) |
| Demo esperienza camminabile | ✔ consegnata (artifact + `DINO_CHIESA_truck/demo_camminata.html`) |
| Test Marble su render FINALE cucina | ✔ **ESEGUITO VIA API il 02/09/2026, tutto in automatico** (chiave API World Labs di Matteo + sandbox Composio come braccio, visto che la rete della sessione è chiusa). Mondo: https://marble.worldlabs.ai/world/cef33ce6-a424-4e43-8003-7f117c67139a — modello `marble-1.1`, seed 26011, costo 1.580 crediti (80 pano + 1.500 world), saldo residuo ~5.420. **Collaudo numerico: PROMOSSO** — riproiezione equirect→prospettiva: correlazione 0,701 col render a (fov 55°, yaw 0, pitch 0) = il centro del mondo È il render approvato; profilo fughe fascia basi 0,35 (struttura conservata, conteggio esatto frontali da confermare a occhio); tenuta laterale: un lato 106% della nitidezza del centro, +60° 77%, ±90° ~66-106%, retro 34-48% (riserva standard sul retro). Matteo ha fatto anche un mondo dall'app: https://marble.worldlabs.ai/world/9000c0fa-1f5f-4950-96be-e3dc452a9fff (non leggibile via API: app e API sono spazi separati). Brief Manus (`DINO_CHIESA_truck/BRIEF_MANUS_MARBLE.md`) resta come alternativa. |
| Disegni scocca camion (pianta aperta, sezione, assonometrie, gabbia pixel) | ✔ ESISTONO: allegati al task Manus `WSLtwCSEyoi5azfnCcFKP5` (scaricati e archiviati nel sandbox il 02/09) |
| Collegamento diretto Manus via Composio | ✔ verificato il 02/09/2026 (account "manus-render"; l'altro account collegato non si tocca) |
| Palcoscenico master del camion FOTOREALISTICO | ✔ **PROMOSSO il 03/09/2026 al giro 5** (tot. 654 crediti in 5 giri, task Manus `WSLtwCSEyoi5azfnCcFKP5`, tutto pilotato da Claude via Composio dopo i VAI). Percorso: g1 scocca vuota + g2 cucina → geometria PROMOSSA (parete 9,2 m: 962 px teoria = 962 misura; NCC 1,000); g3 (198 cr) luce ok ma zoccolo arancione + vetrate opache; g4 (168 cr) zoccolo/vetrate/nitidezza ok ma soffitti antracite + texture grossa; g5 (118 cr) **tutte e 3 le correzioni entrate senza regressioni**: soffitti bianchi (46→164), texture fine (grana 3,0→1,79, spigoli netti), pavimento uniforme (193→223), zoccolo scuro ~79/80/74 col velo LED. La scena `.blend` salvata nel task è la BASE per piazzare gli altri ambienti (un giro per ambiente, stesso task) |
| Conferma degli 8 ambienti/tappe con Matteo | ☐ da fare sul disegno |
| Giri Manus per ambiente sul palcoscenico master + Marble Pro | ☐ ORA SBLOCCATO (palcoscenico promosso): un giro per ambiente al VAI (~100–200 cr l'uno), servono i disegni/misure degli altri 7 ambienti (o il DWG dell'allestimento) |
| Ricetta unica `/commessa-media` ("l'exe": cartella → inventario → menu con costi → produzione con collaudo) | ✔ consegnata e collaudata il 02/09/2026: 6 prove su 2 commesse finte (bagno hotel completo + cabina senza pianta) — **17/17 criteri con la ricetta** vs 15/17 senza, ~45% più veloce, ~40% meno gettoni; si attiva da sola descrivendo una cartella commessa. Skill in `.claude/skills/commessa-media/` + `AVVIA_COMMESSA.bat` + `COME_AVVIARE_UNA_COMMESSA.md`. I due errori del "senza": nessun menu di scelta e misure ipotizzate nelle tavole — esattamente ciò che la ricetta vieta. |
| Quadro lavori con le spunte per Matteo | ✔ pagina viva: https://claude.ai/code/artifact/e4322eb6-6d18-4c85-9c34-1c84061939f1 (aggiornarla a ogni passo) + PDF procedura (3 pag.: giro completo, cosa dà Matteo, requisiti precisi DXF/STP) consegnato in chat il 02/09 |

## 8. Come si riparte (per la prossima sessione Claude)

1. Leggere questo protocollo e il `PROTOCOLLO_RENDER_MANUS.md` (le regole di brief/collaudo valgono).
   Per lavorare una commessa usare la skill `/commessa-media` (si carica da sola dal repo).
2. Chiedere a Matteo: esito del test Marble Free + DWG dell'allestimento.
3. Fase 1 dal punto in cui è ferma la tabella §7; aggiornare la tabella a ogni passo.
4. Per l'interfaccia della pagina definitiva partire dalla demo in `DINO_CHIESA_truck/`.
