@echo off
chcp 65001 > nul
title ODIN MALENIA - Le Guerrier Legendaire

echo.
echo ================================================================
echo.
echo    ODIN MALENIA - Le Guerrier Legendaire
echo.
echo    Deux modes automatiques:
echo    - EXPLORATION : Marche longue, decouverte
echo    - COMBAT : Ultra agressif style Malenia
echo.
echo    Fonctionnalites:
echo    - Basculement auto exploration/combat
echo    - Esquives predictives (timing parfait)
echo    - Combos fluides 3-5 hits + finisher
echo    - Punition apres chaque esquive
echo.
echo ================================================================
echo.
echo   Combien de minutes ?
echo.
echo   [5]  5 minutes
echo   [10] 10 minutes
echo   [30] 30 minutes
echo   [60] 1 heure
echo.

set /p minutes=Choix: 

if "%minutes%"=="5" set minutes=5
if "%minutes%"=="10" set minutes=10
if "%minutes%"=="30" set minutes=30
if "%minutes%"=="60" set minutes=60

echo.
echo   Lancement ODIN MALENIA pour %minutes% minutes...
echo.

cd /d "%~dp0agents\odin_vision"

C:\Users\admin\miniconda3\python.exe odin_malenia.py --minutes %minutes%

echo.
pause

