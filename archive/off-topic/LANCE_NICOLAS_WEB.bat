@echo off
chcp 65001 >nul
title 🌐 Agent Nicolas - Interface Web
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║   🌐 NICOLAS WEB - Interface Navigateur                         ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

echo 📦 Vérification de Flask...
pip show flask >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo ⬇️  Installation de Flask...
    pip install flask
    echo.
)

echo.
echo 🚀 Lancement du serveur web...
echo.
echo    ➡️  Ouvre ton navigateur à: http://localhost:5000
echo.
echo    Pour arrêter: Ctrl+C
echo.

cd /d "%~dp0agents\nicolas_open_schematics"
python nicolas_web.py

pause

