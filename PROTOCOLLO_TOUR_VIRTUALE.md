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

## 7. Stato commessa DINO CHIESA (02/09/2026)

| Voce | Stato |
|---|---|
| Studio tecnologie + piano | ✔ consegnato (artifact + questo protocollo) |
| Demo esperienza camminabile | ✔ consegnata (artifact + `DINO_CHIESA_truck/demo_camminata.html`) |
| Test Marble Free su render FINALE 26-A011 (es. cucina truck) | ☐ da fare — costo zero |
| DWG allestimento camion | ☐ da ricevere da Matteo |
| Conferma degli 8 ambienti/tappe con Matteo | ☐ da fare sul disegno |
| Primo giro Manus "viste 1,60 m" + Marble Pro | ☐ dopo l'ok sul test |

## 8. Come si riparte (per la prossima sessione Claude)

1. Leggere questo protocollo e il `PROTOCOLLO_RENDER_MANUS.md` (le regole di brief/collaudo valgono).
2. Chiedere a Matteo: esito del test Marble Free + DWG dell'allestimento.
3. Fase 1 dal punto in cui è ferma la tabella §7; aggiornare la tabella a ogni passo.
4. Per l'interfaccia della pagina definitiva partire dalla demo in `DINO_CHIESA_truck/`.
