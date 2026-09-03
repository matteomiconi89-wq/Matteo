# -*- coding: utf-8 -*-
# Compone una traccia originale 28 s (120 BPM) sincronizzata con le scene del reel
# e la unisce al video: REEL_01_armadio_2400_MUSICA.mp4

import os, wave, subprocess
import numpy as np

SR = 44100
DUR = 28.0
N = int(SR * DUR)
QUI = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(32)

bufL = np.zeros(N)
bufR = np.zeros(N)

def metti(suono, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= N: return
    s = suono[:N - i0] * gain
    a = (pan + 1) * np.pi / 4
    bufL[i0:i0 + len(s)] += s * np.cos(a)
    bufR[i0:i0 + len(s)] += s * np.sin(a)

def tempo(dur): return np.arange(int(dur * SR)) / SR

def kick():
    t = tempo(0.30)
    f = 46 + 110 * np.exp(-t * 22)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9)

def hat(aperto=False):
    t = tempo(0.16 if aperto else 0.06)
    n = rng.standard_normal(len(t))
    n = np.diff(n, prepend=0.0)
    return n * np.exp(-t * (16 if aperto else 65)) * 0.7

def clap():
    t = tempo(0.22)
    n = rng.standard_normal(len(t))
    n = np.diff(n, prepend=0.0)
    env = np.exp(-t * 22) * (1 + 0.6 * np.sin(2 * np.pi * 95 * t))
    return n * env

def basso(f, dur, dec=4.0):
    t = tempo(dur)
    s = np.sin(2*np.pi*f*t) + 0.35*np.sin(4*np.pi*f*t) + 0.12*np.sin(6*np.pi*f*t)
    att = np.minimum(t / 0.008, 1)
    return s * att * np.exp(-t * dec)

def pluck(f):
    t = tempo(0.45)
    s = np.sin(2*np.pi*f*t) + 0.3*np.sin(4*np.pi*f*t)
    return s * np.exp(-t * 9)

def pad(freqs, dur):
    t = tempo(dur)
    s = sum(np.sin(2*np.pi*f*t + i) for i, f in enumerate(freqs)) / len(freqs)
    att = np.minimum(t / 0.7, 1)
    rel = np.minimum((dur - t) / 0.8, 1)
    return s * att * np.clip(rel, 0, 1)

def riser(dur):
    t = tempo(dur)
    n = rng.standard_normal(len(t))
    n = np.diff(n, prepend=0.0)
    return n * (t / dur) ** 2.2

def boom():
    t = tempo(1.4)
    f = 40 + 30 * np.exp(-t * 6)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 2.2)

BEAT = 0.5
ACC = [55.00, 43.65, 65.41, 49.00]
def acc_bar(b): return ACC[b % 4]

# --- 0-6 s · Excel: minimale ---
for b in range(12):
    t0 = b * BEAT
    if b % 2 == 0:
        metti(kick(), t0, 0.45)
    metti(hat(), t0 + 0.25, 0.10, pan=-0.3)
for bar in range(3):
    metti(basso(acc_bar(bar), 1.6, dec=1.5), bar * 2.0, 0.30)
metti(riser(1.0), 5.0, 0.22)

# --- 6-16 s · generazione 3D + orbit: groove pieno ---
for b in range(12, 32):
    t0 = b * BEAT
    metti(kick(), t0, 0.85)
    metti(hat(), t0 + 0.25, 0.16, pan=-0.3)
    if b % 2 == 1:
        metti(clap(), t0, 0.30, pan=0.2)
    bar = b // 4
    for k in range(2):
        metti(basso(acc_bar(bar), 0.22), t0 + k * 0.25, 0.42)
for b in range(24, 32):
    t0 = b * BEAT
    bar = b // 4
    f0 = acc_bar(bar) * 4
    note = [f0, f0 * 1.5, f0 * 2]
    metti(pluck(note[b % 3]), t0 + 0.25, 0.20, pan=0.4)
metti(hat(True), 11.75, 0.20, pan=0.3)

# --- 16-20 s · Movento slow-mo: mezzo tempo ---
for b in range(32, 40, 4):
    metti(kick(), b * BEAT, 0.55)
for bar in range(8, 10):
    f = acc_bar(bar)
    metti(basso(f, 1.8, dec=1.2), bar * 2.0, 0.30)
metti(pad([220, 261.63, 329.63], 4.0), 16.0, 0.16)

# --- 20-25 s · armadio montato: groove pieno ---
for b in range(40, 50):
    t0 = b * BEAT
    metti(kick(), t0, 0.85)
    metti(hat(), t0 + 0.25, 0.16, pan=-0.3)
    if b % 2 == 1:
        metti(clap(), t0, 0.30, pan=0.2)
    bar = b // 4
    for k in range(2):
        metti(basso(acc_bar(bar), 0.22), t0 + k * 0.25, 0.42)
    f0 = acc_bar(bar) * 4
    metti(pluck([f0, f0 * 1.5, f0 * 2][b % 3]), t0 + 0.25, 0.18, pan=0.4)
metti(riser(1.0), 24.0, 0.25)

# --- 25-28 s · invito: colpo finale e coda ---
metti(boom(), 25.0, 0.8)
metti(clap(), 25.0, 0.35)
metti(pad([220, 261.63, 329.63, 440], 2.8), 25.1, 0.14)

mix = np.tanh(np.vstack([bufL, bufR]) * 1.1)
mix *= 0.95 / max(np.abs(mix).max(), 1e-9)
nfade = int(1.4 * SR)
mix[:, -nfade:] *= np.linspace(1, 0, nfade)
mix[:, :2205] *= np.linspace(0, 1, 2205)

wav_path = os.path.join(QUI, "musica_reel.wav")
dati = (mix.T * 32767).astype(np.int16)
with wave.open(wav_path, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(dati.tobytes())
print("traccia scritta:", wav_path)

import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
vid = os.path.join(QUI, "REEL_01_armadio_2400.mp4")
out = os.path.join(QUI, "REEL_01_armadio_2400_MUSICA.mp4")
subprocess.run([ff, "-y", "-i", vid, "-i", wav_path,
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-shortest", out], check=True, capture_output=True)
print("FATTO:", out)
