@echo off
chcp 65001 >nul
title 🔌 Agent Nicolas - Open Schematics Explorer
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║   🔌 LANCEMENT DE L'AGENT NICOLAS...                             ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0agents\nicolas_open_schematics"
python nicolas_cli.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Erreur! Python n'est peut-être pas installé.
    echo.
    pause
)

