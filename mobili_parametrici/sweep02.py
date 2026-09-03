import os, subprocess
BASE=r"C:\Users\User\Desktop\CLAUDE\mobili_parametrici"; FC=r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe"
S17=r"C:\Users\User\Dropbox\STEFANO\Matteo\ExtraOrdinario\21032\Set_17_18"; S19=r"C:\Users\User\Dropbox\STEFANO\Matteo\ExtraOrdinario\21032\SET_19_20_21_22"
CASI=[(1979,os.path.join(S17,'Set_17_B207_J-03.02.stp'),'Set17/Set_17_B207_J-03.02.stp'),
 (2100,os.path.join(S17,'Set_17_B208_J-03.02.stp'),'Set17/Set_17_B208_J-03.02.stp'),
 (2669,os.path.join(S19,'21032_A102_J-03_02_ter.stp'),'Set19/21032_A102_J-03_02_ter.stp'),
 (2670,os.path.join(S19,'21032_B302_J-03_02_quat.stp'),'Set19/21032_B302_J-03_02_quat.stp'),
 (2672,os.path.join(S17,'Set_18_B202_J-03.02_bis.stp'),'Set18/Set_18_B202_J-03.02_bis.stp')]
for W,rif,donor in CASI:
    gen=os.path.join(BASE,f'sw02_{W}.stp')
    subprocess.run([FC,os.path.join(BASE,'genera2.py')],env=dict(os.environ,GEN_TIPO='J-03.02',GEN_W=str(W),GEN_DONOR=donor,GEN_OUT=gen),capture_output=True)
    out=subprocess.run([FC,os.path.join(BASE,'valida.py')],env=dict(os.environ,VAL_GEN=gen,VAL_RIF=rif),capture_output=True,text=True)
    tot=[l for l in out.stdout.splitlines() if l.startswith('TOTALE')]
    diff=[l for l in out.stdout.splitlines() if l.startswith('DIFF')]
    print(f"W={W} {os.path.basename(rif):32s} | {tot[0] if tot else 'NO OUT'}")
    for d in diff: print("     "+d.strip())
