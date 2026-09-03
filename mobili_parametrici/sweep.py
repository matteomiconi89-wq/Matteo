# -*- coding: utf-8 -*-
# Sweep di validazione: rigenera ogni esemplare J-03.01 (donatore = se stesso) e confronta.
import os, subprocess, re
BASE = r"C:\Users\User\Desktop\CLAUDE\mobili_parametrici"
FC = r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe"
S17 = r"C:\Users\User\Dropbox\STEFANO\Matteo\ExtraOrdinario\21032\Set_17_18"
S19 = r"C:\Users\User\Dropbox\STEFANO\Matteo\ExtraOrdinario\21032\SET_19_20_21_22"
CASI = [
 ('1339c', 1339, os.path.join(S19, '21032_C108_J-03_01.stp'), 'Set19/21032_C108_J-03_01.stp'),
 ('1339m', 1339, os.path.join(S19, '21032_M07_J-03_01.stp'), 'Set19/21032_M07_J-03_01.stp'),
 ('1429',  1429, os.path.join(S19, '21032_C107_J-03_01.stp'), 'Set19/21032_C107_J-03_01.stp'),
 ('1452',  1452, os.path.join(S17, 'Set_17_A211_J-03.01.stp'), 'Set17/Set_17_A211_J-03.01.stp'),
 ('1499',  1499, os.path.join(S19, '21032_M06_J-03_01.stp'), 'Set19/21032_M06_J-03_01.stp'),
 ('1547',  1547, os.path.join(S17, 'Set_17_A203_J-03.01.stp'), 'Set17/Set_17_A203_J-03.01.stp'),
 ('1579',  1579, os.path.join(S17, 'Set_18_A110_J-03.01.stp'), 'Set18/Set_18_A110_J-03.01.stp'),
 ('1586',  1586, os.path.join(S19, '21032_M08_J-03_01.stp'), 'Set19/21032_M08_J-03_01.stp'),
 ('1601',  1601, os.path.join(S17, 'Set_17_A103_J-03.01.stp'), 'Set17/Set_17_A103_J-03.01.stp'),
]
righe = []
for key, W, rif, donor in CASI:
    gen = os.path.join(BASE, f'sw_{key}.stp')
    env = dict(os.environ, GEN_W=str(W), GEN_DONOR=donor, GEN_OUT=gen)
    subprocess.run([FC, os.path.join(BASE, 'genera.py')], env=env, capture_output=True)
    env2 = dict(os.environ, VAL_GEN=gen, VAL_RIF=rif)
    out = subprocess.run([FC, os.path.join(BASE, 'valida.py')], env=env2, capture_output=True, text=True)
    tot = [l for l in out.stdout.splitlines() if l.startswith('TOTALE')]
    diff = [l for l in out.stdout.splitlines() if l.startswith('DIFF')]
    cass = [l for l in out.stdout.splitlines() if 'Cassetto' in l]
    line = tot[0] if tot else 'NO OUTPUT'
    print(f"{key:6s} W={W} {os.path.basename(rif):30s} | {line}")
    for d in diff:
        print("        " + d.strip())
print("\nFatto.")
