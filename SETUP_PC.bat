@echo off
rem ============================================================
rem  SETUP_PC — da lanciare UNA VOLTA sola sul PC di Matteo.
rem  Prepara tutto quello che serve a FAI_3D.bat.
rem ============================================================
cd /d "%~dp0"
echo.
echo == 1/3  Python e librerie CAD ==
where python >nul 2>nul
if errorlevel 1 (
    echo Python non trovato. Scaricalo da https://www.python.org/downloads/
    echo IMPORTANTE: durante l'installazione spunta "Add python.exe to PATH",
    echo poi rilancia questo SETUP_PC.
    pause
    exit /b 1
)
python -m pip install --upgrade pip
python -m pip install ezdxf numpy matplotlib cadquery
if errorlevel 1 (
    echo Installazione librerie fallita: rilancia SETUP_PC con la rete attiva.
    pause
    exit /b 1
)

echo.
echo == 2/3  Claude Code ==
where claude >nul 2>nul
if errorlevel 1 (
    echo Claude Code non e' installato. Apri PowerShell e incolla:
    echo.
    echo     irm https://claude.ai/install.ps1 ^| iex
    echo.
    echo Al primo avvio fai il login col tuo account Claude ^(si apre il browser^).
    echo Consigliato anche "Git for Windows" ^(https://git-scm.com/download/win^):
    echo cosi' Claude puo' usare i comandi bash sul PC.
) else (
    echo Claude Code: gia' installato.
)

echo.
echo == 3/3  (facoltativo) ODA File Converter ==
echo Serve solo per due comodita': leggere i DWG senza passare da AutoCAD
echo e far uscire il DWG 3D gia' pronto. Gratuito:
echo     https://www.opendesign.com/guestfiles/oda_file_converter
echo Dopo l'installazione aggiungi la sua cartella al PATH di Windows.
echo.
echo == Fatto. D'ora in poi usa FAI_3D.bat (doppio click o trascinaci i DWG). ==
pause
