# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['step_dxf_definitivi.py'],
    pathex=[r'C:\Users\User\Desktop\CLAUDE\ConfrontoProgrammi',
            r'C:\Users\User\Desktop\CLAUDE\bom_exe',
            r'C:\Users\User\Desktop\CLAUDE\Dxf2Tlf',
            r'C:\Users\User\Desktop\CLAUDE\Dxf2Mpr',
            r'C:\Users\User\Desktop\CLAUDE\SchedePDF',
            r'C:\Users\User\Desktop\CLAUDE\Definitivi'],
    binaries=[],
    datas=[],
    hiddenimports=['acis_topo', 'confronta_file_unici_dxf', 'genera_sezionatura_cp_21032',
                   'dxf2tlf_masterwood', 'dxf2mpr_homag', 'inietta_3d', 'scheda_pdf',
                   'scheda_base_da_filiera', 'nesting_pannelli',
                   'win32gui', 'win32con', 'win32com.client',
                   'automazioni_excel_FINALE', 'tkinter', 'ordini_fornitori_pdf', 'riepilogo_costi'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FILIERA_21032',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

