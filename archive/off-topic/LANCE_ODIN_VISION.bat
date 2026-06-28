@echo off
chcp 65001 >nul
title 👁️ ODIN VISION - Agent de Vision IA
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║   👁️  ODIN VISION - Agent de Vision IA                          ║
echo ║                                                                  ║
echo ║   Inspiré de Nvidia ACE NIM Agent Blueprint                      ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

:: ========================================
:: ACTIVATION DE MINICONDA
:: ========================================
call C:\Users\admin\miniconda3\Scripts\activate.bat C:\Users\admin\miniconda3 >nul 2>&1

echo 📦 Vérification des dépendances...
python -c "import mss, pyautogui, pydirectinput, pygetwindow" 2>nul
if errorlevel 1 (
    echo ⬇️ Installation des outils manquants...
    python -m pip install mss Pillow pyautogui pydirectinput pygetwindow -q
    echo ✅ Installation terminée !
)

echo.
echo 🚀 Lancement d'ODIN VISION...
echo.

cd /d "%~dp0agents\odin_vision"
python odin_cli.py

pause
