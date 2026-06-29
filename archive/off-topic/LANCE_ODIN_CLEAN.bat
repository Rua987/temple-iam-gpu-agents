@echo off
chcp 65001 > nul
title ODIN CLEAN

echo.
echo ================================================================
echo    ODIN CLEAN - Pas de Gaspillage
echo.
echo    EXPLORATION = Marcher/Sprinter SEULEMENT
echo    COMBAT = Active par lock-on (ennemi detecte)
echo.
echo    Logs minimaux - Economie memoire
echo ================================================================
echo.
echo   Duree ?
echo   [5] 5 min  [10] 10 min  [30] 30 min  [60] 1h
echo.
set /p m=Choix: 

cd /d "%~dp0agents\odin_vision"
C:\Users\admin\miniconda3\python.exe odin_clean.py --minutes %m%

pause
