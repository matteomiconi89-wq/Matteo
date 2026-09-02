#!/usr/bin/env python3
"""Clip Veo 3.1 da render collaudati, a lotti con gestione quota.

Uso:
    GEMINI_API_KEY=... python3 veo_clips.py lavori.json

lavori.json = lista di lavori:
[
  {"image": "render_cucina.png",
   "prompt": "Slow, smooth dolly-in ... keep every cabinet exactly as in the reference image; do not add or remove any furniture",
   "dest": "clip_cucina.mp4",
   "aspectRatio": "16:9",          // opzionale, default 16:9 (9:16 per social)
   "durationSeconds": 8,            // opzionale
   "negativePrompt": "people, text, watermark, warped geometry, extra cabinets, extra doors"
  }, ...
]

Regole imparate sul campo (02/09/2026):
- serve fatturazione attiva sul progetto Google, senza: 429 anche alla 1a richiesta;
- quota ~3 generazioni in parallelo -> si lavora a COPPIE, su 429 si riprova dopo 25 s;
- ~45 s a clip; l'audio nativo va scartato in montaggio (-an), non e' collaudabile.
La chiave NON si passa mai come argomento e non si stampa: env GEMINI_API_KEY o ~/.gem_key.
"""
import base64
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

BASE = 'https://generativelanguage.googleapis.com/v1beta'
MODEL = os.environ.get('VEO_MODEL', 'veo-3.1-fast-generate-preview')
NEG_DEFAULT = ('people, humans, text, letters, watermark, warped geometry, bending walls, '
               'extra cabinets, extra doors, changing furniture')


def chiave():
    k = os.environ.get('GEMINI_API_KEY', '').strip()
    if not k:
        p = Path.home() / '.gem_key'
        if p.exists():
            k = p.read_text().strip()
    if not k:
        sys.exit('Manca la chiave: esporta GEMINI_API_KEY o scrivi ~/.gem_key')
    return k


def _req(url, dati=None, k=None, timeout=60):
    corpo = json.dumps(dati).encode() if dati is not None else None
    r = urllib.request.Request(url, data=corpo, headers={
        'x-goog-api-key': k, 'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(r, timeout=timeout).read())


def avvia(lavoro, k):
    """Invia una generazione; torna il nome operazione o None su quota piena."""
    img = base64.b64encode(Path(lavoro['image']).read_bytes()).decode()
    mime = 'image/jpeg' if lavoro['image'].lower().endswith(('.jpg', '.jpeg')) else 'image/png'
    corpo = {
        'instances': [{'prompt': lavoro['prompt'],
                       'image': {'bytesBase64Encoded': img, 'mimeType': mime}}],
        'parameters': {'aspectRatio': lavoro.get('aspectRatio', '16:9'),
                       'resolution': lavoro.get('resolution', '720p'),
                       'durationSeconds': lavoro.get('durationSeconds', 8),
                       'negativePrompt': lavoro.get('negativePrompt', NEG_DEFAULT)}}
    try:
        return _req(f'{BASE}/models/{MODEL}:predictLongRunning', corpo, k)['name']
    except urllib.error.HTTPError as e:
        if e.code == 429:
            return None
        raise


def scarica(op, dest, k, budget=420):
    t0 = time.time()
    while time.time() - t0 < budget:
        d = _req(f'{BASE}/{op}', None, k, timeout=30)
        if d.get('done'):
            if 'error' in d:
                print(f'  {dest}: ERRORE {json.dumps(d["error"])[:180]}')
                return False
            uri = d['response']['generateVideoResponse']['generatedSamples'][0]['video']['uri']
            r = urllib.request.Request(uri, headers={'x-goog-api-key': k})
            Path(dest).write_bytes(urllib.request.urlopen(r, timeout=180).read())
            print(f'  {dest}: OK ({Path(dest).stat().st_size} byte, {time.time()-t0:.0f} s)')
            return True
        time.sleep(12)
    print(f'  {dest}: TIMEOUT dopo {budget} s (operazione: {op})')
    return False


def main(percorso_lavori):
    k = chiave()
    lavori = json.loads(Path(percorso_lavori).read_text())
    esiti = {}
    for i in range(0, len(lavori), 2):          # coppie: la quota regge ~3, noi stiamo a 2
        coppia, ops = lavori[i:i + 2], {}
        for lav in coppia:
            op = avvia(lav, k)
            while op is None:                    # 429: quota piena, si aspetta e si riprova
                print('  quota piena (429), riprovo tra 25 s...')
                time.sleep(25)
                op = avvia(lav, k)
            print(f'  inviata: {lav["dest"]}')
            ops[op] = lav['dest']
        for op, dest in ops.items():
            esiti[dest] = scarica(op, dest, k)
    ko = [d for d, ok in esiti.items() if not ok]
    print(f'\nFatte {len(esiti)-len(ko)}/{len(esiti)}' + (f' — MANCANO: {ko}' if ko else ' — tutte OK'))
    return 0 if not ko else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
