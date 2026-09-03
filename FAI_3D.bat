@echo off
rem ============================================================
rem  FAI_3D — doppio click (o trascina qui sopra i DWG/DXF)
rem  Apre Claude Code nel repo: Claude sa gia' cosa fare
rem  (le istruzioni permanenti stanno in CLAUDE.md).
rem ============================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"

where claude >nul 2>nul
if errorlevel 1 (
    echo Claude Code non e' ancora installato su questo PC.
    echo Apri PowerShell e incolla questa riga, poi rilancia FAI_3D:
    echo.
    echo     irm https://claude.ai/install.ps1 ^| iex
    echo.
    pause
    exit /b 1
)

if not exist "CONSEGNA_2D" mkdir "CONSEGNA_2D"
if not exist "USCITA_3D" mkdir "USCITA_3D"

set PRESI=
:raccogli
if "%~1"=="" goto lancia
copy /y "%~1" "CONSEGNA_2D\" >nul
echo Preso: %~nx1
set PRESI=!PRESI! %~nx1
shift
goto raccogli

:lancia
if "%PRESI%"=="" (
    claude "FAI_3D: lavora i file 2D in CONSEGNA_2D e consegna in USCITA_3D come da CLAUDE.md. Dimmi subito i tempi stimati."
) else (
    claude "FAI_3D: ho appena messo in CONSEGNA_2D questi file:%PRESI%. Lavorali e consegna in USCITA_3D come da CLAUDE.md. Dimmi subito i tempi stimati."
)

start "" explorer "USCITA_3D"
