# BRIEF PER MANUS — Mobile lavabo lavanderia 26-A011 — giro 1

## Come si usa

1. Allega a Manus **queste 4 immagini** (te le ho mandate in chat, stanno anche nella cartella del repo):
   - `gabbia_pixel.png` — la gabbia di inquadratura con le quote in pixel
   - `lavabo_volumi_2_mobile_chiuso.png` — assonometria dei volumi, ante chiuse (àncora geometrica)
   - `lavabo_volumi_3_senza_ante.png` — assonometria senza ante (interni)
   - `lavabo_volumi_5_fianco.png` — vista di fianco (profondità e sbalzi)
2. Incolla il prompt qui sotto.
3. Mandami i render: li collaudo col righello sui pixel e ti dico se passano.

**Attenzione ai link Dropbox monouso**: se ne sbagli uno, Manus li consuma tutti e vanno rigenerati.

---

## PROMPT (copia da qui)

```
Photorealistic interior render of a custom laundry-room washbasin cabinet, built to exact
millimetre dimensions. Attached: a pixel framing grid and three axonometric views of the real
3D volumes extracted from the CAD file. THE ATTACHED GEOMETRY IS THE TRUTH: do not invent,
add or remove any element.

OUTPUT: 2400x1350 px, 16:9, one view, eye-level frontal camera slightly to the left,
lens ~35mm, no distortion.

=== EXACT GEOMETRY (millimetres) ===
Cabinet body: 1173 wide x 400 deep x 670 high to the finished worktop.
Left bay: OPEN NICHE, clear width 432, with EXACTLY ONE shelf at mid height (329 from floor).
Central vertical divider 18 thick.
Right bay: TWO doors only, each 357 wide x 488 high, 18 thick, with a 3 mm gap between them.
NO drawers anywhere. NO third door. NO extra shelves.

=== THE DEFINING DETAIL: RECESSED FINGER PULL ===
ABSOLUTELY NO HANDLES, NO KNOBS, NO VISIBLE HARDWARE, NO KEYHOLES anywhere.
The doors are opened through a 30 mm continuous OPEN GAP running the full width immediately
above the doors (between door top at 580 and worktop edge at 610). Inside that gap the back
surface is mirrored, and a warm LED strip is recessed under the worktop, washing light down
into the gap. This dark horizontal shadow line across the whole front is the signature of
the piece: it must read clearly.

=== BASE ===
NO continuous plinth flush with the front. The plinth is SET BACK 98 mm from the front face,
95 mm high, standing on feet: the cabinet reads as resting on the floor with a deep shadow
recess underneath, and a second recessed LED strip washes the floor from under the base.

=== WORKTOP AND BASIN ===
Worktop 18 thick with a 60 mm high front edge band, finished top at 670 from floor.
Countertop washbasin GALASSIA MEG 11 PRO, 603 x 379, 250 high, centred on the worktop depth,
positioned to the RIGHT (its left edge at 499 from the cabinet's left side), rim at 920 from floor.
Tall single-lever mixer tap, slim 40 mm column, standing on the worktop to the LEFT of the basin,
spout reaching right over the bowl, spout at 1100 from floor.

=== MATERIALS ===
- Carcase, niche interior, shelves, back panels: matt textured laminate, warm greige ("CERA"),
  same finish as the rest of this project.
- Doors, worktop, front edge band and plinth: matt anthracite laminate, absolutely no gloss.
- Back of the finger-pull gap: mirror.
- Basin: matt white ceramic. Tap: matt black.
- Wall behind: mineral-look wall panel, warm off-white.

=== PROPORTIONS TO RESPECT (they will be measured on the pixels) ===
- cabinet width / worktop height = 1173 / 670 = 1.75
- open niche / single door width = 432 / 357 = 1.21
- doors+divider / niche = 723 / 432 = 1.67
- basin width = 51% of cabinet width
- the cabinet occupies 48% of the frame width, its base sits at 92% of frame height

=== SCENE ===
Same environment, lighting and floor as the other renders of this project: calm daylight from
the left, soft shadows, matt floor. Clean laundry-room mood, no clutter, no text, no watermark,
no people. Photographic realism, no CGI plastic look.

=== CHECK BEFORE YOU ANSWER (report your own measurements in pixels) ===
1. Count the doors: exactly 2. Count the shelves: exactly 1 in the niche, 1 in the closed bay.
2. Any handle, knob or keyhole visible? There must be none.
3. Is the 30 mm gap above the doors continuous across the whole width?
4. Is the plinth set back with a shadow gap, not flush?
5. Measure and report: cabinet width in px, worktop height in px, their ratio (target 1.75),
   niche width / door width (target 1.21).
```

---

## Giro 2 e successivi — regole

- **Massimo 3-4 correzioni per volta.** Con otto insieme entrano tutte ma qualcos'altro peggiora.
- **Sempre la lista anti-regressione**: elencare cosa è già giusto e va tenuto identico.
- Se una correzione non entra dopo 2 tentativi → giro dedicato a quella sola, con ancore spaziali
  ("la fascia scura sta sopra le ante, tra il piano e i frontali").
- **Le proporzioni globali non si chiedono a Manus**: se il rapporto è fuori, si corregge in post
  con la matematica (costo zero), non con un altro giro.
