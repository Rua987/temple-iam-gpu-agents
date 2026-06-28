@echo off
:: ========================================
:: TEMPLE IAM - Activation Python Miniconda
:: ========================================
:: Ce fichier active l'environnement Python correct.
:: Il est appelé par tous les autres scripts .bat

call C:\Users\admin\miniconda3\Scripts\activate.bat C:\Users\admin\miniconda3 >nul 2>&1

:: Vérification silencieuse
python -c "import mss, pyautogui" 2>nul
if errorlevel 1 (
    echo [TEMPLE IAM] Installation des outils manquants...
    python -m pip install mss Pillow pyautogui pydirectinput pygetwindow -q
)

