@echo off
chcp 65001 >nul
title ODIN - Mode Autonome (IA Vision)

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║   🤖 ODIN AUTONOME - IA Vision + Décisions auto                 ║
echo ║                                                                  ║
echo ║   Ce mode utilise Ollama + LLaVA pour VOIR et DÉCIDER !        ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

:: ========================================
:: ACTIVATION DE MINICONDA
:: ========================================
echo 🔧 Activation de l'environnement Python...
call C:\Users\admin\miniconda3\Scripts\activate.bat C:\Users\admin\miniconda3

:: Vérification rapide des outils
echo 🔍 Vérification des outils...
python -c "import mss, pyautogui, pydirectinput, pygetwindow; print('✅ Tous les outils sont prêts !')" 2>nul
if errorlevel 1 (
    echo ⚠️ Outils manquants, installation en cours...
    python -m pip install mss Pillow pyautogui pydirectinput pygetwindow -q
    echo ✅ Installation terminée !
)

echo.
echo ⚠️ Assure-toi que ton jeu est lancé !
echo.

cd /d "%~dp0agents\odin_vision"
python autonomous_player.py

pause
