@echo off
chcp 65001 >nul
title AVVIA COMMESSA - Claude
echo ============================================
echo   AVVIA COMMESSA  (pianta + STP -^> media)
echo ============================================
echo.

rem --- serve Claude Code installato sul PC ---
where claude >nul 2>nul
if errorlevel 1 (
  echo Claude Code non e' installato su questo PC.
  echo Installa da:  https://claude.com/claude-code
  echo Poi rilancia questo file.
  echo.
  pause
  exit /b 1
)

rem --- la skill si auto-installa a livello utente (prima volta) ---
set "SORG=%~dp0.claude\skills\commessa-media"
set "DEST=%USERPROFILE%\.claude\skills\commessa-media"
if exist "%SORG%\SKILL.md" (
  robocopy "%SORG%" "%DEST%" /e /njh /njs /ndl /nc /ns >nul
)

rem --- cartella commessa: trascinata sul file, oppure chiesta ---
if "%~1"=="" (
  set /p CARTELLA=Trascina qui la cartella della commessa e premi Invio (o incolla il percorso):
) else (
  set "CARTELLA=%~1"
)
set "CARTELLA=%CARTELLA:"=%"
if not exist "%CARTELLA%\" (
  echo La cartella "%CARTELLA%" non esiste. Controlla il percorso.
  pause
  exit /b 1
)

cd /d "%CARTELLA%"
echo.
echo Avvio Claude sulla commessa: %CARTELLA%
echo (fara' l'inventario e ti chiedera' cosa vuoi tirare fuori)
echo.
claude "/commessa-media Cartella commessa: %CARTELLA% - fai l'inventario e chiedimi cosa produrre."
pause
