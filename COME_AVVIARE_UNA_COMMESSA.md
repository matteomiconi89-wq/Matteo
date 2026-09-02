# Come avviare una commessa (l'"exe")

Un solo gesto: indichi la cartella della commessa (dentro: pianta DWG/DXF e i
disegni STP dei mobili — materiali e ferramenta Claude li legge DENTRO gli STP;
distinte separate solo se vuoi) e Claude fa il resto — inventario, menu di
scelta, produzione, collaudo, consegna.

## I tre modi (equivalenti)

**1. Qui nella chat di Claude (il piu' semplice)** — scrivi ad esempio:

> Commessa 26-B003, cartella `...percorso...`: fammi i render e il PDF

oppure solo "ecco la cartella della commessa" — parte da sola.

**2. Doppio click sul PC (Windows)** — `AVVIA_COMMESSA.bat` nella radice di questo
repo: trascina la cartella della commessa sopra il file `.bat` (o fai doppio click
e incolla il percorso). Serve Claude Code installato sul PC
(https://claude.com/claude-code); la prima volta il .bat installa da solo la skill
a livello utente, cosi' funziona su qualunque cartella del PC.

**3. Comando esplicito** — in una sessione Claude qualsiasi dentro questo repo:
`/commessa-media <percorso cartella>`.

## Cosa succede dopo

1. **Inventario** — Claude elenca cosa ha trovato (pianta, STP, distinte) e cosa
   manca. Non inventa niente: se manca la pianta, te la chiede.
2. **Menu** — scegli cosa tirare fuori (per certi clienti il tour e' inutile):
   render · viste · demo 3D camminabile · mondo Marble · tour video · clip social
   · PDF dossier. Ogni voce col suo costo vivo.
3. **Piano** — passi e cifre nero su bianco; niente parte a pagamento senza il tuo
   **VAI**.
4. **Produzione + collaudo** — ogni prodotto passa il suo collaudo (righello sui
   pixel, checklist camminata, fotogrammi) prima di arrivarti.
5. **Consegna** — file in chat, link/QR per i clienti, stato commessa aggiornato.

## Cose oneste da sapere

- Il "cervello" e' Claude: non e' un `.exe` chiuso, e' un comando che apre Claude
  gia' istruito. Il vantaggio: si aggiorna migliorando il file della skill, senza
  ricompilare nulla.
- Le **chiavi API** (Google/Veo, World Labs/Marble) le incolli in chat quando
  servono: non stanno mai nel repo (che e' pubblico) ne' nei file consegnati.
  A fine progetto vanno rigenerate.
- Anche i **render Manus** vanno da soli: Claude pilota Manus direttamente
  (collegamento Composio "manus-render"), crea i task, segue i giri e collauda.
  Come Marble, Veo, montaggio, PDF e demo. Tu approvi e basta.
- Le regole complete stanno in `.claude/skills/commessa-media/SKILL.md` (+ i due
  protocolli storici `PROTOCOLLO_RENDER_MANUS.md` e `PROTOCOLLO_TOUR_VIRTUALE.md`).
