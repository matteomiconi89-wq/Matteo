# Pipeline API e trappole note (collaudate il 02/09/2026, commessa DINO CHIESA)

Leggere questo file prima di eseguire mondi Marble, clip Veo o catture headless.
Sono i dettagli che costano ore se riscoperti da zero.

## Mappa di rete (sessione Claude remota)

- RAGGIUNGIBILI in sessione: `generativelanguage.googleapis.com` (Veo!), github,
  raw.githubusercontent.com, registry.npmjs.org, pypi.org.
- BLOCCATI in sessione (403 dal proxy, sembra un errore del server ma non lo è):
  `*.worldlabs.ai`, `cdnjs`, `jsdelivr`, `dl./previews.dropboxusercontent.com`.
- Conseguenza: **Veo si chiama direttamente dalla sessione; Marble serve un braccio
  esterno con internet vera** (es. sandbox Composio `COMPOSIO_REMOTE_BASH_TOOL`).
- Sandbox Composio: timeout reale ~60 s per cella (spezzare i passi), output max
  ~30 KB (troncare), il sandbox viene RICICLATO tra riconnessioni → ricreare ogni
  volta chiavi (`~/.wlt_key`) e file. Verificare sempre `hostname` prima di fidarsi
  di file lasciati in giro.
- Nei browser dei clienti (artifact) cdnjs funziona normalmente: il blocco è solo
  della sessione.

## Veo 3.1 (Gemini API) — clip video da render

- Endpoint: `POST https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-fast-generate-preview:predictLongRunning`
- Header: `x-goog-api-key: <GEMINI_API_KEY>` · body:
  `{"instances":[{"prompt":"...","image":{"bytesBase64Encoded":"...","mimeType":"image/png"}}],
    "parameters":{"aspectRatio":"16:9","resolution":"720p","durationSeconds":8,"negativePrompt":"..."}}`
- Polling: `GET v1beta/{operation.name}` finché `done`; il video sta in
  `response.generateVideoResponse.generatedSamples[0].video.uri` → scaricare con lo
  stesso header chiave.
- SERVE fatturazione attiva sul progetto Google (senza: 429 RESOURCE_EXHAUSTED
  anche alla prima richiesta).
- Quota osservata: **~3 generazioni in parallelo, la 4ª prende 429** → lavorare a
  coppie da 2, su 429 riprovare dopo ~25 s. ~45 s a clip. Costo ~0,70 €/clip
  (fast 720p 8 s); `veo-3.1-generate-preview` = qualità piena, costa di più.
- Le clip portano audio AAC nativo non collaudabile → in montaggio si butta (`-an`).
- Modelli video Composio (`GEMINI_GENERATE_VIDEOS`) risultavano RESTRICTED → usare
  REST diretto con la chiave dell'utente.

## Marble / World Labs API — mondi camminabili

- Base: `https://api.worldlabs.ai/marble/v1` · header `WLT-Api-Key: <chiave>`.
- Flusso: `POST media-assets:prepare_upload` → PUT del PNG sull'URL firmato →
  `POST worlds:generate` (modello `marble-1.1`; `permission {"public":false,
  "allow_id_access":true}`; `seed` fisso per riproducibilità) → polling
  `GET operations/{id}` → `GET worlds/{id}` → `world_marble_url` (link navigabile),
  `assets.imagery.pano_url` (panorama equirettangolare), splat `.spz` 500k/150k/100k.
- Costo ~1.580 crediti/mondo (80 pano + 1.500 world); piano free = 7.000 crediti
  API. **Crediti app e crediti API sono spazi separati** (i mondi fatti nell'app
  non si leggono via API e viceversa). L'API può andare in overage fatturato →
  controllare `credits` prima di ogni giro, una generazione per volta.
- `worlds:list` in GET risponde "Method Not Allowed": non serve, tenere gli id.

## Collaudo numerico di un mondo Marble

- Confronto diretto pano↔render NON vale (proiezioni diverse: NCC ~0,2 anche
  quando è giusto). Prima riproiettare l'equirettangolare in prospettiva
  (proiezione gnomonica) a fov ~55°, yaw/pitch 0, POI correlare col render.
- Soglia di promozione: correlazione ≥ ~0,6 al centro (il punto di partenza del
  mondo DEVE essere il render approvato). Test collaudato: 0,701 = PROMOSSO.
- Completare con: profilo fughe sulla fascia delle basi (conteggio frontali),
  nitidezza laterale vs centro (retro sempre più debole: riserva standard).
- Script pronto: `scripts/collaudo_marble.py`.

## Dropbox (per dare i render ai bracci esterni)

- `download_link` (MCP) = link MONOUSO, vita ~900 s: generarlo un attimo prima
  dell'uso; se il braccio lo sbaglia una volta, è consumato → rigenerare.
- I link condivisi `scl` (copy_link_url) servono HTML a curl anonimo: NON usarli
  per download macchina; vanno bene solo per umani/browser.

## Cattura headless (chromium) della demo three.js

- Copia di cattura dedicata (`demo_capture.html`): three.js LOCALE (r128 da
  raw.githubusercontent.com, i CDN sono bloccati), riga Google Fonts RIMOSSA
  (altrimenti il caricamento si pianta).
- `--virtual-time-budget`: con SwiftShader ogni frame rAF costa tempo vero →
  usare 600–700, non migliaia; timeout shell abbondante.
- Banda morta costante di **87 px** in fondo allo screenshot → catturare ad
  altezza H+87 e ritagliare con PIL.
- `--proxy-server="http://127.0.0.1:9"` fa fallire all'istante ogni richiesta
  esterna residua (niente attese).
- Ganci della copia di cattura: `?vista=N` (tappa N), `?cam=x,z,tx,tz[,pitch]`,
  `?film=1` (percorso automatico), `?porte=1` (ante aperte).
- Film via Playwright: registra a ~1/5 della velocità (dt tappato) → correggere
  con `setpts=PTS/5,fps=30`.

## Montaggio (imageio-ffmpeg)

- Il binario ffmpeg di `imageio-ffmpeg` **NON ha il filtro drawtext** → i titoli
  si fanno come PNG RGBA con PIL (font DejaVu) e si applicano con `overlay` +
  `enable='between(t,0.6,7.4)'`.
- Catena di dissolvenze xfade: l'offset cresce di `durata_clip - 0,6` a ogni
  passo (0,6 s = durata dissolvenza). Audio: niente (`-an`).
- Script pronto: `scripts/monta_tour.py` (card, targhette, xfade, QR in coda).

## Igiene chiavi (repo pubblico!)

- Chiavi SOLO da: chat dell'utente → variabile d'ambiente / file effimero
  (`~/.gem_key`, `~/.wlt_key`). Mai in argv visibili nei log condivisi, mai in
  commit/artifact/brief. Gli script di questa skill leggono da
  `GEMINI_API_KEY` / `WLT_API_KEY` o dai file sopra.
- A fine progetto: far rigenerare le chiavi all'utente.
