@echo off
chcp 65001 > nul
title ODIN SMART COMBAT

echo.
echo ================================================================
echo.
echo    ODIN SMART COMBAT - Combat Intelligent
echo.
echo    - Cible les ennemis AVANT d'attaquer
echo    - Bloque avec le bouclier
echo    - Esquive intelligemment
echo    - Heal automatique
echo.
echo ================================================================
echo.
echo   Choisis ta strategie :
echo.
echo   [1] BALANCED   - Equilibre attaque/defense
echo   [2] AGGRESSIVE - Plus d'attaques, moins de defense
echo   [3] DEFENSIVE  - Prudent, beaucoup de blocks
echo   [4] BOSS       - Ultra prudent pour les boss
echo.

set /p strat_choice=Choix: 

if "%strat_choice%"=="1" set strategy=balanced
if "%strat_choice%"=="2" set strategy=aggressive
if "%strat_choice%"=="3" set strategy=defensive
if "%strat_choice%"=="4" set strategy=boss

echo.
echo   Combien de minutes ?
echo.
echo   [5]  5 minutes
echo   [10] 10 minutes
echo   [30] 30 minutes
echo   [60] 1 heure
echo   [0]  Personnalise
echo.

set /p time_choice=Choix: 

if "%time_choice%"=="5" set minutes=5
if "%time_choice%"=="10" set minutes=10
if "%time_choice%"=="30" set minutes=30
if "%time_choice%"=="60" set minutes=60
if "%time_choice%"=="0" (
    set /p minutes=Nombre de minutes: 
)

echo.
echo   Vitesse de combat ?
echo.
echo   [1] Lent (10 cycles/min)
echo   [2] Normal (15 cycles/min)
echo   [3] Rapide (20 cycles/min)
echo.

set /p speed_choice=Choix: 

if "%speed_choice%"=="1" set speed=10
if "%speed_choice%"=="2" set speed=15
if "%speed_choice%"=="3" set speed=20

echo.
echo   Strategie: %strategy%
echo   Duree: %minutes% minute(s)
echo   Vitesse: %speed% cycles/min
echo.

cd /d "%~dp0agents\odin_vision"

C:\Users\admin\miniconda3\python.exe smart_combat.py --strategy %strategy% --minutes %minutes% --speed %speed%

echo.
pause

