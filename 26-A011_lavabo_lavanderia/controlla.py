#!/usr/bin/env python3
"""Collaudo geometrico del modello a volumi:
1) compenetrazioni fra solidi (volume di intersezione > 0)
2) confronto quote con le misure lette dal CAD
3) riepilogo pezzi per gruppo
"""
import json
import sys
from itertools import combinations

path = sys.argv[1] if len(sys.argv) > 1 else "volumi.json"
data = json.load(open(path, encoding="utf-8"))
boxes = data["box"]

def inter(a, b):
    dx = min(a["x1"], b["x1"]) - max(a["x0"], b["x0"])
    dy = min(a["y1"], b["y1"]) - max(a["y0"], b["y0"])
    dz = min(a["z1"], b["z1"]) - max(a["z0"], b["z0"])
    if dx > 0 and dy > 0 and dz > 0:
        return dx, dy, dz
    return None

print(f"=== COLLAUDO {path} — {len(boxes)} solidi ===\n")

# 1) compenetrazioni
print("--- 1. COMPENETRAZIONI ---")
bad = 0
for a, b in combinations(boxes, 2):
    ov = inter(a, b)
    if ov:
        bad += 1
        vol = ov[0] * ov[1] * ov[2] / 1000.0
        print(f"  ✗ {a['nome']}  ∩  {b['nome']}")
        print(f"      sovrapposizione {ov[0]:.1f} x {ov[1]:.1f} x {ov[2]:.1f} mm  (vol {vol:.1f} cm³)")
if not bad:
    print("  ✓ nessuna compenetrazione: tutti i solidi sono disgiunti")
else:
    print(f"\n  TOTALE: {bad} coppie compenetrate")

# 2) spessori sospetti
print("\n--- 2. SPESSORI E DIMENSIONI ---")
for b in boxes:
    dx, dy, dz = b["x1"]-b["x0"], b["y1"]-b["y0"], b["z1"]-b["z0"]
    if min(dx, dy, dz) <= 0:
        print(f"  ✗ {b['nome']}: dimensione nulla o negativa {dx}x{dy}x{dz}")

# 3) ingombri
xs = [c for b in boxes for c in (b["x0"], b["x1"])]
ys = [c for b in boxes for c in (b["y0"], b["y1"])]
zs = [c for b in boxes for c in (b["z0"], b["z1"])]
print(f"\n--- 3. INGOMBRO COMPLESSIVO ---")
print(f"  X (larghezza)  {min(xs):.0f} .. {max(xs):.0f}   = {max(xs)-min(xs):.0f} mm")
print(f"  Y (profondità) {min(ys):.0f} .. {max(ys):.0f}   = {max(ys)-min(ys):.0f} mm")
print(f"  Z (altezza)    {min(zs):.0f} .. {max(zs):.0f}   = {max(zs)-min(zs):.0f} mm")

mob = [b for b in boxes if not b["nome"].startswith(("PAR_", "VETRO_"))]
mx = [c for b in mob for c in (b["x0"], b["x1"])]
my = [c for b in mob for c in (b["y0"], b["y1"])]
mz = [c for b in mob for c in (b["z0"], b["z1"])]
print(f"\n  SOLO MOBILE+LAVABO: L {max(mx)-min(mx):.0f} x P {max(my)-min(my):.0f} x H {max(mz)-min(mz):.0f}")
carc = [b for b in mob if b["nome"].startswith(("CARC_", "ANTA_", "TOP_", "ZOCC", "GOLA", "RIPIANO", "SCHIENALE", "TRAVERSO", "LED_", "PIEDINO"))]
cz = [c for b in carc for c in (b["z0"], b["z1"])]
cy = [c for b in carc for c in (b["y0"], b["y1"])]
print(f"  SOLO MOBILE (senza lavabo/rubinetteria): P {max(cy)-min(cy):.0f} x H {max(cz)-min(cz):.0f}")

# 4) verifica contro misure attese dal CAD
print("\n--- 4. VERIFICA CONTRO IL CAD ---")
attesi = [
    ("fronte mobile (anta) a Y", 466, max(b["y1"] for b in boxes if b["nome"].startswith("ANTA_"))),
    ("retro carcassa a Y", 66, min(b["y0"] for b in boxes if b["nome"].startswith("CARC_"))),
    ("profondità mobile", 400, max(b["y1"] for b in boxes if b["nome"].startswith("ANTA_")) - min(b["y0"] for b in boxes if b["nome"].startswith("CARC_"))),
    ("larghezza mobile", 1173, max(b["x1"] for b in boxes if b["nome"].startswith("CARC_")) - min(b["x0"] for b in boxes if b["nome"].startswith("CARC_"))),
    ("piano finito a Z", 670, max(b["z1"] for b in boxes if b["nome"].startswith("TOP_"))),
    ("anta: base Z", 92, min(b["z0"] for b in boxes if b["nome"].startswith("ANTA_"))),
    ("anta: cima Z", 580, max(b["z1"] for b in boxes if b["nome"].startswith("ANTA_"))),
    ("ripiani a Z", 328.5, min(b["z0"] for b in boxes if b["nome"].startswith("RIPIANO"))),
    ("lavabo: bordo alto Z", 920, max(b["z1"] for b in boxes if b["nome"].startswith("LAVABO"))),
    ("parete: altezza totale", 2215, max(b["z1"] for b in boxes if b["nome"].startswith("PAR_"))),
]
for nome, atteso, trovato in attesi:
    ok = abs(atteso - trovato) < 0.6
    print(f"  {'✓' if ok else '✗'} {nome}: atteso {atteso}, modello {trovato:.1f}")

# 5) gola di presa
ante_top = max(b["z1"] for b in boxes if b["nome"].startswith("ANTA_"))
bordo = [b for b in boxes if b["nome"] == "TOP_bordo_fronte_h60"][0]
print(f"\n  → GOLA DI PRESA: da Z {ante_top:.0f} (cima anta) a Z {bordo['z0']:.0f} (bordo top) = {bordo['z0']-ante_top:.0f} mm di apertura")

# 6) elenco per gruppo
print("\n--- 5. PEZZI PER GRUPPO ---")
gruppi = {}
for b in boxes:
    gruppi.setdefault(b["layer"], []).append(b)
for lay in sorted(gruppi):
    print(f"\n  {lay} ({len(gruppi[lay])})")
    for b in sorted(gruppi[lay], key=lambda b: (b["z0"], b["x0"])):
        dx, dy, dz = b["x1"]-b["x0"], b["y1"]-b["y0"], b["z1"]-b["z0"]
        print(f"    {b['nome']:38s} {dx:6.1f} x {dy:6.1f} x {dz:6.1f}   @ X{b['x0']:.0f} Y{b['y0']:.0f} Z{b['z0']:.0f}")
