# BRIEF PER MANUS — Test Marble cucina truck (DINO CHIESA) — giro 1

> Obiettivo: trasformare il render FINALE della cucina 26-A011 in una stanza 3D camminabile
> con Marble (World Labs) e riportare link + screenshot + auto-collaudo. Manus fa TUTTO
> col suo browser; Matteo non fa nulla, tranne un eventuale login una tantum (takeover).

## Come si usa

1. Incolla in Manus il prompt qui sotto (blocco unico). Non serve allegare nulla:
   il render lo scarica Manus dal link Dropbox che c'è dentro.
2. Se Marble chiede un login/verifica, Manus si ferma e ti chiede il **takeover del browser**:
   fai l'accesso una volta sola (2 minuti) e ridagli il controllo. Dal giro 2 non servirà più.
3. Quando Manus consegna (link del mondo + 8 screenshot + report), incolla tutto nella chat
   di Claude: collaudo io voce per voce sulla SPEC e do il verdetto con la mossa successiva.

Tempi attesi: Manus ~10–15 min (generazione Marble inclusa) · collaudo Claude ~10 min dal report.

Nota link: quello nel prompt è un **link condiviso normale** di Dropbox (non monouso):
se la richiesta fallisce si può riprovare senza rigenerare niente.

---

## PROMPT (copia da qui)

```
MISSIONE (operazione browser, nessuna generazione di immagini tua): trasformare un render
fotorealistico in un mondo 3D navigabile con Marble di World Labs e riportare il risultato
con un auto-collaudo. Il render è la VERITÀ: tu non devi creare né modificare immagini.

=== PASSI ===
1. Scarica questo file PNG (render 4K di una cucina, ~5 MB), link Dropbox diretto:
   https://www.dropbox.com/scl/fi/lojjy3e3x9wxyonlfa49o/render_v10_01_chiuso.png?rlkey=jv66wtbo11cb2g8hs5xs61vyr&dl=1
2. Vai su https://marble.worldlabs.ai . Serve il piano FREE (4 mondi/mese): NON attivare
   piani a pagamento, NON inserire dati di pagamento. Se serve un login o c'è un captcha:
   FERMATI e chiedi all'utente il takeover del browser, poi riprendi tu.
3. Crea un nuovo mondo con input IMMAGINE caricando il PNG scaricato. Se c'è un campo di
   testo opzionale scrivi solo: "modern kitchen interior, photorealistic". Non aggiungere altro.
4. Avvia la generazione e aspetta il mondo completo (anteprima ~30 s, completo pochi minuti).
5. Esplora il mondo e cattura 8 SCREENSHOT nitidi a schermo pieno, numerati 01–08:
   01 punto di partenza (deve coincidere col render)
   02 due passi in avanti, al centro della cucina
   03 da vicino: le due colonne alte a sinistra (frigo + forno)
   04 da vicino: le basi sotto la finestra, inquadrando TUTTI i frontali
   05 zoom in basso: zoccolo scuro arretrato con luce LED
   06 ruotato di 90° a sinistra rispetto alla partenza
   07 ruotato di 180° (quello che c'è alle spalle della camera)
   08 dall'angolo opposto della stanza guardando verso la cucina
6. AUTO-COLLAUDO — misura tu sugli screenshot e riporta voce per voce (✓/✗ + nota):
   a. Frontali delle basi sotto la finestra: devono essere ESATTAMENTE 4 (né 5 né 6). Contali.
   b. Ante a ribalta in alto sopra la finestra: ESATTAMENTE 4, larghezze simili. Contale.
   c. Gola (scanalatura orizzontale scura): UNA linea continua alla stessa quota su tutto
      il fronte, colonne comprese.
   d. Colonna dispensa all'estrema destra: STRETTA, circa metà di un'anta normale.
   e. Giunto tra le due colonne di sinistra: fessura verticale sottile "come una matita".
   f. Zoccolo: scuro, ARRETRATO rispetto alle ante, con striscia LED; le ante non toccano terra.
   g. Finestra sopra le basi: resta una finestra con telaio scuro sottile (non un pensile).
   h. Top e alzatina: bianchi, lisci, senza venature.
   i. OGGETTI INVENTATI: elenca ogni cosa visibile negli screenshot 06/07/08 che NON esiste
      nel render di partenza, e giudica se è credibile o no.
   j. TENUTA: a quanti "passi" dal punto di partenza l'immagine inizia a sfaldarsi o sfocarsi?
7. Attiva la condivisione del mondo e copia il LINK pubblico.

=== CONSEGNA (in un unico messaggio) ===
- Link del mondo Marble
- Gli 8 screenshot come file allegati, numerati
- Il report dell'auto-collaudo (voci a–j)
- Eventuali intoppi (login, captcha, limiti del piano free)

=== REGOLE ===
- Non creare account con email inventate: solo takeover dell'utente per il login.
- Non spendere denaro né crediti a pagamento di alcun servizio.
- Se un passaggio fallisce: riprova UNA volta, poi fermati e riporta l'errore con screenshot.
- Non generare né ritoccare immagini: il PNG scaricato si carica com'è.
```

---

## Giro 2 e successivi — regole

- **Se il collaudo dice "promosso"** → si passa agli 8 ambienti del camion: stesso brief,
  cambia solo il link del render (uno per ambiente), previa attivazione di Marble Pro
  ($35/mese, diritti commerciali) fatta da Matteo.
- **Se "promosso con riserva"** (lati/retro deboli) → giro 2 con più copertura:
  prima il render si allarga a panorama 360° (Skybox AI di Blockade Labs, remix
  dall'immagine), poi si dà a Marble il panorama invece della singola vista.
- **Se "bocciato"** → piano B: tour a tappe 360° (Pannellum/Kuula) con gli stessi render,
  e fotorealismo totale rimandato alla scansione del camion vero (Fase 2).
- Vale sempre la regola dei render: **massimo 3–4 correzioni per giro**, lista
  anti-regressione, e l'occhio del falegname batte il collaudo AI.

## Riferimenti

- Spec sorgente: `SPEC_COLLAUDO.md` in `/STEFANO/Matteo/RENDER_MANUS/26-A011_cucina/`
  (coppia FINALE: `render_v10_01_chiuso` approvato Matteo + `render_v11_02_aperto`).
- Secondo test opzionale (stessa procedura): `render_v11_02_aperto.png`, link Dropbox:
  https://www.dropbox.com/scl/fi/gzhxqfqacqky2kung330e/render_v11_02_aperto.png?rlkey=zn6nvlf1y6mg6wx1zflc34jh3&dl=1
- Kit e criteri di giudizio: https://claude.ai/code/artifact/06870770-7271-4bc0-ba65-44241ba8e157
- Protocollo generale: `PROTOCOLLO_TOUR_VIRTUALE.md` (radice del repo).
