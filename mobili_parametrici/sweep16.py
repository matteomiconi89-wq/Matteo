# -*- coding: utf-8 -*-
import os, subprocess
BASE = r"C:\Users\User\Desktop\CLAUDE\mobili_parametrici"
FC = r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe"
S17 = r"C:\Users\User\Dropbox\STEFANO\Matteo\ExtraOrdinario\21032\Set_17_18"
S19 = r"C:\Users\User\Dropbox\STEFANO\Matteo\ExtraOrdinario\21032\SET_19_20_21_22"
CASI = [
 (1709, os.path.join(S19,'21032_C101-102_J-03_16_bis.stp'), 'Set19/21032_C101-102_J-03_16_bis.stp'),
 (1724, os.path.join(S17,'Set_18_A105_J-03.16.stp'),        'Set18/Set_18_A105_J-03.16.stp'),
 (1770, os.path.join(S19,'21032_C110_J-03_16.stp'),         'Set19/21032_C110_J-03_16.stp'),
 (1804, os.path.join(S19,'21032_C204_J-03_16.stp'),         'Set19/21032_C204_J-03_16.stp'),
 (1851, os.path.join(S17,'Set_17_A107_J-03.16.stp'),        'Set17/Set_17_A107_J-03.16.stp'),
]
for W, rif, donor in CASI:
    gen = os.path.join(BASE, f'sw16_{W}.stp')
    env = dict(os.environ, GEN_TIPO='J-03.16', GEN_W=str(W), GEN_DONOR=donor, GEN_OUT=gen)
    subprocess.run([FC, os.path.join(BASE,'genera2.py')], env=env, capture_output=True)
    env2 = dict(os.environ, VAL_GEN=gen, VAL_RIF=rif)
    out = subprocess.run([FC, os.path.join(BASE,'valida.py')], env=env2, capture_output=True, text=True)
    tot = [l for l in out.stdout.splitlines() if l.startswith('TOTALE')]
    diff = [l for l in out.stdout.splitlines() if l.startswith('DIFF')]
    print(f"W={W} {os.path.basename(rif):32s} | {tot[0] if tot else 'NO OUT'}")
    for d in diff: print("     "+d.strip())
