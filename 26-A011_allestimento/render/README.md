# Render animato — camera master

`render_camera_master.html` è il render navigabile della camera master: 182 solidi
presi dai modelli esecutivi (armadio e divisorio sono gli STEP di Matteo con i nomi
di distinta, testata-letto è ricostruita dal DWG del mobile contenitore).

Vano reale usato per il guscio: **3728 × 3562 × 2293 mm** (pavimento a quota 1395).

## Come si rigenera

```
python3 estrai_scena.py            # reinietta la geometria da ../arredo_geometry.json
python3 verifica_inquadrature.py   # controlla che le camere non attraversino i mobili
```

`verifica_inquadrature.py` esiste perché il vano è quasi tutto occupato: l'armadio
chiude la parete ingresso, la testata quella anteriore e il divisorio il lato living
tranne il varco della porta. Gli unici due settori da cui si vede davvero dentro
sono **la porta** e **il fianco che si allarga**: tutte e quattro le inquadrature
partono da lì, e lo script lo verifica al mm prima di pubblicare.

## Materiali

I materiali non sono inventati: sono i layer `F_...` del DWG, letti da
`pipeline/materiali_da_dwg.py` (che esplode i blocchi della pianta e confronta le
impronte con i pezzi 3D) e resi secondo `materiali_render.json`. Il DWG dice il
**tipo di pannello**, non il colore della finitura: quelli marcati `DA FISSARE`
aspettano ancora la scelta.

## Pacchetto per il render esterno

```
python3 esporta_manus.py     # -> manus/  GLB + OBJ + brief + inquadrature
```

Produce `manus/BRIEF_MANUS.md` con convenzione di coordinate, elenco materiali,
inquadrature verificate e vincoli del vano.
