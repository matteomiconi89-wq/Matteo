# -*- coding: utf-8 -*-
"""Sweep di validazione INCROCIATA: genera un mobile alla larghezza di un ALTRO esemplare
della stessa taglia e confronta col reale. Verifica anche gli identity (donatore=se stesso)."""
import os, subprocess
BASE = r"C:\Users\User\Desktop\CLAUDE\mobili_parametrici"
FC = r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe"
S17 = r"C:\Users\User\Dropbox\STEFANO\Matteo\ExtraOrdinario\21032\Set_17_18"
S19 = r"C:\Users\User\Dropbox\STEFANO\Matteo\ExtraOrdinario\21032\SET_19_20_21_22"

CASI = [
 # (tipo, W, donatore, riferimento reale, etichetta)
 ('J-03.01', 1339, 'Set19/21032_M07_J-03_01.stp',  S19+r'\21032_C108_J-03_01.stp',  'M07->C108 (stessa W, camere diverse)'),
 ('J-03.01', 1499, 'Set19/21032_C107_J-03_01.stp', S19+r'\21032_M06_J-03_01.stp',   'C107->1499 vs M06'),
 ('J-03.01', 1579, 'Set17/Set_17_A203_J-03.01.stp', S17+r'\Set_18_A110_J-03.01.stp','A203->1579 vs A110'),
 ('J-03.01', 1586, 'Set18/Set_18_A110_J-03.01.stp', S19+r'\21032_M08_J-03_01.stp',  'A110->1586 vs M08'),
 ('J-03.16', 1724, 'Set19/21032_C101-102_J-03_16_bis.stp', S17+r'\Set_18_A105_J-03.16.stp', 'C101-102->1724 vs A105'),
 ('J-03.16', 1770, 'Set18/Set_18_A105_J-03.16.stp', S19+r'\21032_C110_J-03_16.stp', 'A105->1770 vs C110'),
 ('J-03.16', 1804, 'Set19/21032_C110_J-03_16.stp',  S19+r'\21032_C204_J-03_16.stp', 'C110->1804 vs C204'),
 ('J-03.16', 1851, 'Set19/21032_C204_J-03_16.stp',  S17+r'\Set_17_A107_J-03.16.stp','C204->1851 vs A107'),
 ('J-03.02', 2100, 'Set17/Set_17_B207_J-03.02.stp', S17+r'\Set_17_B208_J-03.02.stp','B207->2100 vs B208'),
 ('J-03.02', 2672, 'Set19/21032_B302_J-03_02_quat.stp', S17+r'\Set_18_B202_J-03.02_bis.stp','B302->2672 vs B202'),
]

for tipo, W, donor, rif, eti in CASI:
    gen = os.path.join(BASE, f'xc_{tipo.replace("J-03.","")}_{W}.stp')
    env = dict(os.environ, GEN_TIPO=tipo, GEN_W=str(W), GEN_DONOR=donor, GEN_OUT=gen)
    r1 = subprocess.run([FC, os.path.join(BASE, 'genera2.py')], env=env, capture_output=True, text=True)
    err = [l for l in r1.stdout.splitlines()
           if 'Exception' in l or l.strip().startswith('*** ')]
    if err or not os.path.exists(gen):
        print(f"[GEN-ERR] {eti}: {err[:1]}")
        continue
    env2 = dict(os.environ, VAL_GEN=gen, VAL_RIF=rif)
    r2 = subprocess.run([FC, os.path.join(BASE, 'valida.py')], env=env2, capture_output=True, text=True)
    tot = [l for l in r2.stdout.splitlines() if l.startswith('TOTALE')]
    diffs = [l for l in r2.stdout.splitlines() if l.startswith('DIFF')]
    print(f"== {eti}")
    print("   " + (tot[0] if tot else 'NO OUTPUT'))
    for d in diffs:
        print("   " + d.strip())
