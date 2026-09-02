# BRIEF PER MANUS — Scocca 26A011 / scena madre — giro 1

## Come si usa

Il lancio lo faccio io (Claude) via Composio appena la connessione Manus torna attiva
(API key da rigenerare). In manuale: allega a Manus **queste 5 immagini** + le 2 di scena, poi
incolla il prompt qui sotto.

1. `gabbia_pixel_scocca.png` — la gabbia di inquadratura: camera, punto di fuga e quote in pixel
2. `scocca_pianta_aperta.png` — pianta quotata (posizioni di vetrine, oblò, divisori)
3. `scocca_sezione.png` — sezione trasversale (tutte le altezze)
4. `scocca_assonometria_aperto.png` — volumi, lato ingresso (àncora geometrica)
5. `scocca_assonometria_aperto_retro.png` — volumi, lato cucina/retro
6. + 2 render approvati della commessa come riferimento scena (da Dropbox `26-A011_cucina`):
   `render_v10_01_chiuso.png`, `render_v11_02_aperto.png` — **link Dropbox monouso generati
   al momento del lancio** (se un link fallisce, si consumano tutti: rigenerarli).

Parametri task API: `task_mode: "agent"`, `agent_profile: "manus-1.6"`.

---

## PROMPT (copia da qui)

```
Photorealistic interior render of the EMPTY interior of a custom expandable exhibition
semi-trailer, OPEN configuration. This is the MASTER STAGE of the whole project: every future
furniture render will be placed inside this exact space, so geometry and proportions are the
entire job. Attached: a pixel framing cage (the mandatory camera), a dimensioned floor plan,
a cross section, and two axonometric views of the real CAD volumes. THE ATTACHED GEOMETRY IS
THE TRUTH: do not invent, add, move or remove anything. Also attached: two approved renders of
this project's furniture — reuse their scene mood, light temperature and floor material.

OUTPUT: 2400x1350 px, 16:9, ONE view only, matching the pixel cage EXACTLY:
one-point perspective down the length, camera 1.000 mm past the front interior wall, centred
on the width, eye 1.600 mm above the floor, horizontal FOV 72 deg (~24 mm full frame),
vanishing point in the exact frame centre (1200, 675). No people, no furniture, no text,
no watermark, no lens distortion.

=== THE SPACE (millimetres) ===
- Central corridor 2.390 wide, FLAT ceiling at 2.251 above the floor.
- BOTH long sides open onto shallow slide-out bays: left bay 1.152 deep, right bay 1.176 deep.
  Bay ceilings are LOWER and gently sloped: 2.151 at the corridor edge falling to 2.103 at the
  outer wall. So there are EXACTLY TWO ceiling steps (corridor high, bays lower), running the
  full visible length as clean straight lines to the vanishing point.
- Full open interior width wall-to-wall: 4.718.
- Outer bay walls: solid parapet up to +1.000, then a glazed band 647 high (sill at +1.000,
  glass head at +1.647), then solid up to the bay ceiling. Glazing only in the stretches shown
  on the plan; elsewhere the band is closed panel. Daylight comes from these bands.
- 4 rectangular rooflights visible, flush in the flat corridor ceiling, centred on the corridor
  axis, at the depths shown on the plan (the biggest is 1.292 long); they glow softly.
- At 9,2 m from the camera a full-height, full-width partition wall closes the corridor view.
  The two bays continue past it (their perspective lines keep going).
- Two fixed pillar bands interrupt the bays around 3 m from the camera (per plan): show them as
  short solid wall returns in each bay.
- Floor: ONE continuous level. No steps, no ramps, no wheel arches.

=== MATERIALS (stage defaults, same family as the attached approved renders) ===
- Floor: same matt floor as the approved renders.
- Walls, partition, pillar bands, bay parapets: warm off-white matt panels.
- Ceilings: matt white; rooflights = soft luminous panels, no visible bulbs.
- Glazed band: clear glass, bright neutral daylight outside, no landscape detail.

=== PROPORTIONS (they will be measured on the pixels) ===
- corridor ceiling height / corridor width = 2.251 / 2.390 = 0.94 (the corridor mouth is
  almost square)
- full width / corridor width = 4.718 / 2.390 = 1.97
- window sill line = 44% of corridor ceiling height; glazed band = 29% of it
- at 5 m depth the corridor is 789 px wide and 743 px tall (see the cage)
- a standing person (1.750) at mid-trailer would be 481 px tall — scale check only, do NOT
  render people

=== CHECK BEFORE YOU ANSWER (report your own pixel measurements) ===
1. Vanishing point: is it at (1200, 675)? Report where yours is.
2. Measure corridor width and ceiling height in px at ~5 m depth; report the ratio (target 0.94).
3. Count ceiling steps: exactly 2. Count rooflights: exactly 4 visible.
4. Is the window sill a single straight line receding to the VP on each side, starting at
   +1.000 scaled?
5. Any furniture, people, steps, wheel arches, text, watermark? There must be none.
```

---

## Giro 2 e successivi — regole (dal protocollo)

- **Massimo 3-4 correzioni per volta**, sempre con lista anti-regressione (cosa è già giusto
  e va tenuto identico).
- Correzione che non entra dopo 2 tentativi → giro single-fix con ancore spaziali
  ("il gradino di soffitto corre sopra il filo del corridoio, non a mezza baia").
- **Le proporzioni globali non si chiedono a Manus**: se il rapporto 0,94 esce ~0,90 si sistema
  in post con la matematica (costo zero).
- Collaudo su ogni candidato: righello sui pixel (ancore della SPEC_COLLAUDO), conteggi
  (2 gradini, 4 oblò), zoom sulle aree critiche (attacco soffitto/baia, davanzale) prima di
  promuovere.
