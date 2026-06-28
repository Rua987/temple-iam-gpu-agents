@echo off
chcp 65001 >nul
title 🏛️ TEMPLE IAM - Centre de Contrôle
color 0B

:menu
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                              ║
echo ║   🏛️ TEMPLE IAM - Centre de Contrôle Unifié                                ║
echo ║                                                                              ║
echo ║   Tous tes outils en un seul endroit !                                      ║
echo ║                                                                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                         CHOISIS TON MODULE                                   ║
echo ╠══════════════════════════════════════════════════════════════════════════════╣
echo ║                                                                              ║
echo ║   👁️ ODIN - Bot Gaming IA                                                   ║
echo ║   ─────────────────────────────────────────────────────────────────────────  ║
echo ║   [1] 👁️ ODIN MASTER  - Tous les modes de jeu (Menu complet)               ║
echo ║   [2] 🔥 ODIN CHEAT   - Mode Ultime (Vision + Memory + Cheat Engine)        ║
echo ║                                                                              ║
echo ║   📊 GPU OPTIMIZATION                                                        ║
echo ║   ─────────────────────────────────────────────────────────────────────────  ║
echo ║   [3] 📈 GPU Monitor  - Surveillance temps réel                             ║
echo ║   [4] 🌡️ Thermal Opt  - Optimisation thermique ML                          ║
echo ║                                                                              ║
echo ║   🔧 OUTILS MAKERS                                                          ║
echo ║   ─────────────────────────────────────────────────────────────────────────  ║
echo ║   [5] 🤖 NICOLAS      - Assistant Schématiques (Drones, Robots)             ║
echo ║                                                                              ║
echo ║   🔬 REVERSE ENGINEERING                                                     ║
echo ║   ─────────────────────────────────────────────────────────────────────────  ║
echo ║   [6] 🔬 Cheat Engine - Ouvrir Cheat Engine (si installé)                   ║
echo ║   [7] 📊 Memory Test  - Tester lecture mémoire Elden Ring                   ║
echo ║   [8] 🎮 Input Test   - Tester les inputs DirectInput                       ║
echo ║                                                                              ║
echo ║   [0] ❌ QUITTER                                                             ║
echo ║                                                                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

set /p choice="🎮 Ton choix > "

if "%choice%"=="1" goto odin_master
if "%choice%"=="2" goto odin_cheat
if "%choice%"=="3" goto gpu_monitor
if "%choice%"=="4" goto thermal
if "%choice%"=="5" goto nicolas
if "%choice%"=="6" goto cheat_engine
if "%choice%"=="7" goto memory_test
if "%choice%"=="8" goto input_test
if "%choice%"=="0" goto end

echo.
echo ⚠️ Choix invalide !
timeout /t 2 >nul
goto menu

:: ============================================================================
:: ODIN MASTER
:: ============================================================================
:odin_master
echo.
echo 👁️ Lancement ODIN MASTER...
call C:\Users\admin\miniconda3\Scripts\activate.bat C:\Users\admin\miniconda3
cd /d "%~dp0agents\odin_vision"
python odin_master.py
goto menu

:: ============================================================================
:: ODIN CHEAT
:: ============================================================================
:odin_cheat
echo.
echo 🔥 Lancement ODIN CHEAT - Mode Ultime...
call C:\Users\admin\miniconda3\Scripts\activate.bat C:\Users\admin\miniconda3
cd /d "%~dp0agents\odin_vision"
python odin_cheat.py
goto menu

:: ============================================================================
:: GPU MONITOR
:: ============================================================================
:gpu_monitor
echo.
echo 📈 Lancement GPU Monitor...
call C:\Users\admin\miniconda3\Scripts\activate.bat C:\Users\admin\miniconda3
cd /d "%~dp0"
python run_universal_monitor_v2.py
goto menu

:: ============================================================================
:: THERMAL OPTIMIZER
:: ============================================================================
:thermal
echo.
echo 🌡️ Lancement Thermal Optimizer...
call C:\Users\admin\miniconda3\Scripts\activate.bat C:\Users\admin\miniconda3
cd /d "%~dp0"
python run_thermal_optimizer.py
goto menu

:: ============================================================================
:: NICOLAS
:: ============================================================================
:nicolas
echo.
echo 🤖 Lancement NICOLAS...
call C:\Users\admin\miniconda3\Scripts\activate.bat C:\Users\admin\miniconda3
cd /d "%~dp0agents\nicolas_open_schematics"
python nicolas_cli.py
goto menu

:: ============================================================================
:: CHEAT ENGINE
:: ============================================================================
:cheat_engine
echo.
echo 🔬 Recherche de Cheat Engine...

:: Chemins communs
if exist "C:\Program Files\Cheat Engine 7.5\Cheat Engine.exe" (
    start "" "C:\Program Files\Cheat Engine 7.5\Cheat Engine.exe"
    echo ✅ Cheat Engine lancé !
    echo.
    echo 📋 N'oublie pas de charger le script MCP :
    echo    File → Execute Script → ce_mcp_bridge.lua
    timeout /t 5 >nul
    goto menu
)

if exist "C:\Program Files (x86)\Cheat Engine 7.5\cheatengine-x86_64.exe" (
    start "" "C:\Program Files (x86)\Cheat Engine 7.5\cheatengine-x86_64.exe"
    echo ✅ Cheat Engine lancé !
    timeout /t 3 >nul
    goto menu
)

echo.
echo ❌ Cheat Engine non trouvé !
echo.
echo 📥 Télécharge-le sur : https://www.cheatengine.org/downloads.php
echo.
pause
goto menu

:: ============================================================================
:: MEMORY TEST
:: ============================================================================
:memory_test
echo.
echo 📊 Test lecture mémoire Elden Ring...
call C:\Users\admin\miniconda3\Scripts\activate.bat C:\Users\admin\miniconda3
cd /d "%~dp0agents\odin_vision"
python elden_memory.py
pause
goto menu

:: ============================================================================
:: INPUT TEST
:: ============================================================================
:input_test
echo.
echo 🎮 Test des inputs DirectInput...
call C:\Users\admin\miniconda3\Scripts\activate.bat C:\Users\admin\miniconda3
cd /d "%~dp0agents\odin_vision"
python elden_input.py
pause
goto menu

:: ============================================================================
:: END
:: ============================================================================
:end
echo.
echo 👋 Merci d'avoir utilisé Temple IAM !
echo.
timeout /t 2 >nul
exit

