# -*- coding: utf-8 -*-
"""Riassunto della ricognizione: struttura oggetti per file, radici etichette, compound."""
import json
import os
import re
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(BASE, "ricognizione.json"), encoding="utf-8"))

for k, v in d.items():
    if "error" in v:
        print(f"{k}: ERRORE {v['error'][:100]}")
        continue
    objs = v["oggetti"]
    con_solidi = [o for o in objs if o.get("n_solidi")]
    multi = [o for o in con_solidi if o["n_solidi"] > 1]
    senza = [o for o in objs if not o.get("n_solidi")]
    print(f"=== {k}: {len(objs)} oggetti | {len(con_solidi)} con solidi | {len(multi)} compound | {len(senza)} senza shape ===")
    roots = Counter(re.sub(r"\d+$", "", o["label"]).strip("_ ") for o in con_solidi)
    print("   radici:", ", ".join(f"{r}x{n}" for r, n in roots.most_common(15)))
    for o in multi[:8]:
        print(f"   COMPOUND {o['label']!r} n_sol={o['n_solidi']} dims={o.get('dims')}")
    if senza:
        tipi = Counter(o["tipo"] for o in senza)
        print("   senza shape:", dict(tipi))
    print()
