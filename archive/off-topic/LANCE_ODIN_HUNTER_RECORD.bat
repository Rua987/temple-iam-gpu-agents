@echo off
chcp 65001 >nul
title ODIN HUNTER - Record Session

echo.
echo ================================================================
echo.
echo    ODIN HUNTER - RECORD SESSION
echo.
echo    Enregistre: sessions\odin_hunter_YYYYMMDD_HHMMSS\
echo    - events.jsonl
echo    - frames\ (si active)
echo.
echo ================================================================
echo.
echo   Duree ?
echo.
echo   [5] 5 min  [15] 15 min  [30] 30 min  [60] 1h  [1h] 1h  [0] Custom
echo.
set /p choice="Choix: "

if "%choice%"=="5" set minutes=5
if "%choice%"=="15" set minutes=15
if "%choice%"=="30" set minutes=30
if "%choice%"=="60" set minutes=60
if /I "%choice%"=="1h" set minutes=60
if "%choice%"=="0" (
    set /p minutes="Nombre de minutes: "
)
REM Tolérant: si l'utilisateur tape "a60" / "60min" / "min60" on extrait le nombre
if not defined minutes (
  for /f "usebackq delims=" %%m in (`powershell -NoProfile -Command "$m=[regex]::Match('%choice%','\d+').Value; if($m){$m}else{''}"`) do set minutes=%%m
)

if not defined minutes set minutes=15

echo.
echo   Frames (screenshots) ?
echo   [1] Oui (frames)  [0] Non (events only)
set /p frames="Choix: "

set noframes=
if "%frames%"=="0" set noframes=--no-frames

cd /d "%~dp0agents\odin_vision"
C:\Users\admin\miniconda3\python.exe odin_hunter.py --minutes %minutes% --aggression 3 --vision-distance --tactics learned --safe-heal --record-session %noframes%

pause


