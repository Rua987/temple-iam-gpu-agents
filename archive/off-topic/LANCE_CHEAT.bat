@echo off
chcp 65001 >nul
title 🔥 ODIN CHEAT - Le Mode Ultime
color 0C

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║   🔥 ODIN CHEAT - Le Mode Ultime                                ║
echo ║                                                                  ║
echo ║   Combine:                                                       ║
echo ║   - 🧠 Vision IA (Moondream)                                    ║
echo ║   - 🔬 Memory Reading                                           ║
echo ║   - 🎮 DirectInput                                              ║
echo ║   - 📊 Cheat Engine MCP                                         ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

:: Activation de Miniconda
echo 🔧 Activation de l'environnement Python...
call C:\Users\admin\miniconda3\Scripts\activate.bat C:\Users\admin\miniconda3

:: Lancement
cd /d "%~dp0agents\odin_vision"
python odin_cheat.py

pause

