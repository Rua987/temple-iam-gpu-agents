@echo off
REM ========================================================================
REM TEMPLE IAM GPU AGENTS - DEMARRAGE FACILE
REM Double-click sur ce fichier pour tout installer et lancer!
REM ========================================================================

chcp 65001 >nul 2>&1
color 0A

echo.
echo ================================================================================
echo    TEMPLE IAM GPU AGENTS - DEMARRAGE AUTOMATIQUE
echo ================================================================================
echo.
echo    Bienvenue! Ce script va:
echo      1. Verifier Python
echo      2. Installer les dependances
echo      3. Lancer le moniteur GPU universel
echo.
echo ================================================================================
echo.

REM Verification Python
echo [1/3] Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERREUR: Python n'est pas installe!
    echo.
    echo Telecharge Python depuis: https://www.python.org/downloads/
    echo IMPORTANT: Coche la case "Add Python to PATH" pendant l'installation!
    echo.
    pause
    exit /b 1
)
echo     Python detecte!
echo.

REM Installation dependances
echo [2/3] Installation des dependances...
echo     Cela peut prendre quelques minutes la premiere fois...
pip install --quiet --upgrade pip
pip install --quiet -r requirements_gpu.txt
if errorlevel 1 (
    echo.
    echo ERREUR: Installation des dependances echouee!
    echo.
    echo Essaye manuellement: pip install -r requirements_gpu.txt
    echo.
    pause
    exit /b 1
)
echo     Dependances installees!
echo.

REM Test rapide
echo [3/3] Test du systeme...
python test_universal_system_safe.py >nul 2>&1
if errorlevel 1 (
    echo     Warning: Tests partiellement echoues (peut etre normal sans GPU)
) else (
    echo     Tests passes!
)
echo.

REM Menu de choix
echo ================================================================================
echo    QUEL SYSTEME VEUX-TU UTILISER?
echo ================================================================================
echo.
echo    [1] Systeme V2 Enhanced (RECOMMANDE)
echo        - Detection automatique de n'importe quel jeu
echo        - Profils thermiques adaptatifs
echo        - Auto-apprentissage
echo.
echo    [2] Systeme Production (Eugene)
echo        - Teste sur RTX 4090, 4060, 2070
echo        - Ultra stable
echo.
echo    [3] Tests seulement
echo.
echo    [4] Quitter
echo.
echo ================================================================================

set /p choice="Ton choix (1-4): "

if "%choice%"=="1" goto run_v2
if "%choice%"=="2" goto run_eugene
if "%choice%"=="3" goto run_tests
if "%choice%"=="4" goto end

echo Choix invalide!
pause
goto end

:run_v2
echo.
echo ================================================================================
echo    DEMARRAGE SYSTEME V2 ENHANCED
echo ================================================================================
echo.
echo    Lance ton jeu prefere, le systeme le detectera automatiquement!
echo    Appuie sur Ctrl+C pour arreter.
echo.
python run_universal_monitor_v2.py
goto end

:run_eugene
echo.
echo ================================================================================
echo    DEMARRAGE SYSTEME PRODUCTION (Eugene)
echo ================================================================================
echo.
echo    Lance ton jeu, le systeme le detectera automatiquement!
echo    Appuie sur Ctrl+C pour arreter.
echo.
python run_gpu_monitor.py
goto end

:run_tests
echo.
echo ================================================================================
echo    TESTS DU SYSTEME
echo ================================================================================
echo.
python test_universal_system_safe.py
echo.
pause
goto end

:end
echo.
echo Merci d'avoir utilise Temple IAM!
echo.
pause
