@echo off
chcp 65001 > nul
title ODIN ULTIMATE

echo.
echo ================================================================
echo.
echo    ODIN ULTIMATE - Le Guerrier Autonome Ultime
echo.
echo    - Detection automatique du jeu
echo    - Navigation intelligente
echo    - Combat adaptatif
echo    - Heal automatique
echo.
echo ================================================================
echo.
echo   Choisis ta strategie :
echo.
echo   [1] BALANCED   - Equilibre exploration/combat
echo   [2] AGGRESSIVE - Attaque en priorite
echo   [3] DEFENSIVE  - Prudent et reactif
echo   [4] EXPLORER   - Explore beaucoup, combat peu
echo.

set /p strat_choice=Choix: 

if "%strat_choice%"=="1" set strategy=balanced
if "%strat_choice%"=="2" set strategy=aggressive
if "%strat_choice%"=="3" set strategy=defensive
if "%strat_choice%"=="4" set strategy=explorer

echo.
echo   Duree de session ?
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
echo   Vitesse de reaction ?
echo.
echo   [1] Lent (15 cycles/min) - Reflechi
echo   [2] Normal (25 cycles/min) - Equilibre
echo   [3] Rapide (35 cycles/min) - Reactif
echo   [4] Ultra (50 cycles/min) - TRES rapide
echo.

set /p speed_choice=Choix: 

if "%speed_choice%"=="1" set speed=15
if "%speed_choice%"=="2" set speed=25
if "%speed_choice%"=="3" set speed=35
if "%speed_choice%"=="4" set speed=50

echo.
echo ================================================================
echo   Configuration:
echo   - Strategie: %strategy%
echo   - Duree: %minutes% minute(s)
echo   - Vitesse: %speed% cycles/min
echo ================================================================
echo.

cd /d "%~dp0agents\odin_vision"

C:\Users\admin\miniconda3\python.exe odin_ultimate.py --strategy %strategy% --minutes %minutes% --speed %speed%

echo.
pause

