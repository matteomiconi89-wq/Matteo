# -*- coding: utf-8 -*-
"""
Genera i file audio della chiamata numeri con voci NEURALI Microsoft (edge-tts).
Crea, per ogni voce e per ogni tipo (A/B), un MP3 per numero:
    voce/Isabella/A_12.mp3  ->  "A 12. Pronto per il ritiro."
    voce/Elsa/B_7.mp3       ->  "B 7. Pronto per il ritiro."

- Serve internet SOLO per generare (una volta). I file poi suonano OFFLINE.
- Si puo' rilanciare: salta i file gia' creati (resume).

Uso:   py genera_voci.py
"""
import asyncio, os, sys
import edge_tts

# ===================== CONFIGURAZIONE =====================
BASE   = r"C:\Users\User\Desktop\CLAUDE\comande_sagra\voce"
VOICES = {                              # cartella : voce neurale
    "Isabella": "it-IT-IsabellaNeural",
    "Elsa":     "it-IT-ElsaNeural",
}
TIPI   = {"A": "A", "B": "B"}           # chiave file : parola pronunciata
NMIN, NMAX = 1, 999                     # intervallo numeri
FRASE  = "{t}, {n}. Pronto per il ritiro."   # virgola = piccola pausa dopo la lettera

CONCORRENZA = 6                         # download in parallelo (non alzare troppo)
TENTATIVI   = 4                         # ritenta in caso di errore di rete
# =========================================================

sem = asyncio.Semaphore(CONCORRENZA)
fatti = 0
totale = 0
falliti = []

async def genera_uno(voice_id, out_path, text):
    global fatti
    # resume: salta i file gia' presenti e non vuoti
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        fatti += 1
        if fatti % 100 == 0: print(f"  {fatti}/{totale}", flush=True)
        return
    async with sem:
        for tentativo in range(TENTATIVI):
            try:
                await edge_tts.Communicate(text, voice_id).save(out_path)
                if os.path.getsize(out_path) > 0:
                    fatti += 1
                    if fatti % 100 == 0: print(f"  {fatti}/{totale}", flush=True)
                    return
            except Exception as e:
                await asyncio.sleep(1.5 * (tentativo + 1))
        falliti.append(out_path)
        print("  FALLITO:", out_path, file=sys.stderr, flush=True)

async def main():
    global totale
    compiti = []
    for vshort, vid in VOICES.items():
        for tkey, tlab in TIPI.items():
            d = os.path.join(BASE, vshort)
            os.makedirs(d, exist_ok=True)
            for n in range(NMIN, NMAX + 1):
                text = FRASE.format(t=tlab, n=n)
                out  = os.path.join(d, f"{tkey}_{n}.mp3")
                compiti.append(genera_uno(vid, out, text))
    totale = len(compiti)
    print(f"Genero {totale} file audio in {BASE} ...", flush=True)
    await asyncio.gather(*compiti)
    print(f"FINITO. Creati/presenti: {fatti}/{totale}. Falliti: {len(falliti)}", flush=True)
    if falliti:
        print("Rilancia lo script per ritentare i falliti.", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
