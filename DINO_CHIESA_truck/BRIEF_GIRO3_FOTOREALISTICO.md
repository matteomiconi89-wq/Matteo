# BRIEF GIRO 3 — palcoscenico camion FOTOREALISTICO (task Manus WSLtwCSEyoi5azfnCcFKP5)

> Inviato da Claude direttamente via Composio (account manus-render) il 02/09/2026,
> dopo il VAI di Matteo. Giri 1-2 collaudati: geometria PROMOSSA, resa maquette.
> Questo giro cambia SOLO materiali/luce/qualità di resa: la geometria è congelata.

```
ROUND 3 — same task, same saved scene, same camera: now MAKE IT PHOTOREAL.

Load your round-2 scene (master_stage_kitchen_right_closed.blend). If your session
no longer has it, the attachments carry: (1) that .blend, (2) render_v10_01_chiuso.png
(the approved kitchen, closed fronts = the definitive look), (3) render_v11_02_aperto.png.

GEOMETRY IS FROZEN. Do not move, resize, add or remove ANY object. Camera identical:
2400x1350, horizontal FOV 72 deg, vanishing point at exact frame centre (1200, 675).
This round is ONLY materials, lighting and render quality. Target: a photograph,
not a maquette. Match the mood, light temperature, realism and floor of the two
approved renders.

=== MATERIALS — KITCHEN (exact render_v10 look) ===
- Fronts (columns, 4 base fronts, narrow pantry, 4 flap wall units): matt warm
  greige "CERA" laminate, handle-free, subtle texture, NO gloss.
- The continuous GROOVE line (gola): one dark horizontal recess running across
  the whole front, columns included, with a warm LED glow inside. It must read
  clearly as one continuous line.
- Worktop + upstand: white solid surface, matte, seamless.
- Plinth: dark, RECESSED, with LED strip washing the floor; visible shadow gap.
- Under the 4 flap wall units: warm LED strip washing light down on the worktop.
- Oven: built-in, dark glass front, at eye level in the second tall column.
- Kitchen window band (in the kitchen stretch only): slim dark frame, daylight.

=== MATERIALS — SHELL ===
- Floor: SAME matt floor material as the approved renders, continuous, subtle
  realistic reflections (matte, not shiny).
- Walls, partition, pillar bands, parapets: warm off-white matt panels with
  faint panel joints (no decoration).
- Ceilings: matt white. Rooflights: soft luminous panels ~4000K, gentle even
  glow, no visible bulbs, realistic light falloff on the ceiling around them.
- Glazed bands: clear glass, bright neutral daylight outside (white-out, no
  landscape), soft daylight entering and grazing the floor; slim dark frames.

=== RENDER ===
- Physically plausible global illumination, soft shadows, photographic exposure,
  slight warm balance like render_v10. High-quality render with denoise: no noise,
  no clay look, no pure untextured surfaces. No people, no text, no watermark,
  no lens distortion.

=== CHECK BEFORE YOU ANSWER — measure ON THE DELIVERED IMAGE, not in the scene ===
1. Vanishing point still at (1200, 675)? Geometry edges identical to round 2?
2. Recount ON THE IMAGE: 2 tall columns + EXACTLY 4 equal base fronts + 1 narrow
   pantry + 4 flap wall units.
3. Groove line: one continuous dark line across the whole kitchen front? yes/no.
4. Plinth: dark, recessed, LED, visible shadow gap? yes/no.
5. Photorealism: name the floor material you rendered and where its highlights
   fall; list any surface left pure untextured white (there must be none except
   ceiling paint).
6. Left bay: unchanged and empty.

Deliver: final 2400x1350 PNG + updated .blend + the pixel self-check report.
```

## Esito (collaudo Claude 02/09/2026 sera)

- Giro eseguito in ~10 min, 198 crediti (totale task 368). Consegnati PNG +
  scena `.blend` fotorealistica + report.
- **Geometria**: invariata (scena congelata confermata; prospettiva e moduli al
  posto giusto; auto-report Manus: 0 modifiche su 86 oggetti).
- **Resa**: PROGRESSO — luce calda, caduta di luce realistica intorno ai
  lucernari, LED caldo sotto i pensili, pavimento con riflessi morbidi. MA non
  ancora fotografico: superfici sfocate/ammorbidite (denoise pesante), materiali
  senza grana leggibile.
- **2 REGRESSIONI di spec**: (1) lo zoccolo è diventato una fascia ARANCIONE
  accesa invece di zoccolo scuro incassato con LED discreto; (2) le fasce
  vetrate sono diventate pannelli blu-grigi OPACHI senza luce diurna che entra.
- **Verdetto: NON promosso** → giro 4 con 4 correzioni mirate + lista
  anti-regressione (sotto), in attesa del VAI di Matteo (~100–200 crediti).

## Esito GIRO 4 (collaudo Claude 02/09/2026, sera tardi)

- 168 crediti (totale task 536). Consegnati PNG + `.blend` + report.
- **Le 4 correzioni sono entrate**: ① zoccolo ora scuro incassato (mia misura
  RGB ~79/80/74, pixel arancioni da 24.722 a 1.629 = solo il velo LED legittimo);
  ② vetrate con telaio scuro e luce che entra; ③ nitidezza RADDOPPIATA
  (laplaciano 2,35→4,90, niente più sfocature); ④ fronte cucina leggibile con
  forno a vetro scuro in colonna.
- **MA nuova regressione**: il SOFFITTO (corridoio + campate + fasce dei
  gradini) è diventato ANTRACITE SCURO — la spec dice bianco opaco. E la
  texture è ESAGERATA: pareti/frontali a puntinato grosso tipo intonaco,
  non grana fine da laminato CERA; pavimento troppo chiazzato.
- **Verdetto: NON promosso** → giro 5 con 3 correzioni, al VAI (~150–200 cr).

### Correzioni per il giro 5
1. SOFFITTI di nuovo BIANCO OPACO (corridoio, campate, fasce dei gradini) —
   l'antracite resta SOLO allo zoccolo; lucernari invariati.
2. Texture ridotta del ~70%: grana FINE da laminato sui frontali CERA, pareti
   quasi lisce con giunti appena accennati — niente puntinato da intonaco.
3. Pavimento: chiaro e uniforme come nei render approvati (meno chiazze).
ANTI-REGRESSIONE: tenere zoccolo scuro incassato + LED, vetrate con luce,
nitidezza piena, gola, geometria/camera congelate, campata sinistra vuota.

### Correzioni per il giro 4 (max 4, regola dei giri) — ESEGUITE
1. Zoccolo: antracite scuro, incassato, ombra netta; LED solo come velo caldo
   sul pavimento — via la fascia arancione.
2. Vetrate: vetro chiaro con luce diurna neutra brillante (bianco fuori) che
   ENTRA e radente sul pavimento — non pannelli opachi.
3. Nitidezza fotografica ovunque (niente sfocature/DOF), micro-texture leggibile
   su frontali greige CERA e pavimento.
4. Gola: la linea scura continua deve leggersi su tutto il fronte.
ANTI-REGRESSIONE: camera/geometria congelate, mood caldo, caduta luce
lucernari, LED sotto pensili, campata sinistra vuota, conteggi moduli.
