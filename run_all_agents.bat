@echo off
REM Temple IAM GPU Agents - Menu de lancement
REM PLUS ULTRA ! DATTEBAYO !

:menu
cls
echo ========================================
echo   TEMPLE IAM GPU AGENTS - MENU
echo ========================================
echo.
echo 1. GPU Monitor UNIVERSEL (Tous les jeux AAA)
echo 2. Thermal Optimizer (Controle temperature)
echo 3. GPU Virtual Integration (Lance Alan Wake 2)
echo 4. Test GPU Quick (Validation systeme)
echo 5. Tous les agents (Monitor + Thermal)
echo 6. Quitter
echo.
set /p choice="Choisis une option (1-6): "

if "%choice%"=="1" goto monitor
if "%choice%"=="2" goto thermal
if "%choice%"=="3" goto virtual
if "%choice%"=="4" goto test
if "%choice%"=="5" goto all
if "%choice%"=="6" goto end

:monitor
echo.
echo [*] Lancement GPU Monitor UNIVERSEL...
echo [*] Compatible avec TOUS les jeux AAA !
echo [*] Appuie sur Ctrl+C pour arreter
python run_gpu_monitor.py
pause
goto menu

:thermal
echo.
echo [*] Lancement Thermal Optimizer...
echo [!] Necessite permissions admin pour modifier GPU
python temple_iam_thermal_optimizer.py
pause
goto menu

:virtual
echo.
echo [*] Lancement GPU Virtual Integration...
echo [*] Va detecter et lancer Alan Wake 2
python temple_iam_alan_wake2_gpu_virtual_integration.py
pause
goto menu

:test
echo.
echo [*] Lancement tests GPU...
python test_gpu_quick.py
pause
goto menu

:all
echo.
echo [*] Lancement de tous les agents...
echo [*] Monitor + Thermal Optimizer
start "GPU Monitor" python run_gpu_monitor.py
start "Thermal Optimizer" python temple_iam_thermal_optimizer.py
echo.
echo [OK] Agents lances dans des fenetres separees
pause
goto menu

:end
echo.
echo [*] Au revoir ! PLUS ULTRA !
exit
