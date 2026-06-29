@echo off
chcp 65001 > nul
title ODIN EXPLORE - Mode Exploration Pure

echo.
echo ================================================================
echo    ODIN EXPLORE - Mode Exploration Pure
echo.
echo    ZERO combat - Seulement marcher et sprinter
echo    Pour recolter des runes en explorant
echo ================================================================
echo.
echo   Duree ?
echo   [30] 30 min  [60] 1h  [120] 2h  [0] Custom
echo.
set /p m=Choix: 

if "%m%"=="0" (
    set /p m=Minutes: 
)

cd /d "%~dp0agents\odin_vision"
C:\Users\admin\miniconda3\python.exe odin_explore.py --minutes %m%

pause

