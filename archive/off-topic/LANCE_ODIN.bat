@echo off
chcp 65001 >nul
title 👁️ ODIN MASTER - Le Lanceur Ultime
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║   👁️ ODIN MASTER - Le Lanceur Ultime                            ║
echo ║                                                                  ║
echo ║   Tous les modules ODIN en un seul endroit !                    ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

:: ========================================
:: ACTIVATION DE MINICONDA
:: ========================================
echo 🔧 Activation de l'environnement Python...
call C:\Users\admin\miniconda3\Scripts\activate.bat C:\Users\admin\miniconda3

:: Vérification des outils
echo 🔍 Vérification des outils...
python -c "import mss, pyautogui, pydirectinput, pygetwindow; print('✅ Tous les outils sont prêts !')" 2>nul
if errorlevel 1 (
    echo ⚠️ Outils manquants, installation...
    python -m pip install mss Pillow pyautogui pydirectinput pygetwindow requests -q
    echo ✅ Installation terminée !
)

echo.

cd /d "%~dp0agents\odin_vision"
python odin_master.py

pause
