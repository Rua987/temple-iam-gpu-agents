@echo off
chcp 65001 > nul
title ODIN FARMING AVEUGLE

echo.
echo ================================================================
echo.
echo    ODIN FARMING AVEUGLE - SUPER AGRESSIF
echo.
echo    Pas besoin de vision - ODIN attaque en boucle !
echo.
echo ================================================================
echo.
echo   Combien d'heures de farming ?
echo.
echo   [1] 1 heure
echo   [2] 2 heures
echo   [4] 4 heures
echo   [8] 8 heures (toute la nuit)
echo   [0] Personnalise
echo.

set /p choice=Choix: 

if "%choice%"=="1" set hours=1
if "%choice%"=="2" set hours=2
if "%choice%"=="4" set hours=4
if "%choice%"=="8" set hours=8
if "%choice%"=="0" (
    set /p hours=Nombre d heures: 
)

echo.
echo   Vitesse du farming ?
echo.
echo   [1] Lent (5 cycles/min) - Plus prudent
echo   [2] Normal (10 cycles/min) - Equilibre
echo   [3] Rapide (15 cycles/min) - Agressif
echo   [4] Turbo (20 cycles/min) - TRES agressif
echo.

set /p speed_choice=Choix: 

if "%speed_choice%"=="1" set speed=5
if "%speed_choice%"=="2" set speed=10
if "%speed_choice%"=="3" set speed=15
if "%speed_choice%"=="4" set speed=20

echo.
echo   Lancement: %hours% heure(s) a %speed% cycles/min
echo   Ctrl+C pour arreter
echo.

cd /d "%~dp0agents\odin_vision"

C:\Users\admin\miniconda3\python.exe farming_blind.py --hours %hours% --speed %speed%

echo.
pause
