@echo off
chcp 65001 >nul
title ODIN HUNTER - Exploration + Combat

echo.
echo ================================================================
echo.
echo    ODIN HUNTER - Mode Chasseur
echo.
echo    Explore FLUIDEMENT + Combat automatique
echo    Camera lente, virages progressifs
echo    Attaque quand ennemi detecte (Lock-On)
echo.
echo ================================================================
echo.
echo   Duree ?
echo.
echo   [15] 15 min  [30] 30 min  [60] 1h  [0] Custom
echo.
set /p choice="Choix: "

if "%choice%"=="15" set minutes=15
if "%choice%"=="30" set minutes=30
if "%choice%"=="60" set minutes=60
if "%choice%"=="0" (
    set /p minutes="Nombre de minutes: "
)

if not defined minutes set minutes=30

cd /d "%~dp0agents\odin_vision"
REM Aggression 3 = berserk max (demande user)
REM Vision-distance = gate melee-range avant gros combos (si Ollama + capture dispo)
REM Safe-heal = heal périodique en combat (berserk-safe)
C:\Users\admin\miniconda3\python.exe odin_hunter.py --minutes %minutes% --aggression 3 --vision-distance --tactics learned --safe-heal

pause

