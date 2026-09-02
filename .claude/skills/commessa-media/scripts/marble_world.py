#!/usr/bin/env python3
"""Mondo Marble (World Labs) da un render collaudato, via API — zero mani.

Uso (da una macchina che raggiunge api.worldlabs.ai — la sessione Claude remota
NON ci arriva: usare il sandbox Composio o un PC normale):

    WLT_API_KEY=... python3 marble_world.py render.png esito.json [seed]

Scrive in esito.json: world_id, world_marble_url (link navigabile), pano_url,
splat .spz nelle tre densita'. Costo ~1.580 crediti/mondo (piano free 7.000);
crediti APP e API sono separati; possibile overage fatturato -> UNA generazione
per volta e saldo controllato prima. Chiave: env WLT_API_KEY o ~/.wlt_key.
"""
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

BASE = 'https://api.worldlabs.ai/marble/v1'


def chiave():
    k = os.environ.get('WLT_API_KEY', '').strip()
    if not k:
        p = Path.home() / '.wlt_key'
        if p.exists():
            k = p.read_text().strip()
    if not k:
        sys.exit('Manca la chiave: esporta WLT_API_KEY o scrivi ~/.wlt_key')
    return k


def chiama(metodo, percorso, dati, k):
    r = urllib.request.Request(f'{BASE}/{percorso}', method=metodo,
                               data=json.dumps(dati).encode() if dati is not None else None,
                               headers={'WLT-Api-Key': k, 'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(r, timeout=60).read())


def main(png, esito, seed=26011):
    k = chiave()
    prep = chiama('POST', 'media-assets:prepare_upload', {'file_name': Path(png).name}, k)
    up = urllib.request.Request(prep['upload_url'], method='PUT', data=Path(png).read_bytes(),
                                headers={'Content-Type': 'image/png'})
    urllib.request.urlopen(up, timeout=300).read()
    print('render caricato')

    gen = chiama('POST', 'worlds:generate', {
        'model': os.environ.get('MARBLE_MODEL', 'marble-1.1'),
        'world_prompt': {'type': 'single_image', 'image': {'media_asset_id': prep['media_asset']['id']}},
        'permission': {'public': False, 'allow_id_access': True},
        'seed': int(seed)}, k)
    op = gen['operation_id'] if 'operation_id' in gen else gen['id']
    print('generazione avviata:', op)

    t0 = time.time()
    while time.time() - t0 < 900:
        st = chiama('GET', f'operations/{op}', None, k)
        if st.get('done'):
            if 'error' in st:
                sys.exit(f'ERRORE Marble: {json.dumps(st["error"])[:300]}')
            wid = st['response']['id'] if 'response' in st else st['metadata']['world_id']
            mondo = chiama('GET', f'worlds/{wid}', None, k)
            Path(esito).write_text(json.dumps(mondo, indent=1))
            print('MONDO PRONTO:', mondo.get('world_marble_url'))
            print('pano:', mondo.get('assets', {}).get('imagery', {}).get('pano_url', '?')[:120])
            print(f'dettagli completi in {esito} — ora il collaudo: collaudo_marble.py')
            return
        time.sleep(15)
    sys.exit(f'TIMEOUT dopo 900 s (operazione {op}: riprendibile con GET operations/{op})')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], *(sys.argv[3:4] or []))
