@echo off
chcp 65001 > nul
title ODIN WARRIOR V2

echo.
echo ================================================================
echo.
echo    ODIN WARRIOR V2 - Combat Realiste
echo.
echo    Ameliorations:
echo    - Lock-on AVANT chaque attaque
echo    - Sprint LONG (2-5 secondes)
echo    - Combos realistes
echo    - Esquives intelligentes
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
echo   Lancement pour %minutes% minutes...
echo.

cd /d "%~dp0agents\odin_vision"

C:\Users\admin\miniconda3\python.exe odin_warrior.py --minutes %minutes%

echo.
pause

